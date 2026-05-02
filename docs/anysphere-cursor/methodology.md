---
layout: default
title: "Methodology"
permalink: /docs/anysphere-cursor/methodology
parent: Anysphere Cursor
---

# Methodology

---

## Turn-by-turn

>_**Chat-based measurement through interaction, without direct code instrumentation**_

Software instrumentation is the process of adding code to a system
to collect data about how it works; while the Cursor chat is public and accessible,
the testing approach is different than calling an API to extract measurements programmatically.

---

## Approach Comparison

>_**Testing a closed consumer application vs an open API**_

Rather than target specific endpoints with documented interfaces,
Cursor testing targets consumer application with proprietary chat
behavior and multiple fetch mechanisms. Cursor's chat web fetch and MCP
implementations don't have a public API; MCP servers are user-configured,
implementations vary - `mcp-server-fetch`, `fetch-browser-mcp`, third-party,
and are observable through Cursor's agent behavior, but not
instrumentable. Compare to this collection's
[Claude API Web Fetch testing](/docs/anthropic-claude-api-web-fetch-tool/methodology):

| **Aspect** | **Claude API** | **Cursor** |
| -------- | ------------------- | ----------------- |
| **Interface** | Python API call,<br>response object available | _Chat UI_: observable only through output |
| **Layers** | _Single_: URL → fetch → return | _Two_: URL → fetch → `@Web`* output,<br>then agent interprets |
| **Instrumental Access** | _Full_: can inspect `ToolResult.content` directly | _Partial_: can only read agent output or<br>manually copy `@Web` result |
| **Repeatability** | _High_: same URL yields identical API response | _Medium_: LLM interpretation varies, but<br>`@Web` raw content should be stable |
| **Fetch Mechanisms** | _One_ web fetch tool | _Multiple_: `@Web`, `mcp-server-fetch`,<br>`fetch-browser-mcp`, third party |
| **Best Findings** | _Hard limits_, Claude API truncates at ~100 KB | _Comparative limits_: _does MCP override `@Web`? Does agent auto-chunk?_ |

>_*Results logged as "Methods tested: `@Web`" reflect prompt, user-facing syntax. However, post-analysis revealed testing misused `@Web` as a
>fetch command rather than a context attachment mechanism. The backend mechanisms `WebFetch`, `mcp_web_fetch` possibly invoked autonomously by
>Cursor regardless of `@Web syntax`, visit [Friction Note](friction-note.md#web-evolution-from-manual-context-to-automatic-agent-capability) for analysis._

---

## Track Design

| | **Interpreted** | **Raw** |
| - | -------------------- | ------------- |
| **Question** | _What does Cursor report back? Does it accurately perceive truncation? Are there systematic estimation errors?_* | _What actually came through the `@Web` command? Where exactly does truncation occur? Is the boundary consistent?_ |
| **Method** | Chat prompt asks `@Web` to fetch URL and report measurements | Chat prompt asks `@Web` to fetch URL and return output verbatim, human manually extracts measurements |
| **Captures** | Cursor and underlying LLM's interpretation of truncation, completeness | Actual response content from `@Web` command, post-processing, exact character boundaries |
| **Measurements** | LLM estimates: _"appears truncated,"_ _"approximately X KB,"_ _"markdown seems complete"_ | _Manual_: character count via `len()`, token count via `tiktoken`, exact truncation point, last 50 characters |
| **Repeatability** | Varies between runs | _Reproducible_: same URL fetched multiple times yields consistent content |
| **Best For** | Understanding DX, identifying perception gaps | Citable baseline measurements<br>for Agent-Friendly Docs Spec |

> _Approach limitations: general variation between runs; can't programmatically inspect a surfaced API field; variation expected between MCP server >versions, IDE version, LLM selection; some URLs possibly gated_

---

## Cursor-Specific Unknowns

| **Question** | **Details** | **Approach** | **Value** |
| ---------- | --------- | ------------------ | ---------------- |
| **Multiple Fetch Mechanisms** | `@Web` native, proprietary `mcp-server-fetch` configurable; `fetch-browser-mcp` headless browser; third party servers | Compare side-by-side on identical URLs | Determines if one mechanism has different limits; unique to Cursor, addresses ecosystem testing gap |
| **HTML-to-Markdown Conversion Timing** | **_Does Cursor truncate before or after HTML→markdown conversion?_** | `SC-1`-`SC-4` measure truncation relative to content structure | **Pre-conversion**: lose 40-50% of characters to HTML/CSS overhead<br>**Post-conversion**: Markdown smaller, but structure may break at boundary |
| **Agent Auto-chunking** | **_After truncation, does `@Web` automatically request next chunk or require manual request?_** | `OP-4` agent retry pattern: observe unprompted follow-up fetches | Not well-explored in Claude API testing; key gap in ecosystem methodology, shapes DX with large docs |
| **Model Variability** | Cursor's `Auto` chat default setting; additionally supports Claude's `Opus`, `Sonnet`, `Gemini`, `GPT-5` | Run tests with one LLM, tracked per run | Isolates fetch behavior from LLM inference variance; differences documented separately |
