#!/usr/bin/env python3
"""
Cascade Raw Output Verification Script
Verifies key metrics for raw track testing in the Agent Ecosystem Testing framework.

Adapted from the Copilot verification script for Cascade's three-track design.
Saved output files use the naming convention raw_output_{test_id}.txt.

Usage:
    # From the windsurf-cascade-web-search/ directory
    python web_search_verify_raw_results.py {test ID}
    python web_search_verify_raw_results.py BL-1 SC-2 EC-1  # Multiple tests
    python web_search_verify_raw_results.py --all           # All raw output files
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
            "error": f"File not found: {filepath}"
        }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')

    # Basic metrics
    byte_count = filepath.stat().st_size
    char_count = len(content)
    line_count = content.count('\n') + 1
    word_count = len(content.split())

    # Token count
    token_count = None
    chars_per_token = None
    if tiktoken:
        try:
            enc = tiktoken.get_encoding('cl100k_base')
            token_count = len(enc.encode(content))
            chars_per_token = char_count / token_count if token_count > 0 else 0
        except Exception as e:
            token_count = f"Error: {str(e)}"

    # MD5 checksum
    md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    # Content structure metrics
    # Code blocks: count pairs of ``` fences (odd count = unclosed block)
    fence_count = content.count('```')
    code_blocks = fence_count // 2

    # Headers: lines starting with # (Markdown)
    headers = sum(1 for line in content.split('\n') if line.strip().startswith('#'))

    # Table rows: lines that start and end with | (Markdown)
    # Includes header and separator rows — consistent with Cascade's counting behavior.
    # Separator rows (|---|---| etc.) are included since Cascade has no way to exclude them.
    table_rows = sum(
        1 for line in content.split('\n')
        if line.strip().startswith('|') and line.strip().endswith('|') and len(line.strip()) > 1
    )

    # Cascade-specific: detect view_content_chunk pagination markers
    # Cascade uses DocumentId-based chunking; chunk boundaries may appear as markers
    pagination_markers = content.count('[DocumentId:') + content.count('chunk_id:')

    # Truncation indicators
    truncation_indicators = []
    last_256 = content[-256:] if len(content) > 256 else content

    # Unclosed Markdown code block
    if fence_count % 2 != 0:
        truncation_indicators.append("Unclosed Markdown code block (odd number of ``` fences)")

    # Mid-word truncation
    last_char = content[-1] if content else ''
    if last_char.isalnum():
        truncation_indicators.append("Ends mid-word (last character is alphanumeric)")

    # Unclosed Markdown link
    if last_256.count('[') > last_256.count(']'):
        truncation_indicators.append("Unclosed Markdown link bracket in last 256 chars")
    if last_256.count('](') > last_256.count(')'):
        truncation_indicators.append("Incomplete Markdown link URL in last 256 chars")

    # Incomplete table row
    last_line = content.split('\n')[-1] if '\n' in content else content
    if last_line.strip().startswith('|') and not last_line.strip().endswith('|'):
        truncation_indicators.append("Incomplete Markdown table row on last line")

    # Cascade-specific: ellipsis elision markers (read_url_content excerpt indicators)
    # These are expected in interpreted/explicit track output saved verbatim;
    # their presence in raw track output indicates retrieval-layer excerpting
    elision_count = content.count('...')
    if elision_count > 0:
        truncation_indicators.append(
            f"Ellipsis elision markers found ({elision_count} instances of '...') "
            f"— may indicate read_url_content excerpt assembly rather than full retrieval"
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
        "pagination_markers": pagination_markers,
        "elision_count": elision_count,
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
    print("CASCADE RAW OUTPUT VERIFICATION METRICS")
    print("=" * 100)

    for test_id, metrics in results.items():
        print(f"\nTest ID: {test_id}")
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
        if metrics['token_count'] is not None:
            if isinstance(metrics['token_count'], int):
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

        # Cascade-specific
        print(f"\n  Cascade-Specific:")
        print(f"    Pagination Markers (DocumentId/chunk_id): {metrics['pagination_markers']}")
        print(f"    Elision Markers (...):                    {metrics['elision_count']}")

        # Checksum
        print(f"\n  MD5 Checksum:       {metrics['md5_checksum']}")

        # Truncation analysis
        if metrics['truncation_indicators']:
            print(f"\n  ⚠️  Truncation / Retrieval Indicators:")
            for indicator in metrics['truncation_indicators']:
                print(f"    - {indicator}")
        else:
            print(f"\n  ✓ No truncation indicators detected")

        # Last 50 characters
        last_50 = metrics['last_50_chars'].replace('\n', '\\n').replace('\r', '\\r')
        print(f"\n  Last 50 Characters:")
        print(f"    '{last_50}'")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="Verify metrics for Cascade raw search output files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run from windsurf-cascade-web-search/ directory
  python web_search_verify_raw_results.py BL-1
  python web_search_verify_raw_results.py BL-1 SC-2 EC-1
  python web_search_verify_raw_results.py --all

  # Custom results directory
  python web_search_verify_raw_results.py BL-1 --results-dir /path/to/results/raw

  # Direct path to a specific file
  python web_search_verify_raw_results.py --path results/raw/raw_output_BL-1.txt
        """
    )

    parser.add_argument(
        'test_ids',
        nargs='*',
        help='Test IDs to verify (e.g., BL-1, SC-2)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Verify all raw output files in results/raw/'
    )
    parser.add_argument(
        '--path',
        type=str,
        help='Direct path to a specific file'
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default='results/raw',
        help='Directory containing raw output files (default: results/raw)'
    )

    args = parser.parse_args()

    results_dir = Path(args.results_dir)

    # Smart path detection: try alternatives if default doesn't exist
    if not results_dir.exists() and args.results_dir == 'results/raw':
        for alt in [
            Path('cascade-web-search/results/raw'),
            Path('../cascade-web-search/results/raw'),
        ]:
            if alt.exists():
                results_dir = alt
                break

    results = {}

    if args.path:
        filepath = Path(args.path)
        test_id = filepath.stem.replace('raw_output_', '')
        results[test_id] = calculate_metrics(filepath)

    elif args.all:
        if not results_dir.exists():
            print(f"Error: Directory {results_dir} does not exist")
            print(f"Resolved path: {results_dir.resolve()}")
            print(f"\nRun from either:")
            print(f"  - Project root (agent-ecosystem-testing/)")
            print(f"  - cascade-web-search/ directory")
            sys.exit(1)

        for filepath in sorted(results_dir.glob('raw_output_*.txt')):
            test_id = filepath.stem.replace('raw_output_', '')
            results[test_id] = calculate_metrics(filepath)

        if not results:
            print(f"No search output files found in {results_dir}")
            print(f"Expected files named: raw_output_{{test_id}}.txt")
            sys.exit(1)

    elif args.test_ids:
        for test_id in args.test_ids:
            filepath = results_dir / f'raw_output_{test_id}.txt'
            results[test_id] = calculate_metrics(filepath)

    else:
        parser.print_help()
        sys.exit(1)

    print_metrics_table(results)

    successful = sum(1 for m in results.values() if m.get('exists', False))
    print("=" * 100)
    print(f"Summary: {successful}/{len(results)} files verified successfully")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()