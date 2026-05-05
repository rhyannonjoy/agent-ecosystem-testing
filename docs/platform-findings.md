## Architecture Comparison

| **Platform** | **Prompt Syntax** | **Invocation Pattern** | **Retrieval Visibility** |
| ---------- | ------------ | -------------------- | ----------------------- |
| **Claude API web fetch** | Enable tool, prompt with URL | _Mid-generation deterministic_: tool must be explicitly enabled in API request | _High_: only platform where response body includes raw tool result; static shell only |
| **Cursor** | `@Web` context attachment redundant with URL, current version calls autonomously | _Mid-generation nondeterministic_: `Auto` default setting autonomous LLM and method selection per request | _Low_: static shell only, backend selection not explicitly named, but _only_ platform to show content negotation patterns sending `Accept: text/markdown` |
| **GitHub Copilot** | _Not publicly documented_, prompt with URL | _Mid-generation nondeterministic_: `Auto` default setting autonomous LLM and method per request | _Low_: intermittent toolchain visibility via error codes and/or explicit request, `fetch_webpage` returns relevance-ranked semantic excerpts with elision markers, intermittent nonlinear, inaccurate reassembly; `curl` substitution returns byte-perfect retrieval |
| **Windsurf Cascade** | `@web` redundant with URL | _Mid-generation deterministic_, autonomous two-stage pipeline | _Medium_: `read_url_content` returns chunk index with summaries, metadata; per-chunk content requires sequential calls; SPAs and CSS-heavy pages return ~20–35% of expected rendered size |
| **Gemini API URL context** | Request requires `url_context` | _Pre-generation injection deterministic_: fetches from internal cache, if unsuccessful, then live fetch; `url_context_metadata` order is non-deterministic. | _Low_: retrieved content injected into context without a testable field; JS rendering not tested; `tool_use_prompt_token_count` is the only size proxy |
| **OpenAI web search** | Differs by API surface | _Mid-generation nondeterministic: conditional, agent-dependent_: static facts and trivial math don't invoke the tool | _Low_: not applicable for JS rendering; domain filtering documented, but not functional in Python SDK; `search_context_size: low/medium/high` Chat Completions API latency lever consistent, inconsistent in Responses API |
{: .table-architecture}

## Truncation Analysis

| **Platform** | **Truncation Limit** | **Observations** |
| ---------- | ----------------- | ------- |
| **Claude API<br>web fetch** | ~20,700 chars<br>default, unset | `max_content_tokens` parameter is approximate, setting 5,000 returned 17,186 chars. Truncation occurs mid-token. CSS stripped effectively. HTML boilerplate 81–97.5% before first heading; markdown reduces boilerplate 77%. JS-rendered pages return static shell only. |
| **Cursor** | 28KB–240 KB+<br>method-dependent | Behavior varies by backend: `WebFetch MCP` ~28KB, `urllib` ~72KB, other routes 240KB+. Auto routing is opaque; Cursor selects fetch mechanism autonomously. Falls back to `curl`, unfiltered HTML, 16 MB+ observed on timeout. |
| **GitHub<br>Copilot** | _No fixed ceiling detected_<br> tested 6.68M tokens | _Lossy by design_:`fetch_webpage` performs relevance-ranked semantic excerpts with elision markers. No size limit detected across 55 runs. `curl` substitution delivers full byte-perfect retrieval. Auto model routing dispatches across multiple models with no documented routing logic. |
| **Windsurf Cascade** | _No fixed ceiling at retrieval_, agent-dependent write ceiling | _Lossy by design_: full retrieval agent- and doc-size-dependent. Agents often retrieve fully under ~14 chunks, spotty at ~35, sparse sampling at 50+. Per-chunk truncation present; some chunk summaries include byte-count loss notices. Read-write asymmetry confirmed: agents that self-report full retrieval frequently fail to reproduce content. |
| **Gemini API<br>URL context** | _No fixed ceiling detected_<br>20 URL hard limit per request | Docs state 34 MB max fetch size per URL, but this is a retrieval ceiling, not a processing limit. `400 INVALID_ARGUMENT` if URL limit exceeded, zero tokens consumed. Tested on `gemini-2.5-flash` only. |
| **OpenAI<br>web search** | _No fixed ceiling detected_ | 128K token context window. `search_context_size`, low/medium/high,  controls context amount but no per-page truncation limit is surfaced. Truncation of retrieved content occurs pre-generation and isn't observable via the API |
{: .table-truncation}
