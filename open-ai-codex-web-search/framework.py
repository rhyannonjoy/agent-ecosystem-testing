"""
Codex Web Search Testing Framework
Generates standardized test prompts and logs results to CSV

This framework extends the Cascade testing framework (three tracks) to a four-track
design that isolates deployment surface as an additional variable. Where Cascade isolated
the @web directive, Codex isolates the Codex IDE versus VS Code-Codex extension surface.

Key design decisions:
1. URLs are the same proven test cases used across Claude API, Gemini, Copilot, Cursor,
   and Cascade testing suites, enabling direct cross-platform comparison
2. Baseline tests, BL - use the same MongoDB docs pages as Claude API testing
3. Structured content tests, SC - use API docs and reference materials
4. Offset/pagination tests, OP - test chunking, fragment navigation, and auto-pagination
5. Edge case tests, EC - target specific truncation/rendering challenges
6. Four-track measurement:
   - codex-interpreted:    GPT-interpreted, Codex IDE (no local workspace)
   - vscode-codex-interpreted:   GPT-interpreted, VS Code-Codex extension (workspace present)
   - codex-raw:            Raw verbatim output, Codex IDE
   - vscode-codex-raw:           Raw verbatim output, VS Code-Codex extension

Track design rationale:
  T1 vs T2: Does workspace context change self-reported measurements or tool selection?
  T3 vs T4: Does surface context change the actual retrieval ceiling or tool chain?
  T1 vs T3: Does Codex perceive its own truncation accurately?
  T2 vs T4: Same accuracy question, with workspace as a confound.
  All tracks vs Cascade: Direct cross-platform comparison on identical URLs.

This allows direct comparison:
  "Codex-IDE truncates at X KB, VS Code-Codex at Y KB, Cascade at Z KB on same URL"

Usage:
    # From project directory
    python framework.py --list-tests
    python framework.py --test {test ID} --track codex-interpreted
    python framework.py --test {test ID} --track codex-raw
    python framework.py --test {test ID} --track vscode-codex-raw
"""

import csv
from datetime import datetime
from pathlib import Path
import argparse
from dataclasses import dataclass, asdict
from typing import Optional

# Test URLs - identical to Cascade suite for cross-platform comparability
# Organized by category, same IDs as Cascade framework
TEST_URLS = {
    # --- BASELINE TESTS, BL ---
    # Progressive scaling: small HTML → medium → large
    "BL-1": {
        "name": "Short HTML page (heavy CSS before content)",
        "url": "https://www.mongodb.com/docs/manual/reference/change-events/create/",
        "expected_size_kb": 85,
        "category": "baseline",
        "note": "Same as Claude API test 1; CSS problem test from Dachary Carey research",
    },
    "BL-2": {
        "name": "Short Markdown version (same page, mixed format, incomplete field values)",
        "url": "https://www.mongodb.com/docs/manual/reference/change-events/create.md",
        "expected_size_kb": 20,
        "category": "baseline",
        "note": "Same as Claude API test 2; HTML vs Markdown comparison baseline",
    },
    "BL-3": {
        "name": "Long HTML page (multi-section tabbed tutorial)",
        "url": "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/",
        "expected_size_kb": 250,
        "category": "baseline",
        "note": "Same as Claude API test 3; used to measure default truncation ceiling",
    },

    # --- STRUCTURED CONTENT TESTS, SC ---
    # Test how GPT handles different content structures during truncation
    "SC-1": {
        "name": "Markdown-heavy documentation",
        "url": "https://ai.google.dev/gemini-api/docs/url-context",
        "expected_size_kb": 40,
        "category": "structured_content",
        "note": "Google Gemini docs; consistent with Gemini test suite",
    },
    "SC-2": {
        "name": "API documentation with code blocks",
        "url": "https://docs.anthropic.com/en/api/messages",
        "expected_size_kb": 80,
        "category": "structured_content",
        "note": "Anthropic API docs; tests code block integrity across truncation",
    },
    "SC-3": {
        "name": "Table-heavy structured data",
        "url": "https://en.wikipedia.org/wiki/List_of_countries_by_population",
        "expected_size_kb": 100,
        "category": "structured_content",
        "note": "Wikipedia list page; tests table column/row preservation at truncation boundary",
    },
    "SC-4": {
        "name": "Nested headings and structured sections",
        "url": "https://www.markdownguide.org/basic-syntax/",
        "expected_size_kb": 30,
        "category": "structured_content",
        "note": "Markdown reference; tests hierarchy preservation in H1-H6 structure",
    },

    # --- OFFSET/PAGINATION TESTS, OP ---
    # Test chunking, fragment navigation, and auto-pagination
    "OP-1": {
        "name": "Fragment identifier navigation test",
        "url": "https://en.wikipedia.org/wiki/Machine_learning#History",
        "expected_size_kb": 40,
        "category": "offset_pagination",
        "note": "Tests if Codex jumps to specific section via URL fragment",
    },
    "OP-4": {
        "name": "Large document - agent auto-chunking test",
        "url": "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/",
        "expected_size_kb": 250,
        "category": "offset_pagination",
        "note": "Same as BL-3; tests if Codex auto-paginates after truncation",
    },

    # --- EDGE CASE TESTS, EC ---
    # Stress test unusual conditions and error handling
    "EC-1": {
        "name": "JavaScript-heavy single-page application",
        "url": "https://ai.google.dev/gemini-api/docs",
        "expected_size_kb": 100,
        "category": "edge_cases",
        "note": "Google Docs site with JS rendering; tests raw HTML vs rendered behavior",
    },
    "EC-3": {
        "name": "Redirect chain handling",
        "url": "https://httpbin.org/redirect/5",
        "expected_size_kb": 2,
        "category": "edge_cases",
        "note": "Tests how many redirects Codex follows before giving up or timeout",
    },
    "EC-6": {
        "name": "Very long single lines (no line breaks)",
        "url": "https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md",
        "expected_size_kb": 60,
        "category": "edge_cases",
        "note": "Markdown with potentially long lines; tests line-wrapping vs character-based truncation",
    },
}

# Track definitions
TRACKS = {
    "codex-interpreted": {
        "label": "T1 — GPT-interpreted, Codex IDE",
        "surface": "codex",
        "method": "gpt-interpreted",
        "workspace": False,
        "description": "Codex IDE in isolation; no local workspace; agent reports measurements",
    },
    "vscode-codex-interpreted": {
        "label": "T2 — GPT-interpreted, VS Code-Codex",
        "surface": "vscode_codex",
        "method": "gpt-interpreted",
        "workspace": True,
        "description": "VS Code-Codex extension with workspace present; agent reports measurements",
    },
    "codex-raw": {
        "label": "T3 — Raw, Codex IDE",
        "surface": "codex",
        "method": "raw",
        "workspace": False,
        "description": "Codex IDE in isolation; verbatim output returned; verification script measures",
    },
    "vscode-codex-raw": {
        "label": "T4 — Raw, VS Code-Codex",
        "surface": "vscode_codex",
        "method": "raw",
        "workspace": True,
        "description": "VS Code-Codex extension with workspace; verbatim output; verification script measures",
    },
}


@dataclass
class TestResult:
    """Standard test result structure for Codex testing.

    Field naming conventions:
    - No prefix: session metadata and analytical fields not sourced from either track
    - agent_reported_*: values self-reported by the GPT agent (T1/T2 tracks)
    - verified_*: values measured by the verification script against saved raw output (T3/T4 tracks)

    Track behavior:
    - T1/T2 (interpreted): populate unprefixed output fields (output_chars, truncated,
      truncation_char_num, tokens_est); all data is agent-reported by definition
    - T3/T4 (raw): populate both agent_reported_* and verified_* fields, enabling
      direct comparison between what the agent claimed and what the verifier measured

    Codex-specific fields vs Cascade framework:
    - surface: codex | vscode_codex (replaces implicit Cascade single-surface assumption)
    - workspace_present: boolean; key variable distinguishing T1/T3 from T2/T4
    - tools_named: tool identifiers reported by agent (web, web.open, curl vs Cascade's
      read_url_content, view_content_chunk, search_web)
    - workspace_substitution: did agent use local code execution instead of web fetch?
    - codex_version replaces windsurf_version
    - model_intelligence_level: logs GPT intelligence setting (e.g., low, medium, high)
    """

    # --- Session metadata (all tracks) ---
    test_id: str
    timestamp: str
    date: str
    url: str
    track: str                       # codex-interpreted | vscode-codex-interpreted | codex-raw | vscode-codex-raw
    surface: str                     # codex | vscode_codex
    method: str                      # gpt-interpreted | raw
    workspace_present: bool          # False for T1/T3, True for T2/T4
    permission_level: str             # default | auto-review | full-access
    model_observed: str              # LLM observed in output, if reported
    model_intelligence_level: str    # e.g., "low", "medium", "high", "auto"
    input_est_chars: int
    hypothesis_match: str
    codex_version: str
    notes: str

    # --- Codex-specific behavioral fields (all tracks) ---
    # tools_named: tool names reported in agent output (e.g. "web", "web.open", "curl")
    tools_named: Optional[str] = None
    # workspace_substitution: did the agent substitute local script execution for web fetch?
    # Values: yes | no | unknown
    workspace_substitution: Optional[str] = None

    # --- Interpreted track output fields (T1, T2) ---
    # (unprefixed: all data is agent-reported by definition on these tracks)
    output_chars: Optional[int] = None
    truncated: Optional[str] = None          # yes | no
    truncation_char_num: Optional[int] = None
    tokens_est: Optional[int] = None

    # --- Tool behavior fields (T3, T4 raw tracks) ---
    # tools_used: observed tool chain, e.g. "web -> web.open"
    # execution_attempts: total tool calls including fallbacks
    tools_used: Optional[str] = None
    tools_blocked: Optional[str] = None
    execution_attempts: Optional[int] = None

    # --- Agent self-reported fields (T3, T4 raw tracks) ---
    # Values reported by the agent in its output; may differ from verified measurements
    agent_reported_output_chars: Optional[int] = None
    agent_reported_truncated: Optional[str] = None
    agent_reported_truncation_point: Optional[int] = None
    agent_reported_tokens_est: Optional[int] = None
    agent_reported_file_size_bytes: Optional[int] = None
    agent_reported_md5_checksum: Optional[str] = None
    agent_reported_lines: Optional[int] = None
    agent_reported_words: Optional[int] = None
    agent_reported_code_blocks: Optional[int] = None
    agent_reported_table_rows: Optional[int] = None
    agent_reported_headers: Optional[int] = None

    # --- Verified fields (T3, T4 raw tracks) ---
    # Values measured by the verification script against the saved raw output file
    verified_file_size_bytes: Optional[int] = None
    verified_md5_checksum: Optional[str] = None
    verified_total_lines: Optional[int] = None
    verified_total_words: Optional[int] = None
    verified_tokens: Optional[int] = None
    verified_chars_per_token: Optional[float] = None
    verified_code_blocks: Optional[int] = None
    verified_table_rows: Optional[int] = None
    verified_headers: Optional[int] = None


class CodexTestingFramework:
    """Manage Codex web search testing across four tracks."""

    def __init__(self, results_dir: str = None, track: str = "codex-interpreted"):
        if track not in TRACKS:
            raise ValueError(
                f"Unknown track: {track}. Must be one of: {', '.join(TRACKS.keys())}"
            )

        self.track = track
        self.track_info = TRACKS[track]

        if results_dir is None:
            _dir_map = {
                "codex-interpreted": "results/codex-interpreted",
                "vscode-codex-interpreted": "results/vscode-codex-interpreted",
                "codex-raw":          "results/codex-raw",
                "vscode-codex-raw":         "results/vscode-codex-raw",
            }
            results_dir = _dir_map[track]

        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.results_dir / "results.csv"

    # ------------------------------------------------------------------
    # Prompt generators
    # ------------------------------------------------------------------

    def generate_interpreted_prompt(self, test_id: str, surface: str = "codex") -> str:
        """Generate a prompt for T1 or T2 interpreted tracks (agent reports measurements)."""
        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        contamination_warning = (
            "\nTo prevent testing methodology contamination, only run this test and don't proceed to any other tests.\n"
            if surface != "codex"
            else "\n"
        )

        prompt = f"""I'm testing Codex's web retrieval capabilities for the Agent Ecosystem Testing project.
{contamination_warning}Fetch this URL directly:
{url}

Then report back:
1. **Total character count** of the response you received
2. **Estimated token count**
3. **Whether any content appears truncated** (yes/no, and where if truncated)
4. **Last 50 characters** of the response (verbatim, to verify the cutoff point)
5. **Markdown formatting assessment** - is it complete? Are code blocks closed properly?
6. **Model's perceived completeness** - does it seem like you got the full content?
7. **Tool visibility** - report any tool names or method identifiers visible in your tool results,
   including whether web, web.open, curl, or any other tool was invoked
8. **Surface awareness** - do you have access to a local workspace or filesystem?

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB
This is for empirical documentation of retrieval behavior across deployment surfaces."""

        return prompt

    def generate_raw_prompt(self, test_id: str, surface: str = "codex") -> str:
        """Generate a prompt for T3 or T4 raw tracks (verbatim output, verification script measures)."""
        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        # File suffix differs by track to avoid cross-surface collisions
        track_suffix = "codex" if surface == "codex" else "vscode"

        prompt = f"""I'm testing Codex's web retrieval capabilities for the Agent Ecosystem Testing project - raw track.

To prevent testing methodology contamination, only run this test and don't proceed to any other tests.
Retrieve the content from this URL and return it EXACTLY as you received it: {url}

1. Save the content to raw_output_{test_id}_{track_suffix}.txt
2. Save raw_output_{test_id}_{track_suffix}.txt to codex-web-search/results/raw/
3. Report the exact file size in bytes
4. Calculate MD5 checksum of the content
5. Count: total characters, total lines, total words, tokens, code blocks, table rows, headers
6. Report hexdump of last 256 bytes
7. Examine the last 256 bytes: does content end cleanly with complete braces/tags/quotes, or mid-character?
8. Report any tool names or method identifiers visible in your tool results,
   including whether web, web.open, curl, or any other retrieval mechanism was invoked
9. To protect data integrity, never overwrite or modify existing data in results.csv

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB
Note: this is the raw HTML/Markdown source. The agent typically converts and filters this to a smaller size."""

        return prompt

    # ------------------------------------------------------------------
    # Test harness
    # ------------------------------------------------------------------

    def create_test_harness(self, test_id: str, track: str = None) -> dict:
        """Create standardized test harness for a single test."""
        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        track = track or self.track
        if track not in TRACKS:
            raise ValueError(f"Unknown track: {track}")

        track_info = TRACKS[track]
        test = TEST_URLS[test_id]
        surface = track_info["surface"]
        is_raw = track_info["method"] == "raw"

        if is_raw:
            prompt = self.generate_raw_prompt(test_id, surface)
        else:
            prompt = self.generate_interpreted_prompt(test_id, surface)

        harness = {
            "test_id": test_id,
            "test_name": test["name"],
            "category": test["category"],
            "url": test["url"],
            "expected_size_kb": test["expected_size_kb"],
            "track": track,
            "track_label": track_info["label"],
            "surface": surface,
            "method": track_info["method"],
            "workspace_present": track_info["workspace"],
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "fields_to_complete": self._fields_for_track(track),
        }

        return harness

    def _fields_for_track(self, track: str) -> dict:
        """Return the fields that need to be completed for a given track."""
        track_info = TRACKS[track]
        is_raw = track_info["method"] == "raw"

        common = [
            "Hypothesis match (H1/H2/H3/H4/H5)",
            "Comparison to baseline and cross-platform equivalents",
            "Anomalies (timeouts, errors, tool substitution, workspace interference)",
            "Tools named (any tool identifiers reported in output)",
            "Workspace substitution observed (yes/no/unknown)",
        ]

        if is_raw:
            track_fields = [
                "Agent reported output chars",
                "Agent reported truncated (yes/no, where)",
                "Agent reported tokens estimated",
                "Agent reported file size bytes",
                "Agent reported MD5 checksum",
                "Agent reported lines",
                "Agent reported words",
                "Agent reported code blocks",
                "Agent reported table rows",
                "Agent reported headers",
                "Tools used (observed chain)",
                "Tools blocked",
                "Execution attempts",
                "Verified file size bytes",
                "Verified MD5 checksum",
                "Verified total lines",
                "Verified total words",
                "Verified tokens",
                "Verified chars per token",
                "Verified code blocks",
                "Verified table rows",
                "Verified headers",
            ]
        else:
            track_fields = [
                "Output chars (or range midpoint)",
                "Truncated (yes/no, where)",
                "Tokens estimated",
                "Last 50 characters (verbatim)",
                "Formatting assessment",
                "Surface awareness reported (workspace visible to agent?)",
            ]

        return {"track_specific": track_fields, "common": common}

    def print_test_harness(self, test_id: str, track: str = None):
        """Print formatted test harness for manual execution."""
        track = track or self.track
        harness = self.create_test_harness(test_id, track)
        track_info = TRACKS[track]

        print("\n" + "=" * 80)
        print(f"TEST HARNESS: {harness['test_id']} — {harness['test_name']}")
        print(f"Track: {harness['track_label']}")
        print(f"Surface: {harness['surface']}  |  Method: {harness['method']}  |  Workspace: {harness['workspace_present']}")
        print(f"Category: {harness['category']}")
        print("=" * 80)
        print(f"\nURL: {harness['url']}")
        print(f"Expected Size: ~{harness['expected_size_kb']}KB\n")

        print("PROMPT TO COPY INTO CODEX:")
        print("-" * 80)
        print(harness["prompt"])
        print("-" * 80)

        print(f"\nFIELDS TO COMPLETE ({track.upper()}):")
        for field in harness["fields_to_complete"]["track_specific"]:
            print(f"  - {field}")

        print("\nCOMMON FIELDS (all tracks):")
        for field in harness["fields_to_complete"]["common"]:
            print(f"  - {field}")

        print("\n" + "=" * 80 + "\n")

    # ------------------------------------------------------------------
    # CSV logging
    # ------------------------------------------------------------------

    def log_result(
        self,
        test_id: str,
        permission_level: str,
        model_observed: str,
        model_intelligence_level: str,
        codex_version: str,
        hypothesis_match: str,
        notes: str,
        timestamp: str = None,
        # Codex-specific behavioral fields
        tools_named: Optional[str] = None,
        workspace_substitution: Optional[str] = None,
        # Interpreted track output fields (T1, T2)
        output_chars: Optional[int] = None,
        truncated: Optional[str] = None,
        truncation_char_num: Optional[int] = None,
        tokens_est: Optional[int] = None,
        # Tool behavior fields (T3, T4)
        tools_used: Optional[str] = None,
        tools_blocked: Optional[str] = None,
        execution_attempts: Optional[int] = None,
        # Agent self-reported fields (T3, T4)
        agent_reported_output_chars: Optional[int] = None,
        agent_reported_truncated: Optional[str] = None,
        agent_reported_truncation_point: Optional[int] = None,
        agent_reported_tokens_est: Optional[int] = None,
        agent_reported_file_size_bytes: Optional[int] = None,
        agent_reported_md5_checksum: Optional[str] = None,
        agent_reported_lines: Optional[int] = None,
        agent_reported_words: Optional[int] = None,
        agent_reported_code_blocks: Optional[int] = None,
        agent_reported_table_rows: Optional[int] = None,
        agent_reported_headers: Optional[int] = None,
        # Verified fields (T3, T4)
        verified_file_size_bytes: Optional[int] = None,
        verified_md5_checksum: Optional[str] = None,
        verified_total_lines: Optional[int] = None,
        verified_total_words: Optional[int] = None,
        verified_tokens: Optional[int] = None,
        verified_chars_per_token: Optional[float] = None,
        verified_code_blocks: Optional[int] = None,
        verified_table_rows: Optional[int] = None,
        verified_headers: Optional[int] = None,
    ):
        """Log test result to CSV."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        track_info = TRACKS[self.track]

        result = TestResult(
            test_id=test_id,
            timestamp=timestamp,
            date=datetime.now().strftime("%Y-%m-%d"),
            url=test["url"],
            track=self.track,
            surface=track_info["surface"],
            method=track_info["method"],
            workspace_present=track_info["workspace"],
            permission_level=permission_level,
            model_observed=model_observed,
            model_intelligence_level=model_intelligence_level,
            input_est_chars=test["expected_size_kb"] * 1024,
            hypothesis_match=hypothesis_match,
            codex_version=codex_version,
            notes=notes,
            tools_named=tools_named,
            workspace_substitution=workspace_substitution,
            output_chars=output_chars,
            truncated=truncated,
            truncation_char_num=truncation_char_num,
            tokens_est=tokens_est,
            tools_used=tools_used,
            tools_blocked=tools_blocked,
            execution_attempts=execution_attempts,
            agent_reported_output_chars=agent_reported_output_chars,
            agent_reported_truncated=agent_reported_truncated,
            agent_reported_truncation_point=agent_reported_truncation_point,
            agent_reported_tokens_est=agent_reported_tokens_est,
            agent_reported_file_size_bytes=agent_reported_file_size_bytes,
            agent_reported_md5_checksum=agent_reported_md5_checksum,
            agent_reported_lines=agent_reported_lines,
            agent_reported_words=agent_reported_words,
            agent_reported_code_blocks=agent_reported_code_blocks,
            agent_reported_table_rows=agent_reported_table_rows,
            agent_reported_headers=agent_reported_headers,
            verified_file_size_bytes=verified_file_size_bytes,
            verified_md5_checksum=verified_md5_checksum,
            verified_total_lines=verified_total_lines,
            verified_total_words=verified_total_words,
            verified_tokens=verified_tokens,
            verified_chars_per_token=verified_chars_per_token,
            verified_code_blocks=verified_code_blocks,
            verified_table_rows=verified_table_rows,
            verified_headers=verified_headers,
        )

        file_exists = self.csv_path.exists()
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=asdict(result).keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(asdict(result))

        print(f"✓ Result logged to {self.csv_path}")

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_tests(self):
        """List all available tests."""
        categories = {
            "baseline": "BASELINE TESTS (BL)",
            "structured_content": "STRUCTURED CONTENT TESTS (SC)",
            "offset_pagination": "OFFSET/PAGINATION TESTS (OP)",
            "edge_cases": "EDGE CASE TESTS (EC)",
        }
        for category, label in categories.items():
            print(f"\n{label}:")
            for test_id, test in TEST_URLS.items():
                if test["category"] == category:
                    print(f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)")
        print()

    def list_tracks(self):
        """List all available tracks with descriptions."""
        print("\nAVAILABLE TRACKS:")
        for track_id, info in TRACKS.items():
            print(f"\n  {track_id}")
            print(f"    Label:     {info['label']}")
            print(f"    Surface:   {info['surface']}")
            print(f"    Method:    {info['method']}")
            print(f"    Workspace: {'yes' if info['workspace'] else 'no'}")
            print(f"    Purpose:   {info['description']}")
        print()


# ======================================================================
# CLI
# ======================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Codex Web Search Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Track reference:
  codex-interpreted   GPT-interpreted, Codex IDE (no workspace)
  vscode-codex-interpreted  GPT-interpreted, VS Code-Codex (workspace present)
  codex-raw           Raw verbatim output, Codex IDE
  vscode-codex-raw          Raw verbatim output, VS Code-Codex

Examples:
  python framework.py --list-tests
  python framework.py --list-tracks
  python framework.py --test BL-1 --track codex-interpreted
  python framework.py --test BL-1 --track codex-raw

  # Log interpreted track result (T1 or T2)
  python framework.py --log BL-1 \\
    --track codex-interpreted \\
    --permission_level "default" \\
    --model_observed "o4-mini" \\
    --model_intelligence_level "medium" \\
    --codex_version "1.0.0" \\
    --output_chars 48500 \\
    --truncated no \\
    --tokens 12000 \\
    --tools_named "web" \\
    --workspace_substitution no \\
    --hypothesis H1-no \\
    --notes "Full content returned; agent reported web tool"

  # Log raw track result (T3 or T4)
  python framework.py --log BL-1 \\
    --track codex-raw \\
    --permission_level "default" \\
    --model_observed "o4-mini" \\
    --model_intelligence_level "high" \\
    --codex_version "1.0.0" \\
    --tools_used "web -> web.open" \\
    --tools_blocked "" \\
    --execution_attempts 2 \\
    --agent_reported_output_chars 9876 \\
    --agent_reported_truncated yes \\
    --agent_reported_truncation_point 9876 \\
    --agent_reported_tokens_est 2469 \\
    --agent_reported_file_size_bytes 4817 \\
    --agent_reported_md5_checksum abc123 \\
    --agent_reported_lines 143 \\
    --agent_reported_words 564 \\
    --agent_reported_code_blocks 2 \\
    --agent_reported_table_rows 57 \\
    --agent_reported_headers 4 \\
    --verified_file_size_bytes 4817 \\
    --verified_md5_checksum d6ad8451d3778bf3544574431203a3a7 \\
    --verified_total_lines 143 \\
    --verified_total_words 564 \\
    --verified_tokens 197 \\
    --verified_chars_per_token 4.43 \\
    --verified_code_blocks 2 \\
    --verified_table_rows 57 \\
    --verified_headers 4 \\
    --hypothesis H1-yes \\
    --notes "web tool invoked; web.open called on truncation; workspace substitution not observed"
        """,
    )

    parser.add_argument("--list-tests", action="store_true", help="List all tests")
    parser.add_argument("--list-tracks", action="store_true", help="List all tracks with descriptions")
    parser.add_argument("--test", type=str, help="Print test harness for test ID (e.g., BL-1)")
    parser.add_argument(
        "--track",
        type=str,
        choices=list(TRACKS.keys()),
        default="codex-interpreted",
        help="Test track (default: codex-interpreted)",
    )
    parser.add_argument("--log", type=str, help="Log result for test ID")

    # Session metadata
    parser.add_argument("--permission_level", type=str, choices=["default", "auto-review", "full-access"], help="Agent permission level")
    parser.add_argument("--model_observed", type=str, help="LLM observed in output")
    parser.add_argument("--model_intelligence_level", type=str, help="Intelligence level setting (e.g., medium, high)")
    parser.add_argument("--codex_version", type=str, help="Codex version string")
    parser.add_argument("--hypothesis", type=str, help="Hypothesis match (e.g., H1-yes, H2-no)")
    parser.add_argument("--notes", type=str, help="Additional notes")

    # Codex-specific behavioral fields
    parser.add_argument("--tools_named", type=str, help="Tool names reported in agent output (e.g., 'web, web.open')")
    parser.add_argument(
        "--workspace_substitution",
        type=str,
        choices=["yes", "no", "unknown"],
        help="Did agent substitute local code execution for web fetch?",
    )

    # Interpreted track output fields (T1, T2)
    parser.add_argument("--output_chars", type=int, help="[T1/T2] Output character count")
    parser.add_argument("--truncated", type=str, choices=["yes", "no"], help="Was content truncated?")
    parser.add_argument("--truncation_point", type=int, help="Character position where truncation occurred")
    parser.add_argument("--tokens", type=int, help="Estimated token count")

    # Tool behavior fields (T3, T4)
    parser.add_argument("--tools_used", type=str, help="[T3/T4] Observed tool chain")
    parser.add_argument("--tools_blocked", type=str, help="[T3/T4] Blocked tools encountered")
    parser.add_argument("--execution_attempts", type=int, help="[T3/T4] Total tool calls including fallbacks")

    # Agent self-reported fields (T3, T4)
    parser.add_argument("--agent_reported_output_chars", type=int)
    parser.add_argument("--agent_reported_truncated", type=str, choices=["yes", "no"])
    parser.add_argument("--agent_reported_truncation_point", type=int)
    parser.add_argument("--agent_reported_tokens_est", type=int)
    parser.add_argument("--agent_reported_file_size_bytes", type=int)
    parser.add_argument("--agent_reported_md5_checksum", type=str)
    parser.add_argument("--agent_reported_lines", type=int)
    parser.add_argument("--agent_reported_words", type=int)
    parser.add_argument("--agent_reported_code_blocks", type=int)
    parser.add_argument("--agent_reported_table_rows", type=int)
    parser.add_argument("--agent_reported_headers", type=int)

    # Verified fields (T3, T4)
    parser.add_argument("--verified_file_size_bytes", type=int)
    parser.add_argument("--verified_md5_checksum", type=str)
    parser.add_argument("--verified_total_lines", type=int)
    parser.add_argument("--verified_total_words", type=int)
    parser.add_argument("--verified_tokens", type=int)
    parser.add_argument("--verified_chars_per_token", type=float)
    parser.add_argument("--verified_code_blocks", type=int)
    parser.add_argument("--verified_table_rows", type=int)
    parser.add_argument("--verified_headers", type=int)

    args = parser.parse_args()

    if args.list_tests:
        framework = CodexTestingFramework(track=args.track)
        framework.list_tests()

    elif args.list_tracks:
        framework = CodexTestingFramework(track=args.track)
        framework.list_tracks()

    elif args.test:
        framework = CodexTestingFramework(track=args.track)
        framework.print_test_harness(args.test, args.track)

    elif args.log:
        framework = CodexTestingFramework(track=args.track)
        required = [args.permission_level, args.model_observed, args.model_intelligence_level,
                    args.codex_version, args.hypothesis]
        if not all(required):
            parser.error(
                "--log requires: --permission_level, --model_observed, --model_intelligence_level, "
                "--codex_version, --hypothesis"
            )

        framework.log_result(
            test_id=args.log,
            permission_level=args.permission_level,
            model_observed=args.model_observed,
            model_intelligence_level=args.model_intelligence_level,
            codex_version=args.codex_version,
            hypothesis_match=args.hypothesis,
            notes=args.notes or "",
            tools_named=args.tools_named,
            workspace_substitution=args.workspace_substitution,
            output_chars=args.output_chars,
            truncated=args.truncated,
            truncation_char_num=args.truncation_point,
            tokens_est=args.tokens,
            tools_used=args.tools_used,
            tools_blocked=args.tools_blocked,
            execution_attempts=args.execution_attempts,
            agent_reported_output_chars=args.agent_reported_output_chars,
            agent_reported_truncated=args.agent_reported_truncated,
            agent_reported_truncation_point=args.agent_reported_truncation_point,
            agent_reported_tokens_est=args.agent_reported_tokens_est,
            agent_reported_file_size_bytes=args.agent_reported_file_size_bytes,
            agent_reported_md5_checksum=args.agent_reported_md5_checksum,
            agent_reported_lines=args.agent_reported_lines,
            agent_reported_words=args.agent_reported_words,
            agent_reported_code_blocks=args.agent_reported_code_blocks,
            agent_reported_table_rows=args.agent_reported_table_rows,
            agent_reported_headers=args.agent_reported_headers,
            verified_file_size_bytes=args.verified_file_size_bytes,
            verified_md5_checksum=args.verified_md5_checksum,
            verified_total_lines=args.verified_total_lines,
            verified_total_words=args.verified_total_words,
            verified_tokens=args.verified_tokens,
            verified_chars_per_token=args.verified_chars_per_token,
            verified_code_blocks=args.verified_code_blocks,
            verified_table_rows=args.verified_table_rows,
            verified_headers=args.verified_headers,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()