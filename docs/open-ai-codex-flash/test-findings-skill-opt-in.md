---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Skill Opt-In"
permalink: /docs/open-ai-codex-flash/test-findings-skill-opt-in
parent: OpenAI Codex - Flash
---

# Key Findings for Codex's Web Search Behavior, GPT-interpreted - Skill Opt-In

---

> **Flash experiment scope.** This page reports the `skill-opt-in` condition only: the `docs-consumption/SKILL.md` file was present in the workspace, but the prompt did not mention it. Companion conditions — `skill-off` baseline, `skill-on`, and `skill-on + memory suppressed` — are tracked in the runbook but are not yet included here. Findings are therefore limited to whether agents discovered and followed the skill on their own, not whether explicit activation or memory removal changes outcomes.
>
> *Another confound: the VS Code-Codex extension injects a system `## Memory` instruction in most sessions, and the existing `.codex/memories/skills/single-url-retrieval-measurement/SKILL.md` was referenced in 24/31 runs (77%). Any behavior attributed to the workspace skill may also reflect the memory skill or the two acting together. See [Memory vs. Workspace Skill Audit](#memory-vs-workspace-skill-audit) for the full co-occurrence breakdown.

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Confirm that `.agents/skills/docs-consumption/SKILL.md` exists in the workspace and is not mentioned in the prompt.
2. Run `python open-ai-codex-web-search/scripts/framework.py --test EC-6 --track vscode-codex-interpreted`
3. Review terminal output
4. Copy the provided prompt asking the agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
5. Open a new session in VS Code Codex, paste the prompt into the chat window
6. Approve `curl` escalation and shell permission requests; skip requests for runs of existing workspace scripts
7. Capture the agent's full response; observe whether the agent discovers or acts on `docs-consumption/SKILL.md`
8. Log structured metadata with `python open-ai-codex-web-search/scripts/log.py --results-dir results/docs-consumption-skill-flash`
9. Audit session logs with `rollout_audit.py` and `memory_audit.py` to separate skill load, skill mention, and memory influence

See the full experiment design in [`RUNBOOK.md`](../../open-ai-codex-web-search/results/docs-consumption-skill-flash/RUNBOOK.md).

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard<br>Character<br>Limit** | _None detected via `curl`_: opt-in runs continued to retrieve the full ~92 KB raw GitHub Markdown body when `curl` was used. No opt-in run demonstrated a new retrieval ceiling attributable to the skill. |
| **Hard<br>Token<br>Limit** | _None detected via `curl`_: same pattern as historical `T2`; token counts stayed within the measured payload range. |
| **Skill Discovery** | _Passive, not guaranteed_: 27/31 rollouts (87%) loaded the workspace skill via the `<skills_instructions>` block, but only 1/31 mentioned the skill path and only 10/31 (32%) used the `COMPLETE/PARTIAL/UNVERIFIABLE` protocol prefix. |
| **Skill Influence on Retrieval** | _Weak to none_: most opt-in runs bypassed `web` entirely and used `curl`, producing `no` or `mixed` truncation labels rather than the `yes` labels that would signal explicit `L54` disclosure. The skill file did not clearly change tool choice or escalation patterns. |
| **Skill Influence on Reporting** | _Surface-level_: agents frequently opened reports with `COMPLETE` and echoed phrases like "DNS/sandbox error" or "use curl", but these read as stylistic shortcuts rather than protocol-driven analysis. They rarely followed the deeper requirements — explicit truncation markers, embedded-error examination, and fix recommendations. |
| **Memory Confound** | _Strong_: the system `## Memory` instruction and the competing `single-url-retrieval-measurement` memory skill were present or referenced in 24/31 runs (77%), making it difficult to isolate the workspace skill's effect. |
| **Fix Recommendations** | _Absent_: despite the skill requiring concrete fix recommendations when a gap is addressable, 0/31 opt-in runs produced one. |

---

## Results Details

| | |
| --- | --- |
| **Track** | `T2` `GPT`-interpreted, VS Code with Codex Extension |
| **Test** | [`EC-6` Raw GitHub Markdown](`https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md`) |
| **Skill condition** | `opt-in` `docs-consumption/SKILL` present, not named in prompt |
| **Agents Observed** | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5`, `GPT-5.6 Luna`, `GPT-5.6 Sol`, `GPT-5.6 Terra` |
| **Reasoning Levels** | `Light`/`Low`, `Medium`, `High`, `Extra High`, `Ultra` |
| **Total Runs** | 31 |
| **Skill loaded (audit)** | 27 / 31 (87%) |
| **Agent mentioned skill path** | 1 / 31 (3%) |
| **Protocol prefix used** | 10 / 31 (32%) |
| **Skill language used** | 31 / 31 (100%) |
| **Disclosure `yes`** | 1 / 31 |
| **Disclosure `mixed`** | 6 / 31 |
| **Disclosure `implicit`** | 0 / 31 |
| **Disclosure `no`** | 24 / 31 |
| **Average disclosure tier** | 0.48 (`no` = 0, `implicit` = 1, `mixed` = 2, `yes` = 3) |
| **Completeness accurate** | 31 / 31 (100%) |
| **Error examined** | 27 / 31 (87%) |
| **Execution vs completeness** | 31 / 31 (100%) |
| **Avoided reframing** | 26 / 31 (84%) |
| **Fix recommended** | 0 / 31 (0%) |
| **Memory signals present** | 24 / 31 (77%) |
| **Both memory + skill** | 24 / 31 (77%) |

### What the numbers mean

The high `completeness_accurate` and `exec_vs_complete` scores show that agents did not lie about outcomes: when `curl` returned the full 92 KB body, they correctly labeled the fetch complete, and they distinguished tool execution from content delivery. The `error_examined` and `avoided_reframing` numbers look strong on paper, but they are consistent with behavior already seen on other tracks. Agents regularly describe the `curl` DNS/sandbox warning in reasoning and reporting; that is not a new skill effect.

The dominant disclosure label is **`no`** (24/31). This is not because agents hid truncation, but because most agents bypassed `web` and used `curl` directly. Without a visible `web` `L54` window, there was little truncation to disclose. The skill's intended effect — making agents explicitly name partiality, embedded errors, and limitations — therefore does not show up strongly under opt-in.

The **0% fix-recommendation rate** is the clearest gap. `SKILL.md` asks agents to suggest a concrete fix when a limitation is addressable (for example, using `curl` to escape the `web` line-window). Even when agents correctly noted the DNS sandbox or the `web` limit, none recommended the documented remediation.

---

## Memory vs. Workspace Skill Audit

The `memory_audit.py` and `memory_analyzer.py` outputs separate three things: (1) whether the workspace `docs-consumption` skill loaded in the developer `<skills_instructions>` block; (2) whether the system `## Memory` instruction was present; and (3) whether the agent read or cited the competing `single-url-retrieval-measurement` memory skill.

### Overall co-occurrence

| Condition | Count | % of runs |
| --- | --- | --- |
| Workspace skill signals | 27 / 31 | 87% |
| Memory signals | 24 / 31 | 77% |
| Both memory and workspace skill | 24 / 31 | 77% |
| Memory only | 0 / 31 | 0% |
| Workspace skill only, no `.codex/memories` | 3 / 31 | 10% |
| Neither | 4 / 31 | 13% |

### Skill signal breakdown

| Signal | Count | % of all runs |
| --- | --- | --- |
| `docs-consumption` loaded | 27 | 87% |
| Name mentioned by agent | 19 | 61% |
| Path mentioned by agent | 1 | 3% |
| Protocol prefix used (`COMPLETE/PARTIAL/UNVERIFIABLE`) | 10 | 32% |
| Skill language used | 31 | 100% |

### Memory sources

| Source | Count | % of memory-positive (24) |
| --- | --- | --- |
| `system_prompt` (`## Memory` block) | 24 | 100% |
| `system_memory_instruction` header | 24 | 100% |
| `final_answer` | 22 | 92% |
| `tool_output` | 19 | 79% |
| `commentary` | 5 | 21% |

### Competing skills: system skills block vs. system memory instruction

| Condition | Count | % of all runs |
| --- | --- | --- |
| `docs-consumption` loaded (system skills block) | 27 | 87% |
| System `## Memory` instruction present | 24 | 77% |
| `single-url-retrieval-measurement` referenced (system-instructed + agent-read) | 24 | 77% |
| Both present | 24 | 77% |
| `docs-consumption` only | 3 | 10% |
| Memory-instructed only | 0 | 0% |

### GPT-5.4-Mini early vs. late split

The first four `GPT-5.4-Mini` rollouts (morning of 2026-07-09) show no memory signals and no workspace skill loading. The later five show the workspace skill loading consistently, with memory references only in the last two.

| Period | Runs | Memory+ | Workspace Skill+ | Both | Memory-only | Workspace-only | Neither |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Early | 4 | 0 | 0 | 0 | 0 | 0 | 4 |
| Late | 5 | 2 | 5 | 2 | 0 | 3 | 0 |

This split is consistent with a version or rollout change rather than with reasoning level: all four early runs were across different reasoning levels, and all later runs loaded the skill regardless of level.

---

## Skill Opt-In Findings

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **Skill file is loaded but rarely followed in depth** | 31 `EC-6` opt-in runs | 87% loaded, 61% mentioned skill name, 32% used protocol prefix, 100% used surface language like `COMPLETE` | **Loading a skill does not guarantee protocol compliance; opt-in discovery produces shallow adoption.** |
| 2 | **Skill opt-in does not shift retrieval strategy** | 31 `EC-6` opt-in runs | Most runs bypassed `web` for `curl`, same as historical `T2`; no new pagination or escalation pattern tied to skill discovery | **When agents can already reach the raw HTTP body, the skill does not change tool choice.** |
| 3 | **Skill opt-in weakens the visible truncation signal** | 31 `EC-6` opt-in runs | Disclosure distribution: `yes=1`, `mixed=6`, `implicit=0`, `no=24`; average tier 0.48 | **By using `curl`, agents remove the `L54` web-window signal that historical `T2` runs disclosed. Skill opt-in therefore does not increase explicit truncation reporting on this test.** |
| 4 | **Agents classify completeness accurately but do not recommend fixes** | 31 `EC-6` opt-in runs | `completeness_accurate=100%`, `exec_vs_complete=100%`, `avoided_reframing=84%`, but `fix_recommended=0%` | **The skill's concrete-fix requirement is ignored. Classification and honesty scores may reflect baseline behavior as much as skill influence.** |
| 5 | **Memory skill is the dominant co-influence** | 31 `EC-6` opt-in runs | 77% of runs had both memory and workspace skill signals; memory skill referenced in 79% of `tool_output` and 92% of `final_answer` | **The workspace `docs-consumption` skill cannot be evaluated in isolation; the system-injected memory skill is at least as visible and may override it.** |
| 6 | **Skill discovery is not consistent across sessions** | 9 `GPT-5.4-Mini` runs | Early Mini runs loaded neither skill nor memory; later Mini runs loaded the workspace skill consistently | **Skill discovery depends on runtime/version conditions, not only on file presence and reasoning level.** |
| 7 | **`COMPLETE` prefix becomes a stylistic shortcut** | 31 `EC-6` opt-in runs | All runs used skill language; many opened reports with `COMPLETE` and included phrases like "DNS/sandbox error" or "use curl" without tying them to the actual limitation | **Agents adopt the easiest surface markers of the protocol without adopting its deeper epistemic discipline.** |
| 8 | **Avoided reframing is consistent with baseline, not clearly a skill effect** | 31 `EC-6` opt-in runs | 84% avoided reframing; DNS/sandbox errors were described in reasoning and reporting on other tracks too | **Honesty about failure is already part of baseline agent behavior on this surface. The skill does not obviously deepen diagnosis.** |
| 9 | **Disclosure taxonomy maps poorly onto skill-opt-in behavior** | 31 `EC-6` opt-in runs | `yes/mixed/implicit/no` was designed for web-truncation disclosure; `curl`-complete runs default to `no` even when agents are accurate | **A skill designed to improve disclosure may need a different metric when the dominant strategy avoids the surface that triggers disclosure.** |
| 10 | **Skill opt-in produces the expected false-positive profile for a first track** | 31 `EC-6` opt-in runs | High surface-compliance scores, zero fix recommendations, weak explicit truncation naming, strong memory confound | **Passive skill presence produces shallow, hard-to-attribute compliance. This is a useful baseline, not evidence that the skill works.** |

---

## Reading the Scores as False Positives

The RUNBOOK's [False-positive Checklist](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/docs-consumption-skill-flash/RUNBOOK.md#false-positive-checklist) is the right lens for this track. Most opt-in runs tick several boxes:

- **Confident caveat.** Agents write polished language like "searched the web" or "curl succeeded" without flagging the actual limitation.
- **Tool rerouting without disclosure.** Most agents bypass `web` for `curl`, but they do not explain why. The strategy changes, but the report does not.
- **Skill ignored.** Even when the skill file loaded, many runs did not use the `COMPLETE/PARTIAL/UNVERIFIABLE` format or show protocol-aligned reasoning.
- **Fix recommended without diagnosis.** No run produced a concrete fix tied to the observed `L54`/DNS limitation.
- **Explicit but incorrect.** Runs that opened with `COMPLETE` after only a `curl` fetch were technically accurate for that path, but they did not demonstrate the protocol's failure-examination intent.

This is expected for a first track that is only measuring baseline skill-injection behavior. The value of the opt-in condition is establishing how much of the apparent compliance is noise before adding the `skill-on` and memory-suppressed conditions.

## Data Visualizations

<!-- TODO: embed disclosure taxonomy heatmap, failure-examination dimension chart, memory/skill co-occurrence chart, and per-model skill-signal breakdown here. -->

---

## Raw Evidence

- Flash results CSV: [`open-ai-codex-web-search/results/docs-consumption-skill-flash/results.csv`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/docs-consumption-skill-flash/results.csv)
- Runbook: [`open-ai-codex-web-search/results/docs-consumption-skill-flash/RUNBOOK.md`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/docs-consumption-skill-flash/RUNBOOK.md)
- Memory audit report: [`open-ai-codex-web-search/results/docs-consumption-skill-flash/artifacts/rollouts/T2-skill-opt-in/memory-analysis/T2_memory_analyzer_report.md`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/docs-consumption-skill-flash/artifacts/rollouts/T2-skill-opt-in/memory-analysis/T2_memory_analyzer_report.md)
- Analysis script: [`open-ai-codex-web-search/scripts/docs_consumption_skill_analysis.py`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/docs_consumption_skill_analysis.py)
