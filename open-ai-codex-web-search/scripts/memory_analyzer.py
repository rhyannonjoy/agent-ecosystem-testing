#!/usr/bin/env python3
"""Read a memory_audit.csv and write a readable memory-vs-skill comparison.

Usage:
    python3 scripts/memory_analyzer.py \
        results/docs-consumption-skill-flash/artifacts/rollouts/T3-skill-on-memories-suppressed/memory-analysis/T3_memory_audit.csv

Writes a Markdown report next to the input CSV (e.g. T3_memory_analyzer_report.md).
Pass --output to override the destination. The report is also printed to stdout.
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
    # Percentage first, then the raw fraction. No em dashes.
    if denom == 0:
        return "0% 0/0"
    return f"{round(100 * num / denom)}% {num}/{denom}"


REPORT_MEMORY_CITATIONS_RE = re.compile(
    r"\bmemory\s+citations?\b", re.IGNORECASE
)


def _normalize_model(value: str) -> str:
    """Normalize model names so rollout 'gpt-5.4-mini' matches 'GPT-5.4 Mini'."""
    return value.lower().replace(" ", "-").strip()


def _normalize_effort(value: str) -> str:
    """Normalize effort strings between audit and results.csv."""
    e = value.lower().strip()
    if e in ("light/low", "low"):
        return "low"
    if e in ("extra-high", "xhigh"):
        return "xhigh"
    if e in ("medium", "high", "ultra"):
        return e
    return e


def _load_notes_by_group(notes_csv: Path) -> dict[tuple[str, str], list[str]]:
    """Load results.csv notes grouped by (model, effort) and sorted by timestamp.

    Audit rows and results.csv rows share the same (model, effort) distribution,
    but may be ordered differently within a group. We join by group and sort
    each group by timestamp so the i-th audit row in a group maps to the i-th
    results.csv row in the same group.
    """
    groups: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    with open(notes_csv, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            model = _normalize_model(row.get("model_observed", ""))
            effort = _normalize_effort(row.get("model_intelligence_level", ""))
            ts = row.get("timestamp", "").strip()
            groups[(model, effort)].append((ts, row.get("notes", "")))
    sorted_groups: dict[tuple[str, str], list[str]] = {}
    for key, items in groups.items():
        sorted_groups[key] = [notes for _ts, notes in sorted(items)]
    return sorted_groups


def _default_output(csv_path: Path) -> Path:
    """Derive a Markdown report path next to the input CSV.

    T3_memory_audit.csv -> T3_memory_analyzer_report.md
    memory.csv          -> memory_analyzer_report.md
    """
    stem = csv_path.stem
    if stem.endswith("_audit"):
        stem = stem[: -len("_audit")] + "_analyzer_report"
    else:
        stem = stem + "_analyzer_report"
    return csv_path.with_name(stem + ".md")


def main():
    ap = argparse.ArgumentParser(
        description="Summarize a memory_audit.csv as a readable comparison"
    )
    ap.add_argument("csv", help="Path to memory_audit.csv")
    ap.add_argument(
        "--notes-csv",
        help="Path to results.csv containing observer notes; used to derive report_memory_citations",
    )
    ap.add_argument(
        "-o", "--output",
        help="Path to write the Markdown report. Defaults to <csv_stem>_analyzer_report.md next to the CSV.",
    )
    args = ap.parse_args()

    path = Path(args.csv)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    notes_by_group: dict[tuple[str, str], list[str]] = {}
    if args.notes_csv:
        notes_path = Path(args.notes_csv)
        if not notes_path.exists():
            print(f"Notes CSV not found: {notes_path}", file=sys.stderr)
            sys.exit(1)
        notes_by_group = _load_notes_by_group(notes_path)

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

            # Note-derived signals from observer report; joined by (model, effort)
            # group and sorted by rollout/observation timestamp.
            group_key = (_normalize_model(row.get("model", "")), _normalize_effort(row.get("effort", "")))
            group_notes = notes_by_group.get(group_key, [])
            notes = group_notes.pop(0) if group_notes else ""
            row["report_memory_citations"] = bool(
                REPORT_MEMORY_CITATIONS_RE.search(notes)
            )

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

    out: list[str] = []

    def emit(s: str = "") -> None:
        out.append(s)

    emit("# Memory vs. Workspace Docs-Consumption Skill Audit")
    emit(f"\nTotal sessions: **{total}**")
    emit()
    emit(
        "_Memory_ = any `.codex/memories` content, including the competing "
        "`single-url-retrieval-measurement` skill."
    )
    emit(
        "_Workspace skill_ = the repository's `.agents/skills/docs-consumption/SKILL.md`. "
        "The agent loads it through the developer `<skills_instructions>` block, names it, "
        "mentions its path, or uses a `COMPLETE/PARTIAL/UNVERIFIABLE` prefix."
    )
    emit(
        "_Memory skill delivery_ = Codex doesn't list the `single-url-retrieval-measurement` "
        "skill in the `<skills_instructions>` block. Instead, it delivers that skill through "
        "the separate system `## Memory` instruction, which tells the agent it has access to a "
        "memory folder and should use it by default."
    )

    emit("\n## Overall Co-occurrence")
    emit()
    emit(f"- Memory signals: {_pct(memory_any, total)}")
    emit(f"- Workspace skill signals: {_pct(skill_any, total)}")
    emit(f"- Both memory and workspace skill: {_pct(both, total)}")
    emit(f"- Memory only: {_pct(memory_only, total)}")
    emit(f"- Workspace skill only, no `.codex/memories` detected: {_pct(skill_only, total)}")
    emit(f"- Neither: {_pct(neither, total)}")

    # ---- Memory sources ----------------------------------------------------
    emit("\n## Memory Sources")
    emit()
    emit(
        "This table shows where memory-related content appeared in memory-positive runs. "
        "`system_memory_instruction` marks the separate `## Memory` system prompt. "
        "`system_prompt` marks the same block where a concrete path like `.codex/memories` "
        "matched. `report notes` are derived from the observer-written `results.csv` notes "
        "field, not from the rollout logs."
    )
    memory_source_counts = Counter()
    for r in rows:
        if r["memory_positive"]:
            memory_source_counts.update(r["memory_sources_list"])
    emit(f"\n| Source | Count | % of memory-positive: {memory_any} |")
    emit("| --- | --- | --- |")
    for source, count in memory_source_counts.most_common():
        label = MEMORY_SOURCE_LABELS.get(source, source)
        emit(f"| {label} | {count} | {round(100 * count / memory_any)}% |")
    if args.notes_csv:
        report_mem_cits = sum(1 for r in rows if r["memory_positive"] and r["report_memory_citations"])
        emit(f"| report notes: memory citations | {report_mem_cits} | {round(100 * report_mem_cits / memory_any)}% |")

    # ---- Skill signals -----------------------------------------------------
    emit("\n## Workspace Docs-Consumption Skill Signal Breakdown")
    emit()
    emit("| Signal | Count | % of all runs |")
    emit("| --- | --- | --- |")
    skill_counts = {
        "`docs-consumption` loaded": sum(1 for r in rows if r["docs_consumption_loaded"]),
        "name mentioned by agent": sum(1 for r in rows if r["docs_consumption_name_mentioned"]),
        "path mentioned by agent": sum(1 for r in rows if r["docs_consumption_path_mentioned"]),
        "protocol prefix used": sum(1 for r in rows if bool(r.get("protocol_prefix"))),
        "skill language used": sum(1 for r in rows if r["skill_language"]),
    }
    for label, count in skill_counts.items():
        emit(f"| {label} | {count} | {round(100 * count / total)}% |")

    # ---- Per-model comparison ----------------------------------------------
    emit("\n## Per-Model Comparison")
    emit()
    emit("| Model | Runs | Memory+ | Workspace Skill+ | Both | Memory-only | Workspace-only | Neither |")
    emit("| --- | --- | --- | --- | --- | --- | --- | --- |")
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
        emit(
            f"| `{_model_display(model)}` | {m_total} | {m_mem} | {m_skill} | {m_both} | "
            f"{m_mem_only} | {m_skill_only} | {m_neither} |"
        )

    # ---- Competing skills: skills block vs. system memory instruction -----
    emit("\n## Competing Skills: System Skills Block vs. System Memory Instruction")
    emit()
    emit(
        "Codex loads the workspace `docs-consumption` skill through the developer "
        "`<skills_instructions>` block. It doesn't list the `single-url-retrieval-measurement` "
        "skill there. Instead, it delivers that skill through the separate system `## Memory` "
        "instruction, which tells the agent it has access to a memory folder and should use it "
        "by default. The 'referenced' row counts runs where that instruction was present **and** "
        "the agent read or cited the memory skill or folder."
    )
    emit("\n| Condition | Count | % of all runs |")
    emit("| --- | --- | --- |")
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
    emit(f"| `docs-consumption` loaded: system skills block | {docs_loaded} | {round(100 * docs_loaded / total)}% |")
    emit(f"| system `## Memory` instruction present | {memory_instr_present} | {round(100 * memory_instr_present / total)}% |")
    emit(f"| `single-url-retrieval-measurement` referenced: system-instructed, agent-read | {memory_skill_referenced} | {round(100 * memory_skill_referenced / total)}% |")
    emit(f"| Both present | {both_present} | {round(100 * both_present / total)}% |")
    emit(f"| `docs-consumption` only | {docs_only} | {round(100 * docs_only / total)}% |")
    emit(f"| memory-instructed only | {memory_instr_only} | {round(100 * memory_instr_only / total)}% |")

    # ---- Notable edge cases ------------------------------------------------
    emit("\n## Edge Cases")
    emit()

    def _row_label(r):
        effort = r["effort"]
        if effort == "xhigh":
            effort = "extra-high"
        return f"`{_model_display(r['model'])}`, {effort}"

    memory_only_rows = [r for r in rows if r["memory_positive"] and not r["skill_positive"]]
    if memory_only_rows:
        emit("\n### Memory-only sessions: no workspace `docs-consumption` signal")
        emit()
        for r in memory_only_rows:
            emit(f"- `{r['file']}` {_row_label(r)}")
    else:
        emit("\n### Memory-only sessions")
        emit()
        emit("- None")

    skill_only_rows = [r for r in rows if r["skill_positive"] and not r["memory_positive"]]
    if skill_only_rows:
        emit("\n### Workspace-skill-only sessions: no `.codex/memories` detected")
        emit()
        for r in skill_only_rows:
            emit(f"- `{r['file']}` {_row_label(r)}")
    else:
        emit("\n### Workspace-skill-only sessions")
        emit()
        emit("- None")

    no_prefix_rows = [r for r in rows if r["docs_consumption_loaded"] and not r.get("protocol_prefix")]
    if no_prefix_rows:
        emit(f"\n### Sessions where `docs-consumption` loaded but no `COMPLETE/PARTIAL/UNVERIFIABLE` prefix: {len(no_prefix_rows)}")
        emit()
        for r in no_prefix_rows:
            emit(f"- `{r['file']}` {_row_label(r)}")

    emit()

    # ---- Write report -------------------------------------------------------
    report = "".join(line + "\n" for line in out)
    print(report, end="")
    out_path = Path(args.output) if args.output else _default_output(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(f"Report written to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
