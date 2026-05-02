---
layout: default
title: "Key Findings Cursor's Web Fetch Behavior, Cursor-interpreted"
nav_order: 3
permalink: /docs/anysphere-cursor/cursor-test-findings
parent: Anysphere Cursor
---

# Key Findings for Cursor's Web Fetch Behavior, Cursor-interpreted

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/cursor-web-fetch/web_fetch_testing_framework.py)

    1. Run `python web_fetch_testing_framework.py --test {test ID} --track interpreted`
    2. Review terminal output
    3. Copy the provided prompt requesting agent report `@Web`* fetch results:
       character count, token estimate, truncation status, content completeness,
       Markdown formatting integrity
    4. Open a new Cursor session, paste prompt into chat window
    5. Capture agent's full text response, observations as the interpreted-finding;
       gap between agent's self report and actual fetch behavior is a finding
    6. Log structured metadata as described in `framework-reference.md`
    7. Ensure log results saved to `/results/cursor-interpreted/results.csv`

>_*Results logged as "Methods tested: `@Web`" reflect user-facing prompt syntax. Post-analysis revealed testing misused `@Web` as a
>fetch command rather than a context attachment. Cursor may autonomously call backend mechanisms `WebFetch`, `mcp_web_fetch` regardless
>of `@Web syntax`; visit [Friction Note](friction-note.md#web-evolution-from-manual-context-to-automatic-agent-capability) for analysis._

---

## Platform Limit Summary

| **Limit** | **Observed** |
| ------- | ---------- |
| **Hard Character<br>Limit** | _None detected_: tested up to 702 KB |
| **Hard Token<br>Limit** | _None detected_: tested up to ~179K tokens,<br>average 33,912 |
| **Output Consistency**<br>Small | _High variance_: 2-3x across sessions,<br>1.9 KB → 5.6 KB same URL |
| **Output Consistency**<br>Large | _Highly stable_: <1% variance across sessions,<br>245 KB identical across 3 runs |
| **Content Selection Behavior** | _Non-deterministic_ for small files;<br>size-dependent |
| **Truncation<br>Pattern** | _Respects content boundaries_ when occurs,<br>no mid-sentence cuts |
| **JavaScript-heavy<br>SPAs** | Truncation at ~6 KB, ~1.5K tokens;<br>_free tier times out, Pro tier truncates cleanly_ |
| **Redirect Chains** | _Successfully follows_, tested 5-level redirect chain |
| **Self-reported Completeness** | _Unreliable_: model claims "full content" when returning subset |

## Results Details

| --- | --- |
| **Model** | `Auto` |
| **Total Tests** | 26 |
| **Distinct URLs** | 13 |
| **Input Size Range** | 2 KB–256 KB |
| **Truncation Detection** | Model assertion, verbatim last-50-chars, Markdown integrity |

## Cross-run Output Variance

| **Test** | **Category** | **Run 1<br>chars** | **Run 2<br>chars** | **Run 3<br>chars** | **Variance** |
| ------ | ------- | ------: | ------: | ------: | ------: |
| **`BL-1`** | Small - 87 KB | 1,953 | 5,595 | 4,100 | 2.9x |
| **`BL-2`** | Small - 20 KB | 1,953 | 4,200 | 4,350 | 2.2x |
| **`SC-2`** | Large - 80 KB | 702,885 | 702,885 | 702,885 | 1.0x |
| **`OP-4`** | Large - 256 KB | 245,000 | 245,465 | 245,466 | 1.0x |
| **`EC-1`** | SPA - 100 KB | 0 - _timeout_ | 5,857 | _null_ | _null_ |

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Spec** |
| --- | --------- | ------- | ---------- | ------------------- |
| **1** | **JavaScript-heavy SPAs truncation ceiling** | `EC-1`<br>r1 & r2<br>multiple sizes | Free tier: timeout - 0 bytes; Pro tier: truncated at 5,857 chars, ~1.5K tokens, clean ending at last link block; suggests ~6KB or ~1.5K token ceiling specifically for SPA endpoints | **SPAs truncated aggressively, not completely blocked; free tier timeouts mask Pro tier truncation behavior** |
| **2** | **Static HTML/Markdown pages have no detected ceiling** | `BL-1` through `OP-4`<br> `SC-2` - 702 KB<br>`OP-4` - 245 KB | Successfully returned 702,885 characters from `SC-2`; 245,465 characters from `OP-4`; no truncation observed on static content | **No practical character ceiling detected for static docs; tested up to 700 KB** |
| **3** | **Output consistency size-dependent** | `BL-1`<br>`BL-2`<br>`SC-2`<br>`OP-4` | Small files, 1-20 KB: 2-3× variance across sessions, 1.9K→5.6K; large files, 80-256 KB: <1% variance, 702.8K identical, 245.5K identical | **Fetch behavior reliability depends on size - small docs unreliable, large docs stable** |
| **4** | **Content selection is non-deterministic for small files, session-dependent** | `BL-1`<br>r1-r4<br>`BL-2`<br>r1-r3 | Identical prompts in different chat sessions produced 1,953 → 5,595 → 4,100 → 5,500 chars on `BL-1`; new sessions returned larger content than original session | **New chat sessions influence `@Web` output; conversation state affects fetch behavior** |
| **5** | **Same logical content, different formats, different sizes** | `BL-1` HTML vs `BL-2` Markdown<br>both r1 | Both returned 1,953 chars despite different source format, HTML vs `.md`; later runs diverged - 5,595 vs 4,200 - suggesting format-dependent processing | **Format affects fetch behavior; may process HTML and Markdown sources differently** |
| **6** | **Intelligent content filtering, not hard truncation** | `SC-4`,<br>`EC-6` | `SC-4`, 30 KB page returned 28 KB excluding footer/nav/metadata; `EC-6` returned full 71 KB including complex Markdown; always ends at section boundaries | **For static content doesn't truncate mid-content, filters non-essential structural elements, while preserving docs integrity** |
| **7** | **Agent's self-reported completeness diverges from actual content** | `SC-3`<br>`BL-1`<br>r3-r4<br>`EC-1`<br>r2 | `SC-3`: Agent reports _"no truncation, complete reference"_ but content cuts mid-references section;<br>`EC-1` r2: Agent acknowledges truncation at ~6 KB despite 100 KB expected | **Self-report of content completeness unreliable, agent perceives filtered excerpts as _"complete"_ because internally valid** |
| **8** | **Redirect chains handled transparently** | `EC-3` | 5-level redirect chain successfully followed; returned final destination content - 850 chars JSON without truncation | **Follows HTTP redirects without user awareness or latency penalty** |
| **9** | **`H2` supported for static content** | `SC-2`<br>`OP-4`<br>`EC-6`<br>`BL-3` | Token counts range `BL-1` 488 to `SC-2` 175,721 with no observable limit; successfully returned 61K token document, `OP-4`, multiple times identically | **For static pages: if token-based, ceiling is extremely high - 200K+; effectively no practical limit** |
| **10** | **`H3` confirmed for static content** | `BL-1`<br>`BL-2`<br>`SC-2`<br>`SC-3`<br>`SC-4`<br>r1-r3 | 8 tests matched `H3`: content selection respects Markdown section boundaries; truncation occurs at header boundaries, code fence closes, list endings | **For static pages, uses intelligent, structure-aware content selection rather than char/token-based cutting** |

## Size-Dependent Behavior

>_While the exact bifurcation point is unclear, Cursor behavior shows divergent patterns._
><br>_Variance may depend on content type, structure, and size._

| **Characteristic** | **High-Variance Cases** | **Stable Cases** |
| --- | --- | --- |
| **Examples** | `BL-1` 87 KB<br>`BL-2` 20 KB<br>`SC-1` 40 KB | `SC-2` 80 KB - 702 KB<br>`OP-4` 256 KB - 245 KB<br>`EC-6` 61 KB |
| **Consistency** | 2-3× variance across sessions | <1% variance across sessions |
| **Session<br>Dependency** | _New chat<br>different results_ | _Reproducible_<br>same URL = same content |
| **Reliability** | _Unreliable_ | Offer more consistency |

## Perception Gap

>_User char/token count comparisons to detect content subsettings, not agent self-report_

| **Test** | **Size** | **Returned** | **Reported** | **Gap** | **Why "Complete"** |
| --- | --- | --- | --- | --- | --- |
| `SC-3`<br>Wikipedia | 100 KB+ | 38 KB | _"Complete reference"_ | 62% missing | Clean section boundary<br>masks truncation |
| `BL-1`<br>MongoDB | 87 KB | 1.9K B | _"Internally valid"_ | 95% missing | No mid-sentence cutoff,<br>valid Markdown |
| `SC-4`<br>Markdown Guide | 65 KB | 28 KB | _"All syntax sections"_ | 57% missing | Footer intentionally filtered, excerpt coherent |
