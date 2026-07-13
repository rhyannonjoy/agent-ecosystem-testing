# EC-6 GPT-5.4 Flash Experiment Summary

## Test Conditions

|                 | **EC-6, GPT-5.4 flash experiment** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed `91,869` to `91,877` characters depending on measurement tool, roughly `22,969` tokens |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox, `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing` writable, `/private/tmp` also writable |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.4` only |
| Runs            | 4 |
| Skill condition | `docs-consumption` skill present in the project root, skill-opt-in sub-track, `SKILL.md` exists in the workspace but the prompt doesn't mention it |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.4 Light` | 91,877 via `perl` length, `wc -m` returned 91,869 | ~22,969 | No in the saved direct response, the terminal display of one earlier command truncated but that didn't affect the saved body | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` with `curl`, `perl`, `wc`, `web` and `web.open` weren't invoked | Yes, `/private/tmp/ec6_spec.md` 92KB, rollout json log 132KB | `SKILL.md` flagged in rollout, not named by the agent, 3 `MEMORY.md` citations at `L48`, `L14`, `L1-6` | named `Test web retrieval EC-6`, asked permission for `curl` twice, the first `curl` failed with exit code 6 from a sandboxed DNS resolution failure and the retry succeeded, chat timer 45 seconds, rollout audit 54.8 seconds |
| `GPT-5.4 Medium` | 91,869 via `wc -c` | ~22,970 | No, the file ended cleanly on a normal bullet | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` with `curl`, `wc -m`, `wc -c`, `tail -c 50`, `sed`, `python3`, wrapped in `multi_tool_use.parallel`, `web` and `web.open` weren't invoked | Yes, `/private/tmp/ec6-spec.md` 92KB, rollout json log 94KB | `SKILL.md` flagged in rollout, not named by the agent, 2 `MEMORY.md` citations at `L41-49`, `L52-53` | named `Test web retrieval EC-6`, asked permission for `curl` once, the first `curl` failed with exit code 6 couldn't resolve host and the retry succeeded with escalated permissions, chat timer 43 seconds, rollout audit 53.2 seconds |
| `GPT-5.4 High` | 91,877 via `perl` length | ~22,969, `chars / 4` estimate equals `22969.25` | No, the file ended cleanly on a complete bullet with a trailing newline | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` wrapped in `multi_tool_use.parallel`, `curl`, `perl`, `wc`, `tail`, `awk`, `rg`, `web` and `web.open` weren't invoked | Yes, `/tmp/ec6-spec.md` 92KB, rollout json log 105KB, this path reuses the Medium run's artifact name | `SKILL.md` flagged in rollout, not named by the agent, 1 `MEMORY.md` citation at `L47-49` | named `Test web retrieval`, asked permission for `curl` once, the first `curl` failed with exit code 6 and the retry succeeded with escalated network access, chat timer 1 minute 19 seconds, rollout audit 1 minute 27.3 seconds |
| `GPT-5.4 Extra High` | 91,869 UTF-8 characters received, raw byte count of the saved response was 91,877 bytes so the file isn't pure ASCII | ~22,970, `chars / 4` heuristic, a local `tiktoken` check was attempted but the module wasn't installed | No, the file ended cleanly on a normal bullet, not mid-sentence, mid-fence, or mid-structure | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` wrapped in `multi_tool_use.parallel`, `curl`, `wc -c`, `wc -w`, `tail -c 50`, `perl`, `rg`, `python3` tokenization attempt failed, `web` and `web.open` weren't invoked | Yes, `/tmp/spec-ec6.md` 92KB, rollout json log 145KB | `SKILL.md` flagged in the rollout audit's `final_answer`, present throughout the run, not named by the agent, 2 `MEMORY.md` citations at `L43-49`, `L1-15` | named `Test web retrieval EC-6`, it's not confirmed whether it asked permission for `curl`, the first `curl` failed with exit code 6 and the retry succeeded with escalated network access, chat timer 2 minutes 42 seconds, rollout audit 2 minutes 51.7 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. All four runs complete a full `curl` fetch and land within a few characters of each
other, either `91,869` or `91,877` depending on whether the measurement used `wc -m`, `wc -c`, or
`perl` length. That spread reflects a byte-versus-character counting difference, not a retrieval
gap, and every run lands well past any plausible ten to one hundred kilobyte ceiling.

**Combined verdict: `H1` no across all four runs.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. Every run returns roughly `22,969` to `22,970` tokens intact, far past a `2,000`
token ceiling. The Extra High run's attempt to ground this estimate in an actual tokenizer failed
with a `ModuleNotFoundError` for `tiktoken`, so all four runs still rely on the `chars / 4` heuristic.

**Combined verdict: `H2` no across all four runs.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Mostly no. Three of the four runs, Medium, High, and Extra High, report no truncation event of any
kind, so there's nothing to evaluate for structure-awareness in those runs. The Light run is the one
exception, where the terminal display of an earlier command truncated but the location of that cutoff
relative to the document's Markdown structure unconfirmed from the saved response.

**Combined verdict: `H3` no for three runs with no truncation to inspect, indeterminate for the
Light run where a truncation event occurred but its structural position unconfirmed.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Yes. All four runs hit the same two-tier sandboxed DNS failure, an initial `curl` attempt that fails
with exit code 6, followed by an escalated-permission retry that succeeds. None of the four matched
`T1` runs need this retry step, and three of the four `T1` counterparts specifically cite a `web.run`
cache miss or truncated stdout preview instead, a failure mode `GPT-5.4` never hits on this track.
Final character counts converge with `T1` in every case, but the path to get there consistently
diverges.

**Combined verdict: `H4` yes across all four runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Mostly indeterminate. `Light` run shows only local re-inspection of the saved file through repeated
`perl` and file read calls, not live pagination of the web content, so that run reads as no. The
`Medium`, `High`, and `Extra High` runs all show similar local re-measurement activity, `wc -w`, `tail -c 50`,
repeated file reads, batched through `multi_tool_use.parallel`, but none of it touches the live
URL more than once, so content-level pagination isn't confirmed in any of them.

**Combined verdict: `H5` no for the `Light` run, indeterminate for `Medium`, `High`, and `Extra High`, since
repeated measurement calls target the saved local file rather than the live retrieval.**

---

## `H6`: Does the `docs-consumption` skill shift truncation disclosure and completeness reporting

Partially, with a consistent tool-choice signal but no configuration recommendation. `SKILL.md`
presence flagged in the rollout audit for every one of the four runs, and every run bypasses
`web` entirely in favor of direct `curl`, a pattern that holds across all four reasoning levels.
None of the four runs name the skill explicitly in their own reasoning, and none of them produce a
recommendation for working around the recurring sandbox DNS failure, the specific behavior this
experiment targets. `MEMORY.md` citations appear in every run, ranging from one to three per run, but
that citation behavior tracks the established measurement workflow rather than the skill itself.

**Combined verdict: `H6` partially across all four runs. The skill correlates with a consistent shift
away from `web.open` toward direct `curl`, but it never produces the sandbox workaround guidance this
experiment intends to detect.**

---

## Emergent Findings

1. **The `Searched the web` chat label appears in every run despite zero confirmed `web_search`
calls.** All four runs render this label at least once while the rollout audit only flags `curl`,
`perl`, `wc`, and related shell commands, consistent with the `tools_named` unreliability already
logged elsewhere in `T2`, and strong enough now to promote to a confirmed Friction Note candidate.

2. **The two-tier sandboxed DNS failure, then escalated retry, pattern holds without exception across
all four runs.** Per established methodology this counts as expected `T2` surface behavior rather
than direct `H4` evidence, but it's the mechanism driving the process divergence `H4` does capture.

3. **Character count measurement isn't standardized across runs.** `wc -m`, `wc -c`, and `perl` length
return different figures, `91,869` versus `91,877`, depending on whether the count treats the file as
bytes or UTF-8 characters. Worth adding a fixed measurement method to the workflow so future runs
don't need a per-run reconciliation step.

4. **Artifact naming collisions continue on this track.** `ec6_spec.md`, `ec6-spec.md`, and
`spec-ec6.md` variants recur across the four runs, and the High run directly reuses the `Medium` run's
path, echoing the contamination risk already flagged in the base `T2` `EC-6` cycle.

5. **No run at any reasoning level surfaces a sandbox workaround recommendation.** This holds from
`Light` through `Extra High`, which argues the gap isn't tied to reasoning depth, the skill simply never
prompts the agent toward proposing a fix for the DNS failure it hits every time.

6. **The `Extra High` run is the only one in this batch with an unrendered tool error.** Its attempt to
verify the token estimate against a local `tiktoken` install failed with a `ModuleNotFoundError`, and
while the agent reported it in passing, the command execution wasn't visible in the chat, required
rollout audit verification.

7.**In spite of loading the `SKILL.md`, agents' `MEMORY.md` citations indeterministic.** `Light` cites `L48`, `L14`, `L1-6`,
`Medium` cites `L41-49`, `L52-53`, `High` cites `L47-49`, and `Extra High` cites `L43-49`, `L1-15`. This
citation drift suggests the agents lean on `MEMORY.md` content that echoes the prompt and indirectly
reflects `SKILL.md` guidance, without ever naming `SKILL.md` explicitly or citing it from a consistent line range.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4 Light` | Pass | `PASS, curl_91877_chars + terminal_display_truncation_only + memory_citations_L48_L14_L1-6 + 45s` |
| `GPT-5.4 Medium` | Pass | `PASS, curl_91869_bytes + sandbox_exit_code_6_then_escalated + memory_citations_L41-49_L52-53 + 43s` |
| `GPT-5.4 High` | Pass | `PASS, curl_91877_chars + sandbox_exit_code_6_then_escalated + artifact_name_collision + contamination_risk + memory_citations_L47-49 + 1m19s` |
| `GPT-5.4 Extra High` | Pass | `PASS, curl_91869_utf8_chars + tiktoken_error_unrendered_reported + memory_citations_L43-49_1-15 + 2m2s` |
