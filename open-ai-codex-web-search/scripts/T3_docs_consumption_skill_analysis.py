#!/usr/bin/env python3
"""
T3 Docs-Consumption Skill Analysis

Analyzes new-style EC-6 vscode-codex-interpreted flash results. Joins the
self-reported `results.csv` with the structured `rollout_audit.csv` and
`memory_audit.csv` outputs by `session_id`.

Usage:
    python3 scripts/T3_docs_consumption_skill_analysis.py \
        --results results/docs-consumption-skill-flash/T3-results.csv \
        --rollout results/docs-consumption-skill-flash/artifacts/rollouts/T3-skill-on-memories-suppressed/audit.csv \
        --memory results/docs-consumption-skill-flash/artifacts/rollouts/T3-skill-on-memories-suppressed/memory-analysis/T3_memory_audit.csv

The report defaults to `T3_report.md` next to the results CSV. Pass --output to
override.
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Optional


# Sentinel used in place of an em dash for missing or empty values.
EMPTY = "none"


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        print(f"Warning: CSV not found: {path}", file=sys.stderr)
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def normalize_session_id(value: str) -> str:
    return (value or "").strip().lower()


def index_rows(rows: list[dict], key: str = "session_id") -> dict[str, dict]:
    out = {}
    for r in rows:
        sid = normalize_session_id(r.get(key, ""))
        if sid:
            out[sid] = r
    return out


def count_values(rows: list[dict], field: str) -> Counter:
    return Counter((r.get(field) or "").strip() for r in rows if r.get(field))


def markdown_table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _cell(value: str) -> str:
    """Render a single per-run cell, backticking code-like values."""
    v = (value or "").strip()
    if not v or v == "—":
        return EMPTY
    return f"`{v}`"


def _bool_cell(value: str) -> str:
    """Render a boolean-ish cell as a backticked canonical token."""
    v = (value or "").strip().lower()
    if not v:
        return EMPTY
    return f"`{v}`"


def _prefix_cell(value: str) -> str:
    """Render the protocol prefix cell, stripping the trailing colon."""
    v = (value or "").strip()
    if not v or v == "—":
        return EMPTY
    # Some prefixes arrive as 'COMPLETE:' or 'PARTIAL:'. Keep just the keyword.
    v = v.rstrip(":")
    return f"`{v}`" if v else EMPTY


def generate_report(
    results: list[dict],
    rollout_by_sid: dict[str, dict],
    memory_by_sid: dict[str, dict],
    output_path: Optional[Path] = None,
) -> str:
    # Filter to EC-6 T3 new schema rows
    ec6 = [
        r for r in results
        if r.get("test_id") == "EC-6"
        and r.get("track") == "vscode-codex-interpreted"
    ]

    lines: list[str] = [
        "# T3 Docs-Consumption Skill Analysis",
        "",
        f"**EC-6 T3 rows analyzed:** {len(ec6)}",
        "",
    ]

    # --- Results.csv counts ---
    lines.append("## Self-reported skill compliance")
    lines.append("")
    compliance_counts = count_values(ec6, "skill_compliance")
    if compliance_counts:
        lines.append(markdown_table(
            ["Skill compliance", "Count"],
            [[f"`{k}`", str(v)] for k, v in sorted(compliance_counts.items())],
        ))
    else:
        lines.append("_No `skill_compliance` values logged._")
    lines.append("")

    lines.append("## False-positive / attribution summaries")
    lines.append("")
    fp_counts = count_values(ec6, "false_positive")
    if fp_counts:
        lines.append(markdown_table(
            ["False-positive summary", "Count"],
            [[f"`{k}`", str(v)] for k, v in sorted(fp_counts.items())],
        ))
    else:
        lines.append("_No `false_positive` values logged._")
    lines.append("")

    # --- Rollout audit counts ---
    lines.append("## Rollout audit signals")
    lines.append("")
    rollout_rows = [rollout_by_sid.get(normalize_session_id(r.get("session_id", ""))) for r in ec6]
    rollout_rows = [r for r in rollout_rows if r]

    def rollout_count(field: str) -> Counter:
        return Counter((r.get(field) or "").strip().lower() for r in rollout_rows if r.get(field))

    loaded = rollout_count("skill_docs_consumption_loaded")
    prefix = rollout_count("protocol_prefix")
    lang = rollout_count("skill_language")

    lines.append(markdown_table(
        ["Signal", "Yes", "No", "Empty"],
        [
            ["skill loaded", str(loaded.get("true", 0)), str(loaded.get("false", 0)), str(len(ec6) - sum(loaded.values()))],
            ["prefix used", str(prefix.get("yes", 0)), str(prefix.get("no", 0)), str(len(ec6) - sum(prefix.values()))],
            ["skill lang", str(lang.get("true", 0)), str(lang.get("false", 0)), str(len(ec6) - sum(lang.values()))],
        ],
    ))
    lines.append("")

    # --- Memory audit counts ---
    lines.append("## Memory audit signals")
    lines.append("")
    memory_rows = [memory_by_sid.get(normalize_session_id(r.get("session_id", ""))) for r in ec6]
    memory_rows = [r for r in memory_rows if r]

    def memory_count(field: str) -> Counter:
        return Counter((r.get(field) or "").strip().lower() for r in memory_rows if r.get(field))

    mem_inst = memory_count("system_memory_instruction")
    single_url = memory_count("single_url_retrieval_skill")
    docs_loaded = memory_count("docs_consumption_loaded")

    lines.append(markdown_table(
        ["Signal", "Yes", "No", "Empty"],
        [
            ["mem instr", str(mem_inst.get("true", 0)), str(mem_inst.get("false", 0)), str(len(ec6) - sum(mem_inst.values()))],
            ["single-url skill", str(single_url.get("true", 0)), str(single_url.get("false", 0)), str(len(ec6) - sum(single_url.values()))],
            ["docs loaded", str(docs_loaded.get("true", 0)), str(docs_loaded.get("false", 0)), str(len(ec6) - sum(docs_loaded.values()))],
        ],
    ))
    lines.append("")

    # --- Joined per-run table ---
    lines.append("## Per-run join")
    lines.append("")

    def _model_cell(r: dict, sid: str) -> str:
        v = (r.get("model_observed", "") or rollout_by_sid.get(sid, {}).get("model", "") or "").strip()
        return f"`{v}`" if v else EMPTY

    def _level_cell(r: dict, sid: str) -> str:
        v = (r.get("model_intelligence_level", "") or rollout_by_sid.get(sid, {}).get("effort", "") or "").strip()
        return f"`{v}`" if v else EMPTY

    per_run_rows: list[list[str]] = []
    for r in ec6:
        sid = normalize_session_id(r.get("session_id", ""))
        rollout = rollout_by_sid.get(sid, {})
        memory = memory_by_sid.get(sid, {})
        per_run_rows.append([
            f"`{r.get('session_id', '')[:20]}`" if r.get("session_id") else EMPTY,
            _model_cell(r, sid),
            _level_cell(r, sid),
            _cell(r.get("skill_compliance", "")),
            _cell(r.get("false_positive", "")),
            _bool_cell(rollout.get("skill_docs_consumption_loaded", "")),
            _prefix_cell(rollout.get("protocol_prefix", "")),
            _bool_cell(rollout.get("skill_language", "")),
            _bool_cell(memory.get("system_memory_instruction", "")),
            _bool_cell(memory.get("single_url_retrieval_skill", "")),
        ])

    lines.append(
        markdown_table(
            ["Session", "Model", "Level", "compliance", "false positive", "loaded", "prefix", "skill lang", "mem instr", "single-url skill"],
            per_run_rows,
        )
    )
    lines.append("")

    # --- Example notes ---
    lines.append("## Example self-reported details")
    lines.append("")
    for r in ec6:
        sid = r.get("session_id", "")[:20] or "unknown"
        lines.append(f"### `{sid}`")
        lines.append("")
        for field in ["completeness", "errors", "exec_completeness", "reframing", "fix", "false_positive"]:
            value = (r.get(field) or "").strip()
            if value:
                lines.append(f"- **{field}:** `{value}`")
        lines.append("")

    return "\n".join(lines)


def _default_output(results_path: Path) -> Path:
    """Default report path is `T3_report.md` next to the results CSV."""
    return results_path.parent / "T3_report.md"


def main():
    parser = argparse.ArgumentParser(
        description="Analyze T3 docs-consumption skill flash results"
    )
    parser.add_argument("--results", type=Path, required=True, help="Path to results.csv")
    parser.add_argument("--rollout", type=Path, help="Path to rollout_audit.csv")
    parser.add_argument("--memory", type=Path, help="Path to memory_audit.csv")
    parser.add_argument(
        "--output", type=Path,
        help="Optional path to write Markdown report. Defaults to T3_report.md next to the results CSV.",
    )
    args = parser.parse_args()

    results = load_csv(args.results)
    rollout_by_sid = index_rows(load_csv(args.rollout)) if args.rollout else {}
    memory_by_sid = index_rows(load_csv(args.memory)) if args.memory else {}

    report = generate_report(results, rollout_by_sid, memory_by_sid, args.output)
    print(report)

    out_path = args.output if args.output else _default_output(args.results)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"\nReport written to {out_path}")


if __name__ == "__main__":
    main()
