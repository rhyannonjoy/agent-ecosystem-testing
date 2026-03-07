---
layout: default
title: Key Findings URL context - Gemini interpreted
permalink: /gemini-url-context-test-findings/
nav_order: 3
parent: Google Gemini URL Context
---

**Gemini-interpreted Test Workflow**:

    1. Call the Gemini API with the URL context tool enabled
    2. Give Gemini a detailed prompt asking it to describe what it retrieved:
       content length, structure, completeness, any failures
    3. Gemini fetches each URL via its pre-retrieval step, then generates a
       response reflecting on what it received
    4. Capture Gemini's full text response as the interpreted finding
    5. Also capture `url_context_metadata` and `usage_metadata` for
       cross-referencing against the raw track
    6. The gap between Gemini's self-report and the raw metadata is itself
       a finding, and discrepancies belong in the spec
    7. Results stored in `gemini-url-context/results/gemini-interpreted/`

---

## Results Summary

3 runs: `gemini-2.5-flash`, free tier daily cap 20 RPD reached after run 3 test 7

| Test | URLs Req | URLs OK | Tokens - r1/r2/r3 | Result |
| ---- | -------: | ------: | -----------: | ----------: | ------ |
| `test_1_single_html` | 1 | 1 | 3,142/3,151/3,141 | Consistent across runs |
| `test_2_single_pdf` | 1 | 0 | 147/151/156 | `URL_RETRIEVAL_STATUS_ERROR` |
| `test_3_multi_url_5` | 5 | 5 | 27,564/27,579/27,572 | Consistent across runs |
| `test_4_multi_url_20` | 20 | 20 | 111,401/111,714/111,375 | Consistent across runs |
| `test_5_multi_url_21` | 21 | 0 | — | `400 INVALID_ARGUMENT` |
| `test_6_unsupported_youtube` | 1 | 1 | 1,288/1,291/1,570 | Succeeded - docs say unsupported. Token variance in run 3 |
| `test_7_unsupported_google_doc` | 1 | 0 | — / 181/192 | `429` and `URL_RETRIEVAL_STATUS_ERROR` - r1 rate-limited, r2 & r3 confirm |
| `test_8_json_content` | 1 | 0 | — /133/— | `429` and r2: `URL_RETRIEVAL_STATUS_ERROR` - r1 & r3 daily quota exhausted  |

| # | Finding | Tests | Observed | Spec contribution |
| --- | --------- | ------- | ---------- | ------------------- |
| 1 | **20-URL limit is a hard API error** | `test_5` all 3 runs | `400 INVALID_ARGUMENT`: `"Number of urls to lookup exceeds the limit (21 > 20)"`. `url_context_metadata` empty, zero URL content tokens consumed. Reproduced on all 3 runs. | Limit is enforced at the API layer before retrieval. Not truncation or silent dropping. |
| 2 | **YouTube succeeds despite being documented as unsupported** | `test_6` all 3 runs | `URL_RETRIEVAL_STATUS_SUCCESS` all 3 runs. Tool tokens: 1,288 / 1,291 / 1,570. Run 3 returned ~22% more tokens, suggesting live-fetch vs. cache variation. | Documented limitation doesn't reflect current behavior on `gemini-2.5-flash` as of March 2026. Token variance across runs suggests cache vs. live-fetch switching. |
| 3 | **PDF retrieval failed consistently on a valid public PDF** | `test_2` all 3 runs | `URL_RETRIEVAL_STATUS_ERROR` all 3 runs. Tool tokens: 147 / 151 / 156 - minimal, consistent error response. PDF is a documented supported type. | PDF retrieval fails reliably for this W3C URL. Follow-up needed with a different PDF source before drawing a firm conclusion. |
| 4 | **Google Docs fail at the retrieval layer, not the API layer** | `test_7` runs 2 & 3 | `URL_RETRIEVAL_STATUS_ERROR` with tool tokens 181 / 192. Request completes normally - no API-level error. Contrasts with test 5 which rejected at the API layer. | Two distinct failure modes exist: API-layer rejection; hard error, zero retrieval vs. retrieval-layer failure, request completes, status in metadata. |
| 5 | **JSON API endpoint failed retrieval** | `test_8` r2 only | `URL_RETRIEVAL_STATUS_ERROR`, 133 tool tokens. JSON is a documented supported type. GitHub API requires auth headers the tool can't supply; r1 & r3 hit quota before this test. | JSON support applies to public, unauthenticated endpoints. Endpoints requiring auth headers will return `URL_RETRIEVAL_STATUS_ERROR`. |
| 6 | **Tool tokens dominate cost at scale: stable across runs** | `test_1`, `test_3`, `test_4` all 3 runs | At 20 URLs, tool tokens ~111,400 = ~98.6% of total cost across all 3 runs. Tool token counts vary <1% between runs. See token scaling table below. | Use `tool_use_prompt_token_count` for cost estimation; it's stable, reproducible, and accounts for ~98.6% of cost at 20 URLs. |
| 7 | **`url_context_metadata` order is non-deterministic** | `test_3`, `test_4` all 3 runs | Metadata order shuffled relative to input order on every run. Shuffle pattern itself varied between runs, not a stable reordering. | Match results by `retrieved_url` string, not array index. |
| 8 | **Gemini's character count estimates vary within and across runs** | `test_1` across 3 runs, `test_3` across 3 runs | Test 1 same URL: 10,950 / 17,476 / 15,221 chars. Test 3 same URL in multi-URL context: ~11,360 / ~20,400 / ~11,500. Variance is large and non-directional. | Interpreted character counts aren't citable. `tool_use_prompt_token_count` - variance <1%, is the only reproducible proxy for content size. |
| 9 | **Free tier imposes both per-minute and per-day limits** | `test_7` run 1, `test_8` run 3 | Two distinct `429` errors: `GenerateRequestsPerMinutePerProjectPerModel-FreeTier` limit: 5 RPM in r1; `GenerateRequestsPerDayPerProjectPerModel-FreeTier` limit: 20 RPD in r3. 3 runs × ~7 tests exhausted the daily quota. | Free tier: 5 RPM and 20 RPD on `gemini-2.5-flash`. Running interpreted + raw tracks in the same day will exhaust the daily limit. Plan across days or use a paid tier. |
| 10 | **Duplicate response in test 3 was non-reproducible** | `test_3` r1 only | r1 produced the full results table twice in sequence; r2 & r3 didn't reproduce it. Non-deterministic model output artifact. | Treat as known non-determinism. Raw metadata is the authoritative source for retrieval counts and statuses. |

### Token scaling detail - averages across 3 runs

| Test | URLs | Tool tokens - avg | Prompt tokens | % tool |
| ---- | ---: | ----------------: | ------------: | -----: |
| `test_1_single_html` | 1 | 3,145 | 65 | ~86.7% |
| `test_3_multi_url_5` | 5 | 27,572 | 137 | ~96.6% |
| `test_4_multi_url_20` | 20 | 111,497 | 417 | ~98.6% |

## Pending

- **Raw track**: Not yet run. Daily quota, 20 RPD, exhausted after 3 interpreted runs. Run on a separate day.
- **`test_8_json_content`**: Only completed once, r2. A second clean result would strengthen the finding.
- **PDF follow-up**: Test a different publicly accessible PDF to distinguish server-blocking from tool limitation.
