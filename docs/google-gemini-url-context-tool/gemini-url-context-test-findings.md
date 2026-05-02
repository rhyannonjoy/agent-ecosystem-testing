---
layout: default
title: "Key Findings Gemini's URL Context Tool - Gemini-interpreted"
permalink: /docs/google-gemini-url-context-tool/gemini-url-context-test-findings
nav_order: 3
parent: Google Gemini URL Context
---

# Key Findings for Gemini's URL Context Tool, Gemini-interpreted

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/gemini-url-context/url_context_test.py)

1. Call the Gemini API with the URL context tool enabled
2. Give Gemini a detailed prompt asking it to describe what it retrieved:
   <br>content length, structure, completeness, any failures
3. Gemini fetches each URL via its pre-retrieval step, then generates a
   response<br>reflecting on what it received
4. Capture Gemini's full text response as the interpreted finding
5. Capture `url_context_metadata` and `usage_metadata` for
   cross-referencing<br>against the raw track
6. The gap between Gemini's self-report and the raw metadata is itself
   a finding,<br>and discrepancies belong in the spec
7. Results stored in `gemini-url-context/results/gemini-interpreted/`

---

## Results Summary

| **Test** | **URLs Req** | **URLs OK** | **Tokens<br>R1/R2/R3** | **Result** |
| ---- | ------- | ------ | ----------- | ---------- | ------ |
| **`test_1_single_html`** | 1 | 1 | 3,142<br>3,151<br>3,141 | Consistent across runs |
| **`test_2_single_pdf`** | 1 | 0 | 147<br>151<br>156 | `URL_RETRIEVAL_STATUS_ERROR` |
| **`test_3_multi_url_5`** | 5 | 5 | 27,564<br>27,579<br>27,572 | Consistent across runs |
| **`test_4_multi_url_20`** | 20 | 20 | 111,401<br>111,714<br>111,375 | Consistent across runs |
| **`test_5_multi_url_21`** | 21 | 0 | _null_ | `400 INVALID_ARGUMENT` |
| **`test_6_unsupported_youtube`** | 1 | 1 | 1,288<br>1,291<br>1,570 | Succeeded - docs say unsupported. Token variance in run 3 |
| **`test_7_unsupported_google_doc`** | 1 | 0 | _null_<br>181<br>192 | `429` and `URL_RETRIEVAL_STATUS_ERROR`,<br>run 1 rate-limited, runs 2-3 confirm |
| **`test_8_json_content`** | 1 | 0 | _null_<br>133<br>_null_ | `429` and r2: `URL_RETRIEVAL_STATUS_ERROR`,<br>run 1, 3 daily quota exhausted  |

>`gemini-2.5-flash`, free tier daily cap 20 RPD reached after `test_7` run 3

## Truncation Analysis

| **Finding** | **Tests** | **Observation** | **Spec Detail** |
| --------- | ------- | ---------- | ------------------- |
| **20-URL limit is a hard limit** | `test_5` | `400 INVALID_ARGUMENT`:<br>`"Number of urls to lookup exceeds<br>the limit (21 > 20)"`. `url_context_metadata` empty,<br>zero URL content tokens consumed. | API layer enforces limit<br>before retrieval, not<br>truncation or silent dropping |
| **YouTube succeeds despite documented as unsupported** | `test_6` | `URL_RETRIEVAL_STATUS_SUCCESS`; tool tokens: 1,288 / 1,291 / 1,570. Run 3 returned ~22% more tokens, suggesting live-fetch vs. cache variation. | Docs don't reflect current behavior on `gemini-2.5-flash` as of March 2026; token variance suggests cache vs. live-fetch switching |
| **PDF retrieval failed consistently on a valid public PDF** | `test_2` | `URL_RETRIEVAL_STATUS_ERROR`; tool tokens: 147 / 151 / 156 - minimal, consistent error response. PDF is a documented supported type. | PDF retrieval fails reliably for this W3C URL; follow-up needed with a different source before drawing a firm conclusion |
| **Google Docs fail at retrieval layer, not API layer** | `test_7` runs 2 & 3 | `URL_RETRIEVAL_STATUS_ERROR` with tool tokens 181 / 192. Request completes normally, no API-level error. Contrasts with `test_5`, API layer rejected. | Failure modes: API-layer rejection; hard error, zero retrieval vs. retrieval-layer failure, request completes, status in metadata |
| **JSON API endpoint failed retrieval** | `test_8` r2 only | `URL_RETRIEVAL_STATUS_ERROR`, 133 tool tokens. JSON is a documented supported type. GitHub API requires auth headers tool can't supply; run 1, run 3 hit quota before test. | JSON support applies to public, unauthenticated endpoints. Endpoints requiring auth headers return `URL_RETRIEVAL_STATUS_ERROR` |
| **Tool tokens dominate cost at scale** | `test_1` `test_3` `test_4` | 20 URLs, tool tokens ~111,400 = ~98.6% of total cost; tool token counts vary <1% between runs; see token scaling table below. | Use `tool_use_prompt_token_count` for cost est; stable, reproducible, accounts for ~98.6% of cost |
| **`url_context_metadata` order non-deterministic** | `test_3` `test_4` | Metadata order shuffled relative to input order on every run; pattern itself varied between runs | Match results by `retrieved_url` string, not array index |
| **Gemini's char count estimates vary within, across runs** | `test_1` `test_3` | `test_1` same URL: 10,950 / 17,476 / 15,221 chars; `test_3` same URL in multi-URL context: ~11,360 / ~20,400 / ~11,500. Variance large, non-directional. | Interpreted character counts not citable; `tool_use_prompt_token_count` variance <1%, only reproducible proxy for content size |
| **Free tier imposes per-minute, per-day limits** | `test_7` `test_8` | Run 1 `429` errors: `GenerateRequestsPerMinutePerProjectPerModel-FreeTier` limit: 5 RPM; run 3 `GenerateRequestsPerDayPerProjectPerModel-FreeTier` limit: 20 RPD; 3 runs × ~7 tests exhausted daily quota. | Free tier: 5 RPM, 20 RPD on `gemini-2.5-flash`; running interpreted, raw tracks same day exhaust the daily limit; plan across days or use a paid tier |
| **Duplicate response in test 3 was non-reproducible** | `test_3` | Run 1 produced full results table twice in sequence; runs 2-3 didn't; non-deterministic model output artifact. | Treat as known non-determinism; raw metadata authoritative source for retrieval counts, statuses |

## Token Scaling Details

| **Test** | **URLs** | **Tool<br>Tokens** | **Prompt<br>Tokens** | **% Tool** |
| ---- | --- | ------- | ------------ | ----- |
| `test_1_single_html` | 1 | ~3,145 avg | 65 | ~86.7% |
| `test_3_multi_url_5` | 5 | ~27,572 avg | 137 | ~96.6% |
| `test_4_multi_url_20` | 20 | ~111,497 avg | 417 | ~98.6% |
