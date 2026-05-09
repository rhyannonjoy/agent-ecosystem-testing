#!/usr/bin/env python3
"""
Codex Raw Output Verification Script
Verifies key metrics for raw track testing in the Agent Ecosystem Testing framework.

Adapted from the Cascade verification script for Codex's four-track design.
Raw track output files use the naming convention:
  raw_output_{test_id}_codex.txt   (T3 — Codex IDE)
  raw_output_{test_id}_vscode.txt  (T4 — VS Code-Codex)

The surface suffix prevents file collisions when both T3 and T4 produce output
for the same test ID and are stored in a shared results/raw/ directory.

Usage:
    # From the codex-web-search/ directory
    python codex_web_search_verify_raw_results.py BL-1
    python codex_web_search_verify_raw_results.py BL-1 SC-2 EC-1  # Multiple tests
    python codex_web_search_verify_raw_results.py --all           # All raw output files

    # Surface-specific
    python codex_web_search_verify_raw_results.py BL-1 --surface codex
    python codex_web_search_verify_raw_results.py BL-1 --surface vscode

    # Direct path to a specific file
    python codex_web_search_verify_raw_results.py --path results/raw/raw_output_BL-1_codex.txt
"""

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict

try:
    import tiktoken
except ImportError:
    print("Warning: tiktoken not installed. Token counts will be unavailable.")
    print("Install with: pip install tiktoken")
    tiktoken = None


def calculate_metrics(filepath: Path) -> Dict[str, any]:
    """Calculate all metrics for a raw search output file."""

    if not filepath.exists():
        return {
            "exists": False,
            "error": f"File not found: {filepath}",
        }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")

    # Basic metrics
    byte_count = filepath.stat().st_size
    char_count = len(content)
    line_count = content.count("\n") + 1
    word_count = len(content.split())

    # Token count
    token_count = None
    chars_per_token = None
    if tiktoken:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            token_count = len(enc.encode(content))
            chars_per_token = char_count / token_count if token_count > 0 else 0
        except Exception as e:
            token_count = f"Error: {str(e)}"

    # MD5 checksum
    md5_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

    # Content structure metrics
    # Code blocks: count pairs of ``` fences (odd count = unclosed block)
    fence_count = content.count("```")
    code_blocks = fence_count // 2

    # Headers: lines starting with # (Markdown)
    headers = sum(1 for line in content.split("\n") if line.strip().startswith("#"))

    # Table rows: lines that start and end with | (Markdown)
    # Includes header and separator rows — consistent with Cascade counting behavior.
    # Separator rows (|---|---| etc.) are included since the agent has no way to exclude them.
    table_rows = sum(
        1 for line in content.split("\n")
        if line.strip().startswith("|") and line.strip().endswith("|") and len(line.strip()) > 1
    )

    # Codex-specific: detect web / web.open tool boundary markers in verbatim output.
    # Codex's web toolchain may insert chunk boundary annotations or page markers
    # when fetching large documents via web.open; surface for comparison with
    # Cascade's DocumentId/chunk_id pagination markers.
    web_tool_markers = (
        content.count("[web]")
        + content.count("[web.open]")
        + content.count("chunk_id:")
        + content.count("[page ")
    )

    # Truncation indicators
    truncation_indicators = []
    last_256 = content[-256:] if len(content) > 256 else content

    # Unclosed Markdown code block
    if fence_count % 2 != 0:
        truncation_indicators.append("Unclosed Markdown code block (odd number of ``` fences)")

    # Mid-word truncation
    last_char = content[-1] if content else ""
    if last_char.isalnum():
        truncation_indicators.append("Ends mid-word (last character is alphanumeric)")

    # Unclosed Markdown link
    if last_256.count("[") > last_256.count("]"):
        truncation_indicators.append("Unclosed Markdown link bracket in last 256 chars")
    if last_256.count("](") > last_256.count(")"):
        truncation_indicators.append("Incomplete Markdown link URL in last 256 chars")

    # Incomplete table row
    last_line = content.split("\n")[-1] if "\n" in content else content
    if last_line.strip().startswith("|") and not last_line.strip().endswith("|"):
        truncation_indicators.append("Incomplete Markdown table row on last line")

    # Codex-specific: ellipsis elision markers (web / web.open excerpt indicators).
    # In Copilot testing, '...' markers indicated fetch_webpage excerpt assembly rather
    # than byte-boundary truncation. The same pattern may appear in Codex's web toolchain.
    # Their presence in raw track output indicates retrieval-layer excerpting, not a fixed
    # character ceiling — compare with Cascade finding before concluding truncated: yes.
    elision_count = content.count("...")
    if elision_count > 0:
        truncation_indicators.append(
            f"Ellipsis elision markers found ({elision_count} instances of '...') "
            f"— may indicate web/web.open excerpt assembly rather than full retrieval"
        )

    # Workspace substitution indicator: presence of local tool artifacts in verbatim output.
    # T4 (VS Code-Codex) runs carry a risk that the agent used curl or a local Python script
    # instead of web fetch. Shell command output in the file is a strong signal of this.
    workspace_substitution_signals = []
    shell_artifacts = ["$ curl", "$ python", ">>> import", "#!/usr/bin/env", "HTTP/1.1 200"]
    for artifact in shell_artifacts:
        if artifact in content:
            workspace_substitution_signals.append(
                f"Shell/script artifact found: '{artifact}' — possible workspace substitution"
            )

    return {
        "exists": True,
        "byte_count": byte_count,
        "char_count": char_count,
        "line_count": line_count,
        "word_count": word_count,
        "token_count": token_count,
        "chars_per_token": chars_per_token,
        "md5_checksum": md5_hash,
        "code_blocks": code_blocks,
        "table_rows": table_rows,
        "headers": headers,
        "web_tool_markers": web_tool_markers,
        "elision_count": elision_count,
        "workspace_substitution_signals": workspace_substitution_signals,
        "truncation_indicators": truncation_indicators,
        "last_50_chars": content[-50:] if len(content) > 50 else content,
    }


def format_size(bytes_count: int) -> str:
    """Format byte count as human-readable size."""
    if bytes_count < 1024:
        return f"{bytes_count}B"
    elif bytes_count < 1024 * 1024:
        return f"{bytes_count / 1024:.2f}KB"
    else:
        return f"{bytes_count / (1024 * 1024):.2f}MB"


def print_metrics_table(results: Dict[str, Dict]):
    """Print metrics in a formatted table."""

    if not results:
        print("No results to display")
        return

    print("\n" + "=" * 100)
    print("CODEX RAW OUTPUT VERIFICATION METRICS")
    print("=" * 100)

    for label, metrics in results.items():
        print(f"\nFile: {label}")
        print("-" * 100)

        if not metrics.get("exists", False):
            print(f"  ❌ {metrics.get('error', 'Unknown error')}")
            continue

        # Size metrics
        print(f"  File Size:          {format_size(metrics['byte_count'])} ({metrics['byte_count']:,} bytes)")
        print(f"  Character Count:    {metrics['char_count']:,}")
        print(f"  Line Count:         {metrics['line_count']:,}")
        print(f"  Word Count:         {metrics['word_count']:,}")

        # Token count
        if metrics["token_count"] is not None:
            if isinstance(metrics["token_count"], int):
                print(f"  Token Count:        {metrics['token_count']:,} (cl100k_base)")
                print(f"  Chars/Token:        {metrics['chars_per_token']:.2f}")
            else:
                print(f"  Token Count:        {metrics['token_count']}")
        else:
            print(f"  Token Count:        N/A (tiktoken not installed)")

        # Content structure
        print(f"\n  Content Structure:")
        print(f"    Code Blocks:      {metrics['code_blocks']}")
        print(f"    Table Rows:       {metrics['table_rows']}")
        print(f"    Headers:          {metrics['headers']}")

        # Codex-specific
        print(f"\n  Codex-Specific:")
        print(f"    Web Tool Markers ([web]/[web.open]/chunk_id/[page): {metrics['web_tool_markers']}")
        print(f"    Elision Markers (...):                               {metrics['elision_count']}")

        # Workspace substitution signals (most relevant for T4/VS Code-Codex)
        if metrics["workspace_substitution_signals"]:
            print(f"\n  ⚠️  Workspace Substitution Signals:")
            for signal in metrics["workspace_substitution_signals"]:
                print(f"    - {signal}")
        else:
            print(f"\n  ✓ No workspace substitution signals detected")

        # Checksum
        print(f"\n  MD5 Checksum:       {metrics['md5_checksum']}")

        # Truncation analysis
        if metrics["truncation_indicators"]:
            print(f"\n  ⚠️  Truncation / Retrieval Indicators:")
            for indicator in metrics["truncation_indicators"]:
                print(f"    - {indicator}")
        else:
            print(f"\n  ✓ No truncation indicators detected")

        # Last 50 characters
        last_50 = metrics["last_50_chars"].replace("\n", "\\n").replace("\r", "\\r")
        print(f"\n  Last 50 Characters:")
        print(f"    '{last_50}'")

        print()


def resolve_filepaths(test_ids: list, surface: str, results_dir: Path) -> Dict[str, Path]:
    """
    Resolve test IDs to file paths using the surface suffix convention.
    Returns a dict of display_label -> filepath for print_metrics_table.

    surface: 'codex' | 'vscode' | 'both'
    """
    paths = {}

    suffixes = []
    if surface == "both":
        suffixes = ["codex", "vscode"]
    else:
        suffixes = [surface]

    for test_id in test_ids:
        for suffix in suffixes:
            filename = f"raw_output_{test_id}_{suffix}.txt"
            label = f"{test_id} ({suffix})"
            paths[label] = results_dir / filename

    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Verify metrics for Codex raw search output files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
File naming convention:
  raw_output_{test_id}_codex.txt   T3 — Codex IDE
  raw_output_{test_id}_vscode.txt  T4 — VS Code-Codex

Examples:
  # Run from codex-web-search/ directory
  python codex_web_search_verify_raw_results.py BL-1
  python codex_web_search_verify_raw_results.py BL-1 SC-2 EC-1
  python codex_web_search_verify_raw_results.py --all

  # Surface-specific (default: both)
  python codex_web_search_verify_raw_results.py BL-1 --surface codex
  python codex_web_search_verify_raw_results.py BL-1 --surface vscode

  # Custom results directory
  python codex_web_search_verify_raw_results.py BL-1 --results-dir /path/to/results/raw

  # Direct path to a specific file
  python codex_web_search_verify_raw_results.py --path results/raw/raw_output_BL-1_codex.txt
        """,
    )

    parser.add_argument(
        "test_ids",
        nargs="*",
        help="Test IDs to verify (e.g., BL-1, SC-2)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all raw output files in the results directory",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Direct path to a specific file (bypasses surface suffix logic)",
    )
    parser.add_argument(
        "--surface",
        type=str,
        choices=["codex", "vscode", "both"],
        default="both",
        help="Surface to verify: codex (T3), vscode (T4), or both (default: both)",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results/raw",
        help="Directory containing raw output files (default: results/raw)",
    )

    args = parser.parse_args()

    results_dir = Path(args.results_dir)

    # Smart path detection: try alternatives if default doesn't exist
    if not results_dir.exists() and args.results_dir == "results/raw":
        for alt in [
            Path("codex-web-search/results/raw"),
            Path("../codex-web-search/results/raw"),
        ]:
            if alt.exists():
                results_dir = alt
                break

    file_map: Dict[str, Path] = {}

    if args.path:
        filepath = Path(args.path)
        # Derive a display label from the filename
        label = filepath.stem.replace("raw_output_", "").replace("_", " (", 1) + ")"
        file_map[label] = filepath

    elif args.all:
        if not results_dir.exists():
            print(f"Error: Directory {results_dir} does not exist")
            print(f"Resolved path: {results_dir.resolve()}")
            print(f"\nRun from either:")
            print(f"  - Project root (agent-ecosystem-testing/)")
            print(f"  - codex-web-search/ directory")
            sys.exit(1)

        # Glob both surface variants; filter by --surface if specified
        patterns = []
        if args.surface in ("codex", "both"):
            patterns.append("raw_output_*_codex.txt")
        if args.surface in ("vscode", "both"):
            patterns.append("raw_output_*_vscode.txt")

        for pattern in patterns:
            for filepath in sorted(results_dir.glob(pattern)):
                stem = filepath.stem.replace("raw_output_", "")
                # stem is now e.g. "BL-1_codex" → label "BL-1 (codex)"
                parts = stem.rsplit("_", 1)
                label = f"{parts[0]} ({parts[1]})" if len(parts) == 2 else stem
                file_map[label] = filepath

        if not file_map:
            print(f"No raw output files found in {results_dir}")
            print(f"Expected files named: raw_output_{{test_id}}_codex.txt or raw_output_{{test_id}}_vscode.txt")
            sys.exit(1)

    elif args.test_ids:
        file_map = resolve_filepaths(args.test_ids, args.surface, results_dir)

    else:
        parser.print_help()
        sys.exit(1)

    # Calculate metrics and print
    results = {label: calculate_metrics(filepath) for label, filepath in file_map.items()}
    print_metrics_table(results)

    successful = sum(1 for m in results.values() if m.get("exists", False))
    print("=" * 100)
    print(f"Summary: {successful}/{len(results)} files verified successfully")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()