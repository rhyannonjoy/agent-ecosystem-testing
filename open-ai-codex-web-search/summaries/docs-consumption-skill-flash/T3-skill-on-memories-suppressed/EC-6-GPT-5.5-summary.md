# EC-6 GPT-5.5 Flash Experiment Summary, Skill-On Memory-Suppressed Sub-track

## Test Conditions

|                 | **`EC-6`, `GPT-5.5` flash experiment, `/SKILL`-on + `/memories`-suppressed** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed at `91,869` to `91,877` characters or bytes depending on the run, roughly `23,000` tokens |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session scoped sandbox, writable local paths, `/private/tmp` writable |
| Track           | `T2` VS Code-Codex-interpreted, sub-track 3 |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.5` |
| Runs            | 4, runs 9 through 12 |
| Skill condition | `docs-consumption/SKILL` present and prompt agent to read it |
| Memory condition | Suppressed, no `MEMORY.md` citations expected in this sub-track |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.5 Light` run 9 | `91,869` characters confirmed via direct `curl`, also `91,877` bytes on disk | About `22,967` | No, received bytes matched `content-length: 91877` exactly, and the document ended cleanly | "— Notable exclusions with rationale, Appendix B." | `functions.exec_command`, `curl` invoked twice, first failed sandboxed with `Could not resolve host`, second succeeded escalated, plus `wc`, `tail`, `cat`, `rg`, `head`, `file`, `od`, `multi_tool_use.parallel`, `web` and `web.open` not invoked despite the chat rendering "Searched the web" | Yes, wrote and saved `/private/tmp/ec6_headers.txt` `872` bytes with `/private/tmp/ec6_spec.md` `92KB`, flagged for naming collision risk, rollout json log `98KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Test EC-6 URL retrieval`, asked permission for `curl` once, chat timer `46` seconds, rollout audit duration `52.3` seconds, the sandbox DNS failure gets restated three separate times across the reasoning, the report prefix, and a closing line, with no added analysis on any repetition |
| `GPT-5.5 Medium` run 10 | `91,869` characters confirmed via the direct `curl` fetch, `91,877` bytes on disk | About `23,000` | No, byte count matched `content-length`, and the document ended cleanly | "— Notable exclusions with rationale, Appendix B." | `functions.exec_command`, `curl` invoked twice, first sandboxed failure, second escalated success, plus `sed`, `wc`, `tail`, `rg`, `file`, `od`, `web` and `web.open` not invoked despite the chat rendering "Searched the web" | Yes, claimed to write and save `/private/tmp/ec6_headers.txt` `870` bytes with `/private/tmp/ec6_spec.md` `92KB`, naming collision risk against the `Light` run's artifact, rollout json log `101KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Fetch SPEC.md retrieval test`, asked permission for `curl` once, chat timer `55` seconds, rollout audit duration `1` minute `0.7` seconds, the saved headers artifact carries the identical `x-github-request-id` found in the prior run's headers despite differing date, `x-served-by`, and `x-cache` fields |
| `GPT-5.5 High` run 11 | `91,869` characters, `91,877` bytes, captured via a custom `curl -w` format string | About `22,967` | No, the saved body matched the successful `curl` download size and ended cleanly, the agent notes the byte and character counts differ due to multi-byte UTF-8 characters | Same closing text, with the trailing newline explicitly noted | `functions.exec_command`, `curl` invoked twice, first sandboxed failure, second escalated success, plus `wc`, `tail`, `awk`, `od`, `sed`, `multi_tool_use.parallel`, `web` and `web.open` not invoked | Yes, claimed to write and save `/private/tmp/ec6_spec.md` `92KB`, naming collision risk against both the `Light` and `Medium` runs' artifacts, rollout json log `108KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE`, uniquely points to its own saved artifact path rather than a vague access claim | Named `Fetch SPEC.md retrieval test`, asked permission for `curl` once, chat timer `1` minute `23` seconds, rollout audit duration `1` minute `30.2` seconds, the only run in this sub-track to reason explicitly about the byte versus character count gap |
| `GPT-5.5 Extra High` run 12 | `91,869` characters, `91,877` bytes, `curl` reported `100 91877` directly in its transfer summary | About `23,000` | No, `curl` reported `100 91877`, and the file ends cleanly | "— Notable exclusions with rationale, Appendix B." | `functions.exec_command`, `curl` invoked twice, first sandboxed failure showing an empty progress table, second escalated success, plus `cat`, `wc`, `tail`, `rg`, `web` and `web.open` not invoked | Yes, claimed to write and save `/private/tmp/ec-6-spec.md` `92KB`, a new hyphenated naming variant distinct from the underscore pattern used in the other three runs, rollout json log `110KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Fetch SPEC.md retrieval test`, asked permission for `curl` once, chat timer `1` minute `29` seconds, rollout audit duration `1` minute `35` seconds, shows a lighter verification pattern than the `High` run despite the higher reasoning setting |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. All four runs complete a full `curl` fetch and land on `91,869` characters and
`91,877` bytes, well past any plausible ten to one hundred kilobyte ceiling. No run shows a
size based cutoff anywhere near that range.

**Combined verdict: `H1` no.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. Every run returns roughly `23,000` tokens intact on its direct fetch, far past
a `2,000` token ceiling.

**Combined verdict: `H2` no.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not testable. No truncation event occurs in any of the four runs, so none of them offer a
cutoff to check against markdown boundaries. This differs from the `GPT-5.4` sub-track, where
two runs disclosed an actual `web` cutoff to evaluate.

**Combined verdict: `H3` indeterminate across all four runs.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Faint support. Every run converges with its `T1` counterpart on the same retrieval outcome,
`91,869` characters and no truncation, but each also shows a genuine tooling divergence from
`T1`, differing `curl` permission counts, differing command counts, or a distinct combination
of local verification tools such as `awk`, `od`, or `multi_tool_use.parallel`. Since the tool
path itself diverges even when the outcome doesn't, none of the four runs qualify as an exact
match to `T1`.

**Combined verdict: `H4` partially across all four runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Supported. All four runs show a multi-command local verification chain following the escalated
`curl` fetch, reading byte counts, word counts, line counts, hex dumps, and tail excerpts
against the saved artifact rather than taking a single measurement pass. `GPT-5.5 High` run 11
and `GPT-5.5 Extra High` run 12 both run six or more distinct verification commands against the
saved file, and `GPT-5.5 Light` run 9 and `GPT-5.5 Medium` run 10 show a comparable pattern.

**Combined verdict: `H5` yes across all four runs.**

---

## `H6`: Does the `docs-consumption/SKILL` shift truncation disclosure and completeness reporting

Faint support, similar in shape to the `GPT-5.4` sub-track's finding. All four runs cite
`docs-consumption` as read and open with a structured completeness report under a `COMPLETE`
prefix. None surface a configuration recommendation addressing the recurring sandbox
escalation step. Where the skill does show up is in reporting language, tool visibility
framing, and completeness labeling, not in deeper examination of the retrieval mechanism or
in any divergence of the retrieval outcome itself.

**Combined verdict: `H6` partially across all four runs, with influence confined to reporting
structure and framing rather than examination depth.**

---

## Emergent Findings

1. **The two-tier sandboxed failure then escalated retry pattern holds across all four runs.**
Every run needs an escalated `curl` call outside the sandbox to complete the fetch after an
initial `Could not resolve host` failure, and no run recommends a configuration change that
would remove this step.

2. **Every run in this sub-track discloses the sandbox DNS failure somewhere in its reasoning
or report**, unlike the `GPT-5.4` sub-track, where disclosure didn't track cleanly with
reasoning level. `GPT-5.5 Light` run 9 restates the failure three separate times without
adding analysis on any repetition.

3. **Artifact naming collision risk recurs across three of the four runs.** `Light`, `Medium`,
and `High` all write to filename variants sharing the `ec6_spec.md` pattern with only an
underscore difference, while `Extra High` introduces a new hyphenated variant,
`ec-6-spec.md`, that doesn't collide with the other three but adds yet another naming
inconsistency to the batch.

4. **No run invokes `web` at all**, a departure from the
`GPT-5.4` sub-track, where three of four runs called `web` and surfaced a genuine windowed
cutoff around `L54`. Every `GPT-5.5` run bypasses the `web` pipeline entirely and relies on
`curl` alone, so that cutoff pattern never appears here.

5. **Duration scales cleanly with reasoning level in this sub-track**, unlike the `GPT-5.4`
sub-track's inversion between `High` and `Extra High`. `Light` finishes in `46` seconds,
`Medium` in `55` seconds, `High` in `1` minute `23` seconds, and `Extra High` in `1` minute
`29` seconds.

6. **`GPT-5.5 High` run 11 is the only run across the batch to reason explicitly about the gap
between byte count and character count**, attributing it to multi-byte UTF-8 characters, a
distinction the other three runs leave unexamined even though the same `91,877` versus
`91,869` gap appears in every one of them.

7. **`GPT-5.5 Medium` run 10's headers artifact carries an `x-github-request-id` identical to
a prior run's headers** despite differing `date`, `x-served-by`, and `x-cache` fields, an
inconsistency that doesn't fit a simple copy explanation and stays an open question for this
sub-track.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.5 Light` run 9 | Pass | `curl_91869_chars_content_length_match + dns_failure_disclosed_3x + no_web + skill_instructed_docs_consumption + 46s` |
| `GPT-5.5 Medium` run 10 | Pass | `curl_91869_chars_content_length_match + headers_request_id_reuse_flagged + no_web + skill_instructed_docs_consumption + 1m0.7s` |
| `GPT-5.5 High` run 11 | Pass | `curl_91869_chars_byte_char_gap_reasoned + no_web + skill_instructed_docs_consumption + 1m23s` |
| `GPT-5.5 Extra High` run 12 | Pass | `curl_91869_chars_content_length_match + hyphenated_artifact_naming_variant + no_web + skill_instructed_docs_consumption + 1m29s` |
