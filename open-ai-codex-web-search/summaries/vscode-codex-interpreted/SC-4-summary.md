# SC-4 Summary

## Test Conditions

|                 | **SC-4** |
| --------------- | -------- |
| URL             | `https://www.markdownguide.org/basic-syntax/` |
| Expected size   | ~30KB; actual HTML payload 64,659 bytes, 64,527 UTF-8 characters |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/private/tmp` writable; project files accessible as working directory |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.4-Mini`, `GPT-5.5` |
| Runs            | 8 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Light` | 64,659 via `python3 urllib` | ~16,000 | `python3` no; `curl` DNS fail both attempts, unresolved | `markdownguide' });</script></body></html>` | `web.open`, `curl`, `python3 urllib` | No | dual `curl` DNS failures unexamined; `python3 urllib` substituted without reporting pattern; offered to format report; named `Fetch markdown guide URL`; 41 seconds |
| `GPT-5.4-Mini Medium` | ~30,000 estimated from `web.open` | ~7,500 | implicit; `web.open` mid-content; `curl` DNS fail, unresolved | `with in .` | `web.open`, `curl` | No | `curl` DNS failed, not examined; five web searches; metrics estimated from excerpt; named `Test web retrieval SC-4`; 1 minute 16 seconds |
| `GPT-5.4-Mini High` | 64,527 via `curl` | ~16,000 | mixed; `curl` no; `web.open` display truncated mid-document | `markdownguide' });</script></body></html>` | `web.open`, `curl` | No | asked permission to use `curl` twice; explicitly stated `web.open` preview truncated mid-document; named `Test web retrieval`; 1 minute 52 seconds |
| `GPT-5.4-Mini Extra High` | 64,527 sourced from workspace rollout logs | ~16,000 | mixed; `web.open` mid-document in thought panel; no network fetch completed | `markdownguide' });</script></body></html>` | `web.run`, `Browser`, `Playwright`, workspace reads | No | `Browser is not available: iab`; `Playwright` binary not installed; metrics sourced from prior rollout logs without citing source; named `Test web retrieval behavior`; 7 minutes 2 seconds |
| `GPT-5.5 Light` | ~35,000 estimated from `web.open` | ~8,000 to 9,000 | yes at `L657` of 752 | `ces above, the rendered output would be identical:` | `web.open`, `node` | No | sole run with explicit truncation report and no escalation attempt; `node` used only to count and slice the visible string; named `Fetch markdown guide`; 17 seconds |
| `GPT-5.5 Medium` | 64,527 via `curl` | ~16,100 | mixed; `curl` no; `web.open` display truncated before `L657` of 752 | `markdownguide' });</script></body></html>` | `web.run`, `curl`, `wc`, `tail`, `rg`, `multi_tool_use.parallel` | Yes | asked permission to use `curl` twice; artifact written to `/private/tmp` but not referenced in report; named `Test web retrieval`; 1 minute 7 seconds |
| `GPT-5.5 High` | 64,527 chars, 64,659 bytes via `curl` | ~16,100 | mixed; `curl` no; `web.open` stopped at `L657` of 752 | `markdownguide' });</script></body></html>` | `web.run`, `curl`, `wc`, `tail`, `rg`, `perl` | Yes | asked permission to use `curl` once; `perl` used for tag balance analysis; first explicit char vs. byte distinction in the series; named `Test web retrieval`; 1 minute 27 seconds |
| `GPT-5.5 Extra High` | 64,527 via `curl` | 16,132 | mixed; `curl` no; `web.open` stopped at `L657` of 752; second `web.open` confirmed tail through `L752` | `markdownguide' });</script></body></html>` | `web.run`, `curl`, `perl`, `python3`, `wc` | No | asked permission to use `curl` twice; second `web.open` call recovered lines 657 to 752 before `curl` escalation; `tiktoken` not installed; named `Test web retrieval SC-4`; 2 minutes 35 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported on the `curl` path. Every run that completed a `curl` retrieval confirmed 64,527 characters with a clean `</html>` close, well
above the proposed 10 to 100KB ceiling. The `web.open` surface showed consistent truncation at approximately `L657` of 752 across all `GPT-5.5`
runs and the `GPT-5.4-Mini Medium` run that relied on `web.open` for its estimate. Character counts at that cutpoint differed by model:
`GPT-5.5 Light` estimated approximately 35,000 characters while `GPT-5.4-Mini Medium` reported approximately 30,000 characters at the same line
index. Both fall within the proposed ceiling range. `GPT-5.4-Mini Medium`'s last 50 characters of `with in .` confirm a mid-word cutoff rather
than a clean boundary. That divergence in character count at an identical line index mirrors the SC-3 pattern at `L353`, pointing to a
line-indexed window rather than a character-fixed ceiling on the `web.open` surface.

**Combined verdict: `H1` partially. The `curl` path delivered full content at 64,527 characters on every successful escalation. The `web.open`
surface truncated consistently at approximately `L657` with model-dependent character counts in the 30,000 to 35,000 range, which falls within
the proposed 10 to 100KB window, but the ceiling's line-indexed rather than character-fixed nature makes character-based truncation an incomplete
description of the behavior.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. `curl` runs produced token estimates of approximately 16,000 to 16,132 using the 4 chars per token heuristic, roughly eight times
the proposed 2,000-token ceiling. The `web.open`-only run, `GPT-5.5 Light`, estimated 8,000 to 9,000 tokens for the visible excerpt, four times
the proposed ceiling. `GPT-5.4-Mini Medium`'s web-only estimate of approximately 7,500 tokens is the lowest in the series and remains well above
the threshold. `GPT-5.5 Extra High` confirmed `tiktoken` wasn't installed in the sandbox, so all estimates rely on the 4 chars per token
heuristic rather than a tokenizer.

**Combined verdict: `H2` no. Token counts on both retrieval paths exceed the proposed 2,000-token ceiling in every run, with the lowest estimate
at approximately 7,500 tokens from a `web.open`-only excerpt.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported. `web.open` truncation landed mid-sentence or mid-section in every run where a cutpoint was observable. `GPT-5.5 Light` reported
the cutoff explicitly, with the visible response ending after `In both instances above, the rendered output would be identical: `, a mid-sentence
position in a code comparison section. `GPT-5.4-Mini Medium`'s last 50 characters of `with in .` indicate a mid-word cutoff. `GPT-5.4-Mini High`
described the `web.open` display as truncated "in the middle," and `GPT-5.4-Mini Extra High` described it as "mid-document." The `curl` path
produced no truncation events to evaluate for structure-awareness on any successful escalation. SC-4's test URL is a Markdown reference guide,
making a structure-aware cutoff testable here in a way it wasn't for SC-3, and no evidence of it appeared in any run.

**Combined verdict: `H3` no. Truncation on the `web.open` surface fell mid-sentence or mid-section in every run where it was observable. No run
produced a truncation event at a Markdown section boundary, and the `curl` path produced no truncation events to evaluate.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Supported. The two-tier sandboxed DNS failure pattern appeared in every `T2` run that attempted `curl`: sandboxed DNS failure first, permission
escalation second. `T1` runs resolved the same URL without that friction. The largest cross-track divergence appeared at `GPT-5.5 Light`, where
`T1` escalated `curl` and retrieved 64,527 characters while `T2` stayed with `web.open` and reported approximately 35,000 truncated characters
with no escalation attempt. `GPT-5.4-Mini Extra High` introduced workspace substitution as a fallback, sourcing metrics from prior run rollout
logs rather than fetching the URL directly, a behavior with no `T1` parallel. The same run also attempted `Browser` use via `iab` and
`Playwright`, both unavailable on the `T2` surface, consistent with the `Browser` friction pattern documented in SC-1, SC-2, and SC-3. At
reasoning levels where both tracks escalated to `curl`, final character counts converged near 64,527, but toolchain composition differed: `T2`
runs used `wc`, `tail`, `rg`, and `perl`, while `T1` runs additionally introduced `ruby`, `grep`, and `multi_tool_use.parallel`.

**Combined verdict: `H4` yes. Network sandboxing, `Browser` and `Playwright` unavailability, and the two-tier escalation requirement differ
materially between surfaces. Strategy divergences at matched model and level pairs are consistent across the series, with convergence in retrieval
volume occurring only when both tracks escalated to `curl`.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported. Six of eight runs initiated multi-step retrieval after the initial `web.open` fetch proved incomplete or unsuitable for
precise measurement. The most common transition was from `web.open` to `curl` after the agent identified the line-indexed extraction as
insufficient for exact counts. `GPT-5.4-Mini Extra High` produced the most expansive multi-step behavior in the series, attempting `Browser`
via `iab`, `Playwright`, a network fetch, and workspace rollout log reads across nine commands. `GPT-5.5 Extra High` issued a second same-URL
`web.open` call to recover lines 657 to 752 before escalating to `curl`, the closest to genuine pagination behavior in the series. `GPT-5.5 Light`
is the only run with confirmed truncation and no escalation attempt, accepting the `L657` window without further retrieval. No run demonstrated
systematic pre-planned chunking or true pagination of the full document.

**Combined verdict: `H5` partially. Multi-step retrieval appeared in six of eight runs but took the form of surface escalation from `web.open`
to `curl` or measurement verification chains rather than systematic content-completeness pagination. `GPT-5.5 Light` is the sole completed run
with confirmed truncation and no retrieval adaptation.**

---

## Emergent Findings

1. **The `L657` line ceiling on the `web.open` surface was consistent across all `GPT-5.5` runs where it was observable, regardless of
reasoning level.** That consistency at an identical line index across different models and reasoning levels points to a surface-level line window
setting, mirroring SC-3's consistent `L353` ceiling and contrasting with SC-1's variable cutoffs across runs.

2. **Character counts at the `L657` cutpoint differed by model despite the identical line index.** `GPT-5.4-Mini Medium` estimated approximately
30,000 characters while `GPT-5.5 Light` estimated approximately 35,000 characters at the same stopping point. The gap at an identical line
index is consistent with per-model rendering depth variation on the `web.open` surface, matching the SC-3 divergence at `L353`.

3. **`curl` confirmed as the reliable full-document retrieval path for SC-4.** Every run that escalated to `curl` successfully retrieved 64,527
characters and 64,659 bytes with clean `</html>` closes. The payload was stable across the collection window.

4. **The expected size of ~30KB underestimated the actual payload by approximately 2x.** The HTML payload at 64,659 bytes delivers full page
HTML rather than a Markdown text representation, which accounts for the gap between the expected source size and the actual retrieval volume.

5. **`GPT-5.4-Mini Extra High` introduced workspace substitution as a novel fallback strategy.** After `Browser` and `Playwright` both failed,
the agent sourced metrics from prior SC-4 rollout logs rather than attempting further network fetches. The source wasn't cited in the structured
output, leaving a discrepancy between the thought panel reasoning and the reported results.

6. **`GPT-5.4-Mini Extra High` attempted `Browser` use via `iab` and `Playwright`, both unavailable on the `T2` surface.** The agent loaded
the browser control skill from GitHub before discovering `Browser is not available: iab`, then tried `Playwright` before finding the binary
wasn't installed. The `Browser` friction pattern has now appeared across SC-1, SC-2, SC-3, and SC-4.

7. **`GPT-5.5 Light` is the only run in the SC-4 series with explicit truncation acknowledgment and no escalation attempt.** Despite confirming
the `L657` cutoff and reporting it accurately, the agent accepted the window without invoking `curl`. That inversion, where explicit truncation
awareness doesn't produce escalation, matches the `GPT-5.5 Extra High` pattern from SC-3.

8. **`GPT-5.5 High` explicitly distinguished 64,659 bytes from 64,527 characters, the first byte vs. character distinction in the SC-4 series.**
A `perl` one-liner confirmed the tag balance of the fetched HTML, the first use of `perl` for structural validation in the set.

9. **`GPT-5.5 Extra High` issued a second same-URL `web.open` call to recover content from lines 657 to 752 before escalating to `curl`.**
That pattern parallels `GPT-5.5 Low`'s second `web.open` tail confirmation in SC-3 and is the closest approach to deliberate pagination in
the SC-4 series.

10. **Artifacts written to `/private/tmp` weren't referenced in the final reports.** Runs 6 and 7 both wrote 65KB HTML files to temporary
storage and omitted the file paths from their structured output. The written-but-not-disclosed artifact pattern documented in SC-1, SC-2, and
SC-3 continued unbroken across SC-4.

11. **`tiktoken` isn't installed in the `T2` sandbox**, confirmed in run 8 when the module import failed. All token estimates in the SC-4
series rely on the 4 chars per token heuristic, making cross-run token comparisons internally consistent but approximate.

12. **`GPT-5.4-Mini Light`'s dual `curl` DNS failures went unexamined.** The agent substituted `python3 urllib` without reporting the failure
pattern or offering to retry with escalated permissions. The substitution succeeded but the failure mode wasn't disclosed, consistent with
`GPT-5.4-Mini Low`'s unreported `curl` failure in `SC-3`.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Light` | Pass | `PASS, python3_urllib_64659_chars + curl_dns_fail_both_attempts_unexamined + no_artifact + 41 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_open_30k_implicit_truncation_mid_content + curl_dns_fail_unexamined + no_artifact + 1 minute 16 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, curl_64527_chars + web_open_mid_document + permission_asked_twice + no_artifact + 1 minute 52 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, workspace_rollout_log_substitution_64527 + browser_iab_unavailable + playwright_not_installed + source_not_cited + no_artifact + 7 minutes 2 seconds` |
| `GPT-5.5 Light` | Pass | `PASS, web_open_35k_explicit_truncation_L657 + no_curl_attempted + node_slice_only + no_artifact + 17 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, curl_64527_chars + web_open_display_truncated + sc4_html_private_tmp + artifact_path_not_reported + permission_asked_twice + 1 minute 7 seconds` |
| `GPT-5.5 High` | Pass | `PASS, curl_64527_chars_64659_bytes + web_open_L657 + perl_tag_balance + char_byte_distinction + sc4_html_private_tmp + artifact_path_not_reported + permission_asked_once + 1 minute 27 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, curl_64527_chars + web_open_L657 + second_web_open_tail_L752 + tiktoken_not_installed + permission_asked_twice + no_artifact + 2 minutes 35 seconds` |
