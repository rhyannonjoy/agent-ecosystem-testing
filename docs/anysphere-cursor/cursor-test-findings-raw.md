---
layout: default
title: "Key Findings for Cursor's Web Fetch Behavior, Raw"
permalink: /docs/anysphere-cursor/cursor-test-findings-raw
nav_order: 3
parent: Anysphere Cursor
---

# Key Findings for Cursor's Web Fetch Behavior, Raw

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/cursor-web-fetch/web_fetch_testing_framework.py)

    1. Run `python web_fetch_testing_framework.py --test {test ID} --track raw`
    2. Review terminal output
    3. Copy provided prompt requesting `@Web`* fetch the URL, save verbatim output
    4. Open a new Cursor session in VS Code, paste prompt into the chat window
    5. Examine saved `raw_output{test ID}.txt` file
    6. Run `python3 web_fetch_verify_raw_results.py {test ID}` to calculate metrics
    7. Log structured metadata with metrics as described in `framework-reference.md`
    8. Ensure log results saved to `/results/raw/results.csv`

>_*Results logged as "Methods tested: `@Web`" reflect user-facing, prompt syntax. Post-analysis revealed testing misuse of `@Web` as a
>fetch command rather than a context attachment. Cursor may autonomously call backend mechanisms `WebFetch`, `mcp_web_fetch`
>regardless of `@Web` syntax, visit [Friction Note](friction-note.md#web-evolution-from-manual-context-to-automatic-agent-capability)
>for analysis._

---

## Platform Limit Summary

| **Limit** | **Observed** |
| ------- | ---------- |
| **Hard<br>Character<br>Limit** | _Method-dependent_: `WebFetch MCP` ~28 KB, `urllib` ~72 KB,<br>_none detected_ for other paths; tested up to 17 MB |
| **Hard<br>Token Limit** | _None detected_ - tested up to 6.68 M tokens<br>with `SC-2` raw HTML |
| **Output Consistency**<br> Same URL | _Perfect reproducibility_: `BL-1`/`BL-2` identical across runs,<br>same MD5, `BL-3`/`OP-4` identical, same MD5 |
| **Content<br>Conversion Pattern** | _Non-deterministic_: simple docs → Markdown `BL-1`, `SC-1`, `OP-3`;<br>complex/timeout → raw HTML - `SC-2`;<br>raw Markdown → pass-through - `EC-6` |
| **Truncation<br>Pattern** | _Method-specific_: `WebFetch MCP` ~28 KB, `urllib` ~72 KB;<br>respects structure, ends mid-word or at boundaries |
| **Chars/Token<br>Ratio Range** | JSON 2.62 to clean Markdown 4.36 -<br>strong indicator of content type |
| **Reference<br>List Filtering** | _Deterministic selection_: Wikipedia 252 refs → consistently selects<br>ref #14, the first commercial source after govt sources |
| **Redirect<br>Chains** | _Successfully follows_, tested 5-level redirect chain |
| **Backend<br>Routing** | _Multiple fetch paths_: `WebFetch` - `MCP-style`, `urllib`, `curl` fallback;<br>each with different size limits |

## Results Details

| --- | --- |
| **Model** | `Auto` |
| **Total Tests** | 27 |
| **Distinct URLs** | 13 |
| **Input Size Range** | 2 KB–256 KB - expected raw source |
| **Output Size Range** | 1 KB–17.6 MB actual converted/fetched |
| **Truncation Detection** | MD5 comparison, hexdump analysis,<br>fence/brace counting, mid-word detection |

## Content Conversion Patterns

| **Test** | **Input Type** | **Expected** | **Received** | **Format** | **Conversion** |
| ------ | ------- | ------: | ------: | ------: | ------: |
| **BL**<br>**1** | HTML | 85 KB | 4.8 KB | Markdown | 94% reduction |
| **BL**<br>**2** | Markdown | 20 KB | 4.8 KB | Markdown | 76% reduction |
| **SC**<br>**2** | HTML<br>complex | 80 KB | 17.6 MB | Raw HTML/JS | 22,000% expansion,<br>timeout→`curl` fallback |
| **SC**<br>**3** | HTML | 100 KB | 38 KB | Markdown | 62% reduction<br>, ref filtering |
| **OP**<br>**4** | HTML | 250 KB | 245 KB | Markdown | 2% reduction |
| **EC**<br>**6** | Raw<br>`.md` | 60 KB | 73 KB | Markdown<br>pass-through | 22% expansion<br>version drift |

## Chars/Token Ratio Analysis

| **Content Type** | **Chars/Token** | **Tests** | **Interpretation** |
| --- | ---: | --- | --- |
| **Clean Markdown<br>Prose** | 4.13–4.36 | `BL-1`, `BL-2`, `SC-1`,<br>`EC-1`, `EC-6` | Natural language,<br>**efficient encoding** |
| **Documentation<br> with Code** | 3.91–4.37 | `SC-4`, `OP-4`, `BL-3` | Mixed content,<br>**moderate efficiency** |
| **Table-Heavy<br>Data** | 3.06 | `SC-3` | Repetitive structure,<br>**less efficient** |
| **Raw<br>HTML/JS** | 2.65 | `SC-2` | Heavy markup, symbols,<br>**very inefficient** |
| **JSON** | 2.62 | `EC-3` | Structural chars,<br>**lowest efficiency** |

## HTTP Content Negotiation

Cursor's web fetch mechanisms request `text/markdown` via the `Accept` header,
signaling a preference for Markdown over HTML when the server supports content
negotiation. Cursor sends `Accept: text/markdown, text/html...` with
Markdown listed first - highest implicit `q` value, with HTML and other types as
fallback preferences. Impact on results:

- Servers that ignore `Accept`, typical for normal websites, still return HTML
- Servers that support content negotiation, some "Markdown-first" or agent-oriented
setups may return `Content-Type: text/markdown`; Cursor can use without HTML cleanup
- Raw track result artifacts show this header structure, such as _`raw_output_EC-3.txt`_:
<br>_`"Accept": "text/markdown,text/html;q=0.9,application/xhtml+xml;q=0.8,application/xml;q=0.7"`_

| **Test** | **Server Response** | **Cursor Behavior** | **Output** |
| ---------- | --------------------- | --------------------- | ------------ |
| **`EC-6`**<br>GitHub raw `.md` | `Content-Type: text/plain; charset=utf-8` | Passed through<br>as Markdown | 73 KB |
| **`BL-1`**<br>HTML docs | HTML | Converted to Markdown | 4.8 KB from<br>85 KB source |
| **`SC-2`**<br>timeout→`curl` fallback | HTML | No conversion | 17.6 MB raw HTML |

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Spec** |
| ----- | --------- | ------- | ---------- | --------- |
| **1** | **Truncation limits fetch-method-dependent,<br>not universal** | `SC-4`<br>`EC-6`<br>`OP-4` | `SC-4` `WebFetch MCP` truncated at 27,890 chars; `EC-6` `urllib` truncated at 72,600 chars;<br>`OP-4`/`BL-3`, different path,<br>no truncation at 245 KB | **`@Web` routes to multiple backends with different size constraints: `WebFetch MCP` ~28 KB ceiling, `urllib` ~72 KB ceiling, other paths 240 KB+<br>no ceiling detected** |
| **2** | **Markdown conversion<br>format-agnostic** | `BL-1` HTML <br>`BL-2` `.md` | Both URLs return identical 4,817-byte output, same `MD5` despite different source formats | **`@Web` normalizes HTML and Markdown sources to identical output,<br>conversion pipeline<br>format-blind** |
| **3** | **Perfect reproducibility for same URL** | `BL-1` `BL-2` `BL-3` `OP-4`  | Identical MD5 checksums across multiple runs on same URL | **Raw track has perfect run-to-run consistency - same URL always produces identical output - same MD5,<br>same byte count** |
| **4** | **Intelligent reference filtering,<br>not truncation** | `SC-3` | Wikipedia page with 252 references consistently returns reference #14 _"Moody's Analytics"_ first commercial source after 13 institutional sources | **`@Web` applies deterministic content heuristics: preserves core content, filters govt/academic refs** |
| **5** | **Complex pages may trigger `curl` fallback** | `SC-2` `EC-1` | `WebFetch` timeout → autonomous `curl` fallback; returns 16-17 MB raw HTML instead of filtered Markdown | **On timeout, `@Web` may substitute `curl`, returning unfiltered HTML - output format/size unpredictable on complex pages** |
| **6** | **Chars/token ratio reliably indicates content type** | All tests | Strong correlation: JSON 2.62, Raw HTML 2.65, Tables 3.06, Docs 3.91-4.37; <3.0 = code/markup, >4.0 = prose | **Chars/token metric enables content-type classification without parsing - useful for automated analysis** |
| **7** | **Large docs, minimal conversion overhead** | `OP-4` `BL-3` | Expected 250 KB, received<br>245 KB Markdown, only 2% reduction despite rich structure, 241 code blocks, 237 headers | **`@Web` preserves large structured docs nearly verbatim, no aggressive filtering on multi-section tutorials** |
| **8** | **Truncation respects structure** | `SC-4` `EC-6` | `SC-4` ends mid-word _"updated"_, alphanumeric final char; `EC-6` ends mid-sentence. but clean `UTF-8` boundary; both incomplete but structurally valid | **When truncation occurs, may cut mid-content, but preserves character boundaries** |
| **9** | **JS-heavy SPAs extract rendered content** | `EC-1` | Expected 100 KB raw HTML/JS, received 5.7 KB Markdown - 94% reduction; successfully extracted doc content<br>despite SPA architecture | **`@Web` handles client-side rendering - extracts semantic content, strips JS overhead** |
| **10** | **Token-based ceiling not detected** | `SC-2` | Successfully returned 17.6 MB - 6,680,678 tokens raw HTML | **If token limits exist, ceiling is extremely high - 7M+; char/method<br>limits dominate** |

## Method-Specific Behavior

| **Fetch Backend** | **Identified** | **Size Limit** | **Conversion** | **Reliability** |
| --- | --- | --- | --- | --- |
| **`WebFetch MCP`** | `SC-4`<br>`SC-3`<br>`OP-3` | ~28 KB | Markdown | **High** - consistent results |
| **`urllib.request`** | `EC-6` | ~72 KB | Pass-through `.md` | **High** - clean truncation boundary |
| **`curl`** | `SC-2`<br>`EC-1` | _None detected_<br>17 MB+ | Raw HTML<br>no conversion | **Low** - only on timeout |
| **Unknown Path** | `OP-4`<br>`BL-3` | _None detected_<br>245 KB+ | Markdown | **High** - perfect reproducibility |

## Content Filtering Heuristics

>_Beyond basic truncation, Cursor applies intelligent content selection_

| **Heuristic** | **Example** | **Behavior** |
| --- | --- | --- |
| **Reference<br>Deduplication** | `SC-3`<br>Wikipedia | _Deterministic_<br>252 refs → 1 commercial source |
| **Footer/Nav<br>Stripping** | `SC-4`<br>Markdown Guide | _Reduction from_<br> 30 KB page → 28 KB |
| **Boilerplate<br>Reduction** | `BL-1`<br>MongoDB HTML | _Reduction from_<br>85 KB → 4.8 KB |
| **Core Content<br>Preservation** | `OP-4`<br>Tutorial | _241 Code blocks intact_<br>250 KB → 245 KB |

## Perception Gap

>_Raw track measurements reveal that the **Cursor-interpreted track under-reports**_

| **Test** | **Raw Track** | **Interpreted Track** | **Gap** |
| --- | ---: | ---: | --- |
| `BL-1` | 4,817 chars | Run 1<br>1,953 chars | Interpreted shows subset;<br>UI reformats Markdown |
| `SC-2` | 17,691,628 chars | Run 2<br>702,885 chars | Interpreted shows filtered;<br>raw shows `curl` fallback |
| `OP-4` | 245,465 chars | 245,453 chars | Near-perfect match on large docs |
