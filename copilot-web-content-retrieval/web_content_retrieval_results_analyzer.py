#!/usr/bin/env python3
"""
Copilot Web Content Retrieval Testing Results Analyzer
- Analyzes CSV results, identifies truncation patterns, and generates summary report
- Compares interpreted and raw track measurements
- Matches findings to hypotheses, H1-H5

Usage:
    # From copilot-web-content-retrieval/ directory
    python web_content_retrieval_results_analyzer.py --csv results/raw/results.csv --full
    python web_content_retrieval_results_analyzer.py --csv results/raw/results.csv --summary
    python web_content_retrieval_results_analyzer.py --csv results/raw/results.csv --method vscode-chat

    python web_content_retrieval_results_analyzer.py --csv results/copilot-interpreted/results.csv --full
    python web_content_retrieval_results_analyzer.py --csv results/copilot-interpreted/results.csv --summary
    python web_content_retrieval_results_analyzer.py --csv results/copilot-interpreted/results.csv --method vscode-chat

    python web_content_retrieval_results_analyzer.py \
        --csv results/copilot-interpreted/results.csv results/raw/results.csv --full
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import argparse

class CopilotResultsAnalyzer:
    """Analyze Copilot testing results"""

    def __init__(self, csv_paths):
        if isinstance(csv_paths, (str, Path)):
            csv_paths = [csv_paths]

        self.csv_paths = [Path(csv_path) for csv_path in csv_paths]
        for csv_path in self.csv_paths:
            if not csv_path.exists():
                raise FileNotFoundError(f"CSV file not found: {csv_path}")

        self.results = []
        self._load_csv()

    @staticmethod
    def _parse_optional_int(value):
        """Convert a CSV field to int when populated, otherwise return None."""
        if value is None:
            return None

        if isinstance(value, int):
            return value

        value = str(value).strip()
        if value == "":
            return None

        return int(value)

    def _normalize_row(self, row, inferred_track: str):
        """Normalize interpreted and raw CSV schemas into shared analysis fields."""
        normalized_row = dict(row)

        normalized_row["input_est_chars"] = self._parse_optional_int(row.get("input_est_chars")) or 0

        if 'track' not in normalized_row or not normalized_row.get('track') or normalized_row.get('track', '').strip() == '':
            normalized_row['track'] = inferred_track

        normalized_row["output_chars"] = self._parse_optional_int(row.get("output_chars"))
        normalized_row["tokens_est"] = self._parse_optional_int(row.get("tokens_est"))
        normalized_row["truncation_char_num"] = self._parse_optional_int(row.get("truncation_char_num"))

        if normalized_row["track"] == "raw":
            normalized_row["output_chars"] = (
                normalized_row["output_chars"]
                or self._parse_optional_int(row.get("verified_file_size_bytes"))
                or self._parse_optional_int(row.get("copilot_reported_output_chars"))
                or self._parse_optional_int(row.get("copilot_reported_file_size_bytes"))
                or 0
            )
            normalized_row["tokens_est"] = (
                normalized_row["tokens_est"]
                or self._parse_optional_int(row.get("verified_tokens"))
                or self._parse_optional_int(row.get("copilot_reported_tokens_est"))
                or 0
            )
            normalized_row["truncation_char_num"] = (
                normalized_row["truncation_char_num"]
                or self._parse_optional_int(row.get("copilot_reported_truncation_point"))
            )
            if not normalized_row.get("truncated"):
                normalized_row["truncated"] = row.get("copilot_reported_truncated", "")
        else:
            normalized_row["output_chars"] = normalized_row["output_chars"] or 0
            normalized_row["tokens_est"] = normalized_row["tokens_est"] or 0

        return normalized_row

    def _load_csv(self):
        """Load results from one or more CSV files and infer track per file path"""
        total_loaded_count = 0
        total_skipped_count = 0

        for csv_path in self.csv_paths:
            path_str = str(csv_path).lower()
            if 'raw' in path_str:
                inferred_track = 'raw'
            elif 'interpreted' in path_str or 'copilot-interpreted' in path_str:
                inferred_track = 'interpreted'
            else:
                inferred_track = 'unknown'

            loaded_count = 0
            skipped_count = 0
            test_ids_loaded = []

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (line 1 is header)
                    try:
                        normalized_row = self._normalize_row(row, inferred_track)

                        self.results.append(normalized_row)
                        test_ids_loaded.append(normalized_row.get('test_id', 'UNKNOWN'))
                        loaded_count += 1

                    except ValueError as e:
                        print(
                            f"⚠️  Skipped row {row_num} from {csv_path.name} "
                            f"(test_id: {row.get('test_id', 'UNKNOWN')}) - conversion error: {e}"
                        )
                        skipped_count += 1
                    except KeyError as e:
                        print(f"⚠️  Skipped row {row_num} from {csv_path.name} - missing field: {e}")
                        skipped_count += 1
                    except Exception as e:
                        print(f"⚠️  Skipped row {row_num} from {csv_path.name} - unexpected error: {e}")
                        skipped_count += 1

            total_loaded_count += loaded_count
            total_skipped_count += skipped_count

            print(f"Loaded {loaded_count} test results from {csv_path.name}")
            if skipped_count > 0:
                print(f"⚠️  Skipped {skipped_count} rows due to errors")
            print(f"Inferred track: {inferred_track}")
            print(f"Test IDs loaded: {', '.join(test_ids_loaded)}\n")

        if len(self.csv_paths) > 1:
            print(
                f"Merged {total_loaded_count} total test results from "
                f"{len(self.csv_paths)} CSV files"
            )
            if total_skipped_count > 0:
                print(f"⚠️  Skipped {total_skipped_count} total rows due to errors")
            print()

    def filter_by_method(self, method: str):
        """Filter results by web content retrieval method"""
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
        """Analyze differences between web content retrieval methods"""
        print("=" * 80)
        print("METHOD COMPARISON (vscode-chat vs UI-chat)")
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
                print(f"  OP-3 (vscode-chat vs UI-chat):")
                for r in op3_results:
                    print(f"    - {r['output_chars']:,} chars, truncated: {r['truncated']}")

            print()

    def analyze_by_track(self):
        """Compare interpreted vs raw track measurements"""
        print("=" * 80)
        print("INTERPRETED vs RAW TRACK COMPARISON")
        print("=" * 80 + "\n")

        tracks_present = {r.get("track") for r in self.results}
        if not {"interpreted", "raw"}.issubset(tracks_present):
            print("Both interpreted and raw track results are required for comparison.\n")
            return

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
        if len(self.csv_paths) == 1:
            print(f"Results from: {self.csv_paths[0]}\n")
        else:
            joined_paths = ", ".join(str(path) for path in self.csv_paths)
            print(f"Results from: {joined_paths}\n")

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
        web_tests = [r for r in self.results if r["method"] == "vscode-chat"]

        if mcp_tests and web_tests:
            print("vscode-chat vs UI-chat:")
            print(f"  vscode-chat tests: {len(web_tests)}")
            print(f"  MCP tests: {len(mcp_tests)}")
            print(f"  → Compare OP-3 results to determine if MCP overrides vscode-chat limits\n")

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
        print("  2. Compare vscode-chat vs UI-chat on OP-3 if applicable")
        print("  3. Run SC-1 through SC-4 for structure-aware truncation analysis")
        print("  4. Execute OP-4 to test auto-chunking behavior")
        print("  5. Review edge cases (EC-1, EC-3, EC-6)")

        print()

def main():
    parser = argparse.ArgumentParser(
        description="Copilot Web Content Retrieval Testing Results Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_content_retrieval_results_analyzer.py --csv results/raw/results.csv --summary
  python web_content_retrieval_results_analyzer.py --csv results/copilot-interpreted/results.csv --full
    python web_content_retrieval_results_analyzer.py --csv results/copilot-interpreted/results.csv results/raw/results.csv --full
        """,
    )

    parser.add_argument(
                "--csv",
                type=str,
                nargs="+",
                required=True,
                help="One or two paths to results CSV files to analyze together",
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

    if len(args.csv) > 2:
        parser.error("--csv accepts at most two files: interpreted and raw")

    analyzer = CopilotResultsAnalyzer(args.csv)

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
