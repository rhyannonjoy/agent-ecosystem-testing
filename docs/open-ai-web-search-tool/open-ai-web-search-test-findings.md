---
layout: default
title: "Key Findings OpenAI Web Search, ChatGPT-interpreted"
nav_order: 3
permalink: /docs/open-ai-web-search-tool/open-ai-web-search-test-findings
parent: OpenAI Web Search
---

## Key Findings for OpenAI Web Search, ChatGPT-interpreted

---

**ChatGPT-interpreted Test Workflow**:

    1. Call the Chat Completions API with `gpt-4o-mini-search-preview`
    2. Give the model a detailed prompt asking it to describe what it retrieved -
       result quality, recency, completeness, any failures
    3. The model "always searches" before generating a response; no tool plumbing
       exposed to the caller
    4. Capture the model's full text response as the interpreted finding
    5. Also capture inline `url_citation` annotations from `message.annotations`
       for cross-referencing against the raw track
    6. The gap between the model's self-report and raw citation counts is itself
       a finding — discrepancies belong in the spec
    7. Results are saved to `open-ai-web-search/results/chatgpt-interpreted/`

---

## Platform Limit Summary

| Limit | Observed |
| ------- | ---------- |
| Citation count per response | 0–20 - high variance, non-deterministic |
| `search_context_size` latency impact | Consistent: `high` ~1.5–1.7× slower than `low` |
| `search_context_size` citation impact | Inconsistent across runs |
| Static fact search skip | Non-deterministic: skipped in 2/3 runs |
| Self-reported source count accuracy | Unreliable: frequently overstates inline citations |
| Sources list - all URLs consulted | Not available, Chat Completions API doesn't expose a `sources` field |
| Domain filtering | Not available, Chat Completions search models don't support `filters` |
| Tool invocation visibility | Not available, search is implicit, no `web_search_call` item |

## Results Details

Model: `gpt-4o-mini-search-preview` · 3 runs

>*_5 runs total: first two runs ran without credits and errored out_

### Cross-run Citation Counts

| Test | Label | r1 | r2 | r3 |
| ------ | ------- | ------: | ------: | ------: |
| `test_1_live_data` | Live data | 4 | 0 | 0 |
| `test_2_recent_event` | Recent event | 6 | 6 | 3 |
| `test_3_static_fact` | Static fact | 0 | 1 | 0 |
| `test_4_open_research` | Open-ended research | 6 | 3 | 1 |
| `test_5_ambiguous_query` | Ambiguous query | 3 | 3 | 2 |
| `test_6_search_context_low` | `context_size`: low | 3 | 1 | 4 |
| `test_7_search_context_high` | `context_size`: high | 4 | 9 | 3 |
| `test_8_multi_hop` | Multi-hop research | 8 | 20 | 9 |

| # | Finding | Tests | Observed | Spec Contribution |
| --- | --------- | ------- | ---------- | ------------------- |
| 1 | **Citation count is highly non-deterministic** | `test_1`, `test_8`, all 3 runs | `test_8_multi_hop` ranged 8–20 citations; `test_1_live_data` returned 4 in r1, 0 in r2 & r3; **no test produced identical** citation counts across all 3 runs | **Citation count isn't a reliable proxy** for search depth or result quality in this track |
| 2 | **_"Always-search"_ model doesn't always produce citations and doesn't always search** | `test_1`, r2 & r3 | `test_1_live_data` returned 0 citations in r2 & r3 yet produced accurate live BTC prices in a structured block with no `url_citation` annotations; model retrieved live data without citing | `citation_count == 0` doesn't mean search wasn't performed; **citation count ≠ search invocation** in this track |
| 3 | **Static fact search behavior is inconsistent across runs** | `test_3`, all 3 runs | r1: 0 citations, stated "answered from memory"; r2: 1 citation - Britannica - stated "answered from memory" but searched anyway; r3: 0 citations, stated "answered from memory" | The model's **self-report of search behavior isn't a reliable** indicator of search performance |
| 4 | **Self-reported source counts diverge significantly from inline citation counts** | `test_4`, `test_6`, r2 & r3 | `test_6` r2 reported "10 sources" but produced 1 inline citation. `test_4` r3 reported "12 distinct sources" but produced 1 citation - a YouTube video | **Self-reported counts aren't verifiable** from the response object; no `sources` field equivalent exists in the Chat Completions API |
| 5 | **`search_context_size` latency impact is consistent; citation impact isn't** | `test_6` vs `test_7`, all 3 runs | `high` was consistently ~1.5–1.7× slower than `low`; citation counts didn't follow the same pattern  - in r3, `low` - 4, outperformed `high` - 3; token count was more reliably higher for `high` - see latency table below | `search_context_size` is a reliable latency lever, but it's **not a reliable citation-depth lever** |
| 6 | **Multi-hop query produces the highest variance overall** | `test_8`, all 3 runs | Citation range: 8–20. Latency range: 8406–9869 ms; token range: 916–1333; r2 produced a fully structured Markdown table; r1 & r3 used inline prose citations only | **Response _format_ is non-deterministic** in addition to citation count for complex multi-source queries |
| 7 | **Ambiguous query resolves consistently to programming language** | `test_5`, all 3 runs | All 3 runs defaulted to Python programming language; all acknowledged the animal interpretation but deprioritized it without prompting; no run searched for the animal first | Disambiguation behavior was **the most stable finding across runs**, more consistent than citation count for any other test |

### `search_context_size` latency detail

| | r1 | r2 | r3 |
| --- | ------: | ------: | ------: |
| `low` latency - ms | 2,983 | 4,725 | 2,888 |
| `high` latency - ms | 6,256 | 8,203 | 4,490 |
| `low` citations | 3 | 1 | 4 |
| `high` citations | 4 | 9 | 3 |
