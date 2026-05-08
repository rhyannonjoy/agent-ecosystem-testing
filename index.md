---
layout: default
title: Testing Index
---

# Testing Index

Empirical measurement of what happens between _"agent fetches URL"_ and _"user sees output"_ -
retrieval mechanism behavior, content transformation, and architectural constraints. Observes
the URL-to-response pipeline through layers platforms don't disclose. Documents output variation
with a two-track approach: **interpreted** captures agent self-perception, **raw** produces citable
data for the [Agent-Friendly Documentation Spec](https://agentdocsspec.com/).

---

## Blogs

| **Post** | **Focus** |
| -------- | --------- |
| **[Field Notes from a Yelper: Guerrilla Testing Agents](/blogs/field-notes-from-yelper.md)** | Methodology evolution: what broke,<br>what changed, and letting data lead |

## Documentation Structure

| **Section** | **Purpose** |
| --------- | --------- |
| **Methodology** | Testing approach details, track design, constraints |
| **Interpreted vs Raw** | Observations, implications for agent devs, docs teams |
| **Findings: Interpreted** | Agentic retrieval, reasoning, reporting |
| **Findings: Raw** | Agentic write behavior, programmatically extracted metrics |
| **Friction Note** | Known issues, gaps, or edge cases encountered during testing |

## Results Summary

>_More analysis in [Platform Comparisons](/docs/platform-comparisons.md). Platform links lead to testing methodologies_.

| **Platform** | **Key Finding** | **Focus** |
| ---------- | ------------- | ---------- |
| **[Anthropic Claude API](/docs/anthropic-claude-api-web-fetch-tool/methodology.md)** | Char-based truncation at ~**100 KB** of rendered content | Baseline reference; establishing two-track methodology |
| **[Anysphere Cursor](/docs/anysphere-cursor/methodology.md)** | Agent-routed fetch with undocumented truncation **28 KB–240 KB+**;<br>high cross-session variance | Reverse-engineering opaque, closed consumer tools |
| **[Cognition Windsurf Cascade](/docs/cognition-windsurf-cascade/methodology.md)** | Two-stage chunking-pipeline, no fixed ceiling; retrieval completeness agent and source size-dependent; read-write asymmetry; `@web` redundant with a URL | Three-track design; truncation testing partially documented lossy architecture |
| **[Google Gemini API](/docs/google-gemini-url-context-tool/methodology.md)** | Hard limit: **20 URLs** per request; supports PDF and JSON | Identifying architectural constraints, format support |
| **[Microsoft GitHub Copilot](/docs/microsoft-github-copilot/methodology.md)** | Agent-routed `fetch_webpage`&rarr;relevance-ranked excerpts, no fixed ceiling detected vs `curl` byte-perfect full retrieval | Separating retrieval mechanism from retrieval quality through toolchain visibility |
| **[OpenAI Codex](/docs/open-ai-codex/methodology.md)** | _testing in progress_ | Surface Comparison |
| **[OpenAI Web Search](/docs/open-ai-web-search-tool/methodology.md)** | Tool invocation **conditional**, agent-dependent; differs by API surface | Comparing behavior across different APIs |
