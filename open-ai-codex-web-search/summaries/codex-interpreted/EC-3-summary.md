# EC-3 Summary

## Test Conditions

|                 | **EC-3**                                                                                      |
| --------------- | --------------------------------------------------------------------------------------------- |
| URL             | `https://httpbin.org/redirect/5`                                                              |
| Expected size   | ~2KB per prompt; actual confirmed 660 chars / 254 bytes via `curl` / ~165 tokens             |
| Surface         | Codex IDE                                                                                     |
| Workspace       | Session-scoped sandbox; `/private/tmp` cleared between sessions; `Documents/Codex` persistent |
| Track           | `T1` GPT-interpreted, Codex IDE                                                               |
| Method          | GPT-interpreted                                                                               |
| Runs            | 20                                                                                            |
| Chunks returned | N/A, codex-interpreted track                                                                        |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL only; no artifacts written; acknowledged redirect; 35 seconds |
| `GPT-5.2 Medium` | 254 | ~64 | No | `47.232.34", "url": "https://httpbin.org/get" }` | `functions.exec_command`, `curl`, `python3` | Yes | bypassed web pipeline entirely; `curl` with DNS failure then retry; wrote `ec3_body.txt` to `/private/tmp`; 53 seconds |
| `GPT-5.2 High` | 660 | ~165–184 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; searched web twice; acknowledged redirect chain; didn't receive intermediate 302 bodies; no artifacts written; 1 minute |
| `GPT-5.2 Extra High` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js`, `functions.exec_command`, `python3` | Yes | tiktoken probe failed; pkgutil fallback; `count2: 618` anomalous token estimate; `Total lines: 1` surfaced; `codex_app.load_workspace_dependencies` invoked; no artifacts written; 1 minute 39 seconds |
| `GPT-5.3-Codex Low` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; no artifacts written; 10 seconds |
| `GPT-5.3-Codex Medium` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; `ref_id` parameter exposed in tool call; no artifacts written; 16 seconds |
| `GPT-5.3-Codex High` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; searched web twice; tail length verification pass; `lineno:null` exposed alongside `ref_id`; no artifacts written; 36 seconds |
| `GPT-5.3-Codex Extra High` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js`, `functions.exec_command` | Yes | web + Node REPL; `web.open`/`web.find` follow-up call returned `invalid ref_id` error; `Total lines: 1` surfaced; searched web three times; no artifacts written; 1 minute |
| `GPT-5.4-Mini Low` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run` | Yes | web-only run; no Node REPL invoked; fastest run in cycle; metrics computed inline from web output; proactively noted redirect resolution; no artifacts written; 7 seconds |
| `GPT-5.4-Mini Medium` | 660 | ~165–175 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `nodeRepl.write` | Yes | web + Node REPL; `turn0view0` citation identifier surfaced; offered archival JSON block unprompted but didn't act without confirmation; no artifacts written; 20 seconds |
| `GPT-5.4-Mini High` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; two-pass tail extraction after REPL name collision; explicitly reasoned about measurement precision; `turn0view0` surfaced again; no artifacts written; 43 seconds |
| `GPT-5.4-Mini Extra High` | 660 | ~165 / `count2: 618` anomalous | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js`, `functions.exec_command`, `python3` | Yes | tiktoken failed twice; pkgutil search; `bytes: 660` confirmed parity with chars; `count2: 618` anomalous estimate; `Total lines: 1` surfaced; longest run in cycle; no artifacts written; 2 minutes 33 seconds |
| `GPT-5.4 Low` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; `approxTokens` key name; `ref_id`/`lineno:null` both exposed; noted ~2KB size mismatch; no artifacts written; 12 seconds |
| `GPT-5.4 Medium` | 660 | ~165–190 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; `estTokens4: 165` and `estTokens35: 189` dual tokenizer estimates; first run to frame ~2KB mismatch as "not an expanded multi-hop redirect trace"; `turn0view0` and `ref_id`/`lineno:null` stable; no artifacts written; 15 seconds |
| `GPT-5.4 High` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; `Total lines: 1` surfaced; proposed "normalizing/minifying" hypothesis for ~2KB mismatch; explicitly reconciled `web.open` vs `open()` method terminology; no artifacts written; 29 seconds |
| `GPT-5.4 Extra High` | 660 | ~165–180 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js`, `functions.exec_command` | Yes | web + Node REPL; `turn0view0` re-access returned `invalid ref_id` error; `approxTokens4: 165` and `approxTokens3_7: 178.37...` floating-point estimate; `charCount` key name; no artifacts written; 1 minute 22 seconds |
| `GPT-5.5 Low` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; `bytes: 660` confirmed char/byte parity; `tokens_est` key name; `ref_id`/`lineno:null` exposed; didn't bypass web despite 5.5 tendency; no artifacts written; 10 seconds |
| `GPT-5.5 Medium` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `mcp__node_repl__.js` | Yes | web + Node REPL; `Total lines: 1` surfaced; explicitly reconciled `web.run` with `open` method vs literal `web.open` tool name; measurement explicitly isolated from tool wrapper text; no artifacts written; 18 seconds |
| `GPT-5.5 High` | 254 | ~64 | No | `47.232.34", "url": "https://httpbin.org/get" }` | `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail` | Yes | bypassed web pipeline entirely; `curl` with DNS failure then retry; wrote `ec3-httpbin-response.txt` to `/private/tmp`; `multi_tool_use.parallel` invoked; 1 minute 14 seconds |
| `GPT-5.5 Extra High` | 660 | ~165 | No | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run`, `web.open`, `node` | Yes | web + Node REPL; `Total lines: 1` surfaced; `web.open` reported without correction unlike some prior runs; returned to web pipeline despite 5.5 curl tendency; no artifacts written; 43 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. The EC-3 payload is too small to stress any plausible ceiling. All 20 runs returned either 660 chars via the web pipeline or 254 bytes via `curl`, both
well under any proposed 10–100 KB threshold. No truncation event occurred across the cycle. The curl/web char discrepancy is the more interesting signal: web pipeline
runs consistently returned 660 chars while `curl` runs returned 254 bytes, suggesting the web tool wraps or pads the response rather than the body being larger on that path.

**Combined verdict: `H1` no. Payload too small to test. The curl/web char split is a retrieval surface artifact rather than a truncation signal.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Web pipeline runs consistently returned ~165 tokens and `curl` runs returned ~64 tokens, both far below a 2,000-token ceiling. No run approached
the threshold. The ~2KB expected size noted in the test prompt was a persistent prior error across multiple model families, not a reflection of actual payload size.

**Combined verdict: `H2` no. Token ceiling not a factor. The 2KB prompt expectation was consistently wrong and worth correcting for future `EC-3` runs if the test reused.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not assessable. No truncation occurred in any run, so no boundary evaluation was possible. The payload is a single-line JSON object with no Markdown structure.

**Combined verdict: `H3` indeterminate. No truncation event to evaluate across any of the 20 runs.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively.

**Combined verdict: `H4` untested.**

---

## `H5`: Agent auto-chunks or auto-paginates

Not supported. Every run used a single fetch with no multi-step retrieval chaining. The payload was small enough that no run showed any instinct toward chunking
or pagination. The more complex toolchains seen in some runs were measurement overhead, not retrieval strategy.

**Combined verdict: `H5` no. Single fetch across all 20 runs. No adaptive retrieval behavior observed.**

---

## Emergent Findings

1. **`curl` and web pipeline return different char counts from the same URL.** `curl` runs returned 254 bytes consistently; web pipeline runs returned 660 chars
consistently. This is the inverse of the `EC-1` pattern where `curl` retrieved substantially more than `web.open`. For a compact JSON endpoint, the web tool
appears to surface more text than raw `curl`, likely due to wrapper or metadata text counted alongside the response body. This distinction is worth isolating
on future runs.

2. **Only 2 artifacts written across 20 runs, both `curl`-path runs, both to `/private/tmp`.** `GPT-5.2 Medium` wrote `ec3_body.txt` and `GPT-5.5 High` wrote
`ec3-httpbin-response.txt`. Both were nearly identical JSON bodies. No run wrote artifacts to the persistent `Documents/Codex` directory. Artifact production
rate is substantially lower than EC-1, consistent with the payload being too small to motivate save behavior.

3. **`web` pipeline was the dominant retrieval path, unlike `EC-1`.** In `EC-1`, most runs escalated from `web.open` to `curl` for full retrieval. In `EC-3`,
only 2 of 20 runs used `curl` at all. The small payload appears to suppress curl escalation instinct, making this cycle the inverse of `EC-1` in terms of tool
path distribution.

4. **Truncation reporting was consistently no, but implicit truncation argument is possible.** Most runs used Node REPL for metric calculation rather than
trusting web tool output directly, which suggests the web surface isn't considered measurement-reliable. `GPT-5.4-Mini Low` is the only run that computed metrics
inline from web output alone. The "web not suitable for metrics" pattern is consistent enough as a soft signal of implicit truncation awareness.

5. **`~2KB` expected size prior was persistently wrong across model families.** At least five runs across `GPT-5.2`, `GPT-5.4`, and `GPT-5.5` explicitly noted the
mismatch between expected ~2KB and actual 660 chars or 254 bytes. `GPT-5.4 Medium` offered the most useful framing: the agent expected an expanded multi-hop
redirect trace, not just the final response body. `GPT-5.4 High` proposed the most mechanistic explanation: the retrieval layer may normalize or minify content
rather than passing raw bytes. Both framings are useful for `EC-3` documentation.

6. **`Total lines: 1` surfaces as a stable Extra High and High signal.** Reported by `GPT-5.2 Extra High`, `GPT-5.3-Codex Extra High`, `GPT-5.4-Mini Extra High`,
`GPT-5.4 High`, `GPT-5.5 Medium`, and `GPT-5.5 Extra High`. Appears to be metadata from the web pipeline's internal line-numbering output, surfaced when the model
reads raw tool output carefully. Not intelligence-gated but more common at higher reasoning levels.

7. **`turn0view0` invalid `ref_id` error is a recurring Extra High failure mode.** `GPT-5.3-Codex Extra High` and `GPT-5.4 Extra High` both attempted to re-access
fetched content via a stored reference after the initial fetch, received an `invalid ref_id` error, and logged it. This is a consistent Extra High retrieval surface
quirk worth tracking across test cycles.

8. **Web tool parameter internals surface more at higher intelligence levels.** `ref_id`, `lineno:null`, `turn0view0`, `L0:`, and `Total lines: 1` all appear in run
reports as model intelligence increases. Lower intelligence levels don't report these details. The pattern suggests higher reasoning levels read and report raw tool
output more thoroughly rather than summarizing it.

9. **Metric key naming is non-deterministic across runs.** Nine distinct key names for the character/token count metric appeared across 20 runs: `charCount`, `chars`,
`estTokens`, `estTokens4`, `estTokens35`, `estTokens36`, `approxTokens`, `approxTokens4`, `approxTokens3_7`, and `tokens_est`. All converge on ~165 but the schema is
unstable. This is a recurring documentation challenge for the test cycle.

10. **`GPT-5.5 High` is the only 5.5 run to bypass web and use `curl`, mirroring `EC-1`'s 5.5 pattern.** In `EC-1`, three of four `GPT-5.5` runs bypassed `web.open`
entirely. In `EC-3`, only `GPT-5.5 High` did. The small payload appears to suppress the curl instinct in `GPT-5.5 Low`, `GPT-5.5 Medium`, and `GPT-5.5 Extra High` but
not High. No clean rule explains the selective bypass.

11. **`web.open` prompt terminology correction is intermittent, not stable.** Several runs noted that `web.open` as named in the test prompt doesn't match the actual
tool call, which is `web.run` using the `open` method. This correction appeared in `GPT-5.4 High` and `GPT-5.5 Medium` but not consistently. Unlike Cursor and Windsurf
Cascade testing where no agent flagged prompt terminology mismatches, some Codex agents do surface this, but the behavior is nondeterministic.

12. **Runtime scales with intelligence level within model families but not linearly at `Extra High`.** `Low` intelligence runs across newer families cluster at 7–12
seconds. `Extra High` runs range from 1 minute to 2 minutes 33 seconds. The overhead at `Extra High` driven by self-directed instrumentation such as tokenizer probing,
dual metric estimation, and tool re-access attempts rather than retrieval complexity. The payload didn't warrant the additional overhead in any `Extra High` run.

13. **`multi_tool_use.parallel` appears in `GPT-5.5 High` only.** Consistent with `EC-1` findings where this identifier appeared exclusively in `GPT-5.5` runs. Its
appearance here in a `curl`-path run rather than a web-path run suggests it's a `GPT-5.5` toolchain characteristic rather than a retrieval strategy adaptation.

14. **Over-engineering is the dominant pattern for a minimum-payload test.** `EC-3` intended a floor test. Most runs applied the same or greater instrumentation effort
as larger-payload tests without producing additional insight. The most informative run in the cycle is arguably `GPT-5.4-Mini Low` at 7 seconds with a web-only single
pass, which surfaced the same measurements as the 2-minute 33-second `GPT-5.4-Mini Extra High` run.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.2 Low` | Pass | `PASS - web_660_chars + node_repl_metrics + redirect_acknowledged + no_artifacts + 35 seconds` |
| `GPT-5.2 Medium` | Pass | `PASS - curl_254_bytes + dns_failure_retry + ec3_body_txt_artifact + private_tmp + web_bypassed + 53 seconds` |
| `GPT-5.2 High` | Pass | `PASS - web_660_chars + node_repl_metrics + redirect_acknowledged + 302_bodies_noted_absent + no_artifacts + 1 minute` |
| `GPT-5.2 Extra High` | Pass | `PASS - web_660_chars + tiktoken_probe_failed + count2_618_anomaly + total_lines_1_surfaced + codex_app_load_invoked + no_artifacts + 1 minute 39 seconds` |
| `GPT-5.3-Codex Low` | Pass | `PASS - web_660_chars + node_repl_metrics + no_artifacts + 10 seconds` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - web_660_chars + node_repl_metrics + ref_id_exposed + no_artifacts + 16 seconds` |
| `GPT-5.3-Codex High` | Pass | `PASS - web_660_chars + node_repl_metrics + tail_verify_pass + lineno_null_exposed + no_artifacts + 36 seconds` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - web_660_chars + invalid_ref_id_error + total_lines_1_surfaced + no_artifacts + 1 minute` |
| `GPT-5.4-Mini Low` | Pass | `PASS - web_only_660_chars + inline_metrics + redirect_noted + no_node_repl + no_artifacts + 7 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS - web_660_chars + node_repl_metrics + turn0view0_surfaced + archival_offer_not_executed + no_artifacts + 20 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS - web_660_chars + two_pass_tail_extraction + repl_collision_recovered + turn0view0_stable + no_artifacts + 43 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - web_660_chars + tiktoken_failed_twice + count2_618_anomaly + bytes_char_parity_confirmed + total_lines_1_surfaced + no_artifacts + 2 minutes 33 seconds` |
| `GPT-5.4 Low` | Pass | `PASS - web_660_chars + node_repl_metrics + approxTokens_key + ref_id_lineno_null_exposed + 2kb_mismatch_noted + no_artifacts + 12 seconds` |
| `GPT-5.4 Medium` | Pass | `PASS - web_660_chars + dual_tokenizer_estimates + multi_hop_trace_framing + turn0view0_stable + no_artifacts + 15 seconds` |
| `GPT-5.4 High` | Pass | `PASS - web_660_chars + total_lines_1_surfaced + normalizing_hypothesis + webopen_terminology_reconciled + no_artifacts + 29 seconds` |
| `GPT-5.4 Extra High` | Pass | `PASS - web_660_chars + invalid_ref_id_error + floating_point_token_estimate + charCount_key + no_artifacts + 1 minute 22 seconds` |
| `GPT-5.5 Low` | Pass | `PASS - web_660_chars + bytes_char_parity_confirmed + tokens_est_key + ref_id_lineno_null_exposed + no_artifacts + 10 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS - web_660_chars + total_lines_1_surfaced + webrun_open_method_reconciled + measurement_wrapper_isolated + no_artifacts + 18 seconds` |
| `GPT-5.5 High` | Pass | `PASS - curl_254_bytes + dns_failure_retry + multi_tool_use_parallel + ec3_httpbin_response_artifact + private_tmp + web_bypassed + 1 minute 14 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS - web_660_chars + total_lines_1_surfaced + web_open_uncorrected + no_artifacts + 43 seconds` |
