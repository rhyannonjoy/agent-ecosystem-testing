# EC-6 GPT-5.6 Sol Flash Experiment Summary, Skill-On Memory-Suppressed Sub-track

## Test Conditions

|                 | **`EC-6`, `GPT-5.6 Sol` flash experiment, `/SKILL`-on + `/memories`-suppressed** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | Confirmed at `91,869` to `91,877` characters or bytes when the agent verifies via `curl`, roughly `22,967` to `23,000` tokens, the `web` tool's own extraction lands at `25,453` characters and about `6,364` tokens when it appears |
| Surface         | VS Code-Codex Extension, `v26.715.31925` |
| Workspace       | Session scoped sandbox, writable local paths, `/private/tmp` writable |
| Track           | `T2` VS Code-Codex-interpreted, sub-track 3 |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.6 Sol` |
| Runs            | 5, runs 17 through 21 |
| Skill condition | `docs-consumption/SKILL` present and prompt agent to read it |
| Memory condition | Suppressed, no `MEMORY.md` citations expected in this sub-track |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.6 Sol Light` run 17 | `91,869` characters confirmed via direct `curl`, also `91,877` bytes on disk | About `22,967` | No, the response ended cleanly at `L1,722` and the received byte count matched `Content-Length` | "Notable exclusions with rationale, Appendix B." | `curl` invoked directly, `exec_command` and `functions.wait` used, `sed` and `ruby` used locally, which is unusual since most runs reach for `python3`, `web` and `web.open` not invoked, the first `curl` attempt fails `DNS` then the escalated retry succeeds, chat renders about `4` commands, the rollout audit counts `5` | Wrote `ec6-headers.txt` `872` bytes and `ec6-spec.md` `92KB`, no naming collision since `/private/tmp` had already cleared, rollout json log `83KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Test direct SPEC retrieval`, asked permission for `curl` once, chat timer `57` seconds, rollout audit duration `1` minute `4.3` seconds, the report stretches protocol point `9`'s single-`web`-extraction verification language into a general requirement it wasn't written for |
| `GPT-5.6 Sol Medium` run 18 | `91,869` characters confirmed via `curl`, also `91,877` bytes on disk | About `22,967` | No, `HTTP` status `200`, `size_download` and `Content-Length` both match at `91,877` bytes | "Notable exclusions with rationale, Appendix B." | `curl` invoked twice, first a sandboxed failure then an escalated success, `sed`, `wc`, `tail`, `rg`, `tr`, and `file` used locally, `web` and `web.open` not invoked | Wrote `ec6_headers.txt` `871` bytes and `ec6_spec.md` `92KB`, rollout json log `94KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Test URL retrieval completeness EC-6`, asked permission for `curl` once, chat timer `1` minute `7` seconds, rollout audit duration `1` minute `13.7` seconds, the headers artifact shows an internally contradictory `x-cache: HIT` paired with `x-cache-hits: 0` |
| `GPT-5.6 Sol High` run 19 | `91,869` characters confirmed via `curl`, also `91,877` bytes on disk | About `22,967` | No apparent truncation, `curl` completed with `HTTP 200` and its `91,877`-byte download matches the saved file size | "Notable exclusions with rationale, Appendix B." | `curl` attempted twice, `sed`, `wc`, `tail`, `rg`, `stat`, and `od` used locally, `web`, `web.open`, and `web_run` not invoked, about `12` commands ran | Claimed to write `ec6_spec.md` `92KB` with naming collision risk, rollout json log `101KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Run EC-6 retrieval test`, asked permission for `curl` once, chat timer `1` minute `16` seconds, rollout audit duration `1` minute `22.4` seconds, the report frames a plain strategy description as though the skill required it, when the skill text doesn't actually make that requirement |
| `GPT-5.6 Sol Extra High` run 20 | `25,453` characters received through `web`, this figure includes tool-added source metadata and line labels rather than raw document body alone | About `6,364` | Yes, the response ends at `L54` mid-sentence after "`JSON-LD metadata,`" in the `llms-txt-directive-html` check, and the document describes seven categories so substantial content is missing | "a page about `llms.txt`, `JSON-LD` metadata, `" | `web__run` invoked with `open`, `curl` not invoked at all, `exec_command` and `sed` used only to read the skill file, the URL gets fetched three times within this run, an initial retrieval, a stability retry, and a final retry after a `JavaScript TextEncoder` error | No file artifacts saved, rollout json log `134KB` | `docs-consumption` confirmed present, prompt instructed, prefix `PARTIAL` | Named `Test EC-6 web retrieval`, chat timer `1` minute `29` seconds, rollout audit duration `1` minute `39.9` seconds, the only run in this sub-track that retrieves via `web` instead of `curl` and the only run to report a genuine truncation event |
| `GPT-5.6 Sol Ultra` run 21 | `91,869` characters confirmed via `curl`, also `91,877` bytes on disk | About `23,000` | No, `HTTP Content-Length`, `curl`'s download size, and the local file size all match at `91,877` bytes | "Notable exclusions with rationale, Appendix B." | `curl` invoked, `functions.exec`, `tools.exec_command`, and `tools.update_plan` invoked, `sed`, `cat`, `wc`, `tail`, `od`, and `rg` used locally, neither `web` nor `web.open` invoked, about `19` commands ran | Claimed to write `ec6_headers.txt` `871` bytes with `ec6_spec.md` `92KB`, naming collision risk, rollout json log `264KB` | `docs-consumption` confirmed present, prompt instructed, prefix `COMPLETE` | Named `Test EC-6 web retrieval`, asked permission for `curl` once, chat timer `2` minutes `44` seconds, rollout audit duration `2` minutes `51.4` seconds, reads the saved spec file about `8` times in a pagination-like pattern, and the report doesn't disclose a `UI` truncation that the rollout audit flagged |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported at the source level for four of the five runs. Runs 17, 18, 19, and 21 all
verify through `curl` and land on the full `91,869` characters and `91,877` bytes, well past
any plausible ten to one hundred kilobyte ceiling. Run 20 stands apart, its `web`-tool
extraction lands at `25,453` characters, which sits inside `H1`'s hypothesized range. That
cutoff tracks with the `web` tool's own extraction mechanism rather than a ceiling on the
underlying document, since the source's full size gets independently confirmed at `91,877`
bytes across the other four runs on the identical `URL`.

**Combined verdict: `H1` no for runs 17, 18, 19, and 21, with run 20's `web`-tool clip pattern
falling inside the hypothesized range but attributable to the retrieval mechanism rather than
the source.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. The `curl`-verified runs return roughly `23,000` tokens intact, and even run
20's more limited `web` extraction still clears `6,364` tokens, more than three times the
hypothesized ceiling.

**Combined verdict: `H2` no across all five runs.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Mixed. Run 20 shows the `web` tool cutting off mid-sentence at `L54`, right after "`JSON-LD
metadata,`", with an unclosed inline backtick left open, which reads as an arbitrary content
break rather than a markdown boundary like a closed heading or list. The other four runs show
no truncation at all, so there's no cutoff to evaluate in any of them.

**Combined verdict: `H3` no for run 20, and indeterminate for runs 17, 18, 19, and 21.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Not testable. `GPT-5.6 Sol` wasn't available at the time `T1` testing closed, so there's no
matching `T1` run to compare against for any of the five reasoning levels.

**Combined verdict: `H4` untested across all five runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Mixed, and split more finely than the `Luna` sub-track. Run 17 shows a single direct fetch
with no repeated verification chain. Runs 18 and 21 each show local, repeated inspection
commands against the saved file, `wc`, `tail`, `rg`, `od`, or repeated reads, but the actual
retrieval stays a single fetch, so this reads as pagination-like local probing rather than
true chunked retrieval. Run 19 goes further with a denser multi-chain local verification
pass, `sed`, `wc`, `tail`, `rg`, `stat`, and `od` together, which reads as the clearest case
for the hypothesis as written. Run 20 fetches the identical `URL` three times, but each
attempt returns the same `L54` cutoff instead of advancing to new content, which is repeated
stability-checking rather than successful chunking.

**Combined verdict: `H5` no for run 17, partially for runs 18, 20, and 21, yes for run 19.**

---

## `H6`: Does the `docs-consumption/SKILL` shift truncation disclosure and completeness reporting

All runs cite `docs-consumption` as read, and the memory-suppressed condition holds
cleanly, no run cites `MEMORY.md` or references stored feature in its reasoning. Every run
opens with a prefix drawn from `/SKILL`'s own disclosure format, `COMPLETE` for four runs and
`PARTIAL` for run 20, and run 20 is the strongest compliance case in the batch, it states the
exact cutoff location, discloses the `TextEncoder` error under tool visibility, and closes
with a concrete recommended fix. The gap that recurs elsewhere: invented or over-extended
attribution, run 17 stretches a real `/SKILL` clause past its intended scope, and runs 19
and 21 both attach "the skill requires X" framing to claims the skill text doesn't actually
make, dressed in the same confident citation syntax as a genuine reference. Runs 19 and 20
also share near identical `/SKILL`-derived phrasing about distinguishing tool success from
complete delivery, but justify opposite tool choices, `curl` in one case and `web` in the
other, which suggests the phrasing functions as a post-hoc narrative wrapper rather than a
genuine driver of retrieval strategy.

**Combined verdict: `H6` yes across all five runs, with the strength of compliance varying,
run 20 shows the most substantive adherence, while runs 17, 19, and 21 show citation-shaped
framing that doesn't always track the skill's actual requirements.**

---

## Emergent Findings

1. **The two-tier sandboxed failure then escalated retry pattern holds for every `curl`-based
run.** Runs 17, 18, 19, and 21 all complete an escalated `curl` retry after the initial "Could
not resolve host" failure, consistent with the pattern already established in the `Luna`
sub-track. Run 20 is the outlier since it never invokes `curl` at all, so the two-tier pattern
doesn't apply to it.

2. **Artifact naming collision risk recurs across most of the batch.** Run 17 avoids collision
only because `/private/tmp` had already cleared before it ran, and runs 18, 19, and 21 all
write files under names that don't share a consistent convention across the batch, `spec.md`
versus `headers.txt` versus underscore variants. Across the batch this adds up to about `7`
artifacts, mostly small header files and one `92KB` spec body per `curl`-based run, all under
`/private/tmp`.

3. **`accept-ranges: bytes` appears in every headers artifact reviewed**, runs 17, 18, and 21,
and no agent's report mentions it or the possibility of a ranged request to partially verify
content, even though the skill's protocol point `2` calls for examining full tool metadata.

4. **The `etag` stays identical across runs 17, 18, and 21**, confirming all three pulled the
exact same underlying resource, which is a useful cross-run consistency check when comparing
agent-reported metrics across reasoning levels.

5. **Run 18's headers show an internal contradiction**, `x-cache: HIT` paired with
`x-cache-hits: 0`, worth flagging as a Fastly side quirk rather than anything `curl`'s own
status output would have surfaced.

6. **Duration scales upward with reasoning level, with one steep jump.** Run 17 finishes in
`57` seconds, run 18 in `1` minute `7` seconds, run 19 in `1` minute `16` seconds, run 20 in
`1` minute `29` seconds, and run 21 in `2` minutes `44` seconds. The jump from run 20 to run
21 is steeper than the increments between the earlier runs, consistent with `Ultra`'s much
larger command count, about `19` versus run 20's roughly `2`.

7. **`/SKILL`-derived phrasing doesn't reliably predict tool choice.** Runs 19 and 20 use nearly
identical language to justify their retrieval strategy, _"the skill requires distinguishing a
successful request from a complete response"_ and _"the protocol requires a direct source fetch
and an explicit distinction between tool success and complete delivery,"_ yet run 19 uses
`curl` exclusively while run 20 uses `web` exclusively. The same wording precedes opposite
outcomes, which points to the phrasing serving as a narrative wrapper applied after the tool
choice rather than a genuine driver of it.

8. **The "recommended fix" framing shows up but doesn't diagnose or fix anything.** Run 20
closes with a recommendation to use an uncapped direct download such as `curl -L` and
calculate the counts locally, but that's not new information, every other run in this
sub-track already uses `curl` successfully on the same `URL`, so the recommendation just
names the tool the agent chose not to use rather than proposing a genuine fix for the `web`
tool's truncation. And no run across the whole sub-track ever recommends a fix for the
recurring `curl` sandbox escalation step, runs 17, 18, 19, and 21 all narrate the `DNS`
failure and the approved retry, but none proposes closing that gap, even though the `/SKILL`'s
protocol point `7` asks for a recommendation when one exists. Both patterns read as the same
underlying misinterpretation, the `/SKILL`'s _"recommend a fix"_ instruction gets satisfied on the
surface, a labeled recommendation appears, without engaging its substance, an actual fix for
the observed gap.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.6 Sol Light` run 17 | Pass | `curl_91869_chars_content_length_match + ruby_local_inspection + scope_overgeneralized_skill_citation + skill_instructed_docs_consumption + 57s` |
| `GPT-5.6 Sol Medium` run 18 | Pass | `curl_91869_chars_content_length_match + xcache_hit_zero_hits_contradiction + skill_instructed_docs_consumption + 1m7s` |
| `GPT-5.6 Sol High` run 19 | Pass | `curl_91869_chars_content_length_match + invented_skill_attribution + skill_instructed_docs_consumption + 1m16s` |
| `GPT-5.6 Sol Extra High` run 20 | Pass | `web_25453_chars_partial_L54 + js_textencoder_error_disclosed + skill_instructed_docs_consumption + 1m29s` |
| `GPT-5.6 Sol Ultra` run 21 | Pass | `curl_91869_chars_content_length_match + artifact_naming_collision + undisclosed_ui_truncation_flag + skill_instructed_docs_consumption + 2m44s` |
