---
layout: default
title: "Key Findings OpenAI Web Search, Raw"
nav_order: 4
parent: OpenAI Web Search
---

## Key Findings OpenAI Web Search, Raw

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
| Tool invocation | Conditional: skipped for static facts and trivial math, consistent across all 3 runs |
| Tool invocation visibility | Available: explicit `web_search_call` item in `response.output` |
| `search_context_size` latency impact | Inconsistent: `high` was slower in r1 & r3, but faster than `low` in r2 |
| `search_context_size` source count impact | None observed: source count was 12 across all context sizes in all runs |
| Sources list - all URLs consulted | Available via `include=["web_search_call.action.sources"]` |
| Domain filtering - allow-list | Worked once on `web_search_preview` for r1; broken on `web_search` across all subsequent runs |
| Domain filtering - block-list | Never succeeded; `filters` parameter rejected in all configurations and models tested |
| `search_queries_issued` date accuracy | Unreliable: model appends training-era year to internal queries despite running in 2026 |

## Results Details

Model: `gpt-4o` · 5 runs

### Cross-run tool invocation

| Test | Label | r1 Invoked | r1 Latency | r2 Invoked | r2 Latency | r3 Invoked | r3 Latency |
| ------ | ------- | :-------: | ------: | :-------: | ------: | :-------: | ------: |
| `test_1_live_data` | Live data | True | 7380.7 ms | True | 16029.8 ms | True | 4180.5 ms |
| `test_2_recent_event` | Recent event | True | 8039.6 ms | True | 10375.8 ms | True | 7444.5 ms |
| `test_3_static_fact` | Static fact | False | 3901.6 ms | False | 3085.7 ms | False | 2032.1 ms |
| `test_4_trivial_math` | Trivial math | False | 1854.3 ms | False | 2464.0 ms | False | 730.6 ms |
| `test_5_open_research` | Open-ended research | True | 7385.2 ms | True | 12505.7 ms | True | 12299.5 ms |
| `test_6_context_size_low` | `context_size`: low | True | 10457.6 ms | True | 10867.6 ms | True | 10251.3 ms |
| `test_7_context_size_high` | `context_size`: high | True | 5744.0 ms | True | 15984.4 ms | True | 8614.0 ms |
| `test_8_domain_filter_allowed` | Allow-list filter | `ERROR†` | — | True* | 4416.7 ms | `ERROR‡` | — |
| `test_9_domain_filter_blocked` | Block-list filter | `ERROR†` | — | `ERROR§` | — | `ERROR‡` | — |
| `test_10_ambiguous_query` | Ambiguous query | True | 9341.7 ms | True | 7140.5 ms | True | 6195.8 ms |

| Test | Label | r4 Invoked | r4 Latency | r5 Invoked | r5 Latency | r6 Invoked | r6 Latency |
| ------ | ------- | :-------: | ------: | :-------: | ------: | :-------: | ------: |
| `test_1_live_data` | Live data | True | 4823.1 ms | — | — | True | 4301.6 ms |
| `test_2_recent_event` | Recent event | True | 9792.4 ms | — | — | True | 5165.9 ms |
| `test_3_static_fact` | Static fact | False | 1130.7 ms | — | — | False | 829.0 ms |
| `test_4_trivial_math` | Trivial math | False | 2578.6 ms | — | — | False | 701.4 ms |
| `test_5_open_research` | Open-ended research | True | 13531.2 ms | — | — | True | 6899.7 ms |
| `test_6_context_size_low` | `context_size`: low | True | 10142.6 ms | — | — | True | 9531.2 ms |
| `test_7_context_size_high` | `context_size`: high | True | 10710.5 ms | — | — | True | 11233.4 ms |
| `test_8_domain_filter_allowed` | Allow-list filter | `ERROR‡` | — | `ERROR¶` | — | `ERROR‡` | — |
| `test_9_domain_filter_blocked` | Block-list filter | `ERROR‡` | — | `ERROR¶` | — | `ERROR‡` | — |
| `test_10_ambiguous_query` | Ambiguous query | True | 6195.8 ms | — | — | True | 5532.7 ms |

>_r5 = `test_8` & `test_9` only, targeted domain filter retry on `web_search_preview`; r5 model = `gpt-5`_

**Domain filter error progression**

- † r1: `"Unknown parameter: 'tools[0].filters.type'"` - initial schema with `type: "domain"` key
- * r2 test_8: `filter_respected: true`, 2 "apnews.com" sources - `web_search_preview` + `allowed_domains`, only success across all runs
- § r2 test_9: `"Unknown parameter: 'tools[0].filters.excluded_domains'"` - first block-list key attempt
- ‡ r3/r4/r6: `"Unsupported parameter 'filters'"` - after switching to `web_search` per docs guidance
- ¶ r5 with `gpt-5`: `"Unsupported parameter 'filters'"` - model change produced identical error

### `search_context_size` latency detail

| | r1 | r2 | r3 |
| --- | ------: | ------: | ------: |
| `low` latency - ms | 10,867 | 10,251 | 9,531 |
| `high` latency - ms | 15,984 | 8,614 | 11,233 |
| `low` source count | 12 | 12 | 12 |
| `high` source count | 12 | 12 | 12 |
