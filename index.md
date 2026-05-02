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

| **Platform** | **Key Finding** | **Focus** |
| ---------- | ------------- | ---------- |
| **[Anthropic Claude API](/docs/anthropic-claude-api-web-fetch-tool/methodology.md)** | Char-based truncation at ~**100 KB** of rendered content | Baseline reference;<br>establishing two-track methodology |
| **[Anysphere Cursor](/docs/anysphere-cursor/methodology.md)** | Agent-routed fetch with undocumented truncation<br>**28 KB–240 KB+**; high cross-session variance | Reverse-engineering opaque, closed<br>consumer tools |
| **[Cognition Windsurf Cascade](/docs/cognition-windsurf-cascade/methodology)** | Two-stage chunking-pipeline, no fixed ceiling; retrieval completeness agent, source size-dependent; read-write asymmetry confirmed; `@web` redundant with a URL | Three-track design;<br> truncation testing<br>partially documented<br>lossy architecture |
| **[Google Gemini API](/docs/google-gemini-url-context-tool/methodology.md)** | Hard limit: **20 URLs** per request; supports PDF and JSON | Identifying architectural constraints, format support |
| **[Microsoft GitHub Copilot](/docs/microsoft-github-copilot/methodology.md)** | Agent-routed `fetch_webpage`&rarr;relevance-ranked excerpts, no fixed ceiling detected vs `curl` byte-perfect full retrieval | Separating retrieval mechanism from retrieval quality through<br>toolchain visibility |
| **[OpenAI Web Search](/docs/open-ai-web-search-tool/methodology.md)** | Tool invocation **conditional**, agent-dependent;<br>differs by API surface | Comparing behavior across different APIs |
