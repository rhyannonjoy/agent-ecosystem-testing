---
layout: default
title: Platform Findings
permalink: /docs/platform-findings/
---

# Platform Findings

---

## Architecture Comparison

>_The web fetch gap isn't in retrieval, but between retrieval and utilization, suggesting that the bottleneck
isn't the fetch pipeline, but what happens to content after retrieval, whether that's context window
handling, chunking losses, or how agents attend to various content types during generation._
>_Platform links lead to public documentation._
---

| **Platform** | **Prompt Syntax** | **Invocation Pattern** | **Retrieval Behavior** |
| ---------- | ------------ | -------------------- | ----------------------- |
| **[Claude API web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)** | Enable tool to augment Claude's context with URL | _Mid-generation deterministic_: tool requires enablement in API request, includes URL validation and results cache, may or may not provide live web content | _Visibility high_: only platform where response body includes raw tool result; no JavaScript execution, CSS-heavy pages and/or SPAs often return little to no prose |
| **[Cursor](https://cursor.com/docs)** | _No web fetch behavior publicly documented_, `@Web` context attachment redundant, agents don't correct misuse | _Mid-generation nondeterministic_: `Auto` default setting autonomous LLM and fetch method selection per request | _Visibility low_: fetch method not explicitly named, no JavaScript execution, CSS-heavy pages and/or SPAs often return little to no prose; prefers Markdown, content negotation documented with `Accept: text/markdown` |
| **[GitHub Copilot](https://docs.github.com/en/copilot)** | _No web fetch behavior publicly documented_, prompt with URL | _Mid-generation nondeterministic_: `Auto` default setting autonomous LLM and fetch method selection per request | _Visibility medium_: intermittently tools named via error, `fetch_webpage` returns relevance-ranked excerpts with elision markers, occasional nonlinear, inaccurate reassembly, `curl` byte-perfect retrieval, but no prose; content negotiation tool-dependent, presents as a browser, but overclaims `User-Agent`: `Mozilla/5.0`, `AppleWebKit` `Accept`: full HTML, `curl/8.7.1` no preference,`Accept`: `*/*` |
| **[Windsurf Cascade](https://docs.windsurf.com/windsurf/cascade/web-search)** | Web and docs search partially documented, `@web` directive redundant with URL, agents don't correct misuse | _Mid-generation deterministic_: autonomous two-stage pipeline designed to emulate human skimming, acknowledges not all pages parseable | _Visibility medium_: `read_url_content` returns chunk index with summaries, metadata and requires sequential `view_content_chunk` calls; `curl` substitution for CSS-heavy pages, SPAs return ~20–35% of expected size, little or no prose; `@web`'s `web_search` used as verification once every ~60 turns; presentation transparent about using crawler-scaper, but underdelivers, `User-Agent`: [Colly](https://github.com/gocolly/colly) |
| **[Gemini API URL context](https://ai.google.dev/gemini-api/docs/url-context)** | Enable tool to augment Gemini's context with URL, request requires `url_context` with full, unnested URLs | _Pre-generation injection deterministic_: two-step process, fetches from internal cache, if unsuccessful, then live fetch; documents parsing limitations | _Visibility low_: retrieved content injected into context without a testable field, retrieval orchestration and generation process opaque; `url_context_metadata` order _nondeterministic_, authoritative signal `url_retrieval_status`, `tool_use_prompt_token_count` only size proxy |
| **OpenAI web search** | Differs by API surface | _Mid-generation nondeterministic: conditional, agent-dependent_: static facts and trivial math don't invoke the tool | _Low_: not applicable for JS rendering; domain filtering documented, but not functional in Python SDK; `search_context_size: low/medium/high` Chat Completions API latency lever consistent, inconsistent in Responses API |
{: .table-architecture}

## Truncation Analysis

>_Lossy by design, balance speed, cost, and access to fresh data_.
>_Platform links lead to interpreted vs raw track analysis_.

---

| **Platform** | **Truncation Limit** | **Observations** |
| ---------- | ----------------- | ------- |
| **[Claude API web fetch](./anthropic-claude-api-web-fetch-tool/claude-interpreted-vs-raw.md)** | Truncation intended to control token usage; ~20,700 chars<br>default, unset | `max_content_tokens` parameter is approximate, setting 5,000 returned 17,186 chars. Truncation occurs mid-token. CSS stripped effectively. HTML boilerplate 81–97.5% before first heading; markdown reduces boilerplate 77%. JS-rendered pages return static shell only. |
| **[Cursor](./anysphere-cursor/cursor-interpreted-vs-raw.md)** | 28KB–240 KB+<br>method-dependent | Behavior varies by backend: `WebFetch MCP` ~28KB, `urllib` ~72KB, other routes 240KB+. Auto routing is opaque; Cursor selects fetch mechanism autonomously. Falls back to `curl`, unfiltered HTML, 16 MB+ observed on timeout. |
| **[GitHub<br>Copilot](./microsoft-github-copilot/copilot-interpreted-vs-raw.md)** | _No fixed ceiling detected_<br> tested 6.68M tokens | _Lossy by design_:`fetch_webpage` performs relevance-ranked semantic excerpts with elision markers. No size limit detected across 55 runs. `curl` substitution delivers full byte-perfect retrieval. Auto model routing dispatches across multiple models with no documented routing logic. |
| **[Windsurf Cascade](./cognition-windsurf-cascade/cascade-interpreted-explicit-vs-raw.md)** | _No fixed ceiling at retrieval_, agent-dependent write ceiling | _Lossy by design_: full retrieval agent- and doc-size-dependent. Agents often retrieve fully under ~14 chunks, spotty at ~35, sparse sampling at 50+. Per-chunk truncation present; some chunk summaries include byte-count loss notices. Read-write asymmetry confirmed: agents that self-report full retrieval frequently fail to reproduce content. |
| **[Gemini API<br>URL context](./google-gemini-url-context-tool/gemini-interpreted-vs-raw.md)** | _No fixed ceiling detected_<br>20 URL hard limit per request | Docs state 34 MB max fetch size per URL, but this is a retrieval ceiling, not a processing limit. `400 INVALID_ARGUMENT` if URL limit exceeded, zero tokens consumed. Tested on `gemini-2.5-flash` only. Format support inconsistent with documentation: PDF fails despite being documented as supported; YouTube succeeds despite being documented as unsupported; JSON non-deterministic; Google Docs return `URL_RETRIEVAL_STATUS_ERROR` consistently.|
| **[OpenAI<br>web search](./open-ai-web-search-tool/chatgpt-interpreted-vs-raw.md)** | _No fixed ceiling detected_ | 128K token context window. `search_context_size`, low/medium/high,  controls context amount but no per-page truncation limit is surfaced. Truncation of retrieved content occurs pre-generation and isn't observable via the API |
{: .table-truncation}
