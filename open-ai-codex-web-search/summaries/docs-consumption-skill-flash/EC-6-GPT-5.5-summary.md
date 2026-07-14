# EC-6 GPT-5.5 Flash Experiment Summary

## Test Conditions

|                 | **EC-6, GPT-5.5 flash experiment** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed `91,869` to `91,877` characters depending on measurement tool, roughly `22,967` to `23,000` tokens |
| Surface         | `VS Code-Codex Extension` |
| Workspace       | Session scoped sandbox, `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing` writable, `/private/tmp` also writable |
| Track           | `T2` `VS Code-Codex` interpreted |
| Method          | `GPT` interpreted |
| Model           | `GPT-5.5` only |
| Runs            | 4 |
| Skill condition | `docs-consumption` skill present in the project root, `skill-opt-in` sub-track, `SKILL.md` exists in the workspace but the prompt doesn't mention it |
| Chunks returned | N/A |
| Extension version | `v26.707.41301` |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.5 Light` | 91,869 via `wc -m`, byte count 91,877 via `wc -c` | ~22,967 | No apparent truncation, code fences balanced with two total fence markers opening at `L432` and closing at `L450` | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` with `curl`, `wc`, `tail`, `rg`, and `perl`, `web` and `web` weren't invoked | Yes, `/private/tmp/ec6_SPEC.md` 92KB, rollout json log 109KB | `SKILL.md` explicitly named by the agent, reasoning read "I'll keep this tightly scoped to `EC-6` and use the project's docs-consumption skill so the measurements line up with your retrieval-test format," report opened with `COMPLETE` per skill direction, 2 `MEMORY.md` citations at `L15-23` and `L49` | named `Test web retrieval EC-6`, asked permission for `curl` twice, the first `curl` failed with exit code 6 from a sandboxed DNS resolution failure and the retry succeeded, chat timer 1 minute 1 second, rollout audit 1 minute 8.8 seconds |
| `GPT-5.5 Medium` | 91,869 via `wc -m`, byte count 91,877 | ~22,967 | No apparent truncation, the file ends cleanly on the Appendix B bullet with a final newline | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` with `curl`, `wc`, `tail`, `perl`, `rg`, and `sed`, `web` and `web` weren't invoked | Yes, `/private/tmp/ec6_SPEC.md` 92KB, naming collision with the `Light` run's artifact, rollout json log 112KB | `SKILL.md` explicitly named by the agent, reasoning read "I'll keep this scoped to `EC-6` only and use the local docs-consumption skill because this is exactly its retrieval-measurement shape," report opened with `COMPLETE` per skill direction, 1 `MEMORY.md` citation at `L49`, the agent's own justification leaned on that citation rather than the skill | named `Measure raw SPEC.md retrieval`, asked permission for `curl` once, the first `curl` failed with exit code 6 and the retry succeeded, chat timer 1 minute 9 seconds, rollout audit 1 minute 16.3 seconds |
| `GPT-5.5 High` | 91,869 via `wc -m`, byte count 91,877 via `wc -c` | approximately 23,000 | No, the agent reported it saw no cutoff marker, mid-line ending, or incomplete final section | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` with `curl`, `wc`, `tail`, and `perl`, `web` and `web` weren't invoked | Yes, `/private/tmp/ec6_SPEC.md` 92KB, identical path to the `Light` and `Medium` artifacts, rollout json log 112KB | `SKILL.md` explicitly named by the agent, reasoning read "I'll use the docs-consumption skill because this is exactly a retrieval-behavior measurement, and I'll keep the run scoped to the single URL and test ID you gave," report opened with `COMPLETE` per skill direction, the only run in this batch with no `MEMORY.md` citation | named `Test web retrieval EC-6`, asked permission for `curl` once, the first `curl` failed with exit code 6 and the retry succeeded, a local quoting error surfaced during measurement and the agent reran only the tail check without refetching, chat timer 1 minute 19 seconds, rollout audit 1 minute 24.6 seconds |
| `GPT-5.5 Extra High` | 91,869 via `wc -m`, byte count 91,877 via `wc -c` | approximately 23,000, `chars / 4` estimate | No apparent truncation, the file ends cleanly at `L1722` with the final changelog bullet, two fenced code block markers found at `L432` and `L450` | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` with `curl`, `wc`, `tail`, `perl`, `rg`, `file`, and `nl`, `web` and `web` weren't invoked | Yes, `/private/tmp/ec6_SPEC.md` 92KB, same path as the prior three runs' artifacts, rollout json log 128KB | `SKILL.md` explicitly named by the agent, reasoning read "I'll use the docs-consumption retrieval workflow for this single URL only, since your requested report fields match that skill," report opened with `COMPLETE` per skill direction, but the sandbox DNS failure got flattened into one sentence and an unmatched quote error at exit code 1 went unreported, 2 `MEMORY.md` citations at `L6-15` and `L49` | named `Measure web retrieval EC-6`, asked permission for `curl` once, the first `curl` failed with exit code 6 and the retry succeeded, chat timer 1 minute 52 seconds, rollout audit 2 minutes 0.6 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. All four runs complete a full `curl` fetch and land on the same figures, `91,869`
characters via `wc -m` and `91,877` bytes via `wc -c`, with no spread between reasoning levels the
way the `GPT-5.4` batch showed. Every run lands well past any plausible ten to one hundred kilobyte
ceiling.

**Combined verdict: `H1` no across all four runs.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. `Light` and `Medium` return roughly `22,967` tokens, `High` and `Extra High` round to
approximately `23,000`, and every run still relies on the `chars / 4` heuristic rather than a real
tokenizer. All four figures sit far past a `2,000` token ceiling.

**Combined verdict: `H2` no across all four runs.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Untested rather than no. None of the four runs report a truncation event of any kind, so none of
them give a boundary to evaluate for structure-awareness. This batch is cleaner than the `GPT-5.4`
batch, where the `Light` run's terminal display truncation at least offered one partial data point.
Calling this hypothesis "no" would overstate what these runs actually show, since a hypothesis about
where truncation falls not assessible when truncation never occurs.

**Combined verdict: `H3` indeterminate across all four runs, since no run produced a truncation event
to examine.**

---

## `H4`: Surface context, `T2` `VS Code-Codex Extension` changes retrieval behavior against `T1`

Mixed. `Medium` and `High` show the clearest shift, both escalate straight to `curl` and avoid
`web`'s display truncation entirely, while their `T1` counterparts hit a `web.run` cache miss or
a truncated terminal preview instead. `Light` and `Extra High` also escalate to `curl` and avoid
`web`, but their final character, byte, and token counts converge with `T1` closely enough that
the difference reads more as a tooling and verification style shift than a change in retrieval
outcome. All four runs hit the same two tier sandboxed DNS failure pattern, an initial `curl` attempt
that fails with exit code 6, followed by an escalated retry that succeeds, a step none of the matched
`T1` runs need.

**Combined verdict: `H4` yes for `Medium` and `High`, partially for `Light` and `Extra High`.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially across all four runs. Every run performs a single direct `curl` fetch against the live URL,
then follows that fetch with an extended local verification chain against the saved file, repeated
`wc`, `tail`, `perl`, `rg`, `file`, and `nl` calls that recheck character counts, byte counts, and
tail content several times over. None of that chain touches the live URL more than once, so content
level pagination against the live source isn't confirmed in any run, but the sequential, multiple
probe structure of the local checks keeps every run from reading as a clean single measurement path.

**Combined verdict: `H5` partially across all four runs.**

---

## `H6`: Does the `docs-consumption` skill shift truncation disclosure and completeness reporting

Partially, with a stronger and more explicit skill signal than the `GPT-5.4` batch showed. Every run
bypasses `web` entirely in favor of direct `curl`, and every run's report opens with `COMPLETE` per
the skill's formatting instruction. `Light` and `Medium` load `SKILL.md` and name it explicitly in
their own reasoning, and `High` and `Extra High` do the same, so naming behavior is consistent across
this batch rather than split by reasoning level. The `Medium` run's own stated justification leans on
a `MEMORY.md` citation rather than the skill itself, which raises a memory echo risk, since neither
the prompt nor the skill specifies raw `curl` or `wc` and `tail` precision. The `High` run is the only
one in the batch with no `MEMORY.md` citation at all, which makes it the cleanest single data point
for isolating a skill effect from a memory effect. Despite the skill's failure examination language,
the sandbox DNS failure gets flattened into one clean sentence in every run that hits it, and the
`Extra High` run's unmatched quote error at exit code 1 goes unreported entirely, while `High`
uniquely self-corrects a quoting error rather than omitting it.

**Combined verdict: `H6` partially across all four runs. The skill correlates with a consistent shift
away from `web` toward direct `curl` and a `COMPLETE` first report structure, but it doesn't
produce deeper or more consistent failure examination, and its effect is harder to separate from
`MEMORY.md` influence in the `Medium` run.**

---

## Emergent Findings

1. **The `Searched the web` chat label appears in every run despite zero confirmed `web_search`
calls.** All four runs render this label at least once while the rollout audit only flags `curl`,
`wc`, `tail`, `perl`, `rg`, and related shell commands, consistent with the `tools_named`
unreliability already logged elsewhere in `T2`.

2. **The two tier sandboxed DNS failure, then escalated retry, pattern holds without exception across
all four runs.** Per established methodology this counts as expected `T2` surface behavior rather
than direct `H4` evidence, but it's the mechanism driving the process divergence `H4` does capture.

3. **Artifact naming collision compounds across the whole cycle rather than resetting per run.** All
four runs claim to write and save `/private/tmp/ec6_SPEC.md`, so despite four separate claimed
artifacts, only two look distinct once the repeated overwrites and the contamination risk already
flagged in each individual run summary.

4. **`MEMORY.md` citation behavior doesn't track reasoning level in a clean pattern.** `Light` cites
`L15-23` and `L49`, `Medium` cites `L49` alone, `High` cites nothing, and `Extra High` cites `L6-15`
and `L49`. `High`'s absence of any citation, paired with its explicit skill naming, makes it the
strongest single run for separating skill influence from memory influence.

5. **Test naming drifts across every run with no correlation to reasoning level.** `Test web retrieval EC-6`,
`Measure raw SPEC.md retrieval`, `Test web retrieval EC-6` again, and `Measure web retrieval EC-6` all appear
across the four runs, echoing the naming inconsistency already logged on this track.

6. **Error disclosure quality diverges sharply between `High` and `Extra High` despite both explicitly
naming the skill.** `High` surfaces and self-corrects a local quoting error without a refetch,
while `Extra High` never reports its own unmatched quote error at exit code 1, showing that explicit
skill engagement doesn't guarantee complete failure reporting even within the same sub-track.

7. **Extension version stayed fixed at `v26.707.41301` across the batch**, so version drift's
ruled out as a factor in the behavioral differences observed between reasoning levels.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.5 Light` | Pass | `PASS, curl_91869_chars + sandbox_exit_code_6_then_escalated + memory_citations_L15-23_L49 + 1m1s` |
| `GPT-5.5 Medium` | Pass | `PASS, curl_91869_chars + artifact_name_collision + memory_citation_L49 + 1m9s` |
| `GPT-5.5 High` | Pass | `PASS, curl_91869_chars + sandbox_exit_code_6_then_escalated + quoting_error_self_corrected + artifact_name_collision + no_memory_citation + 1m19s` |
| `GPT-5.5 Extra High` | Pass | `PASS, curl_91869_chars + artifact_name_collision + unreported_exit_code_1_error + memory_citations_L6-15_L49 + 1m52s` |
