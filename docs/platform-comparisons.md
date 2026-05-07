---
layout: default
title: Platform Findings
permalink: /docs/platform-comparisons/
---

# Platform Comparisons

| **Section** | **Description** |
| ----------- | ------------------ |
| **[Retrieval](#retrieval)** | How and when an agent fetches content |
| **[Summarization](#summarization)** | What happens to content before the orchestrator receives it |
| **[Truncation](#truncation)** | What gets lost and whether agents report it |

## Retrieval

>_The web fetch gap isn't in retrieval, but in what follows: how agents attend to various content types during generation, whether that's context window handling, chunking losses, or summarization. Platform links lead to each tool's official documentation._

---

| **Platform** | **Prompt Syntax** | **Invocation Pattern** | **Retrieval Behavior** |
| ---------- | ------------ | -------------------- | ----------------------- |
| **[Claude API web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)** | Enable tool to augment Claude's context with URL | _Mid-generation deterministic_: tool requires enablement in API request, includes URL validation and results cache, may or may not provide live web content | _Visibility high_: only platform where response body includes raw tool result; no JavaScript execution, CSS-heavy pages and/or SPAs often return little to no prose |
| **[Cursor](https://cursor.com/docs)** | _No web fetch behavior publicly documented_, `@Web` context attachment redundant, agents don't correct misuse | _Mid-generation nondeterministic_: `Auto` default setting autonomous LLM and fetch method selection per request | _Visibility low_: fetch method not explicitly named, no JavaScript execution, CSS-heavy pages and/or SPAs often return little to no prose; prefers Markdown, content negotation documented with `Accept: text/markdown`; sends full browser fingerprint: `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36` with Chrome client hints `Sec-Ch-Ua`, `Sec-Fetch-*` |
| **[Gemini API URL context](https://ai.google.dev/gemini-api/docs/url-context)** | Enable tool to augment Gemini's context with URL, request requires `url_context` with full, unnested URLs | _Pre-generation injection deterministic_: two-step process, fetches from internal cache, if unsuccessful, then live fetch; documentation includes parsing limitations | _Visibility low_: retrieved content injected into context without a testable field, retrieval orchestration and generation process opaque; `url_context_metadata` order _nondeterministic_, authoritative signal `url_retrieval_status`, `tool_use_prompt_token_count` only size proxy |
| **[GitHub Copilot](https://docs.github.com/en/copilot)** | _No web fetch behavior publicly documented_, prompt with URL | _Mid-generation nondeterministic_: `Auto` default setting autonomous LLM and fetch method selection per request | _Visibility medium_: intermittently tools named via error, `fetch_webpage` returns relevance-ranked excerpts with elision markers, occasional nonlinear, inaccurate reassembly, `curl` byte-perfect retrieval, but no prose; content negotiation tool-dependent, presents as a browser, but overclaims `User-Agent`: `Mozilla/5.0`, `AppleWebKit` `Accept`: full HTML, `curl/8.7.1` no preference,`Accept`: `*/*` |
| **[OpenAI web search](https://developers.openai.com/api/docs/guides/tools-web-search)** | Chat Completions API augments `GPT`'s search with URL, Responses API for `web_search` | _Mid-generation nondeterministic: integration and agent-dependent_: static facts and trivial math don't invoke the tool; Chat Completions search implicit, Responses `web_search_preview` conditional, control cached/indexed or live content `external_web_access` | _Visibility low_: Responses `response.output`'s `web_search_call` names tools, but search context not equal to LLM context window; no JavaScript execution; `search_context_size: low/medium/high` controls context amount, Chat Completions latency lever consistent, but Responses inconsistent |
| **[Windsurf Cascade](https://docs.windsurf.com/windsurf/cascade/web-search)** | Web and docs search partially documented, `@web` directive redundant with URL, agents don't correct misuse | _Mid-generation deterministic_: autonomous two-stage pipeline designed to emulate human browsing and skimming, documentation acknowledges not all pages parseable | _Visibility medium_: `read_url_content` returns chunk index with summaries, metadata and requires sequential `view_content_chunk` calls; `curl` substitution for CSS-heavy pages, SPAs return ~20–35% of expected size, little or no prose; agents used `@web`'s `web_search` as verification once every ~60 turns; presentation transparent about using crawler-scaper, but underdelivers, `User-Agent`: [Colly](https://github.com/gocolly/colly) |
{: .table-architecture}

## Summarization

>_While default settings abstract orchestrator-subagent relationships away, platforms offer agent configuration,
which is outside this testing's scope. Observable outputs inform the conclusions below. Platform links lead to testing methodologies._

---

| **Platform** | **Processing Layer** | **Inference** |
| ---------- | -------------------- | ------------ |
| **[Claude API<br>web fetch](./anthropic-claude-api-web-fetch-tool/methodology.md)** | _Dynamic filtering optional,_<br>`web_fetch_20260209` | Server-side tool called directly with inspectable tool result in response. [Dynamic filtering](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) available with certain LLMs in which Claude writes, executes code to filter before content reaches the context window, but it's not default behavior. |
| **[Cursor](./anysphere-cursor/methodology.md)** | _Inferred via filtering, undocumented<br>for web fetch_ | Codebase research, terminal commands, and browser automation requests trigger [built-in subagents](https://cursor.com/docs/subagents) `explore`, `bash`, and `browser`. AET prompts likely invoked `explore` and `bash` alongside web fetch. Backend routing and structure-aware content filtering suggest a pre-generation processing layer, not a passive, linear pipeline. |
| **[Gemini API<br>URL context](./google-gemini-url-context-tool/methodology.md)** | _API layer pipeline,<br>undocumented_ | Pre-generation injection suggests processing occurs before LLM invocation. No transformation layer between retrieval and generation; LLM receives content directly and any summarization occurs as part of generation, not as an intermediate pipeline stage. |
| **[GitHub<br>Copilot](./microsoft-github-copilot/methodology.md)** | _Inferred via<br>relevance-ranking, undocumented<br>for web fetch_ | Reassembled excerpts, outputs that don't note discarded content, browser masquerading, and tool substitution patterns suggests an orchestrator-subagent relationship and not a linear, passive pipeline, but [Copilot docs](https://docs.github.com/en/copilot/how-tos/copilot-sdk/use-copilot-sdk/custom-agents) describe subagents as configurable, and not default architecture. |
| **[OpenAI<br>web search](./open-ai-web-search-tool/methodology.md)** | _Differs by API surface,<br>undocumented_ | Chat Completions autonomously retrieves, but Responses' LLM actively manages search in the chain of thought with `open_page` and `find_in_page`, suggesting a processing layer, but not explicitly documented or named in either API responses. |
| **[Windsurf<br>Cascade](./cognition-windsurf-cascade/methodology.md)** | _Inferred via chunking, undocumented for web<br>and docs search_ | Codebase research triggers [built-in subagent Fast Context](https://docs.windsurf.com/context-awareness/fast-context). AET prompts likely invoked Fast Context alongside web search. Chunk analysis, tool substitution, terminal execution, and workspace referencing suggest an extensive processing layer, not a passive, linear pipeline. |
{: .table-summarization}

## Truncation

>_Pipelines are lossy by design in attempt to balance token cost, speed, and access to fresh content.
> Agents intermittently acknowledge architectural constraints, misattribute truncation causes, or self-report completeness
>when content is incomplete or unusable. Platform links lead to interpreted vs. raw track analysis_.

---

| **Platform** | **Truncation Limit** | **Observations** |
| ---------- | ----------------- | ------- |
| **[Claude API web fetch](./anthropic-claude-api-web-fetch-tool/claude-interpreted-vs-raw.md)** | ~20,700 chars and/or<br>~100 KB of rendered content<br>_default unset_ | `max_content_tokens` approximate, setting 5,000 returned 17,186 chars, truncation occurs mid-token. Default limit identified in raw track, self-report attributed missing content to JavaScript rendering, masking character limit. |
| **[Cursor](./anysphere-cursor/cursor-interpreted-vs-raw.md)** | 28 KB–240 KB+<br>_method-dependent_,<br>_nondeterministic filtering_ | `WebFetch MCP` ~28 KB, `urllib` ~72 KB, unknown path 245 KB+, `curl` no ceiling detected; appears to apply structure-aware content filtering, navigation and CSS stripped, but content selection heuristic presents as complete, so agents don't report truncation. |
| **[Gemini API<br>URL context](./google-gemini-url-context-tool/gemini-interpreted-vs-raw.md)** | _No fixed ceiling or silent dropping detected_,<br>20 URLs hard limit<br>per request | API-layer rejection returns `400` and doesn't consume tokens; retrieval-layer failure completes the request, but records `URL_RETRIEVAL_STATUS_ERROR`. Format support inconsistent with documentation: PDF fails, YouTube succeeds, JSON nondeterministic; Google Docs fail consistently. |
| **[GitHub<br>Copilot](./microsoft-github-copilot/copilot-interpreted-vs-raw.md)** | _No fixed ceiling detected,_<br>_nondeterministic excerpting_,<br> tested 6.68M tokens | Pipeline with `fetch_webpage` discards whole sections or more granularly before generation, `curl` delivers all raw bytes but unreadable, chat rendering cutoff visible in output, not persisted as requested, but agents don't reliably report these results as truncation. |
| **[OpenAI<br>web search](./open-ai-web-search-tool/chatgpt-interpreted-vs-raw.md)** | _No fixed ceiling or silent dropping detected_ | Raw source count stable at 12 regardless of `search_context_size` setting. Query construction not temporally aware, internal queries append training-era date strings despite running in 2026. Documented domain filtering limits not functional in Python SDK. |
| **[Windsurf Cascade](./cognition-windsurf-cascade/cascade-interpreted-explicit-vs-raw.md)** | _No fixed ceiling detected at retrieval stage_, _nondeterministic agent-dependent write ceiling_ | Full retrieval agent and doc-size-dependent. Agents often retrieve fully under ~14 chunks, spotty at ~35, sparse sampling at 50+. Chunk index summary population not guaranteed, those present often include byte-count loss notices. Unique read-write asymmetry. Agents often self-report full retrieval, but fail to prove it with a write task or report truncation. |
{: .table-truncation}
