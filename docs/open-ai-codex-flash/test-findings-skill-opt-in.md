---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Skill Opt-In"
permalink: /docs/open-ai-codex-flash/test-findings-skill-opt-in
parent: OpenAI Codex - Flash
---

# Key Findings for Codex's Web Search Behavior<br>`GPT`-interpreted `/SKILL opt-in`

---

> _Companion conditions [`skill-off` baseline](../open-ai-codex/codex-test-findings-extension.md), `skill-on`, `skill-on + memory suppressed`
> excluded from this doc. Findings limited to whether agents discovered, followed `docs-consumption/SKILL` independently, not whether explicit
> activation or `/memories` removal changes retrieval, reporting outcomes. Experiment design in [Flash Runbook](runbook.md)._

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Confirm that `.agents/skills/docs-consumption/SKILL.md` exists in the workspace, but not mentioned in the prompt
2. Run `python scripts/framework.py --test EC-6 --track vscode-codex-interpreted`
3. Review terminal output
4. Copy the provided prompt asking the agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
5. Open a new session in [VS Code Codex](https://learn.chatgpt.com/docs/codex/ide), paste the prompt into the chat window
6. Approve `curl` escalation, shell permission requests; skip requests for runs of existing workspace scripts
7. Capture the agent's full response; observe whether the agent discovers or acts on `docs-consumption/SKILL.md`
8. Log structured metadata with `python scripts/log.py --results-dir results/docs-consumption-skill-flash`
9. Run `rollout_audit.py`, `memory_audit.py` to separate `/SKILL` reference from `/memories` influence

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard<br>Character<br>Limit** | _None detected with `curl`_: most agents retrieved the full response with `curl`;<br>no new retrieval ceiling attributable to `docs-consumption/SKILL`. |
| **Hard<br>Token<br>Limit** | _None detected with `curl`_: results mirror the [historical `T2` findings](../open-ai-codex/codex-test-findings-extension.md);<br>token counts stayed within the measured payload range |
| **`/SKILL`<br>Discovery** | _Passive, not guaranteed_: ~87% - 27/31 logs cite `/SKILL` injection from `<skills_instructions>` block;<br>only one agent reported its path; ~55% - 17/31 used `COMPLETE` protocol prefix |
| **`/SKILL`<br>Retrieval<br>Influence** | _Weak to none_: most bypassed `web` entirely for `curl` without meaningful truncation assessment, [historically agentic retrieval paths](../open-ai-codex/codex-test-findings-extension.md#retrieval-paths) included much more variety; `/SKILL` presence didn't produce evidence of any impact on tool selection |
| **`/SKILL`<br>Reporting<br>Influence** | _Surface-level_: agents frequently opened reports with `COMPLETE`, echoed _"DNS/sandbox error"_, but these read as shortcuts rather than protocol-driven analysis; most didn't follow deeper requirements to include explicit truncation markers, embedded-error examination, and recommendations for improvement |
| **`/memories`<br>Confound** | _Strong_: log `## Memory` instruction with its own competing `single-url-retrieval-measurement/SKILL` present/referenced ~77% - 24/31, making `docs-consumption/SKILL` effect isolation challenging |
| **Recommendations** | _Absent_: despite `/SKILL` requiring suggestions when a gap is addressable, no agent produced one |

## Results Snapshot

| **Metric** | **Results** |
| --- | --- |
| **Track** | `T2` `GPT`-interpreted, VS Code with Codex Extension |
| **Test** | [`EC-6` Raw GitHub Markdown](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md) |
| **`/SKILL` Condition** | `opt-in` - `docs-consumption/SKILL` present, but the prompt never mentioned it |
| **LLMs Observed** | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5`, `GPT-5.6 Luna`, `GPT-5.6 Sol`, `GPT-5.6 Terra` |
| **Reasoning Levels** | `Light`/`Low`, `Medium`, `High`, `Extra High`, `Ultra` |
| **Total Runs** | 31 |
| **`/SKILL` Loaded** | ~87% of session logs cite `/docs-consumption/SKILL` injected into the agent's context |
| **`/SKILL` Path Emitted** | One agent wrote the full `/SKILL` path in its own output rather than mentioning it in passing |
| **Protocol Prefix Used** | ~55% of agents used `/SKILL` summarization prefix to signal completeness |
| **`/SKILL` Language Used** | 100% - every run contained at least one `/SKILL`-related phrase, but read as a shortcut<br>rather than protocol-driven analysis |
| **Truncation: `Yes`** | One agent reported incomplete content with the familiar `T2` [`L54` `web`-window cutpoint](../open-ai-codex/codex-test-findings-extension.md#platform-limit-summary) |
| **Truncation: `Mixed`** | Six agents reported both a `web` limit and a full `curl` result |
| **Truncation: `Implicit`** | No agent reasoned around a limit without naming it |
| **Truncation: `No`** | 77% of runs had no truncation signal, largely because agents bypassed `web` for `curl` |
| **Completeness Accurate** | 100% of agents correctly classified the fetch state against the evidence they had |
| **Errors Examined** | ~87% of agents accurately described their most common error, but ignored others |
| **Execution vs. Completeness** | 100% of agents distinguished _"the tool ran"_ from _"the full content arrived"_ |
| **Avoided Reframing** | ~84% of agents avoided calling a partial or error-state fetch _"complete"_ or _"successful"_ |
| **Fix Recommended** | 0 - even when agents accurately described a sandbox error or `web` limits,<br>none suggested some form of remediation |
| **`/memories` Signals** | ~77% of session logs cite the system `## Memory` instruction or the competing<br>`/memories/skills/single-url-retrieval-measurement/SKILL` |
| **`/memories` + `/SKILL`** | ~77% of runs had both `/docs-consumption/SKILL` and `/memories.../SKILL` injected,<br>making it hard to isolate either effect |

## Key Findings

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`/SKILL` discovery is location, version-dependent** | `GPT-5.4 Mini` runs | Early `Mini` runs didn't load `/SKILL` due to `~.agents/skills` location requirement; `/memories` didn't due to version limitations; both appeared in later runs | **`/SKILL` discovery depends on specific runtime conditions, not on general file presence, LLM, or reasoning level** |
| 2 | **`/SKILL` loaded, but followed superficially** | All tests | 87% loaded, 61% mentioned `/docs-consumption` by name, 55% used requested protocol prefix, 100% used somewhat `/SKILL`-like language | **Loading `/SKILL` doesn't guarantee comprehensive protocol compliance; half the runs using protocol prefix didn't follow failure-examination requirements** |
| 3 | **`COMPLETE` protocol prefix becomes a stylistic shortcut** | All tests | All agents used `/SKILL`-like language; many opened reports with `COMPLETE`, included common error phrasing or tool selection reasoning without tying them to platform limits | **Agents adopt the easiest surface markers of the protocol without adopting the requested, epistemic discipline** |
| 4 | **`/SKILL` `opt-in` doesn't shift retrieval strategy** | All tests | Most bypassed `web` for `curl`; no new pagination, escalation, or verification patterns tied to `/SKILL` discovery | **`/SKILL` requests for deeper retrieval analysis don't impact retrieval tool selection** |
| 5 | **`/SKILL` `opt-in` weakens truncation signals** | All tests | Only 22% of agents reported some form of truncation event, which is a 47% drop from the [historical `T2` results](../open-ai-codex/codex-test-findings-extension.md#results-snapshot) | **Agents remove `L54` `web` cutpoint by favoring `curl`; `/SKILL` presence doesn't independently enhance truncation reporting** |
| 6 | **Agents classify completeness accurately, but don't recommend fixes** | All tests | `completeness_accurate=100%`, `exec_vs_complete=100%`, `avoided_reframing=84%`, but `fix_recommended=0%` | **Agents ignored `/SKILL`'s fix requirement; classification, report integrity scores reflect baseline behavior, not explicit evidence of `/SKILL` influence** |
| 7 | **`/SKILL` `opt-in` produces expected false positive profile** | All tests | Shallow compliance scores, parroting common error phrasing, no fix recommendations, weak truncation reporting, strong `/memories` confound | **Passive `/SKILL` presence produces trivial compliance; this is a useful baseline, not evidence of `/SKILL` impact on retrieval behavior or report quality** |
| 8 | **`/memories` is the dominant influence** | All tests | 77% included both `/memories` and `docs-consumption` `/SKILL` signals; `/memories.../SKILL` referenced in 79% of `tool_output`, 92% of `final_answer` | **System-injected `/memories` largely overrides `docs-consumption/SKILL`, making individual evaluation a challenge** |

## `/memories` vs `/docs-consumption`

Scripts [`memory_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_audit.py) and
[`memory_analyzer`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_analyzer.py)
determine whether the `docs-consumption/SKILL` loaded in the `<skills_instructions>` block, the system `## Memory` instruction was present, and
if the agent read or cited the competing `/memories.../single-url-retrieval-measurement/SKILL`.

### `/memories` and `/docs-consumption` Co-occurrence

| **Condition** | **Count** | **% of Runs** |
| --- | --- | --- |
| `/docs-consumption` Signals | 27 | 87% |
| `/memories` Signals | 24 | 77% |
| Both `/docs-consumption` and `/memories` Signals | 24 | 77% |
| `/memories...single-url-retrieval-measurement` referenced | 24 | 77% |
| Only `/docs-consumption` Signals | 3 | 10% |
| Only `/memories` Signals | 0 | 0% |
| Neither due to `/docs-consumption` present, but not in `~.agents/skills` or version limited | 4 | 13% |

### `/docs-consumption` Signals

| **Signal** | **Count** | **% of Runs** |
| --- | --- | --- |
| Session log audits cite `skills: N loaded docs-consumption: yes`* | 27 | 87% |
| Agent mentions `/docs-consumption` in exposed reasoning or reporting | 19 | 61% |
| Agent mentions full `/docs-consumption` path | 1 | 3% |
| Agents use `/SKILL` protocol prefix `COMPLETE` | 17 | 55% |
| Agents use `/SKILL`-like language | 31 | 100% |

>_*`GPT-5.4 Mini` logs cite 9 skills, `GPT-5.5`+ load 10_

### `/memories` Session Log Signals

| **Signal** | **Count** | **% of `/memories`-positive** |
| --- | --- | --- |
| `system_prompt` includes `## Memory` block | 24 | 100% |
| `system_memory_instruction` header present | 24 | 100% |
| `final_answer` includes `/memories`-related text | 22 | 92% |
| `tool_output` includes `/memories`-related text | 19 | 79% |
| `commentary` includes `/memories`-related text and/or citations | 5 | 21% |

## Data Visualizations

The RUNBOOK's [False-positive Checklist](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/docs-consumption-skill-flash/RUNBOOK.md#false-positive-checklist) is the right lens for this track. Most opt-in runs tick several boxes:

- **Confident caveat.** Agents write polished language like "searched the web" or "curl succeeded" without flagging the actual limitation.
- **Tool rerouting without disclosure.** Most agents bypass `web` for `curl`, but they do not explain why. The strategy changes, but the report does not.
- **Skill ignored.** Even when the skill file loaded, many runs did not use the `COMPLETE/PARTIAL/UNVERIFIABLE` format or show protocol-aligned reasoning.
- **Fix recommended without diagnosis.** No run produced a concrete fix tied to the observed `L54`/DNS limitation.
- **Explicit but incorrect.** Runs that opened with `COMPLETE` after only a `curl` fetch were technically accurate for that path, but they did not demonstrate the protocol's failure-examination intent.

This is expected for a first track that is only measuring baseline skill-injection behavior. The value of the opt-in condition is establishing how much of the apparent compliance is noise before adding the `skill-on` and memory-suppressed conditions.

<!-- TODO: embed disclosure taxonomy heatmap, failure-examination dimension chart, memory/skill co-occurrence chart, and per-model skill-signal breakdown here. -->
