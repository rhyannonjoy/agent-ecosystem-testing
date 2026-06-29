# EC-1 Summary

## Test Conditions

|                 | **EC-1** |
| --------------- | -------- |
| URL             | `https://ai.google.dev/gemini-api/docs` |
| Expected size   | ~100KB; actual HTML payload 120,001 to 120,005 bytes per request, 119,785 UTF-8 characters |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/private/tmp` writable; project files accessible |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5` |
| Runs            | 13 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Light` | unavailable | unavailable | indeterminate; zero metrics returned | unavailable | `web.open`, `python3 urllib` | No | `python3 urllib` and `curl` both failed DNS resolution; escalation not attempted; task failure; named `Test web retrieval`; 34 seconds |
| `GPT-5.4-Mini Medium` | ~8,500 via `web.open` | ~2,100 | implicit; `web.open` rendered extraction; natural footer completion | footer language list | `web.open`, `turn0view0` | No | web-only run; no shell commands; named `Test web retrieval`; 1 minute 39 seconds |
| `GPT-5.4-Mini High` | 130,202 via headless Chrome | ~32,550 | mixed; tool-layer preview truncated; saved dump complete | `"true"></devsite-a11y-announce>\n</body></html>` | `web.open`, `curl`, `Browser`, `Playwright`, `mcp__node_repl.js`, headless Chrome | Yes | `Browser is not available: iab`; `Playwright` required 93.5 MB install; SIGABRT on initial attempts; `--dump-dom` succeeded on retry; named `Fetch Gemini API docs`; 5 minutes 31 seconds |
| `GPT-5.4-Mini Extra High` | 119,785 via `curl` | ~31,000 | no; matched `Content-Length: 120001` | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `web.open`, `curl`, `python3 pathlib` | Yes | asked permission to use `curl` x3; headers captured in thought panel, not saved to file; named `Test web retrieval`; 4 minutes 31 seconds |
| `GPT-5.4 Light` | 119,785 via `curl` | ~30,000 | implicit; `web.open` noted as rendered extraction; `curl` body authoritative | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `web.run` with `open`, `curl`, `wc -m`, `python3` | No | asked permission to use `curl` once; `wc -m` shell vs. direct capture discrepancy noted; named `Test web retrieval behavior`; 1 minute 1 second |
| `GPT-5.4 Medium` | 120,001 via `curl` | ~30,000 | mixed; `curl` no; `web.open` stopped at `L286` in language list section | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `web`, `curl`, `functions.exec_command` | Yes | asked permission for shell commands x4; `ec1_body.html` and `ec1_headers.txt` written to `/private/tmp`; named `Test web retrieval`; 1 minute 14 seconds |
| `GPT-5.4 High` | 119,789 chars, 120,005 bytes via `curl` | ~30,000 | mixed; `curl` no; `web.open` returned shorter extracted view | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `web.run` with `open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `sed`, `grep`, `od` | Yes | asked permission to use `curl` once; `web.open` shorter extracted view explicitly noted; `ec1_body.txt` and `ec1_headers.txt` written to `/private/tmp`; named `Test web retrieval`; 1 minute 35 seconds |
| `GPT-5.4 Extra High` | 9,848 via `web.open` | ~2,450 | yes; response globally abridged; ends at footer language list | footer language list, Thai through Korean | `web.run` with `open`, `perl`, `functions.exec_command` | No | `curl` not invoked; `web.open` and `perl` only; tool identifiers visible as page content in fetched document; named `Test web retrieval`; 4 minutes 59 seconds |
| `GPT-5.5 Light` | 119,789 chars, 120,005 bytes via `curl` | ~30,000 | no; matched `Content-Length: 120005` | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `web.run` with `open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail` | Yes | asked permission to use `curl` once; `ec1_body.txt` and `ec1_headers.txt` written to `/private/tmp`; naming collision risk with `GPT-5.4 High` artifacts; named `Test web retrieval`; 37 seconds |
| `GPT-5.5 Light` second run | 119,789 via `curl` | ~29,947 | mixed; `curl` no; `web.open` extraction ended in language list section | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `web.run` with `open`, `functions.exec_command`, `curl`, `wc -m`, `tail`, `python3` | Yes | accidental second `Light` run; `web.open` extraction consistent with `L286` language list endpoint; `ec1_gemini_docs.html` written to `/private/tmp`; named `Test web retrieval behavior`; 1 minute |
| `GPT-5.5 Medium` | 119,789 via `curl` | ~30,000 | no; ends with closing HTML tags | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `functions.exec_command`, `curl` | Yes | `web` pipeline bypassed entirely; artifact path inconsistency between researcher notes and screenshot; named `Test web retrieval`; 38 seconds |
| `GPT-5.5 High` | 119,785 chars, 120,001 bytes via `curl` | ~29,946 | no; ends with closing HTML tags | `nnounce></devsite-a11y-announce>\n</body>\n</html>` | `functions.exec_command`, `curl`, `python3` | Yes | `web` pipeline bypassed entirely; `tiktoken` unavailable; artifact written without file extension; named `Test web retrieval`; 52 seconds |
| `GPT-5.5 Extra High` | ~18,000 to 22,000 estimated via `web.open`; 287 lines | ~4,500 to 5,500 | implicit; rendered text extraction; reaches footer language selector | `L284` 中文 繁體, `L285` 日本語, `L286` 한국어 | `web.run` with `open`, `turn0view0` | No | `curl` not invoked; `web.open` only; opposite retrieval strategy from `T1 GPT-5.5 Extra High`; named `Test web retrieval behavior`; 2 minutes 4 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported on the `curl` path. Every run that completed a `curl` retrieval confirmed 119,785
to 120,001 characters with a clean `</html>` close, against an expected payload of approximately
120,001 bytes. The `web.open` surface showed consistent truncation well below the raw HTML volume
across every run that relied on it for measurement. `GPT-5.4-Mini Medium` returned approximately
8,500 characters, `GPT-5.4 Extra High` confirmed 9,848 characters, and `GPT-5.5 Extra High`
estimated 18,000 to 22,000 characters across 287 lines. Character counts at the `L286` cutpoint
differed substantially by model despite the identical line index, mirroring the model-dependent
count variation documented in SC-3 at `L353` and SC-4 at `L657`. EC-1's JavaScript-heavy SPA
structure means the `web.open` extraction reflects rendered text rather than raw HTML, making the
size reduction more pronounced than on static content test URLs.

**Combined verdict: `H1` partially. The `curl` path delivered full content at approximately
119,785 to 120,001 characters on every successful retrieval. The `web.open` surface returned
rendered extractions ranging from 8,500 to 22,000 characters, well below the raw HTML payload,
consistent with the framework's treatment of rendered extraction as implicit truncation. The
mechanism is surface-level rendering rather than a fixed character ceiling, and character counts
at the consistent `L286` cutpoint vary by model.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. `curl` runs produced token estimates of approximately 29,946 to 32,550 tokens,
well above the proposed 2,000-token ceiling. `web.open`-only runs came closest: `GPT-5.4-Mini
Medium` estimated approximately 2,100 tokens and `GPT-5.4 Extra High` estimated approximately
2,450 tokens. Both exceeded the threshold without a truncation event attributable to a token
limit, and both ended at the footer language list rather than at a mid-content cutoff consistent
with a ceiling hit. `GPT-5.5 Extra High` estimated 4,500 to 5,500 tokens on a `web.open`
extraction, also above the threshold. `tiktoken` wasn't installed in the `T2` sandbox, confirmed
in Run 12, so all estimates rely on the 4 chars per token heuristic.

**Combined verdict: `H2` no. Token counts on both retrieval paths exceeded the proposed 2,000-token
ceiling in every run. `GPT-5.4-Mini Medium` and `GPT-5.4 Extra High` came closest at approximately
2,100 and 2,450 tokens respectively, but both ended at the footer language list rather than at a
mid-content cutoff consistent with a token limit.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Partially supported on the `web.open` surface. The footer language list section emerged as a
consistent structural endpoint across all runs where a `web.open` truncation point documented.
`GPT-5.4 Medium` reported truncation at `L286`, ending in the language list section.
`GPT-5.4 Extra High` confirmed the last 50 characters were the Thai, Simplified Chinese,
Traditional Chinese, Japanese, and Korean language entries. `GPT-5.5 Extra High` showed the same
endpoint at `L284` through `L286`. The second `GPT-5.5 Light` run documented the same language
list endpoint on `web.open` before escalating to `curl`. The endpoint is consistent across models
and reasoning levels, pointing to a surface-level line window that coincides with a structural
page boundary. The `curl` path produced no truncation events to evaluate for structure-awareness.

**Combined verdict: `H3` partially. The `web.open` surface truncated consistently at the footer
language list section across every run where a cutpoint documented, which is a structural page
boundary. Whether the surface is explicitly structure-aware or whether a line-indexed window
happens to coincide with this boundary not resolved from these runs alone. The `curl` path
produced no truncation events to evaluate.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Supported. Retrieval strategy divergences between `T2` and matched `T1` pairs appeared across
multiple model and reasoning level combinations. `GPT-5.4-Mini Light` is the clearest cross-track
divergence: `T2` returned zero usable metrics after both `python3 urllib` and `curl` failed DNS
resolution without escalation, while `T1 GPT-5.4-Mini Low` successfully retrieved 133,106
characters. `GPT-5.4-Mini Medium` used the `web.open` surface exclusively with no shell
escalation in `T2`, while the `T1` counterpart escalated through `curl`, Browser, and Node Repl.
`GPT-5.4-Mini High` encountered `Browser` unavailability via `iab` and a 93.5 MB `Playwright`
install requirement before reaching the `--dump-dom` path, friction absent from the `T1 High`
counterpart. `GPT-5.4 Extra High` showed distinct tool identifiers in `T2`, including `web.click`
and `web.find`, where `T1 Extra High` used `turn0view0` and `mcp__node_repl__.js`. `GPT-5.5
Extra High` is the starkest strategy inversion: `T2` used `web.open` exclusively while `T1`
bypassed the web pipeline entirely for `curl`. `GPT-5.5 Medium` and `GPT-5.5 High` bypassed the
web pipeline entirely in `T2` while their `T1` counterparts used `web.open` before escalating.
The payload difference between `T1` May runs, approximately 132,890 to 144,444 characters, and
`T2` June runs, approximately 119,785 to 120,001 characters, attributed to the June 22, 2026
page modification confirmed by the `last-modified` response header rather than surface behavior.

**Combined verdict: `H4` yes. Tooling availability constraints, tool identifier differences, and
retrieval strategy divergences at matched model and level pairs confirm surface-driven behavioral
differences across the `T2` series. Payload size convergence at reasoning levels where both tracks
escalated to `curl` explained by the June 22 page modification rather than surface equivalence.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported. Multi-step retrieval appeared in most runs, most commonly as escalation from
`web.open` to `curl` after the agent identified the rendered extraction as insufficient for
precise measurement. `GPT-5.4-Mini High` produced the most expansive multi-step behavior,
attempting `Browser` via `iab`, `Playwright`, and headless Chrome in sequence across approximately
19 commands before completing the dump. `GPT-5.5 Extra High` issued a `web.open` call via
`turn0view0` and accepted the 287-line window without escalating. `GPT-5.5 Medium` and
`GPT-5.5 High` bypassed `web.open` entirely and went straight to `curl` in two-step or
three-step measurement chains. Run 1 is a multi-step failure with no successful retrieval. No run
demonstrated systematic pre-planned chunking or pagination of the full document.

**Combined verdict: `H5` partially. Multi-step retrieval appeared in most runs but took the form
of surface escalation from `web.open` to `curl` or measurement verification chains rather than
systematic content-completeness pagination. Run 1 is a task failure with multi-step retrieval
failures and no successful output. Run 13 is the only completed single-tool run with confirmed
truncation and no escalation attempt.**

---

## Emergent Findings

1. **The `web.open` surface returned a rendered text extraction substantially smaller than the
raw HTML payload in every run where it used as the primary retrieval path.** `EC-1`'s
JavaScript-heavy SPA structure makes this extraction especially small relative to raw HTML, with
`web.open` payloads ranging from 8,500 to approximately 22,000 characters against a 119,785-character
raw body, a more extreme reduction than observed in `SC-3` or `SC-4`.

2. **The footer language list section emerged as a consistent structural endpoint for `web.open`
truncation across all runs where a cutpoint documented.** The endpoint appeared at or near
`L286` regardless of model or reasoning level, mirroring the `L353` ceiling in SC-3 and the
`L657` ceiling in `SC-4`. Character counts at `L286` varied substantially by model, with
`GPT-5.4-Mini Medium` returning approximately 8,500 characters and `GPT-5.5 Extra High`
estimating 18,000 to 22,000 characters at the same line index.

3. **`GPT-5.5` models bypassed the `web` pipeline entirely at `Medium` and `High` reasoning levels
in `T2`, going straight to `curl`.** The same models used `web.open` before escalating in `T1`
at matched levels. `GPT-5.5 Extra High` showed the opposite pattern, using `web.open` exclusively
in `T2` while using `curl` exclusively in `T1`.

4. **`GPT-5.4-Mini High` is the most expensive run in the `EC-1` series** by rollout log volume,
297 KB against 66 KB to 140 KB for all other runs, requiring `Browser` via `iab`, a 93.5 MB
`Playwright` install, and a SIGABRT recovery before the `--dump-dom` path succeeded across
approximately 19 commands.

5. **Run 1 is the only task failure in the `EC-1` series**, returning zero usable metrics after
both `python3 urllib` and `curl` failed DNS resolution without the agent attempting permission
escalation. It's the only `EC-1` run with no character count, no token estimate, and no truncation
assessment available.

6. **Double-rendering appeared in 12 of 13 EC-1 runs**, consistent with the surface behavior
documented across `BL-1`, `BL-2`, and `SC-2`. After the session appeared to complete, identical
content appended to the output rather than resolved, producing a duplicate report. The pattern
appeared at every reasoning level and across all three model variants, with no exceptions,
confirming it isn't model-specific or reasoning-level-specific. Run 1 is the only run where
double-rendering wasn't reported, consistent with its task failure producing no complete output
to duplicate.

7. **The `last-modified: Mon, 22 Jun 2026 18:20:45 GMT` header was identical across all `T2`
runs that captured response headers**, confirming a stable page state during the `T2` collection
window. The ~13,000-character difference between `T1` May runs and `T2` June runs is attributable
to the June 22 page modification rather than surface behavior. The `content-length` header showed
minor variation across `T2` requests, 120,001 bytes in some runs and 120,005 bytes in others,
with identical `last-modified` timestamps.

8. **Tool identifier differences between `T1` and `T2` runs at matched model and level pairs
were consistent across the series.** `T1` runs used `turn0view0`, `mcp__node_repl__.js`, and
`multi_tool_use.parallel` at several levels; `T2` counterparts used `web.click`, `web.find`,
and `mcp__node_repl.js` instead. These differences were surface-consistent rather than
reasoning-level-driven.

9. **`GPT-5.4-Mini High` is the only run in the `EC-1` series to attempt all three browser
automation paths, `iab`, `Playwright`, and headless Chrome via `--dump-dom`, in a single
session.** No other run in the `EC-1` or prior `T2` series reached the `--dump-dom` fallback.

10. **Artifact naming varied across runs, creating workspace contamination risk.** Runs 7 and 9
both wrote to `/private/tmp/ec1_body.txt` and `/private/tmp/ec1_headers.txt` with identical
filenames.

11. **`tiktoken` wasn't installed in the `T2` sandbox**, confirmed in Run 12 when the module
import failed. All token estimates in the `EC-1` series rely on the 4 chars per token heuristic,
making cross-run token comparisons internally consistent but approximate.

12. **Tool identifiers and API client names visible in the `EC-1` test URL's page content included
`curl`, `genai.Client`, `client.interactions.create`, and `GoogleGenAI`.** These appeared in Run
8's `web.open` extraction as page content rather than tool output, reflecting the Gemini API
documentation's own code examples. No other `EC-1` test URL produced this kind of tool-name
collision in the extracted content.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Light` | Fail | `FAIL, python3_urllib_dns_fail + curl_dns_fail + no_escalation + zero_metrics + task_failure + 34 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_open_8500_implicit_truncation_footer + turn0view0 + no_shell + no_artifact + 1 minute 39 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, headless_chrome_130202_chars + browser_iab_unavailable + playwright_93mb_install + sigabrt_recovery + ec1_dom_dump_html_130KB + 5 minutes 31 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, curl_119785_chars + headers_thought_panel_only + gemini_api_docs_html_120KB + permission_asked_x3 + 4 minutes 31 seconds` |
| `GPT-5.4 Light` | Pass | `PASS, curl_119785_chars + web_open_implicit_truncation + wc_m_discrepancy_noted + no_artifact + 1 minute 1 second` |
| `GPT-5.4 Medium` | Pass | `PASS, curl_120001_chars + web_open_L286_language_list + ec1_body_html_120KB + ec1_headers_txt + permission_asked_x4 + 1 minute 14 seconds` |
| `GPT-5.4 High` | Pass | `PASS, curl_119789_chars_120005_bytes + web_open_shorter_extracted_view + ec1_body_txt_120KB + ec1_headers_txt + permission_asked_once + 1 minute 35 seconds` |
| `GPT-5.4 Extra High` | Pass | `PASS, web_open_9848_explicit_truncation_footer + perl_only + no_curl + no_artifact + 4 minutes 59 seconds` |
| `GPT-5.5 Light` | Pass | `PASS, curl_119789_chars_120005_bytes + ec1_body_txt_120KB + ec1_headers_txt + naming_collision_risk + permission_asked_once + 37 seconds` |
| `GPT-5.5 Light` second run | Pass | `PASS, curl_119789_chars + web_open_language_list_endpoint + ec1_gemini_docs_html_120KB + accidental_second_light_run + 1 minute` |
| `GPT-5.5 Medium` | Pass | `PASS, curl_119789_chars + web_pipeline_bypassed + artifact_path_inconsistency + 38 seconds` |
| `GPT-5.5 High` | Pass | `PASS, curl_119785_chars_120001_bytes + web_pipeline_bypassed + tiktoken_unavailable + no_file_extension + 52 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_open_18k_22k_implicit_truncation_L286 + no_curl + turn0view0 + opposite_strategy_from_t1 + no_artifact + 2 minutes 4 seconds` |
