"""
Cascade Web Search Testing Framework
Generates standardized test prompts and logs results to CSV

This framework adapts the Copilot testing framework for Windsurf's Cascade agent,
extending it with a third track to isolate the effect of the `@web` directive.

Key design decisions:
1. URLs are the same proven test cases used across Claude API, Gemini, Copilot, and Cursor
   testing suites, enabling direct cross-platform comparison
2. Baseline tests, BL - use the same MongoDB docs pages as Claude API testing
3. Structured content tests, SC - use API docs and reference materials
4. Offset/pagination tests, OP - test chunking, fragment navigation, and auto-pagination
5. Edge case tests, EC - target specific truncation/rendering challenges
6. Three-track measurement:
   - interpreted: what Cascade reports back without steering (no `@web`)
   - raw: what `read_url_content` actually returns verbatim (no `@web`)
   - explicit: identical to interpreted, but prefixed with `@web`

The explicit track exists specifically to answer whether `@web` changes retrieval
behavior — ceiling, tool chain, chunking — or repeats the Cursor finding that the
directive is redundant with autonomous agent behavior.

This allows direct comparison:
  "Cascade-implicit truncates at X KB, Cascade-explicit at Y KB, Copilot at Z KB on same URL"

Usage:
    # From windsurf-cascade-web-search/ directory
    python web_search_testing_framework.py --list-tests
    python web_search_testing_framework.py --test {test ID} --track interpreted
    python web_search_testing_framework.py --test {test ID} --track raw
    python web_search_testing_framework.py --test {test ID} --track explicit
"""

import csv
from datetime import datetime
from pathlib import Path
import argparse
from dataclasses import dataclass, asdict
from typing import Optional

# Test URLs - organized by size category
# Same URLs as Copilot/Cursor/Claude API suites for cross-platform comparability
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
        "name": "Short Markdown version (same page, different encoding)",
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
    # Test how Cascade handles different content structures during truncation
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
    # Test chunking, fragment navigation, and auto-pagination via view_content_chunk
    "OP-1": {
        "name": "Fragment identifier navigation test",
        "url": "https://en.wikipedia.org/wiki/Machine_learning#History",
        "expected_size_kb": 40,
        "category": "offset_pagination",
        "note": "Tests if Cascade jumps to specific section via URL fragment",
    },
    "OP-4": {
        "name": "Large document - agent auto-chunking test",
        "url": "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/",
        "expected_size_kb": 250,
        "category": "offset_pagination",
        "note": "Same as BL-3; tests if Cascade auto-paginates via view_content_chunk after truncation",
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
        "note": "Tests how many redirects Cascade follows before giving up or timeout",
    },
    "EC-6": {
        "name": "Very long single lines (no line breaks)",
        "url": "https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md",
        "expected_size_kb": 60,
        "category": "edge_cases",
        "note": "Markdown with potentially long lines; tests line-wrapping vs character-based truncation",
    },
}


@dataclass
class TestResult:
    """Standard test result structure for Cascade testing.

    Field naming conventions:
    - No prefix: session metadata and analytical fields not sourced from either track
    - cascade_reported_*: values self-reported by Cascade during the raw track session
    - verified_*: values measured by the verification script against the saved raw output file

    Track behavior:
    - Interpreted track: populates unprefixed output fields (output_chars, truncated,
      truncation_char_num, tokens_est); all data is Cascade-reported by definition
    - Raw track: populates both cascade_reported_* and verified_* fields, enabling
      direct comparison between what Cascade claimed and what the verifier measured
    - Explicit track: same fields as interpreted track; method field distinguishes it
      (cascade-explicit vs cascade-implicit)

    Cascade-specific fields vs Copilot framework:
    - approval_required: logs approval-gating behavior per run (no Copilot/Cursor analog)
    - pagination_observed: logs whether view_content_chunk was invoked automatically
    - windsurf_version replaces copilot_version
    - method uses cascade-implicit / cascade-explicit
    """

    # --- Session metadata (all tracks) ---
    test_id: str
    timestamp: str
    date: str
    url: str
    track: str                    # interpreted | raw | explicit
    method: str                   # cascade-implicit | cascade-explicit
    model_selector: str
    model_observed: str
    input_est_chars: int
    hypothesis_match: str
    windsurf_version: str
    notes: str

    # --- Cascade-specific behavioral fields (all tracks) ---
    # approval_required: was the user prompted to approve read_url_content before fetch?
    # Values: yes | no | unknown
    approval_required: Optional[str] = None
    # pagination_observed: did view_content_chunk invoke automatically without prompting?
    # Values: yes-auto | yes-prompted | no | unknown
    pagination_observed: Optional[str] = None

    # --- Interpreted and explicit track output fields ---
    # (unprefixed: all data is Cascade-reported by definition on these tracks)
    output_chars: Optional[int] = None
    truncated: Optional[str] = None
    truncation_char_num: Optional[int] = None
    tokens_est: Optional[int] = None

    # --- Tool behavior fields (raw track) ---
    # tools_used: tool chain observed, e.g. "read_url_content -> view_content_chunk"
    # execution_attempts: total tool calls including fallbacks
    tools_used: Optional[str] = None
    tools_blocked: Optional[str] = None
    execution_attempts: Optional[int] = None

    # --- Cascade self-reported fields (raw track) ---
    # Values reported by Cascade in its output; may differ from verified measurements
    cascade_reported_output_chars: Optional[int] = None
    cascade_reported_truncated: Optional[str] = None
    cascade_reported_truncation_point: Optional[int] = None
    cascade_reported_tokens_est: Optional[int] = None
    cascade_reported_file_size_bytes: Optional[int] = None
    cascade_reported_md5_checksum: Optional[str] = None
    cascade_reported_lines: Optional[int] = None
    cascade_reported_words: Optional[int] = None
    cascade_reported_code_blocks: Optional[int] = None
    cascade_reported_table_rows: Optional[int] = None
    cascade_reported_headers: Optional[int] = None

    # --- Verified fields (raw track) ---
    # Values measured by the verification script against the saved raw_output_{test_id}.txt file
    verified_file_size_bytes: Optional[int] = None
    verified_md5_checksum: Optional[str] = None
    verified_total_lines: Optional[int] = None
    verified_total_words: Optional[int] = None
    verified_tokens: Optional[int] = None
    verified_chars_per_token: Optional[float] = None
    verified_code_blocks: Optional[int] = None
    verified_table_rows: Optional[int] = None
    verified_headers: Optional[int] = None


class CascadeTestingFramework:
    """Manage Cascade web search testing across three tracks."""

    def __init__(self, results_dir: str = None, track: str = "interpreted"):
        if track not in ("interpreted", "raw", "explicit"):
            raise ValueError(f"Unknown track: {track}. Must be interpreted, raw, or explicit.")

        self.track = track

        if results_dir is None:
            results_dir = f"results/cascade-{track}"

        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.results_dir / "results.csv"

    def _method_for_track(self, track: str) -> str:
        """Return the method string for a given track."""
        if track == "explicit":
            return "cascade-explicit"
        return "cascade-implicit"

    def generate_interpreted_prompt(self, test_id: str) -> str:
        """Generate a prompt for the interpreted track (no @web, report measurements)."""
        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        prompt = f"""I'm testing Cascade's web search capabilities for the Agent Ecosystem Testing project.

To prevent testing methodology contamination, only run this test and don't proceed to any other tests.
Please don't run any local scripts. Fetch this URL directly:
{url}

Then report back:
1. **Total character count** of the response you received
2. **Estimated token count**
3. **Whether any content appears truncated** (yes/no, and where if truncated)
4. **Last 50 characters** of the response (verbatim, to verify the cutoff point)
5. **Markdown formatting assessment** - is it complete? Are code blocks closed properly?
6. **Model's perceived completeness** - does it seem like you got the full content?
7. **Tool visibility** - report any tool names or method identifiers visible in your tool results,
   including whether read_url_content, view_content_chunk, or search_web were invoked
8. **Pagination behavior** - did view_content_chunk invoke automatically, or only when prompted?

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB
This is for empirical documentation of truncation limits."""

        return prompt

    def generate_explicit_prompt(self, test_id: str) -> str:
        """Generate a prompt for the explicit track, @web prefixed, otherwise identical to interpreted."""
        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        prompt = f"""I'm testing Cascade's web search capabilities for the Agent Ecosystem Testing project - explicit track.

To prevent testing methodology contamination, only run this test and don't proceed to any other tests.
Please don't run any local scripts. Use the @web directive to fetch this URL directly:
{url}

Then report back:
1. **Total character count** of the response you received
2. **Estimated token count**
3. **Whether any content appears truncated** (yes/no, and where if truncated)
4. **Last 50 characters** of the response (verbatim, to verify the cutoff point)
5. **Markdown formatting assessment** - is it complete? Are code blocks closed properly?
6. **Model's perceived completeness** - does it seem like you got the full content?
7. **Tool visibility** - report any tool names or method identifiers visible in your tool results,
   including whether read_url_content, view_content_chunk, or search_web were invoked
8. **Pagination behavior** - did view_content_chunk invoke automatically, or only when prompted?

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB
This is for empirical documentation of truncation limits."""

        return prompt

    def generate_raw_prompt(self, test_id: str) -> str:
        """Generate a prompt for the raw track, no @web, request verbatim output."""
        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        prompt = f"""I'm testing Cascade's web search capabilities for the Agent Ecosystem Testing project - raw track.

To prevent testing methodology contamination, only run this test and don't proceed to any other tests.
Please complete the steps below without using any local Python scripts from this codebase.
Retrieve the content from this URL and return it EXACTLY as you received it: {url}

1. Save the content to raw_output_{test_id}.txt
2. Save raw_output_{test_id}.txt to windsurf-cascade-web-search/results/raw/
3. Report the exact file size in bytes
4. Calculate MD5 checksum of the content
5. Count: total characters, total lines, total words, tokens, code blocks, table rows, headers
6. Report hexdump of last 256 bytes
7. Examine the last 256 bytes: does content end cleanly with complete braces/tags/quotes, or mid-character?
8. Report any tool names or method identifiers visible in your tool results,
   including whether read_url_content, view_content_chunk, or search_web were invoked
9. To protect data integrity, never overwrite or modify existing data in results.csv

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB
Note: this is the raw HTML/Markdown source. Cascade typically converts and filters this to a smaller size."""

        return prompt

    def create_test_harness(self, test_id: str, track: str = None) -> dict:
        """Create standardized test harness for a single test."""
        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        track = track or self.track
        test = TEST_URLS[test_id]

        harness = {
            "test_id": test_id,
            "test_name": test["name"],
            "category": test["category"],
            "url": test["url"],
            "expected_size_kb": test["expected_size_kb"],
            "track": track,
            "method": self._method_for_track(track),
            "timestamp": datetime.now().isoformat(),
            "instructions": {
                "interpreted": self.generate_interpreted_prompt(test_id),
                "raw": self.generate_raw_prompt(test_id),
                "explicit": self.generate_explicit_prompt(test_id),
            },
            "fields_to_complete": {
                "interpreted": [
                    "Output chars (or range midpoint)",
                    "Truncated (yes/no, where)",
                    "Tokens estimated",
                    "Last 50 characters (verbatim)",
                    "Formatting assessment",
                    "Approval required (yes/no/unknown)",
                    "Pagination observed (yes-auto/yes-prompted/no/unknown)",
                ],
                "explicit": [
                    "Output chars (or range midpoint)",
                    "Truncated (yes/no, where)",
                    "Tokens estimated",
                    "Last 50 characters (verbatim)",
                    "Formatting assessment",
                    "Approval required (yes/no/unknown)",
                    "Pagination observed (yes-auto/yes-prompted/no/unknown)",
                ],
                "raw": [
                    "Actual length (characters)",
                    "Actual length (KB)",
                    "Tokens (via tiktoken)",
                    "Truncation detected (yes/no, exact position)",
                    "Last 50 characters (verbatim)",
                    "Clean truncation (yes/no - mid-word?)",
                    "Approval required (yes/no/unknown)",
                    "Pagination observed (yes-auto/yes-prompted/no/unknown)",
                    "Tools used (chain)",
                    "Tools blocked",
                    "Execution attempts",
                ],
                "both": [
                    "Hypothesis match (H1/H2/H3/H4/H5)",
                    "Comparison to baseline",
                    "Anomalies (timeouts, errors, tool substitution)",
                ],
            },
        }

        return harness

    def print_test_harness(self, test_id: str, track: str = None):
        """Print formatted test harness for manual execution."""
        track = track or self.track
        harness = self.create_test_harness(test_id, track)

        print("\n" + "=" * 80)
        print(f"TEST HARNESS: {harness['test_id']} - {harness['test_name']}")
        print(f"Track: {track.upper()}  |  Method: {harness['method']}")
        print(f"Category: {harness['category']}")
        print("=" * 80)
        print(f"\nURL: {harness['url']}")
        print(f"Expected Size: ~{harness['expected_size_kb']}KB\n")

        print("PROMPT TO COPY INTO CASCADE:")
        print("-" * 80)
        print(harness["instructions"][track])
        print("-" * 80)

        print(f"\nFIELDS TO COMPLETE ({track.upper()}):")
        for field in harness["fields_to_complete"][track]:
            print(f"  - {field}")

        print("\nCOMMON FIELDS (all tracks):")
        for field in harness["fields_to_complete"]["both"]:
            print(f"  - {field}")

        print("\n" + "=" * 80 + "\n")

    def log_result(
        self,
        test_id: str,
        method: str,
        model_selector: str,
        model_observed: str,
        windsurf_version: str,
        hypothesis_match: str,
        notes: str,
        timestamp: str = None,
        # Cascade-specific behavioral fields
        approval_required: Optional[str] = None,
        pagination_observed: Optional[str] = None,
        # Interpreted and explicit track output fields
        output_chars: Optional[int] = None,
        truncated: Optional[str] = None,
        truncation_char_num: Optional[int] = None,
        tokens_est: Optional[int] = None,
        # Tool behavior fields (raw track)
        tools_used: Optional[str] = None,
        tools_blocked: Optional[str] = None,
        execution_attempts: Optional[int] = None,
        # Cascade self-reported fields (raw track)
        cascade_reported_output_chars: Optional[int] = None,
        cascade_reported_truncated: Optional[str] = None,
        cascade_reported_truncation_point: Optional[int] = None,
        cascade_reported_tokens_est: Optional[int] = None,
        cascade_reported_file_size_bytes: Optional[int] = None,
        cascade_reported_md5_checksum: Optional[str] = None,
        cascade_reported_lines: Optional[int] = None,
        cascade_reported_words: Optional[int] = None,
        cascade_reported_code_blocks: Optional[int] = None,
        cascade_reported_table_rows: Optional[int] = None,
        cascade_reported_headers: Optional[int] = None,
        # Verified fields (raw track)
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

        result = TestResult(
            test_id=test_id,
            timestamp=timestamp,
            date=datetime.now().strftime("%Y-%m-%d"),
            url=test["url"],
            track=self.track,
            method=method,
            model_selector=model_selector,
            model_observed=model_observed,
            input_est_chars=test["expected_size_kb"] * 1024,
            hypothesis_match=hypothesis_match,
            windsurf_version=windsurf_version,
            notes=notes,
            approval_required=approval_required,
            pagination_observed=pagination_observed,
            output_chars=output_chars,
            truncated=truncated,
            truncation_char_num=truncation_char_num,
            tokens_est=tokens_est,
            tools_used=tools_used,
            tools_blocked=tools_blocked,
            execution_attempts=execution_attempts,
            cascade_reported_output_chars=cascade_reported_output_chars,
            cascade_reported_truncated=cascade_reported_truncated,
            cascade_reported_truncation_point=cascade_reported_truncation_point,
            cascade_reported_tokens_est=cascade_reported_tokens_est,
            cascade_reported_file_size_bytes=cascade_reported_file_size_bytes,
            cascade_reported_md5_checksum=cascade_reported_md5_checksum,
            cascade_reported_lines=cascade_reported_lines,
            cascade_reported_words=cascade_reported_words,
            cascade_reported_code_blocks=cascade_reported_code_blocks,
            cascade_reported_table_rows=cascade_reported_table_rows,
            cascade_reported_headers=cascade_reported_headers,
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


def main():
    parser = argparse.ArgumentParser(
        description="Cascade Web Search Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_search_testing_framework.py --list-tests
  python web_search_testing_framework.py --test BL-1 --track interpreted
  python web_search_testing_framework.py --test BL-1 --track explicit
  python web_search_testing_framework.py --test SC-2 --track raw

  # Log interpreted or explicit track result
  python web_search_testing_framework.py --log BL-1 \\
    --track interpreted \\
    --method cascade-implicit \\
    --model_selector "Hybrid Arena" \\
    --model_observed "SWE-1" \\
    --windsurf_version "1.9600.38-pro" \\
    --output_chars 48500 \\
    --truncated no \\
    --tokens 12000 \\
    --approval_required yes \\
    --pagination_observed no \\
    --hypothesis H1-no \\
    --notes "Full content returned, approval prompted once"

  # Log explicit track result (note method change)
  python web_search_testing_framework.py --log BL-1 \\
    --track explicit \\
    --method cascade-explicit \\
    --model_selector "Hybrid Arena" \\
    --model_observed "SWE-1" \\
    --windsurf_version "1.9600.38-pro" \\
    --output_chars 51000 \\
    --truncated no \\
    --tokens 12750 \\
    --approval_required yes \\
    --pagination_observed no \\
    --hypothesis H1-no \\
    --notes "@web prefix did not change output size materially"

  # Verify key metrics before logging raw track runs
  python web_content_retrieval_verify_raw_results.py BL-1

  # Log raw track result
  python web_search_testing_framework.py --log BL-1 \\
    --track raw \\
    --method cascade-implicit \\
    --model_selector "Hybrid Arena" \\
    --model_observed "SWE-1" \\
    --windsurf_version "1.9600.38-pro" \\
    --approval_required yes \\
    --pagination_observed yes-auto \\
    --cascade_reported_output_chars 9876 \\
    --cascade_reported_truncated yes \\
    --cascade_reported_truncation_point 9876 \\
    --cascade_reported_tokens_est 2469 \\
    --cascade_reported_file_size_bytes 4817 \\
    --cascade_reported_md5_checksum abc123 \\
    --cascade_reported_lines 143 \\
    --cascade_reported_words 564 \\
    --cascade_reported_code_blocks 2 \\
    --cascade_reported_table_rows 57 \\
    --cascade_reported_headers 4 \\
    --tools_used "read_url_content -> view_content_chunk" \\
    --tools_blocked "" \\
    --execution_attempts 2 \\
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
    --notes "read_url_content returned excerpted content; view_content_chunk auto-invoked"
        """,
    )

    parser.add_argument("--list-tests", action="store_true", help="List all tests")
    parser.add_argument("--test", type=str, help="Print test harness for test ID (e.g., BL-1)")
    parser.add_argument(
        "--track",
        type=str,
        choices=["interpreted", "raw", "explicit"],
        default="interpreted",
        help="Test track: interpreted (no @web), raw (verbatim output, no @web), explicit (@web prefixed)",
    )
    parser.add_argument("--log", type=str, help="Log result for test ID")
    parser.add_argument(
        "--method",
        type=str,
        choices=["cascade-implicit", "cascade-explicit"],
        help="Fetch method — implicit for interpreted/raw tracks, explicit for explicit track",
    )
    parser.add_argument("--model_selector", type=str, help="Model selector used (e.g., Auto)")
    parser.add_argument("--model_observed", type=str, help="Model observed (e.g., SWE-1)")
    parser.add_argument("--windsurf_version", type=str, help="Cascade/Windsurf version")
    parser.add_argument("--hypothesis", type=str, help="Hypothesis match (e.g., H1-yes, H2-no)")
    parser.add_argument("--notes", type=str, help="Additional notes")

    # Cascade-specific behavioral fields
    parser.add_argument(
        "--approval_required",
        type=str,
        choices=["yes", "no", "unknown"],
        help="Was approval prompted before read_url_content executed?",
    )
    parser.add_argument(
        "--pagination_observed",
        type=str,
        choices=["yes-auto", "yes-prompted", "no", "unknown"],
        help="Did view_content_chunk invoke automatically, only when prompted, or not at all?",
    )

    # Interpreted and explicit track output fields
    parser.add_argument("--output_chars", type=int, help="[Interpreted/Explicit] Output character count")
    parser.add_argument("--truncated", type=str, choices=["yes", "no"], help="Was content truncated?")
    parser.add_argument("--truncation_point", type=int, help="Character position where truncation occurred")
    parser.add_argument("--tokens", type=int, help="Estimated token count")

    # Tool behavior fields (raw track)
    parser.add_argument("--tools_used", type=str, help="[Raw] Tool chain (e.g., 'read_url_content -> view_content_chunk')")
    parser.add_argument("--tools_blocked", type=str, help="[Raw] Blocked tools encountered")
    parser.add_argument("--execution_attempts", type=int, help="[Raw] Total tool calls including fallbacks")

    # Cascade self-reported fields (raw track)
    parser.add_argument("--cascade_reported_output_chars", type=int)
    parser.add_argument("--cascade_reported_truncated", type=str, choices=["yes", "no"])
    parser.add_argument("--cascade_reported_truncation_point", type=int)
    parser.add_argument("--cascade_reported_tokens_est", type=int)
    parser.add_argument("--cascade_reported_file_size_bytes", type=int)
    parser.add_argument("--cascade_reported_md5_checksum", type=str)
    parser.add_argument("--cascade_reported_lines", type=int)
    parser.add_argument("--cascade_reported_words", type=int)
    parser.add_argument("--cascade_reported_code_blocks", type=int)
    parser.add_argument("--cascade_reported_table_rows", type=int)
    parser.add_argument("--cascade_reported_headers", type=int)

    # Verified fields (raw track)
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
        framework = CascadeTestingFramework(track=args.track)
        framework.list_tests()

    elif args.test:
        framework = CascadeTestingFramework(track=args.track)
        framework.print_test_harness(args.test, args.track)

    elif args.log:
        framework = CascadeTestingFramework(track=args.track)
        if not all([args.model_selector, args.model_observed, args.windsurf_version, args.hypothesis]):
            parser.error("--log requires: --model_selector, --model_observed, --windsurf_version, --hypothesis")

        # Default method based on track if not explicitly provided
        method = args.method or framework._method_for_track(args.track)

        framework.log_result(
            test_id=args.log,
            method=method,
            model_selector=args.model_selector,
            model_observed=args.model_observed,
            windsurf_version=args.windsurf_version,
            hypothesis_match=args.hypothesis,
            notes=args.notes or "",
            approval_required=args.approval_required,
            pagination_observed=args.pagination_observed,
            output_chars=args.output_chars,
            truncated=args.truncated,
            truncation_char_num=args.truncation_point,
            tokens_est=args.tokens,
            tools_used=args.tools_used,
            tools_blocked=args.tools_blocked,
            execution_attempts=args.execution_attempts,
            cascade_reported_output_chars=args.cascade_reported_output_chars,
            cascade_reported_truncated=args.cascade_reported_truncated,
            cascade_reported_truncation_point=args.cascade_reported_truncation_point,
            cascade_reported_tokens_est=args.cascade_reported_tokens_est,
            cascade_reported_file_size_bytes=args.cascade_reported_file_size_bytes,
            cascade_reported_md5_checksum=args.cascade_reported_md5_checksum,
            cascade_reported_lines=args.cascade_reported_lines,
            cascade_reported_words=args.cascade_reported_words,
            cascade_reported_code_blocks=args.cascade_reported_code_blocks,
            cascade_reported_table_rows=args.cascade_reported_table_rows,
            cascade_reported_headers=args.cascade_reported_headers,
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