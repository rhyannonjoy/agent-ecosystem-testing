#!/usr/bin/env python3
"""
Docs-Consumption Skill Flash Test Analysis

Compares EC-6 T2 (vscode-codex-interpreted) results across three skill
conditions:

    skill: off;      -- baseline, no skill file or no mention of it
    skill: opt-in;   -- skill file present in workspace but not prompted
    skill: on;       -- skill file present and explicitly activated in prompt

The condition is set via the `notes` field prefix. If no prefix is present, the
row is labeled `historical` and treated as skill-off.

You can pass one CSV (the flash-test CSV) or two CSVs (flash-test CSV plus the
historical vscode-codex-interpreted results.csv). Historical rows without a
skill prefix are treated as skill-off.

Output is a Markdown-friendly comparison table plus a per-model/reasoning-level
breakdown of the yes/mixed/implicit/no disclosure taxonomy and failure-examination
dimensions.

Usage:
    # Flash-test CSV only
    python docs_consumption_skill_analysis.py \
        --csv open-ai-codex-web-search/results/docs-consumption-skill-flash/results.csv

    # Flash-test CSV plus historical baseline
    python docs_consumption_skill_analysis.py \
        --csv open-ai-codex-web-search/results/docs-consumption-skill-flash/results.csv \
               open-ai-codex-web-search/results/vscode-codex-interpreted/results.csv \
        --output open-ai-codex-web-search/skills/flash-test-report.md
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Matches the existing analyze.py taxonomy.
TRUNCATION_TIER = {
    "yes": 3,
    "mixed": 2,
    "implicit": 1,
    "no": 0,
}

TIER_LABEL = {
    3: "yes",
    2: "mixed",
    1: "implicit",
    0: "no",
    -1: "unknown",
}

MODEL_ORDER = ["GPT-5.4-Mini", "GPT-5.4", "GPT-5.5"]
LEVEL_ORDER = ["Light", "Medium", "High", "Extra High"]


def normalize_model(value: str) -> str:
    value = (value or "").strip()
    # Accept both "GPT-5.4-Mini" and "gpt-5.4-mini".
    lowered = value.lower()
    for candidate in MODEL_ORDER:
        if candidate.lower().replace(" ", "") == lowered.replace(" ", ""):
            return candidate
    return value


def normalize_level(value: str) -> str:
    value = (value or "").strip().capitalize()
    return value if value in LEVEL_ORDER else value


def detect_skill(notes: str) -> str:
    """Return 'on', 'opt-in', 'off', or 'historical' based on notes prefix."""
    notes = (notes or "").strip().lower()
    if notes.startswith("skill: opt-in") or notes.startswith("skill:opt-in"):
        return "opt-in"
    if notes.startswith("skill: on") or notes.startswith("skill:on"):
        return "on"
    if notes.startswith("skill: off") or notes.startswith("skill:off"):
        return "off"
    return "historical"  # existing rows without explicit skill labeling


DIMENSIONS = [
    ("completeness-accurate", "Correctly classified completeness state"),
    ("error-examined", "Examined embedded errors"),
    ("exec-vs-complete", "Distinguished execution from completeness"),
    ("no-reframing", "Did not reframe failure as success"),
    ("fix-recommended", "Recommended a fix"),
]


def parse_dimension(notes: str, key: str) -> Optional[str]:
    """Extract a yes/no dimension value from notes, e.g. 'error-examined: yes'."""
    pattern = re.compile(rf"{re.escape(key)}\s*[:=]\s*(yes|no)", re.IGNORECASE)
    match = pattern.search(notes or "")
    return match.group(1).lower() if match else None


def load_rows(csv_paths):
    rows = []
    for csv_path in csv_paths:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["model_observed"] = normalize_model(row.get("model_observed", ""))
                row["model_intelligence_level"] = normalize_level(row.get("model_intelligence_level", ""))
                row["truncated_lower"] = (row.get("truncated") or "").strip().lower()
                row["skill"] = detect_skill(row.get("notes", ""))
                row["tier"] = TRUNCATION_TIER.get(row["truncated_lower"], -1)
                notes = row.get("notes", "")
                for key, _ in DIMENSIONS:
                    row[key] = parse_dimension(notes, key)
                row["_csv_path"] = str(csv_path)
                rows.append(row)
    return rows


def filter_ec6_t2(rows):
    return [
        r for r in rows
        if r.get("test_id") == "EC-6"
        and r.get("track") == "vscode-codex-interpreted"
    ]


def build_pairs(rows):
    """Group rows by (model, level) and split by skill condition."""
    pairs = defaultdict(lambda: {"on": [], "opt-in": [], "off": []})
    for r in rows:
        key = (r["model_observed"], r["model_intelligence_level"])
        condition = r["skill"] if r["skill"] in ("on", "opt-in") else "off"
        pairs[key][condition].append(r)
    return pairs


def average_tier(rows):
    tiers = [r["tier"] for r in rows if r["tier"] >= 0]
    return sum(tiers) / len(tiers) if tiers else None


def dominant_tier(rows):
    tiers = [r["tier"] for r in rows if r["tier"] >= 0]
    if not tiers:
        return -1
    return max(set(tiers), key=tiers.count)


def format_tier_count(rows):
    counts = defaultdict(int)
    for r in rows:
        if r["tier"] >= 0:
            counts[TIER_LABEL[r["tier"]]] += 1
    parts = [f"{k}={counts[k]}" for k in ["yes", "mixed", "implicit", "no"] if counts[k]]
    return ", ".join(parts) if parts else "—"


def dimension_rate(rows, key: str):
    """Return (yes_count, scored_count, rate) for a boolean dimension."""
    values = [r.get(key) for r in rows if r.get(key) is not None]
    if not values:
        return 0, 0, None
    yes = sum(1 for v in values if v == "yes")
    return yes, len(values), yes / len(values)


def generate_report(rows):
    ec6_rows = filter_ec6_t2(rows)
    if not ec6_rows:
        return "No EC-6 vscode-codex-interpreted rows found."

    on_rows = [r for r in ec6_rows if r["skill"] == "on"]
    optin_rows = [r for r in ec6_rows if r["skill"] == "opt-in"]
    off_rows = [r for r in ec6_rows if r["skill"] in ("off", "historical")]

    lines = []
    source_paths = sorted(set(r.get("_csv_path", "results.csv") for r in ec6_rows))
    source_str = "`, `".join(str(Path(p)) for p in source_paths)

    lines.append("# Docs-Consumption Skill Flash Test Report")
    lines.append("")
    lines.append(f"**Source:** `{source_str}`")
    lines.append(
        f"**EC-6 T2 rows:** {len(ec6_rows)} total "
        f"({len(off_rows)} skill-off / historical, {len(optin_rows)} skill-opt-in, {len(on_rows)} skill-on)"
    )
    lines.append("")

    # Aggregate comparison
    lines.append("## Aggregate disclosure comparison")
    lines.append("")
    lines.append("| Condition | Runs | Avg disclosure tier | Dominant tier | Tier counts |")
    lines.append("| --------- | ---- | ------------------- | ------------- | ----------- |")
    for label, subset in [
        ("skill-off / historical", off_rows),
        ("skill-opt-in", optin_rows),
        ("skill-on", on_rows),
    ]:
        avg = average_tier(subset)
        dom = dominant_tier(subset)
        counts = format_tier_count(subset)
        avg_str = f"{avg:.2f}" if avg is not None else "—"
        lines.append(
            f"| {label} | {len(subset)} | "
            f"{avg_str} | "
            f"{TIER_LABEL.get(dom, '—')} | {counts} |"
        )
    lines.append("")

    # Failure-examination dimensions (only meaningful when dimension data is logged)
    any_dimensions = any(
        r.get(key) is not None for r in ec6_rows for key, _ in DIMENSIONS
    )
    if any_dimensions:
        lines.append("## Failure-examination comparison")
        lines.append("")
        lines.append(
            "| Dimension | Skill-off (yes / scored / rate) | "
            "Skill-opt-in (yes / scored / rate) | Skill-on (yes / scored / rate) |"
        )
        lines.append(
            "| --------- | -------------------------------- | "
            "----------------------------------- | -------------------------------- |"
        )
        for key, label in DIMENSIONS:
            off_yes, off_total, off_rate = dimension_rate(off_rows, key)
            optin_yes, optin_total, optin_rate = dimension_rate(optin_rows, key)
            on_yes, on_total, on_rate = dimension_rate(on_rows, key)
            off_str = f"{off_yes}/{off_total} ({off_rate:.0%})" if off_rate is not None else "—"
            optin_str = f"{optin_yes}/{optin_total} ({optin_rate:.0%})" if optin_rate is not None else "—"
            on_str = f"{on_yes}/{on_total} ({on_rate:.0%})" if on_rate is not None else "—"
            lines.append(f"| {label} | {off_str} | {optin_str} | {on_str} |")
        lines.append("")

    if not optin_rows and not on_rows:
        lines.append(
            "_No skill-opt-in or skill-on rows yet. Run the prompts and log results with notes prefixed "
            "`skill: opt-in; ` or `skill: on; `._"
        )
        lines.append("")
        return "\n".join(lines)

    # Per-model/reasoning table
    lines.append("## Per-model/reasoning disclosure")
    lines.append("")
    lines.append(
        "| Model | Level | Skill-off tier | Skill-opt-in tier | Skill-on tier |"
    )
    lines.append(
        "| ----- | ----- | -------------- | ----------------- | ------------- |"
    )

    pairs = build_pairs(ec6_rows)
    for model in MODEL_ORDER:
        for level in LEVEL_ORDER:
            key = (model, level)
            if key not in pairs:
                continue
            off = pairs[key]["off"]
            optin = pairs[key]["opt-in"]
            on = pairs[key]["on"]
            if not off and not optin and not on:
                continue

            off_tier = dominant_tier(off)
            optin_tier = dominant_tier(optin)
            on_tier = dominant_tier(on)

            shift_optin = ""
            if optin and off:
                delta = optin_tier - off_tier
                shift_optin = f"{delta:+d}"

            shift_on = ""
            if on and off:
                delta = on_tier - off_tier
                shift_on = f"{delta:+d}"

            lines.append(
                f"| {model} | {level} | "
                f"{TIER_LABEL.get(off_tier, '—')} | "
                f"{TIER_LABEL.get(optin_tier, '—')} ({shift_optin or '—'}) | "
                f"{TIER_LABEL.get(on_tier, '—')} ({shift_on or '—'}) |"
            )
    lines.append("")

    # Interpretation guide
    lines.append("## How to read this")
    lines.append("")
    lines.append("- Disclosure tier: `yes` (3) > `mixed` (2) > `implicit` (1) > `no` (0).")
    lines.append("- A positive **Shift** (e.g., `+2`) means that skill condition produced a higher-disclosure label than skill-off for that matched pair.")
    lines.append("- `skill-opt-in` tells you whether agents discover and use the skill on their own.")
    lines.append("- `skill-on` tells you whether the skill works when explicitly activated.")
    lines.append("- If `skill-on` improves but `skill-opt-in` doesn't, the problem is skill discovery/activation, not skill content.")
    lines.append("- If neither improves, the problem is deeper than instruction-following.")
    lines.append("- Failure-examination rates only appear when notes include the dimension tags (e.g., `error-examined: yes`). Log them to see whether agents classify completeness accurately, examine errors, avoid reframing, and recommend fixes.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze docs-consumption skill flash test results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--csv",
        type=Path,
        nargs="+",
        required=True,
        help="One or more CSV files to analyze. Pass the flash-test CSV first, then the historical CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write Markdown report",
    )
    args = parser.parse_args()

    available_csvs = []
    for csv_path in args.csv:
        if csv_path.exists():
            available_csvs.append(csv_path)
        else:
            print(f"Warning: CSV not found, skipping: {csv_path}", file=sys.stderr)

    if not available_csvs:
        print("No CSV files available to analyze.", file=sys.stderr)
        sys.exit(1)

    rows = load_rows(available_csvs)

    report = generate_report(rows)
    print(report)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"\nReport written to {args.output}")


if __name__ == "__main__":
    main()
