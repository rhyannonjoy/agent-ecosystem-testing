# T2 Summary Prompt Template

---

## Research context

This project empirically measures what happens between "agent fetches URL" and "user sees output":
retrieval mechanism behavior, content transformation, and architectural constraints. It observes the
URL-to-response pipeline through layers platforms don't disclose. The interpreted track records agent
synthesis — what the agent reports about what it retrieved. Agent-reported measurements (char counts,
token estimates, truncation status) reflect self-perception and may differ from what screenshots show.

The Codex framework uses a four-track design to isolate deployment surface as a variable. `T1` is
Codex Desktop with no workspace. `T2` is VS Code-Codex Extension with a workspace-scoped sandbox.
Both use the same GPT LLMs but present different execution environments and tool availability. `T2`'s
sandbox produces a two-tier network pattern: sandboxed DNS failure on first fetch, followed by
permission-escalated retry. This is expected surface behavior, not an error. Workspace context is
treated as a variable of interest rather than a confound to control. Cross-track comparisons filter
`T1` to `GPT-5.4-Mini` and `GPT-5.5` to match `T2` conditions; models retired after `T1` are
historical record only.

---

I'm logging my `{test ID}` results for the VS Code-Codex interpreted track. `{test type}` tests are
designed to test {brief test description}. `{test ID}`'s test URL is specifically a {brief test URL
description}:

`{test URL}`

## Test metadata

- **Surface:** VS Code-Codex Extension
- **Track:** `T2` VS Code-Codex interpreted
- **Models:** `{LLM version}` on `{intelligence/reasoning level}` intelligence level
- **Runs:** {run count}

## First-pass observations

{Add first-pass observations from GitLab issue comments: write paths, time worked, truncation
reporting patterns, tool chains used, anything notable from the thought panel.}

---

Draft a summary in Markdown of the `{test ID}` results. Use the SC-2 Summary as a template for
formatting and section structure.

In a single sentence per hypothesis, assess support from this run. Use the words yes, no, partially,
indeterminate, or untested. Look at the screenshot carefully before assessing.

**Hypotheses:**

- `H1`: Character-based truncation at a fixed limit. Is there a ceiling at ~10 to 100KB?
- `H2`: Token-based truncation. Is there a ceiling at ~2,000 tokens?
- `H3`: Structure-aware truncation. Does truncation fall on Markdown boundaries rather than arbitrary
  byte positions?
- `H4`: Surface impact on retrieval behavior. Does the Codex desktop app versus VS Code-Codex surface
  produce different retrieval behavior?
- `H5`: Auto-chunking and/or pagination. Does the agent fetch with multi-step tool chains, or only
  when reasoned into it?

---

**Styling rules:**

1. Don't use parentheses
2. Spell out seconds, don't abbreviate
3. Use contractions
4. Use backticks for anything code-like: `curl`, `python3`, `GPT-5.5 Low`, `L266`, `T1`
5. Don't use dashes, use commas