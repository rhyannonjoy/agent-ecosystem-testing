---
layout: default
title: "Key Findings Gemini's URL Context Tool - Raw"
permalink: /docs/google-gemini-url-context-tool/gemini-url-context-test-raw-findings
nav_order: 4
parent: Google Gemini URL Context
---

# Key Findings for Gemini's URL Context Tool, Raw

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/gemini-url-context/url_context_test_raw.py)

1. Call the Gemini API with the URL context tool enabled
2. Give Gemini a minimal prompt - just enough to trigger URL retrieval
3. Gemini fetches each URL via its pre-retrieval step, but isn't asked
   to interpret, describe, or reflect on what it received
4. Extract raw retrieval outcomes directly from `url_context_metadata`
   in the response object -`retrieved_url` and `url_retrieval_status`
   per URL
5. Extract token accounting from `usage_metadata` —
   `tool_use_prompt_token_count`, URL content tokens, and
   `prompt_token_count`, text prompt tokensm, recorded separately
6. Run all analysis in Python: URL counts, status enum enumeration,
   success/failure rates, token breakdowns
7. Results stored in `google-gemini-url-context/results/raw/`

---

## Results Summary

| **Test** | **URLs** | **URLs<br>OK** | **Tool<br>Tokens** | **Result** |
| ---- | -------: | ------: | ------------------: | ------: |
| `test_1_single_html` | 1 | 1 | 3,099<br>3,128 | _Consistent<br>across runs_ |
| `test_2_single_pdf` | 1 | 0 | 119<br>126 | _`URL_RETRIEVAL_STATUS_ERROR` consistent_ |
| `test_3_multi_url_5` | 5 | 5 | 27,508<br>27,506 | _Consistent<br>across runs_ |
| `test_4_multi_url_20` | 20 | 20 | 111,326<br>111,326 | _Consistent<br>across runs_ |
| `test_5_multi_url_21` | 21 | 0 | _null_ | _`400 INVALID_ARGUMENT` consistent_ |
| `test_6_unsupported_youtube` | 1 | 1 | 1,584<br>1,570 | _`URL_RETRIEVAL_STATUS_SUCCESS`<br>docs say unsupported_ |
| `test_7_unsupported_google_doc` | 1 | 0 | 162<br>219 | _`URL_RETRIEVAL_STATUS_ERROR` consistent_ |
| `test_8_json_content` | 1 | r1,2:0<br>r4,5:0 | 116<br>112 | _Non-deterministic<br>succeeded r1-2, failed r4-5_ |

> 5 raw track runs: `gemini-2.5-flash`, runs 1–3 on free tier, _daily cap exhausted after r3 test 2_,
>runs 4–5 on paid tier; canonical results in run 4-5

---

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observation** | **Spec Detail** |
| --- | ------- | ----- | -------- | ----------------- |
| 1 | **20-URL limit is hard limit** | `test_5` r3-5 | `400 INVALID_ARGUMENT`: `"Number of urls to lookup exceeds the limit (21 > 20)"`. Zero URL content tokens consumed. Reproduced on all clean runs. | Limit enforced at the API layer before retrieval. Not truncation or silent dropping. |
| 2 | **YouTube succeeds despite being documented as unsupported** | `test_6` r1<br>r4-5 | `URL_RETRIEVAL_STATUS_SUCCESS` on all clean runs. Tool tokens: 1,525 / 1,584 / 1,570<br>variance <4%. | Documented limitation doesn't reflect current behavior on `gemini-2.5-flash` as of March 2026. |
| 3 | **PDF retrieval fails consistently on a valid public PDF** | `test_2` | `URL_RETRIEVAL_STATUS_ERROR` every run. Tool tokens: 119–126, minimal, consistent. PDF documented supported type. | PDF retrieval fails reliably for this W3C URL; follow-up needed with different source before drawing firm conclusion |
| 4 | **Google Docs fail at retrieval layer, not API layer** | `test_7` r1<br>r4-5 | `URL_RETRIEVAL_STATUS_ERROR`, tool tokens 156–219. Request completes normally. | Failure modes: API-layer rejection, hard error, zero tokens, as in `test_5` vs. retrieval-layer failure, request completes, status recorded in metadata |
| 5 | **JSON API endpoint retrieval is non-deterministic** | `test_8` | `URL_RETRIEVAL_STATUS_SUCCESS` in r1-2 ~2,490 tool tokens; `URL_RETRIEVAL_STATUS_ERROR` in r4-5, 112–116 tool tokens. No change in endpoint or prompt between runs. | Handling of `application/json` responses from this endpoint unreliable; treat JSON API endpoints as non-deterministic until confirmed with a stable public endpoint |
| 6 | **Tool tokens dominate cost at scale** | `test_1` `test_3` `test_4` r4-5 | 20 URLs, tool tokens 111,326 r4-r5, 0% variance; 5 URLs: 27,506–27,508; 1 URL: 3,099–3,134. | `tool_use_prompt_token_count` reproducible to <1% across runs, accounts for ~98.6% of total cost at 20 URLs; use for cost estimation |
| 7 | **`url_context_metadata` order non-deterministic** | `test_3`, `test_4` r4-5 | Metadata order shuffled relative to input order on every run; pattern varies between runs. | Match results by `retrieved_url` string, not array index |

## Token Scaling Details

| **Test** | **URLs** | **Tool Tokens** | **% Total** |
| ---- | --- | -------------- | --------- |
| `test_1_single_html` | 1 | ~3,114 avg | ~86% |
| `test_3_multi_url_5` | 5 | ~27,507 avg | ~98.6% |
| `test_4_multi_url_20` | 20 | ~111,326 avg | ~98.9% |
