---
layout: default
title: "Methodology"
permalink: /docs/cognition-windsurf-cascade/methodology
parent: Cognition Windsurf Cascade
---

# Methodology

---

## Turn-by-Turn

>_**Chat-based measurement through interaction, without direct code instrumentation**_

The Cascade testing framework is the third in a series of chat-based agent
testing frameworks in this collection, following
[Cursor](/docs/anysphere-cursor/methodology) and
[Copilot](/docs/microsoft-github-copilot/methodology). Each platform has
surfaced a different relationship between user-facing fetch syntax and actual
agent behavior - a pattern that directly shapes this framework's design.

---

## Syntax Comparison

>_**An evolving relationship between fetch syntax and agent behavior**_

Across three platforms, the role of explicit web fetch directives has shifted in a consistent
direction. This pattern: _**explicit syntax → autonomous behavior → documented-but-effect-unknown**_,
is the central methodological question Cascade testing inherits from the two prior frameworks. The
three-track design below exists specifically to isolate `@web` as a variable, rather than assume its
effect in either direction.

| **Platform** | **Syntax** | **Testing Reveal** |
| ------------ | ---------------------- | ------------------------- |
| **Cursor** | `@Web` context attachment, undocumented | Inclusion unnecessary as capability autonomous<br>when testing began; `WebFetch`, `mcp_web_fetch` called regardless of `@Web` syntax |
| **Copilot** | _None documented_ | No user-invocable syntax exists; testing identified<br>`fetch_webpage` in agent output |
| **Cascade** | `@web` directive,<br>partially documented | _Does invoking `@web` change retrieval behavior,<br>ceiling, tool chain, chunking?_ |

## Architecture Comparison

>_**Testing a closed consumer application vs an open API**_

Rather than target specific API endpoints with documented interfaces, Cascade testing targets a consumer
application with proprietary chat behavior and a partially documented tool layer. Cascade's web fetch
implementation surfaces three named tools: `read_url_content` for direct URL fetch, `view_content_chunk`
for paginating large documents via `DocumentId`, and `search_web` for query-based lookup, reported by
Cascade itself during runs. These tools are partially documented, without many details. Compare with the
methodology of the [Claude API testing](/docs/anthropic-claude-api-web-fetch-tool/methodology),
in which fetch behavior is directly inspectable via `tool_result`.

| **Aspect** | **Cursor** | **Copilot** | **Cascade** |
| -------- | ------------------- | ----------------- | ----------------- |
| **User Fetch Syntax** | `@Web` context attachment | _None_ | `@web` directive |
| **Tools Observed** | `WebFetch`, `mcp_web_fetch` | `fetch_webpage`<br>and/or `curl` | `read_url_content`, `search_web`, `view_content_chunk` |
| **Repeatability** | _Medium_ | _Low_, agent routing variance | _Low_, approval interaction may<br>affect routing |
| **Questions** | _Does MCP override `@Web`?<br>Does agent auto-chunk?_ | _Does `fetch_webpage` have a consistent ceiling? Does it vary by agent?_ | _Does `@web` change the ceiling, tool chain, or chunking behavior?_ |

## Track Design

| | **Interpreted** | **Explicit** | **Raw** |
| - | -------------------- | ------------- | ------------------ |
| **Question** | _What does Cascade report back without steering? Does it accurately perceive truncation?_ | _Does adding `@web` change truncation limits, tool chain, or chunking behavior?_ | _What does `read_url_content`<br>actually return?<br>Where exactly does truncation occur?_ |
| **Method** | Fetch URL, report measurements;<br>no `@web` | Identical to interpreted track, prefixed with `@web` | Fetch URL, return output verbatim; no `@web`; verification script extracts measurements |
| **Measurements** | Model estimates: _"appears truncated at ~X chars," "Markdown seems complete"_ | Same as interpreted track; compared against implicit baseline | Character count via `len()`, token count via `tiktoken`, exact truncation point,<br>last 50 characters |
| **Repeatability** | _Low_, approval interaction may affect routing |  _Medium_, `@web` may stabilize tool selection | _Medium_, same URL should yield consistent `read_url_content` output |
| **Best For** | Understanding DX; surfacing **approval-gated fetch**, _does approval-gating affect routing consistency?_ | **`@web` effect on ceiling** - _does `@web` change or repeat the Cursor finding that the directive is redundant?_ | **Auto-pagination behavior** - _does `view_content_chunk` paginate automatically, or only when prompted?_ |

> _**Limitations**: variations between runs; `read_url_content` requires approval before fetch executes, approval interaction itself may influence routing and logged per run while `view_content_chunk` pagination via `DocumentId` only partially observable through agent thought panel and self-report._
