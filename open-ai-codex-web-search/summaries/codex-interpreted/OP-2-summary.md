# OP-2 Summary

## Test Conditions

|                 | **OP-2**                                                                        |
| --------------- | ------------------------------------------------------------------------------- |
| URL             | `https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array` |
| Expected size   | ~120 KB assumed; actual ~240,370 chars / 240,508 bytes / ~60,000 tokens         |
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
| `GPT-5.2 Low` | 240,504 bytes / 240,366 chars | ~60,126 | No - curl complete. Yes - web.open wordlim:200 | `</div>\n</body>\n\n</html>` | `curl`, `wc`, `tail`, `Node REPL` | No | 3 web searches; wordlim:200 visible; 42 seconds |
| `GPT-5.2 Medium` | 240,504 bytes / 240,366 chars | ~60,092 | No - curl complete. Yes - web.open L317 | `</div>\n</body>\n\n</html>` | `web.run`, `curl`, `wc`, `tail` | No | false file ownership claim; web.open excerpts/sections noted; 53 seconds |
| `GPT-5.2 High` | 240,504 bytes / 240,366 chars | ~60,092-68,676 | No - curl complete. Yes - web.open L590 | `</div>\n</body>\n\n</html>` | `web.run`, `curl`, `wc`, `python3` | Yes `op2_mdn_array.html` | endswith_html/endswith_body checks; multi-denominator token estimation; 1m6s |
| `GPT-5.2 Extra High` | 240,504 bytes / 240,366 chars | ~60,092 | No - curl complete. Yes - web.open L317 lineno=null | `</div>\n</body>\n\n</html>` | `web.run`, `curl`, `wc`, `python3` | No | lineno parameter surfaced; 11 commands; 3m11s |
| `GPT-5.3-Codex Extra High` | 240,504 bytes / 240,366 chars | ~60,100 | No - curl complete. Yes - web.open L317-L590 | `</div>\n</body>\n\n</html>` | `web`, `web.open`, `curl`, `wc`, `tail`, `python3` | Yes `op2_mdn_array.html` | 6 web fetches observed vs 3 reported; implicit multi-fetch pagination signal; 2m39s |
| `GPT-5.3-Codex High` | 240,366 chars / 240,504 bytes | ~64,000 | No - curl complete. Yes - web.open excerpted | `">\n    </div>\n        </body>\n\n        </html>\n    "` | `web.open`, `curl`, `wc`, `tail`, `od`, `node` | No | od hex dump for lossless tail; 3 URL calls vs 1 reported; 1m16s |
| `GPT-5.3-Codex Medium` | 240,504 bytes | ~60,100 | No - curl complete. Yes - web.open L590 then lineno=1200 | `</div>\n</body>\n\n</html>` | `web.run`, `curl` | No | first confirmed explicit lineno=1200 offset; turn0view0/turn1view0; 31 seconds |
| `GPT-5.3-Codex Low` | 240,504 bytes / 240,366 chars | ~60,000 | No - curl complete. Yes - web.open L317 | `</div>\n</body>\n\n</html>` | `web`, `web.open`, `curl`, `wc`, `tail` | No | L317 of 1269 confirmed; 29 seconds |
| `GPT-5.4-Mini Low` | est. 100k-120k chars | ~25k-30k | No obvious truncation in web.open. curl returned 0 bytes | `ontent available under a Creative Commons license.` | `web.open`, `curl` | No | curl silently failed; web.open reached L1267-1268; agent may have missed truncation; 15 seconds |
| `GPT-5.4-Mini Medium` | 240,504 bytes / 240,366 chars | ~60,000 | No - curl complete. Yes - web.open L317 | `</div>\n</body>\n\n</html>` | `web.open`, `curl`, `wc`, `tail`, `python3` | Yes `mdn-array-XXXXXX.html` | L317 named as mid-article in Copying methods and mutating methods section; 49 seconds |
| `GPT-5.4-Mini High` | 240,504 bytes / 240,366 chars | ~60,000 | No - curl complete. Yes - web.open L317 | `'>\n    </div>\n        </body>\n\n        </html>\n    '` | `web.open`, `curl`, `python3` | No | self-corrected wc -c vs UTF-8 chars; no HTML file written; 1m44s |
| `GPT-5.4-Mini Extra High` | DOM 143,701 / rendered text 28,479 chars | ~36k DOM / ~7k text | No - browser complete. Yes - web.open paginated | `ontent available under a Creative Commons license.` | `web.open`, `browser`, `tab.goto`, `tab.playwright.evaluate` | No | first browser surface use; fetch unavailable in page scope; turn0view0/turn1view0 pagination; 2m58s |
| `GPT-5.4 Low` | 240,508 bytes / 240,366 chars | ~60,000-80,000 | No - curl complete. Yes - web.open L316 | `ozilla.org contributors. Content available under .` | `web`, `web.open`, `curl`, `Node REPL` | No | two truncation layers confirmed: web.open L316 and terminal token cap ~446 tokens; lineno=1180 offset; 57 seconds |
| `GPT-5.4 Medium` | 240,370 chars / 240,504 bytes | ~60,000 | No - curl complete. Yes - web.open L0-L317 then lineno=1210 | `</div>\n</body>\n\n</html>` | `web.open`, `curl`, `wc`, `tail`, `head` | Yes `op2_mdn_array_20260515.html` | turn0view0/turn1view0 pagination; 58 seconds |
| `GPT-5.4 High` | 240,508 bytes / 240,366 chars | ~60,100 | No - curl complete. Yes - web.open L317 then lineno offsets to L1268 | `">\n    </div>\n        </body>\n\n        </html>\n    "` | `web.open`, `curl`, `wc`, `tail`, `head`, `node` | Yes `op2_array.html`, `op2_headers.txt` | most pagination steps in set: turn0view0 through turn4view3; headers file saved; cache/last-modified confirmed; 2m54s |
| `GPT-5.4 Extra High` | 240,370 chars / 240,508 bytes | ~60,100 | No - curl complete. Yes - web.open L317 then L590 then lineno to L1268 | `array(s) are copied into the new array as follows:` web.open initial / `</div>\n</body>\n\n</html>` curl | `web.run`, `curl`, `wc`, `tail`, `file`, `node`, `rg` | Yes `mdn-array.html` | two-step window L317 then L590 before lineno offsets; wc -w word count; turn0view0 through turn4view0; 4m33s |
| `GPT-5.5 Low` | 240,370 chars / 240,508 bytes | ~60,093 | No - curl complete. web.open not used | `</div>\n</body>\n\n</html>` | `curl`, `wc`, `tail`, `rg`, `node`, `mcp__node_repl__` | Yes `mdn_array_op2.html`, `mdn_array_op2.headers` | web pipeline bypassed entirely; structured JSON output with fenceCount/htmlClose/bodyClose; headers saved; 1m20s |
| `GPT-5.5 Medium` | 240,370 chars / 240,508 bytes | ~60,000 | No - curl complete. Yes - web.open L590 | `</div>\n</body>\n\n</html>` | `web.run`, `curl`, `wc`, `tail`, `rg`, `node` | Yes `mdn-array.html` | pre 49/49 and code 473/473 balanced tag counts verified; rg backtick fence search failed zsh unmatched; 56 seconds |
| `GPT-5.5 High` | 240,370 chars | ~60,000 | No - curl complete. Yes - web.open L590 then lineno to L1268 | `</div>\n</body>\n\n</html>` | `web.run`, `curl`, `wc -m`, `tail`, `sed -n l` | No | --compressed flag; sed -n l for non-printable char display; trailing spaces confirmed; turn0view0/turn1view0; 1m29s |
| `GPT-5.5 Extra High` | 240,370 chars / 240,508 bytes | ~60,093 | No - curl complete. web.open reached footer without mid-article stop reported | `</div>\n</body>\n\n</html>` | `web.run`, `curl`, `wc`, `tail`, `file`, `node`, `rg`, `multi_tool_use.parallel` | Yes `mdn_array.html` | multi_tool_use.parallel for concurrent checks; curl -w http_code/size_download; rg backtick fence search failed zsh unmatched; 2m4s |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported via `curl` path. Successful `curl` fetches returned 240,370 chars consistently across all runs that used curl,
far above any 10-100 KB ceiling threshold. The ceiling hypothesis is only partially consistent with `web.open` results, where
visible chars in truncated runs reflect a fixed line window rather than a character ceiling. No run encountered a mid-content
character cut on the curl path. The one run where a ceiling appeared plausible was `GPT-5.4-Mini Low`, where curl silently
returned 0 bytes and the agent estimated 100k-120k chars from the web.open view alone, but this reflects a retrieval failure
rather than a platform ceiling.

**Combined verdict: `H1` no for `curl` path. Partially consistent with `web.open` path where the window is line-count-bound not character-bound.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Successful `curl` fetches returned ~60,000 tokens consistently, well above the 2,000-token threshold. `web.open`
windowed results ranged from a few thousand tokens on first-view captures to the full ~60,000 tokens when pagination was used.
No run approached or hit a 2,000-token ceiling on either path.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported as a mechanism. The `web.open` line window consistently terminates at approximately L317 on first fetch across
`GPT-5.2` through `GPT-5.4` runs, and at approximately L590 across `GPT-5.5` runs and some `GPT-5.4 Extra High` secondary calls.
Both cutpoints verified against the raw HTML: L317 in the rendered view corresponds to HTML line 2031, landing mid-sentence
in the `Array.prototype.fill` description inside the Copying methods and mutating methods section, confirmed by `GPT-5.4-Mini Medium`.
This isn't a structural boundary. The L590 cutpoint similarly falls mid-document without evidence of heading alignment. The
truncation mechanism is a fixed line-count window, not Markdown or heading awareness.

**Combined verdict: `H3` no. Truncation boundary is a fixed platform line window, not structure-aware.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively. VS Code-Codex extension comparison
wasn't performed. Within the Codex IDE surface, a meaningful tool-path split confirmed: `curl` returns ~240,370 chars of
complete raw HTML, `web.open` returns a windowed partial extraction capped at approximately L317 or L590 depending on model
version. The two-tier network access pattern, sandboxed DNS failure followed by escalated curl success, is consistent across all
model families and constitutes an infrastructure property of the surface.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval method impact confirmed across all 20 runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported, with meaningful variation across model families and a clear model-version correlation. `GPT-5.3-Codex Medium`
produced the first confirmed explicit `lineno=1200` offset call. `GPT-5.4 Low` and `GPT-5.4 Medium` used targeted `lineno` jumps
to near-end positions. `GPT-5.4 High` produced the most pagination steps in the dataset with turn0view0 through turn4view3. `GPT-5.4
Extra High` showed a two-step unprompted window progression from L317 to L590 before switching to lineno offsets. `GPT-5.5 Low`
bypassed `web.open` entirely in favor of `curl`, representing a retrieval strategy shift rather than pagination. No run executed
proactive chunking before encountering a truncation signal.

**Combined verdict: `H5` partially supported. Reactive pagination via `lineno` offsets observed consistently from `GPT-5.3-Codex Medium`
onward. Proactive auto-pagination not observed. Tool escape to `curl` is the dominant full-document retrieval strategy.**

---

## Emergent Findings

1. **The `web.open` line window is LLM-version-correlated.** L317 is the dominant first-fetch cutpoint across `GPT-5.2` through
`GPT-5.4` runs. L590 is the dominant first-fetch cutpoint across `GPT-5.5` runs and `GPT-5.4 Extra High` secondary calls. This
represents a measurable behavioral difference between model generations on the same surface and the same document.

2. **L317 in the rendered view doesn't correspond to L317 in raw HTML.** The `web.open` line numbering reflects a rendered
text extraction, not raw HTML lines. The text at rendered L317 corresponds to raw HTML line 2031. This distinction is critical
for interpreting all line-number references across runs.

3. **`curl` is the reliable full-document retrieval path.** Runs using `curl` consistently returned 240,370 chars and 240,508 bytes,
matching the HTTP `content-length` header confirmed in Run 15. Runs relying solely on `web.open` never retrieved the full document.
The decision to use `curl`, whether immediate or escalated after DNS failure, was the single strongest predictor of retrieval success.

4. **Two distinct truncation layers confirmed in a single run for the first time.** `GPT-5.4 Low` in Run 13 identified both
the `web.open` line window cap at L316 and a terminal token cap of approximately 446 tokens on `curl -I` output, showing that
truncation can occur at multiple independent layers simultaneously.

5. **Intelligence level doesn't reliably predict retrieval quality.** `GPT-5.5 Low` bypassed `web.open` entirely and retrieved
the full document in 1m20s using 9% context with the richest verification output in its family. `GPT-5.2 Extra High` consumed
22% context over 3m11s for the same result. `GPT-5.4-Mini Extra High` spent 2m58s on a browser-only path that returned a
fundamentally different document representation than all other runs.

6. **`GPT-5.5` shows a convergence toward `curl`-first behavior.** Three of four `GPT-5.5` runs either bypassed `web.open`
entirely or used it only for initial surface assessment before switching to `curl`. `GPT-5.5 Low` and `GPT-5.5 High` both
produced clean `curl`-only retrieval with no `web.open` invocation. This mirrors the pattern observed in `OP-1` for the same
LLM version group.

7. **The `GPT-5.4-Mini Extra High` run introduced a browser surface not seen in any other run.** The in-app Playwright browser
returned a DOM-serialized HTML representation of 143,701 chars and rendered text of 28,479 chars, neither matching the raw
HTTP payload of 240,370 chars. `fetch` was unavailable in page scope with `windowFetchType: undefined`. This constitutes a
third distinct retrieval representation alongside `curl` raw HTML and `web.open` rendered extraction.

8. **Agents consistently misreport truncation by conflating `curl` completeness with overall retrieval completeness.** Across
multiple runs, agents reported no truncation in summary point 3 while separately noting `web.open` truncation in point 7. The
`curl` fetch result treated as the authoritative completeness signal, masking the `web.open` window limitation in self-assessments.

9. **Workspace persistence creates contamination risk across runs.** Files written to `/private/tmp` from earlier runs remained
accessible to later runs. Multiple agents read or overwrote files named `op2_mdn_array.html` or `op2_array.html` without
confirming whether the file was from the current session. The `codex-browser-use` directory initialized by most runs but
produced no usable content.

10. **The `GPT-5.4 High` run is the most methodologically complete in the dataset.** It saved HTTP headers to a separate file,
cross-verified `content-length` against `wc -c`, used `od` hex dump for lossless tail verification, produced the most pagination
steps of any run, and identified cache age and `last-modified` timestamp as sources of potential cross-run variation.

---

## Log Label Summary

| Agent | Result | Label |
| --------------- | ------- | --------------------------- |
| `GPT-5.2 Low` | Pass | `PASS - curl_complete + wordlim_200_visible + 3_web_searches` |
| `GPT-5.2 Medium` | Pass | `PASS - curl_complete + web_open_L317 + false_file_ownership_noted` |
| `GPT-5.2 High` | Pass | `PASS - curl_complete + endswith_checks + multi_denominator_token_est` |
| `GPT-5.2 Extra High` | Pass | `PASS - curl_complete + lineno_parameter_surfaced + 11_commands` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_complete + implicit_multi_fetch_pagination + 6_url_calls_vs_3_reported` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_complete + od_hex_tail + 3_url_calls_vs_1_reported` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_complete + first_confirmed_lineno_1200_offset + 31s` |
| `GPT-5.3-Codex Low` | Pass | `PASS - curl_complete + web_open_L317 + 29s` |
| `GPT-5.4-Mini Low` | Partial | `PARTIAL - curl_0bytes_silent_fail + web_open_only + agent_missed_truncation` |
| `GPT-5.4-Mini Medium` | Pass | `PASS - curl_complete + L317_named_section_boundary + mktemp_filename` |
| `GPT-5.4-Mini High` | Pass | `PASS - curl_complete + self_corrected_bytes_vs_chars + no_html_file_written` |
| `GPT-5.4-Mini Extra High` | Partial | `PARTIAL - browser_surface_only + DOM_143k_vs_raw_240k + fetch_unavailable` |
| `GPT-5.4 Low` | Pass | `PASS - curl_complete + two_truncation_layers_confirmed + lineno_1180_offset` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_complete + lineno_1210_offset + turn0view0_turn1view0` |
| `GPT-5.4 High` | Pass | `PASS - curl_complete + most_pagination_steps + headers_saved + cache_verified` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_complete + L317_L590_two_step_window + wc_word_count` |
| `GPT-5.5 Low` | Pass | `PASS - curl_only + web_open_bypassed + structured_JSON_output + headers_saved` |
| `GPT-5.5 Medium` | Pass | `PASS - curl_complete + web_open_L590 + balanced_tag_counts_verified` |
| `GPT-5.5 High` | Pass | `PASS - curl_complete + web_open_L590_then_lineno + sed_nonprintable_check` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_complete + parallel_tool_use + web_open_footer_reached` |
