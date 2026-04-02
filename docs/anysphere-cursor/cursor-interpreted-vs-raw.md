---
layout: default
title: "Cursor-interpreted vs Raw"
nav_order: 2
permalink: /docs/anysphere-cursor/cursor-interpreted-vs-raw
parent: Anysphere Cursor
---

## Cursor-interpreted vs Raw

Two test tracks measure the same Cursor web fetch behaviors:

**Cursor-interpreted** track captures what the model _believes_ it retrieved: how much content it saw,
whether the fetch was complete, how it characterizes truncation. This is the model's self-report.

**Raw** track captures what Cursor _actually saved to disk_: exact byte counts, hexdump analysis,
MD5 checksums, and token counts. These are filesystem measurements
and cryptographic hashes, and not model estimates.

The gap between these two tracks is itself a finding. If Cursor reports "complete content" in prose
but the raw data shows truncation, that discrepancy belongs in the spec.

| | Interpreted Track | Raw Track |
| - | ---------------------- | -------------------------- |
| **Measures** | Model's interpretation of what it fetched | Filesystem measurements of saved output |
| **Character Counts** | Model estimates, vary 2-3× across sessions on small files | `wc -c` on disk - exact, reproducible |
| **Completeness** | Model's prose assessment of truncation | MD5 comparison, hexdump analysis, fence counting |
| **Token Counts** | Model estimates, ~4 chars/token assumption | `tiktoken cl100k_base`<br>exact OpenAI encoding |
| **Reproducibility** | High variance on small docs, 1.9KB→5.6KB same URL | Perfect reproducibility,<br>same URL = same MD5 |
| **Output Format** | Chat UI Markdown rendering | Raw file on disk, `raw_output_{test_id}.txt` |
| **Best For** | Understanding model<br>perception gaps | Citable measurements for the spec |

## Key Observations

1. **Reproducibility - Raw vs High Variance - Interpreted**

    **Raw track**: Same URL produces identical output
    - `BL-1`: MD5 `d6ad8451d3778bf3544574431203a3a7` across 2 runs
    - `OP-4`/`BL-3`: MD5 `554eb56e8416d86d12af17a2dfe6f815` across 3 runs
    - Character-for-character identical output on disk

    **Interpreted track**: Same URL produces 2-3× variance on small files
    - `BL-1` r1: 1,953 chars → r2: 5,595 chars → r3: 4,100 chars, 2.9× variance
    - `BL-2` r1: 1,953 chars → r2: 4,200 chars → r3: 4,350 chars, 2.2× variance

    **Conclusion**: the variance is in how Cursor _displays_ content in chat UI, 
    not what it fetches. Raw measurements prove the underlying fetch is deterministic;
    interpreted track shows UI rendering is not.

2. **Size-Dependent Consistency**

    Both tracks agree: small files are unreliable, large files are stable.

    **Interpreted track**:
    - Small files, 20-87KB: high session-to-session variance
    - Large files, 245KB: <1% variance, nearly identical across runs

    **Raw track**:
    - Small files, 4.8KB output: identical MD5s despite variance in interpreted display
    - Large files, 245KB output: identical MD5s, consistent across runs

    **Conclusion**: Cursor fetches consistently at all sizes. The interpreted variance
    on small files is possibly a _UI rendering artifact_, not entirely reflective of fetch behavior.

3. **Perception Gap: Model Self-Report is Unreliable**

    **Finding**: Model claims "complete" or "no truncation" when content is actually
    a subset or filtered.

    | **Test** | **Raw Reality** | **Interpreted Report** | **Gap** |
    | --- | --- | --- | --- |
    | **SC-3** | 38KB, truncated at <br>ref #14/252 | "Complete<br>reference section" | Model thinks filtered<br>list is complete |
    | **BL-1** | 4,817 bytes,<br>calculated | 1,953 chars displayed | UI shows subset, model<br>reports what it sees |
    | **SC-4** | Truncated mid-word "updated" | "All syntax<br>sections present" | Clean structure masks incompleteness |

    **Conclusion**: For automated agents, **trust character counts, not prose assertions**.
    Model perceives filtered excerpts as complete because they're internally coherent.

4. **Method-Specific Truncation Limits - Raw**

    - **`WebFetch`, `MCP-style`**: ~28KB ceiling, `SC-4` truncated at 27,890 chars
    - **`urllib.request`**: ~72KB ceiling, `EC-6` truncated at 72,600 chars
    - **`curl fallback`**: No ceiling detected, `SC-2` returned 17.6 MB
    - **Unknown path**: No ceiling detected, `OP-4`/`BL-3` returned 245KB

    **Conclusion**: Cursor routes to multiple backend mechanisms with different limits. The interpreted
    track couldn't discover this because the model didn't report which backend consistently served its request.

5. **Intelligent Content Filtering**

    Both tracks observed structure-aware filtering, but raw track provided the measurements.

    **Interpreted track**: model reports receiving "main content" but missing footer/nav
    **Raw track**: proves it via byte counts
    - `BL-1`: 85KB HTML → 4.8KB Markdown, 94% reduction, CSS/nav stripped
    - `SC-3`: 252 references → deterministically selects #14, the first commercial source
    - `SC-4`: 30KB page → 28KB, footer/metadata filtered

    **Conclusion**: Cursor applies content heuristics, not blind truncation. Raw track quantifies what
    interpreted track observes qualitatively.

6. **Chars/Token Ratio as Content-Type Classifier - Raw**

    - `EC-3`: JSON: 2.62 chars/token
    - `SC-2`: Raw HTML/JS: 2.65 chars/token
    - `SC-3`: Tables: 3.06 chars/token
    - `SC-4`, `OP-4`: Docs + code: 3.91-4.37 chars/token
    - `BL-1`, `BL-2`, `SC-1`: Clean Markdown: 4.13-4.36 chars/token

    **Conclusion**: Chars/token ratio enables content-type classification without parsing. <3.0 = code/markup, >4.0 = prose.
    Useful for automated analysis pipelines; interpreted track had no visibility into this pattern.

7. **Cross-Track Agreement on Redirect Handling**

    Both tracks confirmed: Cursor follows redirects transparently

    **Interpreted track**: model received final destination content, JSON from `httpbin.org/get`
    **Raw track**: confirmed 5-level redirect chain traversed, 1,021 bytes JSON saved

    **Conclusion**: redirect handling is robust across both measurement approaches

---

## Implications for Agent Developers

| **Use Case** | **Interpreted Track** | **Raw Track** |
| --- | --- | --- |
| Exact size limits per backend | ✗ model estimates only; backend not identified | ✓ character ceilings per backend: `WebFetch` ~28KB, `urllib` ~72KB, unknown path 245KB+ |
| Content-type detection | ✗ no access to raw file | ✓ chars/token ratio classifies content type: <3.0 = code/markup, >4.0 = prose |
| Reproducibility verification | ✗ 2–3× variance on small files across sessions | ✓  MD5 checksums confirm byte-identical output for regression testing |
| Ground truth baselines | ✗ self-report only | ✓ what Cursor actually fetched vs what the model claims |
| Model perception gaps | ✓ reveals when models misreport completeness or characterize filtered excerpts as complete | ✗ verifier confirms file integrity but not model's interpretation |
| UI rendering behavior | ✓ reflects how Cursor displays content in chat | ✗ saved file diverges from chat display |
| Session-dependent variance | ✓ captures whether new chat sessions affect output | ✗ file output is deterministic; session effects not visible |
| User-facing experience | ✓ what end users see vs what agents retrieve | ✗ raw file isn't what the user sees |

> **Critical takeaway**: for automation, use raw measurements. Model self-reports are
> unreliable for detecting truncation or content subsetting. The interpreted track
> reveals this gap; the raw track provides the ground truth.

---

## Platform Architecture Comparisons

| **Step** | **Cursor,mid-generation** | **Claude API<br> mid-generation** | **Gemini API<br>pre-generation injection** |
| ------------------------ | ---------------------- | ------------------------------ | --------------------------- |
| **Invocation** | User asks agent via chat, agent decides which model/tool<br> to call | Claude decides when to fetch based on prompts and/or URL availability | Gemini API attempts to fetch each URL from internal index cache |
| **Routing** | Cursor routes to one of multiple backends: `WebFetch MCP`, `urllib`, `curl` | Claude API retrieves<br>content | If not cached, falls back<br>to live fetch |
| **Content Negotiation** | Sends `Accept: text/markdown,...` header; prefers Markdown if server<br>supports it | Unknown; not publicly documented | Unknown; not publicly documented |
| **Content Return** | Markdown usually or<br>raw HTML<br>on timeout | Content comes back as a tool result in the response | URL context tool injects<br>retrieved content into <br>context window |
| **Generation** | Model generates response<br>from fetched content | Claude continues generation, interpreting the tool result | `gemini-2.5-flash` generates response from pre-loaded<br>content |
| **Key Observation** | Backend selection opaque; different paths have different limits | Tool result is visible in API response; truncation via `max_content_tokens` | `url_context_metadata` separates retrieval status from generation; token accounting split between text, `prompt_token_count` and URLs, `tool_use_prompt_token_count` |

### Measurement Precision Comparison

| **Platform** | **Character Counts** | **Token Counts** | **Reproducibility** | **Metadata Visibility** |
| --- | --- | --- | --- | --- |
| **Cursor Raw** | Exact | Exact | Perfect, same MD5 | Opaque backend routing |
| **Cursor-interpreted** | Estimated model | Estimated - model | 2-3× variance - small files | No metadata |
| **Claude web fetch** | Exact | Exact | Perfect - deterministic | Full tool result in API response |
| **Gemini URL Context** | No direct access | Exact | <1% variance | First-class |

**Conclusion**: Claude API's web fetch tool has the cleanest measurement story; tool results are first-class API
response fields, fully observable. Gemini separates retrieval metadata cleanly. Cursor requires filesystem
inspection to get ground truth because the model estimates based on rendered output.
