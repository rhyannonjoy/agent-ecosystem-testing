"""
Copilot Web Content Retrieval Testing Framework
Generates standardized test prompts and logs results to CSV

This framework mirrors the methodology used in agent-ecosystem-testing for
Claude API, Gemini, and OpenAI platforms, but specifically echoes Cursor's testing
approach. Test URLs are sourced from the existing test suites to ensure comparable
results across platforms.

Key design decisions:
1. URLs are proven web content retrieval test cases from existing suites (Claude API, Gemini)
2. Baseline tests, BL - use the same MongoDB docs pages as Claude API testing
3. Structured content tests, SC - use API docs and reference materials
4. Offset/pagination tests, OP - Test chunking, fragment navigation, and method comparison
5. Edge case tests, EC - target specific truncation/rendering challenges
6. Two-track measurement: interpreted (what Copilot reports) + raw (exact measurements)

This allows direct comparison: "Copilot truncates at X KB, Claude API at Y KB on same URL"

Usage:
    # From copilot-web-content-retrieval/ directory
    python web_content_retrieval_testing_framework.py --list-tests
    python web_content_retrieval_testing_framework.py --test {test ID} --track interpreted
    python web_content_retrieval_testing_framework.py --test {test ID} --track raw
"""

import csv
import json
from datetime import datetime
from pathlib import Path
import argparse
from dataclasses import dataclass, asdict
from typing import Optional

# Test URLs - organized by size category
TEST_URLS = {
    # --- BASELINE TESTS, BL ---
    # Same approach as claude-api/web_fetch_test.py and gemini-url-context/url_context_test.py
    # Progressive scaling: small HTML → medium → large
    
    "BL-1": {
        "name": "Short HTML page (heavy CSS before content)",
        "url": "https://www.mongodb.com/docs/manual/reference/change-events/create/",
        "expected_size_kb": 85,  # HTML with heavy inline CSS upfront (~87% boilerplate before docs content)
        "category": "baseline",
        "note": "Same as Claude API test 1; CSS problem test from Dachary Carey research",
    },
    "BL-2": {
        "name": "Short Markdown version (same page, different encoding)",
        "url": "https://www.mongodb.com/docs/manual/reference/change-events/create.md",
        "expected_size_kb": 20,  # Same content as BL-1 but markdown (should be ~60-75% smaller)
        "category": "baseline",
        "note": "Same as Claude API test 2; HTML vs Markdown comparison baseline",
    },
    "BL-3": {
        "name": "Long HTML page (multi-section tabbed tutorial)",
        "url": "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/",
        "expected_size_kb": 250,
        "category": "baseline",
        "note": "Same as Claude API test 3; used in Claude testing to measure default truncation ceiling",
    },
    
    # --- STRUCTURED CONTENT TESTS, SC ---
    # Test how Copilot handles different content structures during truncation
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
    # Test chunking, fragment navigation, and method comparison
    "OP-1": {
        "name": "Fragment identifier navigation test",
        "url": "https://en.wikipedia.org/wiki/Machine_learning#History",
        "expected_size_kb": 40,
        "category": "offset_pagination",
        "note": "Tests if Copilot can jump to specific section via URL fragment",
    },
    "OP-4": {
        "name": "Large document - agent auto-chunking test",
        "url": "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/",
        "expected_size_kb": 250,
        "category": "offset_pagination",
        "note": "Same as BL-3; tests if Copilot agent automatically requests next chunk after truncation",
    },
    
    # --- EDGE CASES / FAILURE MODES, EC ---
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
        "url": " https://httpbin.org/redirect/5",
        "expected_size_kb": 2,
        "category": "edge_cases",
        "note": "Tests how many redirects Copilot follows before giving up or timeout",
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
    """Standard test result structure.

    Field naming conventions:
    - No prefix: session metadata and analytical fields not sourced from either track
    - copilot_reported_*: values self-reported by Copilot during the raw track session
    - verified_*: values measured by web_content_retrieval_verify_raw_results.py
    
    Interpreted track only populates the unprefixed fields (output_chars, truncated,
    truncation_char_num, tokens_est) since all data in that track is Copilot-reported
    by definition; no separate verification step exists for interpreted runs.
    
    Raw track populates both copilot_reported_* and verified_* fields, enabling
    direct comparison between what Copilot claimed and what the verifier measured.
    """

    # --- Session metadata (both tracks) ---
    test_id: str
    timestamp: str
    date: str
    url: str
    method: str
    model_selector: str
    model_observed: str
    input_est_chars: int
    hypothesis_match: str
    copilot_version: str
    notes: str

    # --- Interpreted track output fields (unprefixed: all data is Copilot-reported by definition) ---
    output_chars: Optional[int] = None
    truncated: Optional[str] = None
    truncation_char_num: Optional[int] = None
    tokens_est: Optional[int] = None

    # --- Tool behavior fields (raw track only) ---
    # Captures the tool selection chain and fallback behavior as observational metadata.
    # execution_attempts: total number of tool calls including fallbacks (e.g., 2 = fetch_webpage + pylance fallback)
    tools_used: Optional[str] = None
    tools_blocked: Optional[str] = None
    execution_attempts: Optional[int] = None

    # --- Copilot self-reported fields (raw track only) ---
    # Values reported by Copilot in its output; may differ from verified measurements
    # if Copilot fabricated, estimated, or computed from a different representation
    copilot_reported_output_chars: Optional[int] = None
    copilot_reported_truncated: Optional[str] = None
    copilot_reported_truncation_point: Optional[int] = None
    copilot_reported_tokens_est: Optional[int] = None
    copilot_reported_file_size_bytes: Optional[int] = None
    copilot_reported_md5_checksum: Optional[str] = None
    copilot_reported_lines: Optional[int] = None
    copilot_reported_words: Optional[int] = None
    copilot_reported_code_blocks: Optional[int] = None
    copilot_reported_table_rows: Optional[int] = None
    copilot_reported_headers: Optional[int] = None

    # --- Verified fields (raw track only) ---
    # Values measured by web_content_retrieval_verify_raw_results.py
    # against the saved raw_output_{test_id}.txt file
    verified_file_size_bytes: Optional[int] = None
    verified_md5_checksum: Optional[str] = None
    verified_total_lines: Optional[int] = None
    verified_total_words: Optional[int] = None
    verified_tokens: Optional[int] = None
    verified_chars_per_token: Optional[float] = None
    verified_code_blocks: Optional[int] = None
    verified_table_rows: Optional[int] = None
    verified_headers: Optional[int] = None

class CopilotTestingFramework:
    """Manage Copilot web content retrieval testing"""

    def __init__(self, results_dir: str = None, track: str = "interpreted"):
        self.track = track

        # Set results_dir based on track if not provided
        if results_dir is None:
            if track == "interpreted":
                results_dir = "results/copilot-interpreted"
            else:
                results_dir = f"results/{track}"
        
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.results_dir / "results.csv"

    def generate_interpreted_prompt(self, test_id: str, method: str = "vscode-chat") -> str:
        """Generate a prompt for interpreted track testing"""

        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        prompt = f"""I'm testing GitHub Copilot's web content retrieval capabilities for the Agent Ecosystem Testing project.

To prevent testing methodology contamination, only run this test and don't proceed to any other tests.
In addition, please don't run any local scripts or use any code execution scripts. 
Fetch this URL directly:
{url}

Then report back:
1. **Total character count** of the response you received
2. **Estimated token count** (using roughly 4 characters per token as a baseline)
3. **Whether any content appears truncated** (yes/no, and where if truncated)
4. **Last 50 characters** of the response (verbatim, to verify the cutoff point)
5. **Markdown formatting assessment** - is it complete? Are code blocks closed properly?
6. **Model's perceived completeness** - does it seem like you got the full content?
7. **Tool visibility** - report any tool names, server names, or method identifiers visible in your tool results

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB
This is for empirical documentation of truncation limits."""

        return prompt

    def generate_raw_prompt(self, test_id: str, method: str = "vscode-chat") -> str:
        """Generate a prompt for raw track testing (request verbatim output)"""

        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        prompt = f"""I'm testing GitHub Copilot's web content retrieval capabilities for the Agent Ecosystem Testing project - raw track.

To prevent testing methodology contamination, only run this test and don't proceed to any other tests.
Please retrieve the content from this URL and return it EXACTLY as you received it: {url}

1. Save the content to raw_output_{test_id}.txt
2. Save the raw_output_{test_id}.txt file to copilot-web-content-retrieval/results/raw/
3. Report the exact file size in bytes
4. Calculate MD5 checksum of the content
5. Count: total characters, total lines, total words, tokens, code blocks, table rows, headers
6. Report hexdump of last 256 bytes
7. Examine the last 256 bytes through hexdump: does content end cleanly with complete braces/tags/quotes or mid-character?
8. After retrieving, report any tool names, server names, or method identifiers visible in your tool results
9. To protect data integrity, never overwrite or modify existing data in results.csv

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB (Note: this is the raw HTML/Markdown source. Copilot typically converts and filters this to a smaller size.)"""

        return prompt

    def create_test_harness(self, test_id: str, track: str = "interpreted") -> dict:
        """Create standardized test harness for a single test"""

        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]

        harness = {
            "test_id": test_id,
            "test_name": test["name"],
            "category": test["category"],
            "url": test["url"],
            "expected_size_kb": test["expected_size_kb"],
            "track": track,
            "timestamp": datetime.now().isoformat(),
            "instructions": {
                "interpreted": self.generate_interpreted_prompt(test_id),
                "raw": self.generate_raw_prompt(test_id),
            },
            "fields_to_complete": {
                "interpreted": [
                    "Model Report (exact response from Copilot)",
                    "Estimated Length (KB or characters)",
                    "Truncation Perceived (yes/no, where)",
                    "Formatting Assessment",
                ],
                "raw": [
                    "Actual Length (characters)",
                    "Actual Length (KB)",
                    "Tokens (estimated via tiktoken)",
                    "Truncation Detected (yes/no, exact position)",
                    "Last 50 Characters (verbatim)",
                    "Clean Truncation (yes/no - mid-word?)",
                ],
                "both": [
                    "Hypothesis Match (H1/H2/H3/H4/H5)",
                    "Comparison to Baseline",
                    "Anomalies (timeouts, errors)",
                ],
            },
        }

        return harness

    def print_test_harness(self, test_id: str, track: str = "interpreted"):
        """Print formatted test harness for manual execution"""

        harness = self.create_test_harness(test_id, track)

        print("\n" + "=" * 80)
        print(f"TEST HARNESS: {harness['test_id']} - {harness['test_name']}")
        print(f"Track: {track.upper()}")
        print(f"Category: {harness['category']}")
        print("=" * 80)
        print(f"\nURL: {harness['url']}")
        print(f"Expected Size: ~{harness['expected_size_kb']}KB\n")

        print("PROMPT TO COPY INTO COPILOT:")
        print("-" * 80)
        print(harness["instructions"][track])
        print("-" * 80)

        print(f"\nFIELDS TO COMPLETE ({track.upper()}):")
        for field in harness["fields_to_complete"][track]:
            print(f"  - {field}")

        print("\nCOMMON FIELDS:")
        for field in harness["fields_to_complete"]["both"]:
            print(f"  - {field}")

        print("\n" + "=" * 80 + "\n")

    def log_result(
        self,
        test_id: str,
        method: str,
        model_selector: str,
        model_observed: str,
        copilot_version: str,
        hypothesis_match: str,
        notes: str,
        timestamp: str = None,
        # Interpreted track output fields
        output_chars: Optional[int] = None,
        truncated: Optional[str] = None,
        truncation_char_num: Optional[int] = None,
        tokens_est: Optional[int] = None,
        # Tool behavior fields (raw track)
        tools_used: Optional[str] = None,
        tools_blocked: Optional[str] = None,
        execution_attempts: Optional[int] = None,
        # Copilot self-reported fields (raw track)
        copilot_reported_output_chars: Optional[int] = None,
        copilot_reported_truncated: Optional[str] = None,
        copilot_reported_truncation_point: Optional[int] = None,
        copilot_reported_tokens_est: Optional[int] = None,
        copilot_reported_file_size_bytes: Optional[int] = None,
        copilot_reported_md5_checksum: Optional[str] = None,
        copilot_reported_lines: Optional[int] = None,
        copilot_reported_words: Optional[int] = None,
        copilot_reported_code_blocks: Optional[int] = None,
        copilot_reported_table_rows: Optional[int] = None,
        copilot_reported_headers: Optional[int] = None,
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
        """Log test result to CSV"""
        
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
            method=method,
            model_selector=model_selector,
            model_observed=model_observed,
            input_est_chars=test["expected_size_kb"] * 1024,
            hypothesis_match=hypothesis_match,
            copilot_version=copilot_version,
            notes=notes,
            # Interpreted track output fields
            output_chars=output_chars,
            truncated=truncated,
            truncation_char_num=truncation_char_num,
            tokens_est=tokens_est,
            # Tool behavior fields
            tools_used=tools_used,
            tools_blocked=tools_blocked,
            execution_attempts=execution_attempts,
            # Copilot self-reported fields
            copilot_reported_output_chars=copilot_reported_output_chars,
            copilot_reported_truncated=copilot_reported_truncated,
            copilot_reported_truncation_point=copilot_reported_truncation_point,
            copilot_reported_tokens_est=copilot_reported_tokens_est,
            copilot_reported_file_size_bytes=copilot_reported_file_size_bytes,
            copilot_reported_md5_checksum=copilot_reported_md5_checksum,
            copilot_reported_lines=copilot_reported_lines,
            copilot_reported_words=copilot_reported_words,
            copilot_reported_code_blocks=copilot_reported_code_blocks,
            copilot_reported_table_rows=copilot_reported_table_rows,
            copilot_reported_headers=copilot_reported_headers,
            # Verified fields
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

        # Write or append to CSV
        file_exists = self.csv_path.exists()
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=asdict(result).keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(asdict(result))

        print(f"✓ Result logged to {self.csv_path}")

    def list_tests(self):
        """List all available tests"""

        print("\nAvailable Tests:\n")
        print("BASELINE TESTS (BL):")
        for test_id, test in TEST_URLS.items():
            if test["category"] == "baseline":
                print(f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)")

        print("\nSTRUCTURED CONTENT TESTS (SC):")
        for test_id, test in TEST_URLS.items():
            if test["category"] == "structured_content":
                print(f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)")

        print("\nOFFSET/PAGINATION TESTS (OP):")
        for test_id, test in TEST_URLS.items():
            if test["category"] == "offset_pagination":
                print(f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)")

        print("\nEDGE CASE TESTS (EC):")
        for test_id, test in TEST_URLS.items():
            if test["category"] == "edge_cases":
                print(f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="Copilot Web Fetch Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_content_retrieval_testing_framework.py --list-tests
  python web_content_retrieval_testing_framework.py --test BL-1 --track interpreted
  python web_content_retrieval_testing_framework.py --test SC-2 --track raw

  # Log interpreted track result
  python web_content_retrieval_testing_framework.py --log BL-1 \\
    --track interpreted \\
    --method vscode-chat \\
    --model_selector Auto \\
    --model_observed "Raptor mini (Preview)" \\
    --copilot_version 0.41.1 \\
    --output_chars 48500 \\
    --truncated no \\
    --tokens 12000 \\
    --hypothesis H1-no \\
    --notes "Full content returned, no truncation observed"

  # Verify key metrics before logging raw track runs
  python web_content_retrieval_verify_raw_results.py BL-1

  # Log raw track result
  python web_content_retrieval_testing_framework.py --log BL-1 \\
    --track raw \\
    --method vscode-chat \\
    --model_selector Auto \\
    --model_observed "Raptor mini (Preview)" \\
    --copilot_version 0.41.1 \\
    --copilot_reported_output_chars 9876 \\
    --copilot_reported_truncated yes \\
    --copilot_reported_truncation_point 9876 \\
    --copilot_reported_tokens_est 2469 \\
    --copilot_reported_file_size_bytes 4817 \\
    --copilot_reported_md5_checksum abc123 \\
    --copilot_reported_lines 143 \\
    --copilot_reported_words 564 \\
    --copilot_reported_code_blocks 2 \\
    --copilot_reported_table_rows 57 \\
    --copilot_reported_headers 4 \\
    --tools_used "fetch_webpage -> pylanceRunCodeSnippet" \\
    --tools_blocked "terminal execution" \\
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
    --notes "vscode-chat returns converted..."
        """,
    )

    parser.add_argument("--list-tests", action="store_true", help="List all tests")
    parser.add_argument("--test", type=str, help="Run specific test by ID (e.g., BL-1, SC-2)")
    parser.add_argument(
        "--track",
        type=str,
        choices=["interpreted", "raw"],
        default="interpreted",
        help="Test track (interpreted or raw)",
    )
    parser.add_argument(
        "--method",
        type=str,
        default="vscode-chat",
        help="Fetch method (currently only vscode-chat is tested)",
    )
    parser.add_argument("--log", type=str, help="Log result for test ID")
    parser.add_argument("--model_selector", type=str, help="Model selector used (e.g., Auto)")
    parser.add_argument("--model_observed", type=str, help="Model observed (e.g., 'Raptor mini (Preview)')")
    parser.add_argument("--copilot_version", type=str, help="Copilot IDE version")
    parser.add_argument("--hypothesis", type=str, help="Hypothesis match (e.g., H1-yes, H2-no, EC-timeout)")
    parser.add_argument("--notes", type=str, help="Additional notes")

    # Interpreted track output fields
    parser.add_argument("--output_chars", type=int, help="[Interpreted] Output character count")
    parser.add_argument(
        "--truncated",
        type=str,
        choices=["yes", "no"],
        help="[Interpreted] Was content truncated?",
    )
    parser.add_argument(
        "--truncation_point",
        type=int,
        help="[Interpreted] Character position where truncation occurred",
    )
    parser.add_argument("--tokens", type=int, help="[Interpreted] Estimated token count")

    # Tool behavior fields (raw track)
    parser.add_argument(
        "--tools_used",
        type=str,
        help="[Raw] Tool chain used during retrieval (e.g., 'fetch_webpage -> pylanceRunCodeSnippet')",
    )
    parser.add_argument(
        "--tools_blocked",
        type=str,
        help="[Raw] Blocked or disallowed tools encountered during retrieval",
    )
    parser.add_argument(
        "--execution_attempts",
        type=int,
        help="[Raw] Total tool calls including fallbacks (e.g., 2 = fetch_webpage + pylance fallback)",
    )

    # Copilot self-reported fields (raw track)
    parser.add_argument("--copilot_reported_output_chars", type=int, help="[Raw] Copilot-reported output character count")
    parser.add_argument(
        "--copilot_reported_truncated",
        type=str,
        choices=["yes", "no"],
        help="[Raw] Copilot-reported truncation status",
    )
    parser.add_argument("--copilot_reported_truncation_point", type=int, help="[Raw] Copilot-reported truncation point")
    parser.add_argument("--copilot_reported_tokens_est", type=int, help="[Raw] Copilot-reported estimated token count")
    parser.add_argument("--copilot_reported_file_size_bytes", type=int, help="[Raw] Copilot-reported file size in bytes")
    parser.add_argument("--copilot_reported_md5_checksum", type=str, help="[Raw] Copilot-reported MD5 checksum")
    parser.add_argument("--copilot_reported_lines", type=int, help="[Raw] Copilot-reported line count")
    parser.add_argument("--copilot_reported_words", type=int, help="[Raw] Copilot-reported word count")
    parser.add_argument("--copilot_reported_code_blocks", type=int, help="[Raw] Copilot-reported code block count")
    parser.add_argument("--copilot_reported_table_rows", type=int, help="[Raw] Copilot-reported table row count")
    parser.add_argument("--copilot_reported_headers", type=int, help="[Raw] Copilot-reported header count")

    # Verified fields (raw track)
    parser.add_argument("--verified_file_size_bytes", type=int, help="[Raw] Verifier-measured file size in bytes")
    parser.add_argument("--verified_md5_checksum", type=str, help="[Raw] Verifier-measured MD5 checksum")
    parser.add_argument("--verified_total_lines", type=int, help="[Raw] Verifier-measured line count")
    parser.add_argument("--verified_total_words", type=int, help="[Raw] Verifier-measured word count")
    parser.add_argument("--verified_tokens", type=int, help="[Raw] Verifier-measured token count")
    parser.add_argument(
        "--verified_chars_per_token",
        type=float,
        help="[Raw] Verifier-measured chars/token ratio",
    )
    parser.add_argument("--verified_code_blocks", type=int, help="[Raw] Verifier-measured code block count")
    parser.add_argument("--verified_table_rows", type=int, help="[Raw] Verifier-measured table row count")
    parser.add_argument("--verified_headers", type=int, help="[Raw] Verifier-measured header count")

    args = parser.parse_args()

    if args.list_tests:
        framework = CopilotTestingFramework(track=args.track)
        framework.list_tests()

    elif args.test:
        framework = CopilotTestingFramework(track=args.track)
        framework.print_test_harness(args.test, args.track)

    elif args.log:
        framework = CopilotTestingFramework(track=args.track)
        if not all([
            args.model_selector,
            args.model_observed,
            args.copilot_version,
            args.hypothesis,
        ]):
            parser.error("--log requires: --model_selector, --model_observed, --copilot_version, --hypothesis")

        framework.log_result(
            test_id=args.log,
            method=args.method,
            model_selector=args.model_selector,
            model_observed=args.model_observed,
            copilot_version=args.copilot_version,
            hypothesis_match=args.hypothesis,
            notes=args.notes or "",
            # Interpreted track output fields
            output_chars=args.output_chars,
            truncated=args.truncated,
            truncation_char_num=args.truncation_point,
            tokens_est=args.tokens,
            # Tool behavior fields
            tools_used=args.tools_used,
            tools_blocked=args.tools_blocked,
            execution_attempts=args.execution_attempts,
            # Copilot self-reported fields
            copilot_reported_output_chars=args.copilot_reported_output_chars,
            copilot_reported_truncated=args.copilot_reported_truncated,
            copilot_reported_truncation_point=args.copilot_reported_truncation_point,
            copilot_reported_tokens_est=args.copilot_reported_tokens_est,
            copilot_reported_file_size_bytes=args.copilot_reported_file_size_bytes,
            copilot_reported_md5_checksum=args.copilot_reported_md5_checksum,
            copilot_reported_lines=args.copilot_reported_lines,
            copilot_reported_words=args.copilot_reported_words,
            copilot_reported_code_blocks=args.copilot_reported_code_blocks,
            copilot_reported_table_rows=args.copilot_reported_table_rows,
            copilot_reported_headers=args.copilot_reported_headers,
            # Verified fields
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