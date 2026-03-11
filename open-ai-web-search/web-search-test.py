"""
OpenAI web search tool, ChatGPT-interpreted analysis
=====================================================
Companion to `web_search_test_raw.py`. This script asks the model to reflect
on what it retrieved from each query — characterizing search behavior,
result quality, and failure reasons in its own words.

This captures the model's self-perception of the retrieval, which may differ
from what the raw tool call items report in the raw track.

Uses the Chat Completions API with a dedicated search model
(gpt-4o-search-preview). This model ALWAYS performs a web search before
responding — search is implicit and cannot be disabled.

Usage:
    source .env
    python open-ai-web-search/web_search_test.py

Workflow:
1. Call the Chat Completions API with gpt-4o-search-preview
2. Give the model a detailed prompt asking it to describe what it retrieved —
   result quality, recency, completeness, any failures
3. The model always searches before generating a response; no tool plumbing
   is exposed to the caller
4. Capture the model's full text response as the interpreted finding
5. Also capture inline url_citation annotations from message.annotations
   for cross-referencing against the raw track
6. The gap between the model's self-report and raw citation counts is itself
   a finding — discrepancies belong in the spec
7. Results are saved to open-ai-web-search/results/chatgpt-interpreted/
"""

import os
import json
import time
import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-4o-search-preview"

# Each run gets its own timestamped subdirectory — matches the gemini-url-context track convention.
# Format: results/chatgpt-interpreted/YYYY-MM-DDTHH-MM/
_RUN_TS = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M")
RESULTS_DIR = Path(f"open-ai-web-search/results/chatgpt-interpreted/{_RUN_TS}")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Chat Completions search model has its own rate limits.
# Set to 0 if you are on a tier without rate concerns.
RATE_LIMIT_SLEEP_SECONDS = 5

# ---------------------------------------------------------------------------
# Test queries — mirrors progressive complexity used in url_context_test.py
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "id": "test_1_live_data",
        "label": "Live data (should always search)",
        "prompt": (
            "Search for the current price of Bitcoin in USD. "
            "Tell me: what did you find? How recent was the data? "
            "Did anything appear to be missing or stale?"
        ),
    },
    {
        "id": "test_2_recent_event",
        "label": "Recent event",
        "prompt": (
            "Search for who won the most recent Super Bowl. "
            "Tell me: what did you find? How confident are you in the recency? "
            "Describe the quality of the search results you drew from."
        ),
    },
    {
        "id": "test_3_static_fact",
        "label": "Static fact (may not need search)",
        "prompt": (
            "What is the capital of France? "
            "Tell me: did you search for this or answer from memory? "
            "If you searched, what did you find and was it necessary?"
        ),
    },
    {
        "id": "test_4_open_research",
        "label": "Open-ended research query",
        "prompt": (
            "Search for the latest developments in EU AI regulation. "
            "Tell me: how many distinct sources did you draw from? "
            "How recent were they? Was any information contradictory across sources?"
        ),
    },
    {
        "id": "test_5_ambiguous_query",
        "label": "Ambiguous query (disambiguation behavior)",
        "prompt": (
            "Search for 'Python release'. "
            "Tell me: how did you interpret this query? "
            "Did you search for the programming language, the animal, or both? "
            "Describe what you found and how you resolved the ambiguity."
        ),
    },
    {
        "id": "test_6_search_context_low",
        "label": "search_context_size: low",
        "prompt": (
            "Search for recent AI safety news. "
            "Tell me: how comprehensive were your results? "
            "How many sources did you reference? Did anything feel incomplete?"
        ),
        "web_search_options": {"search_context_size": "low"},
    },
    {
        "id": "test_7_search_context_high",
        "label": "search_context_size: high",
        "prompt": (
            "Search for recent AI safety news. "
            "Tell me: how comprehensive were your results? "
            "How many sources did you reference? Did anything feel incomplete?"
        ),
        "web_search_options": {"search_context_size": "high"},
    },
    {
        "id": "test_8_multi_hop",
        "label": "Multi-hop research (requires synthesizing across sources)",
        "prompt": (
            "Search for which countries have passed national AI laws, "
            "and for each one, search for when the law took effect. "
            "Tell me: how many sources did you draw from? "
            "Were you able to find dates for all countries? "
            "What gaps or uncertainties remain?"
        ),
    },
]


def run_test(test: dict) -> dict:
    """Run a single ChatGPT-interpreted web search test."""
    print(f"\nRunning: {test['id']} — {test['label']}")

    kwargs = {
        "model": MODEL,
        "messages": [{"role": "user", "content": test["prompt"]}],
    }
    if "web_search_options" in test:
        kwargs["web_search_options"] = test["web_search_options"]

    try:
        t0 = time.monotonic()
        response = client.chat.completions.create(**kwargs)
        latency_ms = round((time.monotonic() - t0) * 1000, 1)

        message = response.choices[0].message
        text = message.content or ""
        finish_reason = response.choices[0].finish_reason

        # Extract inline url_citation annotations
        citations = []
        if hasattr(message, "annotations") and message.annotations:
            for ann in message.annotations:
                if ann.type == "url_citation":
                    citations.append({
                        "url": ann.url_citation.url,
                        "title": ann.url_citation.title,
                        "start_index": ann.url_citation.start_index,
                        "end_index": ann.url_citation.end_index,
                    })

        usage = response.usage
        usage_dict = {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }

        result = {
            "test_id": test["id"],
            "label": test["label"],
            "model": MODEL,
            "track": "chatgpt-interpreted",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "prompt": test["prompt"],
            "web_search_options": test.get("web_search_options"),
            "interpreted_response": text,
            "citations": citations,
            "citation_count": len(citations),
            "finish_reason": finish_reason,
            "latency_ms": latency_ms,
            "usage": usage_dict,
            "error": None,
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        result = {
            "test_id": test["id"],
            "label": test["label"],
            "model": MODEL,
            "track": "chatgpt-interpreted",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "prompt": test["prompt"],
            "web_search_options": test.get("web_search_options"),
            "interpreted_response": None,
            "citations": [],
            "citation_count": 0,
            "finish_reason": None,
            "latency_ms": None,
            "usage": {},
            "error": str(e),
        }

    out_path = RESULTS_DIR / f"{test['id']}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved → {out_path}")
    print(f"  Citations: {result['citation_count']} | Latency: {result['latency_ms']}ms | Finish: {result['finish_reason']}")

    return result


def main():
    print(f"=== OpenAI Web Search Test: ChatGPT-interpreted track ===")
    print(f"Model: {MODEL}")
    print(f"Results dir: {RESULTS_DIR}\n")

    all_results = []
    for i, test in enumerate(TEST_CASES):
        if i > 0 and RATE_LIMIT_SLEEP_SECONDS > 0:
            print(f"  Waiting {RATE_LIMIT_SLEEP_SECONDS}s (rate limit)...")
            time.sleep(RATE_LIMIT_SLEEP_SECONDS)
        result = run_test(test)
        all_results.append(result)

    summary_path = RESULTS_DIR / "_summary.json"
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll results saved to {summary_path}")

    print("\n--- Quick Results ---")
    print(f"{'Test ID':<35} {'Citations':>9} {'Latency(ms)':>11} {'Tokens':>7} {'Error'}")
    print("-" * 80)
    for r in all_results:
        tokens = r.get("usage", {}).get("total_tokens", "—")
        error = r.get("error") or ""
        print(
            f"{r['test_id']:<35} "
            f"{r['citation_count']:>9} "
            f"{str(r['latency_ms'] or '—'):>11} "
            f"{str(tokens):>7} "
            f"{error[:30]}"
        )


if __name__ == "__main__":
    main()