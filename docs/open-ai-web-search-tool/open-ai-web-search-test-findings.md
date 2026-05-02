---
layout: default
title: "Key Findings OpenAI Web Search, ChatGPT-interpreted"
nav_order: 3
permalink: /docs/open-ai-web-search-tool/open-ai-web-search-test-findings
parent: OpenAI Web Search
---

# Key Findings for OpenAI Web Search, ChatGPT-interpreted

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-web-search/web_search_test.py)

1. Call the Chat Completions API with `gpt-4o-mini-search-preview`
2. Give the model a detailed prompt asking it to describe what it retrieved -<br>
   result quality, recency, completeness, any failures
3. The model "always searches" before generating a response; no tool<br>plumbing
   exposed to the caller
4. Capture model's full text response as the interpreted finding
5. Capture inline `url_citation` annotations from `message.annotations`<br>
   for cross-referencing against the raw track
6. The gap between the model's self-report and raw citation counts is itself<br>
   a finding, discrepancies belong in the spec
7. Ensure results saved to `open-ai-web-search/results/chatgpt-interpreted/`

---

## Platform Limit Summary

| **Limit** | **Observation** |
| ------- | ---------- |
| **Citation Coun<br>per Response** | 0–20 _high variance_, _non-deterministic_ |
| **`search_context_size`<br>Latency Impact** | _Consistent_, `high` ~1.5–1.7× slower than `low` |
| **`search_context_size`<br> Citation Impact** | _Inconsistent_ across runs |
| **Static Fact Search Skip** | _Non-deterministic_, skipped in 2/3 runs |
| **Self-reported Source<br>Count Accuracy** | _Unreliable_, frequently overstates inline citations |
| **Sources List<br>_all URLs consulted_** | _Not available_, Chat Completions API doesn't expose a `sources` field |
| **Domain Filtering** | _Not available_, Chat Completions search models don't support `filters` |
| **Tool Invocation<br>Visibility** | _Not available_, search is implicit, no `web_search_call` item |

## Results Details

Model: `gpt-4o-mini-search-preview` · 3 runs

>*_5 runs total: first two runs ran without credits, errored out_

### Cross-run Citation Counts

| **Test** | **Label** | **R1** | **R2** | **R3** |
| ------ | ------- | ------: | ------: | ------: |
| **`test_1_live_data`** | Live data | 4 | 0 | 0 |
| **`test_2_recent_event`** | Recent event | 6 | 6 | 3 |
| **`test_3_static_fact`** | Static fact | 0 | 1 | 0 |
| **`test_4_open_research`** | Open-ended research | 6 | 3 | 1 |
| **`test_5_ambiguous_query`** | Ambiguous query | 3 | 3 | 2 |
| **`test_6_search_context_low`** | `context_size`: low | 3 | 1 | 4 |
| **`test_7_search_context_high`** | `context_size`: high | 4 | 9 | 3 |
| **`test_8_multi_hop`** | Multi-hop research | 8 | 20 | 9 |

## Truncation Analysis

| # | Finding | Tests | Observed | Spec Contribution |
| --- | --------- | ------- | ---------- | ------------------- |
| 1 | **Citation count highly non-deterministic** | `test_1` `test_8` | `test_8_multi_hop` ranged 8–20 citations; `test_1_live_data` returned 4 in run 1, 0 in runs 2-3; **no test produced identical** citation counts | **Citation count isn't reliable proxy** for search depth or result quality in this track |
| 2 | **_"Always-search"_ model doesn't always produce citations, doesn't always search** | `test_1` | `test_1_live_data` returned 0 citations in runs 2-3 yet produced accurate live BTC prices in a structured block with no `url_citation` annotations; model retrieved live data without citing | `citation_count == 0` doesn't mean search wasn't performed; **citation count ≠ search invocation** in this track |
| 3 | **Static fact search behavior inconsistent** | `test_3` | run 1: 0 citations, stated "answered from memory"; run 2: 1 citation - Britannica - stated _"answered from memory,"_ but searched anyway; run 3: 0 citations, stated _"answered from memory"_ | Model's **self-report of search behavior isn't reliable** indicator of search performance |
| 4 | **Self-reported source counts diverge significantly from inline citation counts** | `test_4` `test_6` | `test_6` run 2 reported _"10 sources,"_ but produced 1 inline citation. `test_4` run 3 reported _"12 distinct sources,"_ but produced 1 citation, a YouTube video | **Self-reported counts aren't verifiable** from the response object; no `sources` field equivalent exists in Chat Completions |
| 5 | **`search_context_size` latency impact consistent; citation impact isn't** | `test_6` `test_7` | `high` was consistently ~1.5–1.7× slower than `low`; citation counts didn't follow same pattern  in run 3, `low` - 4, outperformed `high` - 3; token count more reliably higher for `high`, see latency table below | `search_context_size` reliable latency lever, but it's **not a reliable citation-depth lever** |
| 6 | **Multi-hop query produces highest variance** | `test_8` | Citation range: 8–20. Latency range: 8406–9869 ms; token range: 916–1333; run 2 produced fully structured Markdown table; run 1, run 3 used inline prose citations only | **Response _format_ non-deterministic** in addition to citation count for complex multi-source queries |
| 7 | **Ambiguous query resolves consistently to programming language** | `test_5` | Defaulted to Python programming language; all acknowledged the animal interpretation but deprioritized without prompting; no run searched for the animal first | Disambiguation behavior **most stable finding**, more consistent than citation count for any other test |

## `search_context_size` Latency Detail

| | **R1** | **R2** | **R3** |
| --- | ------ | ------ | ------ |
| **`Low` Latency ms** | 2,983 | 4,725 | 2,888 |
| **`High` Latency ms** | 6,256 | 8,203 | 4,490 |
| **`Low` Citations** | 3 | 1 | 4 |
| **`High` Citations** | 4 | 9 | 3 |
