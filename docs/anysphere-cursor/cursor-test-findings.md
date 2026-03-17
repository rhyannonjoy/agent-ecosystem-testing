---
layout: default
title: "Key Findings Cursor @Web Tool, Cursor-interpreted"
nav_order: 3
permalink: /docs/anysphere-cursor/web-fetch-tool/cursor-web-findings
parent: Anysphere Cursor
---

## Key Findings for Cursor `@Web` Tool, Cursor-interpreted

---

**Cursor-interpreted Test Workflow**:

    1. Run `python web_fetch_testing_framework.py --test [test name] --track interpreted`
       and review the Terminal output
    2. Copy the provided prompt asking the model to report on @Web fetch results:
       character count, token estimate, truncation status, content completeness,
       markdown formatting integrity
    3. Open a new Cursor chat session and paste the prompt into the chat window
    4. Capture the model's full text response and observations as the interpreted finding;
       the gap between the model's self report and actual fetch behavior is a finding
    5. Log structured metadata: output size, token count, truncation assertion, hypothesis match
       as described in the `testing-framework-instructions.md`
    6. Ensure that the log results are saved to `cursor-web-fetch/results/cursor-interpreted/`

---

## Platform Limit Summary

| **Limit** | **Observed** |
| ------- | ---------- |
| **Hard Character Limit** | None detected - tested up to 702KB |
| **Hard Token Limit** | None detected - tested up to ~179K tokens |
| **Output Consistency** - Small Files | High variance: 2-3x across sessions, 1.9KB → 5.6KB same URL |
| **Output Consistency** - Large Files | Highly stable: <1% variance across sessions, 245KB identical across 3 runs |
| **Content Selection Behavior** | Non-deterministic for small files; size-dependent |
| **Truncation Pattern** | When it occurs, respects content boundaries, no mid-sentence cuts |
| **JavaScript-heavy SPAs** | Truncation at ~6KB, ~1.5K tokens; free tier times out, Pro tier truncates cleanly |
| **Redirect Chains** | Successfully follows, tested 5-level redirect chain |
| **Self-reported Completeness Accuracy** | Unreliable: model claims "full content" when returning subset |

## Results Details

Model: `Claude 3.5 Sonnet` · 22 tests across interpreted track

### Cross-run Output Variance

| Test | Category | r1 (chars) | r2 (chars) | r3 (chars) | Variance |
| ------ | ------- | ------: | ------: | ------: | ------: |
| BL-1 | Small (87KB input) | 1,953 | 5,595 | 4,100 | 2.9x |
| BL-2 | Small (20KB input) | 1,953 | 4,200 | 4,350 | 2.2x |
| SC-2 | Large (80KB input) | 702,885 | 702,885 | 702,885 | 1.0x |
| OP-4 | Large (256KB input) | 245,000 | 245,465 | 245,466 | 1.0x |

### Truncation Analysis

| # | Finding | Tests | Observed | Spec Contribution |
| --- | --------- | ------- | ---------- | ------------------- |
| 1 | **No hard character limit exists** | BL-1 through EC-6, all tests | Successfully returned 702,885 characters from SC-2; 245,465 characters from OP-4; tested across 2KB to 256KB input range | **No practical character ceiling detected within tested range (up to 700KB)** |
| 2 | **Output consistency is size-dependent** | BL-1, BL-2, SC-2, OP-4 | Small files (1-20KB): 2-3× variance across sessions (1.9K→5.6K); Large files (80-256KB): <1% variance (702.8K identical, 245.5K identical) | **Cursor's fetch behavior reliability depends on document size — small docs are unreliable, large docs are stable** |
| 3 | **Content selection is non-deterministic for small files, session-dependent** | BL-1 r1-r4, BL-2 r1-r3 | Identical prompts in different chat sessions produced 1,953 → 5,595 → 4,100 → 5,500 chars on BL-1; new sessions returned larger content than original session | **New chat sessions influence @Web output; conversation state affects fetch behavior** |
| 4 | **Same logical content, different formats, different sizes** | BL-1 (HTML) vs BL-2 (Markdown), both r1 | Both returned 1,953 chars despite different source format (HTML vs .md file); later runs diverged (5,595 vs 4,200), suggesting format-dependent processing | **Format affects fetch behavior; Cursor may process HTML and Markdown sources differently** |
| 5 | **Intelligent content filtering, not hard truncation** | SC-4, EC-6, all tests | SC-4 (30KB page) returned 28KB excluding footer/nav/metadata; EC-6 returned full 71KB including complex markdown; content always ends at section boundaries | **Cursor doesn't truncate mid-content — it intelligently filters non-essential structural elements while preserving documentation integrity** |
| 6 | **Model's self-reported completeness diverges from actual content** | SC-3, BL-1 r3-r4, all large tests | SC-3: Model reports "no truncation, complete reference" but content cuts mid-references section; BL-1 r3-r4: Model says "truncated version" but ends cleanly at section boundary | **Self-report of content completeness is unreliable — model perceives filtered excerpts as "complete" because they're internally valid** |
| 7 | **Failure modes: JavaScript SPAs timeout completely** | EC-1 | Google Docs SPA returned 0 bytes; no partial content, no error message | **Cursor cannot handle JavaScript-rendered single-page applications; SPAs result in silent timeout** |
| 8 | **Redirect chains handled transparently** | EC-3 | 5-level redirect chain (`httpbin.org/redirect/5`) successfully followed; returned final destination content (850 chars JSON) with no truncation | **Cursor's @Web follows HTTP redirects without user awareness or latency penalty** |
| 9 | **Hypothesis H3 (structure-aware truncation) confirmed** | BL-1, BL-2, SC-2, SC-3, SC-4 r1-r3 | 8 tests matched H3: content selection respects markdown section boundaries; truncation occurs at header boundaries, code fence closes, list endings | **Cursor uses intelligent, structure-aware content selection rather than character/token-based cutting** |
| 10 | **Hypothesis H2 (token-based with very high ceiling) supported** | SC-2, OP-4, EC-6, all large tests | Token counts range 488 (BL-1) to 175,721 (SC-2) with no observable limit; successfully returned 61K token document (OP-4) multiple times identically | **If token-based, ceiling is extremely high (200K+); effectively no practical limit for typical documentation** |

## Size-Dependent Behavior: The Critical Finding

Cursor's @Web behavior bifurcates sharply at ~50KB:

**Small files (1-50KB):**
- Highly non-deterministic: 2-3× variance across sessions
- Session-state dependent: new chat = different results
- Format matters: HTML vs Markdown source affects output
- Use case friction: unreliable for consistent content extraction

**Large files (50KB+):**
- Highly stable: <1% variance (identical to machine precision)
- Reproducible: same URL = same content across sessions
- Reliable: suitable for agents that depend on consistent fetch behavior
- Use case fit: documentation scraping, knowledgebase ingestion

## Perception Gap: Content Subset vs. Perceived Completeness

The model frequently reports content as "complete" or "fully fetched" when it's actually a subset:

- **SC-3 (Wikipedia)**: Returns 38KB of 100KB+ source; reports "clean ending at reference" (which is mid-references)
- **BL-1 (MongoDB)**: Returns 1.9KB of 87KB page; reports "complete, internally valid" (but missing 95% of page)
- **SC-4 (Markdown Guide)**: Returns 28KB of 65KB source; reports "all syntax sections present" (footer removed intentionally)

**The model perceives these as complete because:**
1. No mid-sentence or mid-code-block cutoff (respects boundaries)
2. Returned excerpt is internally coherent and valid markdown
3. No explicit truncation marker (e.g., "... [truncated]")

**Implication for agents**: Rely on character/token count comparison, not model self-report, to detect content subsetting.

## Key Differences from Claude API Web Fetch

| Aspect | Claude API | Cursor @Web |
| --- | --- | --- |
| Truncation strategy | Token-based (~2K token ceiling) | Size-dependent non-deterministic |
| Consistency | Deterministic | Session/format-dependent for small files |
| Large files | Not tested in Claude baseline | Extremely stable (>245KB tested) |
| Redirect handling | Reported issue in early testing | Works transparently |
| SPA handling | Not tested | Complete failure (timeout) |
| Perception gap | Not reported | Significant (model overstates completeness) |

---

## Testing Methodology Notes

- **Track**: Interpreted only (model's self-report of fetch results)
- **Model**: Claude 3.5 Sonnet
- **Test scope**: 11 distinct URLs, 22 total runs (3-4 runs per URL in fresh chat sessions)
- **Size range tested**: 2KB to 256KB input
- **Truncation detection**: Model assertion + last-50-chars verbatim capture + markdown integrity check

## Pending Investigation

1. **Raw track measurement**: Exact byte counts via file capture (model estimates used for this analysis)
2. **MCP comparison**: OP-3 run with `mcp-server-fetch` vs `@Web` on same URL
3. **Token ceiling confirmation**: Larger files (500KB+) to test if ceiling exists above 175K tokens tested
4. **Format-dependency**: Systematic HTML vs. Markdown source comparison across more tests
5. **Session state isolation**: Investigate what conversation-level variables influence fetch behavior