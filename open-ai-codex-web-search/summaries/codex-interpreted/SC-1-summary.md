# SC-1 Summary

## Test Conditions

|                 | **SC-1**                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------- |
| URL             | `https://ai.google.dev/gemini-api/docs/url-context`                                          |
| Expected size   | ~40 KB assumed; actual ~121,409–121,826 chars / 121,654–121,826 bytes / ~30,350–30,400 tokens via valid fetch |
| Surface         | Codex IDE                                                                                    |
| Workspace       | Session-scoped sandbox; `/private/tmp` cleared between sessions; `Documents/Codex` persistent |
| Track           | `T1` GPT-interpreted, Codex IDE                                                              |
| Method          | GPT-interpreted                                                                              |
| Runs            | 20                                                                                           |
| Chunks returned | N/A, interpreted track                                                                       |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | ~120,042 chars | ~30,000 | No - `curl` complete. Yes - `web.open` extracted view | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `python3` | No | `curl` not used; `urllib` via `python3`; no artifacts written; 1 minute 42 seconds |
| `GPT-5.2 Medium` | ~120,042 chars | ~30,000 | No - `curl` complete. Yes - `web.open` extracted view | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl` | No | `curl` escalation; wrote `sc-1-url-context.html` to `/tmp`; 40 seconds |
| `GPT-5.2 High` | ~15,618 chars est. | ~3,901–3,904 | Indeterminate - `curl` DNS-blocked; `web.open` line view only | `— 简体\nL469:　＊ 中文 — 繁體\nL470:　＊ 日本語\nL471:　＊ 한국어` | `web.run`, `web.open`, `functions.exec_command`, `python3` | No | `curl` failed DNS; `web.open` line view only surface; wrote `PLACEHOLDER` 12-byte artifact; 6 minutes 19 seconds |
| `GPT-5.2 Extra High` | ~121,581 chars | ~30,395 | No - `curl` complete. Yes - `web.open` extracted view | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | No | `curl` DNS failure then escalation; `triple_backticks_count` confirmed 0; wrote `sc1_url_context.html` to `/tmp`; 3 minutes 24 seconds |
| `GPT-5.3-Codex Low` | ~15,618 chars est. | ~3,904 | Indeterminate - `curl` DNS-blocked; `web.open` line view only | `— 简体\nL469:　＊ 中文 — 繁體\nL470:　＊ 日本語\nL471:　＊ 한국어` | `web.run`, `web.open`, `functions.exec_command`, `curl` | No | `curl` DNS-blocked; `web.open` `L0–L478` confirmed; no artifacts written; 13 seconds |
| `GPT-5.3-Codex Medium` | ~121,826 chars | ~30,457 | No - `curl` complete. Yes - `web.open` 479-line parsed representation | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `cat` | No | `curl` escalation; wrote `sc1_url_context_response.txt` to `/tmp`; node verification; 1 minute 18 seconds |
| `GPT-5.3-Codex High` | ~121,826 chars | ~30,457 | No - `curl` complete. Yes - `web.open` 479-line parsed representation | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `cat`, `node` | No | `curl` escalation; wrote `sc1_url_context.html` to `/tmp`; 479-line web.open confirmed; 33 seconds |
| `GPT-5.3-Codex Extra High` | ~121,577 chars | ~30,400 | No - `curl` complete. Yes - `web.open` response_length short stops at `L362`; long reaches L478 | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `od` | No | first run to report `response_length` short vs long distinction; no artifacts written; 2 minutes 11 seconds |
| `GPT-5.4-Mini Low` | ~26,900 chars est. | ~6,700 | Partially - `web.open` first view line-limited; second fetch covered remainder | `＊ 中文 — 繁體 L477:　＊ 日本語\nL478:　＊ 한국어` | `web.run`, `web.open`, `functions.exec_command`, `curl` | No | `curl` DNS-blocked; two-fetch sequence confirmed; `turn1view1` observed; no artifacts written; 17 seconds |
| `GPT-5.4-Mini Medium` | ~20,000 chars est. | ~5,000 | Indeterminate - `curl` and Node fetch DNS-blocked; `web.open` 479-line surface only | `— 简体\nL476:　＊ 中文 — 繁體\nL477:　＊ 日本語\nL478:　＊ 한국어` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `node` | No | Node REPL fetch failed; `web.open` used twice; no artifacts written; 1 minute 2 seconds |
| `GPT-5.4-Mini High` | ~33,000 chars est. | ~8,000–8,500 | Partially - `web.open` first view paginated at `L362`; follow-up recovered through footer | `＊ ภาษาไทย\n ＊ 中文 — 简体\n ＊ 中文 — 繁體\n ＊ 日本語\n ＊ 한국어` | `web.run`, `web.open`, `functions.exec_command`, `curl` | No | `curl` DNS-blocked; `turn0view0` + `turn1view1` + `turn2view0` observed; no artifacts written; 1 minute 41 seconds |
| `GPT-5.4-Mini Extra High` | ~7,698 chars | ~1,925 | Yes - `web.open` stopped at `L362`; second `web.open` around `L360` exposed remainder; browser path used | `ates.\n\nLast updated 2026-05-18 UTC.\n\nTerms\nPrivacy` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `tab.goto`, `tab.playwright.evaluate` | No | browser plugin invoked; playwright used; fetch failed; `curl` DNS-blocked; no artifacts written; 3 minutes 30 seconds |
| `GPT-5.4 Low` | ~18,000–20,000 chars est. | ~4,500–5,000 | Indeterminate - `web.open` 479 lines; no `curl` invoked | `L478:　＊ 한국어` | `web.run`, `web.open` | No | `curl` not invoked; most explicit surface-characterization language in batch; no artifacts written; 14 seconds |
| `GPT-5.4 Medium` | ~121,581 chars | ~30,400–32,860 | No - `curl` complete. Yes - `web.open` paginated/excerpted view | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3` | No | `truncated_marker: True` flag unexplained; possible contamination from shared filename with `GPT-5.3-Codex Medium`; wrote `sc1_url_context.html` to `/tmp`; 55 seconds |
| `GPT-5.4 High` | ~121,413 chars | ~30,350 | No - `curl` complete. Yes - `web.open` stopped at `L362`; second open reached `L478` | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `file`, `node`, `mcp__node_repl__.js` | No | `wc -c` vs `wc -m` distinction noted; wrote `sc1-url-context.html` to `/tmp`; 1 minute 49 seconds |
| `GPT-5.4 Extra High` | ~121,654 chars | ~30,400 | No - `curl` complete. Yes - `web.open` first response stopped at `L362` while reporting `Total lines: 479` | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `printf` | No | `printf` debug confirmed `L362` lands on page-content `omitted-for-brevity` notice; no artifacts written; 3 minutes 10 seconds |
| `GPT-5.5 Low` | ~121,413 chars | ~30,000 | No - `curl` complete. Yes - `web.open` Markdown-like extracted view | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | No | `wc -w` 6,133 words noted; no artifacts written; 40 seconds |
| `GPT-5.5 Medium` | ~121,409 chars | ~30,353 | No - `curl` complete. Yes - `web.open` rendered text view 479 lines | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `file`, `node` | No | multi_tool_use.parallel first observed in `SC-1` batch; lowest context window in batch at 8 percent; wrote `url-context.html` to `/tmp`; 1 minute 12 seconds |
| `GPT-5.5 High` | ~121,409 chars | ~30,350 | No - `curl` complete. Yes - `web.open` rendered/extracted view 479 lines | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `file`, `rg` | No | `rg` structural tag search confirmed pre count 8 and code count 13; first `H3`-relevant instrumentation in batch; wrote `gemini_url_context.html` to `/tmp`; 1 minute 3 seconds |
| `GPT-5.5 Extra High` | ~121,409 chars | ~30,350 | No - `curl` complete. Yes - `web.open` extracted HTML/text view 479 lines | `nnounce></devsite-a11y-announce>\n  </body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `perl`, `grep` | No | `perl` one-liner confirmed 0 triple-backtick fences; `wc -w` 6,133 consistent with `GPT-5.5 Low`; wrote `sc-1-url-context.html` to `/tmp`; 1 minute 43 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported via the `curl` path. Successful `curl` fetches returned approximately 121,400–121,826 chars consistently across all runs with DNS access, well above
any 10–100 KB ceiling threshold. The `GPT-5.2 High` run retrieved approximately 15,618 chars due to DNS failure forcing reliance on the `web.open` line view only,
which is a network access constraint rather than a character ceiling. Runs relying solely on `web.open` returned approximately 18,000–33,000 chars depending on
whether one or two view calls made, consistent with a fixed line-count viewport rather than a character ceiling.

**Combined verdict: `H1` no for the `curl` path on valid fetches. Partially consistent with the `web.open` path where the window is line-count-bound at 479 lines
rather than character-bound. The `GPT-5.2 High` reduced result flagged as a DNS access artifact, not a truncation ceiling.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Successful `curl` fetches returned approximately 30,350–30,457 tokens consistently, well above the 2,000-token threshold. `web.open`-only runs ranged
from approximately 1,925–8,500 tokens depending on retrieval surface and number of view calls. No run approached or hit a 2,000-token ceiling on either retrieval path.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported as a confirmed mechanism. The `web.open` tool consistently surfaces a 479-line rendered text extraction of this URL. The `L362` first-view threshold confirmed
across multiple runs as a short-mode ceiling, with content beyond that line recovered via a second `open` call. No run observed truncation falling on a Markdown structural
boundary. `GPT-5.3-Codex Extra High` confirmed `triple_backticks_count: 0` on the raw HTML artifact, and `GPT-5.5 High` confirmed balanced `<pre>` and `<code>` tag counts via
`rg`. `GPT-5.5 Extra High` confirmed 0 triple-backtick fences via `perl`. The target URL serves HTML, not Markdown, so fenced code block boundary behavior isn't applicable to
the raw fetch. The `web.open` extraction renders a Markdown-like view with indented code samples rather than fenced blocks, meaning no fence closure behavior is testable on
this surface either.

**Combined verdict: `H3` indeterminate. No truncation event produced a boundary to evaluate against on the `curl` path. The `web.open` `L362` short-mode ceiling is a line-count
threshold confirmed as landing on a page-content notice rather than a Markdown structural boundary. Structural completeness confirmed via tag-balance checks across multiple runs.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively. Within the Codex IDE surface, a consistent two-tier network access pattern confirmed
across all runs: sandboxed DNS resolution failure on the first `curl` attempt followed by escalated success after permission approval. This infrastructure constraint applied uniformly
regardless of LLM version or intelligence level.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval infrastructure behavior confirmed consistent across all 20 runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported, with meaningful variation by LLM version and intelligence level. No run executed proactive chunking before encountering a truncation or incompleteness signal. Most
runs used `web.open` as the first retrieval step and escalated to `curl` upon recognizing the result was an extraction rather than a raw response. `GPT-5.4-Mini Low` used a two-fetch
`web.open` sequence where the second call explicitly recovered lines beyond `L362`, representing the clearest reactive pagination in the batch. `GPT-5.4-Mini Extra High` added a browser
path fallback via `playwright` after `curl` was DNS-blocked. `GPT-5.2 High` and `GPT-5.3-Codex Low` didn't escalate beyond `web.open`. No run used chunked or paginated `curl` requests
against the target URL.

**Combined verdict: `H5` partially supported. Reactive second `web.open` calls to recover beyond the `L362` short-mode threshold observed across multiple runs. True proactive auto-pagination
not observed. Escalation from `web.open` to `curl` is the dominant retrieval strategy from `GPT-5.2` through `GPT-5.5` at Medium intelligence level and above.**

---

## Emergent Findings

1. **`web.open` 479-line ceiling is consistent across all LLM versions and intelligence levels for this URL.** Every run that used `web.open` received
a 479-line rendered text extraction regardless of LLM version or intelligence level. This is a platform-level constraint on the `web.open` tool for
this page, not a LLM behavior.

2. **`web.open` imposes a two-tier line threshold.** A short-mode first view stops at approximately `L362`. A second `open` call with `lineno` offset
or long-mode recovers through `L478`. `GPT-5.3-Codex Extra High` was the first run to explicitly name this as a `response_length` short versus long
parameter distinction, unique across 145 or more tests at time of observation. Subsequent runs confirmed the `L362` threshold behaviorally without
naming it.

3. **`curl` is the reliable full-document retrieval path.** Runs using `curl` with escalated network access consistently returned approximately
121,400–121,826 chars. Runs relying solely on `web.open` never exceeded approximately 33,000 chars estimated. The decision to use `curl` was the
single strongest predictor of retrieval completeness regardless of LLM version or intelligence level.

4. **`web.open` returns a Markdown-like rendered extraction, not raw HTML and not raw Markdown.** `GPT-5.5 Low` provided the clearest characterization
in the batch: the tool produces a rendered text view with headings, links, bullets, and indented code examples. `GPT-5.5 Medium` and subsequent runs
confirmed this as a third surface type distinct from raw HTML and raw Markdown. Code samples appear as indented blocks rather than triple-backtick fences.

5. **`GPT-5.2 High` is the sole run where `curl` was DNS-blocked and no escalation succeeded.** This run worked exclusively from the `web.open` line view,
returned approximately 15,618 chars, wrote a 12-byte `PLACEHOLDER` artifact, and ran for 6 minutes 19 seconds. The disproportionate run time reflects the
failed `curl` retry loop. This run is anomalous within the batch; don't use as a retrieval ceiling data point.

6. **Agents consistently failed to classify `web.open` extraction as truncation by design.** No agent explicitly described the `web.open` line view as
truncation in its final report. Agents instead described it as an extracted view, a rendered representation, or a line-numbered surface, and reasoned
toward `curl` as a separate measurement path. The distinction between surface-imposed extraction and agent-imposed truncation wasn't made by any run.

7. **Artifact production was lower in `SC-1` than in `BL-3`.** Approximately 6 unique HTML files and 1 text file written across all 20 runs, all to `/tmp`.
No run wrote to `Documents/Codex`. No run produced a headers file for server response inspection. Artifact naming was less consistent than in `BL-3` with
several runs reusing filenames across sessions, creating contamination risk.

8. **`multi_tool_use.parallel` appears in `GPT-5.5 Medium`, `High`, and `Extra High` runs.** This parallel tool invocation pattern wasn't observed in
`GPT-5.2` or `GPT-5.3-Codex` runs and appears consistent with `GPT-5.5` across intelligence levels, mirroring the `BL-3` finding.

9. **`wc -w` word count of 6,133 is consistent across `GPT-5.5 Low` and `GPT-5.5 Extra High`.** This cross-run consistency on a non-standard metric provides
an integrity signal that the same document version retrieved in both runs.

10. **Higher intelligence levels produced more thorough structural verification.** `GPT-5.2 Extra High` checked `triple_backticks_count`. `GPT-5.4 Extra High`
used `printf` debugging to inspect the `L362` boundary content. `GPT-5.5 High` used `rg` for tag-balance checks. `GPT-5.5 Extra High` used `perl` one-liners
for fence counting. This depth of verification didn't affect retrieved payload size, but is relevant to metacognitive accuracy assessment.

11. **Intelligence level doesn't reliably predict retrieval quality within an LLM version.** `GPT-5.3-Codex Low` ran for 13 seconds and relied entirely on
`web.open` without escalating. `GPT-5.3-Codex Extra High` produced the most architecturally significant finding in the batch. `GPT-5.4-Mini` runs showed reactive
two-fetch behavior at `Low` but browser fallback at `Extra High`. The most consequential behavioral differences are LLM-version-level, not intelligence-level.

12. **The `GPT-5.4 Medium` run produced an unexplained `truncated_marker: True` flag in `python3` output** that contradicted the agent's own truncation assessment.
This run also shares a filename with prior runs, creating contamination risk. Flag's unresolved; don't use as truncation evidence without follow-up investigation.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.2 Low` | Pass | `PASS - urllib_120KB_complete + web_open_extracted_view + python3_no_curl + 1m42s` |
| `GPT-5.2 Medium` | Pass | `PASS - curl_120KB_complete + web_open_extracted_view + 40s + CONTAM_RISK: sc-1-url-context.html_shared_name` |
| `GPT-5.2 High` | Partial | `PARTIAL - curl_DNS_blocked + web_open_line_view_only + 15KB_surface_only + PLACEHOLDER_artifact + 6m19s` |
| `GPT-5.2 Extra High` | Pass | `PASS - curl_120KB_complete + triple_backticks_count_0 + web_open_extracted_view + 3m24s + CONTAM_RISK: sc1_url_context.html_shared_name` |
| `GPT-5.3-Codex Low` | Pass | `PASS - curl_120KB_complete + web_open_479_line_ceiling + curl_escalation + 13s` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_120KB_complete + web_open_479_line_ceiling + node_verification + 1m18s` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_120KB_complete + web_open_479_line_ceiling + response_length_short_long_distinction + 2m11s` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_120KB_complete + response_length_short_L362_long_L478_named + unique_architectural_finding + 33s` |
| `GPT-5.4-Mini Low` | Partial | `PARTIAL - curl_DNS_blocked + web_open_two_fetch_sequence + turn1view1_observed + reactive_pagination + 17s` |
| `GPT-5.4-Mini Medium` | Partial | `PARTIAL - curl_DNS_blocked + Node_fetch_failed + web_open_479_surface_only + 1m2s` |
| `GPT-5.4-Mini High` | Partial | `PARTIAL - curl_DNS_blocked + web_open_L362_paginated + follow_up_open_recovered_footer + 1m41s` |
| `GPT-5.4-Mini Extra High` | Partial | `PARTIAL - curl_DNS_blocked + browser_playwright_fallback + web_open_L362_ceiling + 7698_browser_rendered_chars + 3m30s` |
| `GPT-5.4 Low` | Partial | `PARTIAL - curl_not_invoked + web_open_479_lines + strongest_surface_characterization_language + 14s` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_120KB_complete + truncated_marker_True_unexplained + web_open_paginated_view + 55s + CONTAM_RISK: sc1_url_context.html_shared_name` |
| `GPT-5.4 High` | Pass | `PASS - curl_120KB_complete + web_open_L362_L478_dual_path_comparison + mcp__node_repl__js_named + 1m49s + CONTAM_RISK: sc1-url-context.html_shared_name` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_120KB_complete + L362_omitted_for_brevity_printf_confirmed + Total_lines_479_delivered_L362_contradiction_named + 3m10s` |
| `GPT-5.5 Low` | Pass | `PASS - curl_120KB_complete + web_open_Markdown_like_extraction_described + wc_w_6133 + 40s` |
| `GPT-5.5 Medium` | Pass | `PASS - curl_120KB_complete + multi_tool_use_parallel_first_SC1 + 8pct_context + node_verification + 1m12s + CONTAM_RISK: url-context.html_shared_name` |
| `GPT-5.5 High` | Pass | `PASS - curl_120KB_complete + rg_tag_balance_H3_instrumentation + pre_count_8_code_count_13 + 1m3s + CONTAM_RISK: gemini_url_context.html_shared_name` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_120KB_complete + perl_fence_count_0 + wc_w_6133_consistent + multi_tool_use_parallel + 1m43s + CONTAM_RISK: sc-1-url-context.html_shared_name` |
