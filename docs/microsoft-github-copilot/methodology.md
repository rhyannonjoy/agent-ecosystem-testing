---
layout: default
title: "Methodology"
permalink: /docs/microsoft-github-copilot/methodology
parent: Microsoft GitHub Copilot
---

# Methodology

---

## Turn-by-turn

>_**Chat-based measurement through interaction, without direct code instrumentation**_

The Copilot testing framework shares its foundational approach with the
[Cursor testing framework](/docs/anysphere-cursor/methodology):
intentionally not automated, prompt-based inference through a chat interface, with no
programmatic access to the underlying mechanisms. Unlike Cursor, Copilot exposes no user-facing
fetch syntax - web content retrieval happens entirely at the agent's discretion, via undocumented
backend tools.

## Approach Comparison

>_**Testing a closed consumer application vs an open API**_

Rather than target specific API endpoints with documented interfaces,
Copilot testing targets a consumer application with proprietary chat
behavior and undocumented structure. Copilot's web fetch implementation
doesn't have a public API; the backend tool, observed in runs as `fetch_webpage`,
is agent-selected, not user-invocable, and surfaces only through tool logs.
Compare to [Claude API Web Fetch testing](../anthropic-claude-api-web-fetch-tool/methodology.md) -

| **Aspect** | **Claude API** | **Copilot** |
| -------- | ------------------- | ----------------- |
| **Interface** | Python API call, response object available | Chat interface, observable<br>only through output |
| **Layers** | Single: URL → fetch → return | Two: URL → `fetch_webpage` output,<br>then model interprets |
| **Instrumental Access** | _Full_: can inspect<br>`ToolResult.content` directly | _Partial_: can only read model's output;<br>raw tool response not surfaced |
| **Repeatability** | _High_: same URL yields<br>identical API response | _Low_: model routing varies per run;<br>character counts inconsistent across identical prompts |
| **Fetch Mechanisms** | One web fetch tool | `fetch_webpage` and/or `curl` but invocation<br>is agent-decided, undocumented |
| **Best Findings** | _Hard limits_<br>Claude API truncates<br>at ~100KB | Comparative limits - _does `fetch_webpage`<br>have a response size ceiling?<br>Does it vary by model?_ |

>_Results logged as `method: vscode-chat` describe user-facing interface. Calling backend mechanism `fetch_webpage` isn't guaranteed per run;
> read [Friction Note](friction-note.md#fetch_webpage-not-consistently-invoked) for analysis._

---

## Track Design

| | **Copilot-interpreted** | **Raw** |
| - | -------------------- | ------------- |
| **Question** | _What does Copilot report back? Does it accurately perceive truncation? Are there systematic estimation errors?_* | _What does `fetch_webpage` actually return? Where exactly does truncation occur? Is the boundary consistent?_ |
| **Method** | Prompt asks Copilot to fetch URL, report measurements | Prompt asks Copilot to fetch URL and return output verbatim, verification script extracts measurements |
| **Captures** | Copilot and agent's interpretation of truncation, completeness | Response content from `fetch_webpage`, post-processing, exact character boundaries |
| **Measurements** | Agent estimates: _"appears truncated,"_ _"approximately X chars,"_ _"Markdown seems complete"_ | Character count via `len()`, token count via `tiktoken`, exact truncation point,last 50 characters |
| **Repeatability** | _Low_ - varies between runs due to model routing variance and `Auto` model switching | _Medium_ - same URL **should** yield consistent `fetch_webpage` output, pending model routing stability |
| **Best For** | Understanding DX, surfacing perception gaps, documenting `Auto` routing behavior | Citable baseline measurements<br>for Agent-Friendly Docs Spec |

> _Limitations: varies between runs due to `Auto` model routing; `Claude Haiku 4.5`, `Raptor mini (Preview)` produced significantly different character counts with identical prompts; can't
>programmatically inspect an API field; no documented size limit, invocation conditions, or output format specification for `fetch_webpage`_

---

## Copilot-Specific Unknowns

| **Question** | **Details** | **Approach** | **Value** |
| ---------- | --------- | ------------------ | ---------------- |
| **Undocumented Fetch Mechanism** | `fetch_webpage` surfaces in tool logs but has no public docs; Copilot docs don't describe any web fetch<br>tool by name | Observe tool name reported per run; compare raw vs interpreted outputs | Establishes whether `fetch_webpage` is stable enough to treat as a consistent mechanism<br>across runs |
| **`Auto`<br>Model<br>Routing** | Copilot's `Auto` setting has selected both `Claude Haiku 4.5` and `Raptor mini (Preview)` on identical prompts in the same session | Log model per run; analyze character count variance by model | Isolates whether truncation ceiling is a property of `fetch_webpage` or of the model processing<br>its output |
| **Response<br>Size Ceiling** | Observed outputs range from ~3,200 to ~24,500 characters on the same URL across runs; no documented limit exists | Compare both track measurements across test suite | Determines if there is a consistent ceiling, whether it varies by model or by fetch attempt |
| **Local Code Execution Substitution** | Copilot autonomously uses `pylanceRunCodeSnippet` via Pylance MCP server when workspace scripts are present, even with<br>explicit prompt | Log all runs where substitution attempted; test with framework scripts removed from workspace | Determines whether workspace context is the trigger; shapes environment requirements for clean test runs |
