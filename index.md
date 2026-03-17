---
layout: default
title: Table of Contents
---

>**<u>Objective</u>**: in support of the
[Agent Docs Spec](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits),
measure what happens between "agent fetches URL" and "model sees content" —
truncation limits, HTML processing, content negotiation - for platforms that don't document these details
>
>**<u>Methodology</u>**: two-track measurement approach with an **interpreted-track** - ask
the model to describe what it received to capture DX and reveal perception gaps, and a **raw track** -
extract raw output and measure programmatically, character and token counts, truncation boundaries
to produce spec-ready, citable measurements

## Documentation Organization

| **Section** | **Purpose** |
|---------|---------|
| **Methodology** | Testing approach details & constraints |
| **Interpreted vs Raw** | Two-track values and measurements |
| **Findings: Interpreted** | What the model reports vs what it received, run variation |
| **Findings: Raw** | Metrics extracted programmatically - reproducible, spec-ready |
| **Friction Note** | Known issues, gaps, or edge cases encountered during testing |
 
## Results Summary
 
| **Platform** | **Key Finding** | **Best For** |
|----------|-------------|----------|
| **[Anthropic Claude API](/docs/anthropic-claude-api-web-fetch-tool/methodology)** | Character-based truncation at ~**100KB** of rendered content | Baseline reference; established measurement methodology |
| **[Anysphere Cursor](/docs/anysphere-cursor/methodology)** | Investigating truncation limits, MCP override behavior, auto-chunking | Documenting closed consumer applications, no public APIs |
| **[Google Gemini API](/docs/google-gemini-url-context-tool/methodology)** | Hard limit: **20 URLs** per request; supports PDF & JSON | Understanding platform-specific constraints |
| **[OpenAI Web Search](/docs/open-ai-web-search-tool/methodology)** | Tool invocation **conditional** and model-dependent; differs by API surface | Comparing behavior across Chat Completions vs Responses API |
