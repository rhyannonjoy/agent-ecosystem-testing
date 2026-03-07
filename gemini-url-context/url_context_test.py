"""
Gemini API URL context tool, Gemini-interpreted analysis
==========================================
Companion to `url_context_test_raw.py`. This script asks Gemini to reflect
on what it retrieved from each URL — characterizing content length, completeness,
and failure reasons in its own words.
This captures Gemini's self-perception of the retrieval, which may differ
from what `url_context_metadata` reports in the raw track.

Usage:
    source .env
    python gemini-url-context/url_context_test.py

Workflow:
1. Call the Gemini API with the URL context tool enabled
2. Give Gemini a detailed prompt asking it to describe what it retrieved —
   content length, structure, completeness, any failures
3. Gemini fetches each URL via its pre-retrieval step, then generates a
   response reflecting on what it received
4. Capture Gemini's full text response as the interpreted finding
5. Also capture `url_context_metadata` and `usage_metadata` for
   cross-referencing against the raw track
6. The gap between Gemini's self-report and the raw metadata is itself
   a finding — discrepancies belong in the spec
7. Results are saved to `google-gemini-url-context/results/gemini-interpreted/`
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
# Format: results/gemini-interpreted/YYYY-MM-DDTHH-MM/
_RUN_TS = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M")
RESULTS_DIR = Path(f"google-gemini-url-context/results/gemini-interpreted/{_RUN_TS}")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Free tier limit: 5 requests per minute for gemini-2.5-flash.
# 13s between requests keeps us safely under that ceiling.
# Set to 0 if you are on a paid tier.
RATE_LIMIT_SLEEP_SECONDS = 13

# ---------------------------------------------------------------------------
# Test URLs — mirrors the progressive complexity used in web_fetch_test.py
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "id": "test_1_single_html",
        "label": "Single HTML page (docs)",
        "urls": ["https://ai.google.dev/gemini-api/docs/url-context"],
        "prompt": (
            "Fetch the content at the URL I've provided. "
            "Tell me: what content did you retrieve? How long was it? "
            "Did anything appear to be missing or truncated? "
            "Describe the structure of what you received."
        ),
    },
    {
        "id": "test_2_single_pdf",
        "label": "Single PDF",
        "urls": ["https://www.w3.org/WAI/WCAG21/wcag21.pdf"],
        "prompt": (
            "Fetch the PDF at the URL I've provided. "
            "Tell me: what content did you retrieve? How long was it? "
            "Did anything appear truncated or missing?"
        ),
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
        "prompt": (
            "Fetch the content at all the URLs I've provided. "
            "For each URL, tell me: did the fetch succeed? "
            "Roughly how much content did you receive? "
            "Was anything truncated or unavailable?"
        ),
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
        "prompt": (
            "Fetch the content at all 20 URLs I've provided. "
            "For each URL, report whether it succeeded or failed. "
            "Did any URLs fail to load? Were any silently skipped? "
            "How much total content did you receive across all URLs?"
        ),
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
            "https://ai.google.dev/gemini-api/docs/quickstart",  # 21st URL
        ],
        "prompt": (
            "Fetch the content at all 21 URLs I've provided. "
            "For each URL, report whether it succeeded or failed. "
            "Did any URLs fail to load? Were any silently skipped or dropped? "
            "Report exactly how many URLs you were able to retrieve."
        ),
    },
    {
        "id": "test_6_unsupported_youtube",
        "label": "Unsupported content type: YouTube",
        "urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
        "prompt": (
            "Fetch the content at the URL I've provided. "
            "What did you receive? Did the fetch succeed or fail? "
            "If it failed, what reason were you given?"
        ),
    },
    {
        "id": "test_7_unsupported_google_doc",
        "label": "Unsupported content type: Google Doc",
        "urls": ["https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit"],
        "prompt": (
            "Fetch the content at the URL I've provided. "
            "What did you receive? Did the fetch succeed or fail? "
            "If it failed, what reason were you given?"
        ),
    },
    {
        "id": "test_8_json_content",
        "label": "JSON content type",
        "urls": ["https://api.github.com/repos/agent-ecosystem/agent-docs-spec"],
        "prompt": (
            "Fetch the JSON at the URL I've provided. "
            "What content did you retrieve? How was it structured? "
            "Was it complete or truncated?"
        ),
    },
]


def run_test(test: dict) -> dict:
    """Run a single Gemini-interpreted URL context test."""
    print(f"\nRunning: {test['id']} — {test['label']}")

    contents = test["prompt"] + "\n\nURLs:\n" + "\n".join(test["urls"])

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=GenerateContentConfig(tools=[{"url_context": {}}]),
        )

        candidate = response.candidates[0]

        # Extract text across all parts (model may return multiple)
        text_parts = [
            part.text for part in candidate.content.parts if hasattr(part, "text") and part.text
        ]
        interpreted_text = "\n".join(text_parts)

        # url_context_metadata — convert to serializable form
        metadata = candidate.url_context_metadata
        url_metadata_list = []
        if metadata and hasattr(metadata, "url_metadata"):
            for entry in metadata.url_metadata:
                url_metadata_list.append({
                    "retrieved_url": entry.retrieved_url,
                    "url_retrieval_status": str(entry.url_retrieval_status),
                })

        usage = response.usage_metadata
        usage_dict = {
            "prompt_token_count": getattr(usage, "prompt_token_count", None),
            "candidates_token_count": getattr(usage, "candidates_token_count", None),
            "tool_use_prompt_token_count": getattr(usage, "tool_use_prompt_token_count", None),
            "thoughts_token_count": getattr(usage, "thoughts_token_count", None),
            "total_token_count": getattr(usage, "total_token_count", None),
        }

        result = {
            "test_id": test["id"],
            "label": test["label"],
            "model": MODEL,
            "track": "gemini-interpreted",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "urls_requested": test["urls"],
            "url_count_requested": len(test["urls"]),
            "prompt": test["prompt"],
            "gemini_interpreted_response": interpreted_text,
            "url_context_metadata": url_metadata_list,
            "urls_successfully_retrieved": sum(
                1 for u in url_metadata_list
                if "SUCCESS" in u.get("url_retrieval_status", "")
            ),
            "usage_metadata": usage_dict,
            "error": None,
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        result = {
            "test_id": test["id"],
            "label": test["label"],
            "model": MODEL,
            "track": "gemini-interpreted",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "urls_requested": test["urls"],
            "url_count_requested": len(test["urls"]),
            "prompt": test["prompt"],
            "gemini_interpreted_response": None,
            "url_context_metadata": [],
            "urls_successfully_retrieved": 0,
            "usage_metadata": {},
            "error": str(e),
        }

    # Save individual result
    out_path = RESULTS_DIR / f"{test['id']}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved → {out_path}")

    return result


def main():
    print(f"=== Gemini URL Context Test: Gemini-interpreted track ===")
    print(f"Model: {MODEL}")
    print(f"Results dir: {RESULTS_DIR}\n")

    all_results = []
    for i, test in enumerate(TEST_CASES):
        if i > 0 and RATE_LIMIT_SLEEP_SECONDS > 0:
            print(f"  Waiting {RATE_LIMIT_SLEEP_SECONDS}s (rate limit)...")
            time.sleep(RATE_LIMIT_SLEEP_SECONDS)
        result = run_test(test)
        all_results.append(result)

    # Save combined summary
    summary_path = RESULTS_DIR / "_summary.json"
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll results saved to {summary_path}")

    # Print quick findings table
    print("\n--- Quick Results ---")
    print(f"{'Test ID':<35} {'URLs Req':>8} {'URLs OK':>8} {'Total Tokens':>13} {'Error'}")
    print("-" * 80)
    for r in all_results:
        tokens = r.get("usage_metadata", {}).get("total_token_count", "—")
        error = r.get("error") or ""
        print(
            f"{r['test_id']:<35} "
            f"{r['url_count_requested']:>8} "
            f"{r['urls_successfully_retrieved']:>8} "
            f"{str(tokens):>13} "
            f"{error[:30]}"
        )


if __name__ == "__main__":
    main()