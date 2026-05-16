# OP-1 Summary

## Test Conditions

|                 | **OP-1**                                                                        |
| --------------- | ------------------------------------------------------------------------------- |
| URL             | `https://en.wikipedia.org/wiki/Machine_learning#History`                        |
| Expected size   | ~40 KB assumed; actual ~696 KB raw HTML / ~173K tokens                          |
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
| `GPT-5.2 Low` | 696,389 bytes / 693,475 chars | ~173,369 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `curl`, `wc`, `tail` | No | Fragment-aware reasoning; no workspace dir created; 1m4s |
| `GPT-5.2 Medium` | 4,170 | ~1,192 | Yes - web.open L303 | `L300-L303 line refs` | `web.run`, `Node REPL` | No | wordlim: 200 visible; line-by-line last50 compute chain; 9m4s |
| `GPT-5.2 High` | 693,475 | ~173,369 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `python3` | Yes `ml.html` | Python DNS fail then curl fallback; chunked line windows via web.run; 2m42s |
| `GPT-5.2 Extra High` | 693,475 | ~173,368 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail`, `python3`, `find`, `search_query` | Yes `op1_response.html` | 37 web searches; History section isolated via regex at 32,650 chars; 10m30s |
| `GPT-5.3-Codex Low` | ~23,000-30,000 est. | ~5,700-7,500 | Yes - web.open L552 missing middle | `a benchmark for "general intelligence".[24][25][26]` | `web.open` | No | lineno offset pagination; missing middle window L553-L1565 confirmed; 21 s |
| `GPT-5.3-Codex Medium` | 693,475 | ~174,000 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail` | Yes `op1_machine_learning.html` | web.open and curl dual-path isolation; 49 s |
| `GPT-5.3-Codex High` | 693,475 | ~173,369 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.open`, `curl`, `wc`, `tail`, `od` | No | Explicit windowing reasoning; L305 and L551 web.open cutpoints named; 2m31s |
| `GPT-5.3-Codex Extra High` | 693,475 | ~173,000 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail`, `perl`, `multi_tool_use.parallel` | Yes `op1_ml_history.html` | L552 web.open cutpoint; session log search attempted; 2m42s |
| `GPT-5.4-Mini Low` | ~35,000-45,000 est. | ~8,000-11,000 | Yes - web.open L305 | `*` | `web.open` | Yes empty | curl returned 0 bytes silently; empty ml_page.html created; 24 s |
| `GPT-5.4-Mini Medium` | ~23,000 est. | ~5,500-6,000 | Yes - web.open L305 then L560 | `...original sizes, respectively.` | `web.run` | No | wordlim: 200 metadata confirmed; turn0view0 / turn1view0 / turn2view0 pagination; 1m1s |
| `GPT-5.4-Mini High` | 693,475 | ~173k | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.open`, `curl`, `wc`, `python3` | No | wordlim: 200 confirmed; web.open L552; mcp__node_repl__ fetch attempted first; 1m26s |
| `GPT-5.4-Mini Extra High` | ~25,000 est. | ~6,200 | Yes - web.open L552 then L553 | `mark for "general intelligence".[24][25][26]` | `web.open`, `Node REPL` | No | Cleanest pagination handoff; L552/L553 consecutive; no curl; 3m16s |
| `GPT-5.4 Low` | ~11,000-13,000 est. | ~3,000-4,000 | Yes - web.open L305 | `39† 5.1 Artificial neural networks 】` | `web.open` | No | lineno=null initial then lineno=1848 jump; no curl; 53 s |
| `GPT-5.4 Medium` | 696,389 bytes / 693,475 chars | ~174,000 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.open`, `curl`, `wc`, `tail`, `Node REPL` | Yes `op1_machine_learning.html` | web.open beginning-then-jump behavior; middle omitted; fragment normalization confirmed; 1m15s |
| `GPT-5.4 High` | 696,389 bytes / 693,475 chars | ~174,000 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail` | No | web.open windowed but full doc addressable via lineno=1820; fragment server-blindness stated; 2m36s |
| `GPT-5.4 Extra High` | 693,475 | ~173k | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail`, `python3`, `perl` | Yes `op1_machine_learning.html` | L552 web.open clip; 20 commands; possible tmp file reuse from Run 14; 5m7s |
| `GPT-5.5 Low` | 693,475 | ~173,369 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `curl`, `wc`, `tail`, `multi_tool_use.parallel` | No | web.open bypassed entirely; fragment-aware; most efficient full-doc retrieval; 1m22s |
| `GPT-5.5 Medium` | 693,475 | ~173,369 | Yes - web.open L552 | `mark for "general intelligence".[24][25][26]` | `web.run`, `curl`, `wc`, `Node REPL` | No | Cleanest dual-surface report; separate last-50 for each path; 1m57s |
| `GPT-5.5 High` | 693,475 | ~173,369 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `curl`, `wc`, `tail` | No | web.open bypassed; fragment server-blindness stated; 1m38s |
| `GPT-5.5 Extra High` | 693,475 | ~173,400 | No - curl complete | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail`, `perl`, `rg`, `multi_tool_use.parallel` | No | HTTP headers saved to op1_headers.txt; content-length cross-verified; L552 clip noted; 3m45s |

---

## `H1`: Character-based truncation at a fixed ceiling

**Not supported via `curl` path.** Successful `curl` fetches returned 693,475 chars consistently across all runs that used curl,
far above any 10-100 KB ceiling threshold. The ceiling hypothesis is only partially consistent with `web.open` results, where
visible chars ranged ~11,000-45,000, but those reflect a fixed line window controlled by `wordlim: 200` rather than a character
ceiling. No run encountered a mid-content character cut on the curl path.

**Combined verdict: `H1` no for `curl` path. Partially consistent with `web.open` path where the window is line-count-bound not
character-bound.**

---

## `H2`: Token-based truncation at ~2,000 tokens

**Not supported.** Successful `curl` fetches returned ~173-174K tokens, orders of magnitude above the 2,000-token threshold.
`web.open` results ranged ~1,192-11,000 tokens depending on model and whether pagination used. No run approached or hit a
2,000-token ceiling on either path. The closest result was `GPT-5.2` `Medium` at ~1,192 tokens, which was a `web.open` window
result, not a token gate.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

**Partially supported.** The `web.open` extraction window consistently terminates at L305 on first fetch for lower-intelligence
runs and at L552 for higher-intelligence or multi-turn runs. The L552 cutpoint confirmed across Runs 7, 8, 11, 12, 15, 18, and 20,
spanning `GPT-5.3-Codex` through `GPT-5.5`. The content at L552 ends mid-article in the Data compression section, and the last
visible text across multiple independent runs converged on the same phrase: `mark for "general intelligence".[24][25][26]`. This is
a structural landmark rather than an arbitrary byte position. However, truncation driven by `wordlim: 200` line windowing, not by
Markdown boundary detection. True structure-aware truncation by agent choice wasn't demonstrated.

**Combined verdict: `H3` partially supported. Truncation boundary is structurally consistent and repeatable but mechanism is a fixed
line window, not Markdown-awareness.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

**Untested for cross-surface comparison.** All 20 runs used the Codex IDE surface exclusively. VS Code-Codex extension comparison
wasn't performed. Within the Codex IDE surface, a meaningful tool-path split confirmed: `curl` returns ~696K complete raw HTML,
`web.open` returns a windowed 141-line or ~L552-line partial extraction. This is a retrieval method difference, not a surface
difference. The two-tier network access pattern, sandboxed DNS failure followed by escalated curl success, is consistent across
all model families and constitutes an infrastructure property of the surface, not a model behavior.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval method impact confirmed across 15+ runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

**Partially supported, with meaningful variation across model families.** `GPT-5.3-Codex` Low used `lineno` offset pagination with
`turn1view0` / `turn2view0`, explicitly confirming a missing middle window and constituting the clearest auto-pagination behavior
in the dataset. `GPT-5.4-Mini` `Medium` used three-turn pagination with advancing offsets. `GPT-5.4-Mini` `Extra High` executed a
clean L552-to-L553 consecutive handoff. `GPT-5.4` `Low` and `GPT-5.4` `Medium` used targeted `lineno` jumps to near-end positions
rather than sequential pagination. `GPT-5.5` `Low` and `High` bypassed web.open entirely and went straight to `curl`, representing
a different form of retrieval strategy rather than pagination. No run executed proactive chunking before encountering a truncation signal.

**Combined verdict: `H5` partially supported. Reactive pagination observed in multiple runs. Proactive auto-pagination not observed.
Tool escape to curl is the dominant full-document retrieval strategy.**

---

## Emergent Findings

1. **The `#History` fragment is silently ignored by both `curl` and `web.open`.** Both tools return the full Machine learning page
HTML rather than a subsection. This was first noted in `GPT-5.2` `Low` and confirmed across `GPT-5.4` `Medium`, `GPT-5.4` `High`,
`GPT-5.5` `Low`, `GPT-5.5` `High`, and `GPT-5.5` `Extra High`. Fragment-awareness was more consistent in later LLM families.
`GPT-5.2` `Low` correctly identified the behavior at the lowest intelligence level in its family, which was the most notable
single-run insight in the dataset.

2. **The L305 and L552 web.open cutpoints are stable surface properties.** L305 appeared as the first-fetch truncation point in
Runs 7, 9, 10, and 13 across `GPT-5.3-Codex` `High` through `GPT-5.4` `Low`. L552 appeared as the dominant cutpoint in Runs 7,
8, 11, 12, 15, 18, and 20, spanning `GPT-5.3-Codex` `High` through `GPT-5.5` `Extra High`. The content landmark at L552 is the
Data compression section ending on `mark for "general intelligence".[24][25][26]`, confirmed independently across six runs.

3. **`wordlim: 200` is the operative `web.open` window parameter.** First surfaced in `GPT-5.4-Mini` `Medium` Run 10 and confirmed
in Runs 11, 12, 14, and 15. This parameter appears to control the line window size and explains both the L305 and L552 cutpoints as
consecutive 200-line windows from the rendered document.

4. **`curl` is the reliable full-document retrieval path.** Runs using `curl` consistently returned 693,475 chars and 696,389 bytes,
matching the HTTP `content-length` header confirmed in Run 20. Runs relying solely on web.open never retrieved the full document.
The decision to use `curl`, whether immediate or escalated after DNS failure, was the single strongest predictor of retrieval success.

5. **Intelligence level doesn't reliably predict retrieval quality.** `GPT-5.2` `Low` retrieved the full document via curl in 1m4s.
`GPT-5.2` `Extra High` used 77% context, 37 web searches, and 10m30s on the same task. `GPT-5.5` `Low` bypassed `web.open` entirely
and retrieved the full document in 1m22s using 8% context. `GPT-5.5` `Extra High` used the most commands in its family while still
noting the L552 `web.open` clip. The most efficient runs were consistently Low or Medium intelligence levels that used curl directly.

6. **A display truncation versus retrieval truncation distinction emerged in Run 18.** `GPT-5.5``Medium` reported that the curl output
clipped in the terminal display but the saved file was complete, explicitly separating what the agent saw in the terminal from what was
actually fetched. This distinction is relevant to interpreting agent-reported truncation across all runs.

7. **`web.open` normalizes the URL fragment.** Run 14 explicitly reported that `#History`'s stripped from the URL in the `web.open`
normalized display, showing `https://en.wikipedia.org/wiki/Machine_learning` rather than the fragment URL. This confirms the fragment
discarded at the tool level, not just at the HTTP level.

8. **Workspace persistence creates contamination risk across runs.** Files saved to `/private/tmp` from earlier runs remained accessible
to later runs. The `op1_machine_learning.html` naming pattern appeared in Runs 14 and 16, raising the possibility that Run 16 read a
cached file rather than executing a fresh fetch. The `codex-browser-use` directory read by most runs but contained no usable content
in the majority of cases.

9. **`GPT-5.5` shows a convergence toward `curl`-first behavior.** Three of four `GPT-5.5` runs either bypassed `web.open` entirely or
used it only for initial surface assessment before switching to `curl`. This represents a behavioral shift relative to `GPT-5.2` and
`GPT-5.3-Codex`, where `web.open` was the default entry point.

---

## Log Label Summary

| Agent | Result | Label |
| --------------- | ------- | --------------------------- |
| `GPT-5.2 Low` | Pass | `PASS - curl_complete + fragment_aware + no_workspace_dir` |
| `GPT-5.2 Medium` | Partial | `PARTIAL - web_open_L303 + wordlim_200 + line_by_line_compute_chain + 9m` |
| `GPT-5.2 High` | Pass | `PASS - curl_complete + chunked_web_run_windows + History_section_isolated` |
| `GPT-5.2 Extra High` | Pass | `PASS - curl_complete + 37_searches + regex_section_isolation + diminishing_returns` |
| `GPT-5.3-Codex Low` | Partial | `PARTIAL - web_open_only + lineno_pagination + missing_middle_L553-L1565_confirmed` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_complete + dual_path_isolation + efficient_49s` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_complete + L305_L551_cutpoints_named + windowing_self_aware` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_complete + L552_confirmed + session_log_search_attempted` |
| `GPT-5.4-Mini Low` | Partial | `PARTIAL - web_open_L305 + curl_0bytes_silent_fail + empty_file_created` |
| `GPT-5.4-Mini Medium` | Partial | `PARTIAL - web_open_L305_L560 + wordlim_200_confirmed + three_turn_pagination` |
| `GPT-5.4-Mini High` | Pass | `PASS - curl_complete + wordlim_200_confirmed + L552_web_open + node_repl_attempted` |
| `GPT-5.4-Mini Extra High` | Partial | `PARTIAL - web_open_only + L552_L553_clean_handoff + no_curl` |
| `GPT-5.4 Low` | Partial | `PARTIAL - web_open_L305 + lineno_1848_jump + no_curl + lineno_null_exposed` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_complete + fragment_normalization_confirmed + middle_omission_noted` |
| `GPT-5.4 High` | Pass | `PASS - curl_complete + lineno_1820_verification + fragment_server_blindness_stated` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_complete + L552_noted + possible_tmp_reuse + 20_commands` |
| `GPT-5.5 Low` | Pass | `PASS - curl_only + web_open_bypassed + fragment_aware + most_efficient` |
| `GPT-5.5 Medium` | Partial | `PARTIAL - web_open_L552 + curl_complete + cleanest_dual_surface_report` |
| `GPT-5.5 High` | Pass | `PASS - curl_only + web_open_bypassed + fragment_server_blindness_stated` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_complete + content_length_cross_verified + headers_saved + L552_noted` |
