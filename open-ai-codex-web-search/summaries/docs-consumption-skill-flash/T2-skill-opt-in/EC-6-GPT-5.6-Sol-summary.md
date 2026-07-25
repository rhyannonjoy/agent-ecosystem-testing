# EC-6 GPT-5.6 Sol Flash Experiment Summary

## Test Conditions

|                 | **EC-6, GPT-5.6 Sol flash experiment** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed `91,869` characters and `91,877` bytes in every run, roughly `22,967` to `22,970` tokens |
| Surface         | `VS Code-Codex Extension` |
| Workspace       | Session scoped sandbox, `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing` writable, `/private/tmp` also writable |
| Track           | `T2` `VS Code-Codex` interpreted |
| Method          | `GPT` interpreted |
| Model           | `GPT-5.6 Sol` only |
| Runs            | 5 |
| Skill condition | `docs-consumption` skill present in the project root, `skill-opt-in` sub-track, `SKILL.md` exists in the workspace but the prompt doesn't mention it |
| Chunks returned | N/A |
| Extension version | `v26.707.41301` |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.6 Sol Ultra` | `91,869` characters, `91,877` bytes, both figures match the `content-length` header exactly | Approximately `22,967` tokens using a four characters per token heuristic, the agent itself notes actual tokenizer results may differ | No, `HTTP/2 200` returns and `content-length` matches the saved body's byte count exactly, the document ends coherently with a final newline | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command` and `shell`, the sandboxed attempt fails with `curl: (6) Could not resolve host`, the approved retry succeeds; local inspection uses `wc`, `perl`, `rg`, `sed`, `tail`, and `nl`; `web`, `web.open`, and Browser aren't invoked; a preliminary `sed` lookup targets the wrong skill file path and fails before making any network request | Yes, the agent saves `/private/tmp/ec6-spec-headers.txt` at 870 bytes and `/private/tmp/ec6-spec.md` at about 92 KB, this collides with the file name three other runs use, the rollout json log runs 180 KB | `SKILL.md` named explicitly, the agent reasons "I'm using the `docs-consumption` skill because this is a single-URL retrieval measurement," opens the report with `COMPLETE`, and voluntarily discloses its own wrong-path lookup rather than hiding it, citations pair `MEMORY.md` `L43` through `L54` with `skills/single-url-retrieval-measurement/SKILL.md` `L23` through `L49` | Named `Measure raw SPEC.md retrieval`, the agent asks permission for `curl` once, the chat timer runs 3 minutes 28 seconds and the rollout audit runs 3 minutes 36 point 2 seconds, the command count claim reaches about 17 while the audit cites 10, the widest gap in this batch |
| `GPT-5.6 Sol Extra High` | `91,869` characters, `91,877` bytes | Approximately `22,967` tokens using the four characters per token heuristic | No, the agent cites `HTTP/2 200`, a `content-length` of `91877` that matches the saved body exactly, a meaningful document ending, and no unclosed fenced code blocks | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command`, the sandboxed attempt fails with `curl: (6) Could not resolve host`, the approved retry succeeds; local measurement uses `wc`, `perl`, `rg`, `tail`, and `sed`; the agent bypasses `web` even though the chat panel renders `searched the web`; `web.open` isn't invoked; no other URL or retrieval test runs | Yes, the agent saves `/private/tmp/ec6-spec-md-headers.txt` at 872 bytes and `/private/tmp/ec6-spec-md-response.md` at about 92 KB, this is the one run in the batch that avoids the shared `ec6-spec.md` file name, the rollout json log runs 152 KB | `SKILL.md` named explicitly, the agent reasons "I'm using the `docs-consumption` skill because this is a single-URL retrieval measurement," opens the report with `COMPLETE, EC-6`, and claims "the protocol calls for one direct raw fetch saved before measurement," a line that doesn't match `SKILL.md`'s actual wording and most likely borrows from `MEMORY.md` instead, citations pair `skills/single-url-retrieval-measurement/SKILL.md` `L32` through `L45` and `L103` through `L110` with `MEMORY.md` `L50` through `L58` | Named `Measure raw GitHub retrieval`, the agent asks permission for `curl` once, the chat timer runs 2 minutes 50 seconds and the rollout audit runs 2 minutes 59 point 4 seconds, the command count claim reaches about 13 while the audit cites 8, and this run's headers show `x-cache: MISS` where every other run with header data shows `x-cache: HIT` |
| `GPT-5.6 Sol High` | `91,869` characters, `91,877` bytes | Approximately `22,970` tokens using the four characters per token heuristic | No, the retrieved body matches the `content-length` of `91,877` bytes and ends cleanly | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command`, the sandboxed attempt fails with `curl: (6) Could not resolve host`, the approved retry succeeds with exit code 0; local measurement uses `wc`, `perl`, `rg`, `sed`, `tail`, and `od`; a `perl` command crashes with `zsh:1: unknown file attribute: 8` and the agent quietly switches to `od` rather than disclosing the crash; `web` and `web.open` aren't invoked | Yes, the agent saves `/private/tmp/ec6-headers.txt` at 868 bytes and `/private/tmp/ec6-spec.md` at about 92 KB, this collides with the file name three other runs use, the rollout json log runs 140 KB | `SKILL.md` named explicitly, the agent reasons "I'm using the `docs-consumption` skill because this is a single-URL retrieval measurement," states "the `docs-consumption` skill governed the reporting procedure," and claims "the skill's procedure points to a saved raw-body fetch for exact Unicode character and byte measurements," a line `SKILL.md` doesn't actually contain and most likely borrows from `MEMORY.md` instead, citations pair `skills/single-url-retrieval-measurement/SKILL.md` `L30` through `L49` with `MEMORY.md` `L41` through `L54` | Named `Test web retrieval EC-6`, the agent's permission request for `curl` reads less confidently than in other runs, the chat timer runs 1 minute 38 seconds and the rollout audit runs 1 minute 46 point 6 seconds, the command count claim reaches about 10 while the audit cites 8, this is the only run in the batch where a tool crash goes unreported in the final summary |
| `GPT-5.6 Sol Medium` | `91,869` characters, `91,877` bytes | Approximately `22,967` tokens using the four characters per token heuristic | No, the response returns `HTTP 200`, its `91,877` byte body matches `content-length: 91877`, and it ends cleanly | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command`, the sandboxed attempt fails with `curl: (6) Could not resolve host`, the approved retry succeeds; local measurement uses `wc`, `perl`, `ruby`, `rg`, `tail`, and `sed`; the agent bypasses `web` even though the chat panel renders `searched the web`; `web.open` isn't invoked | Yes, the agent saves `/private/tmp/ec6-headers.txt` at 869 bytes and `/private/tmp/ec6-spec.md` at about 92 KB, this collides with the file name three other runs use, the rollout json log runs 132 KB | `SKILL.md` named explicitly, the agent reasons "I'm using the `docs-consumption` skill because this is a single-URL retrieval measurement with explicit completeness and tooling fields," opens the report with `COMPLETE, EC-6`, and that's where compliance ends, citations pair `skills/single-url-retrieval-measurement/SKILL.md` `L21` through `L72` with `MEMORY.md` `L41` through `L58` | Named `Measure web retrieval`, the agent asks permission for `curl` once, the chat timer runs 1 minute 22 seconds and the rollout audit runs 1 minute 32 seconds, the command count claim reaches about 8 while the audit cites 7 |
| `GPT-5.6 Sol Light` | `91,869` characters, `91,877` bytes | Approximately `22,967` tokens using the four characters per token heuristic | No, the response ends coherently, includes a final newline, and shows no clipping or truncation markers | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command`, the sandboxed attempt fails with `Could not resolve host: raw.githubusercontent.com`, the approved retry succeeds; local measurement uses `wc`, `tail`, `perl`, and `file`; `web` and `web.open` aren't invoked | Yes, the agent saves the response at `/tmp/ec6-spec.md`, this run doesn't log a separate file size or rollout log size | `SKILL.md` named explicitly, the agent reasons "I'm using the `docs-consumption` skill because this is a controlled single-URL retrieval measurement," opens the report with `COMPLETE`, citations cite `MEMORY.md` three separate times at `L47` through `L50`, `L39` through `L43`, and `L10` through `L15`, with no `skills/single-url-retrieval-measurement/SKILL.md` citation this run | Named `Test web retrieval EC-6`, the chat timer runs 1 minute 18 seconds, this run doesn't log a separate rollout audit duration or a command count comparison |

---

## `H1`: Truncation based on a fixed character ceiling

Not supported. Every run completes a full `curl` fetch and lands on the same figures, `91,869`
characters and `91,877` bytes, with no spread across reasoning levels. Every run lands well past
any plausible ten to one hundred kilobyte ceiling, and the `content-length` header independently
confirms the same byte count in every run that captures headers.

**Combined verdict: `H1` no across all five runs.**

---

## `H2`: Truncation based on a fixed token ceiling

Not supported. Every run estimates between `22,967` and `22,970` tokens using a `chars / 4`
heuristic rather than a real tokenizer, and every figure sits far past a `2,000` token ceiling.

**Combined verdict: `H2` no across all five runs.**

---

## `H3`: Truncation that respects Markdown structure

Indeterminate rather than no. None of the five runs reports a truncation event of any kind, so
none of them offers a boundary to evaluate for structure awareness. Calling this hypothesis no
would overstate what these runs show, since a hypothesis about where truncation falls isn't
assessable when truncation never occurs.

**Combined verdict: `H3` indeterminate across all five runs, since no run produces a truncation
event to examine.**

---

## `H4`: Surface context affecting retrieval behavior

Untested. No `T1` or `T2` baseline exists yet for `GPT-5.6 Sol` in this test cycle, so a surface
comparison against Codex Desktop isn't possible this round.

**Combined verdict: `H4` untested across all five runs.**

---

## `H5`: Automatic chunking or pagination behavior

Partially, with one exception. `GPT-5.6 Sol Light` performs a single local read pass, one `Read
files` event followed by a battery of measurement commands, and never repeats that read, so it
stays no. Every other run in the batch, `Medium`, `High`, `Extra High`, and `Ultra`, triggers a
second or third distinct `Read files` event over the same saved artifact. The mechanism driving
that repetition differs by run: `Medium`, `Extra High`, and `Ultra` re-read the file to verify
completeness before committing to a `COMPLETE` label, while `High` re-reads after a `perl` command
crashes and the agent falls back to `od`. None of the five runs touches the live URL more than
once, so none of them confirms content level pagination against the source itself, but the
repeated local read pattern in four of five runs keeps this hypothesis from landing on a flat no.

**Combined verdict: `H5` no for `Light`, partially for `Medium`, `High`, `Extra High`, and `Ultra`.
The repeat read pattern tracks reasoning level more cleanly than it tracks the skill condition, a
non-skill baseline at matching reasoning levels would help confirm that.**

---

## `H6`: Skill influence on disclosure and completeness reporting

Partially, and the signal splits into two layers worth keeping separate. At the surface layer,
every run bypasses `web` in favor of direct `curl`, every run names `docs-consumption` explicitly,
and every run's report opens with `COMPLETE` per the skill's formatting instruction, that layer
holds without exception across all five runs. At the protocol layer, none of the five runs
exercises the skill's substantive branching logic. No run reaches a `PARTIAL` or `UNVERIFIABLE`
label, no run recommends a fix for the recurring sandboxed DNS failure despite the skill's step
seven instruction to do so, and `High` actively violates the skill's rule six by quietly reframing
a `perl` crash as a clean `COMPLETE` result instead of disclosing it.

The citation pattern reinforces this split. `Medium`, `High`, `Extra High`, and `Ultra` all pair a
`skills/single-url-retrieval-measurement/SKILL.md` citation with a `MEMORY.md` citation in the same
breath, and `High` and `Extra High` both misattribute `MEMORY.md` procedural language directly to
`SKILL.md`. Across the broader run set beyond this batch, a `SKILL.md` citation almost never
appears without a paired `MEMORY.md` citation, only once by count. That pattern points toward the
model treating `SKILL.md` as a confirming reference for a memory-driven script rather than as a
protocol it actually consults on its own terms.

**Combined verdict: `H6` partially across all five runs. The skill correlates with a consistent
surface shift toward `curl` and a `COMPLETE` first report structure, but it doesn't produce deeper
failure examination, fix recommendations, or independent citation behavior at any reasoning level,
and its effect is hard to separate from `MEMORY.md` influence in four of the five runs.**

---

## Emergent Findings

1. **The `Searched the web` chat label appears in every run despite zero confirmed `web_search`
calls.** All five runs render this label at least once while the rollout audit only cites `curl`,
`wc`, `tail`, `perl`, `ruby`, `rg`, `sed`, `od`, `nl`, and `file`, consistent with the `tools_named`
unreliability already logged elsewhere in `T2`.

2. **The two tier sandboxed DNS failure, then escalated retry, pattern holds without exception
across all five runs.** Per established methodology this counts as expected `T2` surface behavior
rather than direct `H4` evidence, but it's the mechanism that opens every run's tool chain.

3. **Artifact naming collision affects four of five runs.** `Light`, `Medium`, `High`, and `Ultra`
all write the fetched body to `/tmp/ec6-spec.md` or `/private/tmp/ec6-spec.md`, so a repeated
overwrite risk carries across most of the batch. `Extra High` is the only run that picks a distinct
filename, `ec6-spec-md-response.md`, and avoids the collision entirely.

4. **Cache state varies across the batch and looks like an uncontrolled variable.** `Medium`,
`High`, and `Ultra` all show `x-cache: HIT`, while `Extra High` shows `x-cache: MISS`, so cache
state doesn't track reasoning level and is worth logging explicitly per run going forward.

5. **`MEMORY.md` and `SKILL.md` citation pairing holds in every run from `Medium` onward.** `Light`
is the only run that cites `MEMORY.md` without any `skills/single-url-retrieval-measurement/SKILL.md`
citation alongside it, which lines up with `Light`'s otherwise minimal skill engagement.

6. **Command count claimed in chat consistently exceeds the rollout audit's count, and the gap
widens as reasoning level climbs.** `Medium` claims about 8 against an audited 7, `High` claims
about 10 against an audited 8, `Extra High` claims about 13 against an audited 8, and `Ultra`
claims about 17 against an audited 10.

7. **Chat timer duration scales up cleanly from `Light` to `Ultra`, 1 minute 18 seconds, 1 minute
22 seconds, 1 minute 38 seconds, 2 minutes 50 seconds, and 3 minutes 28 seconds, but report depth
and failure disclosure quality don't scale with it in a consistent way.** `High` actually loses
ground on failure disclosure relative to `Light` despite running longer, since `High` is the only
run in the batch that hides a tool crash from its own report.

8. **Test naming drifts across every run with no correlation to reasoning level.** `Test web retrieval EC-6`,
`Measure web retrieval`, `Test web retrieval EC-6` again, `Measure raw GitHub retrieval`, and
`Measure raw SPEC.md retrieval` all appear across the five runs.

9. **Repeated local read behavior, the `H5` finding, appears in every run except `Light` and
correlates with reasoning level more cleanly than skill presence does.** The mechanism behind the
repetition still differs by run: verification driven in `Medium`, `Extra High`, and `Ultra`, versus
error recovery driven in `High`, so the pattern isn't uniform even where it appears.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.6 Sol Ultra` | Pass | `PASS, curl_91869_chars_91877_bytes, sandboxed_dns_fail_then_escalated, repeat_read_verification_driven, self_reported_tool_path_failure, artifact_name_collision, skill_memory_citation_paired, chat_timer_208_seconds, audit_216_seconds` |
| `GPT-5.6 Sol Extra High` | Pass | `PASS, curl_91869_chars_91877_bytes, sandboxed_dns_fail_then_escalated, repeat_read_verification_driven, cache_miss, artifact_name_unique, skill_memory_citation_paired, chat_timer_170_seconds, audit_179_seconds` |
| `GPT-5.6 Sol High` | Pass | `PASS, curl_91869_chars_91877_bytes, sandboxed_dns_fail_then_escalated, repeat_read_error_recovery_driven, perl_crash_undisclosed, artifact_name_collision, skill_memory_citation_paired, chat_timer_98_seconds, audit_106_seconds` |
| `GPT-5.6 Sol Medium` | Pass | `PASS, curl_91869_chars_91877_bytes, sandboxed_dns_fail_then_escalated, repeat_read_verification_driven, artifact_name_collision, skill_memory_citation_paired, chat_timer_82_seconds, audit_92_seconds` |
| `GPT-5.6 Sol Light` | Pass | `PASS, curl_91869_chars_91877_bytes, sandboxed_dns_fail_then_escalated, single_read_pass, no_skill_path_citation, chat_timer_78_seconds` |
