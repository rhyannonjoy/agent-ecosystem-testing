#!/usr/bin/env env python3
"""
Raw Output Verification Script
Verifies key metrics for raw track testing in the Agent Ecosystem Testing framework

Usage:
    # From the copilot-web-content-retrieval directory
    python3 web_content_retrieval_verify_raw_results.py {test ID}
    python3 web_content_retrieval_verify_raw_results.py BL-1 SC-2 EC-1  # Multiple tests
    python3 web_content_retrieval_verify_raw_results.py --all  # All raw output files
"""

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict, List

try:
    import tiktoken
except ImportError:
    print("Warning: tiktoken not installed. Token counts will be unavailable.")
    print("Install with: pip install tiktoken")
    tiktoken = None

def calculate_metrics(filepath: Path) -> Dict[str, any]:
    """Calculate all metrics for a raw output file"""
    
    if not filepath.exists():
        return {
            "exists": False,
            "error": "File not found"
        }
    
    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try binary mode if UTF-8 fails
        with open(filepath, 'rb') as f:
            content = f.read()
            content = content.decode('utf-8', errors='ignore')
    
    # Basic metrics
    byte_count = filepath.stat().st_size
    char_count = len(content)
    line_count = content.count('\n') + 1
    word_count = len(content.split())
    
    # Token count (if tiktoken available)
    token_count = None
    if tiktoken:
        try:
            enc = tiktoken.get_encoding('cl100k_base')
            token_count = len(enc.encode(content))
        except Exception as e:
            token_count = f"Error: {str(e)}"
    
    # MD5 checksum
    md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    
    # Content structure metrics
    code_blocks = content.count('```')
    headers = sum(1 for line in content.split('\n') if line.strip().startswith('#'))

    # Table row count: lines that start and end with | are Markdown table rows.
    # This includes header rows and separator rows (e.g. |---|---|) — consistent
    # with how Copilot counts them, since it has no way to exclude separators either.
    # A single | on an otherwise empty line is excluded via the len > 1 guard.
    table_rows = sum(
        1 for line in content.split('\n')
        if line.strip().startswith('|') and line.strip().endswith('|') and len(line.strip()) > 1
    )

    # Detect potential truncation indicators
    truncation_indicators = []
    last_256 = content[-256:] if len(content) > 256 else content
    
    # Check for unclosed Markdown code blocks (odd number of ```)
    if content.count('```') % 2 != 0:
        truncation_indicators.append("Unclosed Markdown code block")
    
    # Check for mid-word truncation (ends with alphanumeric, not whitespace/punctuation)
    last_char = content[-1] if content else ''
    if last_char.isalnum():
        truncation_indicators.append("Ends mid-word (last char is alphanumeric)")
    
    # Check for incomplete Markdown links
    if last_256.count('[') > last_256.count(']'):
        truncation_indicators.append("Unclosed Markdown link bracket")
    if last_256.count('](') > last_256.count(')'):
        truncation_indicators.append("Incomplete Markdown link")
    
    # Check for incomplete table row (starts with | but doesn't complete)
    last_line = content.split('\n')[-1] if '\n' in content else content
    if last_line.strip().startswith('|') and not last_line.strip().endswith('|'):
        truncation_indicators.append("Incomplete Markdown table row")
    
    # Note: We do NOT check for HTML braces/brackets since content may be 
    # converted from HTML to Markdown, stripping those elements
    
    return {
        "exists": True,
        "byte_count": byte_count,
        "char_count": char_count,
        "line_count": line_count,
        "word_count": word_count,
        "token_count": token_count,
        "md5_checksum": md5_hash,
        "code_blocks": code_blocks // 2 if code_blocks > 0 else 0,  # Divide by 2 (opening + closing)
        "table_rows": table_rows,
        "headers": headers,
        "truncation_indicators": truncation_indicators,
        "last_50_chars": content[-50:] if len(content) > 50 else content,
    }

def format_size(bytes_count: int) -> str:
    """Format byte count as human-readable size"""
    if bytes_count < 1024:
        return f"{bytes_count}B"
    elif bytes_count < 1024 * 1024:
        return f"{bytes_count / 1024:.2f}KB"
    else:
        return f"{bytes_count / (1024 * 1024):.2f}MB"

def print_metrics_table(results: Dict[str, Dict]):
    """Print metrics in a formatted table"""
    
    if not results:
        print("No results to display")
        return
    
    # Print header
    print("\n" + "=" * 100)
    print("RAW OUTPUT VERIFICATION METRICS")
    print("=" * 100)
    
    for test_id, metrics in results.items():
        print(f"\nTest ID: {test_id}")
        print("-" * 100)
        
        if not metrics.get("exists", False):
            print(f"  ❌ {metrics.get('error', 'Unknown error')}")
            continue
        
        # Size metrics
        print(f"  File Size:        {format_size(metrics['byte_count'])} ({metrics['byte_count']:,} bytes)")
        print(f"  Character Count:  {metrics['char_count']:,}")
        print(f"  Line Count:       {metrics['line_count']:,}")
        print(f"  Word Count:       {metrics['word_count']:,}")
        
        # Token count
        if metrics['token_count'] is not None:
            if isinstance(metrics['token_count'], int):
                char_per_token = metrics['char_count'] / metrics['token_count'] if metrics['token_count'] > 0 else 0
                print(f"  Token Count:      {metrics['token_count']:,} (cl100k_base)")
                # Chars per token tells you how many characters are in each token; this is a ratio
                print(f"  Chars/Token:      {char_per_token:.2f}")
            else:
                print(f"  Token Count:      {metrics['token_count']}")
        else:
            print(f"  Token Count:      N/A (tiktoken not installed)")
        
        # Content structure
        print(f"\n  Content Structure:")
        print(f"    Code Blocks:    {metrics['code_blocks']}")
        print(f"    Table Rows:     {metrics['table_rows']}")
        print(f"    Headers:        {metrics['headers']}")
        
        # Checksum
        print(f"\n  MD5 Checksum:     {metrics['md5_checksum']}")
        
        # Truncation analysis
        if metrics['truncation_indicators']:
            print(f"\n  ⚠️  Truncation Indicators:")
            for indicator in metrics['truncation_indicators']:
                print(f"    - {indicator}")
        else:
            print(f"\n  ✓ No truncation indicators detected")
        
        # Last 50 characters
        print(f"\n  Last 50 Characters:")
        last_50 = metrics['last_50_chars'].replace('\n', '\\n').replace('\r', '\\r')
        print(f"    '{last_50}'")
        
        print()

def main():
    parser = argparse.ArgumentParser(
        description="Verify metrics for raw output files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run from copilot-web-content-retrieval/ directory
  python3 web_content_retrieval_verify_raw_results.py BL-1
  python3 web_content_retrieval_verify_raw_results.py BL-1 SC-2 EC-1
  python3 web_content_retrieval_verify_raw_results.py --all
  
  # Custom results directory
  python3 web_content_retrieval_verify_raw_results.py BL-1 --results-dir /path/to/results/raw
  
  # Custom path to specific file
  python3 web_content_retrieval_verify_raw_results.py --path results/raw/raw_output_BL-1.txt
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
    
    # Smart path detection: check if we're in copilot-web-content-retrieval/ or project root
    results_dir = Path(args.results_dir)
    
    # If the default path doesn't exist, try alternative locations
    if not results_dir.exists() and args.results_dir == 'copilot-web-content-retrieval/results/raw':
        # Try current directory (if we're already in copilot-web-content-retrieval/)
        alt_dir = Path('results/raw')
        if alt_dir.exists():
            results_dir = alt_dir
        else:
            # Try going up one level and then down (if we're in a subdirectory)
            alt_dir = Path('../copilot-web-content-retrieval/results/raw')
            if alt_dir.exists():
                results_dir = alt_dir
    
    results = {}
    
    if args.path:
        # Verify specific file
        filepath = Path(args.path)
        test_id = filepath.stem  # Use filename without extension as test_id
        results[test_id] = calculate_metrics(filepath)
    
    elif args.all:
        # Verify all files in results directory
        if not results_dir.exists():
            print(f"Error: Directory {results_dir} does not exist")
            print(f"Tried to find results in: {results_dir.resolve()}")
            print(f"\nMake sure you're running from either:")
            print(f"  - Project root (agent-ecosystem-testing/)")
            print(f"  - copilot-web-content-retrieval/ directory")
            sys.exit(1)
        
        for filepath in sorted(results_dir.glob('raw_output_*.txt')):
            # Extract test ID from filename
            test_id = filepath.stem.replace('raw_output_', '')
            results[test_id] = calculate_metrics(filepath)
        
        if not results:
            print(f"No raw output files found in {results_dir}")
            sys.exit(1)
    
    elif args.test_ids:
        # Verify specific test IDs
        for test_id in args.test_ids:
            filepath = results_dir / f'raw_output_{test_id}.txt'
            results[test_id] = calculate_metrics(filepath)
    
    else:
        parser.print_help()
        sys.exit(1)
    
    # Print results
    print_metrics_table(results)
    
    # Summary statistics
    successful = sum(1 for m in results.values() if m.get('exists', False))
    print("=" * 100)
    print(f"Summary: {successful}/{len(results)} files verified successfully")
    print("=" * 100 + "\n")

if __name__ == "__main__":
    main()