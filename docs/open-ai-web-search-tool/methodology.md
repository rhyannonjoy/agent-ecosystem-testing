---
layout: default
title: "Methodology"
nav_order: 1
parent: OpenAI Web Search
---

## Methodology

Empirical testing of the [OpenAI web search tool](https://platform.openai.com/docs/guides/tools-web-search)
across two tracks that expose different layers of the same behavior.

The **ChatGPT-interpreted track** mirrors the ChatGPT UI experience: the model always searches,
self-reports what it found, and cites inline. There is no tool plumbing exposed to the caller -
search invocation, source lists, and internal queries are all implicit. The **raw track** exposes
the plumbing: explicit `web_search_call` items in `response.output`, exact source lists, and
the internal query string the model issued. These are Python `len()` calls and dictionary
lookups, not model estimates.

The gap between these two tracks is itself a finding. If the interpreted track reports "12 distinct
sources" but the raw `source_count` is 1, that discrepancy belongs in the spec.

| | `web_search_test.py` | `web_search_test_raw.py` |
| - | -------------------- | ------------------------ |
| API | Chat Completions API | Responses API |
| Model | `gpt-4o-mini-search-preview` | `gpt-4o` + `web_search_preview` tool |
| Always searches? | Yes - implicit, no visibility | Model decides - explicit `web_search_call` item |
| Source list | Not available | `web_search_call.action.sources` via `include` param |
| Internal query | Not exposed | `action.query` from `web_search_call` item |
| Domain filtering | Not available | Available on `web_search` tool - non-functional as tested |
| `max_output_tokens` | Not set | `256` - metadata is the signal, not prose |
| Best used for | What the model perceives it retrieved | Citable measurements for the spec |

## Measurement Constraints

The interpreted track uses `gpt-4o-mini-search-preview`, a specialized Chat Completions model
that always performs web search before generating. Search invocation, source selection, and
citation behavior are all internal to the model; there is no `web_search_call` item, no
`sources` field, and _no way to verify the model's self-reported source counts against actual
URLs consulted_.

The raw track uses `gpt-4o` with `web_search_preview` as an explicit tool via the Responses API.
Tool invocation is conditional: the model decides whether to search based on the query. This
exposes `search_queries_issued`, full source lists, and exact token accounting, but also
surfaces model bias: internal queries appended training-era years "2023" despite running in
March 2026.

Docs describe domain filtering - `filters` parameter on the `web_search` tool, but use returned
`"Unsupported parameter 'filters'"` on every attempt across `gpt-4o` and `gpt-5`. See
[friction note](friction-note.md) for the full error progression.
