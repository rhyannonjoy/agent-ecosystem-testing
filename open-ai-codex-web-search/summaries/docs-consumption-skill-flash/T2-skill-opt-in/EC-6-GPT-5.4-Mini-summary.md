# EC-6 GPT-5.4-Mini Flash Experiment Summary

## Test Conditions

|                 | **EC-6, GPT-5.4-Mini flash experiment** |
| --------------- | ---------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt, actual confirmed `91,869` characters, `91,877` bytes via `curl`, roughly `23,000` tokens |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox, `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing` writable, `/private/tmp` also writable |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Model           | `GPT-5.4-Mini` only |
| Runs            | 9 |
| Skill condition | `docs-consumption` skill present in the project root but outside `.agents`, so discovery requires the agent to read it unprompted rather than auto-load it |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Skill signal | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ------------- | ----- |
| `GPT-5.4-Mini Light` flash run 1 | 91,877 | ~23,000 | No in the direct fetch, `web.open` clipped at the end of `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `perl` | No, rollout json log 66KB | None, predates any `docs-consumption` signal in the rollout log | named `Test web retrieval`, asked permission for `curl` once, worked 40 seconds |
| `GPT-5.4-Mini Medium` flash run 1 | 91,877 | ~23,000 | No for the direct fetch body, `web.open` display truncated near the closing Appendix B section | `— Notable exclusions with rationale (Appendix B).` | `web`, `curl` | No, rollout json log 78KB | None | named `Fetch SPEC.md`, asked permission for `curl` twice, worked 1 minute, first appearance of the chat-versus-audit tool count mismatch |
| `GPT-5.4-Mini High` flash run 1 | 91,869 | ~22,970 | No in the fetched HTTP payload, the `exec_command` streamed preview display-truncated after roughly `22,970` output tokens | `— Notable exclusions with rationale (Appendix B).` | `web`, `curl`, `wc`, `tail`, `od`, `awk` | Yes, `/private/tmp/ec6_SPEC.md` 92KB | `docs-consumption` present in the project root, not discovered | named `Test web retrieval`, asked permission for `curl` twice, worked 1 minute 50 seconds, a local fetch attempt failed before the escalated network `curl` succeeded |
| `GPT-5.4-Mini Extra High` flash run 1 | 91,869 | ~18,000 | No in the raw fetch, `web.open` preview cut off mid-sentence at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open` called three times, `curl`, `python3` | Yes, `/private/tmp/ec6_SPEC_fetched.md` 92KB | `docs-consumption` present, not discovered | named `Fetch SPEC.md EC-6`, asked permission for `curl` once, worked 5 minutes 29 seconds, the most expensive run in this batch |
| `GPT-5.4-Mini Light` flash run 2 | Not confirmed, the `curl` attempt failed and wasn't retried | ~3,500 to 5,000, built on the unverified estimate | Yes, "the content appears truncated at the end of line 54" | Not verified, the agent flagged it couldn't confirm the true tail | `web` called three times, `curl` | No, rollout json log 68KB | `docs-consumption` confirmed present in the rollout log, first skill-on run | named `Test web retrieval`, didn't ask permission for `curl`, didn't examine the `curl` failure, worked 28 seconds |
| `GPT-5.4-Mini Light` flash run 3 | 91,869 | ~23,000 | No, "the retrieved body was 1,722 lines long, consistent with a full document fetch" | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `python3`, `wc`, `tail` | Yes, `/private/tmp/ec6_SPEC.md` 92KB | `docs-consumption` confirmed present, not named by the agent | named `Test web retrieval`, asked permission for `curl` once, worked 40 seconds |
| `GPT-5.4-Mini Medium` flash run 2 | 91,877 | ~23,000 | No for the direct `curl` fetch, `web.open` preview truncated mid-line around `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open` called three times, `curl`, `wc`, `tail`, `rg` | Yes, `/private/tmp/agent-docs-spec-SPEC.md` 92KB | `docs-consumption` confirmed present, not named by the agent | named `Test web retrieval`, asked permission for `curl` once, worked 1 minute 29 seconds, the agent's own report calls the pattern clearly paginated |
| `GPT-5.4-Mini High` flash run 2 | 91,877 | ~23,000 | No, "it looks like the full content was retrieved, with a natural ending and no signs of cutoff" | `— Notable exclusions with rationale (Appendix B).` | `exec_command` with `curl` and `perl`, `web` and `web.open` weren't used | No, rollout json log 101KB | `docs-consumption` confirmed present, the agent cited unrelated `MEMORY.md` content instead | named `Measure SPEC.md retrieval`, asked permission for `curl` twice, worked 1 minute 17 seconds, the first sandboxed `curl` attempt failed with exit code 6 before the escalated retry succeeded |
| `GPT-5.4-Mini Extra High` flash run 2 | 91,869 | ~22,967 | No, "the raw file ends cleanly at the Appendix B sentence" | `— Notable exclusions with rationale (Appendix B).`, with a trailing newline | `exec_command` with `curl`, `wc -m`, `wc -c`, `tail -c 50`, `awk`, `python3`, `web` wasn't used at all | Yes, `ec6-spec.AIBPGs` 0 bytes, `ec6-spec.RbQbd0` 92KB | `docs-consumption` confirmed present, the agent cited `MEMORY.md` content from an unrelated URL instead | named `Test web retrieval EC-6`, asked permission for `curl` once, worked 4 minutes 53 seconds, opened with a `MEMORY.md` search and hit a DNS resolution failure on the first `curl` attempt |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. Eight of the nine runs complete a full `curl` fetch and land on the identical `91,869`
characters or `91,877` bytes, well past any plausible ten to one hundred kilobyte ceiling. The one exception,
`GPT-5.4-Mini Light` flash run 2, never confirms a byte count because its `curl` attempt failed and the agent
didn't retry, so its lower estimate reflects an incomplete fetch, not a platform ceiling.

**Combined verdict: `H1` no. The one run reporting a smaller size failed its fetch rather than hitting a ceiling.**

---

## `H2`: Token-based truncation at roughly 2,000 tokens

Not supported. Every completed fetch returns roughly `23,000` tokens intact, far past a `2,000` token ceiling.
The lower estimate in `GPT-5.4-Mini Light` flash run 2 traces back to the same incomplete fetch, not a token limit.

**Combined verdict: `H2` no.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Mostly indeterminate. Seven of the nine runs report no truncation in the raw body at all, so there's no cutoff
to evaluate for structure-awareness on those runs. The two runs that do show an actual truncation event,
`GPT-5.4-Mini Extra High` flash run 1 and `GPT-5.4-Mini Light` flash run 2, both land mid-sentence rather than
on a heading, list break, or code fence, which argues against structure-awareness wherever a cutoff does occur.

**Combined verdict: `H3` indeterminate where no truncation occurs to inspect, no for the two runs that do show
a cutoff, since both land mid-sentence.**

---

## `H4`: Surface context, `T2` VS Code-Codex Extension changes retrieval behavior against `T1`

Partially to yes. Final character counts converge with `T1` in every run that completes a fetch, but the
retrieval process diverges consistently. `GPT-5.4-Mini High` flash run 1 needs a failed local fetch before
escalating, `GPT-5.4-Mini Extra High` flash run 1 runs nearly five and a half minutes across roughly ten
commands against `T1`'s single clean fetch, and `GPT-5.4-Mini Light` flash run 2 fails outright to retrieve the
full document, something no matched `T1` run does. `GPT-5.4-Mini Extra High` flash run 2 shows the sharpest
divergence, opening with a `MEMORY.md` search, skipping `web.open` entirely, and hitting a confirmed DNS
failure before its escalated `curl` succeeds.

**Combined verdict: `H4` partially to yes. Every completed run converges on the same final payload, but the
path each run takes to get there consistently differs from `T1`.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially. Runs that call `web` or `web.open` more than once, `GPT-5.4-Mini Light` flash run 1,
`GPT-5.4-Mini Extra High` flash run 1, `GPT-5.4-Mini Light` flash run 2, and `GPT-5.4-Mini Medium` flash run 2,
show chaining behavior consistent with pagination, even though none confirm that each call retrieved a
different slice of content rather than re-rendering the same one. The remaining five runs escalate straight
from a single `web` or `web.open` check to `curl` without repeated calls, which reads as standard failure
recovery rather than pagination.

**Combined verdict: `H5` partially. Repeated same-URL `web` calls appear in four of the nine runs, but
content-level pagination isn't confirmed in any of them.**

---

## `H6`: Does the `docs-consumption` skill shift truncation disclosure and completeness reporting

This is the hypothesis the flash experiment was built to test, and the support across five skill-on runs is
faint. No skill-on run ever surfaces a configuration recommendation addressing the recurring sandbox
DNS failure, the specific behavior this experiment targeted, even in `GPT-5.4-Mini High` flash run 2, where
relevant fix language was sitting in the agent's own cited `MEMORY.md` content and still didn't make it into
the final report. The signal instead clusters around two secondary behaviors. `GPT-5.4-Mini Light` flash run 3
and `GPT-5.4-Mini Medium` flash run 2 both show more decisive completeness and truncation language than the
skill-off baseline runs, while `GPT-5.4-Mini High` flash run 2 and `GPT-5.4-Mini Extra High` flash run 2 both
cite `MEMORY.md` content unprompted, a behavior the skill-off runs never show, even though the cited content
wasn't task relevant in either case. Retrieval quality itself doesn't track the skill consistently,
`GPT-5.4-Mini Light` flash run 2 regresses to a partial, unverified fetch, while every other skill-on run
matches the full baseline retrieval.

**Combined verdict: `H6` partially, with faint support. The skill correlates with more decisive completeness
reporting and with a new memory-citation behavior, but never produces the configuration guidance this
experiment intends to detect, and doesn't reliably improve or preserve retrieval quality.**

---

## Emergent Findings

1. **The chat-versus-audit tool count mismatch recurs across four runs.** `GPT-5.4-Mini Medium` flash run 1,
`High` flash run 1, `Extra High` flash run 1, and `Medium` flash run 2 all show reasoning text citing a
different `web` or command count than the rollout audit reports, consistent with a double-rendering issue at
this reasoning tier rather than a one-off.

2. **The two-tier sandboxed DNS failure, then escalated retry, pattern holds across nearly every `curl`-using
run.** Per established methodology this counts as expected `T2` surface behavior rather than direct `H4`
evidence, but it shapes the process divergence `H4` does capture.

3. **`GPT-5.4-Mini Light` flash run 2 is the only run in this batch with a genuine retrieval failure.** Its
`curl` attempt returned nothing and the agent never retried, a distinct outcome from every other skill-on or
skill-off run, which completed a full fetch.

4. **`H6` support splits into two behaviors that don't overlap in the same runs.** Decisive completeness
language appears at Light and Medium reasoning, while spontaneous `MEMORY.md` citation appears at High and
Extra High reasoning. Worth tracking these as separate sub-signals rather than one combined verdict going
forward.

5. **Artifact naming collisions continue in this batch.** `ec6_SPEC.md`, `ec6_SPEC_fetched.md`, and
`ec6-spec.md` variants recur across runs, consistent with the contamination risk flagged in the base `T2`
`EC-6` cycle.

6. **The `web.open` `L54` cutpoint reappears at Extra High reasoning in flash run 1, matching the base cycle's
finding of an identical cutoff position across models and reasoning levels.**

7. **Duration doesn't track cleanly with reasoning level in this batch either.** `Extra High` flash run 1 takes
5 minutes 29 seconds and flash run 2 takes 4 minutes 53 seconds, both far longer than `High` flash run 1 and
flash run 2, which both finish in under 2 minutes.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Light` FR 1 | Pass | `PASS, curl_91877_bytes + web_open_clip_l54 + no_skill_signal + 40 seconds` |
| `GPT-5.4-Mini Medium` FR 1 | Pass | `PASS, curl_91877_bytes + web_open_clip_appendix_b + no_skill_signal + 1 minute` |
| `GPT-5.4-Mini High` FR 1 | Pass | `PASS, curl_91869_chars + local_fetch_failed_then_escalated + skill_present_undiscovered + 1 minute 50 seconds` |
| `GPT-5.4-Mini Extra High` FR 1 | Pass | `PASS, curl_91869_chars + web_open_clip_mid_sentence_l54 + skill_present_undiscovered + 5 minutes 29 seconds` |
| `GPT-5.4-Mini Light` FR 2 | Fail | `FAIL, curl_returned_zero + no_retry + partial_estimate_only + skill_on_docs_consumption + 28 seconds` |
| `GPT-5.4-Mini Light` FR 3 | Pass | `PASS, curl_91869_chars + no_truncation + skill_on_docs_consumption + 40 seconds` |
| `GPT-5.4-Mini Medium` FR 2 | Pass | `PASS, curl_91877_bytes + web_open_clip_mid_line + skill_on_docs_consumption + 1 minute 29 seconds` |
| `GPT-5.4-Mini High` FR 2 | Pass | `PASS, curl_91877_bytes + sandbox_exit_code_6_then_escalated + memory_md_cited + skill_on_docs_consumption + 1 minute 17 seconds` |
| `GPT-5.4-Mini Extra High` FR 2 | Pass | `PASS, curl_91869_chars + dns_resolution_failure_then_escalated + memory_md_cited + skill_on_docs_consumption + 4 minutes 53 seconds` |
