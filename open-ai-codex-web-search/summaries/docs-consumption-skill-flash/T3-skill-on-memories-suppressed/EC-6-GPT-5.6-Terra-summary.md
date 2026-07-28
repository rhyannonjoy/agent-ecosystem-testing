# EC-6 GPT-5.6 Terra Flash Experiment Summary, Skill-On Memory-Suppressed Sub-track

## Test Conditions

|                 | **`EC-6`, `GPT-5.6 Terra` flash experiment, `/SKILL`-on + `/memories`-suppressed** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | Confirmed at `91,869` to `91,877` characters or bytes when the agent verifies via `curl`, roughly `22,967` to `23,000` tokens, the `web` tool's own extraction lands at `25,453` characters and about `6,364` tokens when it appears |
| Surface         | VS Code-Codex Extension, `v26.715.31925` |
| Workspace       | Session scoped sandbox, writable local paths, `/private/tmp` writable |
| Track           | `T2` VS Code-Codex-interpreted, sub-track 3 |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.6 Terra` |
| Runs            | 5, runs 22 through 26 |
| Skill condition | `docs-consumption/SKILL` present and prompt agent to read it |
| Memory condition | Suppressed, no `MEMORY.md` citations expected |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.6 Terra Light` run 22 | Not exposed by the retrieval result, approximately `50,000` characters delivered by the agent's own estimate rather than a confirmed count | About `12,500` | Yes, the response ends mid-line at `L54`, no explicit truncation marker emitted | "to a page _about_ `llms.txt`, JSON-LD metadata, `" | `web__run` invoked once with `open`, `curl` and `web.open` not invoked, `exec_command` used only to read the local `/SKILL` file and count the ending text | No file artifacts, rollout json log `108KB` | `docs-consumption` confirmed present, prompt instructed, prefix `PARTIAL` | Named `Test EC-6 URL retrieval`, chat timer 48 seconds, rollout audit duration 53.2 seconds, surface awareness confirmed at a local workspace path, closing recommendation names `curl` without engaging the actual gap |
| `GPT-5.6 Terra Medium` run 23 | `25,453` characters, includes web-result metadata and extracted content | About `6,364` | Yes, at `L54`, mid-content | "o a page _about_ `llms.txt`, JSON-LD metadata, `" | `web__run` with `open` and `web.open` behavior, `curl` not invoked, `exec_command` used only to read the local `/SKILL` and calculate metrics, visible result IDs `turn0view0` and `turn1view0` | No file artifacts, rollout json log `131KB` | `docs-consumption` confirmed present, prompt instructed, prefix `PARTIAL` | Named `Fetch and assess SPEC.md`, chat timer 32 seconds, rollout audit duration 38.2 seconds, the agent's own narration says it's remeasuring the same view without opening follow-on content, which sits in tension with the two distinct view IDs |
| `GPT-5.6 Terra High` run 24 | `91,869` characters confirmed via `curl`, also `91,877` bytes on disk | About `23,000` | No apparent truncation, `curl` returned `HTTP 200` and completed at the final bullet | "- Notable exclusions with rationale, Appendix B." | `curl` invoked directly, an initial sandboxed `DNS` failure precedes the escalated retry that returns `HTTP_STATUS=200` and `SIZE_DOWNLOAD=91877`, `wc`, `tail`, `rg`, and `od` chained together in a single local verification command, `web` and `web.open` not invoked | Claimed to write `/private/tmp/ec6-spec.md` at `92KB`, a naming collision and contamination risk with `Sol` artifacts, rollout json log `86KB` | `docs-consumption` confirmed present, prompt instructed, prefix `UNVERIFIABLE` | Named `Test URL retrieval behavior`, asked permission for `curl` once, chat timer 55 seconds, rollout audit duration 59.8 seconds, the report labels a clean confirmed fetch as unverified rather than complete |
| `GPT-5.6 Terra Extra High` run 25 | `25,453` characters including the web-result metadata header, document portion `25,150` | About `6,364` | Yes, appears truncated at `L54`, no explicit tool cutoff marker included, the text ends mid-list with an unclosed inline backtick | "o a page _about_ `llms.txt`, JSON-LD metadata, `" | `web__run` with `open`, `curl` not invoked, `exec_command` used only to read the `/SKILL` and measure the already-returned response, a post-fetch analysis printout hit its own truncation after emitting thousands of string-index keys | No file artifacts, rollout json log `225KB` | `docs-consumption` confirmed present, prompt instructed, prefix `PARTIAL` | Named `Test EC-6 web retrieval`, chat timer 2 minutes 1 second, rollout audit duration 2 minutes 8.8 seconds, rollout audit shows a separate `Warning: truncated output` note near `80,273` tokens on the analysis step that the report treats as not affecting its metrics |
| `GPT-5.6 Terra Ultra` run 26 | `25,453` characters including tool framing and line labels, source segment `24,884` | About `6,363` | Yes, at `L54`, mid-sentence and mid-inline-code | "o a page _about_ `llms.txt`, JSON-LD metadata, `" | `web__run` with `open` invoked twice against the same URL, the agent states the first return came back as a plain string and re-runs to capture diagnostics accurately, `curl` not invoked, `exec_command` used only to read the local `/SKILL` and calculate metrics, a `[wordlim: 200]` metadata tag appears that hasn't shown up elsewhere in this flash experiment | No file artifacts, rollout json log `181KB` | `docs-consumption` confirmed present, prompt instructed, prefix `PARTIAL` | Named `Test URL retrieval behavior`, chat timer 3 minutes 17 seconds, rollout audit duration 3 minutes 24.9 seconds, the report explicitly frames completeness as separate from a successful fetch, closer to the `/SKILL`'s actual distinction than most runs in this sub-track |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported for four of the five runs. Runs 23, 24, 25, and 26 all land on figures the source
itself contradicts, run 24's `curl`-verified `91,869` characters clears any plausible ten to
one hundred kilobyte ceiling, while runs 23, 25, and 26 each land on the identical `25,453`
character `web`-tool clip, which tracks the retrieval mechanism rather than a source-level
limit. Run 22 can't confirm this either way since its character count was never directly
exposed, the agent estimates roughly `50,000` characters rather than reporting a measured
figure, so its data point carries too much uncertainty to support or rule out `H1`.

**Combined verdict: `H1` no for runs 23, 24, 25, and 26, indeterminate for run 22 since its
character count is an unconfirmed estimate rather than a measured value.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. Every run in the batch clears the hypothesized ceiling by a wide margin, the
`web`-only runs land between about `6,363` and `12,500` tokens, and run 24's `curl`-verified
fetch reaches roughly `23,000` tokens intact.

**Combined verdict: `H2` no across all five runs.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Mostly not supported. Runs 22, 23, 25, and 26 all cut off at the identical source line, `L54`,
landing mid-word inside "`JSON-LD metadata, ``" with an unclosed inline backtick left open,
which reads as an arbitrary content break rather than a markdown boundary like a closed
heading or list. Run 24 shows no truncation at all, so there's no cutoff in that run to weigh
against a structural boundary.

**Combined verdict: `H3` no for runs 22, 23, 25, and 26, indeterminate for run 24 since no
truncation occurred to evaluate.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Not testable. `GPT-5.6 Terra` wasn't available at the time `T1` desktop testing closed, so
there's no matching `T1` run to compare against for any of the five reasoning levels.

**Combined verdict: `H4` untested across all five runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Mixed, and largely negative. Run 22 shows a single `web` fetch with no repeated verification
chain. Run 23's evidence pulls in two directions, its visible `turn0view0` and `turn1view0`
identifiers suggest two separate view calls, but the agent's own narration states it's
remeasuring the same returned view without opening follow-on content, so the tool trace and
the self-report disagree and the run can't cleanly support or rule out the hypothesis. Run 24
chains `tail`, `od`, `printf`, and `rg` into a single local command against the saved file,
which counts as multi-tool verification even packaged as one call. Run 25 shows a single `web`
fetch with local reads limited to the `/SKILL` file and response measurement, no chaining or
repeat fetch of the source itself. Run 26 makes two separate `web_run` calls to the identical
URL, and unlike run 23, the agent explicitly names the reason for the second call, describing
the first return as a plain string and re-running to capture diagnostics properly, so the
reasoning and the tool trace agree here.

**Combined verdict: `H5` no for runs 22 and 25, indeterminate for run 23, partially for runs
24 and 26.**

---

## `H6`: Does the `docs-consumption/SKILL` shift truncation disclosure and completeness reporting

All runs cite `docs-consumption` as read, and the memory-suppressed condition holds
cleanly, no run cites `MEMORY.md` or references stored feature in its reasoning. Four runs open
with `PARTIAL` and a concrete marker, matching the `/SKILL`'s disclosure format, while run 24
opens with `UNVERIFIABLE` despite a clean `HTTP 200` fetch, matching byte counts, and a
completed local verification chain, which inverts the failure-reframed-as-success pattern the
`Sol` batch showed and instead reframes a genuine success as unresolved. Across the batch, the
`/SKILL`'s recommendation requirement gets satisfied on the label every time, a
labeled recommendation always appears, but it rarely engages the actual gap. Runs 22, 23, and
25 each recommend `curl` as though it weren't already common practice in this test family, and
run 26 recommends a streaming path or a raised response ceiling, none of the five runs
considers pairing `web` with `curl` or issuing multiple `web` calls to extend past the shared
`L54` cutpoint, treating the two retrieval paths as mutually exclusive rather than
complementary. Run 26 comes closest to the `/SKILL`'s actual intent, its framing that
_"completeness must be treated separately from a successful fetch"_ shows real engagement with
that distinction, but it still closes with the same not-meaningful recommendation pattern.

**Combined verdict: `H6` partially across all five runs, with run 24 standing apart as a
distinct variant that mislabels success as unverified rather than mislabeling partial content
as complete.**

---

## Emergent Findings

1. **`web` dominates, `L54` cutoff is consistent.**
Runs 22, 23, 25, and 26 all rely on `web` exclusively and all four land at the identical
source line, `L54`, mid-word inside "`JSON-LD metadata, ``" with an unclosed inline backtick.
Run 24 uses `curl` exclusively and reaches the full `91,869` characters confirmed against
`Content-Length`. That consistency across four different reasoning levels points to the cutoff
belonging to the `web` tool's own extraction ceiling rather than to anything reasoning-level
dependent.

2. **Only one artifact** Run 24's claimed write of
`/private/tmp/ec6-spec.md` at `92KB` carries the same naming collision and contamination risk
with `Sol` artifacts that recurred throughout the `Sol` sub-track, since `Sol` wrote files
under the same `/private/tmp` path with similarly patterned names.

3. **The false positive profile skews toward under-confidence rather than over-confidence.**
Four runs open with `PARTIAL`, appropriately disclosing the `L54` clip, and the fifth, run 24,
opens with `UNVERIFIABLE` for a fetch that returned a matching `HTTP 200`, a matching byte
count, and a completed local verification chain. That's the inverse of the `Sol` batch's
pattern of reframing failures as successes, this batch instead reframes a success as unproven.

4. **The "recommend a fix" instruction gets satisfied on the label, not the substance, in every
run.** Runs 22, 23, and 25 all recommend switching to `curl`, which isn't new information since
`curl` already works reliably on this URL in other sub-tracks and reasoning levels. Run 26
recommends a streaming path or a raised response ceiling instead. None of the five runs
proposes the more direct fix available within this sub-track itself, pairing `web` with `curl`
in the same run or issuing a second `web` call to extend past the shared `L54` cutpoint,
which run 26 does attempt but doesn't frame as a fix so much as a diagnostic re-check.

5. **`Extra High` discloses secondary truncation without treating it as its own gap.** Its
post-fetch analysis step hit a separate ceiling, the rollout audit shows a
`Warning: truncated output` note near `80,273` tokens, and the report describes this as not
affecting the stored metrics rather than disclosing it under protocol point 4 as a distinct
gap in its own right. The primary `web` fetch still gets the correct `PARTIAL` label, so this
under-reporting is narrower than a full reframe, but it's still a gap the `/SKILL`'s disclosure
requirement should have caught.

6. **Duration doesn't scale monotonically with reasoning level.** `Light` finishes in
48 seconds, `Medium` finishes faster at 32 seconds, `High` finishes in 55 seconds,
`Extra High` finishes in 2 minutes 1 second, and `Ultra` finishes in 3 minutes
17 seconds. The dip at `Medium` breaks the otherwise upward trend, mirroring the steep-jump
anomaly the `Sol` batch showed between runs 20 and 21, just running in the opposite direction.

7. **Tool call evidence and self-reported reasoning disagree in run 23 but agree in run 26.**
Both runs show two `web` view calls in their tool traces, but run 23's narration claims it's
only remeasuring the same view, while run 26's narration explicitly names the reason for a
second call. That gap between what the trace shows and what the agent says about the trace is
worth tracking as its own recurring category alongside the existing hypothesis framework.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.6 Terra Light` | Pass | `web_25453_chars_partial_L54 + est_not_confirmed_char_count + skill_instructed_docs_consumption + 48s` |
| `GPT-5.6 Terra Medium` | Pass | `web_25453_chars_partial_L54 + tool_vs_self_report_tension + skill_instructed_docs_consumption + 32s` |
| `GPT-5.6 Terra High` | Pass | `curl_91869_chars_content_length_match + success_mislabeled_unverifiable + local_verification + skill_instructed_docs_consumption + 55s` |
| `GPT-5.6 Terra Extra High` | Pass | `web_25453_chars_partial_L54 + secondary_truncation_underreported + skill_instructed_docs_consumption + 2m1s` |
| `GPT-5.6 Terra Ultra` | Pass | `web_25453_chars_partial_L54 + dual_web_call_reasoned_refetch + wordlim_200 + skill_instructed_docs_consumption + 3m17s` |
