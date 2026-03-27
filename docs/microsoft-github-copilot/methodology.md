---
layout: default
title: "Methodology"
permalink: /docs/microsoft-github-copilot/methodology
parent: Microsoft GitHub Copilot
---

## Methodology

---

_**Chat-based measurement through interaction, without direct code instrumentation**_

> _The Copilot testing framework shares its foundational approach with [the Cursor testing framework](/docs/anysphere-cursor/methodology):
> intentionally not automated, prompt-based inference through a chat interface, with no
> programmatic access to the underlying mechanisms. Unlike Cursor, Copilot exposes no user-facing fetch syntax -
> web content retrieval happens entirely at the agent's discretion, via undocumented backend tools._

---

_**Testing a closed consumer application vs an open API**_

Rather than target specific API endpoints with documented interfaces,
Copilot testing targets a consumer application with proprietary chat
behavior and undocumented structure. Copilot's web fetch implementation
doesn't have a public API; the backend tool, observed in runs as `fetch_webpage`,
is agent-selected, not user-invocable, and surfaces only through tool logs.
Compare to [Claude API Web Fetch testing](/docs/anthropic-claude-api-web-fetch-tool/methodology) -

| **Aspect** | **Claude API Testing** | **Copilot Testing** |
| -------- | ------------------- | ----------------- |
| **Interface** | Python API call, response object available | Chat interface, observable only through output |
| **Layers** | Single: URL → fetch → return | Two: URL → `fetch_webpage` output, then model interprets |
| **Instrumental Access** | Full: can inspect `ToolResult.content` directly | Partial: can only read model's output; raw tool response not surfaced |
| **Repeatability** | High: same URL yields identical API response | Low: model routing varies per run; character counts inconsistent across identical prompts |
| **Fetch Mechanisms** | One web fetch tool | One observed - `fetch_webpage`, but invocation is agent-decided and undocumented |
| **Best Findings** | Hard limits - Claude API truncates at ~100KB | Comparative limits - _does `fetch_webpage` have a response size ceiling? Does it vary by model?_ |

>_All results logged as `method: vscode-chat` reflect the user-facing interface
used in prompts. Identified through agent output, invocation of the backend mechanism `fetch_webpage` isn't guaranteed per run;
read [Friction Note](friction-note.md#fetch_webpage-not-consistently-invoked) for analysis._

---

**Goal**: use GitHub Copilot in VS Code with two complementary tracks -
the interpreted track catches perception gaps, while the raw track
produces reproducible numbers for documentation -

| | **Copilot-interpreted Track** | **Raw Track** |
| - | -------------------- | ------------- |
| **Question** | _What does Copilot report back? Does it accurately perceive truncation? Are there systematic estimation errors?* | *What actually came back from `fetch_webpage`? Where exactly does truncation occur? Is the boundary consistent?_ |
| **Method** | Chat prompt asks Copilot to fetch URL and report measurements | Chat prompt asks Copilot to fetch URL and return output verbatim, human manually extracts measurements |
| **Captures** | Copilot's, and the underlying model's, interpretation of truncation and completeness | Actual response content from `fetch_webpage`, post-processing, exact character boundaries |
| **Measurements** | Model estimates: "appears truncated," "approximately X chars," "markdown seems complete" | Manual: character count via `len()`, token count via `tiktoken`, exact truncation point, last 50 characters |
| **Repeatability** | Low - varies between runs due to model routing variance and Auto model switching | Medium - same URL should yield consistent `fetch_webpage` output, pending model routing stability |
| **Best For** | Understanding DX, surfacing perception gaps, documenting Auto routing behavior | Citable baseline measurements for the Agent Docs Spec |

> _Known limitations of this approach: interpreted-track varies between runs due to
> Auto model routing - `Claude Haiku 4.5` and `Raptor mini (Preview)` observed on
> identical prompts, producing significantly different character counts; can't programmatically
> inspect a surfaced API field; `fetch_webpage` has no documented size limit, invocation
> conditions, or output format specification_

### Copilot-Specific Unknowns

| **Question** | **Details** | **Approach** | **Value** |
| ---------- | --------- | ------------------ | ---------------- |
| **Undocumented Fetch Mechanism** | `fetch_webpage` surfaces in tool logs but has no public docs; GitHub Copilot docs don't describe any web fetch tool by name | Observe tool name reported per run; compare raw vs interpreted outputs | Establishes whether `fetch_webpage` is stable enough to treat as a consistent mechanism across runs |
| **Auto Model Routing** | Copilot's `Auto` setting has selected both `Claude Haiku 4.5` and `Raptor mini (Preview)` on identical prompts in the same session | Log model per run; analyze character count variance by model | Isolates whether truncation ceiling is a property of `fetch_webpage` or of the model processing its output |
| **Response Size Ceiling** | Observed outputs range from ~3,200 to ~24,500 characters on the same URL across runs; no documented limit exists | Compare interpreted and raw track measurements across `BL`, `SC`, and `OP` tests | Determines if there is a consistent ceiling, and whether it varies by model or by fetch attempt |
| **Local Code Execution Substitution** | Copilot autonomously attempts `pylanceRunCodeSnippet` via Pylance MCP server when workspace scripts are present, even when explicitly asked not to | Log all runs where substitution attempted; test with framework scripts removed from workspace | Determines whether workspace context is the trigger; shapes environment requirements for clean test runs |
