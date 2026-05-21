# SC-3 Summary

## Test Conditions

|                 | **SC-3** |
| --------------- | ------------------------------------------------------------------------------------------------ |
| URL             | `https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population`                 |
| Expected size   | ~100 KB assumed; actual ~785,605 chars / 792,528 bytes / ~196,000–196,402 tokens via valid fetch |
| Surface         | Codex IDE                                                                                        |
| Workspace       | Session-scoped sandbox; `/private/tmp` cleared between sessions; `Documents/Codex` persistent    |
| Track           | `T1` GPT-interpreted, Codex IDE                                                                  |
| Method          | GPT-interpreted                                                                                  |
| Runs            | 21                                                                                               |
| Chunks returned | N/A, interpreted track                                                                           |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | ~18,000 chars est. | ~4,500 | Indeterminate - `web.run` snippets far below expected size; no `curl` | `ependencies by population\n122 languages\nAdd topic` | `web.run`, `web.open`, `node_repl` | No | no `curl`; two `web.run` fetches returned snippets from different page regions; no artifacts written; 24 seconds |
| `GPT-5.2 Medium` | ~785,605 chars | ~198,132 | No - `curl` complete. Yes - `web.open` excerpt stops mid-article around `L266` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | No | `curl` escalation; wrote `sc3.html` to `/private/tmp`; 2 minutes 11 seconds |
| `GPT-5.2 High` | ~785,605 chars | ~196,000–262,000 | No - `curl` complete. Yes - `web.open` stops mid-article around `L266` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | Yes | `curl` escalation x3; wrote `SC-3_wikipedia_List_of_countries_by_population.html` and `SC-3_wikipedia_List_of_countries_by_population_action_render.html` to `Documents/Codex`; near-identical dual artifact first observed; 2 minutes 18 seconds |
| `GPT-5.2 Extra High` | ~785,605 chars | ~196,401 | No - `curl` complete. Yes - `web.open` stops around `L266`; `lineno` jumps used | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | Yes | `curl` escalation x3; wrote `sc-3_wikipedia.html`, `sc-3_wikipedia_oldformat.html`, `sc-3_wikipedia_compressed.html` to `Documents/Codex`; triple near-identical artifact first observed; 20 web searches; 5 minutes 27 seconds |
| `GPT-5.3-Codex Low` | ~18,000 chars est. | indeterminate | Yes - first `web.run` fetch partial; second fetch at `lineno=1200` reached footer | `L1225` footer confirmed | `web.run`, `web.open` | No | no `curl`; two-fetch start-and-end sequence; page coverage confirmed architecturally without shell access; no artifacts written; 19 seconds |
| `GPT-5.3-Codex Medium` | ~785,605 chars | ~196,000 | No - `curl` complete. Yes - `web.open` excerpt clearly truncated/snippet-limited | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | Yes | `curl` escalation x1; wrote `sc3_wikipedia.html` to `Documents/Codex`; 37 seconds |
| `GPT-5.3-Codex High` | ~785,605 chars | ~200,000 | No - `curl` complete. Yes - `web.open` stops around `L353`; `lineno` jumps used | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | Yes | `curl` escalation x1; wrote `sc3_wiki.html` to `/private/tmp`; 4 web searches; 1 minute 36 seconds |
| `GPT-5.3-Codex Extra High` | ~785,605 chars | ~200,000 | No - `curl` complete. Yes - `web.open` stops around `L353`; `lineno` jumps used | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `web.search_query`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | Yes | `curl` escalation x3; wrote `sc3_wiki_response.html` to `Documents/Codex`; accidental `web.search_query` call; 8 web searches; 3 minutes 9 seconds |
| `GPT-5.4-Mini Low` | ~18,000 chars | ~4,500 | No - `web.open` excerpt believed complete by agent; agent did not recognize truncation by design | `dependencies by population\n122 languages\nAdd topic` | `web.run`, `web.open`, `curl` | No | `curl` returned 0 bytes; agent perceived excerpt as full page; no artifacts written; 23 seconds |
| `GPT-5.4-Mini Medium` | ~11,000 chars | ~2,700–3,000 | Yes - `web.open` stops at `L266` after China row; `Total lines: 1226` reported | `000 17.0% 31 Dec 2025 Official estimate[ 5 ] [ c ]` | `web.run`, `web.open`, `node_repl`, `curl` | No | `curl` failed; `web.open` truncation correctly identified; no artifacts written; 50 seconds |
| `GPT-5.4-Mini High` | ~785,605 chars | ~196,000 | No - `curl` complete. Yes - `web.open` stops at `L266` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3` | No | `curl` escalation x4; `wordlim: 200` visible in tool output; no artifacts written; 1 minute 44 seconds |
| `GPT-5.4-Mini Extra High` | ~785,605 chars | ~196,000 | No - `curl` complete. Yes - `web.open` paginates into chunks; `Total lines: 1226` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3`, `urllib` | No | `curl` escalation x4; text-only proxy measured at ~67,005 chars separately from raw HTML; no artifacts written; 4 minutes 20 seconds |
| `GPT-5.4 Low` | ~10,000–12,000 chars est. | ~2,500–3,000 | Yes - `web.open` stops at `L266` after China row; follow-up `lineno` calls confirmed `L1225` | `L266: 1,404,890,000 17.0% 31 Dec 2025 Official estimate[ 5 ] [ c ]` | `web.run`, `web.open` | No | no `curl`; no shell commands; offset-based `web.open` pagination without shell access; strongest metacognitive surface characterization in `GPT-5.4` batch; no artifacts written; 36 seconds |
| `GPT-5.4 Medium` | ~95,000–110,000 chars est. | ~24,000–28,000 | Yes - `web.open` stops at `L266`; follow-up fetches at `L560` and `L1180` confirmed middle and end | `ependencies by population\n\n122 languages\n\nAdd topic` | `web.run`, `web.open`, `python3` | No | no `curl`; autonomous three-point page traversal; strongest `H5` signal in non-`curl` set; no artifacts written; 1 minute 6 seconds |
| `GPT-5.4 High` | ~22,000–23,000 chars est. | ~5,500–6,000 | Yes - `web.open` stops at `L353`; follow-up `web.open` reached `L1225` | `0.1% 31 Mar 2026 Monthly national estimate[ 100 ]` | `web.run`, `web.open`, `python3` | No | no `curl`; `wordlim: 200` confirmed in tool output; autonomous pagination via `web.open` offset; no artifacts written; 6 minutes 47 seconds |
| `GPT-5.4 Extra High` | ~785,605 chars | ~196,000 | No - `curl` complete. Yes - `web.open` stops at `L266` then `L353` in same session | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `python3`, `HTMLParser` | Yes | `curl` escalation x4; both `L266` and `L353` cutoffs observed in single session confirming soft/adjustable window; wrote `wiki_sc3.html` to `/private/tmp`; 5 minutes 23 seconds |
| `GPT-5.5 Low` | ~785,605 chars | ~196,000 | No - `curl` complete. Yes - `web.open` stops around `L353` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail` | Yes | `curl` escalation without explicit permission request noted; wrote `wiki_population_response.html` to `Documents/Codex`; 29 seconds |
| `GPT-5.5 Medium` | ~785,605 chars | ~196,402 | No - `curl` complete. Yes - `web.open` stops around `L353` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `printf` | Yes | `curl` escalation x1; wrote `wikipedia_population.html` to `Documents/Codex`; token estimate via `printf` arithmetic; 45 seconds |
| `GPT-5.5 High` | ~785,605 chars | ~196,400 | No - `curl` complete. Yes - `web.open` stops around `L266` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `ruby`, `wc` | Yes | `curl` escalation x1; `ruby` used for tail verification; wrote `wikipedia_population.html` to `Documents/Codex`; `L266` reversion from `L353` in prior 5.5 runs; 1 minute 5 seconds |
| `GPT-5.5 High` | ~785,605 chars | ~196,000 | No - `curl` complete. Yes - `web.open` stops around `L353`; follow-up `web.open` inspected ending lines | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `perl`, `tail`, `grep` | Yes | `curl` escalation x1; `perl` used for measurement alongside `ruby` from run 1; wrote `wikipedia_population.html` to `Documents/Codex`; 1 minute 20 seconds |
| `GPT-5.5 Extra High` | ~785,605 chars | ~196,402 | No - `curl` complete. Yes - `web.open` first window shows `L0–309` of 1226; follow-up reached `L1225` | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `node`, `head`, `tail` | Yes | `curl` escalation x1; custom user-agent `-A "Codex retrieval test SC-3"` first observed; `L309` third distinct cutoff point; wrote `wikipedia_population_response.html` to `Documents/Codex`; 2 minutes 12 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported via the `curl` path. Successful `curl` fetches returned approximately 785,605 chars consistently across all runs with DNS access, well above
any 10–100 KB ceiling threshold. Runs relying solely on `web.open` returned approximately 10,000–23,000 chars for single-view calls, consistent with a fixed
line-count viewport rather than a character ceiling. `GPT-5.4-Mini Low` is the strongest `H1` signal in the set: the agent received approximately 18,000 chars,
believed the excerpt was the full page, and reported no truncation, consistent with a hard display ceiling operating below the agent's awareness threshold.

**Combined verdict: `H1` no for the `curl` path on valid fetches. Partially consistent with the `web.open` path where the window is line-count-bound rather
than character-bound. The `GPT-5.4-Mini Low` false-complete report is the clearest evidence of a fixed display ceiling in the SC-3 set.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Successful `curl` fetches returned approximately 196,000–196,402 tokens consistently, well above the 2,000-token threshold. `web.open`-only runs
and `web.open` initial excerpts ranged from approximately 1,400–6,000 tokens. `GPT-5.4-Mini Medium` reported approximately 2,700–3,000 tokens in the visible
excerpt, the closest approach to a 2,000-token ceiling in the set, but this reflects the `web.open` line window rather than a token-based cutoff mechanism.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported. The `web.open` tool consistently truncated at `L266`, `L353`, or `L309` depending on run and model. All three cutoff points land mid-table in the
population data, not on structural boundaries. `wordlim: 200` was visible in tool output in `GPT-5.4-Mini High` and `GPT-5.4 High`, indicating a word-count-driven
window rather than a structure-aware mechanism. `GPT-5.4 Extra High` observed both `L266` and `L353` in a single session by varying response length settings,
confirming the window is adjustable rather than fixed. Three distinct cutoff points across 21 runs effectively rules out structure-aware truncation.

**Combined verdict: `H3` no. Truncation is word-count-driven and consistently lands mid-table at non-structural boundaries. The `wordlim: 200` parameter is the
strongest mechanistic evidence in the set.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 21 runs used the Codex IDE surface exclusively. Within the Codex IDE surface, a consistent two-tier network access pattern
confirmed across most runs: sandboxed DNS resolution failure on the first `curl` attempt followed by escalated success after permission approval.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval infrastructure behavior confirmed consistent across all 21 runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported, with meaningful variation by LLM version and intelligence level. No run executed proactive chunking before encountering a truncation signal.
`GPT-5.4 Medium` is the strongest `H5` positive in the set: without `curl` or shell access, the agent autonomously fetched windows at start, `L560`, and `L1180` to
verify beginning, middle, and end of the document. `GPT-5.4 High` and `GPT-5.5 Extra High` used follow-up `web.open` offset calls after recognizing truncation.
`GPT-5.2 Extra High` used 20 web searches and three distinct `curl` fetches with active token estimation reasoning. `GPT-5.4-Mini Low` and `GPT-5.3-Codex Low` made
two-fetch sequences covering start and end without systematic middle traversal. Runs using `curl` successfully typically didn't paginate `web.open` further, treating
the direct fetch as authoritative.

**Combined verdict: `H5` partially supported. Reactive offset-based `web.open` pagination observed across multiple runs. True proactive auto-pagination not observed.
Escalation from `web.open` to `curl` is the dominant retrieval strategy from `GPT-5.2` through `GPT-5.5` at `Medium` intelligence level and above.**

---

## Emergent Findings

1. **`web.open` imposes a variable line-count window, not a fixed ceiling.** Cutoff points of `L266`, `L309`, and `L353` observed across 21 runs. All three land
mid-table in the population data. `GPT-5.4 Extra High` observed both `L266` and `L353` in a single session by varying response length settings, and `wordlim: 200`
appeared explicitly in tool output in multiple runs. The window is soft and adjustable rather than a single fixed limit.

2. **`curl` reliable full-document retrieval path.** Runs using `curl` with escalated network access consistently returned approximately 785,605 chars. Runs relying
solely on `web.open` never exceeded approximately 23,000 chars estimated. The decision to use `curl` was the single strongest predictor of retrieval completeness
regardless of LLM version or intelligence level.

3. **Artifact production higher in `SC-3` than `SC-1`, with approximately 14 HTML files written across 21 runs.** Files were approximately 793 KB consistently across
all runs that produced artifacts, reflecting the full raw HTML fetch. Artifacts written to `Documents/Codex` permanent workspace more frequently than to `/private/tmp`,
which may reflect agent reasoning about a table-heavy document requiring persistent reference. `GPT-5.4` runs produced the fewest artifacts in the batch.

4. **`GPT-5.2` uniquely produced multiple artifacts per run.** `GPT-5.2 High` wrote two near-identical HTML files and `GPT-5.2 Extra High` wrote three, including a
compressed variant. This multi-artifact pattern wasn't observed in any other LLM version. Both runs wrote to `Documents/Codex`.

5. **`GPT-5.3-Codex` showed most consistent agentic retrieval pattern in the batch.** The dominant sequence was: call `web`, view text window with optional `lineno`
pagination, then use `curl` for precise measurement, then write artifact to persistent workspace. This pattern reflects explicit reasoning that `web.open` offers
extractions unsuitable for precise measurements.

6. **`GPT-5.4` didn't produce artifacts in most runs and consistently used `python3` over `curl` for measurements.** `GPT-5.4 Low` and `GPT-5.4 Medium` relied entirely
on `web.open` offset pagination without shell escalation. `GPT-5.4 Medium` produced the clearest autonomous three-point traversal in the set. The preference for
estimation over precision and `python3` over `curl` may reflect a reasoning style difference at this model version.

7. **`GPT-5.4-Mini` produced no artifacts and consistently reported truncation by design without always relying on `curl` for measurements.** `GPT-5.4-Mini Low` is the
only run in the set where the agent failed to recognize that the `web.open` excerpt truncated, believing approximately 18,000 chars represented the full page.
`GPT-5.4-Mini Medium` correctly identified `L266` as a truncation boundary without `curl` access.

8. **`multi_tool_use.parallel` appears in `GPT-5.5 Medium`, `High` run 2, and implicitly in other `GPT-5.5` runs.** This parallel tool invocation pattern not observed
in `GPT-5.2` or `GPT-5.3-Codex` runs and appears consistent with `GPT-5.5` across intelligence levels, consistent with the `SC-1` and `BL-3` findings.

9. **`GPT-5.5` introduced novel measurement tools not seen in prior LLM versions.** `ruby` appeared in `GPT-5.5 High` run 1, `perl` in `GPT-5.5 High` run 2 and
`GPT-5.5 Extra High`, and `node` in `GPT-5.5 Extra High`. This broader scripting tool repertoire not observed in `GPT-5.2` through `GPT-5.4-Mini` runs.

10. **`GPT-5.5 Extra High` used a custom `curl` user-agent, the first observed instance across all SC-3 runs.** The `-A "Codex retrieval test SC-3"` flag appeared in both
sandboxed and escalated `curl` attempts. The motivation is unclear, it may reflect labeling convention, bot-blocking awareness, or incidental behavior, but the pattern
wasn't observed in any other run across all 21 sessions and may be worth watching in subsequent `GPT-5.5 Extra High` runs.

11. **The `L266` versus `L353` cutoff split may correlate with model tier.** `L266` appears predominantly in `GPT-5.2`, `GPT-5.4-Mini`, and some `GPT-5.4` runs. `L353`
appears predominantly in `GPT-5.3-Codex`, `GPT-5.4 High`, and `GPT-5.5` runs. `L309` appeared once in `GPT-5.5 Extra High`. Within `GPT-5.5`, inconsistency between `L266`
and `L353` within the same tier suggests the window is also session-variable rather than strictly model-determined.

12. **Intelligence level doesn't reliably predict retrieval quality within LLM version.** `GPT-5.4 Low` produced the most explicit surface characterization in the `GPT-5.4`
batch without any shell tools. `GPT-5.4 Medium` produced the strongest `H5` result in the non-`curl` set. `GPT-5.2 Extra High` produced the most exhaustive multi-fetch
behavior in the `GPT-5.2` batch. The most consequential behavioral differences are LLM-version-level, not intelligence-level.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.2 Low` | Partial | `PARTIAL - web_run_snippets_only + no_curl + two_region_fetch + indeterminate_truncation + 24s` |
| `GPT-5.2 Medium` | Pass | `PASS - curl_785KB_complete + web_open_L266_excerpt + sc3_html_artifact + 2m11s` |
| `GPT-5.2 High` | Pass | `PASS - curl_785KB_complete + web_open_L266_excerpt + dual_near_identical_artifact_first + Documents_Codex + 2m18s` |
| `GPT-5.2 Extra High` | Pass | `PASS - curl_785KB_complete + triple_near_identical_artifact_first + compressed_variant + 20_web_searches + Documents_Codex + 5m27s` |
| `GPT-5.3-Codex Low` | Partial | `PARTIAL - no_curl + web_open_two_fetch_start_end + L1225_footer_confirmed + architectural_surface_characterization + 19s` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_785KB_complete + web_open_snippet_limited + sc3_wikipedia_html_artifact + Documents_Codex + 37s` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_785KB_complete + web_open_L353_lineno_jumps + sc3_wiki_html_artifact + private_tmp + 1m36s` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_785KB_complete + web_open_L353_lineno_jumps + accidental_web_search_query + sc3_wiki_response_html + Documents_Codex + 3m9s` |
| `GPT-5.4-Mini Low` | Fail | `FAIL - curl_0_bytes + web_open_18KB_believed_complete + truncation_not_recognized + no_artifacts + 23s` |
| `GPT-5.4-Mini Medium` | Partial | `PARTIAL - curl_failed + web_open_L266_correctly_identified + no_pagination_attempt + no_artifacts + 50s` |
| `GPT-5.4-Mini High` | Pass | `PASS - curl_785KB_complete + web_open_L266 + wordlim_200_visible + no_artifacts + 1m44s` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - curl_785KB_complete + web_open_paginated_chunks + text_proxy_67KB_measured + no_artifacts + 4m20s` |
| `GPT-5.4 Low` | Partial | `PARTIAL - no_curl + web_open_L266 + lineno_offset_pagination + L1225_confirmed + strongest_surface_characterization + no_artifacts + 36s` |
| `GPT-5.4 Medium` | Partial | `PARTIAL - no_curl + python3_only + autonomous_three_point_traversal + L560_L1180_fetched + strongest_H5_non_curl + no_artifacts + 1m6s` |
| `GPT-5.4 High` | Partial | `PARTIAL - no_curl + web_open_L353 + wordlim_200_confirmed + follow_up_open_L1225 + no_artifacts + 6m47s` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_785KB_complete + L266_and_L353_both_observed_single_session + soft_window_confirmed + wiki_sc3_html_artifact + private_tmp + 5m23s` |
| `GPT-5.5 Low` | Pass | `PASS - curl_785KB_complete + web_open_L353 + no_permission_request_noted + multi_tool_use_parallel + Documents_Codex + 29s` |
| `GPT-5.5 Medium` | Pass | `PASS - curl_785KB_complete + web_open_L353 + printf_token_arithmetic + multi_tool_use_parallel + Documents_Codex + 45s` |
| `GPT-5.5 High` | Pass | `PASS - curl_785KB_complete + web_open_L266_reversion + ruby_measurement_first + Documents_Codex + 1m5s` |
| `GPT-5.5 High` | Pass | `PASS - curl_785KB_complete + web_open_L353 + perl_measurement + multi_tool_use_parallel + Documents_Codex + 1m20s` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_785KB_complete + web_open_L309_third_cutoff + custom_user_agent_first + follow_up_L1225 + node_measurement + Documents_Codex + 2m12s` |
