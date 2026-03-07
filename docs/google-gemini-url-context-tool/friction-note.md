---
layout: default
title: Friction Note
nav_order: 5
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
retries. The daily cap was exhausted across three partial runs; tests 3–8
returned `429 RESOURCE_EXHAUSTED` on the final run. A paid-tier is required
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

2. **`max_output_tokens=128` truncates multi-URL metadata**, `test_3_multi_url_5` -
   5-URL test hit `FinishReason.MAX_TOKENS` with only 577 tool tokens and zero
   `url_metadata` entries; output cap truncates the response before populating metadata

   **Fix**: raise `max_output_tokens` to at least 512 for multi-URL cases, or globally - the raw
   track measures metadata, not prose, so the original 128 ceiling was unnecessarily tight

3. **Missing candidates guard**, `test_3_multi_url_5`, `test_5_multi_url_21` -
   when Gemini hits an internal tool call budget, it returns `response.candidates = None`
   rather than a structured error; SDK emits `UserWarning: TOO_MANY_TOOL_CALLS isn't
   a valid FinishReason`, but the response object isn't usable; script crashed at
   `response.candidates[0]` because no guard was in place

   **Fix**: check `if not response.candidates` before accessing the candidate, raise a
   `ValueError` with the prompt feedback, record `finish_reason` in all result branches

4. **Silent metadata gap**, `test_4_multi_url_20` -
   20 URLs at the documented limit returned `url_metadata: []` despite tool tokens firing
   4,233; no error was raised and `any_error` is `false`; Gemini appears to process
   URLs internally without populating metadata or silently drops the batch

   **Fix**: needs a follow-up run to determine if this is consistent

5. **Transient `503 UNAVAILABLE`**, `test_4_multi_url_20`, r2 - Gemini returned a `503` on
   the 20-URL test, citing high demand: infrastructure-level noise, not a behavioral finding;
   error is caught and recorded correctly

   **Fix**: re-run required to get a clean result for this test case

---

## Confirmed Behavior

1. `test_5_multi_url_21` returned a clean `400 INVALID_ARGUMENT` on r3:
   `"Number of urls to lookup exceeds the limit (21 > 20). Please reduce the
   number of urls in the request."` - confirming the hard URL cap enforced at
   the API level; no further runs needed for this test case
