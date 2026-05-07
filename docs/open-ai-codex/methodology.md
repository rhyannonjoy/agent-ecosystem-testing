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

>_**A new variable: does deployment context change retrieval behavior?**_

Across all prior frameworks, testing targeted a single deployment surface per platform and added
tracks to isolate variables within that surface. Cascade's three-track design isolated `@web`
as a directive variable, but the finding was redundancy. Codex inherits that logic and extends it
to a higher-order variable: the same setting accessible through two different deployment surfaces.
The four-track design below exists specifically to test whether surface context, not LLM, drives
retrieval behavior differences.

| **Platform** | **Tracks** | **Variable Isolated** | **Finding** |
| ------------ | ---------- | --------------------- | ----------- |
| **Cursor** | 2 | `@Web` directive vs. autonomous fetch | `@Web` redundant; `WebFetch`, `mcp_web_fetch` called regardless |
| **Copilot** | 2 | Interpreted vs. raw `fetch_webpage` output | `fetch_webpage` agent-selected; `curl` substitution byte-perfect but unreadable; no documented ceiling |
| **Cascade** | 3 | `@web` directive effect on ceiling, toolchain, chunking | `@web` redundant with URL; two-stage chunking pipeline; read-write asymmetry |
| **Codex** | _4_ | _Deployment surface: standalone environment versus VS Code extension_ | _Does surface context change tool selection, truncation ceiling, or retrieval behavior? |

## Architecture Comparison

>_**Testing surface variants of the same underlying model**_

Rather than comparing across models or isolating a directive variable, Codex testing compares
across deployment surfaces. Both targets — Codex directly and Copilot (Codex-powered) in VS Code
— share an underlying model but present different execution environments, workspace contexts, and
potentially different retrieval toolchains. Tool names are unknown going into testing; discovery
is part of the framework. Compare with the [Cascade methodology](/docs/cognition-windsurf-cascade/methodology),
where `read_url_content`, `view_content_chunk`, and `search_web` surfaced through agent self-report
during runs, and the [Copilot methodology](/docs/microsoft-github-copilot/methodology), where
`fetch_webpage` surfaced only through tool logs with no public documentation.

| **Aspect** | **Copilot (prior)** | **Codex Direct** | **Codex via Copilot Extension** |
| -------- | ------------------- | ---------------- | ------------------------------- |
| **User Fetch Syntax** | _None documented_ | _Unknown going in_ | _None documented_ |
| **Tools Observed** | `fetch_webpage`, `curl` | _Unknown going in_ | _Unknown going in_ |
| **Workspace Context** | VS Code workspace present | _Isolated — no local workspace_ | VS Code workspace present |
| **Repeatability** | _Low_, model routing variance | _TBD_ | _Low_, inherited from Copilot baseline |
| **Questions** | _Does `fetch_webpage` have a consistent ceiling? Does it vary by agent?_ | _What tools does Codex expose? Does isolation from a workspace change retrieval behavior?_ | _Does Copilot's toolchain change when Codex is the underlying model? Does workspace context contaminate retrieval?_ |

## Track Design

| | **Track 1** | **Track 2** | **Track 3** | **Track 4** |
| - | ----------- | ----------- | ----------- | ----------- |
| **Surface** | Codex direct | Copilot extension (VS Code) | Codex direct | Copilot extension (VS Code) |
| **Method** | GPT-interpreted | GPT-interpreted | Raw, Python | Raw, Python |
| **Question** | _What does Codex report back in isolation? Does it accurately perceive truncation?_ | _What does Copilot report back with workspace context present? Does surface change self-perception?_ | _What does Codex's retrieval mechanism actually return verbatim? Where does truncation occur?_ | _Does Copilot's raw retrieval output differ from Codex's when surface context changes?_ |
| **Method Detail** | Fetch URL via Codex, report measurements; no workspace | Fetch URL via Copilot in VS Code, report measurements; workspace present | Fetch URL, return output verbatim; verification script extracts measurements | Fetch URL, return output verbatim; verification script extracts measurements; log workspace context per run |
| **Measurements** | Model estimates: _"appears truncated at ~X chars," "Markdown seems complete"_ | Same as Track 1; compared against Codex direct baseline | Character count via `len()`, token count via `tiktoken`, exact truncation point, last 50 characters | Same as Track 3; compared against Codex direct raw baseline |
| **Repeatability** | _TBD_ | _Low_, inherited from Copilot baseline | _TBD_ | _Low_, inherited from Copilot baseline |
| **Best For** | Understanding DX in isolated environment; surfacing **tool names** and invocation patterns | Understanding DX with workspace context; **does surface change agent self-perception?** | **Retrieval ceiling in isolation** — is there a consistent boundary without workspace interference? | **Surface-variant retrieval comparison** — does workspace context produce a measurably different raw output? |

> _**Limitations**: tool names and invocation conditions unknown going in; Copilot's `Auto` model routing may or may not select Codex consistently across runs, which will be logged; workspace context in VS Code tracks is a confound that cannot be fully controlled, but is treated as a variable of interest rather than noise._

---

## Codex-Specific Unknowns

| **Question** | **Details** | **Approach** | **Value** |
| ------------ | ----------- | ------------ | --------- |
| **Undocumented Retrieval Mechanism** | No web fetch tool named in Codex documentation; tool names, invocation conditions, and output format unknown going in | Observe any tool names reported in output per run; compare across surfaces | Establishes whether Codex exposes a consistent, nameable retrieval mechanism |
| **Surface-Driven Behavioral Divergence** | Codex direct operates without a local workspace; Copilot extension runs with VS Code workspace present; unknown whether this changes retrieval tool selection or ceiling | Compare raw track measurements across Track 3 and Track 4 | Determines whether surface context is a meaningful variable or a null finding — either outcome is documentable |
| **Model Routing Stability** | Copilot's `Auto` setting has historically selected non-Codex models; consistency of Codex selection across runs is not guaranteed | Log model per run in extension tracks; flag runs where Codex is not the selected model | Isolates whether findings are attributable to Codex specifically or to `Auto` routing variance |
| **Workspace Context Contamination** | Copilot autonomously substitutes local code execution when workspace scripts are present, observed in prior testing as `pylanceRunCodeSnippet` | Log all runs where substitution is attempted; remove framework scripts from workspace before extension track runs where possible | Determines whether workspace cleanup is required as a precondition for clean extension track runs |
