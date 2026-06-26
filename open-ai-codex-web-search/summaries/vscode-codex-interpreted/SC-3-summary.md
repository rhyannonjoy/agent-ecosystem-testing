# SC-3 Summary

## Test Conditions

|                 | **SC-3** |
| --------------- | -------- |
| URL             | `https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population` |
| Expected size   | ~100KB; actual HTML payload 792,899 bytes, 786,213 UTF-8 characters |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/private/tmp` writable; project files accessible as working directory |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.4-Mini`, `GPT-5.5` |
| Runs            | 9 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Low` | not measured; token estimate only | ~12k to 18k visible excerpt | `web.open` yes at `L353` of 1225; `curl` DNS fail, unresolved | `31 Dec 2025 Official estimate[ 5 ] [ c ]` | `web.open`, `curl` | No | two-tier DNS failure unreported and unexamined; no metrics calculated; didn't ask permission for `curl`; named `Test web retrieval`; 50 seconds |
| `GPT-5.4-Mini Medium` | ~23,000 to 25,000 `web.open`; 786,213 `curl` | ~5,500 to 6,500 visible excerpt | `web.open` yes at `L353` of 1225; `curl` no | `0.1% 30 Apr 2026 Monthly national estimate[ 101 ]` | `web.open`, `curl`, `wc`, `tail`, `file`, `node` | Yes | two-tier DNS pattern first visible in chat output; asked permission once; named `Fetch Wikipedia response metrics`; 2 minutes 31 seconds |
| `GPT-5.4-Mini High` | 786,213 chars, 792,899 bytes via `curl` | ~200k coarse estimate | mixed; `curl` no; `web.open` yes at `L353` of 1225 | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.open`, `curl`, `Browser`, `wc`, `tail`, `Node REPL` | Yes | `Browser` attempted, failed `Browser is not available: iab`; didn't ask permission initially, asked before `curl` escalation; named `Test web retrieval`; 4 minutes 57 seconds |
| `GPT-5.4-Mini Extra High` | indeterminate; node script returned 786,213 before failure | N/A | indeterminate | N/A | `web`, `curl` | Yes | capacity failure `Selected model is at capacity. Please try a different model`; searched for `browser control in-app-browser SKILL.md` before requesting permission; no report generated; rollout 6 minutes 58 seconds |
| `GPT-5.4-Mini Extra High` | 786,213 chars, 792,899 bytes via `curl` | ~200k coarse estimate | mixed; `curl` no; `web.open` yes at `L353` of 1225 | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.open`, `python3`, `curl` | Yes | three-tier escalation: network fetch probed without permission, `python3 urllib.request` returned HTTP 403, `curl` with `Mozilla/5.0` User-Agent succeeded; named `Test retrieval behavior`; 9 minutes 53 seconds |
| `GPT-5.5 Low` | ~65,000 to 75,000 estimated from `web.open` | ~15,000 to 19,000 | yes at `L353` of 1225; second `web.open` confirmed tail through `L1224` | `0.1% 30 Apr 2026 Monthly national estimate[ 101 ]` | `web.run`, `Compute suffix` | No | no `curl` attempted; `Compute suffix` tool appeared for first time in SC-3 series; named `Test web retrieval SC-3`; 35 seconds |
| `GPT-5.5 Medium` | 786,213 chars, 792,899 bytes via `curl` | ~196,500 via explicit 4 chars/token heuristic | mixed; `curl` no; `web.open` yes at `L353` of 1225 | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.run`, `curl`, `wc`, `tail`, `file`, `node` | Yes | asked permission once; explicitly stated 4 chars/token heuristic; `node` self-corrected after shell quoting failure; named `Test web retrieval SC-3`; 2 minutes 3 seconds |
| `GPT-5.5 High` | 786,213 chars, 792,899 bytes via `curl` | ~196,500 via 4 chars/token heuristic | implicit; `curl` no; `web.open` display clipped at `L353` of 1225 | `"Wikimedia list article"}</script>\n</body>\n</html>` | `web.open`, `curl`, `wc`, `tail`, `rg`, `functions.exec_command`, `multi_tool_use.parallel` | Yes | asked permission once; `rg` appeared for first time in `T2` SC-3 series; agent named two-tier pattern explicitly in output; named `Test web retrieval SC-3`; 2 minutes 16 seconds |
| `GPT-5.5 Extra High` | not measured; agent explicitly declined to estimate | ~12,000 to 16,000 visible excerpt | yes at `L353` of 1225 | `0.1% 30 Apr 2026 Monthly national estimate[ 101 ]` | `web.open` only | No | zero shell commands; didn't invoke `curl`; declined to estimate character count from excerpt alone; simplest tool chain in series despite highest reasoning level; named `Test web retrieval SC-3`; 2 minutes 39 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported on the raw `curl` path. Runs that escalated to `curl` successfully, specifically `GPT-5.4-Mini Medium`, `GPT-5.4-Mini High`, the completed `GPT-5.4-Mini Extra High`,
`GPT-5.5 Medium`, and `GPT-5.5 High`, all confirmed 786,213 characters with clean `</html>` closes well above the proposed 10 to 100KB ceiling. The `web.open` surface showed
model-dependent variation rather than a consistent fixed ceiling. `GPT-5.4-Mini` runs that relied on `web.open` reported approximately 23,000 to 25,000 characters while `GPT-5.5 Low`
estimated 65,000 to 75,000 characters, with both stopping at the same line index of `L353`. That divergence in character count at an identical line cutoff is consistent with per-model
rendering depth rather than a surface-level character boundary. `GPT-5.5 Extra High` declined to estimate character count at all. The capacity failure run contributes no evidence.

**Combined verdict: `H1` no. The `curl` path delivered full content at 786,213 characters on every successful escalation. The `web.open` surface truncated at `L353` consistently but
with model-dependent character counts ranging from approximately 23,000 to 75,000 characters, which doesn't support a fixed character ceiling on either path.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. `curl` runs retrieved content estimated at approximately 196,000 to 200,000 tokens using the 4 chars/token heuristic, far above the proposed threshold. `web.open` runs
returned visible excerpt estimates ranging from approximately 5,500 to 19,000 tokens, all well above the threshold. `GPT-5.5 Extra High` estimated 12,000 to 16,000 tokens for the visible
excerpt, the lowest in the series, and still an order of magnitude above the proposed ceiling. No run on either retrieval path produced output clustered near 2,000 tokens. Run 7 explicitly
identified the 4 chars/token estimate as coarse, and no tokenizer package was available in the `T2` sandbox across the series.

**Combined verdict: `H2` no. Token counts on both retrieval paths exceed the proposed ceiling in every completed run.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported on this URL. SC-3's test target is a Wikipedia HTML page with no Markdown source in the rendered retrieval output. The `web.open` surface reported a line-indexed cutoff at
`L353` in every run where the cutoff was observable, landing mid-table in the population data at the Sweden row. That consistent line index across different models and reasoning levels
is more consistent with a fixed line window than content-aware behavior. The `curl` path returned raw HTML throughout with no truncation on any successful escalation. Unlike SC-1, where
some single-pass `web.open` extractions terminated near the page footer, every SC-3 `web.open` cutoff landed mid-content, making a structural boundary explanation untenable on this URL.

**Combined verdict: `H3` no. Truncation on the `web.open` surface fell at a fixed line index mid-table in HTML with no Markdown structure present on either path. No structure-aware cutoff behavior was observed.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Supported. The two-tier sandboxed network pattern appeared in every `T2` run that attempted `curl`: sandboxed DNS failure first, permission escalation second. `T1` runs resolved the same
URL without that friction. The largest cross-track divergences appeared at `GPT-5.5 Low`, where `T1` escalated `curl` and retrieved 785,605 characters while `T2` stayed with `web.open` and
estimated 65,000 to 75,000 characters, and at `GPT-5.5 Extra High`, where `T1` escalated `curl` and produced a 793KB artifact while `T2` issued a single `web.open` and ran zero shell commands.
At reasoning levels where both tracks escalated to `curl`, retrieval volume converged near 786,000 characters, but toolchain composition differed: `T2` runs used `wc`, `tail`, `node`, and in
one case `rg`, while `T1` runs additionally introduced `ruby`, `perl`, `grep`, and `multi_tool_use.parallel`. The `GPT-5.4-Mini High` run uniquely attempted `Browser` use via `iab`, which isn't
available on the `T2` surface, consistent with the `Browser` friction pattern from SC-1 and SC-2.

**Combined verdict: `H4` yes. Network sandboxing, tool availability differences, and escalation requirements differ materially between surfaces. Strategy divergences at matched model and level
pairs are consistent across the series, with convergence in retrieval volume occurring only when both tracks escalate to `curl`.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported. Seven of eight completed runs initiated multi-step retrieval after the first fetch proved incomplete or surface-limited. Five of those transitions moved from `web.open` to
`curl` after the agent identified the line-indexed extraction as insufficient for precise measurement. `GPT-5.4-Mini Low` attempted `curl` reactively but the escalation failed silently.
`GPT-5.5 Low` issued a second `web.open` to confirm the page tail after observing the `L353` cutoff. All transitions were reactive rather than pre-planned: each followed an observed shortfall rather
than a systematic multi-segment fetch strategy. `GPT-5.5 Extra High` issued a single `web.open` and made no retrieval adaptation, accepting the excerpted window without escalation. The capacity failure
run didn't complete. No run in the series demonstrated true systematic chunking or pagination of the full document.

**Combined verdict: `H5` partially. Reactive multi-step retrieval appeared in seven of eight completed runs but took the form of surface escalation from `web.open` to `curl` rather than chunked pagination.
`GPT-5.5 Extra High` is the sole completed run with no retrieval adaptation.**

---

## Emergent Findings

1. **The `L353` line ceiling on the `web.open` surface was consistent across all runs where it was observable, regardless of model or reasoning level.** That cross-model consistency 
points to a surface-level line window setting rather than a per-model behavior, and contrasts with SC-1's variable first-pass cutoffs near `L344` across runs.

2. **Character counts at the `L353` cutoff differed significantly by model despite the identical line index.** `GPT-5.4-Mini` runs reported approximately 23,000 to 25,000 characters 
while `GPT-5.5 Low` estimated 65,000 to 75,000 characters at the same stopping point. The gap at an identical line index suggests line length or rendering format varies between models, 
making the `web.open` ceiling line-indexed rather than character-fixed.

3. **`curl` confirmed as the reliable full-document retrieval path for SC-3.** Every run that escalated to `curl` successfully retrieved 786,213 characters and 792,899 bytes with clean 
`</html>` closes. The payload was stable across the collection window, unlike SC-2's dynamic drift between runs.

4. **The expected size of ~100KB significantly underestimated the actual payload.** The HTML payload at 792,899 bytes is nearly 8x the expected figure. The page delivers full Wikipedia 
article HTML rather than any Markdown or plaintext representation.

5. **The capacity failure in the first `GPT-5.4-Mini Extra High` run introduced a new failure mode.** The error `Selected model is at capacity. Please try a different model` terminated 
the session before report generation and wasn't recoverable within the run. It's distinct from the DNS failures, sandbox policy errors, and tool availability failures documented in 
earlier cycles.

6. **The completed `GPT-5.4-Mini Extra High` run produced a three-tier escalation sequence not seen in prior `T2` runs.** The sequence moved from an unpermissioned network fetch probe 
that failed with `TypeError: fetch failed`, to `python3 urllib.request` that returned HTTP 403, to `curl` with a `Mozilla/5.0` User-Agent header that succeeded. It's the first instance 
in the series of an agent reasoning about HTTP request headers as a retrieval variable.

7. **`GPT-5.4-Mini High` attempted `Browser` use via the `iab` integration and received `Browser is not available: iab`.** The agent loaded the `Control In App Browser` skill from 
`github.com` before attempting the connection. The `T2` surface doesn't support `iab`, consistent with the `Browser` friction pattern documented in SC-1 and SC-2.

8. **`GPT-5.5 Extra High` produced the simplest tool chain in the series despite being the highest available reasoning level.** A single `web.open`, zero shell commands, and no `curl` 
attempt contrasts sharply with `T1 GPT-5.5 Extra High`, which escalated `curl` and produced a 793KB artifact in 2 minutes 12 seconds. This inversion is the clearest evidence in the SC-3 
set that higher reasoning level doesn't monotonically increase retrieval thoroughness on `T2`.

9. **All five runs that wrote artifacts to `/private/tmp` didn't reference or surface the artifact path in their final reports.** Runs 2, 3, 5, 7, and 8 all wrote 793KB HTML files and 
omitted the file path from their structured output. The written-but-not-disclosed pattern documented in SC-1 and SC-2 continued unbroken across `SC-3`.

10. **`GPT-5.5` runs consistently included the `SC-3` test ID in the session name as `Test web retrieval SC-3`, while `GPT-5.4-Mini` runs omitted the suffix in most cases.** The 
completed `GPT-5.4-Mini Extra High` run uniquely used `Test retrieval behavior`. The naming split suggests `GPT-5.5` models more reliably incorporated the test ID from the prompt into 
session naming.

11. **`GPT-5.4-Mini Low`'s `curl` DNS failure went completely unreported and unexamined in the chat output.** The agent moved on to reporting token estimates from the `web.open` excerpt 
without acknowledging the failed command or its exit code. Runs 2 and the `GPT-5.5 High` run explicitly noted the DNS failure and explained the escalation retry.

12. **All agents fetched `https://en.wikipedia.org/wiki/List_of_countries_by_population` rather than the specified `https://en.wikipedia.org/wiki/
List_of_countries_and_dependencies_by_population`.** Consistent character counts, line indexes, and content markers across all nine runs confirm both resolve to the same payload, with 
the shorter URL serving as the resolved form.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Pass | `PASS, web_open_L353_of_1225 + curl_dns_fail_unreported + no_metrics_calculated + no_artifact + 50 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, curl_786213_chars + web_open_L353_23k_to_25k + two_tier_dns_visible_in_chat + sc3_population_html_private_tmp + asked_permission_once + 2 minutes 31 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, curl_786213_chars + web_open_L353 + browser_iab_unavailable + list_of_countries_html_private_tmp + permission_asked_mid_session + 4 minutes 57 seconds` |
| `GPT-5.4-Mini Extra High` | Fail | `FAIL, capacity_failure + wiki_pop_html_793kb_private_tmp + browser_skill_searched + no_report_generated + rollout_6_minutes_58_seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, curl_786213_chars_mozilla_user_agent + three_tier_escalation + python3_http_403 + sc3_html_private_tmp + network_probe_unpermissioned + 9 minutes 53 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, web_open_L353_65k_to_75k + second_web_open_tail_L1224 + compute_suffix_tool + no_curl + no_artifact + 35 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, curl_786213_chars + web_open_L353 + explicit_4_chars_token_heuristic + node_self_correction + sc3_population_html_private_tmp + asked_permission_once + 2 minutes 3 seconds` |
| `GPT-5.5 High` | Pass | `PASS, curl_786213_chars + web_open_L353_implicit + rg_first_appearance + two_tier_pattern_named_explicitly + sc3_response_html_private_tmp + asked_permission_once + 2 minutes 16 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_open_only + L353_of_1225 + no_curl + no_shell_commands + char_count_declined + tokens_12k_to_16k_est + no_artifact + 2 minutes 39 seconds` |
