#!/usr/bin/env python3
"""Classify Codex tool output strings into failure modes.

The Codex JSONL session logs do not emit structured error events. Failures such
as sandboxed DNS blocks, Node fetch failures, missing browsers, and `Cache miss`
responses appear only as plain text inside `function_call_output` records. This
module provides deterministic pattern matching so the harness can detect and
count those failures independently of the agent's own chat summaries.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CATEGORIES = (
    "browser_unavailable",
    "dns_blocked",
    "fetch_failed",
    "sandbox_empty_response",
    "cache_miss",
    "command_not_found",
    "runtime_error",
    "ui_truncation",
    "escalation_recovered",
    "capability_abandonment",
    "unknown_error",
    "ok",
)


SEVERITY = {
    "browser_unavailable": "error",
    "dns_blocked": "error",
    "fetch_failed": "error",
    "sandbox_empty_response": "error",
    "command_not_found": "error",
    "runtime_error": "error",
    "unknown_error": "error",
    "cache_miss": "warning",
    "ui_truncation": "warning",
    "escalation_recovered": "warning",
    "capability_abandonment": "warning",
    "ok": "info",
}


# Patterns are evaluated in order; the first match wins. More specific patterns
# must appear before more general ones.
OUTPUT_PATTERNS: tuple[tuple[str, re.Pattern], ...] = (
    ("browser_unavailable", re.compile(r"Browser\s+is\s+not\s+available\s*:\s*iab", re.I)),
    ("ui_truncation", re.compile(r"Truncated\s+content|was\s+UI-truncated", re.I)),
    (
        "dns_blocked",
        re.compile(r"curl\s*:\s*\(\s*6\s*\).*Could\s+not\s+resolve\s+host", re.I),
    ),
    ("cache_miss", re.compile(r"\bCache\s+miss\b", re.I)),
    ("fetch_failed", re.compile(r"TypeError\s*:\s*fetch\s+failed", re.I)),
    ("fetch_failed", re.compile(r"\bfetch\s+failed\b", re.I)),
    ("fetch_failed", re.compile(r"getaddrinfo\s+ENOTFOUND", re.I)),
    # Other nonzero curl exits (excluding DNS code 6 already handled above).
    ("fetch_failed", re.compile(r"curl\s*:\s*\(\s*[1-9]\d*\s*\)", re.I)),
    ("command_not_found", re.compile(r"Process\s+exited\s+with\s+code\s*127", re.I)),
    (
        "command_not_found",
        # Match standard tracebacks ("ModuleNotFoundError: No module named"),
        # Codex's formatted error line ("ERROR ModuleNotFoundError No module named"),
        # and the exception repr emitted by Codex's python tool
        # ("ModuleNotFoundError('No module named ...')").
        re.compile(r"ModuleNotFoundError[:'\"(\s]*No\s+module\s+named", re.I),
    ),
    ("command_not_found", re.compile(r"\bcommand\s+not\s+found\b", re.I)),
    ("command_not_found", re.compile(r"\bNo\s+such\s+file\s+or\s+directory\b", re.I)),
    ("runtime_error", re.compile(r"Traceback\s+\(most\s+recent\s+call\s+last\)", re.I)),
    ("runtime_error", re.compile(r"HTTP\s+Error\s+\d{3}", re.I)),
    ("runtime_error", re.compile(r"urllib\.error\.HTTPError", re.I)),
)


NONZERO_EXIT_RE = re.compile(r"Process\s+exited\s+with\s+code\s*([1-9]\d*)", re.I)
EXIT_ZERO_RE = re.compile(r"Process\s+exited\s+with\s+code\s*(\d+)", re.I)
OUTPUT_SECTION_RE = re.compile(r"Output\s*:\s*(.*)$", re.I | re.S)


def _looks_like_sandbox_empty_response(text: str) -> bool:
    """Detect Codex sandbox silently blocking a network fetch.

    In the workspace-write sandbox with network disabled, commands such as
    `curl` sometimes exit 0 but return no body. The agent then retries with
    `sandbox_permissions: require_escalated` and succeeds. This heuristic
    matches an exit-0 record whose Output: section is empty, whitespace-only,
    or just `0` (the byte count from `wc -c` when curl produces nothing).

    The check is intentionally conservative: the surrounding metadata must be
    short and must include the standard Codex process-exit line, so normal
    empty outputs from commands like `true` are not flagged.
    """
    if not EXIT_ZERO_RE.search(text):
        return False

    m = EXIT_ZERO_RE.search(text)
    if not m or int(m.group(1)) != 0:
        return False

    # Only consider small outputs; real successful commands that intentionally
    # produce no output are unlikely to include the Codex Chunk/Process headers.
    if len(text) > 500:
        return False

    out_m = OUTPUT_SECTION_RE.search(text)
    if out_m:
        after_output = out_m.group(1).strip()
    else:
        after_output = ""

    # Empty output section, or only whitespace / the literal digit 0.
    if after_output and not re.fullmatch(r"\s*0?\s*", after_output):
        return False

    return True


@dataclass(frozen=True)
class FailureClass:
    """A single failure classification for a tool output."""

    category: str
    detail: str
    severity: str

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"unknown category: {self.category}")

    def to_dict(self) -> dict:
        return {"category": self.category, "detail": self.detail, "severity": self.severity}

    @classmethod
    def ok(cls) -> "FailureClass":
        return cls(category="ok", detail="", severity="info")


def _extract_unknown_error_detail(text: str, exit_code: str) -> str:
    """Return a concise, distinctive message from an unrecognized nonzero output.

    The detail is used as the failure signature in audit CSVs, so it should be
    stable enough to track recurring errors while still surfacing the actual
    error string emitted by the tool.
    """
    m = OUTPUT_SECTION_RE.search(text)
    if m:
        after = m.group(1).strip()
    else:
        after = text.strip()

    lines = [line.strip() for line in after.splitlines() if line.strip()]
    if not lines:
        return f"exit code {exit_code}"

    # Python-style exceptions usually put the exception name/message on the last
    # line; shell one-liners usually report the error on the first line.
    last = lines[-1]
    if re.search(r"\b\w*?(Error|Exception|Failure)\b", last, re.I) or any(
        kw in last.lower() for kw in ("syntaxerror", "unmatched", "refused", "denied", "not found")
    ):
        msg = last
    else:
        msg = lines[0]

    # Normalize whitespace and truncate to keep CSV cells readable.
    msg = " ".join(msg.split())
    if len(msg) > 120:
        msg = msg[:117] + "..."
    return f"exit code {exit_code}: {msg}"


def _flatten_output(output: str | list | dict | None) -> str:
    """Normalize a Codex tool output to a plain string.

    Codex JSONL logs store `function_call_output.output` either as a raw string
    or as a list of content blocks (e.g. `[{"type": "input_text", "text": ...}]`).
    This helper extracts all textual pieces and joins them with newlines.
    """
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        return str(output.get("text", output))
    if isinstance(output, list):
        parts: list[str] = []
        for block in output:
            if isinstance(block, dict):
                text = block.get("text", "")
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(output)


# Regexes for capability-abandonment probes. These map the command text to a
# human-readable capability name and an output shape that indicates the
# capability is unavailable.
_PYTHON_PROBE_RE = re.compile(
    r"find_spec\s*\(\s*['\"](?P<name>[^'\"\s]+)['\"]\s*\)",
    re.I,
)
_SHELL_PROBE_RE = re.compile(
    r"(?:command\s+-v|which)\s+(?P<name>[\w\-:]+)",
    re.I,
)


def _classify_capability_abandonment(
    text: str, command: str | None
) -> FailureClass | None:
    """Detect probes for preferred capabilities that return "not available".

    The agent often checks whether a tool or library exists before using it.
    When the probe exits successfully but reports the capability is missing, the
    agent silently falls back to a less accurate method (e.g., regex token count
    when tiktoken is absent, curl when Browser is unavailable). These are not
    hard errors, but they are behavioral findings worth flagging.
    """
    if not command:
        return None

    # Python library probe: importlib.util.find_spec('X') → False
    m = _PYTHON_PROBE_RE.search(command)
    if m:
        name = m.group("name")
        if re.search(r"Output:\s*\n?\s*False\s*$", text, re.I | re.S):
            return FailureClass(
                category="capability_abandonment",
                detail=f"{name} unavailable; agent used fallback",
                severity=SEVERITY["capability_abandonment"],
            )

    # Shell tool probe: command -v X or which X → empty / not found
    m = _SHELL_PROBE_RE.search(command)
    if m:
        name = m.group("name")
        after = re.split(r"Output\s*:", text, flags=re.I | re.S)[-1].strip()
        if not after or re.search(r"\bnot\s+found\b", after, re.I):
            return FailureClass(
                category="capability_abandonment",
                detail=f"{name} unavailable; agent used fallback",
                severity=SEVERITY["capability_abandonment"],
            )

    return None


def classify_output(
    output: str | list | dict | None,
    tool_name: str | None = None,
    command: str | None = None,
) -> FailureClass:
    """Classify a raw tool output string.

    Args:
        output: The raw text returned by a tool (e.g. `function_call_output`).
                May be a string, a list of content blocks, or a single block dict.
        tool_name: Optional tool name for future disambiguation; currently unused.
        command: Optional shell command or tool input that produced the output.
                 Used to correlate benign-looking outputs (e.g. "False") with the
                 command that generated them.

    Returns:
        A `FailureClass` describing the first matching failure mode, or `ok`.
    """
    _ = tool_name  # reserved for future disambiguation
    text = _flatten_output(output).strip()
    if not text:
        return FailureClass.ok()

    # Capability abandonment: the agent probes for a preferred tool or library,
    # finds it missing, and silently falls back to a less capable method.
    ca = _classify_capability_abandonment(text, command)
    if ca:
        return ca

    for category, pattern in OUTPUT_PATTERNS:
        m = pattern.search(text)
        if m:
            detail = m.group(0)
            if category == "fetch_failed":
                # Surface the curl exit number, if present.
                cm = re.search(r"curl\s*:\s*\(\s*(\d+)\s*\)", text, re.I)
                if cm:
                    detail = f"curl exit {cm.group(1)}"
                elif "getaddrinfo ENOTFOUND" in text:
                    host_m = re.search(r"getaddrinfo\s+ENOTFOUND\s+(\S+)", text, re.I)
                    detail = f"DNS resolution failed: {host_m.group(1)}" if host_m else "DNS resolution failed"
            elif category == "dns_blocked":
                host_m = re.search(r"Could\s+not\s+resolve\s+host\s*:\s*([\w.-]+)", text, re.I)
                detail = f"DNS blocked: {host_m.group(1)}" if host_m else "DNS blocked"
            return FailureClass(
                category=category,
                detail=detail,
                severity=SEVERITY[category],
            )

    # Codex sandbox sometimes silently blocks network commands: the process
    # exits 0 but the body is completely empty. Detect that so recovery via
    # `sandbox_permissions: require_escalated` is still counted as a failure.
    if _looks_like_sandbox_empty_response(text):
        return FailureClass(
            category="sandbox_empty_response",
            detail="sandbox returned empty body with exit code 0",
            severity=SEVERITY["sandbox_empty_response"],
        )

    # If nothing else matched but we have a nonzero shell exit with actual error
    # content, treat it as an unknown error. Empty-output nonzero exits (e.g.
    # `grep` returning 1) are intentionally kept as `ok` to avoid false positives.
    m = NONZERO_EXIT_RE.search(text)
    if m:
        after = text.split("Output:", 1)[-1].strip()
        if len(after) > 6:
            return FailureClass(
                category="unknown_error",
                detail=_extract_unknown_error_detail(text, m.group(1)),
                severity="error",
            )

    return FailureClass.ok()


def recovered(fc: FailureClass) -> FailureClass:
    """Return a copy of ``fc`` denoting that the failure was recovered this turn."""
    if fc.category == "ok":
        return fc
    return FailureClass(
        category="escalation_recovered",
        detail=fc.detail,
        severity=SEVERITY["escalation_recovered"],
    )


def summarize(classes: Iterable[FailureClass]) -> dict:
    """Produce aggregate counts from a sequence of classifications."""
    counts = Counter(fc.category for fc in classes)
    total = sum(counts.values())
    error_count = sum(c for cat, c in counts.items() if SEVERITY.get(cat) == "error")
    warning_count = sum(c for cat, c in counts.items() if SEVERITY.get(cat) == "warning")
    info_count = counts.get("ok", 0)

    # Most common non-ok category.
    top = ""
    for cat, _ in counts.most_common():
        if cat != "ok":
            top = cat
            break

    return {
        "total": total,
        "error_count": error_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "category_counts": dict(counts),
        "top_category": top,
    }


# ─────────────────────────────────────────────────────────────
# Smoke test helpers
# ─────────────────────────────────────────────────────────────

def _extract_sample_outputs(path: Path) -> list[str]:
    """Pull candidate tool-output strings from a Codex rollout JSONL file."""
    outputs: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = rec.get("type")
            p = rec.get("payload", {}) or {}
            pt = p.get("type")

            if t == "response_item" and pt == "function_call_output":
                outputs.append(str(p.get("output", "")))
            elif t == "response_item" and pt == "custom_tool_call_output":
                for block in p.get("output", []) or []:
                    if isinstance(block, dict):
                        outputs.append(str(block.get("text", "")))
            elif t == "event_msg" and pt == "mcp_tool_call_end":
                result = p.get("result") or {}
                ok = result.get("Ok") or {}
                for block in ok.get("content", []) or []:
                    if isinstance(block, dict) and block.get("type") == "text":
                        outputs.append(str(block.get("text", "")))
    return outputs


def _smoke_test() -> int:
    """Run a lightweight sanity check against all available BL-3 rollouts."""
    sample_dir = (
        Path(__file__).resolve().parent.parent
        / "results"
        / "vscode-codex-interpreted"
        / "artifacts"
        / "rollouts"
        / "BL-3"
    )
    samples = sorted(sample_dir.glob("rollout-*.jsonl"))
    if not samples:
        # Fall back to the ~/.codex archived sessions if the repo results are missing.
        archived = Path.home() / ".codex" / "archived_sessions"
        samples = sorted(archived.glob("rollout-*.jsonl"))[:5]

    if not samples:
        print("SMOKE TEST SKIP: no rollout file found", file=sys.stderr)
        return 0

    outputs: list[str] = []
    for sample in samples:
        outputs.extend(_extract_sample_outputs(sample))

    classes = [classify_output(o) for o in outputs]
    summary = summarize(classes)

    print(f"SMOKE TEST: {len(classes)} tool outputs across {len(samples)} file(s)", file=sys.stderr)
    print(f"  categories: {summary['category_counts']}", file=sys.stderr)

    assert summary["category_counts"].get("dns_blocked", 0) >= 1, (
        "expected at least one curl DNS-blocked failure"
    )
    assert summary["category_counts"].get("ok", 0) >= 1, (
        "expected at least one successful tool output"
    )
    print("SMOKE TEST PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(_smoke_test())
    except AssertionError as exc:
        print(f"SMOKE TEST FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
