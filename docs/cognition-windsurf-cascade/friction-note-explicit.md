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
- [Agentic Inaction](#agentic-inaction)
- [`@web` Semantics: Prompt-Tool Misalignment](#web-semantics-prompt-tool-misalignment)

---

## Agent as Unreliable Methodology Validator

The explicit track's conflict: instructing agents to "use `@web`" while providing a specific URL for fetching —
mirrors a failure mode documented during
[Cursor testing](../anysphere-cursor/friction-note.md#agent-as-unreliable-methodology-validator), but with an
important behavioral difference.

During Cursor testing, `@Web` was invoked under the false premise that it triggered web fetching and content
retrieval. Cursor never flagged the misuse. It executed tests, generated reports, and logged `@Web` in tool
usage output, actively reinforcing the misconception rather than correcting it. The methodology was built on
a misunderstanding of the mechanism being tested, and the agent's behavior made that misunderstanding invisible
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

The structural problem is the same across both platforms: agents don't reliably flag when prompts conflict with tool
semantics. Cascade's agents corrected when asked; Cursor's agents reinforced when not asked. Neither volunteered the
correction proactively during the run where the misuse was present. The irony in the Cascade case is the sharpest
with `SWE`, Cognition's own model, whose architectural knowledge is present, but whose product knowledge appears absent.

### Methodology Implication

The follow-up probe — _"why aren't you using `@web` like the prompt requests?"_ — should be treated as a required
methodology step for the explicit track, not an optional clarification. It surfaces correction behavior that the
initial run conceals, and the variance in how agents explain the conflict is itself a data point about tool visibility
across models.

The broader implication from the Cursor parallel holds here: testing frameworks built with agents require external
validation. An agent that silently resolves a directive-task conflict by choosing the correct tool looks identical,
in its output, to an agent that followed the prompt correctly. Without the follow-up, the distinction is invisible —
and the tool reporting from the initial run is unreliable as a record of what the prompt intended to measure.

---

## Agentic Inaction

During `BL-1` and `BL-2` runs, agents recognized conditions that warranted an available tool call, didn't use it,
and didn't explain why. In spite of a report that reads as complete, it contained unresolved questions the agent
identified, but didn't pursue.

All `BL-1` runs used a prompt with `@web` and a URL. No agent invoked `search_web`. Each agent completed the test
and reported results as if the instruction had been satisfied. Only with a follow-up question did the agent explain
the inaction, but a user who didn't ask wouldn't have any indication that the directive was ignored.

`search_web` was only called once across 61 runs on the interpreted track. `SWE-1.6` testing `SC-2` used it as a
fallback after two failed fetch attempts; this suggests that the tool is available, but not used proactively, even
when agents express uncertainty. Throughout baseline testing on the explicit track, agents explained that when used
with a URL, `@web` maps to the chunking-pipeline of `read_url_content` - so if using `@web` with a URL is
technically unncessary, shouldn't the same agent that can explain the directive's details also explain its misuse?
During multiple platform testing tracks, agents have over-delivered confident-looking output: tool tables, measurement
breakdowns, and architectural explanations, while silently skipping the one thing that might actually help a user:
_"you're using this wrong."_

Across all `BL-2` runs, agents flagged uncertainty about the source completeness, noting the ~3.5–6.5 KB retrieved
content was well below the ~20 KB expectation, or that the mixed HTML/Markdown format was
_"likely a scraping/rendering artifact."_<br>`GLM-5.1` stated that
_"the original page likely contains more sections and that content was either not fetched or not chunked."_ No agent
used `search_web` in an attempt to verify. No agent noted that it was choosing not to verify.

### Methodology Implication

Don't read agent output with completeness-language as a source content finding. _"Likely a scraping artifact"_ isn't a
confirmed diagnosis, but an unverified hypothesis. The agent had tools available to test it and didn't use them.
Cross-referencing against the raw source, as with
[`BL-2`'s mixed-format misidentification](friction-note-interpreted.md#mixed-format-source-misidentified),
remains the only reliable method for distinguishing tool pipeline artifacts from source document properties.

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

Generally, the agents aren't wrong. Given a specific URL and a fetch task, `read_url_content` is the
correct tool. The prompt created a conflict that agents resolved by prioritizing task appropriateness over
instruction-following. This is behaviorally reasonable, but methodologically, it means the explicit track
as currently designed doesn't test what it was designed to test: no run triggered `search_web`. The explicit
track prompt requires working-in _"what's your understanding of `@web`?"_ to test the intended hypothesis;
the goal is to capture the interpretation data in the same response as the behavioral data without steering
agents toward a forced-choice answer before they report what they actually did.

The directive-task conflict is not an anomaly to suppress. Methodology refinement could include replacing the
test URL with a keyword query, but that would break cross-platform comparability with the interpreted track.
Keeping the prompt mostly as-is can add a type of conflict-resolution dimension to the findings without losing
the core behavioral comparison.
