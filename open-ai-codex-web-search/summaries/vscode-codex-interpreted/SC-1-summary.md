# SC-1 Summary

## Test Conditions

|                 | **SC-1** |
| --------------- | -------- |
| URL             | `https://ai.google.dev/gemini-api/docs/url-context` |
| Expected size   | ~40KB Markdown-heavy documentation page, actual HTML payload ~125KB |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/private/tmp` writable; project accessible as working directory |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.5`, `GPT-5.4-Mini` |
| Runs            | 8 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Low` | 125,252 | ~31k | `curl` no | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `curl`, `turn0view0`, `turn1view0` | No | two-tier sandbox DNS pattern, escalated `curl` succeeded; asked permission once; named `Test web retrieval SC-1`; offered to calculate separate `web.open` stats unprompted but didn't do so by default; 28 seconds |
| `GPT-5.4-Mini Medium` | ~29,000 | ~7,200 | `web.open` partial, implicit | `L437: *` | `web.open`, `curl`, `mcp__node_repl.js`, browser skill | No | sandboxed `curl` failed DNS twice, didn't escalate; switched to in-app browser; `mcp__node_repl.js` failed with `missing field 'sandboxPolicy'`; browser tool loaded but not actioned; named `Test web retrieval`; 1 minute 33 seconds |
| `GPT-5.4-Mini High` | ~34,000 | ~8,500 | Mixed, first `web.open` windowed at `L344`, second pass through `L437` | `— 简体\nL435: * 中文 — 繁體\nL436: * 日本語\nL437: * 한국어` | `web.open`, `turn0view0`, `turn1view0` | No | uniquely didn't attempt `curl` or run any shell commands; second `web.open` issued reactively from `L345` after first pass windowed; named `Test web retrieval SC-1`; 2 minutes 50 seconds |
| `GPT-5.4-Mini Extra High` | ~27,000 | ~6,800 | Implicit, first `web.open` stopped mid-REST example at `L344`, second pass through `L437` | same as Run 3 | `web.open`, `turn0view0`, `turn1view0`, `mcp__node_repl.js` | No | `mcp__node_repl.js` failed with `missing field 'sandboxPolicy'`; thought panel uniquely rendered the error message; didn't calculate final metrics despite Extra High reasoning level; named `Test web retrieval behavior`; 5 minutes 43 seconds |
| `GPT-5.5 Low` | ~24,000 | ~6,000 | Implicit, format-transformed extraction ending at footer | `中文 — 繁體\n  L436:  * 日本語\nL437:  * 한국어` | `web.run` with `open` | No | single `web` call, no `curl` attempted; didn't reconcile implicit truncation in report; named `Test web retrieval SC-1`; 30 seconds |
| `GPT-5.5 Medium` | 125,248 | ~31,300 | No, `curl` no; terminal display clipped UI output only | same as Run 1 | `functions.exec_command`, `curl` | Yes | bypassed `web` pipeline entirely; terminal display clipped visible output but measured from saved file; wrote `sc-1-url-context.html` to `/private/tmp` but didn't surface or reference it in the report; asked permission twice; rate-limited at session end; named `Test web retrieval`; 1 minute 31 seconds |
| `GPT-5.5 High` | 125,248 | ~31k | No, `curl` no; `web.open` recognized as format transformation, not raw bytes | same as Run 1 | `web.open`, `curl`, `wc`, `tail`, `perl`, `multi_tool_use.parallel` | Yes | `web.open` recognized as line-indexed extraction, not raw bytes; sandboxed `curl` failed DNS, escalated retry succeeded; wrote `sc1_url_context_response.html` to `/private/tmp`; initially stated it wouldn't request broader network access without direct request, then escalated anyway; asked permission once; named `Test web retrieval`; 2 minutes 30 seconds |
| `GPT-5.5 Extra High` | 16,390 | ~4,098 | Implicit, format-transformed extraction ending at footer | `* ภาษาไทย\n  * 中文 — 简体\n  * 中文 — 繁體\n  * 日本語\n  * 한국어` | `web.open`, Ruby via `functions.exec_command` | No | uniquely used Ruby for precise measurement; didn't attempt `curl`; implicit truncation unrecognized, reported result as complete; named `Test web retrieval SC-1`; longest run in cycle; 7 minutes 58 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported on the raw `curl` path. Runs 1, 6, and 7 all confirmed 125,248 to 125,252 characters via escalated or approved `curl` with clean `</body></html>`
closes, well above the proposed 10 to 100KB ceiling. The `web.open` surface delivered variable fractions of the full page, ranging from 16,390 to ~34,000 characters
across the six runs that relied on it. That variance is too wide to support a fixed character ceiling and contrasts sharply with SC-2's tight `L140` line cluster.
Runs 3 and 4 both showed first-pass cutoffs near `L344` with reactive second fetches extending through `L437`, suggesting a per-call line ceiling rather than a
page-level character boundary. Single-pass `web.open` runs produced meaningfully different sizes across models and reasoning levels, further undermining a fixed threshold.

**Combined verdict: `H1` no. No character ceiling on the raw `curl` path. The `web.open` surface delivers variable fractions of the full page, with first-pass line ceiling
evidence near `L344` in multi-pass runs but no consistent fixed character boundary.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. `curl` runs retrieved ~31,000 to ~31,300 tokens intact, far past the proposed 2,000-token threshold. `web.open` runs returned estimates ranging from
~4,098 to ~8,500 tokens, all above the threshold rather than stalling at it. No run's output clustered near 2,000 tokens on either path. All token figures use the
standard 4 chars/token heuristic; no tokenizer packages were available in the `T2` sandbox.

**Combined verdict: `H2` no. Token counts on both retrieval paths exceed the proposed ceiling. The threshold isn't binding on either path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Partially supported, with a competing line-ceiling explanation and one direct counterexample. Run 4's first `web.open` pass stopped mid-REST example at `L344`, an
arbitrary mid-section position, actively arguing against structure-aware cutoff behavior. The format-transformed extractions in runs 5 and 8 both ended at the page
footer rather than mid-section, weakly suggesting structure-awareness, but that's more consistent with a line extraction window that clears the page chrome than with
intentional Markdown boundary detection. The `curl` path delivered raw HTML throughout, so Markdown boundary assessment doesn't apply to those runs. Unlike `SC-2`'s
JavaScript shell, `SC-1`'s page does contain prose content in the raw payload, making boundary behavior more observable here, but the evidence points in competing directions.

**Combined verdict: `H3` partially. Footer-terminating web extractions could reflect structure-awareness or a line ceiling that clears the page prose. Run 4's mid-REST-example
cutoff is the one hard counterexample in the series.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Supported. The two-tier sandboxed/escalated network pattern dominated `T2` runs that attempted `curl`: sandboxed DNS failure first, permission escalation second. `T1`
runs resolved the same URL without that friction. Strategy inversions at matched levels confirm surface effects on agent decision-making independent of outcome volume.
`T2 GPT-5.5 Low` issued a single `web.open` call and retrieved ~24,000 characters; `T1 GPT-5.5 Low` escalated `curl` and retrieved 121,413 characters from the same URL.
In the opposite direction, `T2 GPT-5.4-Mini Low` succeeded via escalated `curl` and retrieved 125,252 characters while `T1 GPT-5.4-Mini Low` limited to ~23,000 characters
through `web.open`. No `T2` run accessed Browser Use or Playwright tooling, consistent with the Browser Use friction note candidate. `mcp__node_repl.js` failed in two
`T2` runs with `missing field 'sandboxPolicy'`, a surface-specific error not observed in `T1`.

Cross-track character counts converge where both tracks used `curl`: 125,248 to 125,252 in `T2` against 121,409 in `T1`. A minor content update between collection windows
is the most parsimonious explanation for that gap, not surface behavior.

**Combined verdict: `H4` yes. Network sandboxing, tool availability, and escalation requirements differ materially by surface. Strategy inversions at matched model and level
pairs confirm surface effects on agent decision-making that are independent of raw outcome volume.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported. Runs 1, 2, 3, 4, and 7 all initiated multi-step retrieval after recognizing the first fetch as incomplete or surface-limited. Runs 3 and 4 issued a
second `web.open` from `L345` after the first pass windowed at `L344`. Run 7 transitioned from `web.open` to `curl` after recognizing the line-indexed extraction format
as unsuitable for raw measurement. All those transitions were reactive gap-filling rather than systematic chunking: each followed an observed shortfall rather than a
pre-planned multi-segment strategy. Runs 5, 6, and 8 made no multi-step retrieval adaptation. Run 5 accepted a single `web.open` result as complete. Run 6 went directly
to `curl` without attempting `web` first. Run 8 used a single `web.open` and measured the received extraction with Ruby rather than fetching additional content.

**Combined verdict: `H5` partially. Reactive multi-step retrieval appeared in five of eight runs, but true chunking or pagination didn't appear in any. Three runs made
no retrieval adaptation after an initial or partial fetch.**

---

## Emergent Findings

1. **`curl` confirmed as the reliable full-document retrieval path for SC-1.** Runs 1, 6, and 7 all retrieved 125,248 to 125,252 characters with clean `</body></html>`
closes via escalated or approved `curl`. Unlike SC-2's hydrated JavaScript shell, SC-1's full payload contains the actual documentation prose, making `curl` not just
larger but content-correct for this URL.

2. **`web.open` output varied widely across the cycle, from 16,390 to ~34,000 characters.** SC-2 showed a tight cluster near `L140`. SC-1's single-pass `web.open`
results didn't converge, suggesting per-call extraction depth varies by model and reasoning level rather than being fixed at the surface level.

3. **A first-pass line ceiling near `L344` appeared in both multi-pass runs.** Runs 3 and 4 each reported `web.open` windowing at `L344` and continued from `L345`
through the footer at `L437`. That ceiling is notably higher than SC-2's `L140`, likely because SC-1's page delivers prose content in the initial rendering rather
than a JavaScript shell with placeholder bands.

4. **`mcp__node_repl.js` failed in two runs with `missing field 'sandboxPolicy'`.** Runs 2 and 4 both hit this error, consistent with the SC-2 finding. The error
appeared in run 4's thought panel but not run 2's, confirming inconsistent error visibility in the thought panel across runs.

5. **`GPT-5.4-Mini` showed the widest intra-model strategy variance in the cycle.** Low succeeded via escalated `curl`. Medium hit a DNS wall and didn't escalate.
High and Extra High both used two `web.open` passes with no `curl` attempt at all. That's four distinct retrieval strategies across four runs of the same model.
In SC-2, three of four `GPT-5.4-Mini` runs converged on the escalated `curl` path.

6. **`GPT-5.5 Extra High` was the longest run at 7 minutes 58 seconds and produced the smallest output at 16,390 characters.** Higher reasoning level didn't
correlate with more thorough retrieval in this cycle. The run uniquely used Ruby for measurement, didn't attempt `curl`, and didn't recognize the implicit
truncation in its received extraction.

7. **Only two of eight runs wrote artifacts, both `GPT-5.5` models that reached the full payload via `curl`.** `GPT-5.5 Medium` wrote `sc-1-url-context.html` and
`GPT-5.5 High` wrote `sc1_url_context_response.html`, both to `/private/tmp`. `GPT-5.5 Medium` didn't surface or reference its artifact in the report, meaning
the written but not disclosed. This extends the unreported artifact pattern into SC-1.

8. **`GPT-5.5 High` stated it wouldn't request escalation without being asked, then escalated anyway.** The agent reasoned that requesting broader network access
would change the surface tested, treating it as a methodology concern. It escalated anyway after recognizing the `web.open` extraction as format-limited, a direct
contradiction between stated reasoning and executed behavior.

9. **`GPT-5.5 Medium` hit the Codex session message limit at run end.** The rate limit prompt appeared after the run completed, with a reset timestamp of Jul 17, 2026, 4:24 PM.
This is the first SC-cycle run to surface a rate limit event, adding a new session disruption mode to the test record.

10. **The expected size of ~40KB was an underestimate of the actual HTML payload at ~125KB.** The test URL delivers full documentation prose as rendered HTML rather
than raw Markdown source. Char counts were stable across the cycle at 125,248 to 125,252, confirming a static payload over the SC-1 collection window, unlike SC-2's
dynamic 578,233 to 578,275 drift.

11. **`T2 GPT-5.5 Low` and `T1 GPT-5.5 Low` showed the largest cross-track outcome divergence in the SC-1 series.** `T1` escalated `curl` and retrieved 121,413 characters.
`T2` issued a single `web.open` call and retrieved ~24,000 characters. The same model and reasoning level produced roughly a 5x retrieval gap driven entirely by surface-influenced
tool selection.

12. **Runs 5 and 8 didn't recognize the implicit truncation in their received `web.open` extractions.** Both reported the format-transformed output as complete without flagging
that 24,000 or 16,390 characters represented a fraction of the available ~125KB. Agent self-perception of completeness and actual retrieval volume diverged in both cases,
consistent with the implicit truncation mode documented across the series.

13. **Test naming split three ways.** Runs 1, 3, 5, and 8 used `Test web retrieval SC-1`. Runs 2, 6, and 7 used `Test web retrieval`. Run 4 uniquely used
`Test web retrieval behavior`. The SC-1 suffix appeared in exactly half of runs.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Pass | `PASS, curl_125252_chars + two_tier_dns_pattern + web_open_stats_offered_not_default + no_artifact + 28 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_open_partial_29k + curl_dns_fail_no_escalation + node_repl_sandbox_policy_fail + browser_loaded_unused + no_artifact + 1 minute 33 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, web_open_L344_windowed + second_pass_L345_to_L437 + no_curl + no_shell_commands + no_artifact + 2 minutes 50 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, web_open_L344_mid_rest + second_pass_L345_to_L437 + node_repl_sandbox_policy_fail + thought_panel_error + no_metrics_calculated + no_artifact + 5 minutes 43 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, web_open_single_call_24k + no_curl + implicit_truncation_unrecognized + no_artifact + 30 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, web_bypassed + curl_125248_chars + terminal_display_clip + sc_1_url_context_html_private_tmp_unreported + rate_limited + 1 minute 31 seconds` |
| `GPT-5.5 High` | Pass | `PASS, web_open_format_recognized + curl_125248_chars + escalation_stated_then_executed + sc1_url_context_response_html_private_tmp + 2 minutes 30 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_open_only + ruby_measurement_16390_chars + no_curl + implicit_truncation_unrecognized + no_artifact + 7 minutes 58 seconds` |
