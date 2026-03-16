---
layout: default
title: "Friction Note"
nav_order: 5
permalink: /docs/anysphere-cursor/friction-note
parent: Anysphere Cursor
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## WTF is Cursor?

<!-- compare platform differences, account setups, platform confusion, rate limiting -->

## Test Framework Note: Numbering

The test suite defines 13 total tests (BL-1-3, SC-1-4, OP-1,3-4, EC-1,3,6) but the recommended testing strategy only covers 10 critical tests. Tests OP-1 and EC-2,4,5 were either deprioritized (OP-1: fragment navigation) or not implemented (EC-2,4,5). The numbering reflects the original comprehensive test design before the strategy was optimized for the most critical ecosystem testing gaps.

# BL-1 Friction Note - MongoDB Change Events Page

## Setup
- Test: BL-1 (Short HTML page with heavy CSS)
- URL: https://www.mongodb.com/docs/manual/reference/change-events/create/
- Expected size: ~85KB
- Actual received: 1,953 characters

## Findings

### Content Received
- Compact excerpt focused on `create` change event only
- Includes: summary, field table, one JSON example
- Missing from full page: navigation, multiple sections, related links, cross-references

### Truncation Status
- **No mid-truncation detected**: content ends cleanly after closing code fence
- **But**: likely a platform-level excerpt, not the full 85KB page
- Question: Is Cursor presenting a summarized/excerpted version, or is this due to fetch truncation?

### Markdown Quality
- Headings intact (`## Summary`, `## Description`, `## Example`)
- Table present but formatting degraded (repeated pipes, wrapped lines)
- Code blocks valid (opening/closing ``` properly placed)

### Developer Friction
- Had to ask Cursor twice for structured output format
- Initial response was narrative; needed explicit "numbers only" request
- Suggestion: Template prompts could specify output format upfront

## Hypothesis Impact
- H1 (character-based truncation): Unclear—excerpt is short but may be intentional platform behavior
- H3 (structure-aware): If intentional, Cursor may be structure-aware in selection
- Needs: Comparison with raw track to confirm truncation vs. excerpt

## Next Steps
- Run BL-2 (same page, markdown) to compare sizes
- Run BL-3 (long page) to test behavior on larger content
- Compare @web vs mcp-server-fetch on same URL

## Expected vs Actual Size Mismatch

- **Expected**: ~85KB raw HTML (includes CSS, navigation, boilerplate)
- **Actual**: 1,953 characters (~2KB markdown)
- **Ratio**: ~2-3% of original page received

### Hypothesis
Cursor appears to be either:
1. Aggressively excerpting (selecting only "create" event section)
2. Stripping 97% of boilerplate during HTML-to-markdown conversion
3. Using platform-level filtering to return only relevant section

**Test to resolve**: BL-2 (same page, markdown source) will show if this is format-dependent or content-selection-dependent.

## Expected vs Actual Size Mismatch

- **Expected**: ~85KB raw HTML (includes CSS, navigation, boilerplate)
- **Actual**: 1,953 characters (~2KB markdown)
- **Ratio**: ~2-3% of original page received

### Hypothesis
Cursor appears to be either:
1. Aggressively excerpting (selecting only "create" event section)
2. Stripping 97% of boilerplate during HTML-to-markdown conversion
3. Using platform-level filtering to return only relevant section

**Test to resolve**: BL-2 (same page, markdown source) will show if this is format-dependent or content-selection-dependent.

After r1, BL-2:
This strongly suggests Cursor is excerpting/filtering intentionally, not just converting HTML to markdown. If it were pure HTML-to-markdown conversion efficiency, the markdown source (BL-2) should return significantly more content. But it's identical.

After r1, SC-2

## URL Resolution Finding

- **Requested URL**: https://docs.anthropic.com/en/api/messages (167 bytes — HTTP redirect)
- **Cursor fetched**: 702,885 characters from final destination
- **Actual page size**: ~700KB (much larger than initial 80KB estimate)

### Implication
Cursor successfully follows redirects and fetches the final destination page, not the redirect header. The large size difference between BL-1 (1,953 chars) and SC-2 (702,885 chars) suggests:
- **NOT a fixed character limit** (would cap BL-1 and SC-2 similarly)
- **Possibly token-based** (176K tokens for SC-2 vs 488 tokens for BL-1 — huge range)
- **Or content-dependent** (Cursor treats different content types differently)

**Hypothesis**: H2 (token-based truncation) with high ceiling (200K+ tokens?)

After r1, BL-3

✅ H2 (token-based) is strongly supported — Token counts vary 488 → 175,721 with no hard character limit
✅ Very high ceiling — Successfully returns 700KB+ pages
✅ Content-aware selection — Returns excerpts OR full docs depending on content type/structure
✅ No mid-truncation — No evidence of cutting mid-sentence or mid-code-block

Cursor's web fetch doesn't truncate mid-content. Instead, it intelligently selects relevant sections and returns them cleanly. No character or token ceiling detected within tested range (up to 700KB / 175K tokens). Content always ends at natural section boundaries (code fences, section headers, link lists).

After r1, SC-4
You're not looking at "truncation" anymore — you're looking at intelligent content filtering:

Keeps: Documentation, examples, core content
Removes: Navigation, footers, metadata, author info, CTAs to external products

after r1, EC-6
1. Returns full pages for standard HTML/markdown (BL-3, SC-2, OP-4, EC-6: all returned 200K+ chars cleanly)
2. Filters intelligently at section boundaries, removing footers/nav (SC-4: excluded marketing footer)
3. Fails gracefully on JavaScript-heavy SPAs (EC-1: timeout, 0 chars)
4. Handles redirects successfully (EC-3: 5-level redirect chain followed)
5. Perception gap: Model reports "complete" content even when it's a subset (SC-3, SC-4)