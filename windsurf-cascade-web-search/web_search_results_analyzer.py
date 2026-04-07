#!/usr/bin/env python3
"""
Cascade Web Search Testing Results Analyzer
- Analyzes CSV results, identifies truncation patterns, and generates summary report
- Compares interpreted, raw, and explicit track measurements
- Isolates @web directive effect, implicit vs explicit tracks
- Matches findings to hypotheses H1-H5

Usage:
    # From windsurf-cascade-web-search/ directory

    # Single track
    python web_search_results_analyzer.py --csv results/raw/results.csv --full
    python web_search_results_analyzer.py --csv results/cascade-interpreted/results.csv --summary
    python web_search_results_analyzer.py --csv results/explicit/results.csv --summary

    # Cross-track comparison (two or three CSVs)
    python web_search_results_analyzer.py \\
        --csv results/cascade-interpreted/results.csv results/explicit/results.csv --full

    python web_search_results_analyzer.py \\
        --csv results/cascade-interpreted/results.csv \\
               results/raw/results.csv \\
               results/explicit/results.csv --full
"""

import csv
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import argparse


class CascadeResultsAnalyzer:
    """Analyze Cascade web search testing results across three tracks."""

    def __init__(self, csv_paths):
        if isinstance(csv_paths, (str, Path)):
            csv_paths = [csv_paths]

        self.csv_paths = [Path(p) for p in csv_paths]
        for p in self.csv_paths:
            if not p.exists():
                raise FileNotFoundError(f"CSV file not found: {p}")

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

    @staticmethod
    def _parse_optional_float(value):
        """Convert a CSV field to float when populated, otherwise return None."""
        if value is None:
            return None
        if isinstance(value, float):
            return value
        value = str(value).strip()
        if value == "":
            return None
        return float(value)

    def _infer_track(self, csv_path: Path) -> str:
        """Infer track from CSV path."""
        path_str = str(csv_path).lower()
        if 'explicit' in path_str:
            return 'explicit'
        if 'raw' in path_str:
            return 'raw'
        if 'interpreted' in path_str:
            return 'interpreted'
        return 'unknown'

    def _normalize_row(self, row: dict, inferred_track: str) -> dict:
        """Normalize CSV row into shared analysis fields across all three tracks."""
        normalized = dict(row)

        # Track — prefer field value, fall back to inferred
        if not normalized.get('track', '').strip():
            normalized['track'] = inferred_track

        normalized['input_est_chars'] = self._parse_optional_int(row.get('input_est_chars')) or 0

        # Core output fields — resolve from track-appropriate sources
        if normalized['track'] == 'raw':
            normalized['output_chars'] = (
                self._parse_optional_int(row.get('output_chars'))
                or self._parse_optional_int(row.get('verified_file_size_bytes'))
                or self._parse_optional_int(row.get('cascade_reported_output_chars'))
                or self._parse_optional_int(row.get('cascade_reported_file_size_bytes'))
                or 0
            )
            normalized['tokens_est'] = (
                self._parse_optional_int(row.get('tokens_est'))
                or self._parse_optional_int(row.get('verified_tokens'))
                or self._parse_optional_int(row.get('cascade_reported_tokens_est'))
                or 0
            )
            normalized['truncation_char_num'] = (
                self._parse_optional_int(row.get('truncation_char_num'))
                or self._parse_optional_int(row.get('cascade_reported_truncation_point'))
            )
            if not normalized.get('truncated'):
                normalized['truncated'] = row.get('cascade_reported_truncated', '')
        else:
            # Interpreted and explicit tracks: all data is Cascade-reported by definition
            normalized['output_chars'] = self._parse_optional_int(row.get('output_chars')) or 0
            normalized['tokens_est'] = self._parse_optional_int(row.get('tokens_est')) or 0
            normalized['truncation_char_num'] = self._parse_optional_int(row.get('truncation_char_num'))

        # Cascade-specific behavioral fields
        normalized['approval_required'] = row.get('approval_required', '').strip() or 'unknown'
        normalized['pagination_observed'] = row.get('pagination_observed', '').strip() or 'unknown'

        return normalized

    def _load_csv(self):
        """Load and normalize results from one or more CSV files."""
        total_loaded = 0
        total_skipped = 0

        for csv_path in self.csv_paths:
            inferred_track = self._infer_track(csv_path)
            loaded = 0
            skipped = 0
            test_ids = []

            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    try:
                        normalized = self._normalize_row(row, inferred_track)
                        self.results.append(normalized)
                        test_ids.append(normalized.get('test_id', 'UNKNOWN'))
                        loaded += 1
                    except ValueError as e:
                        print(f"⚠️  Skipped row {row_num} from {csv_path.name} "
                              f"(test_id: {row.get('test_id', 'UNKNOWN')}) — conversion error: {e}")
                        skipped += 1
                    except KeyError as e:
                        print(f"⚠️  Skipped row {row_num} from {csv_path.name} — missing field: {e}")
                        skipped += 1
                    except Exception as e:
                        print(f"⚠️  Skipped row {row_num} from {csv_path.name} — unexpected error: {e}")
                        skipped += 1

            total_loaded += loaded
            total_skipped += skipped
            print(f"Loaded {loaded} results from {csv_path.name} (track: {inferred_track})")
            if skipped:
                print(f"⚠️  Skipped {skipped} rows due to errors")
            print(f"Test IDs: {', '.join(test_ids)}\n")

        if len(self.csv_paths) > 1:
            print(f"Merged {total_loaded} total results from {len(self.csv_paths)} CSV files")
            if total_skipped:
                print(f"⚠️  Skipped {total_skipped} total rows")
            print()

    # --- Filters ---

    def filter_by_track(self, track: str):
        return [r for r in self.results if r.get('track') == track]

    def filter_by_method(self, method: str):
        return [r for r in self.results if r.get('method') == method]

    def filter_by_test_id(self, test_id: str):
        return [r for r in self.results if r['test_id'] == test_id]

    # --- Analyses ---

    def analyze_truncation_threshold(self):
        """Identify truncation threshold patterns across all results."""
        print("=" * 80)
        print("TRUNCATION THRESHOLD ANALYSIS")
        print("=" * 80 + "\n")

        truncated = [r for r in self.results if r.get('truncated') == 'yes']
        not_truncated = [r for r in self.results if r.get('truncated') == 'no']

        if not truncated:
            print("No truncation detected in any tests.\n")
            return

        truncation_points = [
            r['truncation_char_num'] for r in truncated if r.get('truncation_char_num')
        ]

        if truncation_points:
            print("Truncation Points:")
            print(f"  Average: {mean(truncation_points):,.0f} characters")
            if len(truncation_points) > 1:
                print(f"  Stdev:   {stdev(truncation_points):,.0f}")
            print(f"  Min:     {min(truncation_points):,.0f}")
            print(f"  Max:     {max(truncation_points):,.0f}\n")

        print("Input sizes where truncation occurred:")
        for r in sorted(truncated, key=lambda x: x['input_est_chars']):
            print(f"  {r['test_id']} [{r.get('track','?')}]: "
                  f"{r['input_est_chars']:,} chars in → {r['output_chars']:,} chars out")

        print("\nInput sizes where NO truncation occurred:")
        for r in sorted(not_truncated, key=lambda x: x['input_est_chars']):
            print(f"  {r['test_id']} [{r.get('track','?')}]: "
                  f"{r['input_est_chars']:,} chars in → {r['output_chars']:,} chars out (full)")
        print()

    def analyze_implicit_vs_explicit(self):
        """
        Compare implicit, no @web vs explicit, @web, tracks.
        This is the primary Cascade-specific analysis — isolates @web as a variable.
        """
        print("=" * 80)
        print("IMPLICIT vs EXPLICIT TRACK COMPARISON (@web effect)")
        print("=" * 80 + "\n")

        implicit = self.filter_by_track('interpreted')
        explicit = self.filter_by_track('explicit')

        if not implicit or not explicit:
            print("Both interpreted (implicit) and explicit track results required.\n")
            return

        # Group by test_id for paired comparison
        implicit_by_id = {r['test_id']: r for r in implicit}
        explicit_by_id = {r['test_id']: r for r in explicit}
        shared_ids = sorted(set(implicit_by_id) & set(explicit_by_id))

        if not shared_ids:
            print("No test IDs present in both tracks for comparison.\n")
            return

        divergences = []

        for test_id in shared_ids:
            imp = implicit_by_id[test_id]
            exp = explicit_by_id[test_id]

            output_delta = exp['output_chars'] - imp['output_chars']
            truncation_divergence = imp.get('truncated') != exp.get('truncated')

            print(f"{test_id}:")
            print(f"  Implicit output:  {imp['output_chars']:,} chars  truncated: {imp.get('truncated','?')}")
            print(f"  Explicit output:  {exp['output_chars']:,} chars  truncated: {exp.get('truncated','?')}")
            print(f"  Output delta:     {output_delta:+,} chars")

            if truncation_divergence:
                print(f"  ⚠️  TRUNCATION DIVERGENCE — tracks disagree")
                divergences.append(test_id)

            # Tool chain comparison
            imp_tools = imp.get('tools_used', '')
            exp_tools = exp.get('tools_used', '')
            if imp_tools or exp_tools:
                if imp_tools != exp_tools:
                    print(f"  Tool chain differs:")
                    print(f"    Implicit: {imp_tools or 'not recorded'}")
                    print(f"    Explicit: {exp_tools or 'not recorded'}")
                else:
                    print(f"  Tool chain identical: {imp_tools}")

            print()

        # Summary
        if divergences:
            print(f"⚠️  Truncation divergences on: {', '.join(divergences)}")
            print(f"   → @web appears to affect retrieval behavior on these URLs\n")
        else:
            print(f"✓ No truncation divergences — @web may be redundant with autonomous behavior,")
            print(f"  consistent with the Cursor finding.\n")

    def analyze_by_track(self):
        """Compare interpreted, raw, and explicit track measurements."""
        print("=" * 80)
        print("THREE-TRACK COMPARISON (interpreted / raw / explicit)")
        print("=" * 80 + "\n")

        tracks_present = {r.get('track') for r in self.results}
        tests_by_id = defaultdict(list)
        for r in self.results:
            tests_by_id[r['test_id']].append(r)

        for test_id in sorted(tests_by_id):
            results = tests_by_id[test_id]
            by_track = {r.get('track'): r for r in results}

            if len(by_track) < 2:
                continue

            print(f"{test_id}:")
            for track in ('interpreted', 'raw', 'explicit'):
                if track in by_track:
                    r = by_track[track]
                    print(f"  {track:12s}: {r['output_chars']:>8,} chars  "
                          f"truncated: {r.get('truncated','?'):<3}  "
                          f"approval: {r.get('approval_required','?'):<7}  "
                          f"pagination: {r.get('pagination_observed','?')}")

            # Flag interpreted/explicit divergence
            if 'interpreted' in by_track and 'explicit' in by_track:
                if by_track['interpreted'].get('truncated') != by_track['explicit'].get('truncated'):
                    print(f"  ⚠️  Interpreted/explicit truncation mismatch")

            # Flag interpreted/raw divergence
            if 'interpreted' in by_track and 'raw' in by_track:
                if by_track['interpreted'].get('truncated') != by_track['raw'].get('truncated'):
                    print(f"  ⚠️  Interpreted/raw truncation mismatch — perception gap")

            print()

    def analyze_approval_behavior(self):
        """
        Analyze approval-gating behavior across runs.
        Cascade-specific: read_url_content requires explicit user approval before fetch.
        """
        print("=" * 80)
        print("APPROVAL-GATED FETCH ANALYSIS")
        print("=" * 80 + "\n")

        approval_counts = defaultdict(int)
        for r in self.results:
            approval_counts[r.get('approval_required', 'unknown')] += 1

        print("Approval behavior across all runs:")
        for value, count in sorted(approval_counts.items(), key=lambda x: -x[1]):
            print(f"  {value}: {count} runs")

        # Check if approval behavior varies by track
        print("\nApproval behavior by track:")
        for track in ('interpreted', 'raw', 'explicit'):
            track_results = self.filter_by_track(track)
            if not track_results:
                continue
            counts = defaultdict(int)
            for r in track_results:
                counts[r.get('approval_required', 'unknown')] += 1
            counts_str = ', '.join(f"{k}: {v}" for k, v in sorted(counts.items()))
            print(f"  {track}: {counts_str}")

        # Check if approval behavior varies by URL
        print("\nApproval behavior by test ID:")
        tests_by_id = defaultdict(list)
        for r in self.results:
            tests_by_id[r['test_id']].append(r)

        for test_id in sorted(tests_by_id):
            values = {r.get('approval_required', 'unknown') for r in tests_by_id[test_id]}
            if len(values) > 1:
                print(f"  {test_id}: ⚠️  inconsistent — {values}")
            else:
                print(f"  {test_id}: {next(iter(values))}")

        print()

    def analyze_pagination_behavior(self):
        """
        Analyze view_content_chunk auto-pagination behavior.
        Key unknown: does Cascade self-paginate automatically, or only when prompted?
        """
        print("=" * 80)
        print("AUTO-PAGINATION BEHAVIOR ANALYSIS (view_content_chunk)")
        print("=" * 80 + "\n")

        pagination_counts = defaultdict(int)
        for r in self.results:
            pagination_counts[r.get('pagination_observed', 'unknown')] += 1

        print("Pagination behavior across all runs:")
        for value, count in sorted(pagination_counts.items(), key=lambda x: -x[1]):
            label = {
                'yes-auto': 'Auto-paginated (no prompt)',
                'yes-prompted': 'Paginated when prompted',
                'no': 'No pagination',
                'unknown': 'Not recorded',
            }.get(value, value)
            print(f"  {value} ({label}): {count} runs")

        # Focus on OP-1 and OP-4 — the pagination test cases
        print("\nPagination on offset/pagination test cases (OP-1, OP-4):")
        for test_id in ('OP-1', 'OP-4'):
            op_results = self.filter_by_test_id(test_id)
            if not op_results:
                print(f"  {test_id}: no results")
                continue
            for r in op_results:
                print(f"  {test_id} [{r.get('track','?')}]: "
                      f"pagination={r.get('pagination_observed','?')}  "
                      f"tools={r.get('tools_used','not recorded')}")

        auto_paginated = [r for r in self.results if r.get('pagination_observed') == 'yes-auto']
        if auto_paginated:
            print(f"\n✓ Auto-pagination confirmed on {len(auto_paginated)} run(s) — "
                  f"structural capability not confirmed in Copilot or Cursor")
        else:
            print(f"\n— No auto-pagination observed yet")

        print()

    def analyze_elision_markers(self):
        """
        Analyze ellipsis elision markers in raw track output.
        In Copilot testing, '...' markers indicated fetch_webpage excerpt assembly
        rather than byte-boundary truncation — worth surfacing early for Cascade.
        """
        print("=" * 80)
        print("ELISION MARKER ANALYSIS (...)")
        print("=" * 80 + "\n")

        raw_results = self.filter_by_track('raw')
        if not raw_results:
            print("No raw track results available.\n")
            return

        print("Elision marker presence in raw track notes:")
        elision_found = []
        for r in raw_results:
            notes = r.get('notes', '').lower()
            if '...' in notes or 'elision' in notes or 'excerpt' in notes:
                elision_found.append(r)
                print(f"  {r['test_id']}: {r.get('notes','')[:80]}...")

        if elision_found:
            print(f"\n⚠️  Elision markers found in {len(elision_found)} raw run(s)")
            print(f"   → read_url_content may be performing excerpt assembly, not full retrieval")
            print(f"   → Compare with Copilot finding: '...' markers were retrieval-layer elision,")
            print(f"      not byte-boundary cutoffs. 'truncated: yes' may reflect incomplete sampling")
            print(f"      rather than a fixed character ceiling.")
        else:
            print("No elision markers noted in raw track results yet.")

        print()

    def identify_hypothesis(self):
        """Attempt to identify which truncation hypothesis best fits the data."""
        print("=" * 80)
        print("HYPOTHESIS MATCHING")
        print("=" * 80 + "\n")

        print("Hypotheses under evaluation:")
        print("  H1: Character-based truncation at a fixed ceiling")
        print("  H2: Token-based truncation (e.g., 2,000 tokens ≈ 8,000 chars)")
        print("  H3: Structure-aware truncation (respects Markdown boundaries)")
        print("  H4: @web directive changes the retrieval ceiling")
        print("  H5: Agent auto-chunks via view_content_chunk after truncation\n")

        hypothesis_counts = defaultdict(int)
        for r in self.results:
            if r.get('hypothesis_match'):
                hypothesis_counts[r['hypothesis_match']] += 1

        print("Hypothesis matches logged in results:")
        for hyp, count in sorted(hypothesis_counts.items(), key=lambda x: -x[1]):
            print(f"  {hyp}: {count} run(s)")

        # Chars-per-token ratio — helps distinguish H1 vs H2
        raw_results = self.filter_by_track('raw')
        ratios = [
            r['output_chars'] / r['tokens_est']
            for r in raw_results
            if r.get('tokens_est', 0) > 0
        ]
        if ratios:
            avg_ratio = mean(ratios)
            print(f"\nCharacter-to-token ratio (raw track):")
            print(f"  Average: {avg_ratio:.2f} chars/token")
            if 3.5 <= avg_ratio <= 4.5:
                print(f"  → Consistent with TOKEN-BASED truncation (H2)")
            else:
                print(f"  → Consistent with CHARACTER-BASED truncation (H1)")

        # H4: @web effect
        implicit = self.filter_by_track('interpreted')
        explicit = self.filter_by_track('explicit')
        if implicit and explicit:
            imp_avg = mean(r['output_chars'] for r in implicit if r['output_chars'])
            exp_avg = mean(r['output_chars'] for r in explicit if r['output_chars'])
            delta = exp_avg - imp_avg
            print(f"\n@web effect on output size (H4):")
            print(f"  Implicit avg: {imp_avg:,.0f} chars")
            print(f"  Explicit avg: {exp_avg:,.0f} chars")
            print(f"  Delta:        {delta:+,.0f} chars")
            if abs(delta) < 500:
                print(f"  → @web has negligible effect — consistent with Cursor finding (directive redundant)")
            else:
                print(f"  → @web produces meaningful output difference — H4 supported")

        # H5: auto-chunking
        auto_paginated = [r for r in self.results if r.get('pagination_observed') == 'yes-auto']
        print(f"\nAuto-chunking (H5):")
        if auto_paginated:
            print(f"  ✓ Auto-pagination confirmed on {len(auto_paginated)} run(s) — H5 supported")
        else:
            print(f"  — No auto-pagination observed yet")

        print()

    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        print(f"\nTotal runs analyzed: {len(self.results)}")
        paths_str = ', '.join(str(p) for p in self.csv_paths)
        print(f"Sources: {paths_str}\n")

        tracks_present = defaultdict(int)
        for r in self.results:
            tracks_present[r.get('track', 'unknown')] += 1
        print("Runs by track:")
        for track, count in sorted(tracks_present.items()):
            print(f"  {track}: {count}")

        truncated = [r for r in self.results if r.get('truncated') == 'yes']
        print(f"\nTruncation events: {len(truncated)} / {len(self.results)}")

        output_chars = [r['output_chars'] for r in self.results if r.get('output_chars')]
        if output_chars:
            print(f"Average output size: {mean(output_chars):,.0f} chars")

        tokens = [r['tokens_est'] for r in self.results if r.get('tokens_est')]
        if tokens:
            print(f"Average token count: {mean(tokens):,.0f} tokens")

        # Approval behavior summary
        approval_yes = sum(1 for r in self.results if r.get('approval_required') == 'yes')
        print(f"\nApproval-gated fetch: {approval_yes} / {len(self.results)} runs prompted for approval")

        # Pagination summary
        auto_pag = sum(1 for r in self.results if r.get('pagination_observed') == 'yes-auto')
        prompted_pag = sum(1 for r in self.results if r.get('pagination_observed') == 'yes-prompted')
        print(f"Auto-pagination:      {auto_pag} run(s) auto, {prompted_pag} run(s) prompted")

        # OP-4 auto-chunking
        op4 = self.filter_by_test_id('OP-4')
        if op4:
            print(f"\nOP-4 (auto-chunking test):")
            for r in op4:
                notes_preview = r.get('notes', '')[:60]
                if len(r.get('notes', '')) > 60:
                    notes_preview += '...'
                print(f"  [{r.get('track','?')}] {notes_preview}")

        print("\nNext steps:")
        print("  1. Complete baseline tests (BL-1, BL-2, BL-3) on all three tracks")
        print("  2. Run SC-1 through SC-4 for structure-aware truncation analysis")
        print("  3. Run OP-1 and OP-4 to probe auto-pagination behavior")
        print("  4. Compare implicit vs explicit on BL-3 and OP-4 to evaluate @web effect on ceiling")
        print("  5. Review edge cases (EC-1, EC-3, EC-6)")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Cascade Web Search Testing Results Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_search_results_analyzer.py --csv results/cascade-interpreted/results.csv --summary
  python web_search_results_analyzer.py --csv results/raw/results.csv --full
  python web_search_results_analyzer.py \\
      --csv results/cascade-interpreted/results.csv results/explicit/results.csv --full
  python web_search_results_analyzer.py \\
      --csv results/cascade-interpreted/results.csv \\
             results/raw/results.csv \\
             results/explicit/results.csv --full
        """,
    )

    parser.add_argument(
        '--csv',
        type=str,
        nargs='+',
        required=True,
        help='One to three paths to results CSV files (interpreted, raw, explicit)',
    )
    parser.add_argument('--summary', action='store_true', help='Print summary report')
    parser.add_argument('--full', action='store_true', help='Run all analyses')
    parser.add_argument('--method', type=str, help='Filter by method string')
    parser.add_argument('--track', type=str,
                        choices=['interpreted', 'raw', 'explicit'],
                        help='Filter output to a single track')

    args = parser.parse_args()

    if len(args.csv) > 3:
        parser.error("--csv accepts at most three files: interpreted, raw, and explicit")

    analyzer = CascadeResultsAnalyzer(args.csv)

    if args.full:
        print("\n" + "=" * 80)
        print("FULL ANALYSIS REPORT")
        print("=" * 80)
        analyzer.generate_summary_report()
        analyzer.analyze_truncation_threshold()
        analyzer.analyze_implicit_vs_explicit()
        analyzer.analyze_by_track()
        analyzer.analyze_approval_behavior()
        analyzer.analyze_pagination_behavior()
        analyzer.analyze_elision_markers()
        analyzer.identify_hypothesis()

    elif args.summary:
        print("\n" + "=" * 80)
        print("SUMMARY REPORT")
        print("=" * 80)
        analyzer.generate_summary_report()

    elif args.method:
        method_results = analyzer.filter_by_method(args.method)
        print(f"\nResults for method '{args.method}':\n")
        for r in method_results:
            print(f"  {r['test_id']} [{r.get('track','?')}]: "
                  f"{r['output_chars']:,} chars  truncated: {r.get('truncated','?')}")
        print()

    elif args.track:
        track_results = analyzer.filter_by_track(args.track)
        print(f"\nResults for track '{args.track}':\n")
        for r in track_results:
            print(f"  {r['test_id']}: {r['output_chars']:,} chars  "
                  f"truncated: {r.get('truncated','?')}  "
                  f"approval: {r.get('approval_required','?')}")
        print()

    else:
        analyzer.analyze_truncation_threshold()
        analyzer.analyze_implicit_vs_explicit()
        analyzer.identify_hypothesis()


if __name__ == "__main__":
    main()