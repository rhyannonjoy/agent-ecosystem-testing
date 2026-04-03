---
layout: default
title: Table of Contents
---

>**<u>Objective</u>**: in support of the
[Agent Docs Spec](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits),
measure what happens between "agent fetches URL" and "model sees content" -
retrieval mechanism behavior, HTML processing, truncation limits - for platforms that don't document these details
>
>**<u>Methodology</u>**: two-track measurement approach with an **interpreted-track** - ask
the model to describe what it received to capture DX and reveal perception gaps, and a **raw track** -
extract raw output and measure programmatically, character and token counts, truncation boundaries
to produce spec-ready, citable measurements

## Documentation Organization

| **Section** | **Purpose** |
| --------- | --------- |
| **Methodology** | Testing approach details & constraints |
| **Interpreted vs Raw** | Two-track values and measurements |
| **Findings: Interpreted** | What the model reports vs what it received, run variation |
| **Findings: Raw** | Metrics extracted programmatically - reproducible, spec-ready |
| **Friction Note** | Known issues, gaps, or edge cases encountered during testing |

## Results Summary

| **Platform** | **Key Finding** | **Focus** |
| ---------- | ------------- | ---------- |
| **[Anthropic Claude API](/docs/anthropic-claude-api-web-fetch-tool/methodology.md)** | Character-based truncation at<br>~**100KB** of rendered content | Baseline reference; establishing two-track methodology |
| **[Anysphere Cursor](/docs/anysphere-cursor/methodology.md)** | Agent-routed fetch with undocumented truncation - **28KB–240KB+**;<br>high cross-session variance | Reverse-engineering opaque, closed consumer tools |
| **[Cognition Windsurf Cascade](/docs/cognitition-windsurf-cascade/methodology.md)** | Currently testing | Reverse-engineering opaque, closed consumer tools |
| **[Google Gemini API](/docs/google-gemini-url-context-tool/methodology.md)** | Hard limit: **20 URLs** per request;<br>supports PDF & JSON | Identifying architectural constraints and format support |
| **[Microsoft GitHub Copilot](/docs/microsoft-github-copilot/methodology.md)** | Agent-routed `fetch_webpage` - relevance-ranked excerpts, no fixed ceiling detected and/or `curl` - byte-perfect full retrieval | Separating retrieval mechanism from retrieval quality through tool-call visibility |
| **[OpenAI Web Search](/docs/open-ai-web-search-tool/methodology.md)** | Tool invocation **conditional** and model-dependent; differs by API surface | Comparing behavior across <br>API endpoints |
