---
layout: default
title: "Key Findings Gemini's URL Context Tool - Raw"
permalink: /docs/google-gemini-url-context-tool/gemini-url-context-test-raw-findings
nav_order: 4
parent: Google Gemini URL Context
---

## Key Findings for Gemini's URL Context Tool, Raw

---

## Topic Guide

- [Raw Test Workflow](#raw-test-workflow)
- [Results Summary](#results-summary)

---

## [Raw Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/gemini-url-context/url_context_test_raw.py)

1. Call the Gemini API with the URL context tool enabled
2. Give Gemini a minimal prompt - just enough to trigger URL retrieval
3. Gemini fetches each URL via its pre-retrieval step, but isn't asked
   to interpret, describe, or reflect on what it received
4. Extract raw retrieval outcomes directly from `url_context_metadata`
   in the response object -`retrieved_url` and `url_retrieval_status`
   per URL
5. Extract token accounting from `usage_metadata` —
   `tool_use_prompt_token_count` - URL content tokens - and
   `prompt_token_count` - text prompt tokens - recorded separately
6. Run all analysis in Python: URL counts, status enum enumeration,
   success/failure rates, token breakdowns
7. Gemini never interprets or reflects on the retrieval results
8. Results stored in `google-gemini-url-context/results/raw/`

---

## Results Summary

5 raw track runs: `gemini-2.5-flash`, runs 1–3 on free tier, _daily cap exhausted after r3 test 2_,
runs 4–5 on paid tier; canonical results are r4 and r5 -

| Test | URLs Req | URLs OK | Tool tokens - r4/r5 | Result |
| ---- | -------: | ------: | ------------------: | ------: |
| `test_1_single_html` | 1 | 1 | 3,099 / 3,128 | Consistent across runs |
| `test_2_single_pdf` | 1 | 0 | 119 / 126 | `URL_RETRIEVAL_STATUS_ERROR` consistent |
| `test_3_multi_url_5` | 5 | 5 | 27,508 / 27,506 | Consistent across runs |
| `test_4_multi_url_20` | 20 | 20 | 111,326 / 111,326 | Consistent across runs |
| `test_5_multi_url_21` | 21 | 0 | - | `400 INVALID_ARGUMENT` consistent |
| `test_6_unsupported_youtube` | 1 | 1 | 1,584 / 1,570 | `URL_RETRIEVAL_STATUS_SUCCESS` - docs say unsupported |
| `test_7_unsupported_google_doc` | 1 | 0 | 162 / 219 | `URL_RETRIEVAL_STATUS_ERROR` consistent |
| `test_8_json_content` | 1 | 1 - r1, r2 / 0 - r4, r5 | 116 / 112 | Non-deterministic - succeeded r1 & r2, failed r4 & r5 |

| # | Finding | Tests | Observed | Spec contribution |
| --- | ------- | ----- | -------- | ----------------- |
| 1 | **20-URL limit is a hard API error** | `test_5` r3, r4, r5 | `400 INVALID_ARGUMENT`: `"Number of urls to lookup exceeds the limit (21 > 20)"`. Zero URL content tokens consumed. Reproduced on all clean runs. | Limit enforced at the API layer before retrieval. Not truncation or silent dropping. |
| 2 | **YouTube succeeds despite being documented as unsupported** | `test_6` r1, r4, r5 | `URL_RETRIEVAL_STATUS_SUCCESS` on all clean runs. Tool tokens: 1,525 / 1,584 / 1,570 - variance <4%. | Documented limitation doesn't reflect current behavior on `gemini-2.5-flash` as of March 2026. |
| 3 | **PDF retrieval fails consistently on a valid public PDF** | `test_2` all 5 runs | `URL_RETRIEVAL_STATUS_ERROR` on every run. Tool tokens: 119–126, minimal and consistent. PDF is a documented supported type. | PDF retrieval fails reliably for this W3C URL. Follow-up needed with a different PDF source before drawing a firm conclusion. |
| 4 | **Google Docs fail at the retrieval layer, not the API layer** | `test_7` r1, r4, r5 | `URL_RETRIEVAL_STATUS_ERROR` with tool tokens 156–219. Request completes normally - no API-level rejection. | Two distinct failure modes exist: API-layer rejection, hard error, zero tokens, as in `test_5` vs. retrieval-layer failure, request completes, status recorded in metadata. |
| 5 | **JSON API endpoint retrieval is non-deterministic** | `test_8` all runs | `URL_RETRIEVAL_STATUS_SUCCESS` in r1 and r2  - ~2,490 tool tokens; `URL_RETRIEVAL_STATUS_ERROR` in r4 and r5 - 112–116 tool tokens. No change in endpoint or prompt between runs. | The Gemini URL context tool's handling of `application/json` responses from this endpoint is unreliable. Treat JSON API endpoints as non-deterministic until confirmed with a stable public endpoint. |
| 6 | **Tool tokens dominate cost at scale and are stable across runs** | `test_1`, `test_3`, `test_4` r4 & r5 | At 20 URLs, tool tokens = 111,326 on both r4 and r5 - 0% variance. At 5 URLs: 27,506–27,508. At 1 URL: 3,099–3,134. | `tool_use_prompt_token_count` is reproducible to <1% across runs and accounts for ~98.6% of total cost at 20 URLs. Use it for cost estimation. |
| 7 | **`url_context_metadata` order is non-deterministic** | `test_3`, `test_4` r4 & r5 | Metadata order shuffled relative to input order on every run. Shuffle pattern itself varies between runs. | Match results by `retrieved_url` string, not array index. |

### Token Scaling - r4 and r5 Averages

| Test | URLs | Tool tokens avg | % of total |
| ---- | ---: | --------------: | ---------: |
| `test_1_single_html` | 1 | 3,114 | ~86% |
| `test_3_multi_url_5` | 5 | 27,507 | ~98.6% |
| `test_4_multi_url_20` | 20 | 111,326 | ~98.9% |
