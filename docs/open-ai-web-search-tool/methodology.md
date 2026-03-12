---
layout: default
title: "Methodology"
nav_order: 1
parent: OpenAI Web Search
---

## Methodology

Empirical testing of the [OpenAI web search tool](https://platform.openai.com/docs/guides/tools-web-search)
across two tracks that expose different layers of the same behavior. See
[ChatGPT-interpreted vs Raw](chatgpt-interpreted-vs-raw.md) for a full comparison of what each
track measures and where the two diverge.

The **ChatGPT-interpreted track** uses the Chat Completions API with `gpt-4o-mini-search-preview` -
search is always implicit, no tool plumbing exposed to the caller. The **raw track** uses the
Responses API with `gpt-4o` + `web_search_preview` - tool invocation is conditional and explicitly
observable via `web_search_call` items in `response.output`.

---

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

Docs describe domain filtering - `filters` parameter on the `web_search` tool, but tests returned
`"Unsupported parameter 'filters'"` on every attempt across `gpt-4o` and `gpt-5`. See
[the Friction Note](friction-note.md) for the full error progression.
