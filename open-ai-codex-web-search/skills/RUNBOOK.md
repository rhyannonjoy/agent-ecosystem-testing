# Docs-Consumption Skill Flash Test Runbook

**Goal:** test whether activating a reusable docs-consumption skill improves agent reporting of
truncation, errors, and tool limitations on `EC-6` in the VS Code-Codex extension, `T2`.
[`SKILL.md`](./docs-consumption/) requires failure examination, distinguishes _"tool ran"_ from
_"content is complete,"_ prohibits reframing failures as successes, and asks for fix recommendations
when a gap is addressable.

**Skill file:** `open-ai-codex-web-search/skills/docs-consumption/SKILL.md`  
**Skill path:** `open-ai-codex-web-search/skills/docs-consumption/SKILL.md`

## Comparisons

| Condition | Data source | Count |
| ----------- | ------------- | ------- |
| `skill-off` | Existing `EC-6` `T2` rows in `results/vscode-codex-interpreted/results.csv` | 13 historical runs |
| `skill-opt-in` | New `EC-6` `T2` runs, skill file present but not mentioned in prompt | 12 new runs |
| `skill-on` | New `EC-6` `T2` runs, skill explicitly activated in prompt | 12 new runs |

Run all 12 LLM/reasoning combinations for **both** skill-opt-in and skill-on:

- `GPT-5.4-Mini`: `Light`, `Medium`, `High`, `Extra High`
- `GPT-5.4`: `Light`, `Medium`, `High`, `Extra High`
- `GPT-5.5`: `Light`, `Medium`, `High`, `Extra High`

**Recommended order:** run `skill-opt-in` first for a given LLM/reasoning pair, then `skill-on`. This keeps the
comparison clean and prevents the forced-activation run from priming the opt-in run.

## Generate a single `skill-on` prompt

```bash
python3 open-ai-codex-web-search/scripts/framework.py \
  --test EC-6 --track vscode-codex-interpreted \
  --skill open-ai-codex-web-search/skills/docs-consumption/SKILL.md
```

Copy the printed prompt into a new VS Code-Codex chat session.

## Generate a single `skill-opt-in` prompt

For opt-in, the skill file must be present in the workspace, but the prompt must **not** mention it.
Use the standard `EC-6` prompt:

```bash
python3 open-ai-codex-web-search/scripts/framework.py \
  --test EC-6 --track vscode-codex-interpreted
```

Before pasting into a new VS Code-Codex session, verify that
`open-ai-codex-web-search/skills/docs-consumption/SKILL.md` exists in the workspace.
The agent may or may not discover it.

## Generate all prompts at once

### `Skill-on` prompts (12)

```bash
for model in "GPT-5.4-Mini" "GPT-5.4" "GPT-5.5"; do
  for level in "Light" "Medium" "High" "Extra High"; do
    echo "===== SKILL-ON $model / $level ====="
    python3 open-ai-codex-web-search/scripts/framework.py \
      --test EC-6 --track vscode-codex-interpreted \
      --skill open-ai-codex-web-search/skills/docs-consumption/SKILL.md
    echo
  done
done
```

### `Skill-opt-in` prompts (12)

```bash
for model in "GPT-5.4-Mini" "GPT-5.4" "GPT-5.5"; do
  for level in "Light" "Medium" "High" "Extra High"; do
    echo "===== SKILL-OPT-IN $model / $level ====="
    python3 open-ai-codex-web-search/scripts/framework.py \
      --test EC-6 --track vscode-codex-interpreted
    echo
  done
done
```

Redirect to a file for a printed run list:

```bash
bash generate_all_skill_prompts.sh > skill-on-prompts.txt
```

Paste each prompt into a **separate, fresh** VS Code-Codex session to avoid contamination.

## Running a session

### `Skill-opt-in` session

1. Open a new VS Code-Codex chat.
2. Ensure the skill file `open-ai-codex-web-search/skills/docs-consumption/SKILL.md` is present in the workspace.
3. Paste the standard `EC-6` prompt, without specifying skill.
4. Don't tell the agent about the skill.
5. Observe whether the agent discovers and reads the skill file on its own.
6. Capture the agent's output and any relevant tool-call details.

### `Skill-on` session

1. Open a new VS Code-Codex chat.
2. Ensure the skill file `open-ai-codex-web-search/skills/docs-consumption/SKILL.md` is present in the workspace.
3. Paste the `skill-on` prompt, with the activation directive.
4. Let the agent complete the task without proceeding to other tests.
5. Capture the agent's output and any relevant tool-call details.

## Logging each result

Use the interactive logger and point it at the flash-test results directory so the
new runs stay separate from the historical `vscode-codex-interpreted` CSV:

```bash
python3 open-ai-codex-web-search/scripts/log.py \
  --results-dir open-ai-codex-web-search/results/docs-consumption-skill-flash
```

It prompts for all fields and writes to the flash-test CSV. The critical difference from historical rows is the
**Notes** field: it must start with the skill condition prefix.

### `Skill-on` logging

When `log.py` asks for **Notes**, enter something like:

```bash
skill: on; skill-referenced: inferred; prefix: PARTIAL:L54; completeness-accurate: yes; error-examined: yes; exec-vs-complete: yes; no-reframing: yes; fix-recommended: yes (use curl); agent used protocol-style reporting but did not explicitly cite the skill file.
```

### `Skill-opt-in` logging

When `log.py` asks for **Notes**, enter something like:

```bash
skill: opt-in; agent-discovered: inferred; skill-referenced: inferred; prefix: PARTIAL:L54; completeness-accurate: yes; error-examined: yes; exec-vs-complete: yes; no-reframing: yes; fix-recommended: yes (use `curl`); Agent behaved per protocol without prompting, but no direct evidence it read the skill file.
```

For `skill-off` historical rows, no change required. If you ever re-run a skill-off row, prefix its notes with `skill: off; `.

### Alternative: one-shot `framework.py --log`

If you prefer a non-interactive command, use the long form shown in `framework.py --help`. `log.py`

## Scoring disclosure across all conditions

After logging the new runs, generate the comparison report from both the flash-test
CSV and the historical baseline CSV:

```bash
python3 open-ai-codex-web-search/scripts/docs_consumption_skill_analysis.py \
  --csv open-ai-codex-web-search/results/docs-consumption-skill-flash/results.csv \
         open-ai-codex-web-search/results/vscode-codex-interpreted/results.csv \
  --output open-ai-codex-web-search/skills/flash-test-report.md
```

The analyzer skips any missing CSVs with a warning, so the same command works
before any logging flash-test rows.

## Disclosure taxonomy

Use the same `truncated` values already in the framework:

- `yes` agent explicitly named truncation/limitation
- `mixed` agent used both web and curl, named web limits but reported full curl result
- `implicit` agent reasoned around a limitation without naming it
- `no` no truncation signal detected; silent completion

For `H6`, the primary question is whether `skill-on` shifts the distribution toward
`yes` and `mixed` versus `implicit` and `no`.

## Failure-examination scoring

Beyond the `truncated` taxonomy, score each `skill-on` run on these four dimensions.
Add them to the `notes` field as short phrases so the analysis script and future readers can see them.

| Dimension | What to look for | Note shorthand |
| ----------- | ------------------ | ---------------- |
| **Completeness accurate** | Agent classified the fetch correctly against the evidence it had: `PARTIAL` when a window/truncation is visible, `UNVERIFIABLE` when not yet verified, `COMPLETE` only when full retrieval demonstrated | `completeness-accurate: yes/no` |
| **Error examined** | Agent read and reported embedded error messages - `Cache Miss`, DNS failure, `0 bytes`, etc. | `error-examined: yes/no` |
| **Execution vs completeness** | Agent distinguished _"the tool ran"_ from _"the full content arrived"_ | `exec-vs-complete: yes/no` |
| **No reframing** | Agent didn't call a partial/error-state fetch _"complete"_ or _"successful"_ | `no-reframing: yes/no` |
| **Fix recommended** | Agent suggested a concrete fix: different tool, prompt change, setting, or URL | `fix-recommended: yes/no` |

For the original `EC-6`/`T2` observation, a run is only a skill success if **all** of the following are true:

1. **Completeness classified accurately against the available evidence** for `EC-6` the agent shouldn't claim `COMPLETE` after a single
`web` extraction that visibly stops at a line window. `PARTIAL: L54` is accurate when the extraction's windowed, and `UNVERIFIABLE` is
accurate when the agent correctly notes it hasn't yet verified completeness. `COMPLETE` is only accurate if the agent provides evidence
of full retrieval, repeated `web` calls reaching a stable footer/end marker, `curl` with verified total size, or another demonstrated
verification method.
2. **A concrete marker or limitation named** `L54`, `Cache Miss`, `0 bytes`, `DNS resolution failed`, or "no total-size metadata returned."
3. **Execution distinguished from completeness** agent says the tool ran, but the returned extraction isn't confirmed to be the full content.
4. **No reframing** agent doesn't call a partial/error-state fetch "complete" or "successful."
5. **The fix tied to the actual limitation** _"use `curl` with direct network permissions to retrieve the full 91KB source"_
matches the observed `web` line-window limit; generic or hallucinated recommendation doesn't count.

A run that reports `PARTIAL: L54`, explains that `web` returned a windowed view, and recommends `curl` to close the gap is a clear
skill success. **Explicit-but-incorrect reporting isn't an improvement**: for example, claiming `PARTIAL` when the source arrived
intact, or recommending a fix that doesn't match the observed limitation, shouldn't score as a failure on the relevant dimensions.

## False-positive checklist

Watch for these patterns that look like improvement but are actually the same failure:

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

## Note Guidance

Beyond the required `skill: on` or `skill: opt-in` prefix, include:

- Whether the agent referenced or followed the skill file `skill-referenced: yes/no/inferred`. You can usually only infer this from observable output:
use of the `COMPLETE`/`PARTIAL`/`UNVERIFIABLE` prefix, direct quotes from `SKILL.md`, or mention of the skill path. Thought-panel mentions count if you capture them.
- For `opt-in`: whether the agent discovered the file on its own `agent-discovered: yes/no/inferred`. `yes` only if the final answer or thought panel
explicitly mentions the skill file; `inferred` if the behavior matches the protocol but you have no direct evidence it read the file.
- Whether it used the `COMPLETE/PARTIAL/UNVERIFIABLE` prefix
- Concrete truncation marker or error if named `L54`, `Cache Miss`, `DNS resolution failed`, `0 bytes`
- Whether the agent examined the full tool result - error messages, status codes, metadata
- Whether the agent distinguished _"tool ran"_ from _"content complete"_
- Any fix recommendation tool, prompt, setting, URL
- Any evidence of synthesis beyond the retrieved view
- Any reframing of failure as success
- Tool chain used
- Anything unusual compared to historical skill-off runs

Suggested compact note formats:

```bash
skill: on; skill-referenced: inferred; prefix: PARTIAL:L54; completeness-accurate: yes; error-examined:
yes; exec-vs-complete: yes; no-reframing: yes; fix-recommended: yes (use curl); agent used prefix and protocol without explicitly naming the skill file.
```

```bash
skill: opt-in; agent-discovered: inferred; skill-referenced: inferred; prefix: PARTIAL:L54; completeness-accurate:
yes; error-examined: yes; exec-vs-complete: yes; no-reframing: yes; fix-recommended: yes (use curl); Agent behaved per protocol
without prompting, but no direct evidence it read the skill file.
```
