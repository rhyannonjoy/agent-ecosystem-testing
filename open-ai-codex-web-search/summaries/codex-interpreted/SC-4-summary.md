# SC-4 Summary

## Test Conditions

|                 | **SC-4** |
| --------------- | ------------------------------------------------------------------------------------------------ |
| URL             | `https://www.markdownguide.org/basic-syntax/`                                                    |
| Expected size   | ~30 KB assumed; actual ~64,527 chars / 64,659 bytes / ~16,100 tokens via valid fetch             |
| Surface         | Codex IDE                                                                                        |
| Workspace       | Session-scoped sandbox; `/private/tmp` cleared between sessions; `Documents/Codex` persistent    |
| Track           | `T1` GPT-interpreted, Codex IDE                                                                  |
| Method          | GPT-interpreted                                                                                  |
| Runs            | 20                                                                                               |
| Chunks returned | N/A, interpreted track                                                                           |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | indeterminate | indeterminate | Partially - `web.run` viewer reports `Total lines: 752`; content ends mid-article in Reference-style Links section | `the rendered output would be identical:` | `web.run`, `web.open` | No | no `curl`; `wordlim: 200` visible; no artifacts written; 21 seconds |
| `GPT-5.2 Medium` | ~64,527 chars | ~16,132 | No - `curl` complete. Yes - `web.open` capped at `wordlim: 200` | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc` | Yes | `curl` escalation; wrote `sc4_markdownguide_basic_syntax.html` to `/private/tmp` and `sc4_headers.txt` to `/private/tmp`; 1 minute 13 seconds |
| `GPT-5.2 High` | ~64,527 chars | ~16,132 | No - `curl` complete. Yes - `web.open` paged per call | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `python3` | No | no `curl`; used `python3` exclusively; 8 web searches; no artifacts written; 2 minutes 25 seconds |
| `GPT-5.2 Extra High` | ~64,527 chars | ~16,131–18,437 | No - `curl` complete. Yes - `web.open` windowed at `L316` and `L657` per call | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `python3` | No | `curl` escalation; `tokens_est_3_7chars` heuristic used alongside `chars/4`; no artifacts written; 5 minutes 9 seconds |
| `GPT-5.3-Codex Low` | indeterminate | indeterminate | No - `curl` complete. Yes - `web.open` line-indexed view only | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | No | `curl` escalation; never invoked `web`/`web.open` at all; used `multi_tool_use.parallel`; no artifacts written; 22 seconds |
| `GPT-5.3-Codex Medium` | ~64,527 chars | ~16,100 | No - `curl` complete. Yes - `web.open` stopped around `L316`; later windows showed other sections | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | Yes | `curl` escalation; wrote `sc4_markdownguide_basic_syntax.html` to `/private/tmp`; reasoned into jumping to end of document to pinpoint cutoff; 36 seconds |
| `GPT-5.3-Codex High` | ~64,527 chars | ~16,100 | No - `curl` complete. Yes - `web.open` cut around `L657` despite `Total lines: 752` | `markdownguide'\n  });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `sed`, `perl` | Yes | `curl` escalation; used `perl` alongside `sed` and `tail` for precise tail extraction; wrote `sc4_basic_syntax.html` to `/private/tmp`; 1 minute 49 seconds |
| `GPT-5.3-Codex Extra High` | ~64,528 chars | ~16,132–18,437 | No - `curl` complete. Yes - `web.open` windowed at `L316` and `L657` per call | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `node` | No | `curl` escalation; used `node -e` for token estimation; most precise single-payload cutoff characterization in collection; no artifacts written; 2 minutes 17 seconds |
| `GPT-5.4-Mini Low` | ~28,000–32,000 chars est. | ~7,000–8,000 | Indeterminate - `curl` returned 0 bytes; agent estimated from `web.open` only and believed content reached footer | `Made with  in .` | `web.open`, `curl` | No | `curl` failed silently; character estimate notably lower than confirmed 64,527; agent offered second pass but didn't attempt autonomously; no artifacts written; 20 seconds |
| `GPT-5.4-Mini Medium` | ~64,528 chars | ~16,132 | No - `curl` complete. Yes - `web.open` excerpt only | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `node_repl` | No | `curl` escalation; attempted `mcp__node_repl__.js` with `fetch`; only run across all models to attempt MCP-based fetch; no artifacts written; 1 minute 18 seconds |
| `GPT-5.4-Mini High` | ~64,528 chars | ~16,132 | No - `curl` and `web.open` both reported complete; `web.open` also reached footer | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `node` | No | no `curl`; used Node `fetch` exclusively; `web.open` uniquely also reported reaching footer rather than cutting mid-document; no artifacts written; 1 minute 38 seconds |
| `GPT-5.4-Mini Extra High` | ~32,974 chars visible-text / ~64,527 chars raw HTML | ~8,200 visible / ~16,000 raw | No - `curl` complete. Yes - `web.open` windowed; agent didn't recognize windowing as truncation by design | `project. CC BY-SA 4.0. Made with  in New Mexico.` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `node_repl`, `python3` | No | attempted Playwright, `xmllint`, `lynx`, `w3m`, `pup`, `htmlq`, tiktoken via node and python before settling on `curl`; stripped scripts to measure visible text at 32,974 chars; most ambitious tool exploration of any run; thought/output discrepancies noted; no artifacts written; 5 minutes 5 seconds |
| `GPT-5.4 Low` | ~64,659 chars | ~16,000–16,500 | No - `curl` complete. Yes - `web.open` partial by design though reached footer | `markdownguide'\n  });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `perl` | No | `curl` escalation; used `perl` for tail measurement; only run to explicitly reason about ~30 KB versus ~64.7 KB size discrepancy attributing it to HTML markup overhead; uniquely verbose and repetitive report style; no artifacts written; 1 minute 9 seconds |
| `GPT-5.4 Medium` | ~64,527 chars | ~16,000 | No - `curl` complete. Yes - `web.open` clipped at `L316` first call; tail accessible through `L751` on later calls | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `file` | No | `curl` escalation; ran `file` command on saved HTML; clearest explicit recognition that `web.open` is pageable across multiple calls rather than simply truncated; no artifacts written; 1 minute 22 seconds |
| `GPT-5.4 High` | ~64,528 chars | ~16,132 | No - `curl` complete. Yes - `web.open` cut at `L316`; later view skipped intervening lines | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `node` | Yes | `curl` escalation; used `node -e` and `curl`/`tail` for verification; characterized `web.open` as extracted/abridged view rather than full page content; wrote `sc4_markdown_basic_syntax.html` to `/private/tmp`; 1 minute 10 seconds |
| `GPT-5.4 Extra High` | ~64,527 chars | ~16,100 | No - `curl` complete. Yes - `web.open` single payload stopped at `L657`; remainder reachable via additional paged calls | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `python3` | Yes | `curl` escalation; most precise single-payload cutoff characterization identifying `L657` of 752 total lines; unprompted offer to format results as CSV or JSON; wrote `sc4_markdown_guide.html` to `/private/tmp`; desktop app refresh observed mid-run with commands disappearing; 2 minutes 46 seconds |
| `GPT-5.5 Low` | ~64,527 chars | ~16,100 | Indeterminate - bypassed `web` pipeline entirely; no `web.open` surface data | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `file` | Yes | only run in entire collection to never invoke `web`/`web.open`; used `multi_tool_use.parallel` and shell commands exclusively; wrote `sc4_basic_syntax.html` to `/private/tmp`; 0 web searches; 23 seconds |
| `GPT-5.5 Medium` | ~64,527 chars | ~16,100 | No - `curl` complete. Yes - `web.open` initially showed through `L657`; second call retrieved through `L751` | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `rg` | Yes | `curl` escalation; used `rg` to verify `<pre>` count 24/24 and `<code>` count 169/169; most rigorous Markdown formatting integrity check of any run; wrote `markdown-basic-syntax.html` to workspace root; 57 seconds |
| `GPT-5.5 High` | ~64,527 chars | ~16,100 | No - `curl` complete. Yes - `web.open` extraction visibly partial stopping around `L657`; follow-up showed through `L751` | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `grep` | No | `curl` escalation; used `wc -w` word count alongside `wc -m` and `grep -n` for `</html>` verification; combined multiple measurements into single compound shell command; no artifacts written; 52 seconds |
| `GPT-5.5 Extra High` | ~64,527 chars | ~16,100 | No - `curl` complete. Yes - `web.open` windowed; `curl` fetch ends with newline after `</html>` | `markdownguide' });\n</script>\n\n  </body>\n</html>\n` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `file`, `rg`, `perl` | Yes | `curl` escalation; used `perl -CS -Mutf8` for UTF-8 aware tail verification; most precise document-end characterization in entire SC-4 collection; wrote `SC-4-basic-syntax.html` to `Documents/Codex`; 1 minute 59 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported via the `curl` path. Successful `curl` fetches returned approximately 64,527 chars consistently across all runs with DNS access, well within the
10–100 KB range but with no ceiling hit. Runs relying solely on `web.open` returned lower estimates, most notably `GPT-5.4-Mini Low` which estimated 28,000–32,000
chars from `web.open` output alone, roughly half the confirmed full-document size, consistent with a display ceiling operating below the agent's awareness threshold.
`GPT-5.4-Mini Extra High` stripped scripts and measured visible text at 32,974 chars, closely matching the `~30 KB` expectation the agent cited, suggesting the
`web.open` surface delivers a condensed readable rendering rather than the raw HTML body.

**Combined verdict: `H1` indeterminate for the `curl` path where the ceiling was never hit. Partially consistent with the `web.open` path where viewer output is
consistently lower than the confirmed raw fetch size. `GPT-5.4-Mini Low` is the strongest `H1` signal in the set.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Successful `curl` fetches returned approximately 16,100–16,132 tokens consistently, well above the 2,000-token threshold. `web.open`-only runs
returned lower estimates but these reflect the viewer window rather than a token-based cutoff mechanism. No run produced a retrieval that approached a 2,000-token
ceiling via either path.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported. The `web.open` tool consistently truncated at line-count positions rather than Markdown structural boundaries. Cutoff points of `L316` and `L657`
observed across multiple runs, both landing mid-document at non-structural positions. `wordlim: 200` was visible in `GPT-5.2 Low` tool output. The `web.open` surface
delivers a line-indexed extraction with a variable word-count window rather than any structure-aware mechanism.

**Combined verdict: `H3` no. Truncation is line-count and word-count driven, consistently landing at non-structural boundaries.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively. Within the Codex IDE surface, a consistent two-tier network access pattern
confirmed across most runs: sandboxed DNS resolution failure on the first `curl` attempt followed by escalated success after permission approval.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval infrastructure behavior confirmed consistent across all 20 runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported, with meaningful variation by LLM version and intelligence level. No run executed proactive chunking before encountering a truncation signal.
The dominant pattern across nearly all runs was: invoke `web`, recognize viewer limits, escalate to `curl` for precise measurement. `GPT-5.4 Medium` produced the
clearest explicit recognition that `web.open` is pageable across multiple calls. `GPT-5.5 Extra High` used `perl -CS -Mutf8` for the most precise document-end
verification. `GPT-5.5 Low` uniquely bypassed `web` entirely. `GPT-5.4-Mini Extra High` attempted the broadest tool exploration of any run before settling on `curl`.
Runs using `curl` successfully typically didn't paginate `web.open` further, treating the direct fetch as authoritative.

**Combined verdict: `H5` partially supported. Reactive escalation from `web.open` to `curl` is the dominant retrieval strategy from `GPT-5.2` through `GPT-5.5` at
`Medium` intelligence level and above. True proactive auto-pagination not observed.**

---

## Emergent Findings

1. **`web.open` imposes a variable line-count window, not a fixed ceiling.** Cutoff points of `L316` and `L657` observed across 20 runs. `wordlim: 200` appeared
explicitly in `GPT-5.2 Low` tool output. The window is soft rather than a single fixed limit, and the `web.open` surface consistently delivers a condensed
readable rendering rather than raw HTML.

2. **`curl` is the reliable full-document retrieval path.** Runs using `curl` with escalated network access consistently returned approximately 64,527 chars.
The decision to escalate to `curl` was the single strongest predictor of retrieval completeness regardless of LLM version or intelligence level, mirroring the
`SC-3` finding.

3. **Artifact production notably lower than `SC-3`, with 9 artifacts written across 20 runs.** 7 artifacts saved to `/private/tmp` and 2 to `Documents/Codex`.
Agents frequently created workspace infrastructure such as session directories and then wrote no artifacts to them, suggesting the document's relatively small size
reduced perceived need for persistent reference storage compared to the `SC-3` Wikipedia table.

4. **Dominant behavioral pattern is use `web`, recognize limits, escalate to `curl`.** This sequence appeared across nearly all runs from `GPT-5.2 Medium`
through `GPT-5.5 Extra High`. Exceptions include `GPT-5.5 Low` which bypassed `web` entirely, `GPT-5.2 High` which used `python3` instead of `curl`, and
`GPT-5.4-Mini Low` which had `curl` return 0 bytes and estimated from `web.open` output alone.

5. **`GPT-5.4-Mini Extra High` attempted the broadest tool exploration in the collection.** Playwright, `xmllint`, `lynx`, `w3m`, `pup`, `htmlq`, `tiktoken` via
both Node and Python were all attempted and failed before the agent settled on `curl`. Thought panel reasoning and visible output showed notable discrepancies,
unique in the `SC-4` set.

6. **`GPT-5.4-Mini Low` produced the most ambiguous truncation assessment in the set.** With `curl` returning 0 bytes, the agent estimated 28,000–32,000 chars
from `web.open` output and believed content reached the footer, roughly half the confirmed document size. The false-complete signal is the clearest `H1`-adjacent
finding in SC-4.

7. **`GPT-5.5` introduced novel measurement tools not seen in prior LLM versions.** `rg` appeared in `GPT-5.5 Medium`, `perl -CS -Mutf8` in `GPT-5.5 Extra High`,
and `wc -w` word count in `GPT-5.5 High`. This broader scripting tool repertoire is consistent with the `SC-3` findings for the same LLM version.

8. **`multi_tool_use.parallel` appears in `GPT-5.5 Low`, `GPT-5.5 Medium`, and `GPT-5.5 Extra High`.** This parallel tool invocation pattern not observed in
`GPT-5.2` or `GPT-5.3-Codex` runs and appears consistent with `GPT-5.5` across intelligence levels, consistent with `SC-3` findings.

9. **`GPT-5.5 Medium` is the only run to perform structural tag-balance verification.** Searching for `<pre>` count 24/24 and `<code>` count 169/169 via `rg`
represents a qualitatively different completeness check than tail inspection or byte counting, and not observed in any other run across the `SC-4` cycle.

10. **`GPT-5.5 Low` only run to never invoke `web` or `web.open`.** By bypassing the retrieval surface entirely and going directly
to `curl` via `multi_tool_use.parallel`, this run produced no viewer truncation data at all, making `H3` indeterminate for that run specifically.

11. **`L316` versus `L657` cutoff split may reflect a two-stage window structure within `web.open`.** `L316` appeared as a first-call cutoff in several runs,
with subsequent calls reaching `L657` before requiring additional pagination. This suggests the viewer may page in fixed increments rather than delivering a
single variable window, though the pattern not consistent enough across all runs to confirm.

12. **Intelligence level doesn't reliably predict retrieval quality within LLM version.** `GPT-5.5 Low` produced one of the most efficient retrieval sequences in
the set. `GPT-5.4-Mini Extra High` produced the most complex tool exploration while `GPT-5.4-Mini Low` produced the weakest assessment. The most consequential
behavioral differences are LLM-version-level, not intelligence-level, consistent with `SC-3` results.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.2 Low` | Partial | `PARTIAL - web_run_only + wordlim_200_visible + mid_article_truncation + indeterminate_counts + no_artifacts + 21s` |
| `GPT-5.2 Medium` | Pass | `PASS - curl_64KB_complete + web_open_wordlim_capped + sc4_html_artifact + sc4_headers_txt + private_tmp + 1m13s` |
| `GPT-5.2 High` | Pass | `PASS - curl_64KB_complete + python3_only + no_curl + web_open_paged + 8_web_searches + no_artifacts + 2m25s` |
| `GPT-5.2 Extra High` | Pass | `PASS - curl_64KB_complete + web_open_L316_L657_windowed + dual_token_heuristic + no_artifacts + 5m9s` |
| `GPT-5.3-Codex Low` | Pass | `PASS - curl_64KB_complete + web_bypassed_entirely + multi_tool_use_parallel + no_web_open + no_artifacts + 22s` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_64KB_complete + web_open_L316_excerpt + end_jump_reasoning + sc4_html_artifact + private_tmp + 36s` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_64KB_complete + web_open_L657_windowed + perl_sed_tail_extraction + sc4_html_artifact + private_tmp + 1m49s` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_64KB_complete + web_open_L316_L657_windowed + node_token_estimation + L657_cutoff_identified + no_artifacts + 2m17s` |
| `GPT-5.4-Mini Low` | Partial | `PARTIAL - curl_0_bytes + web_open_28_32KB_est + footer_believed_reached + false_complete_signal + no_artifacts + 20s` |
| `GPT-5.4-Mini Medium` | Pass | `PASS - curl_64KB_complete + web_open_excerpt + mcp_node_repl_fetch_attempted + no_artifacts + 1m18s` |
| `GPT-5.4-Mini High` | Pass | `PASS - node_fetch_64KB_complete + web_open_footer_reached + no_curl + no_artifacts + 1m38s` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - curl_64KB_complete + script_strip_32974_visible + playwright_xmllint_pup_all_failed + thought_output_discrepancy + no_artifacts + 5m5s` |
| `GPT-5.4 Low` | Pass | `PASS - curl_64KB_complete + web_open_partial + perl_tail + 30KB_vs_64KB_reasoning + verbose_report + no_artifacts + 1m9s` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_64KB_complete + web_open_L316_L751_pageable + file_command + clearest_pageable_characterization + no_artifacts + 1m22s` |
| `GPT-5.4 High` | Pass | `PASS - curl_64KB_complete + web_open_L316_abridged + node_verification + sc4_html_artifact + private_tmp + 1m10s` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_64KB_complete + web_open_L657_of_752_identified + csv_json_offer_unprompted + sc4_html_artifact + private_tmp + app_refresh_observed + 2m46s` |
| `GPT-5.5 Low` | Pass | `PASS - curl_64KB_complete + web_never_invoked + multi_tool_use_parallel + sc4_html_artifact + private_tmp + 0_web_searches + 23s` |
| `GPT-5.5 Medium` | Pass | `PASS - curl_64KB_complete + web_open_L657_L751 + rg_tag_balance_verification + multi_tool_use_parallel + markdown_html_artifact + workspace_root + 57s` |
| `GPT-5.5 High` | Pass | `PASS - curl_64KB_complete + web_open_L657_L751 + wc_w_word_count + compound_shell_command + no_artifacts + 52s` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_64KB_complete + web_open_windowed + perl_utf8_tail + newline_after_html_noted + sc4_html_artifact + Documents_Codex + 1m59s` |
