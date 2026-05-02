---
layout: default
title: "Cursor-interpreted vs Raw"
nav_order: 2
permalink: /docs/anysphere-cursor/cursor-interpreted-vs-raw
parent: Anysphere Cursor
---

# Cursor-Interpreted vs Raw

---

## Track Design

**Interpreted** track captures what the agent _believes_ it retrieved: how much content it saw,
whether the fetch was complete, how it characterizes truncation. This is the agent's self-report.

**Raw** track captures what Cursor _actually saved to disk_: exact byte counts, hexdump analysis,
MD5 checksums, and token counts. These are filesystem measurements, cryptographic hashes, and not
agent estimates.

The gap between the two tracks is a finding. If Cursor reports _"content complete"_ in prose,
but the raw data shows truncation, that discrepancy belongs in the spec.

| | **Interpreted** | **Raw** |
| - | ---------------------- | -------------------------- |
| **Measures** | Agentic retrieval interpretation | Filesystem measurements<br>of saved output |
| **Character Counts** | Agent estimates, vary 2-3× across sessions on small files | `wc -c` on disk - exact,<br>reproducible |
| **Completeness** | Agentic truncation assessment<br>in prose | MD5 comparison, hexdump analysis, fence counting |
| **Token<br>Counts** | Agent estimates,<br>~4 chars/token assumption | OpenAI encoding with `tiktoken` |
| **Reproducibility** | High variance on small docs, 1.9KB→5.6KB same URL | Perfect reproducibility,<br>same URL = same MD5 |
| **Output<br>Format** | Chat UI Markdown rendering | Raw file on disk, _`raw_output_{test_id}.txt`_ |
| **Best For** | Understanding agent<br>perception gaps | Citable measurements<br>for the spec |

## Key Observations

1. **Reproducibility in Raw vs High Variance in Interpreted**

    **Raw**: Same URL produces identical output
    - `BL-1`: MD5 `d6ad8451d3778bf3544574431203a3a7` across 2 runs
    - `OP-4`/`BL-3`: MD5 `554eb56e8416d86d12af17a2dfe6f815` across 3 runs
    - Character-for-character identical output on disk

    **Interpreted**: Same URL produces 2-3× variance on small files
    - `BL-1` r1: 1,953 chars → r2: 5,595 chars → r3: 4,100 chars, 2.9× variance
    - `BL-2` r1: 1,953 chars → r2: 4,200 chars → r3: 4,350 chars, 2.2× variance

    **Conclusion**: the variance is in how Cursor _displays_ content in chat UI,
    not what it fetches. Raw measurements prove the underlying fetch is deterministic,
    but that interpreted track shows UI rendering isn't.

2. **Size-Dependent Consistency**

    Small file rendering appears unreliable, while larger ones seem stable:

    **Interpreted**:
    - Small files, 20-87 KB: high session-to-session variance
    - Large files, 245 KB: <1% variance, nearly identical across runs

    **Raw**:
    - Small files, 4.8 KB output: identical MD5s despite variance in interpreted display
    - Large files, 245 KB output: identical MD5s, consistent across runs

    **Conclusion**: Cursor fetches consistently at all sizes. The interpreted variance
    on small files is possibly a _UI rendering artifact_, not entirely reflective of fetch
    behavior.

3. **Perception Gap: Model Self-Report is Unreliable**

    Agent claims _"complete"_ or _"no truncation"_ when content is a filtered subset:

    | **Test** | **Raw** | **Interpreted** | **Gap** |
    | --- | --- | --- | --- |
    | **`SC` `3`** | 38 KB<br>truncated<br>at ref #14/252 | _"Complete<br>reference<br>section"_ | Agent interprets filtered<br>list as complete |
    | **`BL`<br>`1`** | 4,817 B<br>calculated | 1,953 chars displayed | UI shows subset, agent<br>reports what it sees |
    | **`SC` `4`** | Truncated mid-word at _"updated"_ | _"All syntax<br>sections<br>present"_ | Clean structure masks incompleteness |

    **Conclusion**: _**trust character counts, not prose assertions**_;
    agent perceives filtered excerpts as complete because they're internally coherent.

4. **Method-Specific Truncation Limits - Raw**

    - **`WebFetch`, `MCP-style`**: ~28 KB ceiling, `SC-4` truncated at 27,890 chars
    - **`urllib.request`**: ~72 KB ceiling, `EC-6` truncated at 72,600 chars
    - **`curl fallback`**: No ceiling detected, `SC-2` returned 17.6 MB
    - **Unknown Path**: No ceiling detected, `OP-4`/`BL-3` returned 245 KB

    **Conclusion**: Cursor routes to many mechanisms with different limits. The interpreted
    track didn't identify this because the agent's self-report didn't consistently include
    its toolchain.

5. **Intelligent Content Filtering**

    Cursor performs structure-aware filtering, but the raw track provided the measurements:

    **Interpreted**: agent reports receiving "main content" but missing footer/navigation

    **Raw**: proves it via byte counts
    - `BL-1`: 85 KB HTML → 4.8KB Markdown, 94% reduction, CSS/navigation stripped
    - `SC-3`: 252 references → deterministically selects #14, the first commercial source
    - `SC-4`: 30 KB page → 28KB, footer/metadata filtered

    **Conclusion**: Cursor applies content heuristics, not blind truncation. Raw track quantifies what
    interpreted track observes qualitatively.

6. **Chars/Token Ratio as Content-Type Classifier - Raw**

    - `EC-3`: JSON: 2.62 chars/token
    - `SC-2`: Raw HTML/JS: 2.65 chars/token
    - `SC-3`: Tables: 3.06 chars/token
    - `SC-4`, `OP-4`: Docs + code: 3.91-4.37 chars/token
    - `BL-1`, `BL-2`, `SC-1`: Clean Markdown: 4.13-4.36 chars/token

    **Conclusion**: Chars/token ratio enables content-type classification without parsing. <3.0 = code/markup, >4.0 = prose.
    Useful for automated analysis pipelines. The interpreted track had no visibility into this pattern.

7. **Cross-Track Agreement on Redirect Handling**

    **Interpreted**: agent received final destination JSON content

    **Raw**: confirmed 5-level redirect chain traversed - 1,021 bytes JSON saved

    **Conclusion**: redirect handling is robust across both measurement approaches

---

## Implications for Agent Developers, Docs Teams

When evaluating or designing testing frameworks or workflows that include agentic
web fetch behavior, consider what each approach can and can't confirm:

| **Use Case** | **Interpreted** | **Raw** |
| --- | --- | --- |
| **Size Limits<br>per Backend** | ✗ Model estimates only;<br>backend not identified | ✓ Character ceilings per backend: `WebFetch` ~28 KB, `urllib` ~72 KB, unknown path 245 KB+ |
| **Content-type Detection** | ✗ No access to raw file | ✓ Chars/token ratio classifies content type: <3.0 = code/markup, >4.0 = prose |
| **Reproducibility Verification** | ✗ 2–3× variance on small files across sessions | ✓  MD5 checksums confirm byte-identical output for regression testing |
| **Ground Truth Baselines** | ✗ Self-report only | ✓ Agent claims vs actually fetched|
| **Model Perception Gaps** | ✓ Reveals when agents misreport completeness or characterize filtered excerpts as complete | ✗ Verifier confirms file integrity <br>but not agent's interpretation |
| **UI Rendering Behavior** | ✓ Reflects how Cursor displays<br>content in chat | ✗ Saved file diverges from<br>chat display |
| **Session-dependent Variance** | ✓ Captures whether new<br>chat sessions affect output | ✗ File output is deterministic;<br>session effects not visible |
| **UX** | ✓ What end users see vs<br>what agents retrieve | ✗ Raw file isn't what<br>the user sees |

> _Agentic self-reports are unreliable for detecting truncation or content subsetting, when building workflows include a raw track-like verification._

---

## Architecture Comparison

| **Step** | **Cursor<br>mid-generation** | **Claude API<br> mid-generation** | **Gemini API<br>pre-generation injection** |
| ------------------------ | ---------------------- | ------------------------------ | --------------------------- |
| **Invocation** | User asks agent via chat, agent decides which agent/tool<br> to call | Claude decides when to fetch based on prompts and/or URL availability | Gemini API attempts to<br>fetch each URL from internal<br>index cache |
| **Routing** | Cursor routes to one of many backends: `WebFetch MCP`, `urllib`, `curl` | Claude API retrieves<br>content | If not cached, falls back<br>to live fetch |
| **Content Negotiation** | Sends `Accept: text/markdown,...` header; prefers Markdown if server<br>supports it | Unknown; not publicly documented | Unknown; not<br>publicly documented |
| **Content Return** | Markdown usually or<br>raw HTML<br>on timeout | Content comes back as a tool result in the response | URL context tool injects<br>retrieved content into <br>context window |
| **Generation** | Model generates response<br>from fetched content | Claude continues generation, interpreting the tool result | `gemini-2.5-flash` generates <br>response from pre-loaded<br>content |
| **Key Observation** | Backend selection opaque; different paths have different limits | Tool result is visible in API response; truncation via `max_content_tokens` | `url_context_metadata` separates retrieval status from generation; token accounting split between text, `prompt_token_count` and URLs, `tool_use_prompt_token_count` |

## Precision Comparison

Claude API's web fetch has the cleanest measurement story as the tool results are first-class response fields,
fully observable. Gemini neatly separates retrieval metadata. Cursor requires filesystem inspection for
precise measurements, because agents deliver estimations by default.

| **Platform** | **Character Counts** | **Token Counts** | **Reproducibility** | **Metadata Visibility** |
| --- | --- | --- | --- | --- |
| **Cursor<br>Raw** | _Exact_ | _Exact_ | _Perfect_,<br>same MD5 | _Opaque_<br>backend routing |
| **Cursor-interpreted** | Agent<br>estimation | Agent<br>estimation | 2-3× variance<br>on small files | _No_ metadata |
| **Claude<br>web fetch** | _Exact_ | _Exact_ | _Perfect_, deterministic | Full tool result<br>in API response |
| **Gemini<br>URL Context** | _No_ direct access | _Exact_ | <1% variance | First-class |
