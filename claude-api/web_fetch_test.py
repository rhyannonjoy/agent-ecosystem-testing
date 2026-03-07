"""
Claude API web fetch tool, Claude-interpreted content analysis
=====================================
Tests the behavior of Anthropic's API-level web fetch tool to document
platform limits for the Agent-Friendly Docs Spec.

See: https://github.com/agent-ecosystem/agent-docs-spec

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python claude-api/web_fetch_test.py

Workflow:
1. Call the API with the web fetch tool enabled
2. Give Claude a URL and ask it to fetch the page and describe what it got
3. Claude fetches the page, then reports back what it received
4. Results are saved to `claude-api/results/`
"""

import anthropic
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Test URLs
# ---------------------------------------------------------------------------

# Short page with heavy inline CSS before content (the same page Dachary used).
# HTML version: lots of CSS upfront, actual docs content buried ~87% down.
SHORT_PAGE_HTML = "https://www.mongodb.com/docs/manual/reference/change-events/create/"

# Markdown version of the same page — should be dramatically smaller.
SHORT_PAGE_MD = "https://www.mongodb.com/docs/manual/reference/change-events/create.md"

# Long tabbed tutorial page — 6,400+ lines of markdown when flattened.
LONG_PAGE_HTML = "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/"
LONG_PAGE_MD   = "https://www.mongodb.com/docs/atlas/atlas-search/tutorial.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Run: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def build_tool(max_content_tokens: int | None = None) -> dict:
    """Return the web_fetch tool definition, optionally with a token limit."""
    tool = {
        "type": "web_fetch_20250910",
        "name": "web_fetch",
    }
    if max_content_tokens is not None:
        tool["max_content_tokens"] = max_content_tokens
    return tool


def fetch_url(
    client: anthropic.Anthropic,
    url: str,
    max_content_tokens: int | None = None,
    ask: str | None = None,
) -> dict:
    """
    Call the API with the web_fetch tool for a single URL.
    Returns a dict with usage stats and content summary.
    """
    user_message = ask or (
        f"Please fetch this URL and tell me: "
        f"(1) how many characters of content you received, "
        f"(2) what the first 200 characters of content are, "
        f"(3) whether the content appears to be CSS/boilerplate or actual documentation, "
        f"(4) approximately what fraction of the page you estimate you received. "
        f"URL: {url}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_message}],
        tools=[build_tool(max_content_tokens)],
        extra_headers={"anthropic-beta": "web-fetch-2025-09-10"},
    )

    # Extract usage
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "web_fetch_requests": getattr(
            getattr(response.usage, "server_tool_use", None),
            "web_fetch_requests",
            "unavailable"
        ),
    }

    # Extract Claude's text response and any fetch result metadata
    text_response = ""
    fetch_content_preview = ""
    fetch_content_length = None

    for block in response.content:
        if block.type == "text":
            text_response = block.text
        elif block.type == "web_fetch_tool_result":
            # Try to get content from the fetch result
            try:
                content_data = block.content.get("content", {}) if isinstance(block.content, dict) else {}
                source = content_data.get("source", {})
                raw = source.get("data", "")
                fetch_content_length = len(raw)
                fetch_content_preview = raw[:300]
            except Exception:
                pass

    return {
        "url": url,
        "max_content_tokens_param": max_content_tokens,
        "usage": usage,
        "fetch_content_length_chars": fetch_content_length,
        "fetch_content_preview": fetch_content_preview,
        "claude_assessment": text_response,
        "stop_reason": response.stop_reason,
    }


def save_result(result: dict, label: str):
    """Save a result dict to claude-api/results/<timestamp>_<label>.json"""
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"{timestamp}_{label}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved to: {filename}")


def print_result(result: dict):
    print(f"  URL:                   {result['url']}")
    print(f"  max_content_tokens:    {result['max_content_tokens_param'] or '(not set)'}")
    print(f"  input_tokens:          {result['usage']['input_tokens']}")
    print(f"  output_tokens:         {result['usage']['output_tokens']}")
    if result["fetch_content_length_chars"]:
        print(f"  fetch content length:  {result['fetch_content_length_chars']} chars")
    print(f"  Claude's assessment:")
    for line in result["claude_assessment"].splitlines():
        print(f"    {line}")


def save_markdown_report(results: list[dict], run_timestamp: str):
    """
    Generate a human-readable markdown summary of all test results
    and save it to claude-api/results/<timestamp>_summary.md
    """
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    filename = results_dir / f"{run_timestamp}_summary.md"

    r1, r2, r3, r4 = results

    t1 = r1["usage"]["input_tokens"]
    t2 = r2["usage"]["input_tokens"]
    diff = t1 - t2
    pct = (diff / t1 * 100) if t1 else 0

    lines = [
        "# Claude API `web_fetch` Test Results",
        "",
        f"**Run at:** {run_timestamp}  ",
        f"**Model:** claude-sonnet-4-6  ",
        f"**Beta header:** web-fetch-2025-09-10  ",
        "",
        "---",
        "",
        "## Token Usage Summary",
        "",
        "| Test | URL | max_content_tokens | input_tokens | output_tokens |",
        "|------|-----|--------------------|--------------|---------------|",
        f"| 1: Short HTML | {r1['url']} | not set | {r1['usage']['input_tokens']} | {r1['usage']['output_tokens']} |",
        f"| 2: Short Markdown | {r2['url']} | not set | {r2['usage']['input_tokens']} | {r2['usage']['output_tokens']} |",
        f"| 3: Long HTML | {r3['url']} | not set | {r3['usage']['input_tokens']} | {r3['usage']['output_tokens']} |",
        f"| 4: Long HTML - limited | {r4['url']} | 5000 | {r4['usage']['input_tokens']} | {r4['usage']['output_tokens']} |",
        "",
        "---",
        "",
        "## HTML vs Markdown Comparison - short page",
        "",
        f"- **HTML input_tokens**: {t1}",
        f"- **Markdown input_tokens**: {t2}",
        f"- **Difference**: {diff} tokens - **{pct:.1f}% reduction** with Markdown",
        "",
        "---",
        "",
    ]

    test_labels = [
        "Test 1: Short HTML page, no token limit",
        "Test 2: Short Markdown page, no token limit",
        "Test 3: Long HTML page, no token limit",
        "Test 4: Long HTML page, max_content_tokens=5000",
    ]

    for label, result in zip(test_labels, results):
        lines += [
            f"## {label}",
            "",
            f"**URL**: {result['url']}  ",
            f"**max_content_tokens**: {result['max_content_tokens_param'] or 'not set'}  ",
            f"**input_tokens**: {result['usage']['input_tokens']}  ",
            f"**output_tokens**: {result['usage']['output_tokens']}  ",
            "",
            "**Claude's Assessment**:",
            "",
            result["claude_assessment"],
            "",
            "---",
            "",
        ]

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"  Markdown report saved to: {filename}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_1_short_html_no_limit(client):
    """Short page, HTML, no max_content_tokens — discover default behavior."""
    print("\n" + "="*60)
    print("TEST 1: Short HTML page, no token limit")
    print("="*60)
    result = fetch_url(client, SHORT_PAGE_HTML, max_content_tokens=None)
    print_result(result)
    save_result(result, "test1_short_html_no_limit")
    return result


def test_2_short_markdown_no_limit(client):
    """Same short page but markdown URL — compare token footprint."""
    print("\n" + "="*60)
    print("TEST 2: Short Markdown page, no token limit")
    print("="*60)
    result = fetch_url(client, SHORT_PAGE_MD, max_content_tokens=None)
    print_result(result)
    save_result(result, "test2_short_markdown_no_limit")
    return result


def test_3_long_html_no_limit(client):
    """Long tabbed tutorial, HTML, no token limit — how much does it get?"""
    print("\n" + "="*60)
    print("TEST 3: Long HTML page, no token limit")
    print("="*60)
    result = fetch_url(
        client,
        LONG_PAGE_HTML,
        max_content_tokens=None,
        ask=(
            f"Please fetch this URL. Then tell me: "
            f"(1) approximately how many characters of content you received, "
            f"(2) what drivers or platforms are covered in the content you can see "
            f"(this is a tabbed tutorial with sections for mongosh, Python, Node.js, etc.), "
            f"(3) whether the content appears truncated before reaching all driver variants. "
            f"URL: {LONG_PAGE_HTML}"
        ),
    )
    print_result(result)
    save_result(result, "test3_long_html_no_limit")
    return result


def test_4_long_html_explicit_limit(client):
    """Long page with max_content_tokens=5000 — verify parameter works."""
    print("\n" + "="*60)
    print("TEST 4: Long HTML page, max_content_tokens=5000")
    print("="*60)
    result = fetch_url(
        client,
        LONG_PAGE_HTML,
        max_content_tokens=5000,
        ask=(
            f"Please fetch this URL with a 5000-token limit. Then tell me: "
            f"(1) how much content you received, "
            f"(2) does the content end cleanly or mid-sentence, "
            f"(3) what is the last thing you can see in the content. "
            f"URL: {LONG_PAGE_HTML}"
        ),
    )
    print_result(result)
    save_result(result, "test4_long_html_explicit_limit")
    return result


def test_5_compare_html_vs_md_tokens(result1, result2):
    """Print a comparison summary of Tests 1 and 2."""
    print("\n" + "="*60)
    print("COMPARISON: HTML vs Markdown token usage (short page)")
    print("="*60)
    t1 = result1["usage"]["input_tokens"]
    t2 = result2["usage"]["input_tokens"]
    if t1 and t2:
        diff = t1 - t2
        pct = (diff / t1 * 100) if t1 else 0
        print(f"  HTML input_tokens:     {t1}")
        print(f"  Markdown input_tokens: {t2}")
        print(f"  Difference:            {diff} tokens ({pct:.1f}% reduction with markdown)")
    else:
        print("  Could not compare — one or both tests did not return usage data.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Claude API web_fetch empirical tests")
    print("Model: claude-sonnet-4-6")
    print("Beta header: web-fetch-2025-09-10")
    print(f"Run at: {run_timestamp}")

    client = make_client()

    r1 = test_1_short_html_no_limit(client)
    r2 = test_2_short_markdown_no_limit(client)
    r3 = test_3_long_html_no_limit(client)
    r4 = test_4_long_html_explicit_limit(client)

    test_5_compare_html_vs_md_tokens(r1, r2)

    print("\n" + "="*60)
    print("Generating markdown report...")
    save_markdown_report([r1, r2, r3, r4], run_timestamp)

    print("\nAll tests complete. Results saved to claude-api/results/")