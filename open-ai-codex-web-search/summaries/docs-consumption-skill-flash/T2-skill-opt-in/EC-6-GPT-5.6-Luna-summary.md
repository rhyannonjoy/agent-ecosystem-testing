# EC-6 GPT-5.6 Luna Flash Experiment Summary

## Test Conditions

|                 | **EC-6, GPT-5.6 Luna flash experiment** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed `91,869` to `91,877` characters depending on measurement tool, roughly `22,967` to `23,000` tokens |
| Surface         | `VS Code-Codex Extension` |
| Workspace       | Session scoped sandbox, `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing` writable, `/private/tmp` also writable |
| Track           | `T2` `VS Code-Codex` interpreted |
| Method          | `GPT` interpreted |
| Model           | `GPT-5.6 Luna` only |
| Runs            | 4 |
| Skill condition | `docs-consumption` skill present in the project root, `skill-opt-in` sub-track, `SKILL.md` exists in the workspace but the prompt doesn't mention it |
| Chunks returned | N/A |
| Extension version | `v26.707.41301` |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.6 Luna Extra High` | `91,869` via `wc -m`, byte count `91,877` via `wc -c` | ~`22,967` | No apparent truncation, the response ends cleanly with a complete bullet and a final newline | `— Notable exclusions with rationale (Appendix B).` | `exec_command` with `curl`, `wc`, `tail`, `web` and `web.open` weren't invoked | Yes, `/private/tmp/ec6-SPEC.md` 92KB, rollout json log 118KB | `SKILL.md` explicitly named by the agent, reasoning read "I'm using the docs-consumption skill because this is a URL-retrieval measurement test, I'll keep scope to `EC-6` and measure the raw curl response directly," report opened with `COMPLETE` per skill direction, 1 `MEMORY.md` citation at `L46-53` that the agent leans on for tool avoidance rather than the skill itself | Named `Test web retrieval`, asked permission for `curl` once, the first `curl` failed with exit code 6 from a sandboxed DNS resolution failure and the retry succeeded, chat timer 1 minute 51 seconds, rollout audit 1 minute 58 seconds |
| `GPT-5.6 Luna High` | `91,877` via a `perl` length check, characters and bytes matched | approximately `23,000`, `chars / 4` estimate | No, the agent reported an HTTP 200 status and a complete looking ending | `— Notable exclusions with rationale (Appendix B).` | `exec_command` shell with `curl` and `perl`, plus `wc` and `sed`, `web` and `web.open` weren't invoked | Yes, `/private/tmp/ec6-SPEC.md` 92KB, naming collision with the `Extra High` run's artifact, rollout json log 110KB | `SKILL.md` explicitly named by the agent, reasoning read "I'm using the docs-consumption skill because this is a URL-retrieval measurement test," report opened with `COMPLETE` per skill direction, 1 `MEMORY.md` citation at `L49` that references the prior run's identical character count directly | Named `Test web retrieval`, asked permission for `curl` once, the first `curl` failed with exit code 6 and the retry succeeded, a head request against the same URL surfaced response headers including an `accept-ranges: bytes` header the agent never reasoned about, chat timer 1 minute 31 seconds, rollout audit 1 minute 37 seconds |
| `GPT-5.6 Luna Medium` | `91,869` via `wc -m`, byte count `91,877` | ~`23,000` using a 4 characters per token heuristic | No apparent truncation, the response ends cleanly with a final newline | `— Notable exclusions with rationale (Appendix B).` | `exec_command` with `curl`, `wc`, `tail`, `web` and `web.open` weren't invoked | Yes, `/private/tmp/ec6_SPEC.md` 92KB, underscore naming variant distinct from the other three runs' hyphenated path, naming collision and contamination risk noted, rollout json log 88KB | `SKILL.md` explicitly named by the agent, reasoning read "I'm using the docs-consumption skill because this is a single-URL retrieval measurement test," report opened with `COMPLETE` per skill direction, that's where compliance ends, 2 `MEMORY.md` citations at `L2` and `L15` | Named `Measure raw SPEC.md retrieval`, asked permission for `curl` twice, the first `curl` failed with exit code 6 and the retry succeeded, the agent independently ran a head request against the source URL and surfaced the same `accept-ranges: bytes` header without engaging its meaning, chat timer 1 minute 3 seconds, rollout audit 1 minute 8.2 seconds |
| `GPT-5.6 Luna Light` | `91,877` via a `perl` length check | ~`22,970` using approximately 4 characters per token | No, the response ends cleanly at the document's final line | `— Notable exclusions with rationale (Appendix B).` | `exec_command` invoked shell `curl` only, `web` and `web.open` weren't invoked | Yes, `/private/tmp/ec6-SPEC.md` 92KB, naming collision and contamination risk noted, rollout json log 79KB | `SKILL.md` explicitly named by the agent, reasoning read "I'm using the docs-consumption skill because this is a URL-retrieval measurement test," report opened and closed with `COMPLETE`, the only run in this batch with no `MEMORY.md` citation despite carrying forward the same `curl` only tool avoidance behavior the other three runs show | Named `Test web retrieval EC-6`, asked permission for `curl` once, the first `curl` failed with exit code 6 and the retry succeeded, chat timer 42 seconds, rollout audit 45.2 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. All four runs complete a full `curl` fetch and land on the same figures, `91,869`
characters and `91,877` bytes depending on the measurement tool, with no spread across reasoning
levels. Every run lands well past any plausible ten to one hundred kilobyte ceiling.

**Combined verdict: `H1` no across all four runs.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. `Light` and `Extra High` return roughly `22,967` to `22,970` tokens, `Medium` and
`High` round to approximately `23,000`, and every run still relies on a `chars / 4` heuristic rather
than a real tokenizer. All four figures sit far past a `2,000` token ceiling.

**Combined verdict: `H2` no across all four runs.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Indeterminate rather than no. None of the four runs report a truncation event of any kind, so none
of them offer a boundary to evaluate for structure awareness. Calling this hypothesis no would
overstate what these runs show, since a hypothesis about where truncation falls isn't assessable
when truncation never occurs.

**Combined verdict: `H3` indeterminate across all four runs, since no run produced a truncation event
to examine.**

---

## `H4`: Surface context, `T2` `VS Code-Codex Extension` changes retrieval behavior against `T1`

Untested. No `T1` or `T2` baseline exists yet for `GPT-5.6 Luna` in this test cycle, so a surface
comparison against Codex Desktop isn't possible this round.

**Combined verdict: `H4` untested across all four runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially across all four runs. Every run performs one direct `curl` fetch against the live URL,
then follows that fetch with an extended local verification chain against the saved artifact,
repeated `wc`, `tail`, `perl`, and `sed` calls that recheck character counts, byte counts, and tail
content multiple times. None of that chain touches the live URL more than once or twice, so none of
the runs confirms content level pagination against the live source, but the sequential multi tool
structure of the local checks keeps every run from reading as a single clean measurement path.

**Combined verdict: `H5` partially across all four runs.**

---

## `H6`: Does the `docs-consumption` skill shift truncation disclosure and completeness reporting

Partially, with a signal that weakens rather than strengthens as reasoning level drops. Every run
bypasses `web` entirely in favor of direct `curl`, and every run's report opens with `COMPLETE` per
the skill's formatting instruction. `Extra High`, `High`, and `Medium` all cite `MEMORY.md` alongside
the skill, and `Medium`'s own justification leans on that citation rather than the skill itself,
which raises a memory echo risk since neither the prompt nor the skill specifies raw `curl`, `wc`, or
`tail` precision. `Light` is the only run with no `MEMORY.md` citation at all, yet it still carries
forward the same `curl` only avoidance pattern, which suggests the behavior may be generalizing into
a default policy rather than getting freshly retrieved each run. Despite the skill's explicit request
in protocol step seven to recommend a fix when one exists, no run at any reasoning level proposes a
fix for the recurring sandboxed DNS failure, and no run engages with the `accept-ranges: bytes`
header that turns up in the two runs where header data is available.

**Combined verdict: `H6` partially across all four runs. The skill correlates with a consistent shift
away from `web` toward direct `curl` and a `COMPLETE` first report structure, but it doesn't produce
deeper failure examination or fix recommendations at any reasoning level, and its effect is hard to
separate from `MEMORY.md` influence in three of the four runs.**

---

## Emergent Findings

1. **The `Searched the web` chat label appears in every run despite zero confirmed `web_search`
calls.** All four runs render this label at least once while the rollout audit only cites `curl`,
`wc`, `tail`, `perl`, `sed`, and related shell commands, consistent with the `tools_named`
unreliability already logged elsewhere in `T2`.

2. **The two tier sandboxed DNS failure, then escalated retry, pattern holds without exception across
all four runs.** Per established methodology this counts as expected `T2` surface behavior rather
than direct `H4` evidence, but it's the mechanism driving the tool chain divergence `H5` captures.

3. **Artifact naming carries a hyphen versus underscore inconsistency on top of the collision already
flagged in each individual run.** `Extra High`, `High`, and `Light` all write to
`/private/tmp/ec6-SPEC.md`, while `Medium` alone writes to `/private/tmp/ec6_SPEC.md`, so the batch
produces two distinct naming conventions layered on top of the repeated overwrite risk.

4. **`MEMORY.md` citation behavior doesn't track reasoning level in a clean pattern.** `Extra High`
cites `L46-53`, `High` cites `L49` and references the prior run's character count directly, `Medium`
cites `L2` and `L15`, and `Light` cites nothing at all. `Light`'s absence of any citation, paired
with its continued `curl` only behavior, is the strongest single data point in this batch for
suspecting the avoidance pattern has become a default policy rather than a fresh per run retrieval.

5. **Test naming drifts across every run with no correlation to reasoning level.** `Test web
retrieval`, `Test web retrieval` again, `Measure raw SPEC.md retrieval`, and `Test web retrieval
EC-6` all appear across the four runs, echoing the naming inconsistency already logged on this
track.

6. **The `accept-ranges: bytes` header appears in both runs where header data is available, `High`
and `Medium`, and neither run engages with what it implies for `H1`.** `Medium` is the more notable
case since the agent ran the head request itself as a deliberate step and displayed the header in
chat, then moved straight to a completeness verdict without connecting it to the truncation question
at all.

7. **Chat timer duration scales down cleanly from `Extra High` to `Light`, 1 minute 51 seconds, 1
minute 31 seconds, 1 minute 3 seconds, and 42 seconds, but report depth and failure disclosure
quality stay flat across the same range.** Reasoning level effort appears to scale run time without
scaling skill protocol compliance.

8. **Command count claimed in chat consistently exceeds the rollout audit's count across all four
runs**, roughly ten against six for `Extra High`, eight against five for `High`, six against five for
`Medium`, and seven against five for `Light`. This reinforces the previously logged undercounting of
agent activity in the chat panel relative to the rollout log.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.6 Luna Extra High` | Pass | `PASS, curl_91869_chars + sandbox_exit_code_6_then_escalated + artifact_name_collision + memory_citation_L46-53 + 1m51s` |
| `GPT-5.6 Luna High` | Pass | `PASS, curl_91877_chars + sandbox_exit_code_6_then_escalated + accept_ranges_header_unused + artifact_name_collision + memory_citation_L49 + 1m31s` |
| `GPT-5.6 Luna Medium` | Pass | `PASS, curl_91869_chars + artifact_name_variant_underscore + accept_ranges_header_unused + memory_citations_L2_L15 + 1m3s` |
| `GPT-5.6 Luna Light` | Pass | `PASS, curl_91877_chars + sandbox_exit_code_6_then_escalated + artifact_name_collision + no_memory_citation + 42s` |
