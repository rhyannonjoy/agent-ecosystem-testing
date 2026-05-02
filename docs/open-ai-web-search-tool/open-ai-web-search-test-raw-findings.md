---
layout: default
title: "Key Findings OpenAI Web Search, Raw"
nav_order: 4
permalink: /docs/open-ai-web-search-tool/open-ai-web-search-test-raw-findings
parent: OpenAI Web Search
---

# Key Findings for OpenAI Web Search, Raw

---

## [Raw Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-web-search/web_search_test.py)

1. Call the Responses API with `gpt-4o`, `web_search_preview` tool enabled
2. Give the model a minimal prompt; just enough to trigger retrieval
3. The model may or may not `invoke web_search_preview` depending on the query
4. Extract raw outcomes directly from `response.output` items:
    - `web_search_call` items: type, `action.query` - the internal search query issued
    - message items: `output_text`
5. Extract sources list from `response.sources` - all URLs consulted, not just cited
6. Extract token accounting from `response.usage`
7. Run all analysis in Python: tool invocation flag, source counts, latency
8. The model never interprets or reflects on the retrieval results
9. Ensure results saved to `open-ai-web-search/results/raw/`

---

## Platform Limit Summary

| **Limit** | **Observation** |
| ------- | ---------- |
| **Tool Invocation** | _Conditional_, skipped for static facts and trivial math, consistent |
| **Tool Invocation<br>Visibility** | _Available_ explicit `web_search_call` item in `response.output` |
| **`search_context_size`<br>Latency Impact** | _Inconsistent_ `high` was slower in run 1, run 3,<br>but faster than `low` in run 2 |
| **`search_context_size`<br>Source Count Impact** | _None observed_ source count was 12 across all context sizes |
| **Sources List<br>All URLs Consulted** | _Available_ via `include=["web_search_call.action.sources"]` |
| **Domain Filtering<br>Allow List** | _Worked once_ on `web_search_preview` for run 1;<br> broken on `web_search` across all subsequent runs |
| **Domain Filtering<br>Block List** | _Never succeeded_, `filters` parameter rejected in<br>all configurations and models tested |
| **`search_queries_issued`<br>Date Accuracy** | _Unreliable_, model appends training-era year to internal<br>queries despite running in 2026 |

## Results Details

>_Run 5 = `test_8`, `test_9` only, targeted domain filter retry on `web_search_preview`;<br>run 5 model = `gpt-5` while
>the remainder of the test runs model = `gpt-4o`_

### Cross-run Tool Invocation

| **Test** | **Label** | **R1** | **R2** | **R3** | **R4** | **R5** | **R6** |
| ------ | ------- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`test_1_live_data`** | Live Data | ✓ | ✓ | ✓ | ✓ | _null_ | ✓ |
| **`test_2_recent_event`** | Recent Event | ✓ | ✓ | ✓ | ✓ | _null_ | ✓ |
| **`test_3_static_fact`** | Static Fact | ✗ | ✗ | ✗ | ✗ | _null_ | ✗ |
| **`test_4_trivial_math`** | Trivial Math | ✗ | ✗ | ✗ | ✗ | _null_ | ✗ |
| **`test_5_open_research`** | Open-ended Research | ✓ | ✓ | ✓ | ✓ | _null_ | ✓ |
| **`test_6_context_size_low`** | `context_size` Low | ✓ | ✓ | ✓ | ✓ | _null_ | ✓ |
| **`test_7_context_size_high`** | `context_size` High | ✓ | ✓ | ✓ | ✓ | _null_ | ✓ |
| **`test_8_domain_filter_allowed`** | Allow List Filter | `ERR`† | ✓* | `ERR`‡ | `ERR`‡ | `ERR`¶ | `ERR`‡ |
| **`test_9_domain_filter_blocked`** | Block List Filter | `ERR`† | `ERR`§ | `ERR`‡ | `ERR`‡ | `ERR`¶ | `ERR`‡ |
| **`test_10_ambiguous_query`** | Ambiguous Query | ✓ | ✓ | ✓ | ✓ | _null_ | ✓ |

**Domain Filter Error Progression**

- †, Run 1: `"Unknown parameter: 'tools[0].filters.type'"` initial schema with `type: "domain"` key
- *, Run 2 `test_8`: `filter_respected: true`, 2 _"apnews.com"_ sources, `web_search_preview` + `allowed_domains`, only success across all runs
- §, Run 2 `test_9`: `"Unknown parameter: 'tools[0].filters.excluded_domains'"` first block-list key attempt
- ‡, R3/R4/R6: `"Unsupported parameter 'filters'"` after switching to `web_search` per docs guidance
- ¶, Run 5 with `gpt-5`: `"Unsupported parameter 'filters'"` model change produced identical error

---

## `search_context_size` Latency Detail

| | **R1** | **R2** | **R3** |
| --- | ------ | ------ | ------ |
| **`Low` Latency - ms** | 10,867 | 10,251 | 9,531 |
| **`High` Latency - ms** | 15,984 | 8,614 | 11,233 |
| **`Low` Source Count** | 12 | 12 | 12 |
| **`High` Source Count** | 12 | 12 | 12 |
