# EC-1 Summary

## Test Conditions

|                 | **EC-1**                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------- |
| URL             | `https://ai.google.dev/gemini-api/docs`                                                           |
| Expected size   | ~100 KB; confirmed ~132,894 chars / 133,110 bytes / ~33,200 tokens via valid `curl` fetch         |
| Surface         | Codex IDE                                                                                         |
| Workspace       | Session-scoped sandbox; `/private/tmp` cleared between sessions; `Documents/Codex` persistent     |
| Track           | `T1` GPT-interpreted, Codex IDE                                                                   |
| Method          | GPT-interpreted                                                                                   |
| Runs            | 20                                                                                                |
| Chunks returned | N/A, interpreted track                                                                            |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | ~132,894 | ~33,223 | No - `curl` complete | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3` | Yes | `curl` escalation; wrote `ec1.html` to `/private/tmp`; contamination risk - same filename reused by `GPT-5.2 High`; 33 seconds |
| `GPT-5.2 Medium` | indeterminate | indeterminate | Partially - `web.run open` returns rendered line-numbered extract; character count not directly measurable from surface; content ends at language selector list | `— 简体\nL353:  ✱ 中文 — 繁體\nL354:  ✱ 日本語\nL355:  ✱ 한국어` | `web.run`, `web.open` | No | no `curl`; `web.run open` only; agent can't obtain exact char count from tool-return buffer; token estimate indeterminate; 24 seconds |
| `GPT-5.2 High` | ~132,894 | ~33,224 | No - `curl` complete | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3` | Yes | `curl` escalation; wrote `ec1.html` to `/private/tmp`; contamination risk - same filename as `GPT-5.2 Low` artifact; double report output; implicit bypass of `web` pipeline implied in first report only; 1 minute 31 seconds |
| `GPT-5.2 Extra High` | ~13,383 | ~3,346 | Indeterminate - no explicit truncation reported; agent spent ~48 minutes re-measuring same `web.run open` buffer without escalating to `curl` | `— 简体\nL353:  ✱ 中文 — 繁體\nL354:  ✱ 日本語\nL355:  ✱ 한국어` | `web.run`, `web.open`, `functions.exec_command`, `python3` | No | runaway failure mode; 113 web searches; context auto-compacted mid-run; never escalated to `curl`; no artifacts written; 48 minutes 10 seconds |
| `GPT-5.3-Codex Low` | ~19,000 est. | ~4,700 est. | Partially - agent reports truncation likely; content ends at language selector list; `curl` returned 0 bytes | `✱ 中文 — 繁體\nL354: ✱ 日本語\nL355: ✱ 한국어` | `web.run`, `web.open`, `curl` | No | `curl` failed silently returning 0 bytes; `web.run open` only effective path; agent didn't recover from `curl` failure; no artifacts written; 11 seconds |
| `GPT-5.3-Codex Medium` | ~132,894 | ~33,300 | No - `curl` complete | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `sed` | No | `curl` escalation; explicitly distinguishes `web.open` extracted view from raw `curl` response; no artifacts written; 56 seconds |
| `GPT-5.3-Codex High` | ~132,894 | ~33,200 | No - `curl` complete; `web.open` noted as extracted/normalized 356-line view distinct from raw HTML | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `perl` | Yes | `curl` escalation; wrote `ec1_gemini_docs.html` to `/private/tmp`; uniquely fired `web.run` with `search_query` for unclear purpose; 1 minute 33 seconds |
| `GPT-5.3-Codex Extra High` | ~132,894 | ~33,223.5 | No - `curl` complete; `web.open` noted as extracted/normalized 356-line view | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3`, `urllib` | No | `curl` + `urllib` dual-path verification; also fired `web.run` with `search_query` for unclear purpose; second consecutive `GPT-5.3-Codex` run showing this anomaly; no artifacts written; 1 minute 50 seconds |
| `GPT-5.4-Mini Low` | ~133,106 bytes via `curl`; `web.open` extraction size not isolated | indeterminate for `web.open`; ~33k for `curl` | Indeterminate - agent explicitly distinguishes `web.open` extraction from raw `curl` but doesn't quantify extraction size; offers second pass unprompted but doesn't execute | `web.open` payload not verbatim reported; `curl` tail ends `</html>` | `web.run`, `web.open`, `curl` | No | single `web.open` plus single `curl`; no chunking; agent aware of two-surface distinction but doesn't act on it; no artifacts written; 16 seconds |
| `GPT-5.4-Mini Medium` | 144,132 DOM HTML chars; 4,521 visible body text chars | ~36k for HTML; ~1.1k for visible text | Indeterminate - DOM closes cleanly; `web.open` surface not isolated for truncation check | `-events: none; z-index: 2147483000;"></div></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `Browser`, `node_repl` | No | unique Browser/Playwright toolchain; `curl` failed; escalated to browser; first run to distinguish DOM HTML chars from visible body text chars; `TypeError: fetch is not a function` during browser eval; 2 minutes 27 seconds |
| `GPT-5.4-Mini High` | 144,444 DOM HTML chars; 4,521 visible body text chars | ~36k for HTML; ~1.1k for visible text | Indeterminate - no truncation reported; agent misidentifies `web.open` reaching footer as completeness | `-events: none; z-index: 2147483000;"></div></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `Browser`, `node_repl` | No | Browser/Playwright toolchain again; `curl` failed; second consecutive `GPT-5.4-Mini` run using Browser surface; Playwright API mismatch encountered; no artifacts written; 2 minutes 13 seconds |
| `GPT-5.4-Mini Extra High` | ~132,894 | ~35,000 | No - `curl` complete; `web.open` 356-line extract noted but boundary not evaluated | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3` | No | reverts to `curl` + Python verification pattern despite Medium and High using Browser; no artifacts written; 3 minutes 30 seconds |
| `GPT-5.4 Low` | ~132,894 | ~33,224 | No - `curl` complete; `web.open` noted as extracted view but boundary not evaluated | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `ruby` | No | uniquely used Ruby for token estimation; first run to explicitly articulate two-surface distinction in final summary without being prompted; no artifacts written; 1 minute 22 seconds |
| `GPT-5.4 Medium` | ~133,106 | ~33,300 | No - `curl` complete; `web.open` noted as "much smaller and more structured" than `curl`; rare `…23376 tokens truncated…` console notice observed | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `file` | Yes | `curl` escalation; wrote `ec1_gemini_api_docs.html` to workspace `Documents/Codex` directory; clearest articulation of two-surface distinction; `…23376 tokens truncated…` console notice correctly identified as rendering artifact not retrieval truncation; 1 minute 19 seconds |
| `GPT-5.4 High` | ~133,110 | ~33,278 | No - `curl` complete; HTTP `content-length: 133110` header verified; `web.open` noted as "much smaller" extracted view | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `sed`, `perl` | Yes | `curl` escalation with HTTP header capture; wrote `ec1_headers.txt` and `ec1_body.html` to `/private/tmp`; most forensically thorough run in cycle; HTTP/2 200 and exact byte match confirmed; 1 minute 43 seconds |
| `GPT-5.4 Extra High` | ~13,132–13,398 | ~3.3k–3.4k | Indeterminate - no `curl` invoked; agent explicitly recognizes `web.open` returned "a much smaller transformed representation" relative to ~100 KB expectation | `— 简体\nL353:  ✱ 中文 — 繁體\nL354:  ✱ 日本語\nL355:  ✱ 한국어` | `web.run`, `web.open`, `node_repl` | No | only Extra High run that didn't escalate to `curl`; only run across all 20 to measure `web.open` output in isolation with this precision; "partial overall" completeness assessment; 4 minutes 41 seconds |
| `GPT-5.5 Low` | ~132,890 | ~33,200 | Indeterminate - `web` pipeline bypassed entirely; `web.open` surface unexamined | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `functions.exec_command`, `curl`, `wc`, `tail`, `file`, `rg`, `perl` | No | first `GPT-5.5` run; explicitly states it didn't invoke `web` or `web.open`; direct `curl` only; contamination risk - `/private/tmp/ec1_gemini_docs.html` same filename as `GPT-5.3-Codex High` artifact; 28 seconds |
| `GPT-5.5 Medium` | ~132,894 | ~33,200 | No - `curl` complete; `web` pipeline bypassed | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `rg` | Yes | second consecutive `GPT-5.5` run to bypass `web`/`web.open` entirely; wrote `gemini-api-docs.html` to workspace `Documents/Codex` directory; 7 structural file searches for tag balance; 40 seconds |
| `GPT-5.5 High` | ~132,890 | ~33,200 | Indeterminate - truncation implied in completeness note; `web.open` described as "extracted/readability-style text view" reaching footer | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `od`, `rg` | No | first `GPT-5.5` run to use `web.open` before escalating to `curl`; "readability-style text view" is most descriptively accurate characterization of `web.open` output in the cycle; no artifacts written; 1 minute |
| `GPT-5.5 Extra High` | ~132,894 | ~33,200 | Indeterminate - truncation implied by bypass of `web` pipeline; no `web.open` surface data | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `head`, `rg` | No | third `GPT-5.5` run to bypass `web`/`web.open` entirely; only `GPT-5.5 High` used `web.open`; no artifacts written; 1 minute 21 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported via the `curl` path. Successful `curl` fetches returned approximately 132,894 chars consistently across all runs with DNS access, well above
the 10–100 KB range with no ceiling hit. Runs relying solely on `web.run open` returned substantially lower output: `GPT-5.2 Medium` and `GPT-5.4 Extra High`
measured approximately 13,383 chars from the `web.open` surface, roughly 10% of the confirmed raw fetch size. `GPT-5.3-Codex Low` estimated approximately
19,000 chars after `curl` failed. `GPT-5.2 Extra High` measured the same ~13,383-char buffer across 113 web searches without escalating. The `web.open`
surface consistently delivers a condensed extracted rendering rather than the raw HTML body, and the ceiling on that surface appears to sit around
13,000–19,000 chars depending on LLM version.

**Combined verdict: `H1` no for the `curl` path where the ceiling was never hit. Partially consistent with the `web.open` path where viewer output is
consistently ~10% of the confirmed raw fetch size. `GPT-5.4 Extra High` is the strongest single-surface `H1` signal in the set, being the only run to
measure `web.open` output in isolation across all 20 runs.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported via the `curl` path. Successful `curl` fetches returned approximately 33,200 tokens consistently, well above the 2,000-token threshold.
`web.open`-only runs returned lower estimates: `GPT-5.4 Extra High` measured approximately 3,300–3,400 tokens from the `web.open` surface exclusively, and
`GPT-5.3-Codex Low` estimated approximately 4,700 tokens after `curl` failure. These figures are closer to the hypothesis range but reflect the viewer surface
rather than a token-based cutoff mechanism. No run produced a retrieval approaching a 2,000-token ceiling via either path.

**Combined verdict: `H2` no. Token ceiling not a factor on the `curl` path. `web.open` surface token counts are lower but don't cluster at 2,000 tokens and
aren't consistent enough across runs to confirm a fixed ceiling.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported. The `web.open` surface consistently delivered a line-indexed extraction ending at the language selector list at approximately `L355`, the same
terminal point across `GPT-5.2 Medium`, `GPT-5.3-Codex Low`, `GPT-5.2 Extra High`, and `GPT-5.4 Extra High`. This endpoint is structurally coincidental rather
than Markdown-boundary-driven, as the page is HTML rather than Markdown. Agents that stayed on `web.open` consistently misidentified reaching the footer as
completeness rather than recognizing the 356-line extraction as a bounded view by design. No run evaluated whether the extraction boundary fell on a structural
element versus an arbitrary position.

**Combined verdict: `H3` indeterminate. The consistent `L355` terminal point across runs suggests a fixed extraction window rather than structure-aware truncation,
but the HTML format of the test URL makes Markdown boundary evaluation impossible. The hypothesis not confirmed or ruled out from this test cycle.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively. Within the Codex IDE surface, a consistent two-tier network access pattern
confirmed across most runs: sandboxed DNS resolution failure on the first `curl` attempt followed by escalated success after permission approval.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval infrastructure behavior confirmed consistent across all 20 runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Not supported in the proactive sense. No run executed chunking or pagination before encountering a retrieval signal. The dominant pattern across nearly all runs was:
invoke `web.run open`, note the extracted view, escalate to `curl` for full measurement. `GPT-5.2 Extra High` is the clearest failure case, looping on `web.open`
re-measurement for 48 minutes without escalating. `GPT-5.4-Mini Medium` and `GPT-5.4-Mini High` escalated to Browser and Playwright rather than `curl`, representing
the most adaptive multi-path escalation in the cycle. `GPT-5.5 Low`, `GPT-5.5 Medium`, and `GPT-5.5 Extra High` bypassed `web.open` entirely and went directly to
`curl`, producing no viewer surface data at all.

**Combined verdict: `H5` no. Reactive escalation from `web.run open` to `curl` is the dominant retrieval strategy from `GPT-5.2` through `GPT-5.5`. True proactive
auto-pagination not observed. The `GPT-5.2 Extra High` runaway is the closest behavior to looped retrieval but represents a failure mode rather than intentional chunking.**

---

## Emergent Findings

1. **`web.run open` delivers ~10% of the raw page by character count.** The confirmed `web.open` extraction across runs that measured it in isolation sits at approximately
13,000–13,400 chars against a ~132,894-char raw fetch. `GPT-5.4 Extra High` is the only run to measure this exclusively, making it the most informative single-surface data
point in the cycle.

2. **`curl` reliable full-document retrieval path.** Runs using `curl` with escalated network access consistently returned approximately 132,894 chars. The decision to
escalate to `curl` was the single strongest predictor of retrieval completeness regardless of LLM version or intelligence level, mirroring the `SC-4` finding.

3. **11 artifacts written across 20 runs, mostly to `/private/tmp`, twice to `Documents/Codex`.** This is consistent with the ~40–60% artifact production rate observed in
prior test cycles. Agents frequently created workspace infrastructure directories and then wrote no artifacts to them.

4. **Truncation reporting was mostly implicit or mixed across the cycle.** Explicit yes/no truncation reports were less common than implied truncation through tooling strategy,
completeness notes, or reasoning about surface limitations. Agents that escalated to `curl` tended to report no truncation on the raw fetch while silently treating `web.open`
as incomplete without formally assessing it.

5. **`GPT-5.2 Extra High` produced the only runaway failure mode in the cycle.** 113 web searches and 48 minutes 10 seconds with context auto-compaction mid-run, all spent
re-measuring the same `web.open` buffer. No escalation to `curl` occurred. This is the clearest failure mode in the entire `EC-1` set and represents a qualitatively different
failure than the `GPT-5.3-Codex Low` `curl` silent failure.

6. **`GPT-5.4-Mini Medium`, `GPT-5.4-Mini High` uniquely escalated to Browser and Playwright.** This two-run cluster within the same LLM version suggests a model-version
characteristic rather than an intelligence-level behavior. Both ran into `curl` DNS failure first and responded by opening a browser session rather than requesting escalated
network access.

7. **`GPT-5.4 Extra High` most informative `web.open` surface measurement in the cycle.** By staying on `web.open` exclusively and measuring the returned payload with Node Repl,
it produced the only clean isolation of `web.open` output size across all 20 runs. All other runs that measured size did so after escalating to `curl`, conflating the two surfaces.

8. **`GPT-5.5` introduced a consistent `web` pipeline bypass pattern not seen in prior LLM versions.** Three of four `GPT-5.5` runs never invoked `web` or `web.open` at all,
going directly to `curl`. Only `GPT-5.5 High` used `web.open`. This makes `GPT-5.5` the least useful LLM version for `H1`, `H2`, and `H3` evaluation and the most efficient for raw
retrieval.

9. **`multi_tool_use.parallel` appears across `GPT-5.5` runs but not in `GPT-5.2` or `GPT-5.3-Codex`.** Consistent with the `SC-4` finding, this parallel tool invocation pattern
appears to be a `GPT-5.5`-level capability rather than an intelligence-level behavior.

10. **`GPT-5.3-Codex High`, `GPT-5.3-Codex Extra High` both fired `web.run` with `search_query` for unclear purposes.** Output obscured in both cases. This two-run pattern within
the same LLM version warrants flagging as a model-version anomaly.

11. **Artifact filename contamination occurred twice in the cycle.** `GPT-5.2 High` wrote `ec1.html` to `/private/tmp`, the same filename used by `GPT-5.2 Low`. `GPT-5.5 Low` wrote
`ec1_gemini_docs.html` to `/private/tmp`, the same filename used by `GPT-5.3-Codex High`. Both represent integrity risks for any run that reads rather than overwrites the prior artifact.

12. **`GPT-5.4 High` only run to capture-save HTTP response headers.** `ec1_headers.txt` artifact includes `content-length: 133110`, HTTP/2 `200` status, `last-modified`, and CSP headers,
providing the most complete server-side retrieval verification in the cycle.

13. **Intelligence level doesn't reliably predict retrieval quality within LLM version.** `GPT-5.5 Low` produced one of the most efficient retrieval sequences in the set.
`GPT-5.2 Extra High` produced the worst outcome. The most consequential behavioral differences are LLM-version-level, not intelligence-level, consistent with `SC-4` results.

14. **Hypotheses largely unsupported due to agentic tendency to bypass `web.run open` for `curl`.** The `web.run open` surface is where `H1`, `H2`, and `H3` behavior lives. Most runs
escalated past it before measuring it, leaving the in-house fetch tool boundaries unexamined. The test cycle demonstrates that the agent's tool escalation instinct works against the
test's observational goals.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.2 Low` | Pass | `PASS - curl_133KB_complete + web_open_implicit_bypass + ec1_html_artifact + private_tmp + filename_contamination_risk + 33s` |
| `GPT-5.2 Medium` | Partial | `PARTIAL - web_run_open_only + line_numbered_extract + char_count_indeterminate + ends_language_list_L355 + no_artifacts + 24s` |
| `GPT-5.2 High` | Pass | `PASS - curl_133KB_complete + web_open_implicit_bypass + double_report_output + ec1_html_artifact + private_tmp + filename_contamination_risk + 1m31s` |
| `GPT-5.2 Extra High` | Fail | `FAIL - web_run_open_loop + 113_web_searches + no_curl_escalation + context_auto_compacted + no_artifacts + runaway_failure_mode + 48m10s` |
| `GPT-5.3-Codex Low` | Partial | `PARTIAL - curl_0_bytes + web_open_19KB_est + truncation_reported_likely + ends_language_list + no_curl_recovery + no_artifacts + 11s` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_133KB_complete + web_open_two_surface_distinction + no_artifacts + 56s` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_133KB_complete + web_open_356_line_noted + search_query_anomaly + ec1_gemini_docs_artifact + private_tmp + 1m33s` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_133KB_complete + urllib_dual_path + web_open_356_line_noted + search_query_anomaly_repeat + no_artifacts + 1m50s` |
| `GPT-5.4-Mini Low` | Indeterminate | `INDETERMINATE - curl_133KB_confirmed + web_open_extraction_not_isolated + two_surface_distinction_noted + second_pass_offered_not_executed + no_artifacts + 16s` |
| `GPT-5.4-Mini Medium` | Pass | `PASS - browser_playwright_144KB_dom + curl_failed + web_open_bypassed + dom_vs_visible_text_distinguished + no_artifacts + 2m27s` |
| `GPT-5.4-Mini High` | Pass | `PASS - browser_playwright_144KB_dom + curl_failed + web_open_bypassed + dom_vs_visible_text_distinguished + playwright_mismatch_encountered + no_artifacts + 2m13s` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - curl_133KB_complete + web_open_356_line_noted + reverts_to_curl_pattern + no_browser_escalation + no_artifacts + 3m30s` |
| `GPT-5.4 Low` | Pass | `PASS - curl_133KB_complete + web_open_partial + ruby_token_estimation + two_surface_distinction_explicit + no_artifacts + 1m22s` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_133KB_complete + web_open_smaller_noted + console_truncation_notice_observed + ec1_gemini_api_docs_artifact + Documents_Codex + 1m19s` |
| `GPT-5.4 High` | Pass | `PASS - curl_133KB_complete + http_header_capture + content_length_verified + ec1_headers_txt + ec1_body_html + private_tmp + 1m43s` |
| `GPT-5.4 Extra High` | Indeterminate | `INDETERMINATE - web_open_only + 13398_chars_isolated + 3346_tokens_isolated + partial_completeness_acknowledged + no_curl + no_artifacts + 4m41s` |
| `GPT-5.5 Low` | Pass | `PASS - curl_133KB_complete + web_never_invoked + direct_curl_only + filename_contamination_risk + 28s` |
| `GPT-5.5 Medium` | Pass | `PASS - curl_133KB_complete + web_never_invoked + multi_tool_use_parallel + gemini_api_docs_artifact + Documents_Codex + 7_structural_searches + 40s` |
| `GPT-5.5 High` | Pass | `PASS - curl_133KB_complete + web_open_readability_style_noted + readability_characterization_most_accurate + no_artifacts + 1m` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_133KB_complete + web_never_invoked + multi_tool_use_parallel + no_artifacts + 1m21s` |
