"""
Gemini API URL context tool, raw content analysis
==========================================
Companion to `url_context_test.py`. Instead of asking Gemini to describe
what it retrieved, this script inspects the raw `url_context_metadata`
and `usage_metadata` fields directly and measures outcomes programmatically.
This gives objective, reproducible measurements that don't depend on
Gemini's interpretation or estimation.

Usage:
    source .env
    python gemini-url-context/url_context_test_raw.py

Workflow:
1. Call the Gemini API with the URL context tool enabled
2. Give Gemini a minimal prompt — just enough to trigger URL retrieval
3. Gemini fetches each URL via its pre-retrieval step, but isn't asked
   to interpret, describe, or reflect on what it received
4. Extract raw retrieval outcomes directly from `url_context_metadata`
   in the response object — `retrieved_url` and `url_retrieval_status`
   per URL
5. Extract token accounting from `usage_metadata` —
   `tool_use_prompt_token_count` (URL content tokens) and
   `prompt_token_count` (text prompt tokens) are recorded separately
6. Run all analysis in Python: URL counts, status enum enumeration,
   success/failure rates, token breakdowns
7. Gemini never interprets or reflects on the retrieval results
8. Results are saved to `google-gemini-url-context/results/raw/`
"""

import os
import json
import time
import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()

client = genai.Client(api_key=os.environ["GOOGLE_GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"
# Each run gets its own timestamped subdirectory — matches the claude-api track convention.
# Format: results/raw/YYYY-MM-DDTHH-MM/
_RUN_TS = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M")
RESULTS_DIR = Path(f"google-gemini-url-context/results/raw/{_RUN_TS}")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Free tier limit: 5 requests per minute for gemini-2.5-flash.
# 13s between requests keeps us safely under that ceiling.
# Set to 0 if you are on a paid tier.
RATE_LIMIT_SLEEP_SECONDS = 13

# ---------------------------------------------------------------------------
# Minimal prompts — we want signal, not model verbosity.
# The raw track uses max_tokens=128 to minimize model output cost and noise,
# mirroring the approach used in web_fetch_test_raw.py.
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "id": "test_1_single_html",
        "label": "Single HTML page (docs)",
        "urls": ["https://ai.google.dev/gemini-api/docs/url-context"],
        "prompt": "Summarize the page at the URL provided in one sentence.",
    },
    {
        "id": "test_2_single_pdf",
        "label": "Single PDF",
        "urls": ["https://www.w3.org/WAI/WCAG21/wcag21.pdf"],
        "prompt": "Summarize the document at the URL provided in one sentence.",
    },
    {
        "id": "test_3_multi_url_5",
        "label": "5 URLs",
        "urls": [
            "https://ai.google.dev/gemini-api/docs/url-context",
            "https://ai.google.dev/gemini-api/docs/google-search",
            "https://ai.google.dev/gemini-api/docs/function-calling",
            "https://ai.google.dev/gemini-api/docs/code-execution",
            "https://ai.google.dev/gemini-api/docs/long-context",
        ],
        "prompt": "List the title of each page at the URLs provided.",
    },
    {
        "id": "test_4_multi_url_20",
        "label": "20 URLs (at limit)",
        "urls": [
            "https://ai.google.dev/gemini-api/docs/url-context",
            "https://ai.google.dev/gemini-api/docs/google-search",
            "https://ai.google.dev/gemini-api/docs/function-calling",
            "https://ai.google.dev/gemini-api/docs/code-execution",
            "https://ai.google.dev/gemini-api/docs/long-context",
            "https://ai.google.dev/gemini-api/docs/text-generation",
            "https://ai.google.dev/gemini-api/docs/image-understanding",
            "https://ai.google.dev/gemini-api/docs/audio",
            "https://ai.google.dev/gemini-api/docs/video-understanding",
            "https://ai.google.dev/gemini-api/docs/document-processing",
            "https://ai.google.dev/gemini-api/docs/structured-output",
            "https://ai.google.dev/gemini-api/docs/thinking",
            "https://ai.google.dev/gemini-api/docs/embeddings",
            "https://ai.google.dev/gemini-api/docs/caching",
            "https://ai.google.dev/gemini-api/docs/files",
            "https://ai.google.dev/gemini-api/docs/tokens",
            "https://ai.google.dev/gemini-api/docs/safety-settings",
            "https://ai.google.dev/gemini-api/docs/rate-limits",
            "https://ai.google.dev/gemini-api/docs/pricing",
            "https://ai.google.dev/gemini-api/docs/models",
        ],
        "prompt": "List the title of each page at the URLs provided.",
    },
    {
        "id": "test_5_multi_url_21",
        "label": "21 URLs (over limit)",
        "urls": [
            "https://ai.google.dev/gemini-api/docs/url-context",
            "https://ai.google.dev/gemini-api/docs/google-search",
            "https://ai.google.dev/gemini-api/docs/function-calling",
            "https://ai.google.dev/gemini-api/docs/code-execution",
            "https://ai.google.dev/gemini-api/docs/long-context",
            "https://ai.google.dev/gemini-api/docs/text-generation",
            "https://ai.google.dev/gemini-api/docs/image-understanding",
            "https://ai.google.dev/gemini-api/docs/audio",
            "https://ai.google.dev/gemini-api/docs/video-understanding",
            "https://ai.google.dev/gemini-api/docs/document-processing",
            "https://ai.google.dev/gemini-api/docs/structured-output",
            "https://ai.google.dev/gemini-api/docs/thinking",
            "https://ai.google.dev/gemini-api/docs/embeddings",
            "https://ai.google.dev/gemini-api/docs/caching",
            "https://ai.google.dev/gemini-api/docs/files",
            "https://ai.google.dev/gemini-api/docs/tokens",
            "https://ai.google.dev/gemini-api/docs/safety-settings",
            "https://ai.google.dev/gemini-api/docs/rate-limits",
            "https://ai.google.dev/gemini-api/docs/pricing",
            "https://ai.google.dev/gemini-api/docs/models",
            "https://ai.google.dev/gemini-api/docs/quickstart",
        ],
        "prompt": "List the title of each page at the URLs provided.",
    },
    {
        "id": "test_6_unsupported_youtube",
        "label": "Unsupported: YouTube",
        "urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
        "prompt": "Summarize the content at the URL provided in one sentence.",
    },
    {
        "id": "test_7_unsupported_google_doc",
        "label": "Unsupported: Google Doc",
        "urls": ["https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit"],
        "prompt": "Summarize the content at the URL provided in one sentence.",
    },
    {
        "id": "test_8_json_content",
        "label": "JSON content type",
        "urls": ["https://api.github.com/repos/agent-ecosystem/agent-docs-spec"],
        "prompt": "Summarize the content at the URL provided in one sentence.",
    },
]


# ---------------------------------------------------------------------------
# Raw measurement helpers — all Python, no model estimates
# ---------------------------------------------------------------------------

def extract_url_metadata(candidate) -> list[dict]:
    metadata = candidate.url_context_metadata
    results = []
    if metadata and hasattr(metadata, "url_metadata"):
        for entry in metadata.url_metadata:
            results.append({
                "retrieved_url": entry.retrieved_url,
                "url_retrieval_status": str(entry.url_retrieval_status),
            })
    return results


def extract_usage(usage_metadata) -> dict:
    return {
        "prompt_token_count": getattr(usage_metadata, "prompt_token_count", None),
        "candidates_token_count": getattr(usage_metadata, "candidates_token_count", None),
        "tool_use_prompt_token_count": getattr(usage_metadata, "tool_use_prompt_token_count", None),
        "thoughts_token_count": getattr(usage_metadata, "thoughts_token_count", None),
        "total_token_count": getattr(usage_metadata, "total_token_count", None),
    }


def extract_text(candidate) -> str:
    parts = []
    for part in candidate.content.parts:
        if hasattr(part, "text") and part.text:
            parts.append(part.text)
    return "\n".join(parts)


def measure_response(candidate, response) -> dict:
    """All measurements derived programmatically from the response object."""
    text = extract_text(candidate)
    url_metadata = extract_url_metadata(candidate)
    usage = extract_usage(response.usage_metadata)

    statuses = [u["url_retrieval_status"] for u in url_metadata]
    status_counts = {}
    for s in statuses:
        status_counts[s] = status_counts.get(s, 0) + 1

    return {
        "response_text_char_count": len(text),
        "response_text_word_count": len(text.split()),
        "url_metadata": url_metadata,
        "urls_retrieved_count": len(url_metadata),
        "retrieval_status_counts": status_counts,
        "all_succeeded": all("SUCCESS" in s for s in statuses) if statuses else False,
        "any_unsafe": any("UNSAFE" in s for s in statuses),
        "any_error": any("ERROR" in s for s in statuses),
        "usage_metadata": usage,
        "tool_use_prompt_tokens": usage.get("tool_use_prompt_token_count"),
        "total_tokens": usage.get("total_token_count"),
    }


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_test(test: dict) -> dict:
    print(f"\nRunning: {test['id']} — {test['label']}")

    contents = test["prompt"] + "\n\nURLs:\n" + "\n".join(test["urls"])

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=GenerateContentConfig(
                tools=[{"url_context": {}}],
                max_output_tokens=128,  # minimize model verbosity; we want metadata, not prose
            ),
        )

        candidate = response.candidates[0]
        measurements = measure_response(candidate, response)

        result = {
            "test_id": test["id"],
            "label": test["label"],
            "model": MODEL,
            "track": "raw",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "urls_requested": test["urls"],
            "url_count_requested": len(test["urls"]),
            "prompt": test["prompt"],
            **measurements,
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
            "urls_requested": test["urls"],
            "url_count_requested": len(test["urls"]),
            "prompt": test["prompt"],
            "response_text_char_count": None,
            "response_text_word_count": None,
            "url_metadata": [],
            "urls_retrieved_count": 0,
            "retrieval_status_counts": {},
            "all_succeeded": False,
            "any_unsafe": False,
            "any_error": True,
            "usage_metadata": {},
            "tool_use_prompt_tokens": None,
            "total_tokens": None,
            "error": str(e),
        }

    out_path = RESULTS_DIR / f"{test['id']}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved → {out_path}")
    print(f"  URLs requested: {result['url_count_requested']} | Retrieved: {result['urls_retrieved_count']}")
    print(f"  Status counts: {result['retrieval_status_counts']}")
    print(f"  Tool tokens: {result['tool_use_prompt_tokens']} | Total: {result['total_tokens']}")

    return result


def main():
    print(f"=== Gemini URL Context Test: Raw track ===")
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
    print(f"{'Test ID':<35} {'Req':>4} {'Got':>4} {'ToolTok':>8} {'TotalTok':>9} {'Statuses'}")
    print("-" * 95)
    for r in all_results:
        statuses = json.dumps(r.get("retrieval_status_counts", {}))
        error = f" ERR: {r['error'][:25]}" if r.get("error") else ""
        print(
            f"{r['test_id']:<35} "
            f"{r['url_count_requested']:>4} "
            f"{r['urls_retrieved_count']:>4} "
            f"{str(r.get('tool_use_prompt_tokens') or '—'):>8} "
            f"{str(r.get('total_tokens') or '—'):>9} "
            f"{statuses}{error}"
        )


if __name__ == "__main__":
    main()