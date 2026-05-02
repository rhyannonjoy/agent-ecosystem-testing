---
layout: default
title: "Methodology"
permalink: /docs/anthropic-claude-api-web-fetch-tool/methodology
---

# Methodology

---

## Approach Comparison

[Dachary Carey's Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/)
documented Claude Code's web fetch behavior by interacting with Claude directly in a chat
interface. _This testing took a different approach, targeting a different tool_.

**Dachary talked to Claude Code directly** in a chat interface, asked it to fetch pages
and report back what it received, then observed the outputs. Claude Code's web fetch has a
summarization LLM in the pipeline, so Dachary's measurements included what the summarization LLM,
`Claude Haiku 3.5`, reported back after processing the fetched content. Two layers of AI interpretation
filtered data before Dachary saw it.

**This testing uses a Python script** to call the Claude API directly with the
web fetch tool enabled. The API tool doesn't have an intermediate summarization LLM. The
fetched content goes straight into the main LLM's context as a document block. The second script,
_`web_fetch_test_raw.py`_, goes one step further and extracts the raw content directly from the response
object in Python, bypassing Claude's interpretation entirely. Python string operations measure character
counts and boilerplate percentages not estimated by a LLM.

**Why this matters for the spec**: Dachary was documenting Claude Code's behavior. This testing
documents the Claude API web fetch tool's behavior. These are genuinely different implementations
with different pipelines, which is exactly the gap in
[the Known Platform Limits table](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits)
that this testing fills. Dachary's description of the CSS problem, the summarization LLM seeing only CSS,
doesn't reproduce in the API tool because the pipeline is different. That isn't a contradiction, but
evidence that the two tools work differently, which is a useful finding for agent developers or docs teams
who may be using one or the other.

---

## Script Comparison

This two-track approach identifies gaps between agent perception and API reality -
[Claude-interpreted vs Raw](claude-interpreted-vs-raw.md) compares findings from both:

| | **Interpreted**| **Raw** |
| - | --------------------- | --------------------- |
| **Measures** | Claude's interpretation of<br>fetched content | Raw content extracted directly<br>from response object |
| **Character<br>Counts** | Claude estimates,<br>vary between runs | Python `len()` on raw string,<br>exact, reproducible |
| **Boilerplate Detection** | Claude's subjective<br>assessment | CSS indicator strings counted<br>programmatically |
| **Truncation Detection** | Claude reports what<br>it perceives | Exact char position, end character, clean/unclean flag |
| **Tokens** | _Higher_ - Claude writes<br>long assessments | _Lower_ - minimal prompt,<br>`max_tokens=128` |
| **Best For** | Understanding agent perception | Citable measurements for<br>the spec |
