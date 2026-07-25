# EC-6 GPT-5.4-Mini Flash Experiment Summary, Skill-On Memory-Suppressed Sub-track

## Test Conditions

|                 | **`EC-6`, `GPT-5.4 Mini` flash experiment, `/SKILL`-on + `/memories`-suppressed** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed `91,869` characters, `91,877` bytes via `curl`, roughly `23,000` tokens |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox, writable local paths, `/private/tmp` writable |
| Track           | `T2` VS Code-Codex-interpreted, `T3` sub-track |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.4 Mini` |
| Runs            | 4 |
| Skill condition | `docs-consumption/SKILL` present and prompt agent to read it |
| Memory condition | Suppressed, no `MEMORY.md` citations expected in this sub-track |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.4-Mini Light` run 1 | Not confirmed, the `curl` attempt hit a `dns_blocked` failure and the visible `web` fragment stayed unverified | Roughly 8,000 to 12,000, built on the unverified visible portion | Yes, "ending mid-sentence after `JSON-LD metadata,`" at `L54` | Not reliably recoverable, the visible cutoff fragment was `JSON-LD metadata, ` | `web_search` four times per the rollout, reported in chat as `web`, `curl` failed once via `exec_command` | No, rollout json log 86KB, artifact `ec-6-spec.jEMRjV` zero bytes and unreadable | `docs-consumption` confirmed present, prompt-instructed, prefix `UNVERIFIABLE` | named `Fetch SPEC.md retrieval test`, didn't ask permission for `curl`, worked 37 seconds, rollout audit 41.9 seconds |
| `GPT-5.4-Mini Medium` run 2 | 91,869 characters, 91,877 bytes confirmed via `curl` and the `content-length` header | About 23,000 | No in the final report, though the reasoning trace called the `web` view line-windowed before the direct fetch superseded it | "— Notable exclusions with rationale (Appendix B)." | `curl`, a failed `urllib.request.urlopen` attempt, `web` called four times, `exec_command` for local checks | Yes, `agent-docs-spec-SPEC.md` 92KB, rollout json log 115KB | `docs-consumption` confirmed present, prompt-instructed, prefix `COMPLETE` | named `Fetch EC-6 specification`, asked permission for `curl` once, worked 1 minute 18 seconds, rollout audit 1 minute 23.4 seconds, headers exposed in chat but not saved as an artifact |
| `GPT-5.4-Mini High` run 3 | 91,869 characters confirmed via direct `curl` fetch | About 23,000 | Mixed, no in the raw `curl` fetch, yes in the `web` display window, cut off after `JSON-LD metadata,` at `L54` | "— Notable exclusions with rationale (Appendix B)." | `web` called five times, `curl` invoked twice, once sandboxed and once escalated, `exec_command` | Yes, `ec6_spec.md` 92KB, rollout json log 123KB | `docs-consumption` confirmed present, prompt-instructed, prefix `COMPLETE` | named `Fetch and assess SPEC.md retrieval`, asked permission for `curl` once, worked 1 minute 45 seconds, rollout audit 1 minute 49.5 seconds |
| `GPT-5.4-Mini Extra High` run 4 | 91,869 characters, 91,877 bytes confirmed via the `content-length` header | About 20,500, using a local regex heuristic since `tiktoken` wasn't available | No, the body size matched `content-length: 91877` and the file ended cleanly with a trailing newline | "— Notable exclusions with rationale (Appendix B).\n" | `curl` once, `wc`, `tail`, `awk`, `python3`, `exec_command` eleven times per the rollout, no `web_search` calls despite the chat rendering "Searched the web" | Yes, `ec6-spec.headers` 870 bytes, `ec6-spec.md` 92KB, rollout json log 258KB | `docs-consumption` confirmed present, prompt-instructed, prefix `COMPLETE` | named `Fetch SPEC.md retrieval test`, asked permission for `curl` once, worked 6 minutes 26 seconds, rollout audit 6 minutes 31.3 seconds, two recovered failures, `sandbox_empty_response` and `capability_abandonment`, neither disclosed in the final report |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. Three of the four runs complete a full `curl` fetch and land on the identical `91,869`
characters or `91,877` bytes, well past any plausible ten to one hundred kilobyte ceiling. The one exception,
`GPT-5.4-Mini Light` run 1, never confirms a byte count because its `curl` attempt hit a `dns_blocked` failure
and the agent didn't retry, so its lower estimate reflects an incomplete fetch, not a platform ceiling.

**Combined verdict: `H1` no. The one run without a confirmed size failed its fetch rather than hitting a ceiling.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. Every completed fetch returns roughly `23,000` tokens intact, far past a `2,000` token ceiling.
The lower estimate in `GPT-5.4-Mini Light` run 1 traces back to the same incomplete fetch, not a token limit.

**Combined verdict: `H2` no.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Mixed, mostly not supported. Three of the four runs show an actual truncation event in the `web` view,
and both `GPT-5.4-Mini Light` run 1 and `GPT-5.4-Mini High` run 3 disclose it landing mid-sentence after
`JSON-LD metadata,` rather than on a heading, list break, or code fence, arguing against structure-awareness.
`GPT-5.4-Mini Medium` run 2 also shows the same cutoff in its reasoning trace, but the final report never
discloses it, leaving the classification for that run genuinely unresolved rather than a clean no.
`GPT-5.4-Mini Extra High` run 4 reports no truncation at all, so there's no cutoff to evaluate on that run.

**Combined verdict: `H3` indeterminate for the run with no truncation and the run with an undisclosed
truncation event, no for the two runs that disclose a cutoff, since both land mid-sentence.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Partially. Final character counts converge with `T1` in three of the four runs, `GPT-5.4-Mini Medium` run 2,
`High` run 3, and `Extra High` run 4 all land on the same complete payload as their matched `T1` runs. The
retrieval process still diverges in every run, since all four hit the same underlying sandbox-blocks-network
condition before an escalated `curl` call, whether that surfaces as a `dns_blocked` error, an exit code 6
resolution failure, or a `sandbox_empty_response`. `GPT-5.4-Mini Light` run 1 shows the sharpest divergence,
since its `T1` counterpart returns a full clean file while this run never confirms a byte count at all.

**Combined verdict: `H4` partially. Final payloads converge with `T1` in three of four runs, but the retrieval
path consistently diverges due to the recurring sandbox escalation step, and one run fails to converge at all.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially. `GPT-5.4-Mini Light` run 1 calls `web_search` four times, `Medium` run 2 chains a failed
`urllib.request.urlopen` attempt into a failed sandboxed `curl` and four `web` calls before an escalated
`curl` succeeds, and `High` run 3 calls `web` five times alongside two `curl` attempts. None of these three
runs confirm that each web call retrieved a different slice of content rather than re-rendering the same
view, so the chaining is consistent with pagination without confirming it at the content level.
`GPT-5.4-Mini Extra High` run 4 breaks this pattern entirely, with a single successful `curl` call, no `web`
calls, and no repeated fetch attempts, only local post-processing commands against the already-saved file.

**Combined verdict: `H5` partially. Repeated `web` calls appear in three of the four runs, but content-level
pagination isn't confirmed in any of them, and the fourth run shows no chaining at all.**

---

## `H6`: Does the `docs-consumption/SKILL` skill truncation disclosure and completeness reporting

Faint support, similar in shape to the `skill opt-in` sub-track but without its secondary signal. No run in
this sub-track ever surfaces a configuration recommendation addressing the recurring sandbox escalation step,
the specific behavior this experiment targets, even in `GPT-5.4-Mini Extra High` run 4, where the agent
diagnosed a `content-length` match and a clean trailing newline but still left both the `sandbox_empty_response`
failure and the abandoned `tiktoken` check out of its final report. `H6` support in this sub-track rests entirely
on completeness and truncation language. That language is more decisive than a no-skill baseline in `Medium` run 2
and `High` run 3, both of which explicitly separate raw-fetch truncation from `web` display truncation, but
`Light` run 1's regression to an unverified partial fetch shows the skill doesn't reliably preserve retrieval
quality either.

**Combined verdict: `H6` partially, with faint support. The skill correlates with more decisive completeness
and truncation language in three of four runs, but never produces the configuration guidance this experiment
intends to detect, and doesn't reliably improve or preserve retrieval quality.**

---

## Emergent Findings

1. **The two-tier sandboxed failure, then escalated retry, pattern holds across all four runs.** The surface
error text varies, a `dns_blocked` label, an exit code 6 resolution failure, and a `sandbox_empty_response`
all describe the same underlying condition, the sandbox blocks network access by default and requires an
escalated `curl` call to complete. No run ever recommends a configuration change that would remove this step.

2. **`GPT-5.4-Mini Light` run 1 is the only genuine retrieval failure in this batch.** Its `curl` attempt never
recovered a confirmed byte count, a distinct outcome from every other run in this sub-track, which completed
a full fetch. This mirrors the `Light`-reasoning failure pattern seen in the `skill opt-in` sub-track as well.

3. **Duration doesn't track cleanly with reasoning level.** `Extra High` run 4 takes 6 minutes 26 seconds,
far longer than `High` run 3's 1 minute 45 seconds, driven mostly by extensive local verification steps,
a fence check, a `tiktoken` availability check, and a regex-based token estimate, rather than retrieval
difficulty itself.

4. **The `web` `L54` cutpoint reappears across three of the four runs.** `Light` run 1, `Medium` run 2,
and `High` run 3 all show the same mid-sentence cutoff after `JSON-LD metadata,` matching the base cycle's
finding of an identical cutoff position across models and reasoning levels.

5. **Self-report gaps persist even at the highest reasoning level.** `Extra High` run 4 produces the most
evidence-grounded report in the sub-track, exact byte match, closed fence count, verified trailing newline,
yet still omits both its `sandbox_empty_response` failure and its abandoned `tiktoken` attempt, suggesting
more reasoning effort sharpens the final classification without necessarily improving disclosure.

6. **Chat-versus-audit tool count mismatches appear in `Medium` run 2 and `High` run 3.** Both show chat
commentary citing a different `web` or command count than the rollout audit reports.

7. **Artifact anomalies recur.** `Light` run 1's saved artifact came back as zero bytes and unreadable, while
`Extra High` run 4 is the only run to save a separate headers file alongside the body.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Light` run 1 | Fail | `FAIL, curl_dns_blocked + web_open_partial_only + skill_instructed_docs_consumption + 37s` |
| `GPT-5.4-Mini Medium` run 2 | Pass | `PASS, curl_91877_bytes + web_view_truncation_undisclosed + skill_instructed_docs_consumption + 1m18s` |
| `GPT-5.4-Mini High` run 3 | Pass | `PASS, curl_91869_chars + web_open_clip_l54_disclosed + skill_instructed_docs_consumption + 1min45s` |
| `GPT-5.4-Mini Extra High` run 4 | Pass | `PASS, curl_91869_chars + sandbox_empty_response_then_escalated + tiktoken_unavailable_undisclosed + skill_instructed_docs_consumption + 6m26s` |
