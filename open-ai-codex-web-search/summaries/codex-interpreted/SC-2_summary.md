## SC-2 GPT-interpreted Track Summary

### Test Conditions

|                 | **SC-2**                                                                        |
| --------------- | ------------------------------------------------------------------------------- |
| URL             | `https://docs.anthropic.com/en/api/messages`                                    |
| Expected size   | ~80 KB assumed; actual ~512 KB Next.js app shell / ~128K tokens                 |
| Surface         | Codex IDE                                                                       |
| Workspace       | Session-scoped sandbox; persistent artifacts observed across sessions           |
| Track           | `T1` GPT-interpreted, Codex IDE                                                 |
| Method          | GPT-interpreted                                                                 |
| Runs            | 20                                                                              |
| Chunks returned | N/A, interpreted track                                                          |

---

### Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | 2,177 | ~545 | Yes - JS render fail | `loading…` + nav/footer | `web.run`, `Node REPL` | Yes empty | JS-render wall; Loading placeholders; no curl; 59 s |
| `GPT-5.2 Medium` | 1,532 | ~383 | Yes - JS render fail | `\nL138–141` line refs | `web.run`, `Node REPL` | Yes empty | wordlim: 200 indicator visible; redirect detected; 7m1s |
| `GPT-5.2 High` | 511,659 | ~127,915 | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `wc`, `python3` | Yes `sc2_response.html` | First curl escape; DNS fail then escalated; Next.js shell identified; 3m55s |
| `GPT-5.2 Extra High` | ~1,830 final turn | ~458 | Indeterminate | `\nL138–141` line refs | `web.run`, `Node REPL` | Yes empty | Curl DNS fail; 30+ web searches; introspection loop; manually stopped at 1 hour+ |
| `GPT-5.3-Codex Low` | 0 curl + web shell | ~900-1,600 | Yes - JS render fail | `†Terms of service: Consumer†www.anthropic.com]` | `web.run`, `curl` | No | Curl returned 0 bytes; web.open partial; offered escalation; 41 s |
| `GPT-5.3-Codex Medium` | 511,402 | ~128K | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `wc`, `tail` | Yes `sc2_messages.html` | Asked curl permission; clean two-path isolation; 57 s |
| `GPT-5.3-Codex High` | 511,822 | ~140K | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `wc`, `tail`, `node` | Yes `sc2_messages.html` | Third ~512K result; gpt-tokenizer attempted; 2m49s |
| `GPT-5.3-Codex Extra High` | 511,821 | ~128-138K | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `wc`, `tail`, `awk`, `multi_tool_use.parallel` | Yes `sc2_messages_response.html` + `sc2_headers.txt` | Headers file saved; CSP nonce + no-store confirmed; methodologically cleanest run; 5m15s |
| `GPT-5.4-Mini Low` | 511,835 | ~128K | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `tail` | No | Most efficient successful run; 57 s; 8% context; no workspace dir |
| `GPT-5.4-Mini Medium` | 1,779 | ~445 | Yes - JS render fail | `L141: *` | `web.run`, `Node REPL` | Yes empty | Curl DNS fail; 142-line L141 tail first confirmed; truncation boundary named; 1m9s |
| `GPT-5.4-Mini High` | 15,299 innerText | ~3,825 | Yes - web.open partial | `Commercial / Terms of service: Consumer / Usage policy` | `web.run`, `tab.goto`, `tab.playwright`, `curl` | Yes empty | First in-app browser use; textContentLength 839,482 confirms JS loads content; 2m43s |
| `GPT-5.4-Mini Extra High` | 511,839 | ~128K | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `node`, `wc`, `tail` | No | 142-line web.open confirmed again; sixth ~512K cluster result; 2m29s |
| `GPT-5.4 Low` | ~4,000-4,500 | ~1,000-1,200 | Yes - JS render fail | `*` | `web.open` | No | No curl; truncation entry point named: after `Messages / API reference`; 1m5s |
| `GPT-5.4 Medium` | 518,974 | ~129,700 | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.open`, `curl`, `wc`, `tail`, `Node REPL` | Yes `sc2-anthropic-messages.html` | Terminal renderer cut at ~120K tokens; display vs retrieval ceiling distinguished; 2m40s |
| `GPT-5.4 High` | 2,423 | ~606 | Yes - web.open partial | `ropic.com] *` | `web.open`, `Node REPL` | Yes empty | No curl attempted; 142-line / L0-L141 confirmed; no mid-line cut stated explicitly; 5m25s |
| `GPT-5.4 Extra High` | 519,723 | ~129,931 | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.open`, `curl`, `wc`, `tail`, `awk`, `multi_tool_use.parallel` | Yes `sc2_anthropic_messages.html` | Loading block mapped L28-L84; highest single-run char count; 2m32s |
| `GPT-5.5 Low` | 518,959 | ~129,740 | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `node` | Yes `anthropic_messages_response.html` | Browser preview screenshot confirms Loading wall visually; saved in Codex IDE not tmp; 1m12s |
| `GPT-5.5 Medium` | 518,959 | ~130,000 | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `curl`, `multi_tool_use.parallel`, `wc`, `tail`, `rg` | No | Bypassed web.open entirely; display truncation vs retrieval truncation distinguished; 1m23s |
| `GPT-5.5 High` | 518,981 | ~129,746 | No - curl complete | `",$L46",null,{}}]}\n"])</script></body></html>` | `web.run`, `curl`, `wc`, `tail`, `perl`, `rg`, `multi_tool_use.parallel` | Yes `anthropic_messages_response.html` | Perl UTF-8 char/byte counting; 0 fences + 0 pre/code tags confirmed; 1m47s |
| `GPT-5.5 Extra High` | 2,423 | ~606 | Yes - web.open partial | `ropic.com] * [43†Usage policy†www.anthropic.com]` | `web.open`, `Node REPL` | No | No curl; line index dump L0-L7 visible; Loading starts L23; codex-browser-use read but empty; 2m59s |

---

### `H1`: Character-based truncation at a fixed ceiling

**Not supported via curl path.** Successful curl fetches returned 511,402-519,723 chars, far above any 10-100 KB ceiling threshold.
The ceiling hypothesis is only consistent with web.open results, where chars ranged ~789-4,500 across runs, but those results
reflect JS-render failure rather than a character ceiling. No run encountered a mid-content character cut on the curl path.

**Combined verdict: `H1` no for `curl` path. Indeterminate for `web.open` path where JS-render failure not distinguished from a ceiling hit.**

---

### `H2`: Token-based truncation at ~2,000 tokens

**Not supported.** Successful curl fetches returned ~128-130K tokens, orders of magnitude above the 2,000-token threshold.
`web.open` results ranged ~198-606 tokens, consistently below 2K, but again reflect JS-render failure not a token gate. No
run approached or hit a 2,000-token ceiling on either path.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

### `H3`: Structure-aware truncation, respects Markdown boundaries

**Partially supported.** The `web.open` extraction window is consistently 141-142 lines across all runs that measured it,
terminating at a named semantic boundary: nav/footer region ending at `Terms and policies → Usage policy`. Run 13 identified
the truncation entry point as `Messages / API reference`, where JS hydration fails. Run 16 mapped the Loading placeholder block
to L28-L84, with nav content at both edges. Run 20 confirmed Loading starts at line 23. These boundaries are structural rather
than arbitrary byte positions. However, the truncation mechanism is ambiguous: the extractor may stop at a fixed line count that
happens to align with the footer boundary, or the footer may be the natural end of available pre-hydration content. True
structure-aware truncation by agent choice wasn't demonstrated. No run encountered truncation in `curl`-fetched content, leaving
Markdown boundary behavior on complete documents untested.

**Combined verdict: `H3` partially supported. Truncation boundary is structurally consistent but mechanism is ambiguous between
fixed line ceiling and JS-hydration limit.**

---

### `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

**Untested for cross-surface comparison.** All 20 runs used the Codex IDE surface exclusively. VS Code-Codex extension comparison
wasn't performed. Within the Codex IDE surface, a meaningful tool-path split confirmed across multiple runs: curl returns ~512K
complete HTML shell, web.open returns 141-142 line partial extraction. This is a retrieval method difference, not a surface difference.
The two-tier network access pattern, sandboxed DNS failure followed by escalated curl success, is consistent across all model families
and constitutes an infrastructure property of the surface.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval method impact confirmed across 12+ runs.**

---

### `H5`: Agent auto-chunks or auto-paginates

**Partially supported as reactive behavior only.** No run demonstrated proactive pagination or automatic chunking. The `GPT-5.2` `Extra High`
hour-long loop with repeated line-by-line metric recomputation constitutes a degenerate pagination attempt, iterating over content in increments
without producing a coherent fetch chain. Agents across multiple runs identified the Loading placeholder pattern and escalated to curl or offered
second-pass retrieval, constituting reactive chunking reasoning. However, no run executed a true multi-segment fetch strategy or divided the
target document into chunks for sequential retrieval.

**Combined verdict: `H5` partially supported as reactive escalation behavior. Proactive auto-pagination not observed in any run.**

---

### Emergent Findings

1. **The  `SC-2` URL is a Next.js client-rendered app shell, making it structurally unsuitable for testing content truncation hypotheses.**
The ~512K curl payload contains nav scaffolding, inline scripts, and JSON data bundles but no readable API reference text. The ~142-line
`web.open` extraction captures a fixed pre-hydration window of nav header, Loading placeholders, and footer. Neither path returns the actual
Messages API documentation body. This is a fundamental retrieval barrier, not a truncation event, and affects all hypotheses that assume
retrievable content.

2. **Two-tier network access architecture confirmed across all LLM variations.** Sandboxed `curl` returns DNS failure or 0 bytes; escalated
`curl` succeeds and returns the full ~512K shell. This pattern appeared in every run that attempted `curl`, spanning `GPT-5.2` through
`GPT-5.5` across all intelligence levels. It is an infrastructure property of the Codex IDE surface independent of model behavior.

3. **The 142-line web.open extraction ceiling is a stable surface property.** Confirmed across Runs 10, 12, 13, 14, 15, 16, and 20 with
consistent line counts of 141-142. The internal structure of this window is: thin nav header before L23, Loading placeholder block from
approximately L23-L84, footer/nav content L84-L141. This is not a model behavior or intelligence-level effect; it is the same regardless
of model family or level.

4. **The nonce-based CSP and no-store cache policy explain why `web.open` can't return hydrated content.** The HTTP/2 301 redirect chain and
response headers confirmed in Run 8 show per-request nonces gating all script execution, combined with `cache-control: no-cache, no-store, must-revalidate`.
The `web.open` extractor receives a fresh shell on every request but can't execute the nonce-gated JS that would hydrate the Loading placeholders.
`curl` bypasses this entirely by not attempting JS execution.

5. **Intelligence level doesn’t automatically improve retrieval quality for this URL.** `GPT-5.2` `High` escaped the JS-render wall via `curl`
and returned the shell. `GPT-5.2` `Extra High` failed `curl` and entered an unrecoverable compute loop for over an hour. `GPT-5.5` `Extra High`
returned only 2,423 chars from web.open despite being the highest intelligence level in its family. The most efficient successful runs were often
`Low` or `Medium` intelligence levels that directly executed `curl` without extended reasoning chains.

6. **Display truncation versus retrieval truncation was first explicitly distinguished in Run 18.** `GPT-5.5` `Medium` reported that the first raw
`curl` output clipped in the terminal display at approximately 120K tokens but the saved file itself was complete. This display-vs-retrieval
distinction is relevant to interpreting all runs where agents reported terminal output as truncated.

7. **The `web.open` surface names its truncation boundary consistently.** Across runs using only `web.open`, agents from different model families
at different intelligence levels converged on the same terminal content: `Terms and policies → Usage policy`. This cross-agent agreement on the
truncation boundary contrasts with Cascade agent behavior on the same URL, where agents couldn't agree on whether truncation had occurred. The
`GPT`-series consensus is a meaningful cross-ecosystem finding.

8. **Workspace persistence creates contamination risk across runs.** Files saved to `/private/tmp` or Codex IDE workspace directories from earlier
runs remained accessible to later runs. The `codex-browser-use` directory read by Runs 19 and 20 was empty, meaning no skill content was available
despite the read attempt. Run 17 saved its HTML to the Codex IDE workspace path referencing the prior session directory `codex-s-web-13`, suggesting
possible workspace reuse rather than fresh fetch.

---

### Log Label Summary

| Agent | Result | Label |
| --------------- | ------- | --------------------------- |
| `GPT-5.2 Low` | Partial | `PARTIAL - JS_render_wall + no_curl + Loading_placeholders` |
| `GPT-5.2 Medium` | Partial | `PARTIAL - JS_render_wall + wordlim_200 + redirect_detected + loop_overhead` |
| `GPT-5.2 High` | Pass | `PASS - curl_escape + DNS_escalated + Next.js_shell_identified` |
| `GPT-5.2 Extra High` | Fail | `FAIL - curl_DNS_fail + introspection_loop + manually_stopped` |
| `GPT-5.3-Codex Low` | Partial | `PARTIAL - curl_0bytes + web_open_partial + escalation_offered_not_executed` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - curl_escalated + clean_two_path + efficient` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_escalated + tokenizer_attempted + third_512K_result` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - headers_saved + CSP_nonce_confirmed + methodologically_cleanest` |
| `GPT-5.4-Mini Low` | Pass | `PASS - curl_escalated + most_efficient + no_workspace_dir` |
| `GPT-5.4-Mini Medium` | Partial | `PARTIAL - curl_DNS_fail + 142_line_ceiling_confirmed + L141_tail` |
| `GPT-5.4-Mini High` | Partial | `PARTIAL - browser_used + innerText_15K + textContent_839K_confirms_JS_loads` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - curl_escalated + 142_line_reconfirmed + sixth_512K_result` |
| `GPT-5.4 Low` | Partial | `PARTIAL - web_open_only + truncation_entry_named + no_curl` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_escalated + display_vs_retrieval_truncation_distinguished` |
| `GPT-5.4 High` | Partial | `PARTIAL - web_open_only + 142_line_confirmed + no_mid_line_cut_stated` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_escalated + Loading_block_mapped_L28_L84 + most_efficient_extra_high` |
| `GPT-5.5 Low` | Pass | `PASS - curl_escalated + browser_preview_screenshot + Loading_wall_visual_confirmed` |
| `GPT-5.5 Medium` | Pass | `PASS - web_open_bypassed + curl_only + display_truncation_distinguished` |
| `GPT-5.5 High` | Pass | `PASS - perl_UTF8_counting + 0_fences_confirmed + 0_pre_code_tags` |
| `GPT-5.5 Extra High` | Partial | `PARTIAL - web_open_only + line_index_dump + Loading_starts_L23 + browser_skill_empty` |
