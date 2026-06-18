# OP-4 Summary

## Test Conditions

|                 | **OP-4** |
| --------------- | -------- |
| URL             | `https://spec.commonmark.org/0.31.2/` |
| Expected size   | ~500KB |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox, `/private/tmp` writable, project accessible as working directory |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.5`, `GPT-5.4-Mini` |
| Runs            | 8 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Low` | Not exposed, `web.open` reported `Total lines: 7423` | ~100,000 to 140,000 | No, explicit report | `ers above stack_bottom from the delimiter stack.` | `web.open`, `curl`, `node` fetch | No | `curl` returned 0 bytes and a Node fetch hit `ENOTFOUND`, neither examined, `web.open` reached the appendix conclusion and the model perceived this as complete, named `Test web retrieval`, 36 seconds |
| `GPT-5.4-Mini Medium` | 514,092 via direct `curl` | ~125,000 | No for `curl` body, yes for `web.open` display | `from the delimiter stack.` then closing `body` and `html` tags | `web.run` via `open`, `curl`, `wc`, `tail`, `grep` | Yes | uniquely wrote-saved `/private/tmp/commonmark_0_31_2.html`, 515KB, asked permission to use `curl` after a DNS failure, `web.open` preview showed only the first 237 of 7423 lines, named `Test web retrieval`, 1 minute |
| `GPT-5.4-Mini High` | ~40,000 visible estimate, `web.open` only, no `curl` success | ~10,000 | Yes, explicit report | `ers above stack_bottom from the delimiter stack.` | `web.open`, `turn0view0`, `turn1view0`, `turn2view0`, `curl` | No | `curl` failed and wasn't examined, three sequential `web.open` views against the same URL suggest auto-chunking at the tool layer rather than agent-reasoned pagination, the model reported the content as truncated and incomplete, named `Fetch CommonMark spec URL`, 2 minutes 16 seconds |
| `GPT-5.4-Mini Extra High` | 514,092 via direct `curl` | ~128,500 | No for raw body, yes for `web.open` display | `from the delimiter stack.` then closing `body` and `html` tags | `web.open`, `turn0view0`, `wordlim:200`, `curl`, `node_repl` | Yes | wrote-saved `/private/tmp/commonmark_0_31_2.html`, 515KB, the same filename and size as `GPT-5.4-Mini Medium`'s artifact, asked permission to use `curl` once, `web.open` preview stopped at `L237` of 7423, named `Test OP-4 web retrieval`, 3 minutes 31 seconds |
| `GPT-5.5 Low` | 514,092 via direct `curl` | ~128,500 | No for `curl` body, yes for `web.open` display | `from the delimiter stack.` then closing `body` and `html` tags | `web.run` with `open`, `curl`, `wc`, `sed`, `tail`, `file`, `node`, `multi_tool_use.parallel` | Yes | wrote-saved `/private/tmp/commonmark_0.31.2.html`, 515KB, asked permission to use `curl` once, `web.open` produced two different excerpts, an initial `L0` to `L616` view then a later view near the end that omitted lines in the middle, named `Test web retrieval limits`, 33 seconds |
| `GPT-5.5 Medium` | 514,092 via direct `curl` | ~128,523 | No, `curl`-first, `web` and `web.open` weren't invoked | `from the delimiter stack.` then closing `body` and `html` tags | `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `file`, `node` | Yes | wrote-saved `/private/tmp/op4_commonmark.html`, 515KB, asked permission to use `curl` twice, bypassed the `web` pipeline completely, named `Test web retrieval OP-4`, 51 seconds |
| `GPT-5.5 High` | 514,092 via direct `curl` | ~128,500 | No for `curl` body, yes for `web.open` display | `from the delimiter stack.` then closing `body` and `html` tags | `web.run` with `open`, `curl`, `functions.exec_command`, `multi_tool_use.parallel`, `ruby`, `tail` | Yes | wrote-saved `/private/tmp/commonmark-0.31.2.html`, 515KB, asked permission to use `curl` early, `web.open` view was display-limited to `L616` of 7423, uniquely used `ruby` for the measurement pass, named `Test web retrieval`, 53 seconds |
| `GPT-5.5 Extra High` | 514,092 via direct `curl` | ~128,523 | No, `curl`-first, `web` and `web.open` weren't invoked | `from the delimiter stack.` then closing `body` and `html` tags, with a final newline after `html` | `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `head`, `file`, `python3`, `rg`, `od` | Yes | wrote-saved `/private/tmp/op4_commonmark_response.html`, 515KB, a different filename pattern from every other `GPT-5.5` run this cycle, asked permission to use `curl` early, bypassed the `web` pipeline completely, named `Test web retrieval`, 1 minute 39 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. Six of eight runs escalated to a direct `curl` fetch and each measured 514,092 characters, 514,698 bytes, with closing `body` and `html`
tags intact, far past any 10 to 100KB ceiling. The two runs without a confirmed raw fetch, `GPT-5.4-Mini Low` and `GPT-5.4-Mini High`, never produced a
character count of their own to compare against, since neither escalation to `curl` succeeded and examined. There's no evidence anywhere in this cycle
of a fixed character limit on the underlying retrieval.

**Combined verdict: `H1` no. No character ceiling on the raw fetch path across any run that reached it.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Every run with a confirmed `curl` fetch estimated roughly 125,000 to 128,500 tokens of raw HTML, far past the proposed threshold.
`GPT-5.4-Mini Low` estimated 100,000 to 140,000 visible tokens from `web.open` alone, and `GPT-5.4-Mini High` estimated roughly 10,000, both well above
2,000 and both still far short of a clean ceiling test since neither had a confirmed raw byte count to anchor against. No run produced a cutoff at or near
the 2,000 token mark. Token estimates throughout used a rough chars divided by four heuristic, no tokenizer packages were available in the sandbox.

**Combined verdict: `H2` no. No 2,000 token ceiling on any retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Partially supported, with a competing explanation. The raw `curl` body was never truncated in any of the six successful escalations, so structural boundary
assessment doesn't fully apply there, the response is HTML, not Markdown, and ends cleanly with closing tags. Two runs, `GPT-5.5 Medium` and `GPT-5.5 Extra High`,
bypassed `web.open` entirely, so there's no preview boundary to assess at all for those, this is `indeterminate` rather than `no` for those two specifically.

On the `web.open` path itself, cutoffs consistently landed at a fixed line count rather than at a Markdown or section boundary, `L237` for `GPT-5.4-Mini Medium`
and `Extra High`, `L616` for `GPT-5.5 Low` and `High`. That a line-count cutoff recurs at two different values across this cycle, rather than landing in the same
place on identical content every time, argues against a single fixed structure-aware boundary. `GPT-5.5 Low`'s two different excerpts within a single run, an initial
`L0` to `L616` view followed by a later view that omitted lines in the middle, is itself worth flagging, since a purely fixed-viewport explanation wouldn't predict
a second, different excerpt of the same document. `GPT-5.4-Mini High`'s three sequential `web.open` views also reached further into the document without an
agent-reasoned request to do so, consistent with some pagination or relevance-driven mechanism shaping what's shown, though we don't have enough detail on the
selection logic to call this a clean yes.

**Combined verdict: `H3` partially. Cutoffs aren't tied to a Markdown or HTML structural boundary, but they aren't a single static line count either, and the
underlying document is never truncated when reached.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Partially supported, model-dependent, with a clean split by model family. Every `GPT-5.4-Mini` run across all four intelligence levels showed `partially` for this
hypothesis, the surface produced different tool vocabulary and different self-reported completeness across runs, `GPT-5.4-Mini Low` reported a `curl` failure as zero
bytes without examining it, `GPT-5.4-Mini Medium` escalated to `curl` only after explicit permission, `GPT-5.4-Mini High` relied entirely on the `web` pipeline with an
unexamined `curl` failure, and `GPT-5.4-Mini Extra High` was the first at this model to complete a raw `curl` fetch. None of these produced a clean divergence in final
retrieval outcome from `T1`, just differences in tool vocabulary, escalation timing, and surface awareness language.

Every `GPT-5.5` run, by contrast, showed yes. `GPT-5.5 Low` and `High` engaged `web.run` with `open` and hit a `web.open` display limit before or alongside a `curl`
escalation, while `GPT-5.5 Medium` and `Extra High` bypassed the `web` pipeline completely and went `curl`-first from the start, explicitly confirming `web` and `web.open`
weren't invoked. That's not a clean intelligence-level gradient either, since `Low` and `High` used `web` while `Medium` and `Extra High` skipped it, but at every level
the run diverged from a counterpart pattern in a way that's attributable to the surface rather than to model disposition alone, since the same model at the same intelligence
level on `T1` either bypassed `web.open` consistently or engaged it consistently depending on the level, and `T2` didn't always match.

**Combined verdict: `H4` mixed, by LLM family. `GPT-5.4-Mini` showed `partially` at every level, surface effects present in tool vocabulary and escalation timing but not in
final outcome. `GPT-5.5` showed `yes` at every level, with `T2` runs splitting between full `web` bypass and `web.open` display-limit encounters in a pattern not explained by
intelligence level alone.**

---

## `H5`: Agent auto-chunks or auto-paginates

Mixed, no clean pattern across the cycle. `GPT-5.4-Mini High` showed the clearest evidence, three sequential `web.open` views, `turn0view0` through `turn2view0`, against a
single URL with no visible reasoning trace requesting each one, consistent with auto-chunking at the tool layer. `GPT-5.5 Low` showed a softer version of the same signature,
two different `web.open` excerpts of the same document, but it's `partially` rather than `yes` since the second excerpt's relationship to the first wasn't fully explained.
`GPT-5.4-Mini Low` and `Medium` also landed at `partially`, both folded a `curl` escalation in after the initial `web.open` view, reasoned tool-switching rather than confirmed
automatic chunking. The remaining four runs, `GPT-5.4-Mini Extra High`, `GPT-5.5 Medium`, `High`, and `Extra High`, all showed `no`, either a single `web.open` call followed by
one deliberate `curl` escalation, or no `web` engagement at all.

**Combined verdict: `H5` mixed. One run showed clear multi-view auto-pagination, three showed a softer partial signature, and four showed no pagination behavior at all, with no
clean split by LLM or intelligence level explaining the difference.**

---

## Emergent Findings

1. **Artifact creation was more frequent than the prior cycle, but came with a renewed contamination risk.** Six of eight runs wrote a saved file beyond the standard
rollout log this cycle, up from four of eight in `OP-2`. All six artifacts measured byte-identical at 514,698 bytes regardless of filename, confirming they captured
the test URL's content accurately. But filename collisions recurred, `GPT-5.4-Mini Medium` and `Extra High` both wrote to the identical path
`/private/tmp/commonmark_0_31_2.html`, and `GPT-5.5 Low` and `High` both wrote to `/private/tmp/commonmark-0.31.2.html`, a period rather than underscore variant.
`GPT-5.5 Medium` and `Extra High` were the two outliers with unique filenames, `op4_commonmark.html` and `op4_commonmark_response.html`. Agents saved artifacts to
temporary storage in `/private/tmp`, none persisted to a project-local directory.

2. **The `web.open` window showed two recurring line counts rather than one fixed value.** `GPT-5.4-Mini Medium` and `Extra High` both cut at `L237`, while `GPT-5.5 Low`
and `High` both cut at `L616`. This is consistent with the `OP-2` observation that the line ceiling is model-dependent, and sharpens it, the cutoff appears to cluster by
LLM family within this cycle rather than scaling smoothly with intelligence level.

3. **`GPT-5.5` showed a markedly more sophisticated toolchain than `GPT-5.4-Mini`, including two runs that bypassed `web` entirely.** `GPT-5.5 High` uniquely used `ruby`
for its measurement pass, and `GPT-5.5 Extra High` uniquely used `python3` alongside `rg` and `od`. `GPT-5.5 Medium` and `Extra High` both skipped the `web` pipeline
completely in favor of a `curl`-first strategy, something no `GPT-5.4-Mini` run did at any level this cycle.

4. **Failure modes were rarely examined.** Across runs that hit `curl` failures, whether reported as zero bytes or a DNS resolution failure, no run inspected the underlying
error in detail before moving to a workaround. `GPT-5.4-Mini High` similarly didn't examine its failed `curl` attempt. This matches the pattern from prior cycles, named
failures aren't interpreted by default.

5. **The thought panel obscured tooling on several runs.** Command execution counts visible in the chat panel didn't reliably match the full set of operations the agent ran,
with the panel collapsing or hiding command sequences behind summary labels rather than surfacing every step. `GPT-5.4-Mini Extra High` and `GPT-5.5 Extra High` both
showed this, the chat panel displayed a smaller command count than the rollout log's `function_calls` figure cited in the notes. This extends the `OP-2` finding that the
chat display doesn't fully represent everything the agent executed, and that the rollout log remains the more complete record.

6. **Test naming showed a dominant default this cycle, unlike `OP-2`.** `Test web retrieval` appeared exactly four times, `GPT-5.4-Mini Low`, `GPT-5.4-Mini Medium`,
`GPT-5.5 High`, and `GPT-5.5 Extra High`. The remaining four runs each used a distinct variant, `Fetch CommonMark spec URL`, `Test OP-4 web retrieval`, `Test web retrieval limits`,
and `Test web retrieval OP-4`. This contrasts with `OP-2`'s finding of no dominant default for that cycle.

7. **The free tier rate limit wasn't exceeded this cycle, after hit during the prior cycle.** `OP-2` reached its limit during the eighth run, `GPT-5.5 Extra High`. This
`OP-4` cycle completed all eight runs without hitting that limit.

8. **Double rendering of the output report appeared for roughly half the cycle, then stopped, and followed by a separate pattern where command executions disappeared from view.**
This extends the autonomous post-hoc session alteration pattern documented for `T2` in prior cycles, where a single report becomes a double with identical content added rather than
cleaned up. The timer drift between the chat-displayed duration and the rollout's recorded duration also continues this cycle, consistent with the pattern described in the
`Seeing Double` analysis, where the chat's live counter and the rollout's recorded duration measure different endpoints rather than disagreeing due to error.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Pass | `PASS, web_open_no_explicit_truncation + curl_0_bytes_unexamined + node_fetch_enotfound_unexamined + appendix_reached + no_artifact + 36 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, curl_514092_chars + web_open_L237_truncated_of_7423 + permission_asked_after_dns_fail + commonmark_0_31_2_html_private_tmp + 1 minute` |
| `GPT-5.4-Mini High` | Pass | `PASS, web_open_three_sequential_views + curl_failed_unexamined + explicit_truncation_reported + no_artifact + 2 minutes 16 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, curl_514092_chars_first_success + web_open_L237_of_7423 + wordlim_200 + commonmark_0_31_2_html_private_tmp_filename_collision_with_medium + 3 minutes 31 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, curl_514092_chars + web_open_two_different_excerpts_L0_to_L616_then_near_end + commonmark_0_31_2_html_private_tmp + 33 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, curl_514092_chars + web_and_web_open_not_invoked + permission_asked_twice + op4_commonmark_html_private_tmp + 51 seconds` |
| `GPT-5.5 High` | Pass | `PASS, curl_514092_chars + web_open_L616_display_limited_of_7423 + ruby_uniquely_used + commonmark-0_31_2_html_private_tmp + 53 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, curl_514092_chars + web_and_web_open_not_invoked + python3_uniquely_used + op4_commonmark_response_html_private_tmp_filename_outlier + 1 minute 39 seconds` |
