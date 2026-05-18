# OP-4 Summary

## Test Conditions

|                 | **OP-4**                                                                        |
| --------------- | ------------------------------------------------------------------------------- |
| URL             | `https://spec.commonmark.org/0.31.2/`                                           |
| Expected size   | ~500 KB assumed; actual ~514,092 chars / 514,698 bytes / ~128,500 tokens        |
| Surface         | Codex IDE                                                                       |
| Workspace       | Session-scoped sandbox; persistent artifacts observed across sessions           |
| Track           | `T1` GPT-interpreted, Codex IDE                                                 |
| Method          | GPT-interpreted                                                                 |
| Runs            | 20                                                                              |
| Chunks returned | N/A, interpreted track                                                          |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | ~12,082 chars | ~3,021 | Yes - web.open L237 of 7423 | `</code></pre>\nL236: \nL237: Try It` | `web.run`, `functions.exec_command`, `mcp__node_repl__.js` | No | single web.open fetch; no curl attempted; 1 minute 42 seconds |
| `GPT-5.2 Medium` | ~50k chars est. across viewports | ~12,000-15,000 | Yes - web.open per call. No - end reached via lineno=7350 | `ove \ stack_bottom` from the delimiter stack.` | `web.run`, `web.open` | No | probed tail via lineno offset; windowed display confirmed; 41 seconds |
| `GPT-5.2 High` | ~12k chars per viewport | ~3,000 | Yes - web.open L237 of 7423 | `</code></pre>\nL236: \nL237: Try It` | `web.run`, `web.open`, `functions.exec_command`, `mcp__node_repl__.js` | No | 30 commands; 11 web searches; looped on same viewport ceiling; 14 minutes 24 seconds |
| `GPT-5.2 Extra High` | 514,698 bytes confirmed | ~128,500 | No - curl complete. Yes - web.open windowed | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail`, `python3` | Yes `commonmark_0.31.2.html` | curl-to-file strategy; asked curl permission twice; 6 minutes 12 seconds |
| `GPT-5.3-Codex Extra High` | 514,092 chars / 514,698 bytes | ~128,500 | No - curl complete. Yes - web.open windowed L235-L616 | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `perl`, `python3` | Yes `commonmark_0312.html` in `/private/tmp` | explicit lineno pagination noted; asked curl permission; 2 minutes 43 seconds |
| `GPT-5.3-Codex Medium` | 514,698 chars / 514,092 bytes | ~128,700 | No - curl complete. Yes - web.open windowed | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `functions.exec_command`, `curl`, `wc`, `tail`, `od`, `sed` | Yes `op4_commonmark_0312.html` in `/tmp` | curl-to-file; no web.open used; 40 seconds |
| `GPT-5.3-Codex Low` | ~16,000 chars est. | ~4,000 | Yes - web.open L237 of 7423 | `</code></pre>\n\nTry It` | `web.open` | No | single web.open; curl not invoked; 8 seconds |
| `GPT-5.2 High - Run 6` | 514,092 chars / 514,698 bytes | ~128,000-132,000 | No - curl complete. Yes - web.open L237 | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `perl`, `xxd`, `python3` | No | asked curl permission ~7 times for sub-steps; most granular permission behavior in set; 2 minutes 13 seconds |
| `GPT-5.4-Mini Low` | ~16,000 chars est. from web.open | ~4,000 | Yes - web.open partial by design. No - tail fetch reached L7422 | `ers above \`stack_bottom\` from the delimiter stack.` | `web.open`, `curl` | No | curl failed DNS; two web.open calls covering head and tail; 18 seconds |
| `GPT-5.4-Mini Medium` | 514,698 chars / 514,092 bytes | ~129,000 | No - curl complete. Yes - web.open windowed | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.open`, `node_repl`, `curl`, `wc`, `tail`, `python3` | No | explicit tool distinction windowed-for-display vs underlying-fetch-complete; asked curl permission 3 times; 1 minute 31 seconds |
| `GPT-5.4-Mini High` | 514,092 decoded chars / 514,698 bytes | ~130,000-140,000 | No - curl complete. Yes - web.open preview-based | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.open`, `curl`, `python3` with `urllib.request` | No | self-corrected bytes vs Unicode chars; used urllib.request in addition to curl; asked curl permission 3 times; 1 minute 29 seconds |
| `GPT-5.4-Mini Extra High` | 514,092 chars / 514,698 bytes | ~130,000 | No - curl complete. Yes - web.open L616 of 7423 | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `node`, `rg` | Yes `commonmark.html` in `/private/tmp` | programmatic pre/code block balance check 1360/1360; asked curl permission once; 2 minutes 13 seconds |
| `GPT-5.4 Low` | 514,698 chars / 514,092 bytes | ~128,675 | No - curl complete. Yes - web.open L237 then lineno=7390 | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web`, `web.open`, `curl`, `wc`, `tail` | No | first Low-tier run across any LLM version to successfully execute curl; asked curl permission; 45 seconds |
| `GPT-5.4 Medium` | 514,698 chars | ~128,675 | No - curl complete. Yes - web.open L237 to L7164 | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.open`, `curl`, `wc`, `tail`, `head`, `python3` | No | described web.open skip from L237 to L7164 explicitly; sandbox curl returned 0 bytes then escalated; asked curl permission 4 times; 1 minute 21 seconds |
| `GPT-5.4 High` | 514,092 chars / 514,698 bytes | ~128,500 | No - curl complete. Yes - web.open L237 then lineno=7390 to L7422 | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web`, `web.open`, `curl`, `wc`, `tail`, `file`, `rg` | Yes `commonmark-0.31.2.html` in `/private/tmp` | second web.open at lineno 7390 confirmed pagination; described tool as paginated rather than fundamentally incomplete; asked curl permission twice; 3 minutes 1 second |
| `GPT-5.4 Extra High` | 514,092 chars / 514,698 bytes | ~128,523 | No - curl complete. Yes - web.open windowed. curl stdout truncated by terminal display at 124,675 tokens | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `ruby`, `rg`, `multi_tool_use.parallel` | Yes `op4_commonmark_0_31_2.html` in `/private/tmp` | third distinct truncation layer identified: terminal stdout display cap; ruby for tail extraction; concurrent parallel measurement; asked curl permission twice; 3 minutes 7 seconds |
| `GPT-5.5 Low` | 514,092 chars / 514,698 bytes | ~128,500 | No - curl complete. web.open not used | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `curl`, `wc`, `tail`, `perl`, `rg` | Possible reuse of `commonmark-0.31.2.html` | web pipeline bypassed entirely; curl-first without web.open attempt; asked curl permission; 27 seconds |
| `GPT-5.5 Medium` | 514,092 chars / 514,698 bytes | ~128,523 | No - curl complete. web.open not used | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `curl`, `wc`, `tail`, `node`, `python3` | Possible reuse of `commonmark-0.31.2.html` | pre/pre and code/code balance verified; fenced code marker count checked; node JSON output for chars/bytes/last50; asked curl permission once; 35 seconds |
| `GPT-5.5 High` | 514,092 chars / 514,698 bytes | ~128,523 | No - curl complete. web.open not used | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `curl`, `wc`, `tail`, `node` | Possible reuse of `commonmark-0.31.2.html` | web.open explicitly not invoked; open/close counts matched for all major tags; asked curl permission once; 44 seconds |
| `GPT-5.5 Extra High` | 514,092 chars / 514,698 bytes | ~128,500 | No - curl complete. Yes - web.open L616 then curl | `> from the\ndelimiter stack.</p>\n\n</body>\n</html>` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `node`, `multi_tool_use.parallel` | Possible reuse of `commonmark-0.31.2.html` | web.open used for initial inspection only; pre/code block balance 1360/1360 confirmed; parallel concurrent checks; asked curl permission once; 1 minute 12 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported via `curl` path. Successful `curl` fetches returned 514,092 chars consistently across all runs that used curl,
far above any 10-100 KB ceiling threshold. The ceiling hypothesis is only partially consistent with `web.open` results, where
visible chars in truncated runs reflect a fixed line window rather than a character ceiling. The three Low-tier runs on `GPT-5.2`,
`GPT-5.3-Codex`, and `GPT-5.4-Mini` that relied solely on `web.open` returned approximately 12,000-16,000 chars, consistent
with a fixed viewport window rather than a character ceiling. A distinct third truncation layer identified in the `GPT-5.4
Extra High` run, where `curl` stdout capped at approximately 124,675 tokens by the terminal display tool, independent of
both the `web.open` window and the underlying HTTP response.

**Combined verdict: `H1` no for `curl` path. Partially consistent with `web.open` path where the window is line-count-bound not character-bound. A terminal display cap constitutes a third distinct truncation layer.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Successful `curl` fetches returned approximately 128,500 tokens consistently, well above the 2,000-token
threshold. `web.open` windowed results ranged from approximately 3,000 tokens on first-view captures in Low-tier runs to the
full ~128,500 tokens when `curl` used. No run approached or hit a 2,000-token ceiling on either path.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported as a mechanism, though the question can't be fully resolved from available evidence. The `web.open` line window
consistently terminates at approximately L237 on first fetch across `GPT-5.2` through `GPT-5.4` runs, and at approximately
L616 across `GPT-5.5 Extra High` and `GPT-5.4-Mini Extra High` runs. L237 ends on the text `Try It`, which is a named anchor
in the CommonMark spec, and could coincidentally appear structure-aligned. However, the same L237 cutpoint appears consistently
regardless of content density variations across runs, suggesting a fixed line-count window rather than boundary detection.
The variable cutpoint between L237 and L616 across LLM versions and intelligence levels may reflect viewport window size
scaling rather than structural awareness. No run produced evidence that truncation positioned to respect a heading, code
block boundary, or section end.

**Combined verdict: `H3` indeterminate. Truncation boundary appears to be a fixed platform line window. Coincidental alignment with named anchors not ruled out, but not supported by cross-run evidence.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively. VS Code-Codex extension comparison
not performed. Within the Codex IDE surface, a consistent two-tier network access pattern confirmed: sandboxed DNS
failure followed by escalated `curl` success. This infrastructure property was consistent across all LLM versions and
constitutes a surface-level constraint rather than an LLM-level one.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval method impact confirmed across all 20 runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported, with meaningful variation across LLM versions and a clear LLM-version correlation. `GPT-5.2 Medium`
was the first run to use a targeted `lineno` offset to probe the document tail. `GPT-5.4 Low` and `GPT-5.4 Medium` used targeted
`lineno` jumps to near-end positions. `GPT-5.4 High` used a second `web.open` at `lineno 7390` and explicitly described the tool
as paginated rather than fundamentally incomplete, the clearest articulation of deliberate pagination in the dataset.
`GPT-5.4 Extra High` identified all three truncation layers and navigated around each. `GPT-5.5 Low`, `GPT-5.5 Medium`, and
`GPT-5.5 High` bypassed `web.open` entirely in favor of `curl`, representing a retrieval strategy shift rather than pagination.
No run executed proactive chunking before encountering a truncation signal.

**Combined verdict: `H5` partially supported. Reactive pagination via `lineno` offsets observed from `GPT-5.2 Medium` onward at varying intelligence levels.
Proactive auto-pagination not observed. `curl` is the dominant full-document retrieval strategy from `GPT-5.3-Codex` onward.**

---

## Emergent Findings

1. **The `web.open` line window is LLM-version-correlated.** `L237` is the dominant first-fetch cutpoint across `GPT-5.2`
through `GPT-5.4` runs. `L616` appears as the cutpoint in `GPT-5.5 Extra High` and `GPT-5.4-Mini Extra High` runs. This
represents a measurable behavioral difference between LLM generations on the same surface and the same document, consistent
with the pattern observed in `OP-2`.

2. **The `web.open` windowing mechanism exposes a line-indexed rendered view, not raw HTML.** The tool reports `Total lines: 7423`
for the CommonMark spec page, consistent across all runs. The visible content per call bounded by a word or line limit per
viewport, confirmed by the `[wordlim: 200]` marker visible in `GPT-5.2 Low`. This is distinct from the raw HTTP body of 13,334
lines confirmed by `wc -l` on the saved file.

3. **`curl` is the reliable full-document retrieval path.** Runs using `curl` with escalated network access consistently
returned 514,092 chars and 514,698 bytes. Runs relying solely on `web.open` never retrieved the full document. The decision
to use `curl` was the single strongest predictor of retrieval success, regardless of LLM version or intelligence level.

4. **Three distinct truncation layers identified for the first time in a single run.** `GPT-5.4 Extra High` in Run 16
identified the `web.open` viewport window limit, the terminal stdout display cap of approximately 124,675 tokens on `curl`
output, and the complete underlying HTTP body saved to disk. All three layers operate independently and require different
strategies to navigate.

5. **Intelligence level doesn't reliably predict retrieval quality within an LLM version.** `GPT-5.5 Low` bypassed `web.open`
entirely and retrieved the full document in 27 seconds using 8 percent context. `GPT-5.2 High` looped for 14 minutes 24 seconds
at 45 percent context and never escaped the viewport ceiling. `GPT-5.4-Mini Low` completed in 18 seconds but silently accepted
a partial result when `curl` failed.

6. **`GPT-5.5` shows convergence toward `curl`-first behavior across all intelligence levels.** All four `GPT-5.5` runs either
bypassed `web.open` entirely or used it only for initial surface assessment before switching to `curl`. `GPT-5.5 Low`,
`GPT-5.5 Medium`, and `GPT-5.5 High` produced identical efficiency profiles at approximately 8 percent context and under 45 seconds,
with no observable behavioral differentiation by intelligence level. This mirrors the pattern observed in `OP-2` for the same
LLM version group.

7. **LLM-version jump from `GPT-5.4` to `GPT-5.5` appears more predictive of retrieval strategy than intelligence level.**
Every `GPT-5.5` run used `curl`-first regardless of intelligence level. Within `GPT-5.2` and `GPT-5.3-Codex`, intelligence
level predicted strategy more strongly. The threshold at which `curl`-first behavior emerges collapsed from `Medium` or `High`
down to `Low` between `GPT-5.4` and `GPT-5.5`.

8. **Shared temp filename pattern across `GPT-5.5` runs and `GPT-5.4 High` introduces a contamination risk.** The filename
`commonmark-0.31.2.html` used by `GPT-5.4 High`, `GPT-5.5 Low`, `GPT-5.5 Medium`, `GPT-5.5 High`, and
`GPT-5.5 Extra High`. Whether these runs read existing files from prior sessions or wrote new ones not confirmed on the interpreted
track. The raw track write task is the appropriate venue for isolating this behavior.

9. **Permission-request granularity varies by LLM version and may not correlate with intelligence level.** `GPT-5.2 High`
run 6 asked for `curl` permission approximately 7 times for incremental sub-steps of a single retrieval. `GPT-5.4 Extra High` and
`GPT-5.3-Codex Extra High` asked once. `GPT-5.5` runs consistently asked once. This pattern doesn't follow intelligence
level and may reflect prompt sensitivity or version-level differences in permission handling.

10. **Structural verification depth increased across LLM versions independent of retrieval strategy.**
`GPT-5.4-Mini Extra High` and `GPT-5.5 Extra High` both confirmed `1360` `pre` opens and `1360` `pre` closes and matched `code` open and close counts.
`GPT-5.5 Medium` additionally checked fenced code marker counts. `GPT-5.4 High` Run 15 identified the `L237` cutpoint as ending
on the text `Try It` and used a second `lineno` offset to confirm the document tail, the most complete pagination record in
the `GPT-5.4` group for this test.

---

## Log Label Summary

| Agent | Result | Label |
| --------------- | ------- | --------------------------- |
| `GPT-5.2 Low` | Partial | `PARTIAL - web_open_only + L237_ceiling + no_curl_attempted` |
| `GPT-5.2 Medium` | Partial | `PARTIAL - web_open_only + lineno_tail_probe + no_curl` |
| `GPT-5.2 High` | Partial | `PARTIAL - web_open_loop + L237_ceiling + 14m24s + 45pct_context` |
| `GPT-5.2 Extra High` | Pass | `PASS - curl_complete + curl_to_file + asked_permission_twice + CONTAM_RISK: commonmark_0.31.2.html` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_complete + lineno_pagination_noted + explicit_window_description + CONTAM_RISK: commonmark_0312.html` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_complete + web_open_bypassed + 40s + CONTAM_RISK: op4_commonmark_0312.html` |
| `GPT-5.3-Codex Low` | Partial | `PARTIAL - web_open_only + L237_ceiling + no_curl + 8s` |
| `GPT-5.2 High - Run 6` | Pass | `PASS - curl_complete + 7x_permission_requests + granular_sub_steps` |
| `GPT-5.4-Mini Low` | Partial | `PARTIAL - web_open_two_calls + curl_dns_fail + tail_reached_L7422` |
| `GPT-5.4-Mini Medium` | Pass | `PASS - curl_complete + explicit_windowed_vs_underlying_distinction + 1m31s` |
| `GPT-5.4-Mini High` | Pass | `PASS - curl_complete + urllib_request + self_corrected_bytes_vs_chars` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - curl_complete + pre_code_balance_1360 + L616_cutpoint + CONTAM_RISK: commonmark.html` |
| `GPT-5.4 Low` | Pass | `PASS - curl_complete + first_Low_tier_curl_success + lineno_7390_probe` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_complete + L237_to_L7164_skip_described + sandbox_escalation` |
| `GPT-5.4 High` | Pass | `PASS - curl_complete + pagination_described_correctly + lineno_7390_confirmed + CONTAM_RISK: commonmark-0.31.2.html` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_complete + three_truncation_layers_identified + ruby_tail + parallel_measurement + CONTAM_RISK: op4_commonmark_0_31_2.html` |
| `GPT-5.5 Low` | Pass | `PASS - curl_only + web_open_bypassed + 27s + 8pct_context + CONTAM_RISK: commonmark-0.31.2.html_shared_name` |
| `GPT-5.5 Medium` | Pass | `PASS - curl_only + web_open_bypassed + fenced_marker_count + 35s + CONTAM_RISK: commonmark-0.31.2.html_shared_name` |
| `GPT-5.5 High` | Pass | `PASS - curl_only + web_open_bypassed + all_tag_counts_matched + 44s + CONTAM_RISK: commonmark-0.31.2.html_shared_name` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_complete + web_open_L616_initial + pre_code_balance_1360 + parallel_checks + CONTAM_RISK: commonmark-0.31.2.html_shared_name` |
