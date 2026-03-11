"""
OpenAI web search tool, raw content analysis
=============================================
Companion to `web_search_test.py`. Instead of asking the model to describe
what it retrieved, this script inspects the raw tool call items and usage
metadata directly and measures outcomes programmatically.
This gives objective, reproducible measurements that don't depend on
the model's interpretation or estimation.

Uses the Responses API with web_search_preview as an explicit tool on a
base model (gpt-4o). The model decides whether to invoke the tool depending
on the query — invocation is NOT guaranteed.

Usage:
    source .env
    python open-ai-web-search/web_search_test_raw.py

Workflow:
1. Call the Responses API with gpt-4o + web_search_preview tool enabled
2. Give the model a minimal prompt — just enough to trigger retrieval
3. The model may or may not invoke web_search_preview depending on the query
4. Extract raw outcomes directly from response.output items:
   - web_search_call items: type, action.query (the internal search query issued)
   - message items: output_text
5. Extract sources list from response.sources (all URLs consulted, not just cited)
6. Extract token accounting from response.usage
7. Run all analysis in Python: tool invocation flag, source counts, latency
8. The model never interprets or reflects on the retrieval results
9. Results are saved to open-ai-web-search/results/raw/
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
MODEL = "gpt-4o"

# Each run gets its own timestamped subdirectory — matches the gemini-url-context track convention.
# Format: results/raw/YYYY-MM-DDTHH-MM/
_RUN_TS = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M")
RESULTS_DIR = Path(f"open-ai-web-search/results/raw/{_RUN_TS}")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Set to 0 if you are on a tier without rate concerns.
RATE_LIMIT_SLEEP_SECONDS = 5

# ---------------------------------------------------------------------------
# Minimal prompts — we want signal, not model verbosity.
# The raw track uses max_output_tokens=256 to minimize cost and noise,
# mirroring the approach used in url_context_test_raw.py.
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "id": "test_1_live_data",
        "label": "Live data (should always invoke tool)",
        "query": "What is the current price of Bitcoin in USD?",
        "search_context_size": "medium",
    },
    {
        "id": "test_2_recent_event",
        "label": "Recent event",
        "query": "Who won the most recent Super Bowl?",
        "search_context_size": "medium",
    },
    {
        "id": "test_3_static_fact",
        "label": "Static fact (tool invocation may be skipped)",
        "query": "What is the capital of France?",
        "search_context_size": "medium",
    },
    {
        "id": "test_4_trivial_math",
        "label": "Trivial fact — no search expected",
        "query": "What is 2 + 2?",
        "search_context_size": "medium",
    },
    {
        "id": "test_5_open_research",
        "label": "Open-ended research query",
        "query": "Summarize the latest developments in EU AI regulation.",
        "search_context_size": "medium",
    },
    {
        "id": "test_6_context_size_low",
        "label": "search_context_size: low",
        "query": "What are the latest AI safety news headlines?",
        "search_context_size": "low",
    },
    {
        "id": "test_7_context_size_high",
        "label": "search_context_size: high",
        "query": "What are the latest AI safety news headlines?",
        "search_context_size": "high",
    },
    {
        "id": "test_8_domain_filter_allowed",
        "label": "Domain filter: allow-list (reuters.com, apnews.com)",
        "query": "Latest news on US Federal Reserve interest rate decisions.",
        "search_context_size": "medium",
        "domain_filter": {
            "type": "domain",
            "domains": ["reuters.com", "apnews.com"],
        },
    },
    {
        "id": "test_9_domain_filter_blocked",
        "label": "Domain filter: block-list (wikipedia.org)",
        "query": "History of the European Union.",
        "search_context_size": "medium",
        "domain_filter": {
            "type": "domain",
            "exclude_domains": ["wikipedia.org"],
        },
    },
    {
        "id": "test_10_ambiguous_query",
        "label": "Ambiguous query",
        "query": "Python release",
        "search_context_size": "medium",
    },
]


# ---------------------------------------------------------------------------
# Raw measurement helpers — all Python, no model estimates
# ---------------------------------------------------------------------------

def extract_output_items(output) -> dict:
    """Parse response.output items into structured measurements."""
    tool_invoked = False
    search_queries_issued = []
    response_text = ""

    for item in output:
        if item.type == "web_search_call":
            tool_invoked = True
            action = getattr(item, "action", None)
            if action:
                q = getattr(action, "query", None) or str(action)
                search_queries_issued.append(q)
        elif item.type == "message":
            for part in getattr(item, "content", []):
                if hasattr(part, "text"):
                    response_text += part.text

    return {
        "tool_invoked": tool_invoked,
        "search_queries_issued": search_queries_issued,
        "search_call_count": len(search_queries_issued),
        "response_text": response_text,
        "response_text_char_count": len(response_text),
    }


def extract_sources(response) -> list[dict]:
    sources = []
    raw_sources = getattr(response, "sources", None) or []
    for src in raw_sources:
        sources.append({
            "url": getattr(src, "url", None),
            "title": getattr(src, "title", None),
        })
    return sources


def extract_usage(response) -> dict:
    usage = getattr(response, "usage", None)
    if not usage:
        return {}
    return {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def check_domain_filter_respected(sources: list[dict], domain_filter: dict | None) -> dict | None:
    """Programmatically verify whether domain filtering was respected."""
    if not domain_filter or not sources:
        return None

    urls = [s.get("url", "") or "" for s in sources]

    if "domains" in domain_filter:
        allowed = domain_filter["domains"]
        violations = [u for u in urls if u and not any(d in u for d in allowed)]
        return {
            "filter_type": "allow",
            "allowed_domains": allowed,
            "violation_count": len(violations),
            "violations": violations[:5],
            "filter_respected": len(violations) == 0,
        }

    if "exclude_domains" in domain_filter:
        blocked = domain_filter["exclude_domains"]
        violations = [u for u in urls if u and any(d in u for d in blocked)]
        return {
            "filter_type": "block",
            "blocked_domains": blocked,
            "violation_count": len(violations),
            "violations": violations[:5],
            "filter_respected": len(violations) == 0,
        }

    return None


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_test(test: dict) -> dict:
    print(f"\nRunning: {test['id']} — {test['label']}")

    tool_config = {"type": "web_search_preview"}
    if "search_context_size" in test:
        tool_config["search_context_size"] = test["search_context_size"]
    if "domain_filter" in test:
        tool_config["filters"] = test["domain_filter"]

    try:
        t0 = time.monotonic()
        response = client.responses.create(
            model=MODEL,
            tools=[tool_config],
            input=test["query"],
            max_output_tokens=256,  # minimize verbosity; we want metadata, not prose
        )
        latency_ms = round((time.monotonic() - t0) * 1000, 1)

        output_measurements = extract_output_items(response.output)
        sources = extract_sources(response)
        usage = extract_usage(response)
        domain_check = check_domain_filter_respected(sources, test.get("domain_filter"))

        result = {
            "test_id": test["id"],
            "label": test["label"],
            "model": MODEL,
            "track": "raw",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "query": test["query"],
            "search_context_size": test.get("search_context_size"),
            "domain_filter": test.get("domain_filter"),
            **output_measurements,
            "sources": sources,
            "source_count": len(sources),
            "domain_filter_check": domain_check,
            "latency_ms": latency_ms,
            "usage": usage,
            "error": None,
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        result = {
            "test_id": test["id"],
            "label": test["label"],
            "model": MODEL,
            "track": "raw",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "query": test["query"],
            "search_context_size": test.get("search_context_size"),
            "domain_filter": test.get("domain_filter"),
            "tool_invoked": None,
            "search_queries_issued": [],
            "search_call_count": 0,
            "response_text": None,
            "response_text_char_count": 0,
            "sources": [],
            "source_count": 0,
            "domain_filter_check": None,
            "latency_ms": None,
            "usage": {},
            "error": str(e),
        }

    out_path = RESULTS_DIR / f"{test['id']}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved → {out_path}")
    print(f"  Tool invoked: {result['tool_invoked']} | Search calls: {result['search_call_count']} | Sources: {result['source_count']} | Latency: {result['latency_ms']}ms")
    if result.get("domain_filter_check"):
        dfc = result["domain_filter_check"]
        print(f"  Domain filter respected: {dfc['filter_respected']} (violations: {dfc['violation_count']})")

    return result


def main():
    print(f"=== OpenAI Web Search Test: Raw track ===")
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

    # Citable measurements table — these are the spec-ready numbers
    print("\n--- Raw Measurements (citable) ---")
    print(f"{'Test ID':<35} {'Invoked':>7} {'Calls':>5} {'Sources':>7} {'Latency':>9} {'Tokens':>7} {'DomainOK'}")
    print("-" * 95)
    for r in all_results:
        domain_ok = ""
        if r.get("domain_filter_check"):
            domain_ok = str(r["domain_filter_check"]["filter_respected"])
        error = f" ERR: {r['error'][:20]}" if r.get("error") else ""
        print(
            f"{r['test_id']:<35} "
            f"{str(r.get('tool_invoked', '—')):>7} "
            f"{r.get('search_call_count', '—'):>5} "
            f"{r.get('source_count', '—'):>7} "
            f"{str(r.get('latency_ms') or '—'):>9} "
            f"{str(r.get('usage', {}).get('total_tokens') or '—'):>7} "
            f"{domain_ok}{error}"
        )


if __name__ == "__main__":
    main()