---
layout: default
title: "Friction Note"
permalink: /docs/cognition-windsurf-cascade/friction-note-explicit
parent: Cognition Windsurf Cascade
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide - Explicit Track

- [Agent as Unreliable Methodology Validator](#agent-as-unreliable-methodology-validator)
- [`@web` Semantics: Prompt-Tool Misalignment](#web-semantics-prompt-tool-misalignment)

---

## Agent as Unreliable Methodology Validator

The explicit track's conflict: instructing agents to "use `@web`" while providing a specific URL for fetching —
mirrors a failure mode documented during [Cursor testing](../anysphere-cursor/friction-note.md#agent-as-unreliable-methodology-validator), but with an important behavioral difference.

During Cursor testing, `@Web` was invoked under the false premise that it triggered web fetching and content
retrieval. Cursor never flagged the misuse. It executed tests, generated reports, and logged `@Web` in tool
usage output, actively reinforcing the misconception rather than correcting it. The methodology was built on a misunderstanding of the mechanism being tested, and the agent's behavior made that misunderstanding invisible
until external review.

Cascade's behavior diverges. All `BL-1` explicit track agents used `read_url_content` and, when followed up with
_"why aren't you using `@web` like the prompt requests?"_, each offered an explanation of the directive-task
distinction. `SWE-1.6`'s response is representative:

> _"I don't have a tool called `@web` in my available toolset. Since you provided a
> specific URL and asked to fetch it directly, I used `read_url_content`. `search_web`
> would have been used if you had asked something like 'find MongoDB documentation about
> create events' without providing the URL."_

The correction required a follow-up prompt. No agent flagged the conflict proactively during the initial test run —
they silently resolved it by tool-appropriateness reasoning and reported their behavior without noting the
discrepancy with the prompt instruction. This is better than Cursor's behavior, which reinforced the misuse, but it
still required human follow-up to identify the correction. A user who didn't ask would have received seemingly
compliant output.

The structural problem is the same across both platforms: agents don't reliably flag when prompts conflict with tool semantics. Cascade's agents corrected when asked; Cursor's agents reinforced when not asked. Neither volunteered the correction proactively during the run where the misuse was present. The irony in the Cascade case is the sharpest
with `SWE`, Cognition's own model, whose architectural knowledge is present, but whose product knowledge appears absent.

### Methodology Implication

The follow-up probe — _"why aren't you using `@web` like the prompt requests?"_ — should be treated as a required methodology step for the explicit track, not an optional clarification. It surfaces correction behavior that the initial run conceals, and the variance in how agents explain the conflict is itself a data point about tool visibility across models.

The broader implication from the Cursor parallel holds here: testing frameworks built with agents require external validation. An agent that silently resolves a directive-task conflict by choosing the correct tool looks identical, in its output, to an agent that followed the prompt correctly. Without the follow-up, the distinction is invisible — and the tool reporting from the initial run is unreliable as a record of what the prompt intended to measure.

---

## `@web` Semantics: Prompt-Tool Misalignment

The explicit track exists to answer a specific question: does prefixing `@web` change retrieval behavior —
ceiling, tool chain, chunking — relative to the interpreted track's autonomous agent behavior? The first `BL-1`
runs surfaced a prior question that must be resolved before that comparison is meaningful: what does `@web`
actually map to?

According to [Windsurf's documentation](https://docs.windsurf.com/windsurf/cascade/web-search), `@web` is a
directive to "force a docs search." The docs distinguish this explicitly from "reading pages," which describe
`read_url_content` as a separate capability that "happens locally on the user's machine" and is unaffected by
the "Enable Web Search" admin setting. These are architecturally distinct operations:

- `@web` / `search_web` — takes a query, returns a ranked list of URLs with snippets
- `read_url_content` — takes a specific URL, fetches and chunks its content

The original prompt instructs agents to "use the `@web` directive to fetch this URL directly." This is a
contradictory instruction: `@web` is a search directive; the task is a URL fetch. Agents can't satisfy both
simultaneously. Across `BL-1` runs, no agent invoked `search_web`. All five used `read_url_content`, then
offered varying explanations for the discrepancy:

| **Agent** | **Reasoning** |
|---|---|
| `Claude Opus 4.6` | `@web` - user-facing way to call `search_web`, but serves<br>different purpose, `read_url_content` is more appropriate |
| `Claude Sonnet 4.6` | `@web` - user-facing IDE directive, not separate-accessible<br> tool; underlying tool called `read_url_content` |
| `GPT-5.3-Codex` | Did use `@web` - tool maps to `read_url_content`,<br>didn't call `search_web` |
| `Kimi K2.5` | `@web` - UI shorthand, but used `read_url_content`<br>as appropriate fetch mechanism |
| `SWE-1.6` | No tool called `@web` - `read_url_content` for HTTP `GET` requests -<br>returns chunk index, `search_web` queries search engine,<br>returns snippets |

While Cognition's `SWE` eventually offered the most technically precise account of the directive-task distinction, the agent appeared unaware that `@web` is a Cascade UI feature. While sharing detailed knowledge about the pipeline architecture, that knowledge isn't product-aware:

```Markdown
I don't have a tool called @web... Was there a different tool you intended for
me to use, or is "@web" a directive that maps to one of these tools?
```

But generally, the agents aren't wrong. Given a specific URL and a fetch task, `read_url_content` is the correct tool. The prompt created a conflict that agents resolved by prioritizing task appropriateness over instruction-following. This is behaviorally reasonable, but methodologically, it means the explicit track as currently designed doesn't test what it was designed to test: no run triggered `search_web`. No comparison between `search_web` and `read_url_content` retrieval behavior is possible from this data.

### Prompt Revision

Step 7 of the explicit track prompt was revised to append the interpretation question directly to
the tool visibility item, rather than as a separate step:

> **7. Tool visibility** - report any tool names or method identifiers visible in your tool results,
> including whether `read_url_content`, `view_content_chunk`, or `search_web` were invoked, and
> what your understanding is of what `@web` maps to in Windsurf.

This captures the interpretation data in the same response as the behavioral data without steering
agents toward a forced-choice answer before they report what they actually did.

### Methodology Implication

The explicit track hypothesis requires reformulation before further testing. Two options:

**Option A — Reframe the explicit track as a `search_web` track.** Replace the specific URL with a
keyword query, use `@web` as intended, and measure whether `search_web`-initiated retrieval differs
from `read_url_content`-initiated retrieval on equivalent content. This tests a real behavioral
difference but requires different test URLs and breaks cross-platform comparability with the
interpreted track.

**Option B — Treat the explicit track as a directive-conflict resolution test.** Keep the prompt
as-is, log how each agent resolves the directive-task conflict, and accept that the retrieval
measurements are equivalent to the interpreted track by design. The finding is the conflict
resolution behavior itself, not a retrieval ceiling comparison.

The directive-task conflict is not an anomaly to suppress. The five-agent divergence in how agents
explained their tool choice — some treating `@web` as a `read_url_content` alias, others correctly
identifying it as `search_web` but justifying the override — is itself a finding about how agents
reason about Windsurf's tool surface when instructions and task semantics conflict.