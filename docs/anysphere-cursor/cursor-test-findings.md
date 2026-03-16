---
layout: default
title: "Key Findings for Cursor's @Web Tool, Cursor-interpreted"
permalink: /docs/anysphere-cursor/cursor-test-findings
nav_order: 3
parent: Anysphere Cursor
---

## Key Findings for Cursor's @Web Tool, Cursor-interpreted

---

Free-write r1: BL-1

Expected: ~85KB = 85,000 characters (raw HTML with CSS overhead)
Actual: 1,953 characters = ~2KB of markdown
That's roughly 2-3% of the original page size making it through.
This suggests one of three things:

Cursor's fetch is heavily summarizing/excerpting — It's not just truncating at a character limit; it's actively selecting and condensing the content (just the "create" event section, not the full page)
Cursor's HTML-to-markdown conversion is extremely aggressive — It's stripping 97% of the page (CSS, navigation, boilerplate) which is actually very efficient
Platform-level filtering — Cursor may be returning only the most relevant section of the page based on the URL/context