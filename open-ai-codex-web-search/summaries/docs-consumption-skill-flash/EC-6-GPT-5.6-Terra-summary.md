# EC-6 GPT-5.6 Terra Flash Experiment Summary

## Test Conditions

|                 | **EC-6, GPT-5.6 Terra flash experiment** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed `91,869` characters and `91,877` bytes in every run, roughly `22,967` to `22,970` tokens |
| Surface         | `VS Code-Codex Extension` |
| Workspace       | Session scoped sandbox, `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing` writable, `/private/tmp` also writable |
| Track           | `T2` `VS Code-Codex` interpreted |
| Method          | `GPT` interpreted |
| Model           | `GPT-5.6 Terra` only |
| Runs            | 5 |
| Skill condition | `docs-consumption` skill present in the project root, `skill-opt-in` sub-track, `SKILL.md` exists in the workspace but the prompt doesn't mention it |
| Chunks returned | N/A |
| Extension version | `v26.707.41301` |

---

## Original Test Prompt

Every run receives the same prompt, and it's worth reproducing in full here since several
findings below turn on how much of it each run actually engages with.

```
I'm testing Codex's web retrieval capabilities for the Agent Ecosystem Testing project.

To prevent testing methodology contamination, only run this test and don't proceed to any other tests.
Fetch this URL directly:
https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md

Then report back:
1. **Total character count** of the response you received
2. **Estimated token count**
3. **Whether any content appears truncated** (yes/no, and where if truncated)
4. **Last 50 characters** of the response (verbatim, to verify the cutoff point)
5. **Markdown formatting assessment** - is it complete? Are code blocks closed properly?
6. **Model's perceived completeness** - does it seem like you got the full content?
7. **Tool visibility** - report any tool names or method identifiers visible in your tool results,
   including whether web, web.open, curl, or any other tool was invoked
8. **Surface awareness** - do you have access to a local workspace or filesystem?

Test ID: EC-6
Expected size: ~60KB
This is for empirical documentation of retrieval behavior across deployment surfaces.
```

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.6 Terra Ultra` | `91,869` characters, `91,877` bytes, both figures match the `content-length` header exactly | Approximately `22,970` tokens using a four characters per token heuristic | No, the successful response reaches its declared content length and ends cleanly, an earlier sandboxed `curl` attempt fails DNS resolution and returns zero content, and the agent retries that same fetch instead of treating it as a second test | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command`, wrapped by `functions.exec`, using `--location --fail --silent --show-error`, the sandboxed attempt fails with `curl: (6) Could not resolve host`, the approved retry succeeds, local measurement uses `perl`, `wc`, `sed`, and `rg`, `web`, `web.open`, and `web.run` all get named explicitly as not invoked | Yes, the agent writes `/private/tmp/ec6-spec-md-headers.txt` at 871 bytes and `/private/tmp/ec-6-spec-md-response.md` at about 92KB, this collides with the naming pattern `GPT-5.6 Sol` runs use, the rollout json log runs 192KB | `SKILL.md` named explicitly, the agent reasons "I'm using the `docs-consumption` skill because it provides the required retrieval-measurement reporting," opens the report with `COMPLETE`, and also reads a prior rollout summary file twice, a step the skill's own protocol never calls for, citations pair `MEMORY.md` `L41` through `L57` with a rollout summary file at `L14` through `L32` | Named `Fetch SPEC.md`, the agent asks permission for `curl` once, the chat timer runs 3 minutes 40 seconds and the rollout audit runs 3 minutes 49.6 seconds, the command count claim reaches about 12 while the audit cites 8, the widest gap in this batch, and the headers show `x-cache: MISS` with an `x-github-request-id` that doesn't match any other Terra run |
| `GPT-5.6 Terra Extra High` | `91,869` characters, `91,877` bytes | Approximately `22,967` tokens using the four characters per token heuristic | No, the direct response returns `HTTP/2 200`, its byte count matches `content-length: 91877`, and it ends cleanly | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `functions.exec` into `exec_command`, the sandboxed attempt fails with `curl: (6) Could not resolve host`, the approved retry succeeds, local measurement uses `wc`, `tail`, `rg`, `awk`, and `od`, `web` and `web.open` aren't invoked even though the chat panel renders `searched the web` | Yes, the agent writes `/private/tmp/ec6-spec-md-headers.txt` at 870 bytes and `/private/tmp/ec6-spec.md` at about 92KB, this collides with the naming pattern `GPT-5.6 Sol` runs use, the rollout json log runs 257KB, the largest in this batch | `SKILL.md` named vaguely, the agent reasons "I'm using the workspace's retrieval-measurement procedure because this is an empirical URL-fetch test," a phrase that doesn't match either skill file's actual wording and most likely borrows from `MEMORY.md` instead, opens the report with `COMPLETE`, citations pair `MEMORY.md` `L52` through `L57` with `L44` through `L46` | Named `Measure web retrieval`, the agent asks permission for `curl` once, the chat timer runs 1 minute 2 seconds and the rollout audit runs 1 minute 9.8 seconds, the command count claim reaches about 5 while the audit cites 4, and the headers show `x-cache: HIT` |
| `GPT-5.6 Terra High` | `91,869` characters, `91,877` bytes | Approximately `22,967` tokens using the four characters per token heuristic | No, the response was `HTTP/2 200`, the byte count matched `content-length`, and it ended cleanly | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command`, the initial sandboxed attempt fails with `curl: (6) Could not resolve host`, the retry with external network access succeeds, local checks use `wc`, `tail`, `awk`, `rg`, and `sed`, `web` and `web.open` aren't invoked | Yes, the agent writes `/private/tmp/ec6-spec-md-headers.txt` at 871 bytes and `/private/tmp/ec6-spec-md-response.md` at about 92KB, this collides with the naming pattern `GPT-5.6 Sol` runs use, the rollout json log runs 123KB | `SKILL.md` named explicitly and correctly, the agent reasons "I'll run only `EC-6`, a direct retrieval of the supplied raw URL, then measure the received body literally, I'm using the repository's docs-consumption procedure because this is a single-URL retrieval characterization," opens the report with `COMPLETE`, citations `MEMORY.md` `L41` through `L57`, the clearest and most accurate skill naming in the Terra batch | Named `Measure raw GitHub fetch`, the agent phrases its own permission request as "May I retry the requested direct fetch of this one raw GitHub URL with external DNS/network access?" with no user turn prompting that framing, chat timer runs 1 minute 28 seconds, rollout audit runs 1 minute 35.1 seconds, command count claim reaches about 8 while the audit cites 7, headers show `x-cache: HIT` |
| `GPT-5.6 Terra Medium` | `91,869` characters, `91,877` bytes | Approximately `22,967` tokens using the four characters per token heuristic | No, the response ended cleanly, `HTTP` status was `200`, and the body size matched the declared content length | `— Notable exclusions with rationale (Appendix B).` | `curl` runs directly through `exec_command`, the sandboxed attempt fails with `curl: (6) Could not resolve host`, the retry succeeds, local checks use `wc`, `tail`, `sed`, and `rg`, `web` and `web.open` aren't invoked | Yes, the agent uniquely creates a directory at `/private/tmp/ec6/` and writes `headers.txt` at 871 bytes alongside `SPEC.md` at about 92KB, this is the only run in the batch that avoids the shared filename collision, the rollout json log runs 89KB | `SKILL.md` named vaguely, the agent reasons "I'll run only `EC-6`, I'm using the project's retrieval-reporting skill so the measurements and completeness assessment stay source-faithful," opens the report with `COMPLETE — EC-6 direct retrieval completed`, and fully discloses the DNS failure in the final report, citations `MEMORY.md` `L52` through `L57` | Named `Measure raw GitHub retrieval`, permission asked once, chat timer runs 51 seconds, rollout audit runs 58.5 seconds, command count claim reaches about 4 and matches the audit exactly, the only run in the batch where the claim and the audit agree, headers show `x-cache: HIT` |
| `GPT-5.6 Terra Light` | `91,869` characters, `91,877` bytes | Approximately `22,967` tokens using the four characters per token heuristic | No, the response ends cleanly at the document's apparent final Appendix B item | `— Notable exclusions with rationale (Appendix B).` | `curl` runs through `exec_command`, the initial sandboxed attempt fails with `curl: (6) Could not resolve host`, the retry with network permission succeeds, local checks use `wc`, `perl`, `awk`, and `rg`, a separate `perl` command that attempts a `tiktoken` based token count crashes with `ModuleNotFoundError: No module named 'tiktoken'`, that crash never appears anywhere in the final report, `web` and `web.open` aren't invoked | Yes, the agent writes `/private/tmp/ec6-spec-md-headers.txt` at 872 bytes and `/private/tmp/ec6-SPEC.md` at about 92KB, this collides with the naming pattern `GPT-5.6 Sol` runs use, the rollout json log runs 89KB | `SKILL.md` attribution stays unclear, the agent reasons "I'm using the project's retrieval-measurement procedure for this single `EC-6` URL only," a line that doesn't clearly name either skill file, the report opening still matches the `docs-consumption` format exactly, citations pair `MEMORY.md` `L44` through `L46` with `L52` through `L54`, no distinct skill file citation this run | Named `Measure raw SPEC.md fetch`, permission asked once, chat timer runs 51 seconds, rollout audit runs 58.6 seconds, command count claim reaches about 6 while the audit cites 5, headers show `x-cache: MISS` |

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
heuristic rather than a real tokenizer, and `GPT-5.6 Terra Light` never gets a real tokenizer
result at all, since its own `tiktoken` lookup fails and the agent falls back to the heuristic
without disclosing the failure. Every figure sits far past a `2,000` token ceiling regardless.

**Combined verdict: `H2` no across all five runs.**

---

## `H3`: Truncation that respects Markdown structure

Indeterminate rather than no. None of the five runs reports a truncation event of any kind, so
none of them offers a boundary to evaluate for structure awareness. Every run also reaches for
full-body `curl` instead of the windowed `web` tool, and the response headers show
`accept-ranges: bytes` in every run that captures headers, so a windowed fetch path stays
available and simply never gets triggered. Calling this hypothesis no would overstate what these
runs show, since a hypothesis about where truncation falls isn't assessable when truncation never
occurs.

**Combined verdict: `H3` indeterminate across all five runs, since no run produces a truncation
event to examine and no run tests the windowed path that headers confirm exists.**

---

## `H4`: Surface context affecting retrieval behavior

Untested. No `T1` or `T2` baseline exists yet for `GPT-5.6 Terra` in this test cycle, so a surface
comparison against Codex Desktop isn't possible this round.

**Combined verdict: `H4` untested across all five runs.**

---

## `H5`: Automatic chunking or pagination behavior

No for four of five runs, partially for one. `Light`, `Medium`, `High`, and `Extra High` each
perform a single verification pass over one saved artifact, using tools such as `wc`, `perl`,
`tail`, `awk`, `rg`, `sed`, and `od`, without touching the live URL more than once and without
re-reading the saved file through a second distinct read event. `Ultra` breaks that pattern, it
reads a prior rollout summary file twice and runs two separate `perl` passes aimed at distinct
extraction goals, producing a materially more elaborate multi-tool chain than the other four
runs. Even `Ultra` never paginates or windows the live source itself, so this stays short of a
full yes.

**Combined verdict: `H5` no for `Light`, `Medium`, `High`, and `Extra High`, partially for
`Ultra`. Unlike the Sol batch, where repeat local reads tracked reasoning level cleanly across
four of five runs, the Terra batch shows this pattern only at the top reasoning level, and it's
driven by cross-run artifact reading rather than by re-verification of the same saved file.**

---

## `H6`: Skill influence on disclosure and completeness reporting

Partially, and the signal splits the same two ways it does in the Sol batch. At the surface
layer, every run bypasses `web` in favor of direct `curl`, and every run's report opens with
`COMPLETE` per the skill's formatting instruction, that layer holds without exception across all
five runs. At the protocol layer, results diverge more than they do in the Sol batch. `Medium`
and `High` fully disclose the sandboxed DNS failure and name `docs-consumption` correctly, so
each reaches yes on substantive engagement. `Extra High` matches the formatting but its own
reasoning language doesn't match either skill file's actual wording, so it reaches yes only on
the surface. `Light` copies the report structure exactly while quietly dropping its own
`tiktoken` crash from the final report, a direct violation of the skill's rule six, so it stays
at partially. `Ultra` names the skill correctly and cleanly but pulls in a prior rollout summary
file that the skill's protocol never calls for, introducing a contamination path the skill
doesn't govern, so it also stays at partially.

No run across the batch reaches a `PARTIAL` or `UNVERIFIABLE` label, and no run recommends a fix
for the recurring sandboxed DNS failure despite the skill's step seven instruction to do so.

**Combined verdict: `H6` partially across all five runs. The skill correlates with a consistent
surface shift toward `curl` and a `COMPLETE` first report structure, but substantive compliance
with the skill's disclosure and fix-recommendation rules tracks each run's own skill naming
accuracy far more than it tracks reasoning level.**

---

## Emergent Findings

1. **The `Searched the web` chat label renders in every run despite zero confirmed `web_search`
calls.** All five runs display this label at least once while the rollout audit only cites
`curl`, `wc`, `tail`, `perl`, `awk`, `rg`, `sed`, and `od`, consistent with the `tools_named`
unreliability already logged elsewhere in `T2`.

2. **The two tier sandboxed DNS failure, then escalated retry, pattern holds without exception
across all five runs.** Per established methodology this counts as expected `T2` surface
behavior rather than direct `H4` evidence, but it opens every run's tool chain the same way.

3. **Artifact naming collision affects four of five runs.** `Light`, `High`, `Extra High`, and
`Ultra` all write the fetched body to a filename that collides with the pattern `GPT-5.6 Sol`
runs already used, while `Medium` is the only run in the batch that avoids the collision, by
writing to a unique `/private/tmp/ec6/` directory instead of a shared top level filename.

4. **Command count claimed in chat exceeds the rollout audit's count in four of five runs, and
the gap widens most sharply at the top reasoning level.** `Light` claims about 6 against an
audited 5, `Medium` claims about 4 and matches the audit exactly, `High` claims about 8 against
an audited 7, `Extra High` claims about 5 against an audited 4, and `Ultra` claims about 12
against an audited 8, the widest gap in the batch.

5. **Chat timer duration doesn't scale cleanly with reasoning level, unlike `Sol` runs.**
`Light` and `Medium` both land at 51 seconds, `High` jumps to 1 minute 28 seconds, `Extra High`
actually drops back down to 1 minute 2 seconds, and only `Ultra` climbs sharply to 3 minutes 40
seconds. Reasoning level and runtime track each other far less consistently here than they do
across the `GPT-5.6 Sol` batch.

6. **The `x-github-request-id` header repeats identically across four of five runs.** `Light`,
`Medium`, `High`, and `Extra High` all report the exact same request id,
`3560:18B56D:1C5198:20B492:6A5556D9`, while each of those four runs shows a different
`x-served-by` cache node and a different timestamp, and only `Ultra` reports a distinct request
id. Four independently timestamped fetches sharing one origin request id doesn't have an obvious
benign explanation and is worth checking against the raw rollout logs before treating these as
five _genuinely independent origin fetches_.

7. **`SKILL.md` attribution accuracy tracks `H6` compliance more closely than reasoning level
does.** `High` and `Ultra` name `docs-consumption` explicitly and correctly, `Medium` and `Extra High`
use vaguer language that borrows more from `MEMORY.md` phrasing than from either skill
file's own wording, and `Light` doesn't clearly attribute either file at all. The run that
reasons most accurately about the skill also reports most completely, and that pairing doesn't
line up neatly with the reasoning level ladder.

8. **Test naming drifts across every run with no correlation to reasoning level, mirroring Sol runs.**
`Measure raw SPEC.md fetch`, `Measure raw GitHub retrieval`, `Measure raw GitHub fetch`,
`Measure web retrieval`, and `Fetch SPEC.md` all appear across the five runs.

9. **The original prompt's own wording gets lost in every run.** The prompt explicitly asks for
eight numbered fields and explicitly warns against proceeding to any other test to prevent
methodology contamination, but no run's reasoning trace quotes or restates that prompt directly.
Every run instead opens by naming its own retrieval procedure, sourced from `MEMORY.md` or
`SKILL.md` language, so the prompt's contamination warning gets honored only incidentally,
through skill and memory conventions that happen to restrict scope to `EC-6`, rather than
through the agent actually engaging with what the prompt says.

10. **Every run's tool choice answers the prompt's tool visibility question while sidestepping
the test's actual intent.** The prompt asks the agent to report on truncation, not to avoid it,
yet every run's skill or memory driven habit of reaching for `curl` first guarantees a full,
untruncated body before any truncation behavior gets a chance to appear. An edge case test built
to observe truncation risk stays largely untested across this batch, not because truncation
doesn't happen, but because the agent's own retrieval habit never gives it room to happen.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.6 Terra Ultra` | Pass | `PASS, curl_91869_chars_91877_bytes, repeat_read_rollout_summary_reread, artifact_name_collision, skill_named_explicitly, chat_timer_220s, audit_229s` |
| `GPT-5.6 Terra Extra High` | Pass | `PASS, curl_91869_chars_91877_bytes, single_read_pass, skill_language_mismatched, artifact_name_collision, cache_hit, chat_timer_62s, audit_69s` |
| `GPT-5.6 Terra High` | Pass | `PASS, curl_91869_chars_91877_bytes, single_read_pass, skill_named_explicitly, ungrounded_permission_phrasing, artifact_name_collision, chat_timer_88s, audit_95s` |
| `GPT-5.6 Terra Medium` | Pass | `PASS, curl_91869_chars_91877_bytes, single_read_pass, artifact_name_unique, command_count_matches_audit, chat_timer_51s, audit_58s` |
| `GPT-5.6 Terra Light` | Pass | `PASS, curl_91869_chars_91877_bytes, single_read_pass, tiktoken_crash_undisclosed, no_clear_skill_attribution, artifact_name_collision, chat_timer_51s, audit_58s` |
