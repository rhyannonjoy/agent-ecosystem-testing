---
layout: default
title: "Methodology"
permalink: /methodology/
---

## Methodology

[Dachary Carey's Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/)
documented Claude Code's web fetch behavior by interacting with Claude directly in a chat
interface. _This testing took a different approach, targeting a different tool_.

**Dachary talked to Claude Code directly** in a chat interface, asked it to fetch pages
and report back what it received, then observed the outputs. Claude Code's web fetch has a
summarization model in the middle - so what Dachary was measuring was what the summarization model,
Claude 3.5 Haiku, reported back after processing the fetched content. Two layers of AI interpretation
filtered data before Dachary saw it.

**This testing uses a Python script** to call the Claude API directly with the
web fetch tool enabled. The API tool doesn't have an intermediate summarization model. The
fetched content goes straight into the main model's context as a document block. The second script,
`web_fetch_test_raw.py`, goes one step further and extracts the raw content directly from the response
object in Python, bypassing Claude's interpretation entirely. Python string operations measure character counts
and boilerplate percentages and not estimated by a model.

**Why this matters for the spec**: Dachary was documenting Claude Code's behavior. This testing
documents the Claude API web fetch tool's behavior. These are genuinely different implementations
with different pipelines, which is exactly the gap in
[the Known Platform Limits table](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits)
that this testing fills. Dachary's CSS problem - the summarization model seeing only CSS -
doesn't reproduce in the API tool because the pipeline is different. That isn't a contradiction, but
evidence that the two tools work differently, which is a useful finding for tech writers who may be
using one or the other.

---

## Script Comparison

This two-track approach surfaces gaps between model perception and API reality -
[Claude-interpreted vs Raw](claude-interpreted-vs-raw.md) compares findings from both -

| | `web_fetch_test.py` | `web_fetch_test_raw.py` |
| - | --------------------- | --------------------- |
| What it measures | Claude's interpretation of fetched content | Raw content extracted directly from response object |
| Character counts | Claude estimates - vary between runs - | Python `len()` on raw string - exact, reproducible |
| Boilerplate detection | Claude's subjective assessment | CSS indicator strings counted programmatically |
| Truncation detection | Claude reports what it perceives | Exact char position, end character, clean/unclean flag |
| Token cost per run | Higher - Claude writes long assessments | Lower  - minimal prompt, `max_tokens=128` |
| Best used for | Understanding what the model perceives | Citable measurements for the spec |
