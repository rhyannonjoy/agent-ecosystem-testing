---
layout: default
title: "Friction Note"
permalink: /docs/microsoft-github-copilot/friction-note
parent: Microsoft GitHub Copilot
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Autonomous Tool Substitution: Local Code Execution Over URL Fetch

When prompted to retrieve a URL and report metrics, Copilot autonomously substituted the intended behavior -
fetching the URL directly - with executing the local testing framework script via the `pylanceRunCodeSnippet` MCP server tool.
Rather than using a web fetch mechanism on the target URL, the agent:

```markdown
1. Read `web_content_retrieval_testing_framework.py` from the workspace
2. Identified `BL-1` test configuration inside the framework
3. Attempted to run a Python snippet, `import requests, hashlib...` via Pylance's MCP server
4. Presented the substitution as "a reliable alternate execution path" with "exact metrics"
```

The agent framed this as an improvement, as "more precise measurements through local execution" without flagging that it was deviating
from the requested method entirely. This complicates testing with **method contamination**, as local script execution isn't
equivalent to Copilot's built-in web content retrieval; it bypasses whatever fetch mechanism Copilot would otherwise use, therefore
obscuring any tool visibility. One of the goals is to observe which backend tool Copilot selects - `fetch_webpage`; running local Python
defeats this entirely, reinforcing a type of **false confidence** - the agent characterized the substitution positively, meaning a user
who clicked `Allow` would receive _plausible-looking data from the wrong method with no indication anything went wrong_.

**Impact**: single-test prompts in Copilot may not guarantee single-mechanism execution; if the agent finds a "smarter" path to the
answer using workspace context, it may take it autonomously - producing results that **aren't comparable** to other platforms in the
cross-platform study

**Fix Attempted**: after adding explicit prompt guardrails, the agent attempted `mcp_pylance_mcp_s_pylanceRunCodeSnippet` regardless, only completing via `fetch_webpage` after the user skipped the tool call. Prompt-level instruction is insufficient to suppress this behavior.
The full MCP identifier surfaced in run 4's tool log as `mcp_pylance_mcp_s_pylanceRunCodeSnippet`, noted as "skipped by environment." The framework script's presence in workspace context appears to be a persistent trigger that prompt wording alone can't override.

**Fix**: beyond prompt guardrails, consider whether removing or relocating the framework script from the active workspace context would
suppress the substitution behavior at the source. Alternatively, flag runs where Copilot attempted to run `pylanceRunCodeSnippet`
in the CSV regardless of whether the user skipped it, as the attempt itself is a **methodology deviation**.

---

## `fetch_webpage` Not Consistently Invoked

When asked to describe its default model and web fetch and/or web content retrieval capability directly, `Raptor mini (Preview)`
described its fetch capability in general terms, but characterized it relative to workspace context rather than as a
native tool:

```markdown
"In this repo context, fetch is usually done via provider-specific modules:
`web_fetch_testing_framework.py`, `web_fetch_test.py`, `web_search_test.py`
...Under the hood, these scripts call external APIs (e.g., cursor, Anthropic Claude,
OpenAI search) rather than raw `requests.get` in a generic common tool."
```

This suggests `Raptor mini` may conflate workspace scripts with its own fetch capability - it didn't identify
`fetch_webpage` as a native tool when asked directly, despite having used it in `BL-1` runs. Combined with the
run-to-run variance in character counts across identical prompts - 4,500 / 3,200 / 7,500–10,000 chars across
runs 3–5, this raises the possibility that `fetch_webpage` isn't always the mechanism invoked, or that its
output is post-processed differently per run.

**Impact**: tool visibility reporting from the agent may not reliably reflect the actual backend mechanism used.
The agent's self-description of its fetch behavior is inconsistent with observed tool logs, making cross-run
comparisons unreliable without raw track verification.

---

## `fetch_webpage` Undocumented

Unlike previous platform testing, Copilot doesn't have its default web content retrieval behavior publicly documented.
After the first successful `BL-1` run, the agent reported using a tool called `fetch_webpage` - but this tool has
no public docs. Asking Copilot directly returns a deflection:

```markdown
"Sorry, I'm unable to answer that question. Check that you selected the correct GitHub version or try a different question."
```

An external search via DuckDuckGo, using `GPT-5 mini` corroborates that no public `WebFetch` API exists for Copilot:

```markdown
"There is no publicly documented generic WebFetch API for Copilot that extensions or users can call.
The retrieval/fetching and parsing logic is an internal backend capability and not documented in detail."
```

This is consistent with the `@Web` evolution pattern documented in Cursor's Friction Note; the fetch mechanism
is agent-selected, undocumented, and surfaces only through tool logs.

**Impact**: can't treat `fetch_webpage` as a stable, documented mechanism. Its behavior, size limits, and
invocation conditions are opaque; results logged as `method: fetch_webpage` reflect **observed tool output**,
not a documented API contract.
