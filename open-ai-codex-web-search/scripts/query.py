#!/usr/bin/env python3
"""
Query Codex interpreted-track results and format selected fields as Markdown.

Supports Track 1 (codex-interpreted) and Track 2 (vscode-codex-interpreted).

Mirrors the manual RSQL query used for H4 assessment:

    SELECT a1, a10, a11, a13, a15, a16, a18, a19, a20, a21
    WHERE a1 == 'SC-1' && (a10 == 'GPT-5.4-Mini' || a10 == 'GPT-5.5')

Alias mapping:
    a1  -> test_id
    a10 -> model_observed
    a11 -> model_intelligence_level
    a13 -> hypothesis_match
    a15 -> notes
    a16 -> tools_named
    a18 -> output_chars
    a19 -> truncated
    a20 -> truncation_note
    a21 -> tokens_est

Usage:
    # From open-ai-codex-web-search/
    python scripts/query.py --test SC-1 --models GPT-5.4-Mini,GPT-5.5
    python scripts/query.py --track 2 --test SC-1 --models GPT-5.4-Mini,GPT-5.5

    # From repo root
    python open-ai-codex-web-search/scripts/query.py --test SC-1 --models GPT-5.4-Mini,GPT-5.5
"""

import argparse
import csv
import sys
from pathlib import Path

# Columns selected by the manual query, mapped to real CSV headers.
SELECTED_COLUMNS = [
    "test_id",
    "model_observed",
    "model_intelligence_level",
    "hypothesis_match",
    "notes",
    "tools_named",
    "output_chars",
    "truncated",
    "truncation_note",
    "tokens_est",
]

# Fields that appear in the Markdown output block, in order.
OUTPUT_FIELDS = [
    ("Hypotheses Assessment", "hypothesis_match"),
    ("Notes", "notes"),
    ("Tools", "tools_named"),
    ("Truncation", "truncated"),
    ("Truncation Note", "truncation_note"),
    ("Character Count", "output_chars"),
    ("Token Estimation", "tokens_est"),
]


# Track number -> default results CSV directory name.
TRACKS: dict[int, str] = {
    1: "codex-interpreted",
    2: "vscode-codex-interpreted",
}


def default_csv_path(track: int) -> Path:
    """Return the default CSV path for the given track number."""
    return (
        Path(__file__).resolve().parent.parent
        / "results"
        / TRACKS[track]
        / "results.csv"
    )


def read_rows(csv_path: Path, test_id: str, models: list[str] | None) -> list[dict[str, str]]:
    """Read the CSV and return rows matching the test_id and optional model filters."""
    rows: list[dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("test_id") != test_id:
                continue
            if models and row.get("model_observed") not in models:
                continue
            rows.append(row)
    return rows


def format_markdown(rows: list[dict[str, str]]) -> str:
    """Format matching rows as Markdown blockquote lines."""
    blocks: list[str] = []
    for row in rows:
        lines: list[str] = []
        lines.append(
            f">`{row.get('test_id', '')}` | {row.get('model_observed', '')} | "
            f"{row.get('model_intelligence_level', '')}"
        )
        for label, column in OUTPUT_FIELDS:
            value = row.get(column, "") or "-"
            lines.append(f">{label}: {value}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query Codex interpreted-track results and format selected fields as Markdown."
    )
    parser.add_argument(
        "--track",
        type=int,
        choices=list(TRACKS.keys()),
        default=1,
        help="Results track to query: 1=codex-interpreted, 2=vscode-codex-interpreted (default: 1).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Path to a results CSV (overrides --track).",
    )
    parser.add_argument("--test", required=True, help="Test ID to filter on, e.g. SC-1.")
    parser.add_argument(
        "--models",
        help="Comma-separated list of model_observed values to include, e.g. GPT-5.4-Mini,GPT-5.5.",
    )
    args = parser.parse_args()

    csv_path = args.csv if args.csv else default_csv_path(args.track)
    models = [m.strip() for m in args.models.split(",")] if args.models else None

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    rows = read_rows(csv_path, args.test, models)
    if not rows:
        print(
            f"No rows found for test_id={args.test} and models={models}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(format_markdown(rows))


if __name__ == "__main__":
    main()
