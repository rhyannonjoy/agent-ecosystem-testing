---
layout: default
title: "Key Findings OpenAI Web Search, Raw"
nav_order: 4
permalink: /docs/open-ai-web-search-tool/open-ai-web-search-test-raw-findings
parent: OpenAI Web Search
---

## Key Findings for OpenAI Web Search, Raw

---

**Raw Test Workflow**:

    1. Call the Responses API with `gpt-4o` + `web_search_preview` tool enabled
    2. Give the model a minimal prompt; just enough to trigger retrieval
    3. The model may or may not `invoke web_search_preview` depending on the query
    4. Extract raw outcomes directly from response.output items:
       - `web_search_call` items: type, `action.query` - the internal search query issued
       - message items: `output_text`
    5. Extract sources list from `response.sources` - all URLs consulted, not just cited
    6. Extract token accounting from `response.usage`
    7. Run all analysis in Python: tool invocation flag, source counts, latency
    8. The model never interprets or reflects on the retrieval results
    9. Results are saved to `open-ai-web-search/results/raw/`

---

## Platform Limit Summary

| Limit | Observed |
| ------- | ---------- |
| Tool invocation | **Conditional**: skipped for static facts and trivial math, consistent across all 3 runs |
| Tool invocation visibility | **Available**: explicit `web_search_call` item in `response.output` |
| `search_context_size` latency impact | **Inconsistent**: `high` was slower in r1 & r3, but faster than `low` in r2 |
| `search_context_size` source count impact | **None observed**: source count was 12 across all context sizes in all runs |
| Sources list - all URLs consulted | **Available** via `include=["web_search_call.action.sources"]` |
| Domain filtering - allow-list | **Worked _once_** on `web_search_preview` for r1; broken on `web_search` across all subsequent runs |
| Domain filtering - block-list | **Never succeeded**; `filters` parameter rejected in all configurations and models tested |
| `search_queries_issued` date accuracy | **Unreliable**: model appends training-era year to internal queries despite running in 2026 |

## Results Details

>_r5 = `test_8` & `test_9` only, targeted domain filter retry on `web_search_preview`; r5 model = `gpt-5` while
the remainder of the test runs model = `gpt-4o`_

### Cross-run Tool Invocation

| Test | Label | r1 | r2 | r3 | r4 | r5 | r6 |
| ------ | ------- | :---: | :---: | :---: | :---: | :---: | :---: |
| `test_1_live_data` | Live data | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `test_2_recent_event` | Recent event | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `test_3_static_fact` | Static fact | ✗ | ✗ | ✗ | ✗ | — | ✗ |
| `test_4_trivial_math` | Trivial math | ✗ | ✗ | ✗ | ✗ | — | ✗ |
| `test_5_open_research` | Open-ended research | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `test_6_context_size_low` | `context_size`: low | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `test_7_context_size_high` | `context_size`: high | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `test_8_domain_filter_allowed` | Allow-list filter | `ERR`† | ✓* | `ERR`‡ | `ERR`‡ | `ERR`¶ | `ERR`‡ |
| `test_9_domain_filter_blocked` | Block-list filter | `ERR`† | `ERR`§ | `ERR`‡ | `ERR`‡ | `ERR`¶ | `ERR`‡ |
| `test_10_ambiguous_query` | Ambiguous query | ✓ | ✓ | ✓ | ✓ | — | ✓ |

**Domain Filter Error Progression**

- †,r1: `"Unknown parameter: 'tools[0].filters.type'"` - initial schema with `type: "domain"` key
- *,r2 `test_8`: `filter_respected: true`, 2 "apnews.com" sources - `web_search_preview` + `allowed_domains`, only success across all runs
- §,r2 `test_9`: `"Unknown parameter: 'tools[0].filters.excluded_domains'"` - first block-list key attempt
- ‡,r3/r4/r6: `"Unsupported parameter 'filters'"` - after switching to `web_search` per docs guidance
- ¶,r5 with `gpt-5`: `"Unsupported parameter 'filters'"` - model change produced identical error

---

### `search_context_size` Latency Detail

| | r1 | r2 | r3 |
| --- | ------: | ------: | ------: |
| `low` latency - ms | 10,867 | 10,251 | 9,531 |
| `high` latency - ms | 15,984 | 8,614 | 11,233 |
| `low` source count | 12 | 12 | 12 |
| `high` source count | 12 | 12 | 12 |
