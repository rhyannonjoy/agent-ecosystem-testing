#!/usr/bin/env python3
"""
T3 Docs-Consumption Skill Analysis

Analyzes new-style EC-6 vscode-codex-interpreted flash results. Joins the
self-reported `results.csv` with the structured `rollout_audit.csv` and
`memory_audit.csv` outputs by `session_id`.

Usage:
    python3 scripts/T3_docs_consumption_skill_analysis.py \
        --results results/docs-consumption-skill-flash/results.csv \
        --rollout results/docs-consumption-skill-flash/artifacts/rollouts/audit.csv \
        --memory results/docs-consumption-skill-flash/artifacts/memory_audit.csv \
        --output report.md
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Optional


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


def generate_report(
    results: list[dict],
    rollout_by_sid: dict[str, dict],
    memory_by_sid: dict[str, dict],
    output_path: Optional[Path] = None,
) -> str:
    # Filter to EC-6 T2 new schema rows
    ec6 = [
        r for r in results
        if r.get("test_id") == "EC-6"
        and r.get("track") == "vscode-codex-interpreted"
    ]

    lines = [
        "# T3 Docs-Consumption Skill Analysis",
        "",
        f"**EC-6 T2 rows analyzed:** {len(ec6)}",
        "",
    ]

    # --- Results.csv counts ---
    lines.append("## Self-reported skill compliance")
    lines.append("")
    compliance_counts = count_values(ec6, "skill_compliance")
    if compliance_counts:
        lines.append(markdown_table(
            ["Skill compliance", "Count"],
            [[k, str(v)] for k, v in sorted(compliance_counts.items())],
        ))
    else:
        lines.append("_No skill_compliance values logged._")
    lines.append("")

    lines.append("## False-positive / attribution summaries")
    lines.append("")
    fp_counts = count_values(ec6, "false_positive")
    if fp_counts:
        lines.append(markdown_table(
            ["False-positive summary", "Count"],
            [[k, str(v)] for k, v in sorted(fp_counts.items())],
        ))
    else:
        lines.append("_No false_positive values logged._")
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
            ["Skill loaded", str(loaded.get("true", 0)), str(loaded.get("false", 0)), str(len(ec6) - sum(loaded.values()))],
            ["Protocol prefix used", str(prefix.get("yes", 0)), str(prefix.get("no", 0)), str(len(ec6) - sum(prefix.values()))],
            ["Skill language used", str(lang.get("true", 0)), str(lang.get("false", 0)), str(len(ec6) - sum(lang.values()))],
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
            ["System memory instruction", str(mem_inst.get("true", 0)), str(mem_inst.get("false", 0)), str(len(ec6) - sum(mem_inst.values()))],
            ["Single-url-retrieval skill referenced", str(single_url.get("true", 0)), str(single_url.get("false", 0)), str(len(ec6) - sum(single_url.values()))],
            ["Docs-consumption loaded", str(docs_loaded.get("true", 0)), str(docs_loaded.get("false", 0)), str(len(ec6) - sum(docs_loaded.values()))],
        ],
    ))
    lines.append("")

    # --- Joined per-run table ---
    lines.append("## Per-run join")
    lines.append("")
    lines.append(
        markdown_table(
            ["Session", "Model", "Level", "Skill compliance", "False positive", "Loaded", "Prefix", "Skill lang", "Memory inst", "Single-url skill"],
            [
                [
                    r.get("session_id", "")[:20],
                    r.get("model_observed", "") or rollout_by_sid.get(sid, {}).get("model", ""),
                    r.get("model_intelligence_level", "") or rollout_by_sid.get(sid, {}).get("effort", ""),
                    r.get("skill_compliance", "") or "—",
                    r.get("false_positive", "") or "—",
                    rollout_by_sid.get(sid, {}).get("skill_docs_consumption_loaded", "") or "—",
                    rollout_by_sid.get(sid, {}).get("protocol_prefix", "") or rollout_by_sid.get(sid, {}).get("protocol_prefix", "") or "—",
                    rollout_by_sid.get(sid, {}).get("skill_language", "") or "—",
                    memory_by_sid.get(sid, {}).get("system_memory_instruction", "") or "—",
                    memory_by_sid.get(sid, {}).get("single_url_retrieval_skill", "") or "—",
                ]
                for r in ec6
                for sid in [normalize_session_id(r.get("session_id", ""))]
            ],
        )
    )
    lines.append("")

    # --- Example notes ---
    lines.append("## Example self-reported details")
    lines.append("")
    for r in ec6:
        sid = r.get("session_id", "")[:20] or "unknown"
        lines.append(f"### {sid}")
        for field in ["completeness", "errors", "exec_completeness", "reframing", "fix", "false_positive"]:
            value = (r.get(field) or "").strip()
            if value:
                lines.append(f"- **{field}:** {value}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze T3 docs-consumption skill flash results"
    )
    parser.add_argument("--results", type=Path, required=True, help="Path to results.csv")
    parser.add_argument("--rollout", type=Path, help="Path to rollout_audit.csv")
    parser.add_argument("--memory", type=Path, help="Path to memory_audit.csv")
    parser.add_argument("--output", type=Path, help="Optional path to write Markdown report")
    args = parser.parse_args()

    results = load_csv(args.results)
    rollout_by_sid = index_rows(load_csv(args.rollout)) if args.rollout else {}
    memory_by_sid = index_rows(load_csv(args.memory)) if args.memory else {}

    report = generate_report(results, rollout_by_sid, memory_by_sid, args.output)
    print(report)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"\nReport written to {args.output}")


if __name__ == "__main__":
    main()
