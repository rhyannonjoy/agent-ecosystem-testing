#!/usr/bin/env python3
"""
Codex Web Search Testing Results Analyzer
- Analyzes CSV results, identifies truncation patterns, and generates summary report
- Compares T1/T2 (interpreted) and T3/T4 (raw) track measurements
- Isolates surface effect: Codex IDE vs VS Code-Codex extension
- Isolates workspace effect: workspace-present vs isolated
- Matches findings to hypotheses H1-H5

Four tracks:
  t1_codex_interpreted   GPT-interpreted, Codex IDE (no workspace)
  t2_vscode_interpreted  GPT-interpreted, VS Code-Codex (workspace present)
  t3_codex_raw           Raw verbatim output, Codex IDE
  t4_vscode_raw          Raw verbatim output, VS Code-Codex

Cross-track comparisons of interest:
  T1 vs T2: Does workspace context change self-reported measurements or tool selection?
  T3 vs T4: Does surface context change the actual retrieval ceiling or tool chain?
  T1 vs T3: Does Codex perceive its own truncation accurately? (perception gap)
  T2 vs T4: Same accuracy question with workspace as a confound
  All tracks vs Cascade: Cross-platform comparison on identical URLs

Usage:
    # From project directory

    # Single track
    python codex_web_search_results_analyzer.py --csv results/codex-t1_codex_interpreted/results.csv --summary
    python codex_web_search_results_analyzer.py --csv results/codex-t3_codex_raw/results.csv --full

    # Cross-track comparison (two to four CSVs)
    python codex_web_search_results_analyzer.py \\
        --csv results/codex-t1_codex_interpreted/results.csv \\
               results/codex-t2_vscode_interpreted/results.csv --full

    python codex_web_search_results_analyzer.py \\
        --csv results/codex-t1_codex_interpreted/results.csv \\
               results/codex-t2_vscode_interpreted/results.csv \\
               results/codex-t3_codex_raw/results.csv \\
               results/codex-t4_vscode_raw/results.csv --full
"""

import csv
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import argparse

# Track metadata for display and inference
TRACK_META = {
    "t1_codex_interpreted": {
        "label": "T1 — GPT-interpreted, Codex IDE",
        "surface": "codex",
        "method": "gpt-interpreted",
        "workspace": False,
    },
    "t2_vscode_interpreted": {
        "label": "T2 — GPT-interpreted, VS Code-Codex",
        "surface": "vscode_codex",
        "method": "gpt-interpreted",
        "workspace": True,
    },
    "t3_codex_raw": {
        "label": "T3 — Raw, Codex IDE",
        "surface": "codex",
        "method": "raw",
        "workspace": False,
    },
    "t4_vscode_raw": {
        "label": "T4 — Raw, VS Code-Codex",
        "surface": "vscode_codex",
        "method": "raw",
        "workspace": True,
    },
}

# Pairing definitions for the four primary cross-track comparisons
COMPARISONS = [
    ("t1_codex_interpreted", "t2_vscode_interpreted",
     "T1 vs T2 — workspace effect on interpreted output"),
    ("t3_codex_raw", "t4_vscode_raw",
     "T3 vs T4 — workspace effect on raw retrieval ceiling"),
    ("t1_codex_interpreted", "t3_codex_raw",
     "T1 vs T3 — Codex IDE perception gap (interpreted vs raw)"),
    ("t2_vscode_interpreted", "t4_vscode_raw",
     "T2 vs T4 — VS Code-Codex perception gap (interpreted vs raw)"),
]


class CodexResultsAnalyzer:
    """Analyze Codex web search testing results across four tracks."""

    def __init__(self, csv_paths):
        if isinstance(csv_paths, (str, Path)):
            csv_paths = [csv_paths]

        self.csv_paths = [Path(p) for p in csv_paths]
        for p in self.csv_paths:
            if not p.exists():
                raise FileNotFoundError(f"CSV file not found: {p}")

        self.results = []
        self._load_csv()

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_optional_int(value):
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
        if value is None:
            return None
        if isinstance(value, float):
            return value
        value = str(value).strip()
        if value == "":
            return None
        return float(value)

    def _infer_track(self, csv_path: Path) -> str:
        """Infer track ID from CSV path when the field is absent or empty."""
        path_str = str(csv_path).lower()
        for track_id in TRACK_META:
            if track_id in path_str:
                return track_id
        # Fallback: surface + method heuristics
        if "t1" in path_str:
            return "t1_codex_interpreted"
        if "t2" in path_str:
            return "t2_vscode_interpreted"
        if "t3" in path_str:
            return "t3_codex_raw"
        if "t4" in path_str:
            return "t4_vscode_raw"
        return "unknown"

    def _normalize_row(self, row: dict, inferred_track: str) -> dict:
        """Normalize a CSV row into shared analysis fields across all four tracks."""
        normalized = dict(row)

        # Track — prefer field value, fall back to inferred
        track = normalized.get("track", "").strip() or inferred_track
        normalized["track"] = track

        # Surface and workspace — derive from track if not stored
        meta = TRACK_META.get(track, {})
        normalized.setdefault("surface", meta.get("surface", "unknown"))
        normalized["workspace_present"] = (
            str(normalized.get("workspace_present", "")).strip().lower()
            in ("true", "yes", "1")
            if normalized.get("workspace_present", "") != ""
            else meta.get("workspace", False)
        )

        normalized["input_est_chars"] = self._parse_optional_int(row.get("input_est_chars")) or 0

        # Core output fields — resolve from track-appropriate sources
        is_raw = track in ("t3_codex_raw", "t4_vscode_raw")

        if is_raw:
            normalized["output_chars"] = (
                self._parse_optional_int(row.get("output_chars"))
                or self._parse_optional_int(row.get("verified_file_size_bytes"))
                or self._parse_optional_int(row.get("agent_reported_output_chars"))
                or self._parse_optional_int(row.get("agent_reported_file_size_bytes"))
                or 0
            )
            normalized["tokens_est"] = (
                self._parse_optional_int(row.get("tokens_est"))
                or self._parse_optional_int(row.get("verified_tokens"))
                or self._parse_optional_int(row.get("agent_reported_tokens_est"))
                or 0
            )
            normalized["truncation_char_num"] = (
                self._parse_optional_int(row.get("truncation_char_num"))
                or self._parse_optional_int(row.get("agent_reported_truncation_point"))
            )
            if not normalized.get("truncated"):
                normalized["truncated"] = row.get("agent_reported_truncated", "")
        else:
            # Interpreted tracks: all data is agent-reported by definition
            normalized["output_chars"] = self._parse_optional_int(row.get("output_chars")) or 0
            normalized["tokens_est"] = self._parse_optional_int(row.get("tokens_est")) or 0
            normalized["truncation_char_num"] = self._parse_optional_int(row.get("truncation_char_num"))

        # Codex-specific behavioral fields
        normalized["tools_named"] = row.get("tools_named", "").strip() or "unknown"
        normalized["workspace_substitution"] = row.get("workspace_substitution", "").strip() or "unknown"

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

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    try:
                        normalized = self._normalize_row(row, inferred_track)
                        self.results.append(normalized)
                        test_ids.append(normalized.get("test_id", "UNKNOWN"))
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
            track_label = TRACK_META.get(inferred_track, {}).get("label", inferred_track)
            print(f"Loaded {loaded} results from {csv_path.name} (track: {track_label})")
            if skipped:
                print(f"⚠️  Skipped {skipped} rows due to errors")
            print(f"Test IDs: {', '.join(test_ids)}\n")

        if len(self.csv_paths) > 1:
            print(f"Merged {total_loaded} total results from {len(self.csv_paths)} CSV files")
            if total_skipped:
                print(f"⚠️  Skipped {total_skipped} total rows")
            print()

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    def filter_by_track(self, track: str):
        return [r for r in self.results if r.get("track") == track]

    def filter_by_surface(self, surface: str):
        return [r for r in self.results if r.get("surface") == surface]

    def filter_by_method(self, method: str):
        return [r for r in self.results if r.get("method") == method]

    def filter_by_test_id(self, test_id: str):
        return [r for r in self.results if r["test_id"] == test_id]

    def filter_by_workspace(self, present: bool):
        return [r for r in self.results if r.get("workspace_present") == present]

    # ------------------------------------------------------------------
    # Analyses
    # ------------------------------------------------------------------

    def analyze_truncation_threshold(self):
        """Identify truncation threshold patterns across all results."""
        print("=" * 80)
        print("TRUNCATION THRESHOLD ANALYSIS")
        print("=" * 80 + "\n")

        truncated = [r for r in self.results if r.get("truncated") == "yes"]
        not_truncated = [r for r in self.results if r.get("truncated") == "no"]

        if not truncated:
            print("No truncation detected in any tests.\n")
            return

        truncation_points = [
            r["truncation_char_num"] for r in truncated if r.get("truncation_char_num")
        ]

        if truncation_points:
            print("Truncation Points:")
            print(f"  Average: {mean(truncation_points):,.0f} characters")
            if len(truncation_points) > 1:
                print(f"  Stdev:   {stdev(truncation_points):,.0f}")
            print(f"  Min:     {min(truncation_points):,.0f}")
            print(f"  Max:     {max(truncation_points):,.0f}\n")

        output_sizes = [r["output_chars"] for r in self.results if r.get("output_chars")]
        if output_sizes:
            print(f"Output size range (all runs): {min(output_sizes):,} – {max(output_sizes):,} chars")

        print("\nInput sizes where truncation occurred:")
        for r in sorted(truncated, key=lambda x: x["input_est_chars"]):
            track_label = TRACK_META.get(r.get("track", ""), {}).get("label", r.get("track", "?"))
            print(f"  {r['test_id']} [{track_label}]: "
                  f"{r['input_est_chars']:,} chars in → {r['output_chars']:,} chars out")

        print("\nInput sizes where NO truncation occurred:")
        for r in sorted(not_truncated, key=lambda x: x["input_est_chars"]):
            track_label = TRACK_META.get(r.get("track", ""), {}).get("label", r.get("track", "?"))
            print(f"  {r['test_id']} [{track_label}]: "
                  f"{r['input_est_chars']:,} chars in → {r['output_chars']:,} chars out (full)")
        print()

    def analyze_surface_effect(self):
        """
        Compare Codex IDE vs VS Code-Codex extension results.
        Primary Codex-specific analysis — isolates deployment surface as a variable.
        Pairs T1 vs T2 (interpreted) and T3 vs T4 (raw) separately to avoid
        conflating the surface effect with the interpreted-vs-raw measurement gap.
        """
        print("=" * 80)
        print("SURFACE EFFECT ANALYSIS (Codex IDE vs VS Code-Codex)")
        print("=" * 80 + "\n")

        # Interpreted pair: T1 vs T2
        self._compare_track_pair(
            "t1_codex_interpreted",
            "t2_vscode_interpreted",
            "Interpreted tracks — T1 (Codex IDE) vs T2 (VS Code-Codex)",
            "surface-interpreted",
        )

        # Raw pair: T3 vs T4
        self._compare_track_pair(
            "t3_codex_raw",
            "t4_vscode_raw",
            "Raw tracks — T3 (Codex IDE) vs T4 (VS Code-Codex)",
            "surface-raw",
        )

    def analyze_perception_gap(self):
        """
        Compare interpreted vs raw tracks within each surface.
        Answers whether the GPT agent accurately perceives its own truncation.
        Pairs T1 vs T3 (Codex IDE) and T2 vs T4 (VS Code-Codex) separately.
        This is the Codex analog of the Cascade interpreted/raw divergence check.
        """
        print("=" * 80)
        print("PERCEPTION GAP ANALYSIS (interpreted vs raw, per surface)")
        print("=" * 80 + "\n")

        # Codex IDE: T1 vs T3
        self._compare_track_pair(
            "t1_codex_interpreted",
            "t3_codex_raw",
            "Codex IDE — T1 (interpreted) vs T3 (raw)",
            "perception-codex",
        )

        # VS Code-Codex: T2 vs T4
        self._compare_track_pair(
            "t2_vscode_interpreted",
            "t4_vscode_raw",
            "VS Code-Codex — T2 (interpreted) vs T4 (raw)",
            "perception-vscode",
        )

    def _compare_track_pair(self, track_a: str, track_b: str, label: str, context: str):
        """
        Core paired comparison helper used by surface effect and perception gap analyses.
        Logs per-test-ID output delta, truncation divergence, and tool chain differences.
        """
        results_a = self.filter_by_track(track_a)
        results_b = self.filter_by_track(track_b)

        label_a = TRACK_META.get(track_a, {}).get("label", track_a)
        label_b = TRACK_META.get(track_b, {}).get("label", track_b)

        print(f"--- {label} ---\n")

        if not results_a or not results_b:
            missing = []
            if not results_a:
                missing.append(label_a)
            if not results_b:
                missing.append(label_b)
            print(f"  Insufficient data — missing results for: {', '.join(missing)}\n")
            return

        by_id_a = {r["test_id"]: r for r in results_a}
        by_id_b = {r["test_id"]: r for r in results_b}
        shared_ids = sorted(set(by_id_a) & set(by_id_b))

        if not shared_ids:
            print("  No test IDs present in both tracks for comparison.\n")
            return

        divergences = []
        tool_divergences = []

        for test_id in shared_ids:
            a = by_id_a[test_id]
            b = by_id_b[test_id]

            output_delta = b["output_chars"] - a["output_chars"]
            truncation_divergence = a.get("truncated") != b.get("truncated")

            print(f"  {test_id}:")
            print(f"    {label_a}: {a['output_chars']:,} chars  truncated: {a.get('truncated', '?')}")
            print(f"    {label_b}: {b['output_chars']:,} chars  truncated: {b.get('truncated', '?')}")
            print(f"    Output delta: {output_delta:+,} chars")

            if truncation_divergence:
                print(f"    ⚠️  TRUNCATION DIVERGENCE — tracks disagree")
                divergences.append(test_id)

            # Tool chain comparison
            tools_a = a.get("tools_named", "") or a.get("tools_used", "")
            tools_b = b.get("tools_named", "") or b.get("tools_used", "")
            if tools_a or tools_b:
                if tools_a != tools_b:
                    print(f"    Tool chain differs:")
                    print(f"      {label_a}: {tools_a or 'not recorded'}")
                    print(f"      {label_b}: {tools_b or 'not recorded'}")
                    tool_divergences.append(test_id)
                else:
                    print(f"    Tool chain identical: {tools_a}")

            # Workspace substitution flag (relevant for T2/T4)
            ws_sub_a = a.get("workspace_substitution", "unknown")
            ws_sub_b = b.get("workspace_substitution", "unknown")
            if ws_sub_a == "yes" or ws_sub_b == "yes":
                print(f"    ⚠️  WORKSPACE SUBSTITUTION — agent used local execution instead of web fetch")

            print()

        # Summary for this pair
        if divergences:
            print(f"  ⚠️  Truncation divergences on: {', '.join(divergences)}")
        else:
            print(f"  ✓ No truncation divergences across shared test IDs")

        if tool_divergences:
            print(f"  ⚠️  Tool chain divergences on: {', '.join(tool_divergences)}")
        else:
            print(f"  ✓ No tool chain divergences")

        print()

    def analyze_by_track(self):
        """Print a side-by-side view of all four tracks for each test ID."""
        print("=" * 80)
        print("FOUR-TRACK COMPARISON (T1 / T2 / T3 / T4)")
        print("=" * 80 + "\n")

        tests_by_id = defaultdict(list)
        for r in self.results:
            tests_by_id[r["test_id"]].append(r)

        for test_id in sorted(tests_by_id):
            results = tests_by_id[test_id]
            by_track = {r.get("track"): r for r in results}

            if len(by_track) < 2:
                continue

            print(f"{test_id}:")
            for track in ("t1_codex_interpreted", "t2_vscode_interpreted",
                          "t3_codex_raw", "t4_vscode_raw"):
                if track in by_track:
                    r = by_track[track]
                    short_label = track.replace("_codex_interpreted", " interp")  \
                                       .replace("_vscode_interpreted", " interp") \
                                       .replace("_codex_raw", " raw")             \
                                       .replace("_vscode_raw", " raw")
                    ws_sub = r.get("workspace_substitution", "?")
                    print(f"  {track:<28}: {r['output_chars']:>8,} chars  "
                          f"truncated: {r.get('truncated', '?'):<3}  "
                          f"tools: {r.get('tools_named', '?'):<20}  "
                          f"ws_sub: {ws_sub}")

            # Flag perception gaps (interpreted vs raw per surface)
            if "t1_codex_interpreted" in by_track and "t3_codex_raw" in by_track:
                if by_track["t1_codex_interpreted"].get("truncated") != by_track["t3_codex_raw"].get("truncated"):
                    print(f"  ⚠️  Perception gap — Codex IDE (T1 vs T3 truncation mismatch)")

            if "t2_vscode_interpreted" in by_track and "t4_vscode_raw" in by_track:
                if by_track["t2_vscode_interpreted"].get("truncated") != by_track["t4_vscode_raw"].get("truncated"):
                    print(f"  ⚠️  Perception gap — VS Code-Codex (T2 vs T4 truncation mismatch)")

            # Flag surface divergences (same method, different surface)
            if "t1_codex_interpreted" in by_track and "t2_vscode_interpreted" in by_track:
                if by_track["t1_codex_interpreted"].get("truncated") != by_track["t2_vscode_interpreted"].get("truncated"):
                    print(f"  ⚠️  Surface divergence — interpreted tracks (T1 vs T2 truncation mismatch)")

            if "t3_codex_raw" in by_track and "t4_vscode_raw" in by_track:
                if by_track["t3_codex_raw"].get("truncated") != by_track["t4_vscode_raw"].get("truncated"):
                    print(f"  ⚠️  Surface divergence — raw tracks (T3 vs T4 truncation mismatch)")

            print()

    def analyze_workspace_substitution(self):
        """
        Analyze whether agents substitute local script execution for web fetch.
        Codex-specific: VS Code-Codex has a local workspace, creating a risk that
        the agent uses local tools (curl, Python scripts) instead of web retrieval.
        This would contaminate T2/T4 results and make surface comparison invalid.
        """
        print("=" * 80)
        print("WORKSPACE SUBSTITUTION ANALYSIS")
        print("=" * 80 + "\n")

        substitution_counts = defaultdict(int)
        for r in self.results:
            substitution_counts[r.get("workspace_substitution", "unknown")] += 1

        print("Workspace substitution across all runs:")
        for value, count in sorted(substitution_counts.items(), key=lambda x: -x[1]):
            label = {
                "yes": "Substituted (local execution instead of web fetch)",
                "no": "No substitution (web fetch used as intended)",
                "unknown": "Not recorded",
            }.get(value, value)
            print(f"  {value} ({label}): {count} runs")

        # Break down by track — substitution should only be possible on T2/T4
        print("\nWorkspace substitution by track:")
        for track in ("t1_codex_interpreted", "t2_vscode_interpreted",
                      "t3_codex_raw", "t4_vscode_raw"):
            track_results = self.filter_by_track(track)
            if not track_results:
                continue
            counts = defaultdict(int)
            for r in track_results:
                counts[r.get("workspace_substitution", "unknown")] += 1
            counts_str = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
            label = TRACK_META.get(track, {}).get("label", track)
            print(f"  {label}: {counts_str}")

        # Flag T1/T3 substitution — should be impossible without a workspace
        isolation_tracks = self.filter_by_track("t1_codex_interpreted") + self.filter_by_track("t3_codex_raw")
        unexpected = [r for r in isolation_tracks if r.get("workspace_substitution") == "yes"]
        if unexpected:
            print(f"\n⚠️  Unexpected substitution on T1/T3 (no workspace expected): "
                  f"{[r['test_id'] for r in unexpected]}")
            print(f"   → Isolation assumption violated; T1/T3 results may be contaminated")
        else:
            print(f"\n✓ No substitution on T1/T3 — workspace isolation holding")

        workspace_tracks = self.filter_by_track("t2_vscode_interpreted") + self.filter_by_track("t4_vscode_raw")
        substituted = [r for r in workspace_tracks if r.get("workspace_substitution") == "yes"]
        if substituted:
            print(f"⚠️  Substitution confirmed on T2/T4: {[r['test_id'] for r in substituted]}")
            print(f"   → These runs should be excluded from surface effect comparison (T1 vs T2, T3 vs T4)")
        else:
            print(f"✓ No substitution on T2/T4 — workspace context did not contaminate retrieval")

        print()

    def analyze_tool_visibility(self):
        """
        Analyze which tool names agents reported across tracks and surfaces.
        Codex named 'web' and 'web.open'; VS Code-Codex named 'web', 'web.open', 'curl'.
        This analysis tracks whether tool naming is consistent within and across surfaces,
        and whether any tool names correlate with different retrieval behavior.
        """
        print("=" * 80)
        print("TOOL VISIBILITY ANALYSIS")
        print("=" * 80 + "\n")

        print("Tools named by track:\n")
        for track in ("t1_codex_interpreted", "t2_vscode_interpreted",
                      "t3_codex_raw", "t4_vscode_raw"):
            track_results = self.filter_by_track(track)
            if not track_results:
                continue

            tool_counts = defaultdict(int)
            for r in track_results:
                tools = r.get("tools_named", "unknown") or "unknown"
                for tool in [t.strip() for t in tools.split(",")]:
                    tool_counts[tool] += 1

            label = TRACK_META.get(track, {}).get("label", track)
            print(f"  {label}:")
            for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
                print(f"    {tool}: {count} run(s)")
            print()

        # Flag tool name differences across same-method tracks (surface effect on toolchain)
        t1_tools = {r.get("tools_named", "") for r in self.filter_by_track("t1_codex_interpreted")}
        t2_tools = {r.get("tools_named", "") for r in self.filter_by_track("t2_vscode_interpreted")}
        if t1_tools and t2_tools and t1_tools != t2_tools:
            print(f"⚠️  Tool names differ between T1 and T2 — surface may change toolchain")
            print(f"   T1 (Codex IDE):       {t1_tools}")
            print(f"   T2 (VS Code-Codex):   {t2_tools}")
        elif t1_tools and t2_tools:
            print(f"✓ Tool names consistent between T1 and T2 — surface does not change toolchain")

        t3_tools = {r.get("tools_used", "") for r in self.filter_by_track("t3_codex_raw")}
        t4_tools = {r.get("tools_used", "") for r in self.filter_by_track("t4_vscode_raw")}
        if t3_tools and t4_tools and t3_tools != t4_tools:
            print(f"⚠️  Tool chains differ between T3 and T4 — surface may change raw retrieval toolchain")
            print(f"   T3 (Codex IDE):       {t3_tools}")
            print(f"   T4 (VS Code-Codex):   {t4_tools}")
        elif t3_tools and t4_tools:
            print(f"✓ Tool chains consistent between T3 and T4")

        print()

    def analyze_elision_markers(self):
        """
        Analyze ellipsis elision markers in raw track output.
        In Copilot testing, '...' markers indicated fetch_webpage excerpt assembly
        rather than byte-boundary truncation. The same pattern may appear in Codex's
        web / web.open toolchain and is worth surfacing early.
        """
        print("=" * 80)
        print("ELISION MARKER ANALYSIS (...)")
        print("=" * 80 + "\n")

        raw_results = (
            self.filter_by_track("t3_codex_raw") + self.filter_by_track("t4_vscode_raw")
        )
        if not raw_results:
            print("No raw track results available.\n")
            return

        print("Elision marker presence in raw track notes:")
        elision_found = []
        for r in raw_results:
            notes = r.get("notes", "").lower()
            if "..." in notes or "elision" in notes or "excerpt" in notes:
                elision_found.append(r)
                label = TRACK_META.get(r.get("track", ""), {}).get("label", r.get("track", "?"))
                print(f"  {r['test_id']} [{label}]: {r.get('notes', '')[:80]}...")

        if elision_found:
            print(f"\n⚠️  Elision markers found in {len(elision_found)} raw run(s)")
            print(f"   → web / web.open may be performing excerpt assembly, not full retrieval")
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
        print("  H4: Surface context (Codex IDE vs VS Code-Codex) changes retrieval ceiling")
        print("  H5: Agent auto-chunks above the truncation ceiling\n")

        hypothesis_counts = defaultdict(int)
        for r in self.results:
            if r.get("hypothesis_match"):
                hypothesis_counts[r["hypothesis_match"]] += 1

        print("Hypothesis matches logged in results:")
        for hyp, count in sorted(hypothesis_counts.items(), key=lambda x: -x[1]):
            print(f"  {hyp}: {count} run(s)")

        # Chars-per-token ratio from raw tracks — distinguishes H1 vs H2
        raw_results = (
            self.filter_by_track("t3_codex_raw") + self.filter_by_track("t4_vscode_raw")
        )
        ratios = [
            r["output_chars"] / r["tokens_est"]
            for r in raw_results
            if r.get("tokens_est", 0) > 0
        ]
        if ratios:
            avg_ratio = mean(ratios)
            print(f"\nCharacter-to-token ratio (raw tracks T3/T4):")
            print(f"  Average: {avg_ratio:.2f} chars/token")
            if 3.5 <= avg_ratio <= 4.5:
                print(f"  → Consistent with TOKEN-BASED truncation (H2)")
            else:
                print(f"  → Consistent with CHARACTER-BASED truncation (H1)")

        # H4: surface effect on output size
        codex_results = self.filter_by_surface("codex")
        vscode_results = self.filter_by_surface("vscode_codex")
        if codex_results and vscode_results:
            codex_avg = mean(r["output_chars"] for r in codex_results if r["output_chars"])
            vscode_avg = mean(r["output_chars"] for r in vscode_results if r["output_chars"])
            delta = vscode_avg - codex_avg
            print(f"\nSurface effect on output size (H4):")
            print(f"  Codex IDE avg:      {codex_avg:,.0f} chars")
            print(f"  VS Code-Codex avg:  {vscode_avg:,.0f} chars")
            print(f"  Delta:              {delta:+,.0f} chars")
            if abs(delta) < 500:
                print(f"  → Surface has negligible effect on output size — H4 not supported")
            else:
                print(f"  → Surface produces meaningful output difference — H4 supported")

        # H5: auto-chunking — check raw tracks for multi-step tool chains
        raw_with_chains = [
            r for r in raw_results
            if "->" in (r.get("tools_used") or "")
        ]
        print(f"\nAuto-chunking evidence (H5):")
        if raw_with_chains:
            print(f"  ✓ Multi-step tool chains observed on {len(raw_with_chains)} raw run(s) — H5 supported")
            for r in raw_with_chains:
                label = TRACK_META.get(r.get("track", ""), {}).get("label", r.get("track", "?"))
                print(f"    {r['test_id']} [{label}]: {r.get('tools_used', '')}")
        else:
            print(f"  — No multi-step tool chains observed yet")

        print()

    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        print(f"\nTotal runs analyzed: {len(self.results)}")
        paths_str = ", ".join(str(p) for p in self.csv_paths)
        print(f"Sources: {paths_str}\n")

        tracks_present = defaultdict(int)
        for r in self.results:
            tracks_present[r.get("track", "unknown")] += 1
        print("Runs by track:")
        for track in ("t1_codex_interpreted", "t2_vscode_interpreted",
                      "t3_codex_raw", "t4_vscode_raw", "unknown"):
            if track in tracks_present:
                label = TRACK_META.get(track, {}).get("label", track)
                print(f"  {label}: {tracks_present[track]}")

        truncated = [r for r in self.results if r.get("truncated") == "yes"]
        print(f"\nTruncation events: {len(truncated)} / {len(self.results)}")

        output_chars = [r["output_chars"] for r in self.results if r.get("output_chars")]
        if output_chars:
            print(f"Average output size: {mean(output_chars):,.0f} chars")
            print(f"Output size range:   {min(output_chars):,} – {max(output_chars):,} chars")

        tokens = [r["tokens_est"] for r in self.results if r.get("tokens_est")]
        if tokens:
            print(f"Average token count: {mean(tokens):,.0f} tokens")
            print(f"Token count range:   {min(tokens):,} – {max(tokens):,} tokens")

        # Workspace substitution summary
        ws_sub_yes = sum(1 for r in self.results if r.get("workspace_substitution") == "yes")
        print(f"\nWorkspace substitution: {ws_sub_yes} / {len(self.results)} runs")

        # Surface comparison summary
        codex_results = self.filter_by_surface("codex")
        vscode_results = self.filter_by_surface("vscode_codex")
        if codex_results and vscode_results:
            codex_trunc = sum(1 for r in codex_results if r.get("truncated") == "yes")
            vscode_trunc = sum(1 for r in vscode_results if r.get("truncated") == "yes")
            print(f"\nTruncation by surface:")
            print(f"  Codex IDE ({len(codex_results)} runs):      {codex_trunc} truncated")
            print(f"  VS Code-Codex ({len(vscode_results)} runs): {vscode_trunc} truncated")

        # OP-1 fragment navigation result
        op1_results = self.filter_by_test_id("OP-1")
        if op1_results:
            print(f"\nOP-1 (fragment navigation): {len(op1_results)} run(s) logged")

        # OP-4 CommonMark spec / auto-chunking result
        op4_results = self.filter_by_test_id("OP-4")
        if op4_results:
            raw_op4 = [r for r in op4_results if r.get("track") in ("t3_codex_raw", "t4_vscode_raw")]
            multi_step = [r for r in raw_op4 if "->" in (r.get("tools_used") or "")]
            print(f"OP-4 (CommonMark spec ~500KB, auto-chunking): {len(op4_results)} run(s) logged")
            if multi_step:
                print(f"  ✓ Multi-step tool chain observed on {len(multi_step)} raw run(s) — auto-chunking confirmed")
            else:
                print(f"  — No multi-step tool chain observed yet on OP-4")


# ======================================================================
# CLI
# ======================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Codex Web Search Testing Results Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Track reference:
  t1_codex_interpreted   GPT-interpreted, Codex IDE (no workspace)
  t2_vscode_interpreted  GPT-interpreted, VS Code-Codex (workspace present)
  t3_codex_raw           Raw verbatim output, Codex IDE
  t4_vscode_raw          Raw verbatim output, VS Code-Codex

Examples:
  python codex_web_search_results_analyzer.py \\
      --csv results/codex-t1_codex_interpreted/results.csv --summary

  python codex_web_search_results_analyzer.py \\
      --csv results/codex-t3_codex_raw/results.csv --full

  python codex_web_search_results_analyzer.py \\
      --csv results/codex-t1_codex_interpreted/results.csv \\
             results/codex-t2_vscode_interpreted/results.csv --full

  python codex_web_search_results_analyzer.py \\
      --csv results/codex-t1_codex_interpreted/results.csv \\
             results/codex-t2_vscode_interpreted/results.csv \\
             results/codex-t3_codex_raw/results.csv \\
             results/codex-t4_vscode_raw/results.csv --full
        """,
    )

    parser.add_argument(
        "--csv",
        type=str,
        nargs="+",
        required=True,
        help="One to four paths to results CSV files (one per track)",
    )
    parser.add_argument("--summary", action="store_true", help="Print summary report")
    parser.add_argument("--full", action="store_true", help="Run all analyses")
    parser.add_argument("--method", type=str, help="Filter output by method string")
    parser.add_argument(
        "--track",
        type=str,
        choices=list(TRACK_META.keys()),
        help="Filter output to a single track",
    )

    args = parser.parse_args()

    if len(args.csv) > 4:
        parser.error("--csv accepts at most four files, one per track")

    analyzer = CodexResultsAnalyzer(args.csv)

    if args.full:
        print("\n" + "=" * 80)
        print("FULL ANALYSIS REPORT")
        print("=" * 80)
        analyzer.generate_summary_report()
        analyzer.analyze_truncation_threshold()
        analyzer.analyze_surface_effect()
        analyzer.analyze_perception_gap()
        analyzer.analyze_by_track()
        analyzer.analyze_workspace_substitution()
        analyzer.analyze_tool_visibility()
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
            label = TRACK_META.get(r.get("track", ""), {}).get("label", r.get("track", "?"))
            print(f"  {r['test_id']} [{label}]: "
                  f"{r['output_chars']:,} chars  truncated: {r.get('truncated', '?')}")
        print()

    elif args.track:
        track_results = analyzer.filter_by_track(args.track)
        label = TRACK_META.get(args.track, {}).get("label", args.track)
        print(f"\nResults for {label}:\n")
        for r in track_results:
            print(f"  {r['test_id']}: {r['output_chars']:,} chars  "
                  f"truncated: {r.get('truncated', '?')}  "
                  f"tools: {r.get('tools_named', '?')}  "
                  f"ws_sub: {r.get('workspace_substitution', '?')}")
        print()

    else:
        analyzer.analyze_truncation_threshold()
        analyzer.analyze_surface_effect()
        analyzer.identify_hypothesis()


if __name__ == "__main__":
    main()