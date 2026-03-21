#!/usr/bin/env python3
"""
Cursor Testing Results Analyzer
- Analyzes CSV results, identifies truncation patterns, and generates summary report
- Compares interpreted and raw track measurements
- Matches findings to hypotheses, H1-H5
- Exports results as Markdown table for spec contribution

Usage:
    python web_fetch_results_analyzer.py --csv results/raw/results.csv --full
    python web_fetch_results_analyzer.py --csv results/raw/results.csv --summary
    python web_fetch_results_analyzer.py --csv results/raw/results.csv --method @Web

    python web_fetch_results_analyzer.py --csv results/cursor-interpreted/results.csv --full
    python web_fetch_results_analyzer.py --csv results/cursor-interpreted/results.csv --summary
    python web_fetch_results_analyzer.py --csv results/cursor-interpreted/results.csv --method @Web
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import argparse

class CursorResultsAnalyzer:
    """Analyze Cursor testing results"""

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        self.results = []
        self._load_csv()

    def _load_csv(self):
        """Load results from CSV and infer track from file path"""
        # Infer track from file path
        path_str = str(self.csv_path).lower()
        if 'raw' in path_str:
            inferred_track = 'raw'
        elif 'interpreted' in path_str or 'cursor-interpreted' in path_str:
            inferred_track = 'interpreted'
        else:
            inferred_track = 'unknown'
        
        loaded_count = 0
        skipped_count = 0
        test_ids_loaded = []
        
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (line 1 is header)
                try:
                    # Convert numeric fields
                    row["input_est_chars"] = int(row["input_est_chars"])
                    row["output_chars"] = int(row["output_chars"])
                    row["tokens_est"] = int(row["tokens_est"])
                    if row.get("truncation_char_num") and row["truncation_char_num"] != "":
                        row["truncation_char_num"] = int(row["truncation_char_num"])
                    else:
                        row["truncation_char_num"] = None
                    
                    # Add inferred track (override if track column exists but is empty/wrong)
                    if 'track' not in row or not row.get('track') or row.get('track', '').strip() == '':
                        row['track'] = inferred_track
                    
                    self.results.append(row)
                    test_ids_loaded.append(row.get('test_id', 'UNKNOWN'))
                    loaded_count += 1
                    
                except ValueError as e:
                    print(f"⚠️  Skipped row {row_num} (test_id: {row.get('test_id', 'UNKNOWN')}) - conversion error: {e}")
                    skipped_count += 1
                except KeyError as e:
                    print(f"⚠️  Skipped row {row_num} - missing field: {e}")
                    skipped_count += 1
                except Exception as e:
                    print(f"⚠️  Skipped row {row_num} - unexpected error: {e}")
                    skipped_count += 1

        print(f"Loaded {loaded_count} test results from {self.csv_path.name}")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} rows due to errors")
        print(f"Inferred track: {inferred_track}")
        
        # Show all test IDs loaded for verification
        print(f"Test IDs loaded: {', '.join(test_ids_loaded)}\n")

    def filter_by_method(self, method: str):
        """Filter results by fetch method"""
        return [r for r in self.results if r["method"] == method]

    def filter_by_track(self, track: str):
        """Filter results by track (interpreted/raw)"""
        return [r for r in self.results if r.get("track") == track]

    def filter_by_test_id(self, test_id: str):
        """Filter results by test ID"""
        return [r for r in self.results if r["test_id"] == test_id]

    def analyze_truncation_threshold(self):
        """Identify truncation threshold across all results"""
        print("=" * 80)
        print("TRUNCATION THRESHOLD ANALYSIS")
        print("=" * 80 + "\n")

        truncated_tests = [r for r in self.results if r["truncated"] == "yes"]
        non_truncated_tests = [r for r in self.results if r["truncated"] == "no"]

        if not truncated_tests:
            print("No truncation detected in any tests.\n")
            return

        # Find the pattern
        truncation_points = [r["truncation_char_num"] for r in truncated_tests if r["truncation_char_num"]]
        
        if truncation_points:
            avg_truncation = mean(truncation_points)
            print(f"Truncation Points Found:")
            print(f"  Average: {avg_truncation:,.0f} characters")
            if len(truncation_points) > 1:
                print(f"  Stdev: {stdev(truncation_points):,.0f}")
            print(f"  Min: {min(truncation_points):,.0f}")
            print(f"  Max: {max(truncation_points):,.0f}\n")

        # Analyze input sizes
        print("Input Sizes Where Truncation Occurred:")
        for r in sorted(truncated_tests, key=lambda x: x["input_est_chars"]):
            print(
                f"  {r['test_id']}: {r['input_est_chars']:,} chars input → {r['output_chars']:,} chars output"
            )

        print("\nInput Sizes Where NO Truncation Occurred:")
        for r in sorted(non_truncated_tests, key=lambda x: x["input_est_chars"]):
            print(f"  {r['test_id']}: {r['input_est_chars']:,} chars → {r['output_chars']:,} chars (full)")

        print()

    def analyze_by_method(self):
        """Analyze differences between fetch methods"""
        print("=" * 80)
        print("METHOD COMPARISON (@Web vs MCP)")
        print("=" * 80 + "\n")

        methods = set(r["method"] for r in self.results)
        for method in sorted(methods):
            results = self.filter_by_method(method)
            truncated_count = len([r for r in results if r["truncated"] == "yes"])

            print(f"{method}:")
            print(f"  Tests run: {len(results)}")
            print(f"  Truncation events: {truncated_count}")
            print(f"  Avg output size: {mean(r['output_chars'] for r in results):,.0f} chars")

            # Group by test_id to find OP-3 comparison
            test_ids = set(r["test_id"] for r in results)
            if "OP-3" in test_ids:
                op3_results = [r for r in results if r["test_id"] == "OP-3"]
                print(f"  OP-3 (MCP vs @Web comparison):")
                for r in op3_results:
                    print(f"    - {r['output_chars']:,} chars, truncated: {r['truncated']}")

            print()

    def analyze_by_track(self):
        """Compare interpreted vs raw track measurements"""
        print("=" * 80)
        print("INTERPRETED vs RAW TRACK COMPARISON")
        print("=" * 80 + "\n")

        # Group by test_id
        tests_by_id = defaultdict(list)
        for r in self.results:
            tests_by_id[r["test_id"]].append(r)

        for test_id in sorted(tests_by_id.keys()):
            results = tests_by_id[test_id]
            if len(results) < 2:
                continue

            interpreted = [r for r in results if r.get("track") == "interpreted"]
            raw = [r for r in results if r.get("track") == "raw"]

            if interpreted and raw:
                int_result = interpreted[0]
                raw_result = raw[0]

                print(f"{test_id}:")
                print(f"  Interpreted truncation: {int_result['truncated']}")
                print(f"  Raw truncation: {raw_result['truncated']}")
                print(
                    f"  Output size difference: {abs(int_result['output_chars'] - raw_result['output_chars']):,} chars"
                )

                # Check for divergence
                if int_result["truncated"] != raw_result["truncated"]:
                    print(f"  ⚠️  DIVERGENCE: Tracks disagree on truncation")
                print()

    def identify_hypothesis(self):
        """Attempt to identify which truncation hypothesis best fits"""
        print("=" * 80)
        print("HYPOTHESIS MATCHING")
        print("=" * 80 + "\n")

        print("Hypotheses to evaluate:")
        print("  H1: Character-based truncation at fixed limit (e.g., 10,000 chars)")
        print("  H2: Token-based truncation (e.g., 2,000 tokens ≈ 8,000 chars)")
        print("  H3: Structure-aware truncation (respects markdown boundaries)")
        print("  H4: MCP servers override native limits")
        print("  H5: Agent auto-chunks after truncation\n")

        # Look at hypothesis matches in results
        hypothesis_counts = defaultdict(int)
        for r in self.results:
            if r.get("hypothesis_match"):
                hypothesis_counts[r["hypothesis_match"]] += 1

        print("Hypothesis matches from test results:")
        for hyp, count in sorted(hypothesis_counts.items(), key=lambda x: -x[1]):
            print(f"  {hyp}: {count} tests")

        # Analyze character/token ratio
        raw_results = self.filter_by_track("raw")
        if raw_results:
            chars_to_tokens = []
            for r in raw_results:
                if r["tokens_est"] > 0:
                    ratio = r["output_chars"] / r["tokens_est"]
                    chars_to_tokens.append(ratio)

            if chars_to_tokens:
                avg_ratio = mean(chars_to_tokens)
                print(f"\nCharacter-to-token ratio:")
                print(f"  Average: {avg_ratio:.2f} chars per token")
                print(f"  Typical token size: ~4 chars (Claude uses ~0.25 tokens per char)")
                if 3.5 <= avg_ratio <= 4.5:
                    print(f"  → Suggests TOKEN-BASED truncation (H2)")
                else:
                    print(f"  → Suggests CHARACTER-BASED truncation (H1)")

        print()

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print(f"\nTotal tests run: {len(self.results)}")
        print(f"Results from: {self.csv_path}\n")

        # Overall stats
        truncated = len([r for r in self.results if r["truncated"] == "yes"])
        print(f"Truncation Events: {truncated} / {len(self.results)}")
        print(
            f"Average output size: {mean(r['output_chars'] for r in self.results):,.0f} chars"
        )
        print(
            f"Average token count: {mean(r['tokens_est'] for r in self.results):,.0f} tokens\n"
        )

        # Methods tested
        methods = set(r["method"] for r in self.results)
        print(f"Methods tested: {', '.join(sorted(methods))}\n")

        # MCP comparison status
        mcp_tests = [r for r in self.results if "mcp" in r["method"].lower()]
        web_tests = [r for r in self.results if r["method"] == "@Web"]

        if mcp_tests and web_tests:
            print("MCP vs @Web Status:")
            print(f"  @Web tests: {len(web_tests)}")
            print(f"  MCP tests: {len(mcp_tests)}")
            print(f"  → Compare OP-3 results to determine if MCP overrides @Web limits\n")

        # Auto-chunking analysis
        op4_results = self.filter_by_test_id("OP-4")
        if op4_results:
            print("Agent Auto-chunking (OP-4):")
            for r in op4_results:
                notes_preview = r.get('notes', '')[:60] + '...' if len(r.get('notes', '')) > 60 else r.get('notes', '')
                print(f"  {r.get('track', 'unknown')}: {notes_preview}")
            print()

        print("Next steps:")
        print("  1. Run remaining baseline tests (BL-3 if not complete)")
        print("  2. Compare MCP vs @Web on OP-3")
        print("  3. Run SC-1 through SC-4 for structure-aware truncation analysis")
        print("  4. Execute OP-4 to test auto-chunking behavior")
        print("  5. Review edge cases (EC-1, EC-3, EC-6)")

        print()

    def print_markdown_table(self):
        """Print results as markdown table for spec contribution"""
        print("\n" + "=" * 80)
        print("RESULTS AS MARKDOWN TABLE (for Agent Docs Spec)")
        print("=" * 80 + "\n")

        # Try to get raw track results, fall back to all results
        raw_results = self.filter_by_track("raw")
        results_to_print = raw_results if raw_results else self.results
        
        if not results_to_print:
            print("No results to display.\n")
            return

        print(
            "| Test ID | Input (KB) | Output (KB) | Truncated | Truncation Point | Method | Notes |"
        )
        print(
            "|---------|-----------|-----------|----------|------------------|--------|-------|"
        )

        for r in sorted(results_to_print, key=lambda x: x["test_id"]):
            input_kb = r["input_est_chars"] / 1024
            output_kb = r["output_chars"] / 1024
            trunc_point = (
                f"{r['truncation_char_num']:,}" if r["truncation_char_num"] else "N/A"
            )
            notes_preview = r.get('notes', '')[:30] + '...' if len(r.get('notes', '')) > 30 else r.get('notes', '')

            print(
                f"| {r['test_id']} | {input_kb:.0f} | {output_kb:.0f} | {r['truncated']} | {trunc_point} | {r['method']} | {notes_preview} |"
            )

        print()


def main():
    parser = argparse.ArgumentParser(
        description="Cursor Testing Results Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_fetch_results_analyzer.py --csv results/raw/results.csv --summary
  python web_fetch_results_analyzer.py --csv results/cursor-interpreted/results.csv --summary
  python web_fetch_results_analyzer.py --csv results/raw/results.csv --method "@Web"
  python web_fetch_results_analyzer.py --csv results/raw/results.csv --markdown
        """,
    )

    parser.add_argument(
        "--csv", type=str, required=True, help="Path to results CSV file"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Print comprehensive summary"
    )
    parser.add_argument("--method", type=str, help="Analyze specific method")
    parser.add_argument(
        "--markdown", action="store_true", help="Output results as markdown table"
    )
    parser.add_argument(
        "--full", action="store_true", help="Run all analyses"
    )

    args = parser.parse_args()

    analyzer = CursorResultsAnalyzer(args.csv)

    if args.full:
        print("\n" + "=" * 80)
        print("FULL ANALYSIS REPORT")
        print("=" * 80)
        analyzer.generate_summary_report()
        analyzer.analyze_truncation_threshold()
        analyzer.analyze_by_method()
        analyzer.analyze_by_track()
        analyzer.identify_hypothesis()

    elif args.summary:
        print("\n" + "=" * 80)
        print("SUMMARY REPORT")
        print("=" * 80)
        analyzer.generate_summary_report()

    elif args.markdown:
        analyzer.print_markdown_table()

    elif args.method:
        method_results = analyzer.filter_by_method(args.method)
        print(f"Results for {args.method}:\n")
        for r in method_results:
            print(f"{r['test_id']}: {r['output_chars']:,} chars, truncated: {r['truncated']}")
        print()

    else:
        analyzer.analyze_truncation_threshold()
        analyzer.identify_hypothesis()

if __name__ == "__main__":
    main()
