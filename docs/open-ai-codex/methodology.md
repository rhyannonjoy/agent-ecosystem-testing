---
layout: default
title: "Methodology"
nav_order: 1
permalink: /docs/open-ai-codex/methodology
parent: OpenAI Codex
---

# Methodology

---

## Turn-by-Turn

>_**Chat-based measurement through interaction, without direct code instrumentation**_

The Codex testing framework is the fourth in a series of chat-based agent testing frameworks
in this collection, following [Cursor](/docs/anysphere-cursor/methodology),
[Copilot](/docs/microsoft-github-copilot/methodology), and
[Cascade](/docs/cognition-windsurf-cascade/methodology). Each platform has uncovered a different
relationship between deployment surface, fetch syntax, and observable agent behavior, a pattern
that directly shapes this framework's design. Where Cascade introduced a third track to isolate
`@web` as a variable, Codex introduces a fourth track to isolate deployment surface itself.

---

## Surface Comparison

>_**Does deployment context change retrieval behavior?**_

Across all prior frameworks, testing targeted a single surface per platform and added tracks to
isolate variables within that surface. Cascade's three-track design isolated directive `@web`, but
the finding was redundancy. Codex inherits that logic and extends it to a higher-order variable: the
same setting accessible through two different deployment surfaces. The four-track design intends to
test whether surface context, among other agentic architectural constraints, drives retrieval behavior
differences.

| **Platform** | **Tracks** | **Primary Variable** | **Finding** |
| ------------ | ---------- | --------------------- | ----------- |
| **[Cursor](../anysphere-cursor/cursor-interpreted-vs-raw.md)** | 2 | `@Web` context attachment<br>vs autonomous fetch | `@Web` redundant; `WebFetch`, `mcp_web_fetch` <br>called regardless |
| **[Copilot](../microsoft-github-copilot/copilot-interpreted-vs-raw.md)** | 2 | `fetch_webpage` autonomous fetch, Copilot-interpreted<br>vs Raw | `fetch_webpage` agent-selected; `curl` substitution byte-perfect, but unreadable; no detected ceiling |
| **[Cascade](../cognition-windsurf-cascade/cascade-interpreted-explicit-vs-raw.md)** | 3 | `@web` directive impact on ceiling, toolchain, chunking | `@web` redundant with URL; two-stage chunking pipeline; read-write asymmetry |
| **[Codex](codex-test-findings.md)** | _4_ | _Standalone environment versus VS Code extension_ | _Does surface context change tool selection, truncation ceiling, or retrieval behavior?_ |

## Architecture Comparison

>_**Testing surface variants of the same underlying LLM family**_

[Codex](https://developers.openai.com/codex) and
[Codex-powered VS Code](https://developers.openai.com/codex/ide) use `GPT` LLMs but present different
execution environments, workspace contexts, and potentially different retrieval toolchains. While
Codex didn't name any specific tools, Codex-powered VS Code cited `web` and `web.open` during
preliminary questioning. [Cascade](/docs/cognition-windsurf-cascade/methodology), agents referenced
`read_url_content`, `view_content_chunk`, and `search_web` when asked while
[Copilot's](/docs/microsoft-github-copilot/methodology) `fetch_webpage` initially only appeared in
error code messages.

| **Aspect** | **Copilot** | **Codex** | **VS Code-Codex** |
| -------- | ------------------- | ---------------- | ------------------------------- |
| **Syntax** | _Undocumented_ | _Undocumented_ | _Undocumented_ |
| **Tools** | `fetch_webpage`, `curl` | _Unknown_ | `web`, `web.open`, `curl` |
| **Workspace** | VS Code present | _No local workspace_ | VS Code present |
| **Repeatability** | _Low_: `Auto` routing variance | _High_: user-selected LLM,<br>intelligence level | _High_: user-selected LLM, intelligence level |
| **Questions** | _Does `fetch_webpage` have an agent-dependent ceiling?_ | _What tools does Codex expose? Does workspace isolation impact retrieval?_ | _Does workspace context contaminate retrieval?_ |

## Track Design

| | **T1** | **T2** | **T3** | **T4** |
| - | ----------- | ----------- | ----------- | ----------- |
| **Surface** | Codex | VS Code-Codex | Codex | VS Code-Codex |
| **Method** | GPT-interpreted | GPT-interpreted | Raw | Raw |
| **Question** | _What does Codex report in isolation? Does it perceive truncation?_ | _What does VS Code-Codex report back with workspace? Does surface change self-perception?_ | _What does Codex's retrieval mechanism return verbatim?_ | _Does VS Code-Codex raw retrieval output differ from Codex?_ |
| **Prompt** | Fetch URL, report measurements; no workspace | Fetch URL, report measurements; workspace present | Fetch URL, return output verbatim; verification script extracts measurements | Fetch URL, return output verbatim; verification script extracts measurements |
| **Measurements** | Agent estimates: _"appears truncated at ~X chars," "Markdown seems complete"_ | _Same as T1_; compared against Codex direct baseline | Character count via `len()`, token count via `tiktoken`, exact truncation point, last 50 characters | _Same as T3_; compared against Codex direct raw baseline |
| **Best For** | Understanding DX, invocation patterns in isolated environment | Understanding DX with workspace context | Retrieval ceiling in isolation | Surface-variant retrieval comparison |

> _VS Code-Codex workspace context is a confound that can't be fully controlled, analysis treats it as a variable of interest rather than noise._

---

## Codex-Specific Unknowns

| **Question** | **Details** | **Approach** | **Value** |
| ------------ | ----------- | ------------ | --------- |
| **Unverified Retrieval Mechanism** | VS Code-Codex agents named `web`, but it's undocumented | Observe any tool names reported in output per run; compare across surfaces | Establishes whether Codex exposes a consistent, nameable retrieval mechanism |
| **Surface-Driven Behavioral Divergence** | Unknown whether workspace isolation changes retrieval, tool selection, or ceiling | Compare raw track measurements across T3, T4 | Determines whether surface context is meaningful variable |
| **Model Routing Stability** | Copilot's default `Auto` selection included more than `GPT` while Codex restricts to `GPT`, but allows for user-set stability | Log LLM and intelligence level<br>per run | Isolates whether findings are attributable to any specific `GPT` LLM or intelligence level |
| **Workspace Context Contamination** | Agents may autonomously substitutes local code execution when workspace scripts are present | Log all runs where agents attempt substitution | Determines whether workspace isolation required as a precondition for clean track execution |
