"""
Cursor Web Fetch Testing Framework
Generates standardized test prompts and logs results to CSV

This framework mirrors the methodology used in agent-ecosystem-testing for
Claude API, Gemini, and OpenAI platforms. Test URLs are sourced from the
existing test suites to ensure **comparable results across platforms**.

Key design decisions:
1. URLs are proven web fetch test cases from existing suites (Claude API, Gemini)
2. Baseline tests, BL - use the same MongoDB docs pages as Claude API testing
3. Structured content tests, - SC use API docs and reference materials
4. Offest/Pagination Tests, OP - Test chunking, fragment navigation, and method comparison
5. Edge case tests, EC - target specific truncation/rendering challenges
6. Two-track measurement: interpreted (what Cursor reports) + raw (exact measurements)

This allows direct comparison: "Cursor truncates at X KB, Claude API at Y KB on same URL"

Usage:
    python cursor_testing_framework.py --list-tests
    python cursor_testing_framework.py --test BL-1 --track interpreted
    python cursor_testing_framework.py --log BL-1 --track interpreted --method @Web ...
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
    # Test how Cursor handles different content structures during truncation
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
        "note": "Tests if Cursor can jump to specific section via URL fragment",
    },
    "OP-3": {
        "name": "MCP vs @Web side-by-side comparison",
        "url": "https://httpbin.org/html",
        "expected_size_kb": 5,
        "category": "offset_pagination",
        "note": "Small, predictable HTML; same URL for both @Web and mcp-server-fetch comparison",
    },
    "OP-4": {
        "name": "Large document - agent auto-chunking test",
        "url": "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/",
        "expected_size_kb": 250,
        "category": "offset_pagination",
        "note": "Same as BL-3; tests if Cursor agent automatically requests next chunk after truncation",
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
        "note": "Tests how many redirects Cursor follows before giving up or timeout",
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
    """Standard test result structure"""

    test_id: str
    timestamp: str
    date: str
    url: str
    method: str
    model: str
    input_est_chars: int
    output_chars: int
    truncated: str
    truncation_char_num: Optional[int]
    tokens_est: int
    hypothesis_match: str
    notes: str
    cursor_version: str
    # Raw track fields (optional, only populated for raw track)
    file_size_bytes: Optional[int] = None
    md5_checksum: Optional[str] = None
    total_lines: Optional[int] = None
    total_words: Optional[int] = None
    code_blocks: Optional[int] = None
    table_rows: Optional[int] = None
    headers: Optional[int] = None

class CursorTestingFramework:
    """Manage Cursor web fetch testing"""

    def __init__(self, results_dir: str = None, track: str = "interpreted"):
        self.track = track

        # Set results_dir based on track if not provided
        if results_dir is None:
            if track == "interpreted":
                results_dir = "results/cursor-interpreted"
            else:
                results_dir = f"results/{track}"
        
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.results_dir / "results.csv"

    def generate_interpreted_prompt(self, test_id: str, method: str = "@Web") -> str:
        """Generate a prompt for interpreted track testing"""

        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        if method == "@Web":
            prompt = f"""I'm testing Cursor's web fetch capabilities for the Agent Ecosystem Testing project.

Run this test only, don't proceed to any other tests. Please use the @Web command to fetch this URL:
{url}

Then report back:
1. **Total character count** of the response you received
2. **Estimated token count** (using roughly 4 characters per token as a baseline)
3. **Whether any content appears truncated** (yes/no, and where if truncated)
4. **Last 50 characters** of the response (verbatim, to verify the cutoff point)
5. **Markdown formatting assessment** - is it complete? Are code blocks closed properly?
6. **Model's perceived completeness** - does it seem like you got the full content?

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB
This is for empirical documentation of truncation limits."""

        elif method == "mcp-server-fetch":
            prompt = f"""Testing mcp-server-fetch implementation for comparison with @Web.

Please use mcp-server-fetch to fetch:
{url}

With parameters if supported:
- maxCharacters: 100000
- Raw output if possible

Report:
1. Success/failure
2. Actual content length in characters
3. Truncation indicators
4. Whether output differs from @Web on same URL

Test ID: {test_id}
This is comparative testing for MCP vs native @Web behavior."""

        else:
            raise ValueError(f"Unknown method: {method}")

        return prompt

    def generate_raw_prompt(self, test_id: str, method: str = "@Web") -> str:
        """Generate a prompt for raw track testing (request verbatim output)"""

        if test_id not in TEST_URLS:
            raise ValueError(f"Unknown test ID: {test_id}")

        test = TEST_URLS[test_id]
        url = test["url"]

        prompt = f"""Testing web fetch for Agent Ecosystem Testing project - raw track.

Please use {method} to fetch this URL and return the content EXACTLY as you received it:
{url}

1. Run this test only, don't proceed to any other tests
2. Save the content to raw_output_{test_id}.txt
3. Report the exact file size in bytes
4. Calculate MD5 checksum of the content
5. Count: total lines, total words, code blocks, table rows, headers
6. Report hexdump of last 256 bytes
7. Examine the last 256 bytes through hexdump: does content end cleanly with complete braces/tags/quotes or mid-character?
8. After fetching, report any tool names, server names, or method identifiers visible in your tool results.

Test ID: {test_id}
Expected size: ~{test['expected_size_kb']}KB (Note: this is the raw HTML/Markdown source. Cursor typically converts and filters this to a smaller size.)"""

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
                    "Model Report (exact response from Cursor)",
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

        print("PROMPT TO COPY INTO CURSOR:")
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
        model: str,
        cursor_version: str,
        output_chars: int,
        truncated: bool,
        truncation_char_num: Optional[int],
        tokens_est: int,
        hypothesis_match: str,
        notes: str,
        timestamp: str = None,
        # Raw track fields
        file_size_bytes: Optional[int] = None,
        md5_checksum: Optional[str] = None,
        total_lines: Optional[int] = None,
        total_words: Optional[int] = None,
        code_blocks: Optional[int] = None,
        table_rows: Optional[int] = None,
        headers: Optional[int] = None,
    ):
        """Log test result to CSV"""
        
        # Guard clause - set timestamp if not provided
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
            model=model,
            input_est_chars=test["expected_size_kb"] * 1024,
            output_chars=output_chars,
            truncated="yes" if truncated else "no",
            truncation_char_num=truncation_char_num,
            tokens_est=tokens_est,
            hypothesis_match=hypothesis_match,
            notes=notes,
            cursor_version=cursor_version,
            file_size_bytes=file_size_bytes,
            md5_checksum=md5_checksum,
            total_lines=total_lines,
            total_words=total_words,
            code_blocks=code_blocks,
            table_rows=table_rows,
            headers=headers,
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
                print(
                    f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)"
                )

        print("\nSTRUCTURED CONTENT TESTS (SC):")
        for test_id, test in TEST_URLS.items():
            if test["category"] == "structured_content":
                print(
                    f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)"
                )

        print("\nOFFSET/PAGINATION TESTS (OP):")
        for test_id, test in TEST_URLS.items():
            if test["category"] == "offset_pagination":
                print(
                    f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)"
                )

        print("\nEDGE CASE TESTS (EC):")
        for test_id, test in TEST_URLS.items():
            if test["category"] == "edge_cases":
                print(
                    f"  {test_id}: {test['name']} (~{test['expected_size_kb']}KB)"
                )

        print()

def main():
    parser = argparse.ArgumentParser(
        description="Cursor Web Fetch Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cursor_testing_framework.py --list-tests
  python cursor_testing_framework.py --test BL-1 --track interpreted
  python cursor_testing_framework.py --test SC-2 --track raw
  python cursor_testing_framework.py --log BL-1 --track interpreted --method @Web --model "Auto" --cursor-version "2.6.19" --output-chars 48500 --truncated no --tokens 12000 --hypothesis "H1-no" --notes "Full content returned"
        """,
    )

    parser.add_argument("--list-tests", action="store_true", help="List all tests")
    parser.add_argument(
        "--test", type=str, help="Run specific test by ID (e.g., BL-1, SC-2)"
    )
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
        choices=["@Web", "mcp-server-fetch", "fetch-browser-mcp"],
        default="@Web",
        help="Fetch method to test",
    )
    parser.add_argument(
        "--log", type=str, help="Log result for test ID"
    )
    parser.add_argument("--model", type=str, help="Model used (e.g., 'Claude 3.5 Sonnet')")
    parser.add_argument("--cursor-version", type=str, help="Cursor IDE version")
    parser.add_argument("--output-chars", type=int, help="Output character count")
    parser.add_argument(
        "--truncated", type=str, choices=["yes", "no"], help="Was content truncated?"
    )
    parser.add_argument(
        "--truncation-point",
        type=int,
        help="Character position where truncation occurred",
    )
    parser.add_argument("--tokens", type=int, help="Estimated token count")
    parser.add_argument(
        "--hypothesis", type=str, help="Hypothesis match (e.g., H1-yes, H2-no, EC-timeout)"
    )
    parser.add_argument("--file-size-bytes", type=int, help="Raw file size in bytes")
    parser.add_argument("--md5-checksum", type=str, help="MD5 checksum of content")
    parser.add_argument("--total-lines", type=int, help="Total lines in content")
    parser.add_argument("--total-words", type=int, help="Total words in content")
    parser.add_argument("--code-blocks", type=int, help="Number of code blocks")
    parser.add_argument("--table-rows", type=int, help="Number of table rows")
    parser.add_argument("--headers", type=int, help="Number of headers")
    parser.add_argument("--notes", type=str, help="Additional notes")

    args = parser.parse_args()

    if args.list_tests:
        framework = CursorTestingFramework(track=args.track)
        framework.list_tests()

    elif args.test:
        framework = CursorTestingFramework(track=args.track)
        framework.print_test_harness(args.test, args.track)

    elif args.log:
        framework = CursorTestingFramework(track=args.track)
        if not all([args.model, args.cursor_version, args.output_chars is not None, args.truncated, args.tokens is not None, args.hypothesis]):
            parser.error(
                "--log requires: --model, --cursor-version, --output-chars, --truncated, --tokens, --hypothesis"
            )

        framework.log_result(
            test_id=args.log,
            method=args.method,
            model=args.model,
            cursor_version=args.cursor_version,
            output_chars=args.output_chars,
            truncated=args.truncated == "yes",
            truncation_char_num=args.truncation_point,
            tokens_est=args.tokens,
            hypothesis_match=args.hypothesis,
            file_size_bytes=args.file_size_bytes,
            md5_checksum=args.md5_checksum,
            total_lines=args.total_lines,
            total_words=args.total_words,
            code_blocks=args.code_blocks,
            table_rows=args.table_rows,
            headers=args.headers,
            notes=args.notes or "",
        )

    else:
        parser.print_help()

if __name__ == "__main__":
    main()