# EC-6 GPT-5.6 Luna Flash Experiment Summary, Skill-On Memory-Suppressed Sub-track

## Test Conditions

|                 | **`EC-6`, `GPT-5.6 Luna` flash experiment, `/SKILL`-on + `/memories`-suppressed** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | Confirmed at `91,869` to `91,877` characters or bytes when the agent verifies via `curl`, roughly `23,000` tokens, the `web` tool's own extraction lands closer to `24,884` to `25,453` characters and about `6,200` tokens when it appears |
| Surface         | VS Code-Codex Extension, `v26.715.31925` |
| Workspace       | Session scoped sandbox, writable local paths, `/private/tmp` writable |
| Track           | `T2` VS Code-Codex-interpreted, sub-track 3 |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.6 Luna` |
| Runs            | 4, runs 13 through 16 |
| Skill condition | `docs-consumption/SKILL` present and prompt agent to read it |
| Memory condition | Suppressed, no `MEMORY.md` citations expected in this sub-track |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.6 Luna Light` run 13 | `24,884` characters received through `web`, `curl` never confirmed the full source since it failed and wasn't retried with escalation | About `6,200` | Yes, ends mid-line at `L54` after `JSON-LD metadata,` | "to a page *about* `llms.txt`, JSON-LD metadata," | `web_run` invoked with `open`, `curl` invoked once and failed with `DNS` error `6`, the rollout audit counts `3` `web_search` calls and `5` `exec_command` calls against `2` visible chat actions, flagged `SHELL_DOMINANT` and `escalation_abandonment` not recovered | No file artifacts saved, rollout json log `129KB` | `docs-consumption` confirmed present, prompt instructed, prefix `PARTIAL` | Named `Test EC-6 web retrieval`, chat timer `29` seconds, rollout audit duration `33.8` seconds, the only run in this sub-track where the sandbox failure is never retried with escalated access |
| `GPT-5.6 Luna Medium` run 14 | `91,869` characters confirmed via direct `curl`, also `91,877` bytes on disk | About `23,000` | No, received bytes matched `content-length: 91877` exactly | "— Notable exclusions with rationale, Appendix B." | `exec_command`, `curl` invoked twice, first sandboxed failure, second escalated success, about `4` commands total, `web` and `web.open` not invoked, the tool visibility report omits `wc`, `tail`, and `rg` even though the transcript shows them running | Yes, wrote two directories, `/private/tmp/ec6.mfji8y` with an empty `headers` file and `/private/tmp/ec6.quiLgO` with `body` `92KB` and `headers` `872` bytes, naming collision and contamination risk, rollout json log `79KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Run EC-6 retrieval test`, asked permission for `curl` once, chat timer `47` seconds, rollout audit duration `50.9` seconds, the skill's requirements get paraphrased slightly inaccurately in the report |
| `GPT-5.6 Luna High` run 15 | `91,869` characters, `91,877` bytes, confirmed via `curl` with a `4` character per token heuristic noted for the estimate | About `23,000` | No, `HTTP Content-Length` matched the received body size | "— Notable exclusions with rationale, Appendix B." | `exec_command`, `curl` invoked twice, first sandboxed failure, second escalated success, plus `wc`, `tail`, `sed`, `rg`, `od`, `printf`, no `web` or `web.open` invoked, a separate `zsh` read-only variable error on the first `curl` attempt goes undisclosed in the report | Claimed to write `/private/tmp/ec6_headers.txt` `870` bytes with `/private/tmp/ec6_body.txt` `92KB`, naming collision risk, rollout json log `90KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Title fell back to raw prompt text rather than an auto-generated name, a mid-run connection interruption shows `Reconnecting 2/5` before the skill loads, asked permission for `curl` once, chat timer `2` minutes `8` seconds, rollout audit duration `2` minutes `12.1` seconds |
| `GPT-5.6 Luna Extra High` run 16 | `24,885` payload characters from `web`, `25,453` including tool metadata, the agent then verifies the full source at `91,869` characters via a follow-up `curl` fetch | About `6,200` payload tokens from the `web` result | Yes, the `web` result ends mid-sentence at `L54`, even though the agent's own verification confirms the complete source runs to `91,869` characters | "o a page *about* `llms.txt`, JSON-LD metadata," | `web_run` invoked with `open`, `curl` invoked for same-URL verification after an initial sandbox `DNS` failure and a successful escalated retry, plus `exec_command`, `cat`, `wc`, `tail`, `rg`, `od`, chat renders `4` `web` searches, rollout audit cites `9` commands against about `4` visible | Claimed to write `/private/tmp/ec6-spec.md` `92KB`, a hyphenated naming variant distinct from the underscore and directory patterns in the other three runs, rollout json log `168KB` | `docs-consumption` confirmed present, prompt instructed, prefix `PARTIAL` | Title fell back to raw prompt text, asked permission for `curl` once, chat timer `3` minutes `13` seconds, rollout audit duration `3` minutes `18.8` seconds, the agent reasons explicitly about separating `web`-tool clipping from true source length, then reports the more limited `web` metrics anyway |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported at the source level. Every run that verifies through `curl`, runs 14, 15, and 16,
lands on the full `91,869` characters and `91,877` bytes, well past any plausible ten to one
hundred kilobyte ceiling. The one exception worth separating out is the `web` tool's own
extraction, which lands in the `24,884` to `25,453` character range in runs 13 and 16. That's a
consistent window inside the range `H1` describes, but it tracks with the `web` tool's own
mechanism rather than a ceiling on the underlying document, since a follow-up `curl` fetch in
run 16 clears it entirely on the same URL in the same session.

**Combined verdict: `H1` no across all four runs, with the `web` tool's own clip pattern noted
separately.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. The `curl`-verified runs return roughly `23,000` tokens intact, and even the
`web` tool's more limited extraction in runs 13 and 16 still clears `6,200` tokens, more than
three times the hypothesized ceiling.

**Combined verdict: `H2` no across all four runs.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Mixed. Runs 13 and 16 both show the `web` tool cutting off at the identical point, mid-line or
mid-sentence at `L54` right after `JSON-LD metadata,`, which reads as an arbitrary content break
rather than a markdown boundary like a closed heading or list. Runs 14 and 15 show no truncation
at all, so there's no cutoff to evaluate in either of those.

**Combined verdict: `H3` no where truncation occurs, runs 13 and 16, and indeterminate where it
doesn't, runs 14 and 15.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Not testable. `GPT-5.6 Luna` wasn't available at the time `T1` testing closed, so there's no
matching `T1` run to compare against for any of the four reasoning levels.

**Combined verdict: `H4` untested across all four runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Mostly supported, with one run standing apart. Runs 13, 14, and 15 each show a multi-command
verification chain, but it's reactive, triggered by the sandboxed `curl` failure and followed
by local checks like `wc`, `tail`, `rg`, or `od` against the saved or fetched body. Run 16 is
the clearest case for the hypothesis as written, since the agent notices the `web` result's own
`Total lines: 55` marker on its own, reasons explicitly about separating source length from
`web`-tool clipping, and then deliberately cross-verifies with `curl` rather than reacting to a
failure.

**Combined verdict: `H5` partially for runs 13, 14, and 15, yes for run 16.**

---

## `H6`: Does the `docs-consumption/SKILL` shift truncation disclosure and completeness reporting

Faint support, in the same shape as the `GPT-5.5` sub-track's finding. All runs cite
`docs-consumption` as read and open with a `COMPLETE` or `PARTIAL` prefix, and the memory
suppressed condition holds cleanly, no runs cite `MEMORY.md` or reference stored
feature in their reasoning. Where the gap persists is in recommendations, no run proposes
a fix for the recurring sandbox escalation step even though the `/SKILL`'s protocol asks for
one when a gap exists. Runs 13 and 16 both show a sharper version of this gap, an early exit
pattern where the agent does the harder work of reconciling `web` and `curl` metrics and then
reports the more conservative, less informative figure.

**Combined verdict: `H6` partially across all four runs, with influence confined to reporting
structure and framing rather than examination depth or recommendation.**

---

## Emergent Findings

1. **The two-tier sandboxed failure then escalated retry pattern mostly holds, with one break.**
Runs 14, 15, and 16 all complete an escalated `curl` retry after the initial `Could not resolve
host` failure. Run 13 is the exception, the sandbox failure is never retried with escalation,
which the rollout audit flags as `escalation_abandonment` not recovered, a genuine departure
from the `GPT-5.5` sub-track where every run escalated successfully.

2. **Artifact naming collision risk recurs across three of the four runs.** Run 14 writes to two
differently named temp directories in the same session, run 15 claims `ec6_headers.txt` and
`ec6_body.txt`, and run 16 introduces yet another variant, `ec6-spec.md`, none of which match
each other or the underscore and directory patterns from the other runs. Across the batch this
adds up to about `8` artifacts, mostly directories and small or empty files, all under
`/private/tmp`.

3. **The `web` tool reappears unlike `GPT-5.5`.** Runs 13 and 16 both invoke
`web` and both land on the identical `L54` mid-sentence cutoff, reviving the windowed clipping
pattern that the `GPT-5.5` sub-track never showed since every one of those runs bypassed `web`
entirely in favor of `curl` alone.

4. **A `zsh` scripting bug in run 15 goes undisclosed.** The first `curl` attempt
throws a separate `read-only variable: status` error alongside the `DNS` failure, and the agent
never narrates or flags it, moving straight to the retry instead. This sits outside the `/SKILL`'s
own disclosure protocol, since it's a tool-authoring flaw rather than a retrieval gap, but it
fits the same pattern as the naming collisions. The agent isn't doing preventative work to avoid
reserved words or path reuse even under a clean-slate, memory-suppressed condition. That the
pattern shows up here at all, with memory fully suppressed, suggests the collision-prone
scripting habit is default agent behavior rather than something driven by stale memory echoes.

5. **Duration scales upward with reasoning level but with real overhead noise.** Run 13 finishes
in `29` seconds, run 14 in `47` seconds, run 15 in `2` minutes `8` seconds, and run 16 in `3`
minutes `13` seconds. Run 15's jump is partly explained by a mid-run connection interruption,
`Reconnecting 2/5`, that adds wallclock time unrelated to reasoning effort.

6. **No run offers a recommendation for the recurring sandbox escalation step**, the same gap
found in the `GPT-5.5` sub-track. The `/SKILL`'s protocol asks for a fix when one exists, and every
run either narrates the `DNS` failure or works around it silently, but none proposes closing the
gap itself.

7. **Runs 13 and 16 both show the sharpest early exit pattern in the batch.** Run 16 in
particular does the work of reconciling both `web` and `curl` measurements internally, states
the distinction clearly in its reasoning, and then reports only the `web` tool's more limited
`PARTIAL` metrics in the final answer, leaving the fuller `curl`-verified numbers out of the
disclosed report entirely.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.6 Luna Light` run 13 | Pass | `web_24884_chars_partial_L54 + curl_dns_failure_not_escalated + shell_dominant_flag + skill_instructed_docs_consumption + 29s` |
| `GPT-5.6 Luna Medium` run 14 | Pass | `curl_91869_chars_content_length_match + artifact_naming_collision + tool_visibility_undercount + skill_instructed_docs_consumption + 47s` |
| `GPT-5.6 Luna High` run 15 | Pass | `curl_91869_chars_content_length_match + zsh_readonly_var_undisclosed + skill_instructed_docs_consumption + 2m8s` |
| `GPT-5.6 Luna Extra High` run 16 | Pass | `web_24885_chars_partial_L54 + curl_91869_chars_verified + early_exit_partial_label + skill_instructed_docs_consumption + 3m13s` |
