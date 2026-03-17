---
layout: default
title: "Friction Note"
nav_order: 5
permalink: /docs/google-gemini-url-context-tool/friction-note
parent: Google Gemini URL Context
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Google AI Studio API key

Process for getting a Google AI Studio/Gemini API key was more straightforward than the
for the Claude API. The Gemini API URL context docs includes a tools bar on the top
right of the page with a `Get API key` section.

**Instructions**:

1. Go to [aistudio.google.com](https://aistudio.google.com) → sign in
2. Click `Get API key` → `Create API key`
3. Copy the key → add it to your `.env` file
4. Run `source .env`
5. Run `python gemini-url-context/url_context_test_raw.py`

---

## API not available on the free tier - Raw Track

The free tier imposes two hard limits that make reliable test suite runs
impossible without a paid account:

- **Per-minute**: `GenerateRequestsPerMinutePerProjectPerModel-FreeTier`, limit: 5
- **Per-day**: `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit: 20

The 8-test suite requires a minimum of 8 requests per run with no headroom for
retries. The daily cap exhausted across three partial runs; tests 3–8
returned `429 RESOURCE_EXHAUSTED` on the final run. Paid-tier required
to complete the suite reliably in a single run, otherwise you'll see:

```bash
429 RESOURCE_EXHAUSTED: Quota exceeded for metric:
generativelanguage.googleapis.com/generate_content_free_tier_requests,
limit: 20, model: gemini-2.5-flash. Please retry in Xs.
```

---

## Raw Track Roadblocks

1. **`candidate.content.parts` is `None`**, test_5_multi_url_21 - with candidate guard,
   Gemini still raises `NoneType object is not iterable` - candidate exists but is `None` -
   error originates inside `extract_text` and `extract_url_metadata`

   **Fix**: guard both helpers against `None` content before iterating

2. **`max_output_tokens` ceiling interferes with multi-URL metadata**,
   `test_3_multi_url_5`, `test_4_multi_url_20` - `max_output_tokens=128` caused `test_3`
   to return `FinishReason.MAX_TOKENS` with zero `url_metadata` entries; initially appeared in
   r1 as a silent metadata gap on `test_4`: 4,233 tool tokens firing but `url_metadata: []`, no error;
   was the same root cause: response truncated before metadata populated

   **Fix**: raising to 512 resolved `test_3`; `test_4` hit the ceiling at r4 (`FinishReason.MAX_TOKENS`,
   111,326 tool tokens); raising to 1,024 resolved both

3. **Missing candidates guard**, `test_3_multi_url_5`, `test_5_multi_url_21` -
   when Gemini hits an internal tool call budget, it returns `response.candidates = None`
   rather than a structured error; SDK emits `UserWarning: TOO_MANY_TOOL_CALLS isn't
   a valid FinishReason`, but the response object isn't usable; script crashed at
   `response.candidates[0]` because no guard was in place

   **Fix**: check `if not response.candidates` before accessing the candidate, raise a
   `ValueError` with the prompt feedback, record `finish_reason` in all result branches

4. **`test_8_json_content` inconsistent retrieval status across runs** - GitHub API endpoint
   succeeded in r1 and r2:`URL_RETRIEVAL_STATUS_SUCCESS`, ~2,490 tool tokens, but returned
   `URL_RETRIEVAL_STATUS_ERROR` in r4, 116 tool tokens; the near-zero token count on the failed
   run suggests the retriever received an empty or rejected response, likely GitHub API rate
   limiting or auth requirements on unauthenticated requests

   **Fix**: result is non-deterministic; treat as unreliable for the raw track

5. **Transient `503 UNAVAILABLE`**, `test_4_multi_url_20`, r2 - Gemini returned a `503` on
   the 20-URL test, citing high demand: infrastructure-level noise, not a behavioral finding;
   error is caught and recorded correctly

   **Fix**: re-run required to get a clean result for this test case
