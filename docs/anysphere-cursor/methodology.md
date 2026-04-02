---
layout: default
title: "Methodology"
permalink: /docs/anysphere-cursor/methodology
parent: Anysphere Cursor
---

## Methodology

---

_**Chat-based measurement through interaction, without direct code instrumentation**_

>_software instrumentation is the process of adding code to a system
to collect data about how it works; while the Cursor chat is public and accessible,
testing it is different than calling an API to extract measurements programmatically_

---

_**Testing a closed consumer application vs an open API**_

Rather than target specific API endpoints with documented interfaces,
Cursor testing targets consumer application with proprietary chat
behavior and multiple fetch mechanisms. Cursor's chat web fetch and MCP
implementations don't have a public API; MCP servers are user-configured,
implementations vary - `mcp-server-fetch`, `fetch-browser-mcp`, third-party -
and are observable through Cursor's agent behavior, but not
instrumentable. Compare to this collection's
[Claude API Web Fetch testing](/docs/anthropic-claude-api-web-fetch-tool/methodology) -

| **Aspect** | **Claude API Testing** | **Cursor Testing** |
| -------- | ------------------- | ----------------- |
| **Interface** | Python API call, response object available | Chat interface, observable only through output |
| **Layers** | Single: URL → fetch → return | Two: URL → fetch → `@Web`* output, then model interprets |
| **Instrumental Access** | Full: can inspect `ToolResult.content` directly | Partial: can only read model's output or manually copy `@Web` result |
| **Repeatability** | High: same URL yields identical API response | Medium: model interpretation varies, but `@Web` raw content should be stable |
| **Fetch Mechanisms** | One web fetch tool | Multiple - `@Web`, mcp-server-fetch, fetch-browser-mcp, third-party |
| **Best Findings** | Hard limits - Claude API truncates at ~100KB | Comparative limits - _does MCP override `@Web`? Does agent auto-chunk?_ |

>_*All results logged as "Methods tested: `@Web`" reflect user-facing syntax
used in prompts. However, post-analysis revealed testing misused `@Web` as a
fetch command rather than a context attachment mechanism. The actual backend
mechanisms: `WebFetch`, `mcp_web_fetch` possibly invoked autonomously by
Cursor regardless of `@Web syntax` - read
[Friction Note](friction-note.md#web-evolution-from-manual-context-to-automatic-agent-capability)
for full impact analysis._

---

**Goal**: use Cursor IDE with two complementary tracks -
interpreted catches perception gaps, while the raw
produces reproducible numbers for documentation -

| | **Cursor-interpreted Track** | **Raw Track** |
| - | -------------------- | ------------- |
| **Question** | _What does Cursor report back? Does it accurately perceive truncation? Are there systematic estimation errors?* | _What actually came through the `@Web` command? Where exactly does truncation occur? Is the boundary consistent?_ |
| **Method** | Chat prompt asks `@Web` to fetch URL and report measurements | Chat prompt asks `@Web` to fetch URL and return output verbatim, human manually extracts measurements |
| **Captures** | Cursor's, and the underlying model's, interpretation of truncation and completeness | Actual response content from `@Web` command, post-processing, exact character boundaries |
| **Measurements** | Model estimates: "appears truncated," "approximately X KB," "markdown seems complete" | Manual: character count via `len()`, token count via `tiktoken`, exact truncation point, last 50 characters |
| **Repeatability** | Varies between runs due to model variance | Reproducible - same URL fetched multiple times yields consistent content |
| **Best For** | Understanding DX, surfacing perception gaps | Citable baseline measurements for the Agent Docs Spec |

> _Known limitations of this approach: interpreted-track varies between runs; can't programmatically
>inspect a surfaced API field; variation is also expected between MCP server versions,
>IDE version, and model selection; some test URLs may be gated_

### Cursor-Specific Unknowns

| **Question** | **Details** | **Approach** | **Value** |
| ---------- | --------- | ------------------ | ---------------- |
| **Multiple Fetch Mechanisms** | `@Web` - native, proprietary; `mcp-server-fetch` - configurable; `fetch-browser-mcp` - headless browser; third-party MCP servers, such as Oxylabs | Compare side-by-side on identical URLs | Determines if one mechanism has different limits; unique to Cursor, addresses ecosystem testing gap |
| **HTML-to-Markdown Conversion Timing** | **_Does Cursor truncate before or after HTML→markdown conversion?_** | Tests `SC-1` through `SC-4`: measure truncation relative to content structure | **Pre-conversion**: lose 40-50% of characters to HTML/CSS overhead; **Post-conversion**: Markdown smaller but structure may break at boundary |
| **Agent Auto-chunking** | **_After truncation, does `@Web` automatically request next chunk or require manual request?_** | Test `OP-4`, Agent Retry Pattern: observe unprompted follow-up fetches for large URLs | Not well-explored in Claude API testing; key gap in ecosystem methodology, shapes DX with large docs |
| **Model Variability** | Cursor's `Auto` appears to be chat default; additionally supports Claude's `Sonnet`, `Opus`, Gemini, `GPT-5`| Run tests with single consistent model, documented per run | Isolates fetch behavior from model inference variance; divergences documented separately |
