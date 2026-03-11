---
layout: default
title: "Methodology"
nav_order: 1
parent: OpenAI Web Search
---

## Methodology

For contribution to [agent-ecosystem/agent-docs-spec Known Platform Limits](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits).

## ChatGPT-interpreted vs Raw

Track A mirrors the ChatGPT UI experience - abstracted, opinionated, always-on.  
Track B exposes the raw plumbing and is what you'd use for agent workflows.

| | ChatGPT-interpreted | Raw |
| --- | --- | --- |
| **API** | Chat Completions | Responses API |
| **Model** | `gpt-4o-search-preview` | `gpt-4o` + `web_search_preview` tool |
| **Always searches?** | Yes | Model decides |
| **Tool call visible?** | No |  Yes - `web_search_call` item |
| **Full sources list?** | No |  Yes - `response.sources` |
| **Domain filtering?** |  No |  Yes - `filters.domains` |

## Setup

```bash
pip install openai
export OPENAI_API_KEY=sk-...
python openai_web_search_test.py
```

## What it tests

1. **Core comparison**: runs all `TEST_QUERIES` through both tracks side by side, capturing latency, citation count, sources count, and response text.

2. **Probe 1: Static fact tool-skip**: does Track B correctly skip `web_search_preview` for `"What is 2 + 2?"` or does it always search anyway?

3. **Probe 2: `search_context_size` tradeoff**: measures latency and source count across `low`, `medium`, `high` for the same query.

4. **Probe 3: Domain filtering**: verifies that `filters.domains` - Responses API only - actually constrains sources returned.

## Outputs

- Console: side-by-side comparison per query
- `openai_web_search_limits.json`: machine-readable summary of known asymmetries, suitable for pasting into `SPEC.md`

## Known Platform Limits

- Domain filtering is **only** available on Track B - Responses API - not on Chat Completions search models
- Track A **always** issues a web search call; Track B's tool invocation is heuristic; trivial queries may skip
- The `web_search_call` output item exposes the model's internal search query string on Track B, which isn't visible on Track A
- `search_context_size` config is different per track: `web_search_options.search_context_size` on Track A, tool config on Track B
- Citation annotations - inline, available on both; full `sources` list - all URLs consulted - only on Track B
