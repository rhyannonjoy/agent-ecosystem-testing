---
layout: default
title: "Runbook"
permalink: /docs/open-ai-codex-flash/runbook
parent: OpenAI Codex - Flash
---

# `docs-consumption/SKILL` Flash Experiment Runbook

---

>_**Objective**: test whether the presence-activation of reusable `docs-consumption/SKILL` changes
Codex's web retrieval behavior and report quality of `EC-6` using `T2` surface VS Code-Codex extension._
>
>_`H1–H5` measure retrieval ceilings and truncation patterns while `H6` asks whether a `/SKILL` can
shift those patterns by changing how agents retrieve and classify completeness._
>
>_[`SKILL.md`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/.agents/skills/docs-consumption/SKILL.md)
requires failure examination, distinguishes "tool ran" from "content is complete," prohibits reframing failures as successes,
and asks for recommendations when a gap is addressable. This experiment tests whether that instruction produces
observable differences in:_
>
> - _**Retrieval Behavior**: tool choice, escalation, retry patterns, and content delivery state_
> - _**Report Quality**: explicit disclosure of truncation, errors, and limitations vs silence or reframing_

---

## Track Design

Run all available LLM-reasoning combinations for the conditions below. To prevent forced-activation runs
priming `opt-in` runs, start with `skill-opt-in` subtrack, then proceed to `skill-on + memory available`
and `skill-on + memory suppressed`. Verify `/memories` presence and/or suppression with
[`memory_audit`](#audit-memories). For suppression, output should include `system_memory_instruction`: `false`
and exclude `/memories` references.

| **Condition** | **Source** | **Count** |
| ----------- | ------------- | ------- |
| `skill-off` | Existing `EC-6` `T2` rows in<br>`results/vscode-codex-interpreted/results.csv` | 13 runs |
| `skill-opt-in` | New `EC-6` `T2` runs, `/SKILL` present,<br>but not mentioned in prompt | 20+ runs* |
| `skill-on` +<br>`memory available` | New `EC-6` `T2` runs, `/SKILL` explicitly activated in prompt,<br>`.codex/memories` present | 20+ runs |
| `skill-on` +<br>`memory suppressed` | New `EC-6` `T2` runs, `/SKILL` explicitly activated in prompt,<br>`.codex/memories` not enabled | 20+ runs |

> _*Number of runs depends on LLM-reasoning availability for Codex Pro plans_
>
> _**CLI 0.145.x:** Codex no longer injects `## Memory` instruction by default, even when
> `.codex/memories/` exists; `skill-on` runs effectively `memory suppressed` unless enabled_

---

## Generate Prompts

`/docs-consumption/SKILL` must be present without changes to the `EC-6` prompt. Agents
may or may not discover it, that itself is a finding.

```bash
# skill-opt-in
python3 scripts/framework.py --test EC-6 --track vscode-codex-interpreted

# skill-on
python3 scripts/framework.py --test EC-6 --track vscode-codex-interpreted \
  --skill .agents/skills/docs-consumption/SKILL.md
```

## Log Results

Separate observations from historical `vscode-codex-interpreted` results. Point the logger at
`/skill-flash` results, which includes `H6` fields that `T2_docs_consumption_skill_analysis` counts:

```bash
python3 scripts/log.py --results-dir results/docs-consumption-skill-flash
```

### `T2` Fields

| **Field** | **Values** | **Question** |
| --- | --- | --- |
| `skill_condition` | `on` `opt-in` | _Was `/SKILL` explicitly activated in the prompt or only present in the workspace?_ |
| `agent_discovered` | `yes` `no` `inferred` | _Did the agent independently find-follow `/SKILL`?_ Cross-reference session log audits and agent self-report output. |
| `completeness_accurate` | `yes` `no` | _Did the agent classify the fetch correctly against the evidence it had?_ `COMPLETE`: full retrieval demonstrated; `PARTIAL`: window/truncation visible; `UNVERIFIABLE`: correctly noted it couldn't verify. |
| `error_examined` | `yes` `no` | _Did the agent read-report embedded errors - `Cache Miss`, `0 bytes`, or DNS resolution/sandbox failures?_ |
| `exec_vs_complete` | `yes` `no` | _Did the agent distinguish "tool ran" from "full content delivery?"_ |
| `avoided_reframing` | `yes` `no` | _Did the agent avoid reframing a partial or error-state fetch as "complete" or "successful?"_ |
| `fix_recommended` | `yes` `no` | _Did the agent suggest a fix tied to a limitation to make future fetches more efficient?_ |

### `T3` Fields

The logger records free-text fields instead of binary scores meant to capture run nuance, especially when `/memories` flattens
behavior across sessions; examine results with `T3_docs_consumption_skill_analysis`:

| **Field** | **Question** |
| --- | --- |
| `skill_compliance` | _Did the agent name or visibly act on `/SKILL`?_: `yes`, `no`, or `inferred` |
| `completeness` | _How did the agent classify completeness? Was `COMPLETE`/`PARTIAL`/`UNVERIFIABLE` grounded in evidence?_ |
| `errors` | _What embedded errors did the agent examine?_ |
| `exec_completeness` | _How did the agent separate "the tool ran" from "the full content arrived?"_ |
| `reframing` | _Did the agent reframe a partial or error-state fetch as complete/successful?_ |
| `fix` | _Did the agent suggest a fix? Was it tied to a diagnosed limitation?_ |
| `false_positive` | _Summary: `baseline`, `skill-surface-only`, `skill-influenced`, `memory-dominant`, `unclear`, or other?_ |

## Audit Session Logs

[`rollout_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_audit.py)
reports `/SKILL`-related signals from Codex session rollout logs. These columns help separate
_"the skill loaded"_ from _"the skill influenced the agent's output"_:

```bash
# Run audit
python3 scripts/rollout_audit.py results/docs-consumption-skill-flash/artifacts/rollouts/EC-6/*.jsonl
```

| **Field** | **Question** |
| --- | --- |
| `skill_docs_consumption_loaded` | _Was the `docs-consumption/SKILL` present in the agent's loaded skills?_ |
| `skill_path_mentioned` | _Did the agent reference the full path `.agents/skills/docs-consumption/SKILL.md`?_ |
| `protocol_prefix` | _Did the output contain `COMPLETE`, `PARTIAL`, or `UNVERIFIABLE`?_ |
| `protocol_prefix_source` | _Was the prefix in the `final_answer`, `commentary`, or `both`?_ |
| `skill_language` | _Did the output use broader `/SKILL`-protocol phrases: `tool ran`, `full content`, `not verified`, `truncation`, `limitation`?_ |
| `skill_language_source` | _Was that language in `final_answer`, `commentary`, or `both`?_ |

### Audit Memories

[`memory_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_audit.py)
checks whether `.codex/memories` content is competing with `docs-consumption/SKILL`. `/memories` references
don't appear in the `<skills_instructions>` block. Codex injects them through the separate system `## Memory`
instruction and read by the agent each run. Run this audit separately from the rollout audit:

```bash
# Run audit
python3 scripts/memory_audit.py \
  results/docs-consumption-skill-flash/artifacts/rollouts/EC-6/*.jsonl \
  --csv results/docs-consumption-skill-flash/artifacts/memory_audit.csv

# Generate comparison
python3 scripts/memory_analyzer.py \
  results/docs-consumption-skill-flash/artifacts/memory_audit.csv \
  results/docs-consumption-skill-flash/artifacts/memory_analyzer_report.md
```

| **Field** | **Value** | **Measurement** |
| --- | --- | --- |
| `docs_consumption_loaded` | `true`<br>`false` | `docs-consumption/SKILL` presence in `<skills_instructions>` block |
| `docs_consumption_name_mentioned` | `true`<br>`false` | Agent referenced `/SKILL` by name: `docs-consumption` |
| `docs_consumption_path_mentioned` | `true`<br>`false` | Agent referenced full `/SKILL` path: `.agents/skills/docs-consumption/SKILL.md` |
| `protocol_prefix` | `COMPLETE` `PARTIAL` `UNVERIFIABLE` `{ empty }` | Agent prefaced report with `/SKILL`-required protocol prefix |
| `skill_language` | `true`<br>`false` | Agent used protocol phrases: `tool ran`, `full content`, `truncation`, or `limitation` |
| `memory_citation_status` | `absent`<br>`null`<br>`used` | State of rollout’s `memory_citation` field: not present, present but empty, or present with a value |
| `memory_citation_source_discrepancy` | free-text<br>`{ empty }` | Whether rollout’s `memory_citation` field conflicts with the agent’s self-reported `/memories` sources |
| `memory_dot_codex_path`, `memory_md_file`, `raw_memories_file`, `memory_summary_file`, `rollout_summaries_dir`, `memory_skills_dir` | `true`<br>`false` | Whether corresponding `/memories` path appeared |
| `memory_mentioned` | `true`<br>`false` | Agent used `/memories`-related language in commentary, reasoning, or `final_answer` |
| `memory_sources` | comma-separated list<br>or `none` | Locations of `/memories` signals: `system_instruction`, `system`, `commentary`, `reasoning`, `final_answer`, `tool_output` |
| `single_url_retrieval_skill` | `true`<br>`false` | Reference of competing `/memories...single-url-retrieval-measurement/SKILL`; not auto-loaded<br>from `<skills_instructions>` |
| `skill_sources` | comma-separated list<br>or `none` | Locations of `/SKILL` signals: `system_loaded`, `commentary`, `reasoning`, `final_answer`, `tool_output` |
| `system_memory_instruction` | `true`<br>`false` | System prompt included `## Memory` directive telling agent to use `/memories` |

## False-positive Guidance

More polished agentic reporting may look like an improvement while obscuring the same failure:

- **Fix Recommended, No Diagnosis**: suggests a fix but can't point to the failure that motivates it
- **Longer Synthesis, Same Partial View**: produces more details without protocol analysis
- **Loud, Wrong**: uses `COMPLETE`,`PARTIAL`,`UNVERIFIABLE`, but label doesn't match tool result
- **Reframing Failures**: describes errors while reporting _"the fetch worked"_ or _"the content is complete"_
- **`/SKILL` Ignored**: doesn't use report completion prefix or show any protocol-aligned behavior
- **Tool Rerouting, No Disclosure**: bypass `web` for `curl` without explanation
