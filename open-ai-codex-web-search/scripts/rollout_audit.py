#!/usr/bin/env python3
"""Audit Codex rollout .jsonl session logs for duplicate emissions and timing drift.

Usage:
    python3 scripts/rollout_audit.py results/{track}/artifacts/rollouts/{test}/rollout-*.jsonl
    python3 scripts/rollout_audit.py results/{track}/artifacts/rollouts/*/*.jsonl --csv audit.csv
    python3 scripts/rollout_audit.py ~/.codex/sessions/rollouts/rollout-*.jsonl

For each session file this reports:
  1. Identity: session id, model, reasoning effort, CLI version, test prompt ID if present
  2. Emission counts: user messages, commentary updates, final answers, reasoning blocks
  3. API call counts: web search calls, function/tool calls, by tool name
  4. Duplicate detection: any assistant final answer generated more than once,
     and verification that event_msg, response_item, and task_complete.last_agent_message
     are three copies of ONE generation rather than separate generations
  5. Post-completion records: anything appended after the last task_complete
  6. Timing: duration_ms, time_to_first_token_ms, wall clock between first and last record
  7. Token usage from the final token_count event

Exit code is nonzero if any anomaly flag fires, so it can run in CI.
"""

import argparse
import csv
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from failure_classifier import FailureClass, classify_output, classify_output_all, summarize


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


@dataclass
class FailureRecord:
    """A failure classification plus the context needed to map it to Codex chat.

    The classifier stays focused on pattern matching; the audit layer attaches
    provenance (line number, command, call id) and the nearest agent chat
    message so failures can be compared against what Codex actually rendered.
    """

    failure_class: FailureClass
    line_no: int
    call_id: str | None
    tool_name: str
    command: str | None
    output_snippet: str
    chat_before: dict | None
    chat_after: dict | None
    chat_nearest: dict | None
    turn_id: str | None
    recovered: bool = False


# Skills are announced in a developer response_item containing a
# <skills_instructions> block. Each skill is one Markdown bullet:
#   - name: description (locator: path)
# The name may contain colons (e.g. plugin:skill-name), so we split on
# the first ": " and treat the trailing "(locator: path)" as the source.
SKILLS_BLOCK_RE = re.compile(r"<skills_instructions>(.*?)</skills_instructions>", re.DOTALL)
SKILL_LINE_RE = re.compile(
    r"^- (?P<name>.+?):\s+(?P<desc>.+?)\s+\((?P<locator>[^:)]+):\s+(?P<path>[^)]+)\)",
    re.MULTILINE,
)

# Codex CLI 0.144+ wraps exec_command in a response_item of type
# `custom_tool_call` named "exec". The `input` field is a JavaScript snippet
# that passes a `cmd` string to tools.exec_command. We extract every `cmd:`
# string literal so shell commands and their failures remain auditable when the
# newer tool shape is used.
CUSTOM_CMD_RE = re.compile(r'cmd\s*:\s*("(?:\\.|[^"\\])*")', re.S)

# Codex can also batch multiple shell commands into a single exec
# custom_tool_call via `const cmds = [["label", "command"], ...]` followed by
# Promise.all. The regex below captures the string pairs in such arrays.
CUSTOM_CMDS_ARRAY_RE = re.compile(
    r'const\s+cmds\s*=\s*\[\s*(\[\s*"[^"]*"\s*,\s*"(?:\\.|[^"\\])*"\s*\]\s*(?:,\s*\[\s*"[^"]*"\s*,\s*"(?:\\.|[^"\\])*"\s*\]\s*)*)\]',
    re.S,
)
CUSTOM_CMDS_PAIR_RE = re.compile(r'\[\s*"[^"]*"\s*,\s*("(?:\\.|[^"\\])*")\s*\]', re.S)

# Codex represents an escalation request differently across CLI versions:
# - legacy function_call arguments JSON: {"sandbox_permissions": "require_escalated"}
# - newer custom_tool_call JavaScript input: tools.exec_command({..., sandbox_permissions: "require_escalated"})
_ESCALATION_RE = re.compile(r'["\']?sandbox_?permissions["\']?\s*:\s*["\']require_escalated["\']', re.I)
_LOGIN_ESCALATION_RE = re.compile(r'["\']?login["\']?\s*:\s*true', re.I)


def _is_escalated_request(args: dict | str | None) -> bool:
    """Return True if a tool call explicitly requests sandbox escalation."""
    if not args:
        return False
    if isinstance(args, dict):
        if args.get("sandbox_permissions") == "require_escalated":
            return True
        if args.get("login") is True:
            return True
        return False
    text = args
    if _ESCALATION_RE.search(text):
        return True
    if _LOGIN_ESCALATION_RE.search(text):
        return True
    return False


def _extract_custom_tool_commands(input_text: str | None) -> list[str]:
    """Return the cmd strings from a custom_tool_call JavaScript input.

    Codex passes shell commands as JSON string literals inside the JavaScript
    wrapper, so internal quotes are backslash-escaped (e.g. `\"`). The legacy
    regex only handled plain JS string literals; this version parses the
    JSON-escaped `cmd` value so long, escaped commands are recovered.
    """
    if not input_text:
        return []
    cmds = []
    # Single commands passed as `"cmd":"..."` inside a JSON-ish object.
    # Match a JSON string body, then decode it.
    _JSON_STRING_RE = re.compile(r'"cmd"\s*:\s*"((?:\\.|[^"\\])*)"', re.S)
    for m in _JSON_STRING_RE.finditer(input_text):
        try:
            cmd = json.loads('"' + m.group(1) + '"')
        except json.JSONDecodeError:
            cmd = m.group(1)
        if cmd:
            cmds.append(cmd)
    # Batched commands passed as `const cmds = [["label", "..."], ...]`.
    for array_match in CUSTOM_CMDS_ARRAY_RE.finditer(input_text):
        for pair_match in CUSTOM_CMDS_PAIR_RE.finditer(array_match.group(1)):
            raw = pair_match.group(1)
            try:
                cmd = json.loads(raw)
            except json.JSONDecodeError:
                cmd = raw[1:-1]
            if cmd:
                cmds.append(cmd)
    return cmds


def _extract_js_only_summary(input_text: str | None) -> str:
    """Return a short human-readable summary of a JS-only wrapper.

    JS-only wrappers perform pure analysis (no `tools.*` calls). The summary
    is the first non-trivial code statement, capped so the table stays readable.
    """
    if not input_text:
        return ""
    # Drop leading comments and blank lines.
    lines = input_text.splitlines()
    code_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        code_lines.append(stripped)
        if len(code_lines) >= 2:
            break
    summary = " ".join(code_lines)
    if len(summary) > 100:
        summary = summary[:97] + "..."
    return summary


# Codex CLI 0.145 wraps one or more native tool invocations inside a single
# custom_tool_call named "exec". The JavaScript body calls tools.<name>(...).
# We disaggregate the wrapper so web__run and exec_command are counted against
# the same categories used for legacy function_call records.
_CUSTOM_INNER_TOOL_RE = re.compile(r"tools\.(\w+)\s*\(", re.S)


def _extract_custom_inner_tools(input_text: str | None) -> list[str]:
    """Return the names of native tools invoked inside a custom_tool_call wrapper."""
    if not input_text:
        return []
    return _CUSTOM_INNER_TOOL_RE.findall(input_text)


@dataclass
class ToolCallRow:
    """A single auditable tool invocation from a rollout JSONL file."""

    line_no: int
    record_type: str
    name: str
    codex_tool: str | None
    js_only: bool
    summary: str
    call_id: str | None


def parse_skills(records: list[dict]) -> list[dict]:
    """Return skill entries observed in developer <skills_instructions> blocks."""
    skills = []
    for rec in records:
        if rec.get("type") != "response_item":
            continue
        payload = rec.get("payload", {}) or {}
        if payload.get("type") != "message" or payload.get("role") != "developer":
            continue
        for block in payload.get("content", []) or []:
            text = block.get("text", "")
            for block_match in SKILLS_BLOCK_RE.finditer(text):
                for line_match in SKILL_LINE_RE.finditer(block_match.group(1)):
                    skills.append(
                        {
                            "name": line_match.group("name").strip(),
                            "description": line_match.group("desc").strip(),
                            "locator": line_match.group("locator").strip(),
                            "path": line_match.group("path").strip(),
                        }
                    )
    return skills


# --- Skill-language detection --------------------------------------------

SKILL_PATH = ".agents/skills/docs-consumption/SKILL.md"
# SKILL.md requires the report to be prefaced with COMPLETE, PARTIAL, or UNVERIFIABLE.
# Only count a formal protocol label at the start of the answer: optional leading
# markdown decoration, the keyword, optional trailing decoration, then a colon,
# newline, or end of string. This avoids false positives from sentences like
# "Looks complete" or "Perceived completeness".
PROTOCOL_PREFIX_RE = re.compile(
    r"^\s*(?:\*\*|\*|__|_|#+\s*)?(COMPLETE|PARTIAL|UNVERIFIABLE)"
    r"(?:\*\*|\*|__|_)?\s*(?::|\n|$)",
    re.IGNORECASE,
)

# Behavioral proxies for the auto-generated Codex memory skill observed in
# ~/.codex/memories/skills/single-url-retrieval-measurement/SKILL.md. Codex does
# not emit explicit memory-load events in these rollout logs, so we infer use
# from the exact shell recipes it prescribes.
MEMORY_SKILL_FINGERPRINTS: tuple[tuple[str, re.Pattern], ...] = (
    ("retrieval-check.out", re.compile(r"curl\s+.*--output\s+/tmp/retrieval-check\.out", re.I)),
    ("perl-length-tail", re.compile(r"perl\s+-0ne\s+['\"].*print\s+length\(\$_\)", re.I)),
    ("rg-tag-balance", re.compile(r"rg\s+-o\s+['\"]<(/?(?:devsite-code|pre))", re.I)),
)


# Phrases and keywords that indicate the agent reasoned with the docs-consumption
# skill protocol, even when it did not use the formal COMPLETE/PARTIAL/UNVERIFIABLE
# prefix or cite the skill file.
SKILL_LANGUAGE_PATTERNS = [
    re.compile(r"\bthe tool ran\b", re.IGNORECASE),
    re.compile(r"\bfull content\b", re.IGNORECASE),
    re.compile(r"\bnot verified\b", re.IGNORECASE),
    re.compile(r"\bcannot confirm\b", re.IGNORECASE),
    re.compile(r"\bunverifiable\b", re.IGNORECASE),
    re.compile(r"\btruncation\b", re.IGNORECASE),
    re.compile(r"\blimitation\b", re.IGNORECASE),
    re.compile(r"\bcache miss\b", re.IGNORECASE),
    re.compile(r"\b0 bytes\b", re.IGNORECASE),
    re.compile(r"\bdns resolution failed\b", re.IGNORECASE),
    re.compile(r"\buse curl\b", re.IGNORECASE),
]


def _collect_texts_by_source(texts: list[str]) -> dict[str, list[str]]:
    """Return lowercase texts keyed by source bucket."""
    return {
        "final_answer": [t.lower() for t in texts],
        "commentary": [],
    }


def _first_match(patterns: list[re.Pattern], texts: list[str]) -> str | None:
    """Return the first matching text fragment for the given patterns."""
    for text in texts:
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return match.group(0)
    return None


def _detect_memory_fingerprints(cmds: list[str]) -> list[str]:
    """Return the memory-skill recipe names matched by the given shell commands."""
    found = []
    for cmd in cmds:
        for name, pattern in MEMORY_SKILL_FINGERPRINTS:
            if pattern.search(cmd):
                if name not in found:
                    found.append(name)
    return found


def _detect_in_sources(
    patterns: list[re.Pattern],
    final_texts: list[str],
    commentary_texts: list[str],
) -> tuple[str | None, str]:
    """Return (matched_fragment, source) where source is final_answer/commentary/both/none."""
    in_final = any(
        pattern.search(text)
        for text in final_texts
        for pattern in patterns
    )
    in_commentary = any(
        pattern.search(text)
        for text in commentary_texts
        for pattern in patterns
    )
    source = "both" if in_final and in_commentary else ("final_answer" if in_final else ("commentary" if in_commentary else "none"))
    if source == "none":
        return None, "none"
    search_texts = []
    if in_final:
        search_texts.extend(final_texts)
    if in_commentary:
        search_texts.extend(commentary_texts)
    fragment = _first_match(patterns, search_texts)
    return fragment, source


def format_duration(seconds) -> str | None:
    """Convert seconds to a compact abbreviated string.

    Examples:
      303.5  -> "5m3.5s"
      45.2   -> "45.2s"
      60.0   -> "1m"
      0.5    -> "0.5s"
    """
    if seconds is None:
        return None
    minutes = int(seconds // 60)
    remaining = round(seconds - minutes * 60, 1)
    if remaining >= 60.0:
        minutes += 1
        remaining = round(remaining - 60.0, 1)

    def fmt(n):
        return f"{n:.1f}" if n != int(n) else str(int(n))

    if minutes == 0:
        return f"{fmt(remaining)}s"
    if remaining == 0:
        return f"{minutes}m"
    return f"{minutes}m{fmt(remaining)}s"


def display_duration(seconds) -> str:
    """Return a formatted duration, keeping raw seconds for values >= 60s."""
    if seconds is None:
        return "—"
    formatted = format_duration(seconds)
    if seconds >= 60:
        return f"{formatted} ({seconds}s)"
    return formatted


def _nearest_chats(line_no: int, chat_history: list[dict], turn_id: str | None) -> tuple[dict | None, dict | None, dict | None]:
    """Return (nearest_before, nearest_after, nearest_overall) chat messages.

    Prefers messages from the same turn; falls back to the nearest by line
    number if no turn match exists. Returns None for any position that has no
    match, so callers can distinguish intent (before) from reaction (after).
    """
    if not chat_history:
        return None, None, None
    candidates = [c for c in chat_history if turn_id is None or c.get("turn_id") == turn_id]
    if not candidates:
        candidates = chat_history

    before = [c for c in candidates if c["line_no"] <= line_no]
    after = [c for c in candidates if c["line_no"] >= line_no]
    nearest_overall = min(candidates, key=lambda c: abs(c["line_no"] - line_no))
    nearest_before = min(before, key=lambda c: line_no - c["line_no"]) if before else None
    nearest_after = min(after, key=lambda c: c["line_no"] - line_no) if after else None
    return nearest_before, nearest_after, nearest_overall


def _failure_detail(record: FailureRecord) -> str:
    """Return a concise failure detail, enriching generic patterns when possible."""
    detail = record.failure_class.detail
    if record.failure_class.category == "command_not_found" and "No module named" in detail:
        m = re.search(r"No\s+module\s+named\s*['\"]?([^'\"\n]+)", record.output_snippet, re.I)
        if m:
            module = m.group(1).strip().rstrip("'\"")
            return f"ModuleNotFoundError: No module named '{module}'"
    return detail


def _format_chat_snippet(chat: dict | None, label: str) -> str:
    """Return a single formatted chat line, or a not-rendered placeholder."""
    if not chat:
        return f"        chat ({label}): not rendered in chat"
    msg = chat["message"].replace("\n", " ")
    if len(msg) > 200:
        msg = msg[:197] + "..."
    return f"        chat ({label}): line {chat['line_no']} {chat['phase']} — \"{msg}\""


def _attach_chat_context(failure_records: list[FailureRecord], chat_history: list[dict]) -> None:
    """Fill in chat correlation for each failure once the full file has been read."""
    for record in failure_records:
        chat_before, chat_after, chat_nearest = _nearest_chats(record.line_no, chat_history, record.turn_id)
        record.chat_before = chat_before
        record.chat_after = chat_after
        record.chat_nearest = chat_nearest


def _format_failure_console(record: FailureRecord, index: int) -> str:
    """Return a multi-line, indented failure block for console output."""
    lines = []
    status = "recovered" if record.recovered else "not recovered"
    lines.append(f"    [{index}] {record.failure_class.category} — {status}")
    lines.append(
        f"        line {record.line_no} · {record.tool_name}"
        + (f" · {record.call_id}" if record.call_id else "")
    )
    if record.command:
        cmd = record.command
        if len(cmd) > 160:
            cmd = cmd[:157] + "..."
        lines.append(f"        command: {cmd}")
    lines.append(f"        detail: {_failure_detail(record)}")
    if record.chat_before and record.chat_after and record.chat_before["line_no"] != record.chat_after["line_no"]:
        lines.append(_format_chat_snippet(record.chat_before, "before"))
        lines.append(_format_chat_snippet(record.chat_after, "after"))
    else:
        lines.append(_format_chat_snippet(record.chat_nearest, "nearest"))
    return "\n".join(lines)


def audit_file(path: Path) -> dict:
    records = []
    line_no_by_index: dict[int, int] = {}
    with open(path) as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                line_no_by_index[len(records)] = n
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  WARNING {path.name}:{n} unparseable line: {e}", file=sys.stderr)

    r = {
        "file": path.name,
        "session_id": None,
        "model": None,
        "effort": None,
        "cli_version": None,
        "test_id": None,
        "skills_loaded_count": 0,
        "skill_names": "",
        "skill_docs_consumption_loaded": "false",
        "skill_docs_consumption_path": "",
        "skill_docs_consumption_desc": "",
        "skill_path_mentioned": "false",
        "protocol_prefix": "",
        "protocol_prefix_source": "none",
        "skill_language": "false",
        "skill_language_source": "none",
        "turns": 0,
        "user_messages": 0,
        "commentary_msgs": 0,
        "final_answers_event": 0,
        "final_answers_item": 0,
        "reasoning_blocks": 0,
        "web_search_calls": 0,
        "function_calls": 0,
        "custom_exec_records": 0,
        "custom_exec_with_tools": 0,
        "custom_exec_js_only": 0,
        "codex_tools_inside_exec": Counter(),
        "tools": Counter(),
        "rendered_tools": Counter(),
        "task_completes": 0,
        "records_after_complete": 0,
        "after_complete_types": [],
        "duration_s": None,
        "ttft_s": None,
        "wallclock_s": None,
        "tokens_total": None,
        "context_window": None,
        "flags": [],
        "failure_classes": [],
        "failure_count_total": 0,
        "failure_count_error": 0,
        "failure_count_warning": 0,
        "failure_categories": "",
        "recovered_failure_count": 0,
        "has_failure": "no",
        "first_failure_category": "",
        "first_failure_detail": "",
        "unknown_error_messages": [],
        "exec_command_cmds": [],
        "memory_skill_fingerprints": [],
        "tool_call_rows": [],
    }

    final_event_texts = []          # final answers as emitted in the live event stream
    final_item_texts = []           # final answers as stored in the durable transcript
    commentary_texts = []           # agent commentary messages (thought panel)
    chat_history: list[dict] = []   # agent_message records for failure correlation
    call_id_to_cmd: dict[str, tuple[str, str | None]] = {}  # call_id -> (tool_name, command)
    tool_call_rows: list[ToolCallRow] = []  # auditable per-tool-call table
    last_agent_message = None
    last_complete_idx = None
    first_ts = last_ts = None
    last_tokens = None
    current_turn_failures: list[FailureRecord] = []
    web_search_end_count = 0          # web calls reported via the newer event_msg shape
    legacy_web_search_call_count = 0  # legacy response_item shape without a matching end event
    current_turn_id: str | None = None
    escalated_call_line_nos: dict[str, list[int]] = {}  # turn_id -> line numbers of escalation requests

    for i, rec in enumerate(records):
        line_no = line_no_by_index.get(i)
        ts = rec.get("timestamp")
        if ts:
            t = parse_ts(ts)
            first_ts = first_ts or t
            last_ts = t

        rtype = rec.get("type")
        p = rec.get("payload", {}) or {}

        if rtype == "session_meta":
            r["session_id"] = p.get("id")
            r["cli_version"] = p.get("cli_version")

        elif rtype == "turn_context":
            r["model"] = p.get("model")
            r["effort"] = p.get("effort")

        elif rtype == "event_msg":
            pt = p.get("type")
            if pt == "task_started":
                r["turns"] += 1
                current_turn_failures = []
                current_turn_id = p.get("turn_id")
            elif pt == "user_message":
                r["user_messages"] += 1
                msg = p.get("message") or ""
                for line in msg.splitlines():
                    if line.strip().lower().startswith("test id:"):
                        r["test_id"] = line.split(":", 1)[1].strip()
            elif pt == "agent_message":
                msg = p.get("message") or ""
                phase = p.get("phase")
                if phase == "commentary":
                    r["commentary_msgs"] += 1
                    commentary_texts.append(msg)
                elif phase == "final_answer":
                    r["final_answers_event"] += 1
                    final_event_texts.append(msg)
                chat_history.append({
                    "line_no": line_no,
                    "turn_id": (p.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                               or (rec.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id"),
                    "phase": phase,
                    "message": msg,
                })
            elif pt == "task_complete":
                r["task_completes"] += 1
                last_complete_idx = i
                last_agent_message = p.get("last_agent_message")
                if current_turn_failures:
                    # Heuristic: if the turn completed, failures were likely
                    # recovered via escalation or fallback. Keep the raw
                    # categories for accurate counts, but record how many
                    # failures were inside completed turns.
                    for record in current_turn_failures:
                        record.recovered = True
                    r["failure_classes"].extend(current_turn_failures)
                    r["recovered_failure_count"] += len(current_turn_failures)
                    # Detect network failures that were never followed by an
                    # explicit sandbox escalation request in the same turn.
                    turn_id = current_turn_id or p.get("turn_id")
                    escalated_lines = escalated_call_line_nos.get(turn_id or "", [])
                    eligible_categories = {"dns_blocked", "fetch_failed", "sandbox_empty_response"}
                    for record in current_turn_failures:
                        if record.failure_class.category in eligible_categories:
                            if not any(line > record.line_no for line in escalated_lines):
                                abandoned = FailureRecord(
                                    failure_class=FailureClass(
                                        category="escalation_abandonment",
                                        detail=f"{record.failure_class.detail}; no require_escalated retry",
                                        severity="warning",
                                    ),
                                    line_no=record.line_no,
                                    call_id=record.call_id,
                                    tool_name=record.tool_name,
                                    command=record.command,
                                    output_snippet=record.output_snippet,
                                    chat_before=record.chat_before,
                                    chat_after=record.chat_after,
                                    chat_nearest=record.chat_nearest,
                                    turn_id=record.turn_id,
                                    recovered=False,
                                )
                                r["failure_classes"].append(abandoned)
                    current_turn_failures = []
                if p.get("duration_ms") is not None:
                    r["duration_s"] = round(p["duration_ms"] / 1000, 1)
                if p.get("time_to_first_token_ms") is not None:
                    r["ttft_s"] = round(p["time_to_first_token_ms"] / 1000, 1)
            elif pt == "web_search_end":
                # Newer Codex CLI (e.g. GPT-5.6-Luna) reports web calls via
                # event_msg instead of response_item.web_search_call.
                web_search_end_count += 1
                action = p.get("action") or {}
                url = action.get("url", "?")
                tool_call_rows.append(ToolCallRow(
                    line_no=line_no or 0,
                    record_type="web_search_end",
                    name="web_search",
                    codex_tool=None,
                    js_only=False,
                    summary=url,
                    call_id=p.get("call_id"),
                ))
            elif pt == "token_count":
                info = p.get("info") or {}
                total = (info.get("total_token_usage") or {}).get("total_tokens")
                if total is not None:
                    last_tokens = total
                r["context_window"] = info.get("model_context_window") or r["context_window"]
            elif pt == "exec_command_end":
                out = p.get("output") or ""
                for fc in classify_output_all(out):
                    turn_id = (p.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                    current_turn_failures.append(FailureRecord(
                        failure_class=fc,
                        line_no=line_no or 0,
                        call_id=None,
                        tool_name="exec_command",
                        command=None,
                        output_snippet=out,
                        chat_before=None,
                        chat_after=None,
                        chat_nearest=None,
                        turn_id=turn_id,
                        recovered=False,
                    ))
            elif pt == "mcp_tool_call_end":
                inv = p.get("invocation") or {}
                tool_name = f"{(inv.get('server') or '')}.{(inv.get('tool') or '')}".strip(".")
                result = p.get("result") or {}
                ok = result.get("Ok") or {}
                text = ""
                for block in ok.get("content", []) or []:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text += block.get("text", "")
                for fc in classify_output_all(text, tool_name=tool_name):
                    turn_id = (p.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                    current_turn_failures.append(FailureRecord(
                        failure_class=fc,
                        line_no=line_no or 0,
                        call_id=None,
                        tool_name=tool_name,
                        command=None,
                        output_snippet=text,
                        chat_before=None,
                        chat_after=None,
                        chat_nearest=None,
                        turn_id=turn_id,
                        recovered=False,
                    ))

        elif rtype == "response_item":
            it = p.get("type")
            if it == "message" and p.get("role") == "assistant" and p.get("phase") == "final_answer":
                r["final_answers_item"] += 1
                texts = [c.get("text", "") for c in p.get("content", []) if c.get("type") == "output_text"]
                final_item_texts.append("".join(texts))
            elif it == "reasoning":
                r["reasoning_blocks"] += 1
            elif it == "web_search_call":
                # Legacy shape used by GPT-5.4 Mini through 5.5. We count these
                # only when the newer web_search_end event is absent so we do
                # not double-count in logs that contain both shapes.
                legacy_web_search_call_count += 1
                action = (p.get("arguments") or {}).get("action") or {}
                url = action.get("url", "?")
                tool_call_rows.append(ToolCallRow(
                    line_no=line_no or 0,
                    record_type="web_search_call",
                    name="web_search",
                    codex_tool=None,
                    js_only=False,
                    summary=url,
                    call_id=p.get("call_id"),
                ))
            elif it == "function_call":
                r["function_calls"] += 1
                name = p.get("name", "?")
                ns = p.get("namespace")
                tool_name = f"{ns}.{name}" if ns else name
                r["tools"][tool_name] += 1
                call_id = p.get("call_id")
                cmd = None
                args = None
                if name == "exec_command":
                    try:
                        args = json.loads(p.get("arguments", "{}"))
                        cmd = args.get("cmd", "")
                    except (json.JSONDecodeError, AttributeError):
                        cmd = ""
                    if cmd:
                        r["exec_command_cmds"].append(cmd)
                summary = cmd or ""
                tool_call_rows.append(ToolCallRow(
                    line_no=line_no or 0,
                    record_type="function_call",
                    name=tool_name,
                    codex_tool=None,
                    js_only=False,
                    summary=summary,
                    call_id=call_id,
                ))
                if call_id is not None:
                    call_id_to_cmd[call_id] = (tool_name, cmd)
                # Track explicit sandbox escalation requests for abandonment detection.
                if _is_escalated_request(args):
                    turn_id = current_turn_id or (
                        (p.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                        or (rec.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                    )
                    if turn_id:
                        escalated_call_line_nos.setdefault(turn_id, []).append(line_no or 0)
            elif it == "custom_tool_call":
                r["function_calls"] += 1
                name = p.get("name", "?")
                call_id = p.get("call_id")
                input_text = p.get("input", "")
                cmds = _extract_custom_tool_commands(input_text)
                # Codex uses custom_tool_call as a JavaScript wrapper across CLI
                # versions; the wrapper name has been "exec" (0.145) and
                # "exec_command" (0.142), and may change again. Anchor on known
                # wrapper names, then use content to decide whether the wrapper
                # contains real Codex tool calls or is pure JS analysis.
                inner_tools = _extract_custom_inner_tools(input_text)
                is_exec_wrapper = name in ("exec", "exec_command")
                if is_exec_wrapper:
                    r["custom_exec_records"] += 1
                    if inner_tools:
                        r["custom_exec_with_tools"] += 1
                        for inner_name in inner_tools:
                            r["codex_tools_inside_exec"][inner_name] += 1
                            r["rendered_tools"][inner_name] += 1
                    else:
                        r["custom_exec_js_only"] += 1
                        r["rendered_tools"]["exec_js_only"] += 1
                    tool_name = "exec_wrapper"
                else:
                    tool_name = f"custom.{name}"
                    r["rendered_tools"][tool_name] += 1
                r["tools"][tool_name] += 1
                for cmd in cmds:
                    r["exec_command_cmds"].append(cmd)
                first_cmd = cmds[0] if cmds else None
                # Build an auditable row for each real Codex tool inside the wrapper.
                if inner_tools:
                    for inner_name in inner_tools:
                        summary = first_cmd if inner_name == "exec_command" and first_cmd else ""
                        if inner_name == "web__run":
                            m = re.search(r'open:\s*\[.*?ref_id:\s*"([^"]+)"', input_text, re.S)
                            if m:
                                summary = m.group(1)
                        tool_call_rows.append(ToolCallRow(
                            line_no=line_no or 0,
                            record_type="custom_tool_call",
                            name=name,
                            codex_tool=inner_name,
                            js_only=False,
                            summary=summary,
                            call_id=call_id,
                        ))
                else:
                    js_summary = _extract_js_only_summary(input_text) if is_exec_wrapper else (first_cmd or "")
                    tool_call_rows.append(ToolCallRow(
                        line_no=line_no or 0,
                        record_type="custom_tool_call",
                        name=name,
                        codex_tool=None,
                        js_only=is_exec_wrapper,
                        summary=js_summary,
                        call_id=call_id,
                    ))
                if call_id is not None:
                    call_id_to_cmd[call_id] = (tool_name, first_cmd)
                # Track explicit sandbox escalation requests in the newer tool shape.
                if _is_escalated_request(input_text):
                    turn_id = current_turn_id or (
                        (p.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                        or (rec.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                    )
                    if turn_id:
                        escalated_call_line_nos.setdefault(turn_id, []).append(line_no or 0)
            elif it == "custom_tool_call_output":
                out_blocks = p.get("output") or []
                if isinstance(out_blocks, str):
                    out_text = out_blocks
                else:
                    out_text = ""
                    for block in out_blocks:
                        if isinstance(block, dict):
                            out_text += block.get("text", "")
                call_id = p.get("call_id")
                tool_name, cmd = call_id_to_cmd.get(call_id, ("?", None))
                for fc in classify_output_all(out_text, command=cmd):
                    turn_id = (p.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                    current_turn_failures.append(FailureRecord(
                        failure_class=fc,
                        line_no=line_no or 0,
                        call_id=call_id,
                        tool_name=tool_name,
                        command=cmd,
                        output_snippet=out_text,
                        chat_before=None,
                        chat_after=None,
                        chat_nearest=None,
                        turn_id=turn_id,
                        recovered=False,
                    ))
            elif it == "function_call_output":
                out = p.get("output") or ""
                call_id = p.get("call_id")
                tool_name, cmd = call_id_to_cmd.get(call_id, ("?", None))
                for fc in classify_output_all(out, command=cmd):
                    turn_id = (p.get("internal_chat_message_metadata_passthrough") or {}).get("turn_id")
                    current_turn_failures.append(FailureRecord(
                        failure_class=fc,
                        line_no=line_no or 0,
                        call_id=call_id,
                        tool_name=tool_name,
                        command=cmd,
                        output_snippet=out,
                        chat_before=None,
                        chat_after=None,
                        chat_nearest=None,
                        turn_id=turn_id,
                        recovered=False,
                    ))

    # Any failures outside a completed turn are kept as raw failures.
    if current_turn_failures:
        r["failure_classes"].extend(current_turn_failures)

    # Chat context can only be correlated once every record has been read,
    # because the agent's reaction message often appears after the failing
    # tool output in the JSONL stream.
    _attach_chat_context(r["failure_classes"], chat_history)

    r["tokens_total"] = last_tokens
    if first_ts and last_ts:
        r["wallclock_s"] = round((last_ts - first_ts).total_seconds(), 1)

    # Canonical web-call count: newer Codex CLI emits event_msg.web_search_end;
    # older CLI emits response_item.web_search_call. Use the end events when
    # present so we don't double-count the legacy shape in the same log.
    r["web_search_calls"] = web_search_end_count if web_search_end_count else legacy_web_search_call_count

    # ---- Skill loading ----------------------------------------------------
    skills = parse_skills(records)
    r["skills_loaded_count"] = len(skills)
    r["skill_names"] = ", ".join(s["name"] for s in skills)
    docs_consumption = next(
        (s for s in skills if "docs-consumption" in s["name"]), None
    )
    if docs_consumption:
        r["skill_docs_consumption_loaded"] = "true"
        r["skill_docs_consumption_path"] = docs_consumption["path"]
        r["skill_docs_consumption_desc"] = docs_consumption["description"][:120]

    # ---- Skill-language detection ------------------------------------------
    final_texts = [t.lower() for t in final_event_texts + final_item_texts]
    commentary_texts_lower = [t.lower() for t in commentary_texts]

    r["skill_path_mentioned"] = "true" if any(
        SKILL_PATH.lower() in text for text in final_texts + commentary_texts_lower
    ) else "false"

    protocol_match, protocol_source = _detect_in_sources(
        [PROTOCOL_PREFIX_RE], final_texts, commentary_texts_lower
    )
    r["protocol_prefix"] = (protocol_match or "").strip().upper()
    r["protocol_prefix_source"] = protocol_source

    language_match, language_source = _detect_in_sources(
        SKILL_LANGUAGE_PATTERNS, final_texts, commentary_texts_lower
    )
    r["skill_language"] = "true" if language_match else "false"
    r["skill_language_source"] = language_source

    # Records appended after the last task_complete: the post-hoc alteration check
    if last_complete_idx is not None:
        tail = records[last_complete_idx + 1:]
        r["records_after_complete"] = len(tail)
        r["after_complete_types"] = [
            f"{x.get('type')}/{(x.get('payload') or {}).get('type', '')}" for x in tail
        ]

    # ---- Anomaly flags ----------------------------------------------------
    # A. More final answers than turns means a genuine double generation
    if r["final_answers_event"] > r["turns"]:
        r["flags"].append(
            f"DOUBLE_GENERATION: {r['final_answers_event']} final answers across {r['turns']} turn(s)"
        )

    # B. Identical text generated twice as separate emissions
    dupes = [t for t, c in Counter(sha(t) for t in final_event_texts).items() if c > 1]
    if dupes:
        r["flags"].append(f"DUPLICATE_EMISSION: identical final answer emitted more than once")

    # C. Event stream and durable transcript should be copies of one generation.
    # Strip <oai-mem-citation> blocks first; they are appended to the durable
    # transcript but not streamed, so they would otherwise trigger false positives.
    OAI_MEM_CITATION_RE = re.compile(r"<oai-mem-citation>.*?</oai-mem-citation>", re.DOTALL)
    if final_event_texts and final_item_texts:
        normalized_event = [OAI_MEM_CITATION_RE.sub("", t).rstrip() for t in final_event_texts]
        normalized_item = [OAI_MEM_CITATION_RE.sub("", t).rstrip() for t in final_item_texts]
        if [sha(t) for t in normalized_event] != [sha(t) for t in normalized_item]:
            r["flags"].append("STREAM_TRANSCRIPT_MISMATCH: event_msg and response_item final answers differ")

    # D. task_complete should carry the same single message
    if last_agent_message is not None and final_event_texts:
        if last_agent_message != final_event_texts[-1]:
            r["flags"].append("LAST_MESSAGE_MISMATCH: task_complete.last_agent_message differs from emitted final answer")

    # E. Anything written after completion is post-hoc activity
    if r["records_after_complete"]:
        r["flags"].append(
            f"POST_COMPLETION_RECORDS: {r['records_after_complete']} record(s) after task_complete: "
            + ", ".join(r["after_complete_types"][:5])
        )

    # F. Multiple completion events in a single-turn session
    if r["task_completes"] > r["turns"]:
        r["flags"].append(f"EXTRA_TASK_COMPLETE: {r['task_completes']} completes for {r['turns']} turn(s)")

    # G. Structural sanity: a final answer should exist at all
    if r["turns"] and not r["final_answers_event"]:
        r["flags"].append("NO_FINAL_ANSWER: turn completed without a final answer emission")

    # J. exec wrapper shape: custom_tool_call exec records can contain multiple
    # Codex tool invocations, one invocation, or none at all (pure JS analysis).
    # This flag documents the ratio so it is obvious when the wrapper record
    # count differs from the actual Codex tool calls inside.
    codex_tools_inside = sum(r["codex_tools_inside_exec"].values())
    if r["custom_exec_records"] and codex_tools_inside != r["custom_exec_records"]:
        r["flags"].append(
            f"EXEC_WRAPPER_SHAPE: {r['custom_exec_records']} exec wrapper record(s) contain "
            f"{codex_tools_inside} Codex tool call(s) and {r['custom_exec_js_only']} JS-only analysis block(s)"
        )

    # J. Memory-skill fingerprint flags: Codex does not announce local memory
    # skills in rollout logs, so we flag the exact shell recipes they prescribe.
    r["tool_call_rows"] = tool_call_rows
    r["memory_skill_fingerprints"] = _detect_memory_fingerprints(r["exec_command_cmds"])
    for fp in r["memory_skill_fingerprints"]:
        r["flags"].append(f"MEMORY_LIKE_RECIPE: {fp}")

    # H. Failure-mode summary (raw categories; recovery counted separately)
    failure_classes = [rec.failure_class for rec in r["failure_classes"]]
    failure_summary = summarize(failure_classes)
    r["failure_count_total"] = failure_summary["total"]
    r["failure_count_error"] = failure_summary["error_count"]
    r["failure_count_warning"] = failure_summary["warning_count"]
    r["failure_categories"] = "; ".join(
        f"{cat}={c}" for cat, c in sorted(failure_summary["category_counts"].items()) if cat != "ok"
    )
    # Surface escalation abandonment as its own concise flag so it is visible
    # without parsing the failure_records JSON blob.
    escalation_abandoned_count = failure_summary["category_counts"].get("escalation_abandonment", 0)
    if escalation_abandoned_count:
        r["flags"].append(
            f"ESCALATION_ABANDONED: {escalation_abandoned_count} network failure(s) not retried with escalation"
        )
    r["has_failure"] = "yes" if failure_summary["total"] else "no"
    first_error = next((fc for fc in failure_classes if fc.severity == "error"), None)
    first_warning = next((fc for fc in failure_classes if fc.severity == "warning"), None)
    first = first_error or first_warning
    r["first_failure_category"] = first.category if first else ""
    r["first_failure_detail"] = first.detail if first else ""
    r["unknown_error_messages"] = sorted(
        {fc.detail for fc in failure_classes if fc.category == "unknown_error"}
    )
    r["failure_records"] = json.dumps(
        [
            {
                "category": rec.failure_class.category,
                "severity": rec.failure_class.severity,
                "detail": rec.failure_class.detail,
                "line_no": rec.line_no,
                "call_id": rec.call_id,
                "tool_name": rec.tool_name,
                "command": rec.command,
                "chat_before": rec.chat_before,
                "chat_after": rec.chat_after,
                "chat_nearest": rec.chat_nearest,
                "turn_id": rec.turn_id,
                "recovered": rec.recovered,
            }
            for rec in r["failure_classes"]
        ],
        ensure_ascii=False,
    )
    return r


def _resolve_csv_path(csv_arg: str, input_files: list[Path]) -> Path:
    """Resolve the --csv destination.

    A bare filename like `audit.csv` is stored next to the audited rollouts:
    when every input file lives under a single test directory such as
    `.../rollouts/T3-skill-on-memories-suppressed/<model>/*.jsonl`, the CSV is
    placed at `.../rollouts/T3-skill-on-memories-suppressed/audit.csv`. A path
    that already contains a directory separator is used verbatim.
    """
    if os.path.sep in csv_arg or "/" in csv_arg:
        return Path(csv_arg)
    existing = [f for f in input_files if f.exists()]
    if not existing:
        return Path(csv_arg)
    # Each rollout path is .../rollouts/<test>/<model>/<file>.jsonl; the test
    # directory is two levels up from the file.
    test_dirs = {f.parent.parent.resolve() for f in existing}
    if len(test_dirs) == 1:
        return next(iter(test_dirs)) / csv_arg
    # Mixed test directories: fall back to the shared rollouts parent.
    rollout_parents = {f.parent.parent.parent.resolve() for f in existing}
    if len(rollout_parents) == 1:
        return next(iter(rollout_parents)) / csv_arg
    return Path(csv_arg)


def main():
    ap = argparse.ArgumentParser(description="Audit Codex rollout .jsonl logs for duplicate emissions and drift")
    ap.add_argument("paths", nargs="+", help="jsonl files or globs")
    ap.add_argument("--csv", help="also write results to this CSV path; a bare filename is stored next to the audited rollouts")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        expanded = glob.glob(p)
        files.extend(expanded if expanded else [p])
    files = [Path(f) for f in sorted(set(files))]

    results = []
    any_flags = False
    for f in files:
        if not f.exists():
            print(f"SKIP missing file: {f}", file=sys.stderr)
            continue
        r = audit_file(f)
        results.append(r)

        print("=" * 78)
        print(f"{r['file']}")
        print(f"  session {r['session_id']} | {r['model']} {r['effort']} | cli {r['cli_version']} | test {r['test_id']}")
        skill_summary = f"{r['skills_loaded_count']} loaded"
        if r["skill_docs_consumption_loaded"] == "true":
            skill_summary += " | docs-consumption: yes"
        print(f"  skills: {skill_summary} | names: {r['skill_names']}")
        if r["skill_docs_consumption_loaded"] == "true":
            lang_bits = []
            if r["skill_path_mentioned"] == "true":
                lang_bits.append("path mentioned")
            if r["protocol_prefix"]:
                lang_bits.append(f"prefix={r['protocol_prefix']} ({r['protocol_prefix_source']})")
            if r["skill_language"] == "true":
                lang_bits.append(f"skill-language ({r['skill_language_source']})")
            print(f"  skill-signals: {' | '.join(lang_bits) if lang_bits else 'none'}")
        print(f"  turns {r['turns']} | user msgs {r['user_messages']} | commentary {r['commentary_msgs']} | "
              f"final answers: event {r['final_answers_event']}, transcript {r['final_answers_item']}")
        # Per-call tool table: the single source of truth for tool invocations.
        if r["tool_call_rows"]:
            print("  tool records:")
            for row in r["tool_call_rows"]:
                codex = row.codex_tool or "-"
                js = "JS-only" if row.js_only else "-"
                summary = row.summary
                if len(summary) > 80:
                    summary = summary[:77] + "..."
                print(
                    f"    line {row.line_no:>3}  {row.record_type:<16}  {row.name:<14}  "
                    f"codex_tool={codex:<12}  js={js:<8}  {summary}"
                )
        # Anomaly flags are printed next to the tool table so they are easy to
        # correlate with the data they summarize.
        if r["flags"]:
            any_flags = True
            for fl in r["flags"]:
                print(f"  !! {fl}")
        if r["memory_skill_fingerprints"]:
            print(f"  memory fingerprints: {', '.join(r['memory_skill_fingerprints'])}")
        print(f"  timing: duration {display_duration(r['duration_s'])} | ttft {display_duration(r['ttft_s'])} | file wallclock {display_duration(r['wallclock_s'])}")
        print(f"  tokens {r['tokens_total']} / {r['context_window']}")
        if r["failure_count_total"]:
            print(f"  failures: {r['failure_count_total']} ({r['failure_count_error']} error, {r['failure_count_warning']} warning)")
            for idx, record in enumerate(r["failure_classes"], 1):
                print(_format_failure_console(record, idx))
        # Baseline structural sanity: duplication and post-completion drift are
        # independent of behavioral anomaly flags, so report them last.
        base_ok = (
            r["final_answers_event"] <= r["turns"]
            and r["task_completes"] <= r["turns"]
            and r["records_after_complete"] == 0
        )
        if base_ok:
            print("  OK: single emission, no post-completion records, all three copies match")

    if args.csv and results:
        cols = ["file", "session_id", "model", "effort", "test_id",
                "skills_loaded_count", "skill_names", "skill_docs_consumption_loaded",
                "skill_docs_consumption_path", "skill_docs_consumption_desc",
                "skill_path_mentioned", "protocol_prefix", "protocol_prefix_source",
                "skill_language", "skill_language_source",
                "turns", "user_messages",
                "commentary_msgs", "final_answers_event", "final_answers_item", "web_search_calls",
                "custom_exec_records", "custom_exec_with_tools", "custom_exec_js_only",
                "function_calls", "task_completes", "records_after_complete", "duration_s",
                "ttft_s", "wallclock_s", "tokens_total", "flags", "failure_count_total",
                "failure_count_error", "failure_count_warning", "failure_categories",
                "recovered_failure_count", "has_failure", "first_failure_category",
                "first_failure_detail", "unknown_error_messages", "memory_skill_fingerprints",
                "failure_records"]
        csv_path = _resolve_csv_path(args.csv, files)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in results:
                row = {k: r[k] for k in cols if k not in ("flags", "unknown_error_messages", "memory_skill_fingerprints", "failure_records")}
                row["flags"] = "; ".join(r["flags"])
                row["unknown_error_messages"] = "; ".join(r["unknown_error_messages"])
                row["memory_skill_fingerprints"] = ", ".join(r["memory_skill_fingerprints"])
                row["failure_records"] = r["failure_records"]
                w.writerow(row)
        print(f"\nCSV written to {csv_path}")

    sys.exit(1 if any_flags else 0)


if __name__ == "__main__":
    main()