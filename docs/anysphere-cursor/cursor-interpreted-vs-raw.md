---
layout: default
title: "Cursor-interpreted vs Raw"
nav_order: 2
permalink: /docs/anysphere-cursor/cursor-interpreted-vs-raw
parent: Anysphere Cursor
---

## Cursor-interpreted vs Raw

Two test tracks measure the same `@Web` fetch behaviors:

**Cursor-interpreted** captures what the model _believes_ it retrieved: how much content it saw, whether the fetch was complete, how it characterizes truncation. This is the model's self-report. **Raw track** captures what `@Web` _actually saved to disk_: exact byte counts via `wc -c`, exact MD5 checksums, exact token counts via `tiktoken cl100k_base`. These are filesystem measurements and cryptographic hashes, not model estimates.

The gap between these two tracks is itself a finding. If Cursor reports "complete content" in prose but the raw MD5 shows truncation, that discrepancy belongs in the spec.

| | Interpreted Track | Raw Track |
| - | ---------------------- | -------------------------- |
| **Measures** | Model's interpretation of what it fetched | Filesystem measurements of saved output |
| **Character counts** | Model estimates, vary 2-3× across sessions on small files | `wc -c` on disk - exact, reproducible |
| **Completeness** | Model's prose assessment of truncation | MD5 comparison, hexdump analysis, fence counting |
| **Token counts** | Model estimates (~4 chars/token assumption) | `tiktoken cl100k_base` - exact OpenAI encoding |
| **Reproducibility** | High variance on small docs (1.9KB→5.6KB same URL) | Perfect reproducibility (same URL = same MD5) |
| **Output format** | Chat UI markdown rendering | Raw file on disk (`raw_output_{test_id}.txt`) |
| **Best used for** | Understanding model perception gaps | Citable measurements for the spec |

---

## Key Observations

### 1. **Perfect Reproducibility (Raw) vs High Variance (Interpreted)**

**Raw track**: Same URL always produces identical output
- BL-1: MD5 `d6ad8451d3778bf3544574431203a3a7` across 2 runs
- OP-4/BL-3: MD5 `554eb56e8416d86d12af17a2dfe6f815` across 3 runs
- Character-for-character identical output on disk

**Interpreted track**: Same URL produces 2-3× variance on small files
- BL-1 r1: 1,953 chars → r2: 5,595 chars → r3: 4,100 chars (2.9× variance)
- BL-2 r1: 1,953 chars → r2: 4,200 chars → r3: 4,350 chars (2.2× variance)

**Conclusion**: The variance is in how Cursor _displays_ content in chat UI, not what `@Web` fetches. Raw measurements prove the underlying fetch is deterministic; interpreted track shows UI rendering is not.

---

### 2. **Size-Dependent Consistency**

Both tracks agree: small files are unreliable, large files are stable.

**Interpreted track observation**:
- Small files (20-87KB): high session-to-session variance
- Large files (245KB): <1% variance, nearly identical across runs

**Raw track observation**:
- Small files (4.8KB output): identical MD5s despite variance in interpreted display
- Large files (245KB output): identical MD5s, consistent across runs

**Conclusion**: `@Web` fetches consistently at all sizes. The interpreted variance on small files is a _UI rendering artifact_, not fetch behavior.

---

### 3. **Perception Gap: Model Self-Report is Unreliable**

**Finding**: Model claims "complete" or "no truncation" when content is actually subset or filtered.

| Test | Raw Reality | Interpreted Report | Gap |
| --- | --- | --- | --- |
| **SC-3** | 38KB, truncated at ref #14/252 | "Complete reference section" | Model thinks filtered list is complete |
| **BL-1 r1** | 4,817 bytes (ground truth) | 1,953 chars displayed | UI shows subset, model reports what it sees |
| **SC-4** | Truncated mid-word "updated" | "All syntax sections present" | Clean structure masks incompleteness |

**Conclusion**: For automated agents, **trust character counts, not prose assertions**. Model perceives filtered excerpts as complete because they're internally coherent.

---

### 4. **Method-Specific Truncation Limits (Raw Track Discovery)**

Interpreted track could not determine this — model doesn't report which fetch backend was used.

**Raw track findings**:
- **WebFetch (MCP-style)**: ~28KB ceiling (SC-4 truncated at 27,890 chars)
- **urllib.request**: ~72KB ceiling (EC-6 truncated at 72,600 chars)
- **curl fallback**: No ceiling detected (SC-2 returned 17.6MB)
- **Unknown path**: No ceiling detected (OP-4/BL-3 returned 245KB)

**Conclusion**: `@Web` routes to multiple backends with different limits. Interpreted track couldn't discover this because the model doesn't know which backend served its request.

---

### 5. **Intelligent Content Filtering (Both Tracks Confirm)**

Both tracks observed structure-aware filtering, but raw track provided the measurements.

**Interpreted track**: Model reports receiving "main content" but missing footer/nav
**Raw track**: Proves it via byte counts
- BL-1: 85KB HTML → 4.8KB markdown (94% reduction, CSS/nav stripped)
- SC-3: 252 references → deterministically selects #14 (first commercial source)
- SC-4: 30KB page → 28KB (footer/metadata filtered)

**Conclusion**: `@Web` applies content heuristics, not blind truncation. Raw track quantifies what interpreted track observes qualitatively.

---

### 6. **Chars/Token Ratio as Content-Type Classifier (Raw Track Only)**

Interpreted track had no visibility into this pattern.

**Raw track discovery**:
- JSON: 2.62 chars/token (EC-3)
- Raw HTML/JS: 2.65 chars/token (SC-2)
- Tables: 3.06 chars/token (SC-3)
- Docs + code: 3.91-4.37 chars/token (SC-4, OP-4)
- Clean markdown: 4.13-4.36 chars/token (BL-1, BL-2, SC-1)

**Conclusion**: Chars/token ratio enables content-type classification without parsing. <3.0 = code/markup, >4.0 = prose. Useful for automated analysis pipelines.

---

### 7. **Cross-Track Agreement on Redirect Handling**

Both tracks confirmed: `@Web` follows redirects transparently.

**Interpreted track**: Model received final destination content (JSON from httpbin.org/get)
**Raw track**: Confirmed 5-level redirect chain traversed, 1,021 bytes JSON saved

**Conclusion**: Redirect handling is robust across both measurement approaches.

---

## Implications for Agent Developers

### Use Raw Track Measurements for:
- **Exact size limits**: Character ceilings per backend (28KB, 72KB, 245KB+)
- **Content-type detection**: Chars/token ratio classification
- **Reproducibility verification**: MD5 checksums for regression testing
- **Ground truth baselines**: What `@Web` actually fetched vs what model claims

### Use Interpreted Track for:
- **Model perception gaps**: Understanding when models misreport completeness
- **UI rendering behavior**: How Cursor displays content in chat
- **Session-dependent variance**: Whether new chat sessions affect output
- **User-facing experience**: What end users see vs what agents retrieve

### Critical Takeaway:
**For automation, use raw measurements.** Model self-reports are unreliable for detecting truncation or content subsetting. The interpreted track reveals this gap; the raw track provides the ground truth.

---

## Cursor `@Web` vs Claude API `web_fetch` vs Gemini URL Context

### Architecture Comparison

**Cursor `@Web`** (IDE-integrated, mid-generation):
1. User invokes `@Web` in chat or Composer
2. Cursor routes to one of multiple backends (WebFetch MCP, urllib, curl)
3. Content returned as markdown (usually) or raw HTML (on timeout)
4. Model generates response from fetched content
5. **Observation**: Backend selection is opaque; different paths have different limits

**Claude API `web_fetch`** ([mid-generation tool call](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#web-fetch-tool)):
1. Claude decides when to fetch based on prompts and/or URL availability
2. Claude API retrieves content
3. Content comes back as a tool result in the response
4. Claude continues generation, interpreting the tool result
5. **Observation**: Tool result is visible in API response; truncation via `max_content_tokens`

**Gemini URL Context** (pre-generation injection):
1. Gemini API attempts to fetch each URL from internal index cache
2. If not cached, falls back to live fetch
3. URL context tool injects retrieved content into context window
4. `gemini-2.5-flash` generates response from pre-loaded content
5. **Observation**: `url_context_metadata` separates retrieval status from generation; token accounting split between text (`prompt_token_count`) and URLs (`tool_use_prompt_token_count`)

---

### Measurement Precision Comparison

| Platform | Character Counts | Token Counts | Reproducibility | Metadata Visibility |
| --- | --- | --- | --- | --- |
| **Cursor `@Web` (raw)** | Exact (`wc -c`) | Exact (`tiktoken`) | Perfect (same MD5) | Opaque backend routing |
| **Cursor `@Web` (interpreted)** | Estimated (model) | Estimated (model) | 2-3× variance (small files) | No metadata |
| **Claude `web_fetch`** | Exact (tool result) | Exact (API usage) | Perfect (deterministic) | Full tool result in response |
| **Gemini URL Context** | No direct access | Exact (`tool_use_prompt_token_count`) | <1% variance | First-class `url_context_metadata` |

**Takeaway**: Claude `web_fetch` has the cleanest measurement story — tool results are first-class API response fields, fully observable. Gemini separates retrieval metadata cleanly. Cursor requires filesystem inspection (raw track) to get ground truth because the model only sees rendered output.
