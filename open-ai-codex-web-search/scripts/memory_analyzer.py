#!/usr/bin/env python3
"""Read a memory_audit.csv and print a readable memory-vs-skill comparison.

Usage:
    python3 scripts/memory_analyzer.py \
        results/docs-consumption-skill-flash/artifacts/memory_audit.csv

Output is a plain-text / Markdown friendly report sent to stdout.
"""

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


MEMORY_SIGNAL_COLS = [
    "memory_dot_codex_path",
    "memory_md_file",
    "raw_memories_file",
    "memory_summary_file",
    "rollout_summaries_dir",
    "single_url_retrieval_skill",
    "memory_skills_dir",
    "memory_mentioned",
]

SKILL_SIGNAL_COLS = [
    "docs_consumption_loaded",
    "docs_consumption_name_mentioned",
    "docs_consumption_path_mentioned",
    "protocol_prefix",
    "skill_language",
]

# The audit emits a separate `system_memory_instruction` flag that detects the
# system `## Memory` prompt, independent of content matches in `.codex/memories`.
SYSTEM_MEMORY_INSTRUCTION_COL = "system_memory_instruction"

# Friendlier labels for the `memory_sources` column. `system` means a memory
# path matched inside the system `## Memory` block; `system_instruction` means
# the `## Memory` header itself was detected.
MEMORY_SOURCE_LABELS = {
    "system": "system_prompt, ## Memory block",
    "system_instruction": "system_memory_instruction header",
    "commentary": "commentary",
    "reasoning": "reasoning",
    "final_answer": "final_answer",
    "tool_output": "tool_output",
}


def _bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _parse_sources(value: str) -> list[str]:
    return [s.strip() for s in value.split(",") if s.strip()]


def _extract_datetime(filename: str) -> str | None:
    """Return ISO-ish timestamp from a rollout filename like
    rollout-2026-07-09T12-34-04-....jsonl
    """
    m = re.search(r"rollout-(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})", filename)
    if not m:
        return None
    return f"{m.group(1)} {m.group(2)}:{m.group(3)}:{m.group(4)}"


def _extract_date(filename: str) -> str | None:
    m = re.search(r"rollout-(\d{4}-\d{2}-\d{2})T", filename)
    return m.group(1) if m else None


def _model_display(model: str) -> str:
    # e.g. "gpt-5.4-mini" -> "GPT-5.4 Mini", "gpt-5.4" -> "GPT-5.4"
    base = model.replace("gpt-", "GPT-")
    idx = base.rfind("-")
    if idx <= 3:  # only the GPT- prefix hyphen, no separate model suffix
        return base
    return base[:idx] + " " + base[idx + 1 :].capitalize()


def _pct(num: int, denom: int) -> str:
    if denom == 0:
        return "—"
    return f"{num}/{denom} — {round(100 * num / denom)}%"


def main():
    ap = argparse.ArgumentParser(
        description="Summarize a memory_audit.csv as a readable comparison"
    )
    ap.add_argument("csv", help="Path to memory_audit.csv")
    args = ap.parse_args()

    path = Path(args.csv)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # Normalize booleans
            for col in MEMORY_SIGNAL_COLS + [
                "docs_consumption_loaded",
                "docs_consumption_name_mentioned",
                "docs_consumption_path_mentioned",
                "skill_language",
                SYSTEM_MEMORY_INSTRUCTION_COL,
            ]:
                row[col] = _bool(row.get(col, "false"))
            row["memory_positive"] = any(row[col] for col in MEMORY_SIGNAL_COLS)
            # Strict skill engagement: loaded by system, named by the agent,
            # or the formal COMPLETE/PARTIAL/UNVERIFIABLE prefix was used.
            # We deliberately do NOT count broad skill_language here; that is
            # reported separately because it can match natural retrieval language
            # even when the skill is not in use.
            row["skill_positive"] = any([
                row["docs_consumption_loaded"],
                row["docs_consumption_name_mentioned"],
                row["docs_consumption_path_mentioned"],
                bool(row.get("protocol_prefix", "")),
            ])
            row["memory_sources_list"] = _parse_sources(row.get("memory_sources", ""))
            row["skill_sources_list"] = _parse_sources(row.get("skill_sources", ""))
            row["datetime"] = _extract_datetime(row["file"])
            row["date"] = _extract_date(row["file"])
            rows.append(row)

    total = len(rows)
    if total == 0:
        print("No rows found in CSV.")
        sys.exit(0)

    # ---- Overall co-occurrence ---------------------------------------------
    memory_only = sum(1 for r in rows if r["memory_positive"] and not r["skill_positive"])
    skill_only = sum(1 for r in rows if r["skill_positive"] and not r["memory_positive"])
    both = sum(1 for r in rows if r["memory_positive"] and r["skill_positive"])
    neither = sum(1 for r in rows if not r["memory_positive"] and not r["skill_positive"])
    memory_any = sum(1 for r in rows if r["memory_positive"])
    skill_any = sum(1 for r in rows if r["skill_positive"])

    print("# Memory vs. Workspace Docs-Consumption Skill Audit")
    print(f"\nTotal sessions: **{total}**")
    print()
    print(
        "*Memory* = any `.codex/memories` content, including the competing "
        "`single-url-retrieval-measurement` skill."
    )
    print(
        "*Workspace skill* = the repository's `.agents/skills/docs-consumption/SKILL.md`. "
        "The agent loads it through the developer `<skills_instructions>` block, names it, "
        "mentions its path, or uses a COMPLETE/PARTIAL/UNVERIFIABLE prefix."
    )
    print(
        "*Memory skill delivery* = Codex doesn't list the `single-url-retrieval-measurement` "
        "skill in the `<skills_instructions>` block. Instead, it delivers that skill through "
        "the separate system `## Memory` instruction, which tells the agent it has access to a "
        "memory folder and should use it by default."
    )
    print("\n## Overall Co-occurrence")
    print()
    print(f"- Memory signals: {_pct(memory_any, total)}")
    print(f"- Workspace skill signals: {_pct(skill_any, total)}")
    print(f"- Both memory and workspace skill: {_pct(both, total)}")
    print(f"- Memory only: {_pct(memory_only, total)}")
    print(f"- Workspace skill only, no `.codex/memories` detected: {_pct(skill_only, total)}")
    print(f"- Neither: {_pct(neither, total)}")

    # ---- Memory sources ----------------------------------------------------
    print("\n## Memory Sources")
    print()
    print(
        "This table shows where memory-related content appeared in memory-positive runs. "
        "`system_memory_instruction` marks the separate `## Memory` system prompt. "
        "`system_prompt` marks the same block where a concrete path like `.codex/memories` "
        "matched."
    )
    memory_source_counts = Counter()
    for r in rows:
        if r["memory_positive"]:
            memory_source_counts.update(r["memory_sources_list"])
    print(f"\n| Source | Count | % of memory-positive — {memory_any}")
    print("| --- | --- | ---")
    for source, count in memory_source_counts.most_common():
        label = MEMORY_SOURCE_LABELS.get(source, source)
        print(f"| {label} | {count} | {round(100 * count / memory_any)}%")

    # ---- Skill signals -----------------------------------------------------
    print("\n## Workspace Docs-Consumption Skill Signal Breakdown")
    print()
    print(f"| Signal | Count | % of all runs")
    print("| --- | --- | ---")
    skill_counts = {
        "docs-consumption loaded": sum(1 for r in rows if r["docs_consumption_loaded"]),
        "name mentioned by agent": sum(1 for r in rows if r["docs_consumption_name_mentioned"]),
        "path mentioned by agent": sum(1 for r in rows if r["docs_consumption_path_mentioned"]),
        "protocol prefix used": sum(1 for r in rows if bool(r.get("protocol_prefix"))),
        "skill language used": sum(1 for r in rows if r["skill_language"]),
    }
    for label, count in skill_counts.items():
        print(f"| {label} | {count} | {round(100 * count / total)}%")

    # ---- Per-model comparison ----------------------------------------------
    print("\n## Per-Model Comparison")
    print()
    print(f"| Model | Runs | Memory+ | Workspace Skill+ | Both | Memory-only | Workspace-only | Neither |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)

    for model in sorted(by_model.keys()):
        m_rows = by_model[model]
        m_total = len(m_rows)
        m_mem = sum(1 for r in m_rows if r["memory_positive"])
        m_skill = sum(1 for r in m_rows if r["skill_positive"])
        m_both = sum(1 for r in m_rows if r["memory_positive"] and r["skill_positive"])
        m_mem_only = sum(1 for r in m_rows if r["memory_positive"] and not r["skill_positive"])
        m_skill_only = sum(1 for r in m_rows if r["skill_positive"] and not r["memory_positive"])
        m_neither = sum(1 for r in m_rows if not r["memory_positive"] and not r["skill_positive"])
        print(
            f"| {_model_display(model)} | {m_total} | {m_mem} | {m_skill} | {m_both} | "
            f"{m_mem_only} | {m_skill_only} | {m_neither} |"
        )

    # ---- Competing skills: skills block vs. system memory instruction -----
    print("\n## Competing Skills: System Skills Block vs. System Memory Instruction")
    print()
    print(
        "Codex loads the workspace `docs-consumption` skill through the developer "
        "`<skills_instructions>` block. It doesn't list the `single-url-retrieval-measurement` "
        "skill there. Instead, it delivers that skill through the separate system `## Memory` "
        "instruction, which tells the agent it has access to a memory folder and should use it "
        "by default. The 'referenced' row counts runs where that instruction was present **and** "
        "the agent read or cited the memory skill or folder."
    )
    print(f"\n| Condition | Count | % of all runs")
    print("| --- | --- | ---")
    docs_loaded = sum(1 for r in rows if r["docs_consumption_loaded"])
    memory_instr_present = sum(1 for r in rows if r[SYSTEM_MEMORY_INSTRUCTION_COL])
    memory_skill_referenced = sum(
        1 for r in rows if r[SYSTEM_MEMORY_INSTRUCTION_COL] and r["single_url_retrieval_skill"]
    )
    both_present = sum(
        1 for r in rows if r["docs_consumption_loaded"] and r[SYSTEM_MEMORY_INSTRUCTION_COL]
    )
    docs_only = sum(
        1 for r in rows if r["docs_consumption_loaded"] and not r[SYSTEM_MEMORY_INSTRUCTION_COL]
    )
    memory_instr_only = sum(
        1 for r in rows if r[SYSTEM_MEMORY_INSTRUCTION_COL] and not r["docs_consumption_loaded"]
    )
    print(f"| docs-consumption loaded — system skills block | {docs_loaded} | {round(100 * docs_loaded / total)}%")
    print(f"| system `## Memory` instruction present | {memory_instr_present} | {round(100 * memory_instr_present / total)}%")
    print(f"| single-url-retrieval-measurement referenced — system-instructed and agent-read | {memory_skill_referenced} | {round(100 * memory_skill_referenced / total)}%")
    print(f"| Both present | {both_present} | {round(100 * both_present / total)}%")
    print(f"| docs-consumption only | {docs_only} | {round(100 * docs_only / total)}%")
    print(f"| memory-instructed only | {memory_instr_only} | {round(100 * memory_instr_only / total)}%")

    # ---- GPT-5.4 Mini early vs late split ----------------------------------
    mini_rows = [r for r in rows if r["model"] == "gpt-5.4-mini"]
    if mini_rows:
        mini_rows_sorted = sorted(mini_rows, key=lambda r: r["datetime"] or "")
        print("\n## GPT-5.4 Mini Early vs. Late Split")
        print()
        print(
            "The first four Mini rollouts, from the morning of 2026-07-09, show no memory "
            "signals. The later five load the workspace skill consistently, but memory "
            "references appear only in the last two — 18:51 and 19:06."
        )
        print(f"\n| Period | Runs | Memory+ | Workspace Skill+ | Both | Memory-only | Workspace-only | Neither |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for label, subset in [("Early", mini_rows_sorted[:4]), ("Late", mini_rows_sorted[4:])]:
            s_total = len(subset)
            s_mem = sum(1 for r in subset if r["memory_positive"])
            s_skill = sum(1 for r in subset if r["skill_positive"])
            s_both = sum(1 for r in subset if r["memory_positive"] and r["skill_positive"])
            s_mem_only = sum(1 for r in subset if r["memory_positive"] and not r["skill_positive"])
            s_skill_only = sum(1 for r in subset if r["skill_positive"] and not r["memory_positive"])
            s_neither = sum(1 for r in subset if not r["memory_positive"] and not r["skill_positive"])
            print(
                f"| {label} | {s_total} | {s_mem} | {s_skill} | {s_both} | "
                f"{s_mem_only} | {s_skill_only} | {s_neither} |"
            )

    # ---- Notable edge cases ------------------------------------------------
    print("\n## Edge Cases")
    print()

    def _row_label(r):
        effort = r["effort"]
        if effort == "xhigh":
            effort = "extra-high"
        return f"{_model_display(r['model'])} — {effort}"

    memory_only_rows = [r for r in rows if r["memory_positive"] and not r["skill_positive"]]
    if memory_only_rows:
        print("\n### Memory-only sessions — no workspace docs-consumption signal")
        print()
        for r in memory_only_rows:
            print(f"- `{r['file']}` — {_row_label(r)}")
    else:
        print("\n### Memory-only sessions")
        print()
        print("- None")

    skill_only_rows = [r for r in rows if r["skill_positive"] and not r["memory_positive"]]
    if skill_only_rows:
        print("\n### Workspace-skill-only sessions — no `.codex/memories` detected")
        print()
        for r in skill_only_rows:
            print(f"- `{r['file']}` — {_row_label(r)}")
    else:
        print("\n### Workspace-skill-only sessions")
        print()
        print("- None")

    no_prefix_rows = [r for r in rows if r["docs_consumption_loaded"] and not r.get("protocol_prefix")]
    if no_prefix_rows:
        print(f"\n### Sessions where docs-consumption loaded but no COMPLETE/PARTIAL/UNVERIFIABLE prefix: {len(no_prefix_rows)}")
        print()
        for r in no_prefix_rows:
            print(f"- `{r['file']}` — {_row_label(r)}")

    print()


if __name__ == "__main__":
    main()
