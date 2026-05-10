#!/usr/bin/env python3
"""
Codex Web Search Summary Template Generator
Generates a structured Markdown summary template for a given test ID and track.

The template pre-populates:
  - Test conditions table (from TEST_URLS and TRACKS)
  - Run results table with correct columns per track method
  - Per-hypothesis sections (H1–H5) with standard headers and verdict placeholders
  - Emergent findings scaffold
  - Log label summary table

Everything analytical — verdict reasoning, emergent findings prose, agent
notes, log labels — is left as a TODO placeholder for human completion.

Usage:
    python template.py --test BL-1 --track codex-raw
    python template.py --test SC-2 --track codex-interpreted
    python template.py --test OP-1 --track vscode-codex-raw

    # Generate templates for all tracks of a single test
    python template.py --test BL-1 --all-tracks

    # Generate templates for all tests on a single track
    python template.py --track codex-raw --all-tests

Output:
    summaries/codex-interpreted/{test_id}_summary.md        (t1)
    summaries/vscode-codex-interpreted/{test_id}_summary.md (t2)
    summaries/codex-raw/{test_id}_summary.md                (t3)
    summaries/vscode-codex-raw/{test_id}_summary.md         (t4)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from framework import TEST_URLS, TRACKS

# ---------------------------------------------------------------------------
# Hypothesis definitions
# ---------------------------------------------------------------------------

HYPOTHESES = {
    "H1": "Character-based truncation at a fixed ceiling",
    "H2": "Token-based truncation (e.g., 2,000 tokens ≈ 8,000 chars)",
    "H3": "Structure-aware truncation (respects Markdown boundaries)",
    "H4": "Surface context (Codex IDE vs VS Code-Codex) changes retrieval ceiling",
    "H5": "Agent auto-chunks above the truncation ceiling",
}

# Default verdict note per hypothesis — used when no prior context exists.
# These are conservative safe defaults; the analyst replaces them.
HYPOTHESIS_DEFAULTS = {
    "H1": (
        "**Indeterminate.** <!-- TODO: describe output sizes and whether any ceiling was approached. -->\n\n"
        "**Combined verdict: H1 indeterminate. <!-- TODO -->**"
    ),
    "H2": (
        "**Indeterminate.** <!-- TODO: describe token counts and whether a ceiling was hit. -->\n\n"
        "**Combined verdict: H2 indeterminate. <!-- TODO -->**"
    ),
    "H3": (
        "**Indeterminate.** <!-- TODO: describe truncation boundary behavior, if any. -->\n\n"
        "**Combined verdict: H3 indeterminate. <!-- TODO -->**"
    ),
    "H4": (
        "**Untested.** <!-- TODO: note whether surface divergence was observed. -->\n\n"
        "**Combined verdict: H4 untested. <!-- TODO -->**"
    ),
    "H5": (
        "**Indeterminate.** <!-- TODO: note whether multi-step tool chains were observed. -->\n\n"
        "**Combined verdict: H5 indeterminate. <!-- TODO -->**"
    ),
}

# ---------------------------------------------------------------------------
# Column definitions per track method
# ---------------------------------------------------------------------------

# Interpreted tracks (T1, T2): agent self-reports measurements
INTERPRETED_COLUMNS = [
    "Agent",
    "Output chars",
    "Tokens est.",
    "Truncated",
    "Last 50 chars",
    "Tools named",
    "Workspace sub.",
    "Notes",
]

# Raw tracks (T3, T4): verification script measures; agent self-reports separately
RAW_COLUMNS = [
    "Agent",
    "Output file",
    "File size",
    "Tokens (verified)",
    "Strategy",
    "Tools used",
    "Workspace sub.",
    "Notes",
]

# Number of placeholder agent rows to pre-populate
DEFAULT_AGENT_ROWS = 5

# ---------------------------------------------------------------------------
# Template builder
# ---------------------------------------------------------------------------

def build_markdown_table(headers: list, rows: list) -> str:
    """Build a Markdown table from headers and rows (list of lists)."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def fmt_row(cells):
        return "| " + " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(cells)) + " |"

    separator = "| " + " | ".join("-" * w for w in col_widths) + " |"

    lines = [fmt_row(headers), separator]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def blank_run_results_table(track_method: str, n_agents: int = DEFAULT_AGENT_ROWS) -> str:
    """Generate a blank run results table appropriate for the track method."""
    if track_method == "raw":
        columns = RAW_COLUMNS
        blank_row = [
            "`<!-- Agent -->`",
            "<!-- ✓/✗ -->",
            "<!-- XKB / ~X tokens -->",
            "<!-- X tokens -->",
            "<!-- strategy -->",
            "<!-- web -> web.open -->",
            "<!-- yes/no/unknown -->",
            "<!-- notes -->",
        ]
    else:
        columns = INTERPRETED_COLUMNS
        blank_row = [
            "`<!-- Agent -->`",
            "<!-- X chars -->",
            "<!-- X tokens -->",
            "<!-- yes/no -->",
            "<!-- last 50 chars -->",
            "<!-- web, web.open -->",
            "<!-- yes/no/unknown -->",
            "<!-- notes -->",
        ]

    rows = [blank_row[:] for _ in range(n_agents)]
    return build_markdown_table(columns, rows)


def blank_log_label_table(n_agents: int = DEFAULT_AGENT_ROWS) -> str:
    """Generate a blank log label summary table."""
    columns = ["Agent", "Result", "Label"]
    rows = [
        ["`<!-- Agent -->`", "<!-- ✓/✗/Partial -->", "`<!-- RESULT — label_tag + label_tag -->`"]
        for _ in range(n_agents)
    ]
    return build_markdown_table(columns, rows)


def generate_template(test_id: str, track: str) -> str:
    """Generate the full Markdown summary template for a test ID and track."""
    test = TEST_URLS[test_id]
    track_info = TRACKS[track]
    is_raw = track_info["method"] == "raw"

    now = datetime.now().strftime("%Y-%m-%d")
    surface_label = "Codex IDE" if track_info["surface"] == "codex" else "VS Code-Codex"
    workspace_label = "workspace present" if track_info["workspace"] else "no workspace"
    method_label = "Raw" if is_raw else "GPT-interpreted"

    # --- Test conditions table ---
    conditions_rows = [
        ["URL", f"`{test['url']}`"],
        ["Expected size", f"~{test['expected_size_kb']}KB"],
        ["Surface", surface_label],
        ["Workspace", workspace_label],
        ["Track", f"{track_info['label']}"],
        ["Method", method_label],
        ["Runs", "<!-- N -->"],
        ["Chunks returned", "<!-- N (raw track only; delete row if interpreted) -->" if is_raw else "_N/A — interpreted track_"],
    ]
    conditions_table = build_markdown_table(["", f"**{test_id}**"], conditions_rows)

    # --- Hypothesis sections ---
    hypothesis_sections = []
    for hyp_id, hyp_desc in HYPOTHESES.items():
        section = f"### `{hyp_id}` — {hyp_desc}\n\n{HYPOTHESIS_DEFAULTS[hyp_id]}"
        hypothesis_sections.append(section)
    hypotheses_md = "\n\n---\n\n".join(hypothesis_sections)

    # --- Assemble full template ---
    template = f"""\
<!--
  Codex Web Search Testing — Run Summary Template
  Test ID : {test_id}
  Track   : {track}
  Surface : {surface_label} ({workspace_label})
  Generated: {now}
  
  Instructions:
    1. Fill in run results table (one row per agent run).
    2. Replace <!-- TODO --> placeholders in hypothesis sections with verdict reasoning.
    3. Write emergent findings prose in the numbered list.
    4. Fill in log label summary table.
    5. Delete this comment block before publishing.
-->

## {test_id} {method_label} Track Summary

### Test Conditions

{conditions_table}

---

### Run Results

{blank_run_results_table(track_info['method'])}

---

{hypotheses_md}

---

### Emergent Findings

<!-- TODO: replace placeholders with prose observations. Add or remove items as needed. -->

1. <!-- Finding 1 -->
2. <!-- Finding 2 -->
3. <!-- Finding 3 -->
4. <!-- Finding 4 -->
5. <!-- Finding 5 -->

---

### Log Label Summary

{blank_log_label_table()}
"""
    return template


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

_SUMMARY_DIR = {
    "codex-interpreted": "codex-interpreted",
    "vscode-codex-interpreted": "vscode-codex-interpreted",
    "codex-raw":          "codex-raw",
    "vscode-codex-raw":         "vscode-codex-raw",
}

def write_template(test_id: str, track: str, output_dir: Path, overwrite: bool = False) -> Path:
    """Write the template to disk and return the output path."""
    subdir = output_dir / _SUMMARY_DIR.get(track, track.replace("_", "-"))
    subdir.mkdir(parents=True, exist_ok=True)

    filepath = subdir / f"{test_id}_summary.md"

    if filepath.exists() and not overwrite:
        print(f"  ⚠️  {filepath} already exists — skipping (use --overwrite to replace)")
        return filepath

    content = generate_template(test_id, track)
    filepath.write_text(content, encoding="utf-8")
    print(f"  ✓  {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate Markdown summary templates for Codex web search testing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python template.py --test BL-1 --track codex-raw
  python template.py --test SC-2 --track codex-interpreted
  python template.py --test OP-1 --all-tracks
  python template.py --track codex-raw --all-tests
  python template.py --all-tests --all-tracks

Output directory (default: summaries/):
  summaries/codex-interpreted/        (codex-interpreted)
  summaries/vscode-codex-interpreted/ (vscode-codex-interpreted)
  summaries/codex-raw/                (codex-raw)
  summaries/vscode-codex-raw/         (vscode-codex-raw)
        """,
    )

    parser.add_argument("--test", type=str, help="Test ID (e.g. BL-1, SC-2)")
    parser.add_argument(
        "--track",
        type=str,
        choices=list(TRACKS.keys()),
        help="Track ID (e.g. codex-raw)",
    )
    parser.add_argument(
        "--all-tracks",
        action="store_true",
        help="Generate templates for all four tracks (requires --test)",
    )
    parser.add_argument(
        "--all-tests",
        action="store_true",
        help="Generate templates for all test IDs (requires --track, or combine with --all-tracks)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="summaries",
        help="Output directory (default: summaries/)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing template files",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print the template to stdout instead of writing a file",
    )

    args = parser.parse_args()

    # Resolve test IDs and tracks to generate
    test_ids = list(TEST_URLS.keys()) if args.all_tests else ([args.test] if args.test else None)
    tracks = list(TRACKS.keys()) if args.all_tracks else ([args.track] if args.track else None)

    if not test_ids:
        parser.error("Specify --test TEST_ID or --all-tests")
    if not tracks:
        parser.error("Specify --track TRACK or --all-tracks")

    # Validate test IDs
    for tid in test_ids:
        if tid not in TEST_URLS:
            parser.error(f"Unknown test ID: {tid}. Choose from: {', '.join(TEST_URLS.keys())}")

    if args.preview:
        # Preview mode: print first combination only
        content = generate_template(test_ids[0], tracks[0])
        print(content)
        if len(test_ids) * len(tracks) > 1:
            print(f"\n(Preview shows {test_ids[0]} × {tracks[0]} only; "
                  f"{len(test_ids) * len(tracks) - 1} additional template(s) suppressed)")
        return

    output_dir = Path(args.output_dir)
    print(f"\nGenerating templates → {output_dir}/\n")

    generated = []
    for tid in test_ids:
        for track in tracks:
            path = write_template(tid, track, output_dir, overwrite=args.overwrite)
            generated.append(path)

    print(f"\n{len(generated)} template(s) ready.")


if __name__ == "__main__":
    main()