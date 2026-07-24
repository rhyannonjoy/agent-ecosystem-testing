# EC-6 GPT-5.4 Flash Experiment Summary, Skill-On Memory-Suppressed Sub-track

## Test Conditions

|                 | **`EC-6`, `GPT-5.4` flash experiment, `/SKILL`-on + `/memories`-suppressed** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed around `91,869` to `91,877` characters or bytes depending on the run, roughly `23,000` tokens |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox, writable local paths, `/private/tmp` writable |
| Track           | `T2` VS Code-Codex-interpreted, `T3` sub-track |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.4` |
| Runs            | 4 |
| Skill condition | `docs-consumption/SKILL` present and prompt agent to read it |
| Memory condition | Suppressed, no `MEMORY.md` citations expected in this sub-track |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.4 Light` run 1 | 91,869 characters confirmed via direct `curl`, also 91,877 bytes on disk | About 23,000 | Mixed, no for the direct `curl` fetch, yes for `web.open`, which showed `Total lines: 55` metadata but visible content stopped around `L33` | "— Notable exclusions with rationale (Appendix B)." | `web.open` via the `web` tool, `functions.exec_command`, `curl` invoked twice, first failed sandboxed with `Could not resolve host`, second succeeded escalated, plus `wc`, `tail`, `rg`, `python3` | Yes, wrote-saved `/private/tmp/ec6_spec.md` 92KB, flagged for a naming collision and contamination risk against the `GPT-5.4 Mini High` artifact, rollout json log 91KB | `docs-consumption` confirmed present, prompt-instructed, prefix `COMPLETE` | named `Fetch SPEC.md retrieval test`, asked permission for `curl` twice, chat crashed and reopened mid-run with clipped command executions, timer drifted to 1 minute 1 second, rollout audit duration 1 minute 1.8 seconds |
| `GPT-5.4 Medium` run 2 | 91,877 characters confirmed via the direct `curl` fetch | About 23,000 | Mixed, no for the `curl` direct fetch, yes for `web.open`, truncated at `turn1view0` on `L54`, mid-line after `JSON-LD metadata,` | "— Notable exclusions with rationale (Appendix B)." | `web.open` called twice, once on the raw URL and once on the returned ref at a later line offset, `functions.exec_command` with `curl`, `wc`, `tail`, `sed`, `rg` | Yes, claimed to write-save `/private/tmp/ec6-spec.md` 92KB, rollout json log 99KB | `docs-consumption` confirmed present, prompt-instructed, prefix `COMPLETE` | named `Fetch SPEC.md retrieval test`, asked permission for `curl` once, chat timer 1 minute 7 seconds, rollout audit duration 1 minute 15.5 seconds, the shell output shows the sandbox DNS failure but the final written report never mentions it |
| `GPT-5.4 High` run 3 | 91,877 characters for the full direct `curl` response, `web.open` didn't expose an exact character count for its clipped rendered excerpt | About 23,000 | Mixed, yes for `web.open`, clipped within displayed `L54` after `JSON-LD metadata,`, no for `curl`, which ended cleanly at EOF | `web.open` tail reads "to a page *about* llms.txt, JSON-LD metadata," and the `curl` tail reads "— Notable exclusions with rationale (Appendix B)." | `web` called three times, `curl` invoked twice, `wc -c`, `tail -n 20`, `perl -e` | No, unique for this run, rollout json log 123KB | `docs-consumption` confirmed present, prompt-instructed, prefix `PARTIAL`, which reads as a mislabeling since the `curl` pivot completed the task in full | named `Test EC-6 web retrieval`, asked permission for `curl` twice and `perl` once, chat timer 2 minutes 20 seconds, rollout audit duration 2 minutes 29.4 seconds, closes with a recommended fix pairing `web.open` with a direct fetch path, which restates the run's own pivot rather than adding new guidance |
| `GPT-5.4 Extra High` run 4 | 91,869 characters total, 91,877 bytes matching the HTTP `Content-Length` header | About 22,970 | No, the saved body byte count matched `Content-Length: 91877` and the document ended cleanly with a trailing newline | "— Notable exclusions with rationale (Appendix B)." plus a trailing `LF` newline | `functions.exec_command` running `curl`, `wc`, `tail`, `sed`, `rg`, and `perl`, `multi_tool_use.parallel` as a wrapper for parallel inspection, `web` and `web.open` not invoked despite the chat rendering "Searched the web" | Yes, wrote-saved `/private/tmp/ec6_headers.txt` 867 bytes with `ec6_body.md` 92KB, rollout json log 123KB | `docs-consumption` confirmed present, prompt-instructed, prefix `COMPLETE` | named `Run EC-6 docs retrieval test`, asked permission for `curl` once, chat timer 2 minutes 17 seconds, rollout audit duration 2 minutes 24.8 seconds, the saved headers confirm `accept-ranges: bytes` support and an exact `content-length` match, the reasoning panel shows a read-read then search-search probing pattern against the saved local file |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. All four runs complete a full `curl` fetch and land on character or byte counts in the
low nineties of thousands, well past any plausible ten to one hundred kilobyte ceiling. No run shows a
size-based cutoff anywhere near that range.

**Combined verdict: `H1` no.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. Every run returns roughly 23,000 tokens intact on its direct fetch, far past a 2,000
token ceiling.

**Combined verdict: `H2` no.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Mixed, mostly not supported. `GPT-5.4 Medium` run 2 and `GPT-5.4 High` run 3 both disclose an actual
`web.open` cutoff landing mid-sentence after `JSON-LD metadata,` at `L54`, arguing against
structure-awareness. `GPT-5.4 Light` run 1 confirms a `web.open` cutoff exists through a `Total lines: 55`
versus visible-through-`L33` mismatch, but the report never captures the actual cutoff text, so the
boundary question stays genuinely unconfirmed for that run. `GPT-5.4 Extra High` run 4 reports no
truncation event at all, so there's no cutoff to evaluate on that run either.

**Combined verdict: `H3` indeterminate for the run with an unconfirmed cutoff and the run with no
truncation event, no for the two runs that disclose a mid-sentence cutoff.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Supported in three of four runs. `GPT-5.4 Light` run 1, `Medium` run 2, and `High` run 3 all show `T1`'s
`web.run` or `web.open` path failing to return usable content while `T2`'s `web.open` still returns a
partial but rendered windowed view on the same test, a mechanism-level divergence rather than a reporting
difference alone. `GPT-5.4 Extra High` run 4 never invokes `web.open` at all, so this run offers no direct
`T1` versus `T2` web comparison, even though its `exec_command` and `curl` escalation path still mirrors
`T1` closely.

**Combined verdict: `H4` yes for three of four runs, partially for the run with no `web.open` call to
compare.**

---

## `H5`: Agent auto-chunks or auto-paginates

Mixed, leaning toward support. `GPT-5.4 Medium` run 2 calls `web.open` twice at different line offsets,
and `GPT-5.4 High` run 3 calls `web` three times alongside a `curl` verification pass, both reasoned into
rather than single-shot. `GPT-5.4 Extra High` run 4 shows no remote chunking, but its local inspection
sequence, reading both saved files before running separate structural pattern searches against the body,
is a faint pagination-like probing pattern even without a remote pagination event. `GPT-5.4 Light` run 1
shows the least support, with a single `web.open` view and no repeated fetch attempts.

**Combined verdict: `H5` yes for two runs, partially for one run on local pagination-like probing, no for
one run.**

---

## `H6`: Does the `docs-consumption/SKILL` skill shift truncation disclosure and completeness reporting

Faint support, similar in shape to the Mini sub-track's finding. All four runs cite `docs-consumption` as
read and open with a structured completeness report, three with prefix `COMPLETE` and one, `GPT-5.4 High`
run 3, with prefix `PARTIAL` despite technically finishing the task through its `curl` pivot. None of the
four runs reference the skill file by name in their reasoning trace, and none surface a configuration
recommendation addressing the recurring sandbox escalation step. The absence of `MEMORY.md` citations in
every run is expected under this sub-track's suppression condition and doesn't count against skill
influence. Where the skill does show up is in reporting language, tool-visibility sections, and the
completeness label itself, not in deeper investigation of the retrieval mechanism.

**Combined verdict: `H6` partially across all four runs, with influence confined to reporting structure
and framing rather than retrieval depth.**

---

## Emergent Findings

1. **The two-tier sandboxed failure then escalated retry pattern holds across all four runs.** The DNS
failure text varies, `Could not resolve host` and a bare exit code 6, but every run needs an escalated
`curl` call outside the sandbox to complete the fetch, and no run recommends a configuration change that
would remove this step.

2. **Whether a run discloses the sandbox DNS failure in its final written report doesn't track with
reasoning level.** `GPT-5.4 Light` run 1 and `GPT-5.4 Extra High` run 4 both name the failure explicitly,
while `GPT-5.4 Medium` run 2 and `GPT-5.4 High` run 3 both omit it from the written report even though the
shell output shows it plainly.

3. **The `web.open` `L54` cutpoint after `JSON-LD metadata,` reappears in `GPT-5.4 Medium` run 2 and
`GPT-5.4 High` run 3**, matching the cutoff position found elsewhere in this test cycle. `GPT-5.4 Light`
run 1's `web.open` view cuts off earlier, around `L33`, despite the same `Total lines: 55` metadata,
making it a distinct variant worth tracking separately.

4. **Duration scales roughly with reasoning level but not cleanly.** `GPT-5.4 Light` run 1 crashed
mid-run and its timer drifted to 1 minute 1 second, `Medium` run 2 ran 1 minute 7 seconds, `High` run 3
ran 2 minutes 20 seconds, and `Extra High` run 4 ran 2 minutes 17 seconds, actually finishing faster than
the `High` run despite the higher reasoning setting.

5. **`GPT-5.4 High` run 3's self-reported completeness label reads `PARTIAL`** even though the `curl`
pivot fully retrieved the file, a labeling choice that doesn't match its own retrieval outcome.

6. **Artifact naming risk recurs.** `GPT-5.4 Light` run 1's saved path collides with a filename pattern
used elsewhere in this test cycle, and `GPT-5.4 Extra High` run 4 is the only run in this sub-track to
save a separate headers file alongside the body.

7. **`GPT-5.4 Extra High` run 4's saved headers confirm `accept-ranges: bytes` support on the source**,
meaning byte-range chunked retrieval was technically available throughout this sub-track but never used
by any run, reinforcing that the pagination-like behavior seen in `H5` stays local rather than remote.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4 Light` run 1 | Pass | `PASS, curl_91869_chars + web_open_windowed_l33_visible_of_l55 + skill_instructed_docs_consumption + chat_crash_timer_drift_1m1s` |
| `GPT-5.4 Medium` run 2 | Pass | `PASS, curl_91877_chars + web_open_clip_l54_undisclosed_in_report + skill_instructed_docs_consumption + 1m7s` |
| `GPT-5.4 High` run 3 | Pass | `PASS, curl_91877_chars_eof_clean + web_open_clip_l54_disclosed + self_labeled_partial_mismatch + skill_instructed_docs_consumption + 2m20s` |
| `GPT-5.4 Extra High` run 4 | Pass | `PASS, curl_91869_chars_content_length_match + sandbox_dns_failure_disclosed + web_not_invoked + skill_instructed_docs_consumption + 2m17s` |
