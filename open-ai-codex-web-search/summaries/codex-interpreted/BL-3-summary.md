# BL-3 Summary

## Test Conditions

|                 | **BL-3**                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------- |
| URL             | `https://www.mongodb.com/docs/atlas/atlas-search/tutorial/`                                  |
| Expected size   | ~250 KB assumed; actual ~3,074,160 chars / 3,103,342 bytes / ~768,500 tokens via valid fetch |
| Surface         | Codex IDE                                                                                    |
| Workspace       | Session-scoped sandbox; persistent artifacts observed across sessions                        |
| Track           | `T1` GPT-interpreted, Codex IDE                                                              |
| Method          | GPT-interpreted                                                                              |
| Runs            | 20                                                                                           |
| Chunks returned | N/A, interpreted track                                                                       |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | ~299,227 chars | ~74,800 | No - curl complete. Yes - web.open limited excerpt | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `functions.write_stdin` | Yes `bl-3.html` in `Documents/Codex` | curl escalation after web.open truncated; saved to Documents/Codex; 1 minute 27 seconds |
| `GPT-5.2 Medium` | ~3,008,491 chars | ~752,000 | No - curl complete. Yes - web.open nav/header only | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command` | No | curl escalation; 3 MB retrieved; 38 seconds |
| `GPT-5.2 High` | ~3,067,800 chars | ~766,950 | No - curl complete. Yes - web.open nav + heading only | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `python3` | No | saved separate headers artifact; 1 minute 39 seconds |
| `GPT-5.2 Extra High` | ~2,998,788 chars / 2,998,838 bytes | ~749,697 | No - curl complete. Yes - web.open windowed | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `mcp__node_repl__.js`, `python3` | No | wrote `bl3_body.bin`; first run to use `.bin` extension; Node REPL for computation; 3 minutes 25 seconds |
| `GPT-5.3-Codex Low` | ~17,000 chars est. | ~4,200 | Yes - web.open L427 of 453 | `03†Security Information] *` | `web.open` via `web.run` | No | curl not invoked; accepted web.open result; 10 seconds |
| `GPT-5.3-Codex Medium` | ~20,000-30,000 chars est. | ~5,000-8,000 | Yes - web.open 453 lines; nav/footer only | `* L450: * L451: L452: © 2026 MongoDB, Inc.` | `web.open` via `web.run` | No | curl not invoked; 453-line cap confirmed; 24 seconds |
| `GPT-5.3-Codex High` | ~3,074,160 chars | ~768,540 | No - curl complete. Yes - web.open 453 lines; nav/footer only | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `xxd` | No | curl escalation returned at High; `bl3_mongo_tutorial.html` written to `/tmp`; 52 seconds |
| `GPT-5.3-Codex Extra High` | ~3,074,160 chars / 3,067,800 bytes | ~768,540 | No - curl complete. Yes - web.open 453 lines | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `rg`, `sed` | Yes `bl3_mongodb_response.html` in `Documents/Codex` | parallel tool calls; most thorough GPT-5.3-Codex run; wrote to Documents/Codex; 2 minutes 50 seconds |
| `GPT-5.4-Mini Low` | ~17,000 chars est. | ~3,500-5,000 | Yes - web.open 453 lines; nav/footer | `© 2026 MongoDB, Inc.` | `web.open` via `web.run`, `sonic_webpage` | No | curl not invoked; incorrectly assessed result as complete; 31 seconds |
| `GPT-5.4-Mini Medium` | ~299,225 chars | ~75,000 | No - curl complete. Yes - web.open visual truncation at L426 | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `node` | No | HTTP 404 response fetched; invalid measurement; 1 minute 23 seconds |
| `GPT-5.4-Mini High` | ~299,225 chars | ~74,800 | No - curl complete. Yes - web.open 453 lines | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `node` | No | HTTP 404 response fetched; agent identified 404 but assessed payload as complete; invalid measurement; 1 minute 43 seconds |
| `GPT-5.4-Mini Extra High` | ~299,225 chars | ~74,806 | No - curl complete. Yes - web.open line-paginated | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | No | HTTP 404 response fetched; paginated web.open follow-up call; Node fetch failed; invalid measurement; 2 minutes 1 second |
| `GPT-5.4 Low` | ~17,000 chars est. | ~4,200 | Yes - web.open 453 lines; nav/footer | `© 2026 MongoDB, Inc.` | `web.open` via `web.run`, `sonic_webpage` | No | curl not invoked; correctly assessed result as incomplete; truncation localized to after `# MongoDB Search Quick Start`; 31 seconds |
| `GPT-5.4 Medium` | ~3,103,342 chars | ~775,000 | No - curl complete. Yes - web.open 453 lines; functionally truncated | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | No | spontaneously noted 3.1 MB vs 250 KB expectation reflects hydrated docs page; 48 seconds |
| `GPT-5.4 High` | ~3,103,292 chars / 3,103,342 bytes | ~780,000-890,000 | No - curl complete. Yes - web.open 453 lines; semantically incomplete | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg` | Yes `bl3_mongodb_tutorial.html` in `Documents/Codex` | wc -m vs wc -c distinction noted; ~15 commands; wrote to Documents/Codex; 3 minutes 6 seconds |
| `GPT-5.4 Extra High` | ~3,103,292 chars | ~776,000 | No - curl complete. Yes - web.open truncation at L385-L389 before tutorial body | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `sed`, `curl -I` | No | re-issued web.open with long response mode; most precisely localized web.open truncation boundary in dataset; 4 minutes 38 seconds |
| `GPT-5.5 Low` | ~3,103,292 chars / 3,103,342 bytes | ~775,823 | No - curl complete. web.open not used | `next_f.push([1,"5:null\n"])</script></body></html>` | `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail` | No | web.open bypassed entirely; curl-first without web.open attempt; 30 seconds |
| `GPT-5.5 Medium` | ~3,102,296 chars / 3,102,346 bytes | ~775,600 | No - curl complete. Yes - web.open 453 lines; incomplete | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `file`, `rg` | No | zsh backtick quoting error with rg; multi_tool_use.parallel for measurement; 47 seconds |
| `GPT-5.5 High` | ~3,102,296 chars / 3,102,346 bytes | ~775,574 | No - curl complete. Yes - web.open 453 lines; semantically incomplete | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `rg`, `python3` | No | zsh backtick quoting error with rg; Deployment Type / Interface selector identified as truncation boundary; 1 minute 24 seconds |
| `GPT-5.5 Extra High` | ~3,102,296 chars / 3,102,346 bytes | ~775,574 | No - curl complete. Yes - web.open 453 lines; reduced rendered-text extraction | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `multi_tool_use.parallel`, `curl`, `wc`, `tail`, `xxd`, `node`, `head` | No | gzip-encoded response; Netlify Edge cache hit; node JSON metrics output; zsh backtick quoting error; 1 minute 50 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported via the `curl` path. Successful `curl` fetches returned approximately 3.1 million chars consistently across all valid runs that used `curl`,
far above any 10-100 KB ceiling threshold. Runs relying solely on `web.open` returned approximately 17,000-30,000 chars consistent with a fixed 453-line
viewport window rather than a character ceiling. Three `GPT-5.4-Mini` runs fetched an HTTP `404` error page of approximately 299 KB, which superficially
resembles a ceiling but is an invalid measurement against the `BL-3` target URL. The `GPT-5.2 Low` run retrieved approximately 299 KB via `curl`, which
the `404` pattern in later runs suggests may have been a redirect failure rather than a truncation ceiling, though this isn't confirmed.

**Combined verdict: `H1` no for the `curl` path on valid fetches. Partially consistent with the `web.open` path where the window is line-count-bound at
453 lines rather than character-bound. The 299 KB `GPT-5.2 Low` result and all three `GPT-5.4-Mini` curl results flagged as potentially invalid, don't
use as ceiling evidence.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Successful `curl` fetches returned approximately 768,000-776,000 tokens consistently, well above the 2,000-token threshold. `web.open` windowe
results ranged from approximately 3,500-8,000 tokens in `Low` and `Medium` runs that didn't escalate to `curl`. No run approached or hit a 2,000-token ceiling
on either retrieval path.

**Combined verdict: `H2` no. Token ceiling not a factor on either retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported as a confirmed mechanism, though cross-run evidence points to a consistent structural gap rather than a random byte cutoff. The `web.open` tool
consistently surfaces a 453-line rendered text extraction consisting of navigation, page shell, a UI selector widget around a Deployment Type / Interface element,
and footer content. The actual tutorial body is absent in every run regardless of LLM version or intelligence level. Runs 13 and 16 independently localized the
content gap to after the `# MongoDB Search Quick Start` heading and around lines `L385-L389`, where the page transitions from the selector widget to footer
navigation. This is consistent with the tutorial body being JS-rendered and absent from the static server-side extraction rather than with boundary-aware truncation
logic. No `curl` response showed structure-aware truncation.

**Combined verdict: `H3` indeterminate. The `web.open` extraction omits the tutorial body at a consistent structural position, but this appears to be a rendering
artifact of the Next.js / Gatsby JS architecture rather than deliberate Markdown-boundary truncation. The cut point is reproducible and structurally meaningful but
not evidence of boundary detection.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively. VS Code-Codex extension comparison not performed. Within the Codex IDE
surface, a consistent two-tier network access pattern confirmed across all runs: sandboxed DNS resolution failure followed by escalated `curl` success after permission
approval. This infrastructure constraint is surface-level rather than LLM-level and applied uniformly regardless of LLM version or intelligence level.

**Combined verdict: `H4` untested for its stated cross-surface scope. Within-surface retrieval infrastructure behavior confirmed consistent across all 20 runs.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported, with meaningful variation by LLM version and intelligence level. No run executed proactive chunking before encountering a truncation or incompleteness
signal. `GPT-5.2` through `GPT-5.4` runs consistently used `web.open` as the first retrieval step and escalated to `curl` at `Medium` intelligence level and above upon
recognizing the result was incomplete. `GPT-5.3-Codex Low` and `Medium` didn't escalate regardless of recognized incompleteness. `GPT-5.4 Low` was the first `Low`-tier run
to escalate, though it accepted a truncated `web.open` result without escalating. `GPT-5.5 Low` bypassed `web.open` entirely and issued `curl` directly without encountering
a truncation signal first, representing a strategy shift rather than reactive escalation. No run used chunked or paginated `curl` requests against the target URL.

**Combined verdict: `H5` partially supported. Reactive escalation from `web.open` to `curl` is the dominant pattern from `GPT-5.2` through `GPT-5.4`. Proactive auto-pagination
not observed. `GPT-5.5 Low` represents the first instance of curl-first retrieval without a prior truncation signal, consistent with a LLM-level strategy shift rather than
intelligence-level escalation.**

---

## Emergent Findings

1. **`web.open` 453-line ceiling is consistent across all LLM versions and intelligence levels for this URL.** Every run that used `web.open` received a 453-line rendered
text extraction regardless of LLM version, intelligence level, or whether `curl` was subsequently used. This is a platform-level constraint on the `web.open` tool for this
page, not a LLM behavior.

2. **`web.open` extraction omits the tutorial body at a reproducible structural position.** The extraction surfaces navigation, page shell, a Deployment Type / Interface UI
selector widget around lines L385-L389, and footer content. The actual tutorial walkthrough is absent in every run. This is consistent with the tutorial body being client-side
rendered via Next.js / Gatsby JS and not present in the static server HTML that `web.open` extracts.

3. **`curl` is the reliable full-document retrieval path.** Runs using `curl` with escalated network access consistently returned approximately 3.1 million chars. Runs relying
solely on `web.open` never retrieved the tutorial body. The decision to use `curl` was the single strongest predictor of retrieval success, regardless of LLM version or
intelligence level.

4. **`GPT-5.4-Mini` produced HTTP `404` responses in three of four `curl` runs.** `Medium`, `High`, and `Extra High` `GPT-5.4-Mini` runs fetched a 299 KB error page rather than
the tutorial. The `set-cookie: originalRequest=http%3A%2F%2F...` header in the `404` responses indicates an HTTP to HTTPS redirect failure. `GPT-5.4-Mini Low` didn't use `curl`
at all. This pattern doesn't appear in any other LLM variant at the same point in the test cycle. The target URL confirmed to experience a temporary outage after testing concluded
making it plausible that these runs occurred during a instability window rather than reflecting a LLM-specific URL handling deficiency, cause unresolved. All three affected runs
flagged as invalid for `H1` and `H2` measurement purposes regardless of cause.

5. **`GPT-5.2 Low` retrieved approximately 299 KB rather than the expected 3.1 MB.** The `404` pattern in later `GPT-5.4-Mini` runs and the confirmed temporary outage of the target
URL offer a plausible explanation: this run may have fetched the page during a server instability window, with the CDN returning a cached error response rather than the tutorial.
The differing `etag` values across runs confirm the CDN served at least three distinct cached versions during the test cycle, making per-run response consistency unreliable. Treat
the `GPT-5.2 Low` result with caution for `H1` and `H2` comparisons.

6. **Intelligence level doesn't reliably predict retrieval quality within an LLM version.** `GPT-5.5 Low` retrieved the full document in 30 seconds using 8 percent context by
bypassing `web.open` entirely. `GPT-5.3-Codex Medium` didn't escalate to `curl` despite recognizing the `web.open` result as incomplete. `GPT-5.4-Mini High` fetched a `404` page
and assessed it as complete. The most consequential behavioral differences are LLM-version-level, not intelligence-level.

7. **`GPT-5.5` shows convergence toward `curl`-first behavior.** `GPT-5.5 Low` bypassed `web.open` entirely. `GPT-5.5 Medium` and `High` used `web.open` only as an initial check
before immediately escalating to `curl`. `GPT-5.5 Extra High` used `web.open` for initial inspection before switching to `curl`. All `GPT-5.5` runs produced valid complete fetches.
This mirrors the `curl`-first convergence observed in `OP-4` for the same LLM version group.

8. **`multi_tool_use.parallel` appears in `GPT-5.4 Extra High` and all `GPT-5.5` runs.** This parallel tool invocation pattern not observed in `GPT-5.2` or `GPT-5.3-Codex` runs
and appears to be a capability introduced at the `GPT-5.4 Extra High` level or with `GPT-5.5` across all intelligence levels.

9. **Reproducible `zsh` backtick quoting error with `rg` appears in `GPT-5.5 Medium`, `High`, and `Extra High` runs.** The pattern `rg -n "</html>|``` "` consistently fails with
`zsh:1: unmatched "` across three consecutive `GPT-5.5` runs. This is a shell environment consistency issue in the Codex IDE sandbox rather than a LLM reasoning failure, but it
affected structural verification steps in all three runs.

10. **Higher intelligence levels consistently produced more thorough measurement and verification behavior.** `GPT-5.2 Extra High` used Python for character counting and saved
a separate headers artifact. `GPT-5.4 Extra High` re-issued `web.open` with a long response mode and localized the truncation boundary to `L385-L389`. `GPT-5.5 Extra High` used
`xxd` for binary inspection and Node.js for JSON metrics output including chars, codeUnits, bytes, words, and endsWithHtml. This depth of verification didn't affect the final
retrieved payload size but is relevant to metacognitive accuracy assessment.

11. **Metacognitive accuracy varied significantly across runs.** `GPT-5.4-Mini Low` incorrectly assessed the 453-line `web.open` result as complete full page content.
`GPT-5.4-Mini High` correctly identified an HTTP `404` status but then assessed the `404` payload as a complete document. `GPT-5.4 Low` correctly identified incompleteness and
localized the truncation boundary. `GPT-5.4 Medium` spontaneously noted the discrepancy between the expected 250 KB and the actual 3.1 MB and correctly attributed it to page
hydration. Metacognitive accuracy appears correlated with LLM version more than intelligence level.

12. **The `BL-3` target URL is a Next.js / Netlify / CloudFront stack with gzip encoding and CDN caching.** Headers across runs confirmed this architecture consistently. The
`netlify-vary` header indicates that request headers including `rsc`, `next-router-*`, and `accept-encoding` would produce different responses, which is relevant for any future
test variant using modified request headers. The tutorial body is client-side rendered and isn't present in the static server HTML payload regardless of how completely that payload
retrieved.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.2 Low` | Partial | `PARTIAL - curl_299KB_anomaly + web_open_nav_only + escalated_curl + CONTAM_RISK: 299KB_vs_3MB` |
| `GPT-5.2 Medium` | Pass | `PASS - curl_3MB_complete + web_open_nav_only + 38s + CONTAM_RISK: bl3.html_shared_name` |
| `GPT-5.2 High` | Pass | `PASS - curl_3MB_complete + headers_artifact_saved + web_open_nav_only + 1m39s + CONTAM_RISK: mongodb-atlas-search-tutorial.html_shared_name` |
| `GPT-5.2 Extra High` | Pass | `PASS - curl_3MB_complete + bin_extension + Node_REPL + parallel_calls + 3m25s + CONTAM_RISK: bl3_body.bin_unique_name` |
| `GPT-5.3-Codex Low` | Partial | `PARTIAL - web_open_only + 453_line_ceiling + curl_not_invoked + 10s` |
| `GPT-5.3-Codex Medium` | Partial | `PARTIAL - web_open_only + 453_line_ceiling + curl_not_invoked + 24s` |
| `GPT-5.3-Codex High` | Pass | `PASS - curl_3MB_complete + escalation_returned_at_High + web_open_453_ceiling + 52s + CONTAM_RISK: bl3_mongo_tutorial.html_shared_name` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - curl_3MB_complete + parallel_tool_calls + Documents_Codex_write + 2m50s + CONTAM_RISK: bl3_mongodb_response.html_shared_name` |
| `GPT-5.4-Mini Low` | Partial | `PARTIAL - web_open_only + 453_line_ceiling + curl_not_invoked + incorrect_completeness_assessment + 31s` |
| `GPT-5.4-Mini Medium` | Invalid | `INVALID - HTTP_404_fetched + 299KB_error_page + redirect_failure + web_open_426_of_453 + CONTAM_RISK: mongo_page.html_shared_name` |
| `GPT-5.4-Mini High` | Invalid | `INVALID - HTTP_404_fetched + 299KB_error_page + 404_identified_but_dismissed + metacognitive_failure + CONTAM_RISK: mongo-atlas-search-tutorial.html_shared_name` |
| `GPT-5.4-Mini Extra High` | Invalid | `INVALID - HTTP_404_fetched + 299KB_error_page + paginated_web_open + Node_fetch_failed` |
| `GPT-5.4 Low` | Partial | `PARTIAL - web_open_only + 453_line_ceiling + curl_not_invoked + correct_incompleteness_assessment + truncation_localized_to_MongoDB_Search_Quick_Start` |
| `GPT-5.4 Medium` | Pass | `PASS - curl_3MB_complete + web_open_453_ceiling + hydration_discrepancy_noted + 48s + CONTAM_RISK: bl3_mongodb_tutorial.html_shared_name` |
| `GPT-5.4 High` | Pass | `PASS - curl_3MB_complete + Documents_Codex_write + wc_m_vs_wc_c_noted + 3m6s + CONTAM_RISK: bl3_mongodb_tutorial.html_shared_name` |
| `GPT-5.4 Extra High` | Pass | `PASS - curl_3MB_complete + L385_L389_boundary_localized + web_open_long_mode_retry + 4m38s + CONTAM_RISK: bl3_headers.txt_shared_name` |
| `GPT-5.5 Low` | Pass | `PASS - curl_only + web_open_bypassed + 30s + 8pct_context + CONTAM_RISK: bl3_response.html_shared_name` |
| `GPT-5.5 Medium` | Pass | `PASS - curl_3MB_complete + web_open_453_ceiling + zsh_rg_quoting_error + parallel_calls + 47s + CONTAM_RISK: bl3_mongodb_tutorial.html_shared_name` |
| `GPT-5.5 High` | Pass | `PASS - curl_3MB_complete + Deployment_Type_boundary_localized + zsh_rg_quoting_error + 1m24s + CONTAM_RISK: bl3_mongodb_tutorial.html_shared_name` |
| `GPT-5.5 Extra High` | Pass | `PASS - curl_3MB_complete + gzip_encoded + Netlify_Edge_cache_hit + node_JSON_metrics + zsh_rg_quoting_error + 1m50s + CONTAM_RISK: bl3_response.html_shared_name + bl3_headers.txt_shared_name` |
