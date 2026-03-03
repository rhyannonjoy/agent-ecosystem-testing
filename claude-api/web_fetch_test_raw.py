"""
Claude API web_fetch raw content analysis
==========================================
Companion to web_fetch_test.py. Instead of asking Claude to describe
what it received, this script inspects the raw web_fetch_tool_result
block directly and measures the content programmatically.

This gives objective, reproducible measurements that don't depend on
Claude's interpretation or estimation.

Usage:
    source .env
    python claude-api/web_fetch_raw.py

Results are saved to claude-api/results/.
"""

import anthropic
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Test URLs — same as web_fetch_test.py for direct comparison
# ---------------------------------------------------------------------------

SHORT_PAGE_HTML = "https://www.mongodb.com/docs/manual/reference/change-events/create/"
SHORT_PAGE_MD   = "https://www.mongodb.com/docs/manual/reference/change-events/create.md"
LONG_PAGE_HTML  = "https://www.mongodb.com/docs/atlas/atlas-search/tutorial/"

CSS_INDICATORS = [
    "@font-face", "@media", "font-family", "background-color",
    "margin:", "padding:", "border:", ".css", "px;", "rem;",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Run: source .env")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def fetch_raw(
    client: anthropic.Anthropic,
    url: str,
    max_content_tokens: int | None = None,
) -> dict:
    """
    Fetch a URL and extract the raw content directly from the
    web_fetch_tool_result block, without asking Claude to interpret it.
    """
    tool = {"type": "web_fetch_20250910", "name": "web_fetch"}
    if max_content_tokens is not None:
        tool["max_content_tokens"] = max_content_tokens

    # Minimal prompt — we just need Claude to trigger the fetch.
    # All analysis happens in Python below.
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=128,
        messages=[{"role": "user", "content": f"Fetch this URL: {url}"}],
        tools=[tool],
        extra_headers={"anthropic-beta": "web-fetch-2025-09-10"},
    )

    # --- Extract raw content from the fetch result block ---
    raw_content = None
    fetch_error = None

    for block in response.content:
        if block.type == "web_fetch_tool_result":
            try:
                raw_content = block.content.content.source.data
            except AttributeError:
                fetch_error = "could not extract content — unexpected response structure"

    # --- Programmatic analysis ---
    analysis = analyze_content(raw_content) if raw_content is not None else None

    return {
        "url": url,
        "max_content_tokens_param": max_content_tokens,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "web_fetch_requests": getattr(
                getattr(response.usage, "server_tool_use", None),
                "web_fetch_requests",
                "unavailable"
            ),
        },
        "fetch_error": fetch_error,
        "raw_content_chars": len(raw_content) if raw_content is not None else None,
        "analysis": analysis,
    }


def analyze_content(raw: str) -> dict:
    """
    Programmatically analyze raw fetched content.
    No Claude interpretation — just Python string operations.
    """
    if not raw:
        return {"error": "empty content"}

    total_chars = len(raw)
    first_500 = raw[:500]
    last_200 = raw[-200:]

    # Count how many CSS indicator strings appear in the first 2000 chars
    opening = raw[:2000]
    css_hits = [ind for ind in CSS_INDICATORS if ind in opening]

    # Find where the first heading or paragraph-like content appears
    first_heading = raw.find("\n#")
    first_paragraph_hint = min(
        (raw.find(marker) for marker in ["\n\n", ". ", "The ", "A "] if raw.find(marker) != -1),
        default=-1
    )

    # Check if content ends mid-word or mid-sentence (truncation signal)
    last_char = raw[-1] if raw else ""
    ends_cleanly = last_char in {".", "\n", "]", ")", "}"}

    # Rough estimate: what fraction of chars is before the first heading
    boilerplate_estimate = None
    if first_heading > 0:
        boilerplate_estimate = round(first_heading / total_chars * 100, 1)

    return {
        "total_chars": total_chars,
        "first_500_chars": first_500,
        "last_200_chars": last_200,
        "css_indicators_in_first_2000_chars": css_hits,
        "css_indicator_count": len(css_hits),
        "first_heading_position": first_heading,
        "boilerplate_pct_before_first_heading": boilerplate_estimate,
        "ends_cleanly": ends_cleanly,
        "last_char": repr(last_char),
    }


def print_analysis(result: dict):
    url = result["url"]
    limit = result["max_content_tokens_param"] or "not set"
    print(f"  URL:                    {url}")
    print(f"  max_content_tokens:     {limit}")
    print(f"  input_tokens:           {result['usage']['input_tokens']}")

    if result["fetch_error"]:
        print(f"  FETCH ERROR:            {result['fetch_error']}")
        return

    if result["raw_content_chars"] is None:
        print("  raw content:            (could not extract from response)")
        return

    a = result["analysis"]
    print(f"  raw_content_chars:      {result['raw_content_chars']}")
    print(f"  css_indicators_found:   {a['css_indicator_count']} — {a['css_indicators_in_first_2000_chars']}")
    print(f"  first_heading_at_char:  {a['first_heading_position']}")
    print(f"  boilerplate_before_h1:  {a['boilerplate_pct_before_first_heading']}%")
    print(f"  ends_cleanly:           {a['ends_cleanly']} (last char: {a['last_char']})")
    print(f"  --- first 500 chars ---")
    print(a["first_500_chars"])
    print(f"  --- last 200 chars ---")
    print(a["last_200_chars"])


def save_results(all_results: list[dict], run_timestamp: str):
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Save combined JSON
    json_file = results_dir / f"{run_timestamp}_raw_results.json"
    with open(json_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  JSON saved to: {json_file}")

    # Save markdown report
    md_file = results_dir / f"{run_timestamp}_raw_summary.md"
    with open(md_file, "w") as f:
        f.write(build_markdown(all_results, run_timestamp))
    print(f"  Markdown saved to: {md_file}")


def build_markdown(all_results: list[dict], run_timestamp: str) -> str:
    labels = [
        "Test 1: Short HTML, no token limit",
        "Test 2: Short Markdown, no token limit",
        "Test 3: Long HTML, no token limit",
        "Test 4: Long HTML, max_content_tokens=5000",
    ]

    lines = [
        "# Claude API `web_fetch` Raw Content Analysis",
        "",
        f"**Run at:** {run_timestamp}  ",
        f"**Model:** claude-sonnet-4-6  ",
        f"**Method:** programmatic — raw content extracted directly from `web_fetch_tool_result` block  ",
        "",
        "---",
        "",
        "## Measurements Summary",
        "",
        "| Test | max_content_tokens | input_tokens | raw_content_chars | css_indicators | ends_cleanly |",
        "|------|--------------------|--------------|-------------------|----------------|--------------|",
    ]

    for label, r in zip(labels, all_results):
        if r["fetch_error"] or r["analysis"] is None:
            lines.append(f"| {label} | {r['max_content_tokens_param'] or 'not set'} | {r['usage']['input_tokens']} | ERROR | — | — |")
        else:
            a = r["analysis"]
            lines.append(
                f"| {label} | {r['max_content_tokens_param'] or 'not set'} "
                f"| {r['usage']['input_tokens']} "
                f"| {a['total_chars']} "
                f"| {a['css_indicator_count']} "
                f"| {a['ends_cleanly']} |"
            )

    lines += ["", "---", ""]

    for label, r in zip(labels, all_results):
        lines += [
            f"## {label}",
            "",
            f"**URL**: {r['url']}  ",
            f"**max_content_tokens**: {r['max_content_tokens_param'] or 'not set'}  ",
            f"**input_tokens**: {r['usage']['input_tokens']}  ",
            "",
        ]

        if r["fetch_error"]:
            lines += [f"**Fetch error**: `{r['fetch_error']}`", "", "---", ""]
            continue

        if r["analysis"] is None:
            lines += ["Could not extract raw content from response.", "", "---", ""]
            continue

        a = r["analysis"]
        lines += [
            f"**raw_content_chars**: {a['total_chars']}  ",
            f"**css_indicators_in_first_2000_chars**: {a['css_indicator_count']} — `{a['css_indicators_in_first_2000_chars']}`  ",
            f"**first_heading_position**: char {a['first_heading_position']}  ",
            f"**boilerplate_before_first_heading**: {a['boilerplate_pct_before_first_heading']}%  ",
            f"**ends_cleanly**: {a['ends_cleanly']} (last char: {a['last_char']})  ",
            "",
            "**First 500 characters:**",
            "",
            "```",
            a["first_500_chars"],
            "```",
            "",
            "**Last 200 characters:**",
            "",
            "```",
            a["last_200_chars"],
            "```",
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Claude API web_fetch — raw content analysis")
    print("Model: claude-sonnet-4-6")
    print("Beta header: web-fetch-2025-09-10")
    print(f"Run at: {run_timestamp}")

    client = make_client()

    tests = [
        (SHORT_PAGE_HTML, None,  "Short HTML, no token limit"),
        (SHORT_PAGE_MD,   None,  "Short Markdown, no token limit"),
        (LONG_PAGE_HTML,  None,  "Long HTML, no token limit"),
        (LONG_PAGE_HTML,  5000,  "Long HTML, max_content_tokens=5000"),
    ]

    all_results = []
    for url, limit, label in tests:
        print(f"\n{'='*60}")
        print(f"{label}")
        print("="*60)
        result = fetch_raw(client, url, max_content_tokens=limit)
        print_analysis(result)
        all_results.append(result)

    save_results(all_results, run_timestamp)
    print("\nAll tests complete.")