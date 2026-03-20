---
layout: default
title: "Key Findings for Cursor's @Web Tool, Raw"
permalink: /docs/anysphere-cursor/cursor-test-findings-raw
nav_order: 3
parent: Anysphere Cursor
---

## Key Findings for Cursor `@Web` Tool, Raw

---

**[Raw Track Test Workflow](/cursor-web-fetch/web_fetch_testing_framework.py)**:

    1. Run `python web_fetch_testing_framework.py --test [test ID] --track raw`
       and review the Terminal output
    2. Copy the provided prompt asking `@Web` to fetch the URL and save verbatim output
    3. Open a new Cursor chat session and paste the prompt into the chat window
    4. Capture the saved raw output file, compute exact metrics using verification script
    5. Log structured metadata with precise measurements (file size, MD5, token count via tiktoken)
    6. Ensure log results are saved to `cursor-web-fetch/results/raw/`

## Platform Limit Summary

| **Limit** | **Observed** |
| ------- | ---------- |
| **Hard Character Limit** | Method-dependent: ~28KB (WebFetch MCP), ~72KB (urllib), none detected for other paths (tested up to 17MB) |
| **Hard Token Limit** | None detected - tested up to 6.68M tokens (SC-2 raw HTML) |
| **Output Consistency** - Same URL | _Perfect reproducibility_: BL-1/BL-2 identical across runs (same MD5), BL-3/OP-4 identical (same MD5) |
| **Content Conversion Pattern** | _Non-deterministic_: Simple docs → markdown (BL-1, SC-1, OP-3); Complex/timeout → raw HTML (SC-2); Raw markdown → pass-through (EC-6) |
| **Truncation Pattern** | When occurs, method-specific: WebFetch MCP ~28KB, urllib ~72KB; respects structure (ends mid-word or at boundaries) |
| **Chars/Token Ratio Range** | 2.62 (JSON) to 4.36 (clean markdown) - strong indicator of content type |
| **Reference List Filtering** | _Deterministic selection_: Wikipedia 252 refs → consistently selects ref #14 (first commercial source after govt sources) |
| **Redirect Chains** | Successfully follows, tested 5-level redirect chain |
| **Backend Routing** | _Multiple fetch paths_: WebFetch (MCP-style), urllib, curl fallback - each with different size limits |

## Results Details

| --- | --- |
| **Model** | `Auto` |
| **Total Tests** | 27 |
| **Distinct URLs** | 13 |
| **Input Size Range** | 2KB–256KB (expected raw source) |
| **Output Size Range** | 1KB–17.6MB (actual converted/fetched) |
| **Truncation Detection** | MD5 comparison, hexdump analysis, fence/brace counting, mid-word detection |

### Content Conversion Patterns

| **Test** | **Input Type** | **Expected** | **Received** | **Format** | **Conversion** |
| ------ | ------- | ------: | ------: | ------: | ------: |
| **BL-1** | HTML | 85KB | 4.8KB | Markdown | 94% reduction |
| **BL-2** | Markdown | 20KB | 4.8KB | Markdown | 76% reduction |
| **SC-2** | HTML (complex) | 80KB | 17.6MB | Raw HTML/JS | 22,000% expansion (timeout→curl fallback) |
| **SC-3** | HTML | 100KB | 38KB | Markdown | 62% reduction + ref filtering |
| **OP-4** | HTML | 250KB | 245KB | Markdown | 2% reduction |
| **EC-6** | Raw .md | 60KB | 73KB | Markdown (pass-through) | 22% expansion (version drift) |

### Chars/Token Ratio Analysis

| **Content Type** | **Chars/Token** | **Tests** | **Interpretation** |
| --- | ---: | --- | --- |
| **Clean Markdown Prose** | 4.13–4.36 | BL-1, BL-2, SC-1, EC-1, EC-6 | Efficient encoding, natural language |
| **Documentation + Code** | 3.91–4.37 | SC-4, OP-4, BL-3 | Mixed content, moderate efficiency |
| **Table-Heavy Data** | 3.06 | SC-3 | Repetitive structure, less efficient |
| **Raw HTML/JS** | 2.65 | SC-2 | Heavy markup, symbols, very inefficient |
| **JSON** | 2.62 | EC-3 | Structural chars, lowest efficiency |

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Spec** |
| --- | --------- | ------- | ---------- | ------------------- |
| **1** | **Truncation limits are fetch-method-dependent, not universal** | SC-4 ~28KB,<br>EC-6 ~72KB,<br>OP-4 245KB | SC-4 (WebFetch MCP) truncated at 27,890 chars; EC-6 (urllib) truncated at 72,600 chars; OP-4/BL-3 (different path) no truncation at 245KB | **@Web routes to multiple backends with different size constraints: WebFetch MCP ~28KB ceiling, urllib ~72KB ceiling, other paths 240KB+ no ceiling detected** |
| **2** | **Markdown conversion is format-agnostic** | BL-1 (HTML) vs<br>BL-2 (.md) | Both URLs return identical 4,817-byte output (same MD5: d6ad8451d3778bf3544574431203a3a7) despite different source formats | **@Web normalizes HTML and markdown sources to identical output - conversion pipeline is format-blind** |
| **3** | **Perfect reproducibility for same URL** | BL-3 / OP-4<br>(3 runs),<br>BL-1 / BL-2<br>(2 runs each) | Identical MD5 checksums across multiple runs on same URL; OP-4 & BL-3 both: 554eb56e8416d86d12af17a2dfe6f815 | **Raw track has perfect run-to-run consistency - same URL always produces identical output (same MD5, same byte count)** |
| **4** | **Intelligent reference filtering, not truncation** | SC-3 | Wikipedia page with 252 references consistently returns reference #14 "Moody's Analytics" - first commercial/corporate source after 13 govt/institutional sources | **@Web applies deterministic content heuristics: preserves core content, filters govt/academic refs, selects first commercial source** |
| **5** | **Complex pages may trigger curl fallback** | SC-2 (4 runs),<br>EC-1 | WebFetch timeout → autonomous curl -sL fallback; returns 16-17MB raw HTML instead of filtered markdown | **On timeout, @Web may substitute curl, returning unfiltered HTML - output format/size unpredictable on complex pages** |
| **6** | **Chars/token ratio reliably indicates content type** | All tests | Strong correlation: JSON 2.62, Raw HTML 2.65, Tables 3.06, Docs 3.91-4.37; <3.0 = code/markup, >4.0 = prose | **Chars/token metric enables content-type classification without parsing - useful for automated analysis** |
| **7** | **Large documents have minimal conversion overhead** | OP-4, BL-3<br>245KB output | Expected 250KB, received 245KB markdown - only 2% reduction despite rich structure (241 code blocks, 237 headers) | **@Web preserves large structured docs nearly verbatim - no aggressive filtering on multi-section tutorials** |
| **8** | **Truncation respects structure when it occurs** | SC-4, EC-6 | SC-4 ends mid-word "updated" (alphanumeric final char); EC-6 ends mid-sentence but clean UTF-8 boundary; both incomplete but structurally valid | **When truncation occurs, may cut mid-content but preserves character boundaries - no corrupted UTF-8** |
| **9** | **JS-heavy SPAs extract rendered content** | EC-1 | Expected 100KB raw HTML/JS, received 5.7KB markdown (94% reduction); successfully extracted doc content despite SPA architecture | **@Web handles client-side rendering - extracts semantic content, strips JS overhead** |
| **10** | **No token-based ceiling detected** | SC-2<br>6.68M tokens | Successfully returned 17.6MB (6,680,678 tokens) raw HTML - no evidence of token-based truncation | **If token limits exist, ceiling is extremely high (7M+); character/method limits dominate** |

## Method-Specific Behavior

| **Fetch Backend** | **Identified In** | **Size Limit** | **Conversion** | **Reliability** |
| --- | --- | --- | --- | --- |
| **WebFetch (MCP-style)** | SC-4, SC-3, OP-3 | ~28KB | Markdown | High - consistent results |
| **urllib.request** | EC-6 | ~72KB | Pass-through (.md) | High - clean truncation boundary |
| **curl fallback** | SC-2, EC-1 | None detected (17MB+) | Raw HTML (no conversion) | Low - only on timeout |
| **Unknown path** | OP-4, BL-3 | None detected (245KB+) | Markdown | High - perfect reproducibility |

## Content Filtering Heuristics

@Web applies intelligent content selection beyond simple truncation:

| **Heuristic** | **Example** | **Behavior** |
| --- | --- | --- |
| **Reference deduplication** | SC-3 Wikipedia | 252 refs → 1 commercial source (deterministic) |
| **Footer/nav stripping** | SC-4 Markdown Guide | 30KB page → 28KB excluding footer/metadata |
| **Boilerplate reduction** | BL-1 MongoDB HTML | 85KB → 4.8KB (strips CSS, nav, sidebar) |
| **Core content preservation** | OP-4 Tutorial | 250KB → 245KB (241 code blocks intact) |

## Perception Gap vs Interpreted Track

Raw track measurements reveal interpreted track underreports:

| **Test** | **Raw Track** | **Interpreted Track** | **Gap** |
| --- | ---: | ---: | --- |
| **BL-1** | 4,817 chars | 1,953 chars (run 1) | Interpreted shows subset; UI reformats markdown |
| **SC-2** | 17,691,628 chars | 702,885 chars (run 2) | Interpreted shows filtered; raw shows curl fallback |
| **OP-4** | 245,465 chars | 245,453 chars | Near-perfect match on large docs |

> _**Implication for agents**: Raw track provides ground truth measurements; interpreted track reflects UI-rendered subset_
