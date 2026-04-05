---
layout: default
title: "ChatGPT-interpreted vs Raw"
nav_order: 2
permalink: /docs/open-ai-web-search-tool/chatgpt-interpreted-vs-raw
parent: OpenAI Web Search
---

## ChatGPT-interpreted vs Raw

---

## Topic Guide

- [Track Design](#track-design)
- [Agent Docs Spec - Known Platform Limits](#agent-docs-spec---known-platform-limits)

---

## Track Design

Two Python scripts test the same web search behaviors:

**ChatGPT-interpreted** captures what `gpt-4o-mini-search-preview` _believes_ it retrieved:
how many sources it consulted, whether results felt current, how it characterizes search depth.
This is the model's self-report. The **raw track** captures what the API _actually returned_:
exact `tool_invoked` flags, exact source lists from `web_search_call.action.sources`, exact
token counts from `response.usage`. These are Python `len()` calls and dictionary lookups,
not model estimates.

The gap between these two tracks is itself a finding. If the interpreted track reports "12
distinct sources" but the raw `source_count` is 1, that discrepancy belongs in the spec.

| | `web_search_test.py` | `web_search_test_raw.py` |
| - | ---------------------- | -------------------------- |
| API | Chat Completions API | Responses API |
| Measures | Model's interpretation of what it retrieved | Raw metadata extracted directly from response object |
| Search invocation | Implicit - model always searches, no visibility | Explicit `web_search_call` item in `response.output` |
| Source counts | Model self-report - frequently overstates | Python `len()` on `web_search_call.action.sources` - exact |
| Citation counts | `url_citation` annotations in `message.annotations` | Not applicable, raw track doesn't count inline citations |
| Internal query | Not exposed | `action.query` string from `web_search_call` item - exact |
| `max_output_tokens` | Not set - model writes full assessments | Set to `256` - minimal output, metadata is the signal |
| Token cost per run | Higher - model writes long self-assessments | Lower - minimal prompt, capped output |
| Domain filtering | Not available - Chat Completions API only | Available on `web_search` tool, non-functional as tested |
| Sources list | Not available, Chat Completions API only | Available via `include=["web_search_call.action.sources"]` |
| Best used for | Understanding what the model perceives it retrieved | Citable measurements for the spec |

## Agent Docs Spec - Known Platform Limits

Both tracks agree on the following and are the citable findings for the spec:

### Tool Invocation

- Tool invocation is **conditional and deterministic** for unambiguous query types: static facts
  and trivial math were never searched across all raw track runs; live data and research queries
  always invoked the tool. Behavior was consistent across all 3 complete raw runs.
- In the interpreted track, tool invocation is implicit and not observable. `citation_count == 0`
  doesn't mean search wasn't performed - `test_1_live_data` returned 0 citations in 2/3 runs
  while still producing accurate live BTC prices.

### Citation and Source Counts

- Citation counts in the interpreted track are **highly non-deterministic**: `test_8_multi_hop`
  ranged 8–20 across 3 runs; no test produced identical counts across all runs.
- Self-reported source counts are **unreliable**: `test_6` r2 claimed "10 sources" but produced
  1 inline citation; `test_4` r3 claimed "12 distinct sources" but produced 1 citation.
- Raw source counts were **stable at 12** across all invoked tests and all context sizes - the
  only exception being domain filter tests, which errored, and no-search tests, 0 sources.

### `search_context_size`

- Latency impact is **consistent in the interpreted track** - `high` ~1.5–1.7× slower than `low`
  and **inconsistent in the raw track** - r2 `high` was _faster_ than `low`.
- Citation impact is inconsistent in both tracks.
- Source count impact is **zero in the raw track**: `source_count` was 12 regardless of
  `low`, `medium`, or `high` across all 3 runs.

### Internal Query Construction

- `search_queries_issued` in the raw track contains **stale date strings**: internal queries
  appended training-era years - "2023" and "October 2023" - despite running in March 2026;
  `"latest developments in EU AI regulation 2023"`. Query construction isn't temporally aware -
  `search_queries_issued` reflects model bias, not wall-clock time.

### Domain Filtering

- **Allow-list filtering** - `allowed_domains` worked once on `web_search_preview`, r2,
  `filter_respected: true`, 2 "apnews.com" sources. After switching to `web_search` per
  docs guidance, both allow-list and block-list filtering returned
  `"Unsupported parameter 'filters'"` on every subsequent run across `gpt-4o` and `gpt-5`.
- **Block-list filtering** never succeeded in any configuration across 6 runs, 2 tool types,
  and 2 models. Attempted three parameter names - `exclude_domains`, `excluded_domains`,
  `blocked_domains` - all `400`.
- **The contradiction**: docs state filtering requires `web_search`; empirically it worked once
  on `web_search_preview` and never on `web_search`. Domain filtering is documented but
  non-functional via the Python SDK as tested.
- Domain filtering **isn't available in the interpreted track** - Chat Completions API only.

### Disambiguation

- Both tracks resolved the ambiguous query `"Python release"` consistently to the programming
  language across all runs. Disambiguation behavior was the most stable finding in the suite.
