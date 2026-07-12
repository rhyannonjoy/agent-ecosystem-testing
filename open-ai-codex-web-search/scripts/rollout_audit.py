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
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from failure_classifier import FailureClass, classify_output, recovered, summarize


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


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
    """Convert seconds to a human-readable minutes/seconds string.

    Preserves the original one-decimal precision:
      303.5  -> "5 minutes, 3.5 seconds"
      45.2   -> "45.2 seconds"
      60.0   -> "1 minute"
      0.5    -> "0.5 seconds"
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
        second_word = "second" if remaining == 1 else "seconds"
        return f"{fmt(remaining)} {second_word}"

    minute_word = "minute" if minutes == 1 else "minutes"
    if remaining == 0:
        return f"{minutes} {minute_word}"

    second_word = "second" if remaining == 1 else "seconds"
    return f"{minutes} {minute_word}, {fmt(remaining)} {second_word}"


def display_duration(seconds) -> str:
    """Return a formatted duration, keeping raw seconds for values >= 60s."""
    if seconds is None:
        return "—"
    formatted = format_duration(seconds)
    if seconds >= 60:
        return f"{formatted} ({seconds}s)"
    return formatted


def audit_file(path: Path) -> dict:
    records = []
    with open(path) as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
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
        "tools": Counter(),
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
    }

    final_event_texts = []          # final answers as emitted in the live event stream
    final_item_texts = []           # final answers as stored in the durable transcript
    commentary_texts = []           # agent commentary messages (thought panel)
    last_agent_message = None
    last_complete_idx = None
    first_ts = last_ts = None
    last_tokens = None
    current_turn_failures: list[FailureClass] = []

    for i, rec in enumerate(records):
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
            elif pt == "user_message":
                r["user_messages"] += 1
                msg = p.get("message") or ""
                for line in msg.splitlines():
                    if line.strip().lower().startswith("test id:"):
                        r["test_id"] = line.split(":", 1)[1].strip()
            elif pt == "agent_message":
                msg = p.get("message") or ""
                if p.get("phase") == "commentary":
                    r["commentary_msgs"] += 1
                    commentary_texts.append(msg)
                elif p.get("phase") == "final_answer":
                    r["final_answers_event"] += 1
                    final_event_texts.append(msg)
            elif pt == "task_complete":
                r["task_completes"] += 1
                last_complete_idx = i
                last_agent_message = p.get("last_agent_message")
                if current_turn_failures:
                    # Heuristic: if the turn completed, failures were likely
                    # recovered via escalation or fallback. Keep the raw
                    # categories for accurate counts, but record how many
                    # failures were inside completed turns.
                    r["failure_classes"].extend(current_turn_failures)
                    r["recovered_failure_count"] += len(current_turn_failures)
                    current_turn_failures = []
                if p.get("duration_ms") is not None:
                    r["duration_s"] = round(p["duration_ms"] / 1000, 1)
                if p.get("time_to_first_token_ms") is not None:
                    r["ttft_s"] = round(p["time_to_first_token_ms"] / 1000, 1)
            elif pt == "token_count":
                info = p.get("info") or {}
                total = (info.get("total_token_usage") or {}).get("total_tokens")
                if total is not None:
                    last_tokens = total
                r["context_window"] = info.get("model_context_window") or r["context_window"]
            elif pt == "exec_command_end":
                out = p.get("output") or ""
                fc = classify_output(out)
                if fc.category != "ok":
                    current_turn_failures.append(fc)
            elif pt == "mcp_tool_call_end":
                inv = p.get("invocation") or {}
                tool_name = f"{(inv.get('server') or '')}.{(inv.get('tool') or '')}".strip(".")
                result = p.get("result") or {}
                ok = result.get("Ok") or {}
                text = ""
                for block in ok.get("content", []) or []:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text += block.get("text", "")
                fc = classify_output(text, tool_name=tool_name)
                if fc.category != "ok":
                    current_turn_failures.append(fc)

        elif rtype == "response_item":
            it = p.get("type")
            if it == "message" and p.get("role") == "assistant" and p.get("phase") == "final_answer":
                r["final_answers_item"] += 1
                texts = [c.get("text", "") for c in p.get("content", []) if c.get("type") == "output_text"]
                final_item_texts.append("".join(texts))
            elif it == "reasoning":
                r["reasoning_blocks"] += 1
            elif it == "web_search_call":
                r["web_search_calls"] += 1
            elif it == "function_call":
                r["function_calls"] += 1
                name = p.get("name", "?")
                ns = p.get("namespace")
                r["tools"][f"{ns}.{name}" if ns else name] += 1
            elif it == "function_call_output":
                out = p.get("output") or ""
                fc = classify_output(out)
                if fc.category != "ok":
                    current_turn_failures.append(fc)

    # Any failures outside a completed turn are kept as raw failures.
    if current_turn_failures:
        r["failure_classes"].extend(current_turn_failures)

    r["tokens_total"] = last_tokens
    if first_ts and last_ts:
        r["wallclock_s"] = round((last_ts - first_ts).total_seconds(), 1)

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
    r["protocol_prefix"] = (protocol_match or "").upper()
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

    # H. Failure-mode summary (raw categories; recovery counted separately)
    failure_summary = summarize(r["failure_classes"])
    r["failure_count_total"] = failure_summary["total"]
    r["failure_count_error"] = failure_summary["error_count"]
    r["failure_count_warning"] = failure_summary["warning_count"]
    r["failure_categories"] = "; ".join(
        f"{cat}={c}" for cat, c in sorted(failure_summary["category_counts"].items()) if cat != "ok"
    )
    r["has_failure"] = "yes" if failure_summary["total"] else "no"
    first_error = next((fc for fc in r["failure_classes"] if fc.severity == "error"), None)
    first_warning = next((fc for fc in r["failure_classes"] if fc.severity == "warning"), None)
    first = first_error or first_warning
    r["first_failure_category"] = first.category if first else ""
    r["first_failure_detail"] = first.detail if first else ""
    r["unknown_error_messages"] = sorted(
        {fc.detail for fc in r["failure_classes"] if fc.category == "unknown_error"}
    )
    if failure_summary["total"]:
        breakdown = ", ".join(
            f"{cat}={c}" for cat, c in sorted(failure_summary["category_counts"].items()) if cat != "ok"
        )
        rec_note = f" ({r['recovered_failure_count']} recovered)" if r["recovered_failure_count"] else ""
        r["flags"].append(f"FAILURES_DETECTED: {breakdown}{rec_note}")

    return r


def main():
    ap = argparse.ArgumentParser(description="Audit Codex rollout .jsonl logs for duplicate emissions and drift")
    ap.add_argument("paths", nargs="+", help="jsonl files or globs")
    ap.add_argument("--csv", help="also write results to this CSV path")
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
        print(f"  api calls: web_search {r['web_search_calls']} | function {r['function_calls']} "
              f"{dict(r['tools']) if r['tools'] else ''}")
        print(f"  timing: duration {display_duration(r['duration_s'])} | ttft {display_duration(r['ttft_s'])} | file wallclock {display_duration(r['wallclock_s'])}")
        print(f"  tokens {r['tokens_total']} / {r['context_window']}")
        if r["failure_count_total"]:
            print(f"  failures: {r['failure_count_total']} ({r['failure_count_error']} error, {r['failure_count_warning']} warning) | categories: {r['failure_categories']}")
            for msg in r["unknown_error_messages"]:
                print(f"  !! unknown error: {msg}")
        if r["flags"]:
            any_flags = True
            for fl in r["flags"]:
                print(f"  !! {fl}")
        else:
            print("  OK: single emission, no post-completion records, all three copies match")

    if args.csv and results:
        cols = ["file", "session_id", "model", "effort", "test_id",
                "skills_loaded_count", "skill_names", "skill_docs_consumption_loaded",
                "skill_docs_consumption_path", "skill_docs_consumption_desc",
                "skill_path_mentioned", "protocol_prefix", "protocol_prefix_source",
                "skill_language", "skill_language_source",
                "turns", "user_messages",
                "commentary_msgs", "final_answers_event", "final_answers_item", "web_search_calls",
                "function_calls", "task_completes", "records_after_complete", "duration_s",
                "ttft_s", "wallclock_s", "tokens_total", "flags", "failure_count_total",
                "failure_count_error", "failure_count_warning", "failure_categories",
                "recovered_failure_count", "has_failure", "first_failure_category",
                "first_failure_detail", "unknown_error_messages"]
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in results:
                row = {k: r[k] for k in cols if k not in ("flags", "unknown_error_messages")}
                row["flags"] = "; ".join(r["flags"])
                row["unknown_error_messages"] = "; ".join(r["unknown_error_messages"])
                w.writerow(row)
        print(f"\nCSV written to {args.csv}")

    sys.exit(1 if any_flags else 0)


if __name__ == "__main__":
    main()