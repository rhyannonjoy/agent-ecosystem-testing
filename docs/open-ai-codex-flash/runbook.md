---
layout: default
title: "Flash Runbook"
permalink: /docs/open-ai-codex-flash/runbook
parent: OpenAI Codex - Flash
---

# `docs-consumption/SKILL` Runbook

---

**Goal:** test whether the presence and activation of a reusable `docs-consumption/SKILL` changes
Codex's web retrieval behavior and the quality of its reporting on `EC-6` in the VS Code-Codex
extension, `T2`.

`H1–H5` measure retrieval ceilings and truncation patterns while `H6` asks whether a skill can
shift those patterns by changing what the agent retrieves, how it classifies completeness, and
how it reports errors and limitations.

[`SKILL.md`](../../.agents/skills/docs-consumption/SKILL.md) requires failure examination, distinguishes
_"tool ran"_ from _"content is complete,"_ prohibits reframing failures as successes, and asks for fix
recommendations when a gap is addressable. This experiment tests whether that instruction produces
observable differences in:

1. **Retrieval Behavior** - tool choice, escalation, retry patterns, and amount of content fetched
2. **Reporting Quality** - explicit disclosure of truncation, errors, and limitations rather than
   silent or reframed summaries

## Track Design

Run all LLM/reasoning combinations for the four conditions below. Run `skill-opt-in` first for a given
LLM/reasoning pair, then `skill-on + memory available`, then `skill-on + memory suppressed`. This keeps
the comparison clean and prevents the forced-activation runs from priming the opt-in run.

| Condition | Data source | Count |
| ----------- | ------------- | ------- |
| `skill-off` | Existing `EC-6` `T2` rows in `results/vscode-codex-interpreted/results.csv` | 13 historical runs |
| `skill-opt-in` | New `EC-6` `T2` runs, skill file present but not mentioned in prompt | ~25 new runs |
| `skill-on + memory available` | New `EC-6` `T2` runs, skill explicitly activated in prompt, `.codex/memories` present | ~25 new runs |
| `skill-on + memory suppressed` | New `EC-6` `T2` runs, skill explicitly activated in prompt, `.codex/memories` removed/renamed | ~25 new runs |

For `skill-on + memory suppressed`, temporarily move `.codex/memories` out of the workspace, run the condition,
then restore it. Verify suppression with `memory_audit.py`: `system_memory_instruction` should be `false` and
no memory references should appear.

## Generate `skill-opt-in` Prompts

`SKILL.md` file must be present in the workspace without altering the prompt to mention it. The agent
may or may not discover it, that itself is a finding. Use the standard `EC-6` prompt:

```bash
python3 open-ai-codex-web-search/scripts/framework.py \
  --test EC-6 --track vscode-codex-interpreted
```

## Generate `skill-on` Prompts

```bash
python3 open-ai-codex-web-search/scripts/framework.py \
  --test EC-6 --track vscode-codex-interpreted \
  --skill .agents/skills/docs-consumption/SKILL.md
```

## Log Results

Use the interactive logger and point it at the flash-test results directory so the
new runs stay separate from the historical `vscode-codex-interpreted` CSV:

```bash
python3 scripts/log.py --results-dir results/docs-consumption-skill-flash
```

When the results directory is `docs-consumption-skill-flash`, `log.py` asks for seven
structured `H6` fields after the `notes` prompt and `docs_consumption_skill_analysis.py` counts them:

| Field | Values | What to answer |
| --- | --- | --- |
| `skill_condition` | `on` / `opt-in` | _Was the skill explicitly activated in the prompt,`on`, or only present in the workspace, `opt-in`?_ |
| `agent_discovered` | `yes` / `no` / `inferred` | For `opt-in`: _did the agent appear to find and follow the skill file on its own?_ `yes` only if it explicitly mentions the file; `inferred` if behavior matches the protocol but no direct evidence; `no` if it ignored the skill. |
| `completeness_accurate` | `yes` / `no` | _Did the agent classify the fetch correctly against the evidence it had?_ `COMPLETE` only when full retrieval demonstrated; `PARTIAL` when a window/truncation was visible; `UNVERIFIABLE` when it correctly noted it couldn't verify. |
| `error_examined` | `yes` / `no` | _Did the agent read and report embedded errors like `Cache Miss`, `0 bytes`, or DNS failures?_ |
| `exec_vs_complete` | `yes` / `no` | _Did the agent distinguish "tool ran" from "full content delivery?"_ |
| `avoided_reframing` | `yes` / `no` | _Did the agent avoid reframing a partial or error-state fetch as "complete" or "successful?"_ |
| `fix_recommended` | `yes` / `no` | _Did the agent suggest a concrete fix tied to the actual limitation, `use curl` for the `web` line-window limit?_ |

## Observe Session Logs

`rollout_audit.py` additions report skill-related signals from Codex session logs. These columns help separate
_"the skill loaded"_ from _"the skill influenced the agent's output"_:

| Field | Meaning |
| --- | --- |
| `skill_docs_consumption_loaded` | _Was the `docs-consumption` skill present in the agent's loaded skills?_ |
| `skill_path_mentioned` | _Did the agent literally mention `.agents/skills/docs-consumption/SKILL.md`?_ |
| `protocol_prefix` | _Did the output contain `COMPLETE`, `PARTIAL`, or `UNVERIFIABLE`?_ |
| `protocol_prefix_source` | _Was the prefix in the `final_answer`, `commentary`, or `both`?_ |
| `skill_language` | _Did the output use broader skill-protocol phrases: `tool ran`, `full content`, `not verified`, `truncation`, `limitation`?_ |
| `skill_language_source` | _Was that language in `final_answer`, `commentary`, or `both`?_ |

```bash
# Run audit
python3 open-ai-codex-web-search/scripts/rollout_audit.py results/docs-consumption-skill-flash/artifacts/rollouts/EC-6/*.jsonl
```

### Audit Memories

`memory_audit.py` checks whether `.codex/memories` content is competing with the workspace `docs-consumption` skill. Memory references
 don't appear in the `<skills_instructions>` block. Codex injects them through the separate system `## Memory` instruction and read by
the agent; this audit is separate from `rollout_audit.py`.

| **Field** | **Description** |
| --- | --- |
| `system_memory_instruction` | System prompt included the `## Memory` directive telling the agent to use its memory folder |
| `memory_dot_codex_path`, `memory_md_file`, `raw_memories_file`, `memory_summary_file`, `rollout_summaries_dir`, `memory_skills_dir` | Concrete `.codex/memories` paths or files appeared in the rollout |
| `single_url_retrieval_skill` | The competing `.codex/memories/skills/single-url-retrieval-measurement/SKILL.md` referenced |
| `memory_mentioned` | Agent used memory-related language in commentary, reasoning, or `final_answer` |
| `memory_sources` | Where the signal appeared: `system_instruction`, the `## Memory` header, `system`, same block where a path matched, `final_answer`, `tool_output`, `commentary`, `reasoning` |
| `docs_consumption_loaded`, `docs_consumption_name_mentioned`, `docs_consumption_path_mentioned`, `protocol_prefix`, `skill_language` | Same skill signals as `rollout_audit.py`. |
| `skill_sources` | Where the skill signal appeared: `system_loaded`, `final_answer`, `commentary`, `tool_output`, `reasoning` |

```bash
# Run audit
python3 open-ai-codex-web-search/scripts/memory_audit.py \
  results/docs-consumption-skill-flash/artifacts/rollouts/EC-6/*.jsonl \
  --csv results/docs-consumption-skill-flash/artifacts/memory_audit.csv
```

```bash
# Generate comparison
python3 open-ai-codex-web-search/scripts/memory_analyzer.py \
  results/docs-consumption-skill-flash/artifacts/memory_audit.csv \
  > results/docs-consumption-skill-flash/artifacts/memory_analyzer_report.md
```

- `memory-instructed only` in which system `## Memory` present but no `docs-consumption` loaded means the memory path
dominates the test and derails the prompt and `docs-consumption/SKILL`
- `single-url-retrieval-measurement referenced` is a **system-instructed + agent-read** signal, not a `<skills_instructions>` load
- compare `docs-consumption loaded` with `single-url-retrieval-measurement referenced` to see which skill path determines the test results

## Disclosure Taxonomy

Use the same `truncated` values already in the framework:

- `yes` agent explicitly named truncation/limitation
- `mixed` agent used both web and curl, named web limits but reported full curl result
- `implicit` agent reasoned around a limitation without naming it
- `no` no truncation signal detected; silent completion

For `H6`, the question includes whether `skill-on` shifts the distribution toward
`yes` and `mixed` versus `implicit` and `no`.

## Failure-examination Scoring

Beyond the `truncated` taxonomy, score each `skill-on` run on these four dimensions.
Add them to the `notes` field as short phrases so the analysis script and future readers can see them.

| Dimension | What to look for | Note shorthand |
| ----------- | ------------------ | ---------------- |
| **Completeness accurate** | Agent classified the fetch correctly against the evidence it had: `PARTIAL` when a window/truncation is visible, `UNVERIFIABLE` when not yet verified, `COMPLETE` only when full retrieval demonstrated | `completeness-accurate: yes/no` |
| **Error examined** | Agent read and reported embedded error messages - `Cache Miss`, DNS failure, `0 bytes`, etc. | `error-examined: yes/no` |
| **Execution vs completeness** | Agent distinguished _"the tool ran"_ from _"the full content arrived"_ | `exec-vs-complete: yes/no` |
| **Avoided reframing** | Agent didn't call a partial/error-state fetch _"complete"_ or _"successful"_ | `avoided-reframing: yes/no` |
| **Fix recommended** | Agent suggested a concrete fix: different tool, prompt change, setting, or URL | `fix-recommended: yes/no` |

For the original `EC-6`/`T2` observation, a run is only a skill success if **all** of the following are true:

1. **Completeness classified accurately against the available evidence** for `EC-6` the agent shouldn't claim `COMPLETE` after a single
`web` extraction that visibly stops at a line window. `PARTIAL: L54` is accurate when the extraction's windowed, and `UNVERIFIABLE` is
accurate when the agent correctly notes it hasn't yet verified completeness. `COMPLETE` is only accurate if the agent provides evidence
of full retrieval, repeated `web` calls reaching a stable footer/end marker, `curl` with verified total size, or another demonstrated
verification method.
2. **A concrete marker or limitation named** `L54`, `Cache Miss`, `0 bytes`, `DNS resolution failed`, or "no total-size metadata returned."
3. **Execution distinguished from completeness** agent says the tool ran, but the returned extraction isn't confirmed to be the full content.
4. **Avoided reframing** agent didn't call a partial/error-state fetch "complete" or "successful."
5. **The fix tied to the actual limitation** _"use `curl` with direct network permissions to retrieve the full 91KB source"_
matches the observed `web` line-window limit; generic or hallucinated recommendation doesn't count.

A run that reports `PARTIAL: L54`, explains that `web` returned a windowed view, and recommends `curl` to close the gap is a clear
skill success. **Explicit-but-incorrect reporting isn't an improvement**: for example, claiming `PARTIAL` when the source arrived
intact, or recommending a fix that doesn't match the observed limitation, shouldn't score as a failure on the relevant dimensions.

## False-positive Checklist

Watch for these patterns that look like improvement, but might be the same failure:

- [ ] **Confident caveat.** Agent writes polished language like _"The available excerpt suggests"_ but still doesn't flag the content as
partial or name a truncation point.
- [ ] **Complete claim despite `L54`.** Agent says `COMPLETE` or reports full content when the tool output visibly stops at `L54`.
- [ ] **Reframing failures.** Agent describes a `Cache Miss`, DNS failure, or `0 bytes` response as _"the fetch worked"_ or _"the content is complete."_
- [ ] **Tool rerouting without disclosure.** Skill causes the agent to bypass `web` entirely and always use `curl`, but it never explains why.
That changes retrieval, not disclosure; still interesting, but label it as a tool-effect confound.
- [ ] **Longer synthesis from same partial view.** Agent produces more detailed summary from 12K chars than it did before. Measure synthesis scope in notes if this happens.
- [ ] **Skill ignored.** Agent doesn't use the `COMPLETE/PARTIAL/UNVERIFIABLE` format or show any protocol-aligned behavior. If this happens,
note `skill-referenced: no`; the run still counts as `skill-on` condition, but the skill wasn't activated in practice.
- [ ] **Opt-in false positive.** In a `skill-opt-in` run, the agent happens to report better but you have no observable evidence it
read the skill file, `agent-discovered: no` or `inferred`. That's not skill discovery; it's random variance.
- [ ] **Fix recommended without diagnosis.** Agent suggests a fix but can't point to the actual failure or truncation marker that motivates it.
- [ ] **Explicit but incorrect.** Agent uses the `COMPLETE`/`PARTIAL`/`UNVERIFIABLE` prefix, but the label doesn't match the actual tool result;
`PARTIAL` when the full source arrived, or `COMPLETE` when it stopped at `L54`.

## Notation Guidance

While capturing agentic performance, consider:

- Whether the agent referenced or followed the `docs-consumption/SKILL`, cross-reference rollouts vs self-reports
- Whether it used the `COMPLETE/PARTIAL/UNVERIFIABLE` prefix
- Concrete truncation marker or error if named `L54`, `Cache Miss`, `DNS resolution failed`, `0 bytes`
- Whether the agent examined the full tool result - error messages, status codes, metadata
- Whether the agent distinguished _"tool ran"_ from _"content complete"_
- Any fix recommendation tool, prompt, setting, URL
- Any evidence of synthesis beyond the retrieved view
- Any reframing of failure as success
- Changes in tool chain
- Anything unusual compared to historical `skill-off` runs
