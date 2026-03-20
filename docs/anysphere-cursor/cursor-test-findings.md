---
layout: default
title: "Key Findings Cursor @Web Tool, Cursor-interpreted"
nav_order: 3
permalink: /docs/anysphere-cursor/cursor-test-findings
parent: Anysphere Cursor
---

## Key Findings for Cursor `@Web` Tool, Cursor-interpreted

---

**[Cursor-interpreted Test Workflow](/cursor-web-fetch/web_fetch_testing_framework.py)**:

    1. Run `python web_fetch_testing_framework.py --test {test ID} --track interpreted`
    2. Review the Terminal output
    3. Copy the provided prompt asking the model to report on `@Web` fetch results:
       character count, token estimate, truncation status, content completeness,
       Markdown formatting integrity
    4. Open a new Cursor chat session and paste the prompt into the chat window
    5. Capture model's full text response and observations as the interpreted-finding;
       gap between the model's self report and actual fetch behavior is a finding
    6. Log structured metadata as described in the `framework-reference.md`
    7. Ensure log results are saved to `cursor-web-fetch/results/cursor-interpreted/results.csv`

## Platform Limit Summary

| **Limit** | **Observed** |
| ------- | ---------- |
| **Hard Character Limit** | None detected - tested up to 702KB |
| **Hard Token Limit** | None detected - tested up to ~179K tokens |
| **Output Consistency** - Small | _High variance_: 2-3x across sessions, 1.9KB → 5.6KB same URL |
| **Output Consistency** - Large | _Highly stable_: <1% variance across sessions, 245KB identical across 3 runs |
| **Content Selection Behavior** | _Non-deterministic_ for small files; size-dependent |
| **Truncation Pattern** | When it occurs, respects content boundaries, no mid-sentence cuts |
| **JavaScript-heavy SPAs** | Truncation at ~6KB, ~1.5K tokens; _free tier times out, Pro tier truncates cleanly_ |
| **Redirect Chains** | Successfully follows, tested 5-level redirect chain |
| **Self-reported Completeness** | _Unreliable_: model claims "full content" when returning subset |

## Results Details

| --- | --- |
| **Model** | `Auto` |
| **Total Tests** | 23 |
| **Distinct URLs** | 11 |
| **Input Size Range** | 2KB–256KB |
| **Truncation Detection** | Model assertion, verbatim last-50-chars, Markdown integrity |


### Cross-run Output Variance

| **Test** | **Category** | **r1, chars** | **r2, chars** | **r3, chars** | **Variance** |
| ------ | ------- | ------: | ------: | ------: | ------: |
| **BL-1** | Small - 87KB input | 1,953 | 5,595 | 4,100 | 2.9x |
| **BL-2** | Small - 20KB input | 1,953 | 4,200 | 4,350 | 2.2x |
| **SC-2** | Large - 80KB input | 702,885 | 702,885 | 702,885 | 1.0x |
| **OP-4** | Large - 256KB input | 245,000 | 245,465 | 245,466 | 1.0x |
| **EC-1** | SPA - 100KB input | 0 - timeout | 5,857 | — | — |

### Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Spec** |
| --- | --------- | ------- | ---------- | ------------------- |
| **1** | **JavaScript-heavy SPAs have a ~6KB truncation ceiling** | EC-1<br> r1 & r2 | Free tier: timeout - 0 bytes; Pro tier: truncated at 5,857 chars, ~1.5K tokens, clean ending at last link block; suggests ~6KB or ~1.5K token ceiling specifically for SPA endpoints | **SPAs are truncated aggressively, ~6KB, not completely blocked; free tier timeouts mask Pro tier truncation behavior** |
| **2** | **Static HTML/Markdown pages have no detected ceiling** | BL-1 through OP-4,<br> SC-2 - 702KB,<br> OP-4 - 245KB | Successfully returned 702,885 characters from SC-2; 245,465 characters from OP-4; no truncation observed on static content | **No practical character ceiling detected for static docs; tested up to 700KB** |
| **3** | **Output consistency is size-dependent** | BL-1,<br> BL-2,<br> SC-2,<br> OP-4 | Small files, 1-20KB: 2-3× variance across sessions, 1.9K→5.6K; large files, 80-256KB: <1% variance, 702.8K identical, 245.5K identical | **Cursor's fetch behavior reliability depends on doc size — small docs are unreliable, large docs are stable** |
| **4** | **Content selection is non-deterministic for small files, session-dependent** | BL-1<br> r1-r4,<br> BL-2<br> r1-r3 | Identical prompts in different chat sessions produced 1,953 → 5,595 → 4,100 → 5,500 chars on BL-1; new sessions returned larger content than original session | **New chat sessions influence `@Web` output; conversation state affects fetch behavior** |
| **5** | **Same logical content, different formats, different sizes** | BL-1, HTML vs BL-2, Markdown<br> both r1 | Both returned 1,953 chars despite different source format, HTML vs `.md`; later runs diverged - 5,595 vs 4,200 - suggesting format-dependent processing | **Format affects fetch behavior; Cursor may process HTML and Markdown sources differently** |
| **6** | **Intelligent content filtering, not hard truncation (for static pages)** | SC-4,<br> EC-6,<br> all large tests | SC-4, 30KB page returned 28KB excluding footer/nav/metadata; EC-6 returned full 71KB including complex Markdown; content always ends at section boundaries | **For static content: Cursor doesn't truncate mid-content, but filters non-essential structural elements while preserving documentation integrity** |
| **7** | **Model's self-reported completeness diverges from actual content** | SC-3,<br> BL-1<br> r3-r4, EC-1<br>r2 | SC-3: Model reports "no truncation, complete reference" but content cuts mid-references section; EC-1 r2: Model acknowledges truncation at ~6KB despite 100KB expected | **Self-report of content completeness is unreliable — model perceives filtered excerpts as "complete" because internally valid** |
| **8** | **Redirect chains handled transparently** | EC-3 | 5-level redirect chain successfully followed; returned final destination content - 850 chars JSON with no truncation | **Cursor's `@Web` follows HTTP redirects without user awareness or latency penalty** |
| **9** | **Hypothesis H2 - token-based with high ceiling - supported for static content** | SC-2,<br> OP-4,<br> EC-6,<br> BL-3 | Token counts range 488 - BL-1 - to 175,721 - SC-2 - with no observable limit; successfully returned 61K token document, OP-4, multiple times identically | **For static pages: If token-based, ceiling is extremely high - 200K+; effectively no practical limit** |
| **10** | **Hypothesis H3 - structure-aware truncation, confirmed for static content** | BL-1,<br> BL-2,<br> SC-2,<br> SC-3,<br> SC-4<br> r1-r3 | 8 tests matched H3: content selection respects Markdown section boundaries; truncation occurs at header boundaries, code fence closes, list endings | **For static pages, Cursor uses intelligent, structure-aware content selection rather than character/token-based cutting** |

## Size-Dependent Behavior

While the exact bifurcation point is unclear, `@Web` behavior shows divergent
consistency patterns; variance depends on content type, structure and size:

| **Characteristic** | **High-Variance Cases** | **Stable Cases** |
| --- | --- | --- |
| **Examples** | BL-1, 87KB;<br> BL-2, 20KB;<br> SC-1, 40KB | SC-2, 80KB→702KB;<br> OP-4, 256KB→245KB;<br> EC-6, 61KB |
| **Consistency** | 2-3× variance across sessions | <1% variance across sessions |
| **Session-dependency** | _New chat = different results_ | _Reproducible_: same URL = same content |
| **Reliability** | _Unreliable_ for automated systems | Suitable for agents needing consistency |

## Perception Gap

| **Test** | **Size** | **Returned** | **Reported** | **Gap** | **Why "Complete"** |
| --- | --- | --- | --- | --- | --- |
| **SC-3** - Wikipedia | 100KB+ | 38KB | _"Complete reference"_ | 62% missing | Clean section boundary masks truncation |
| **BL-1** - MongoDB | 87KB | 1.9KB | _"Internally valid"_ | 95% missing | No mid-sentence cutoff, valid Markdown |
| **SC-4** - Markdown Guide | 65KB | 28KB | _"All syntax sections"_ | 57% missing | Footer intentionally filtered, excerpt coherent |

> _**Implication for agents**: to detect content subsetting, rely on character/token count comparison, not model self-report_
