# BL-3 Summary

## Test Conditions

|                 | **BL-3** |
| --------------- | -------- |
| URL             | `https://www.mongodb.com/docs/vector-search/tutorials/quick-start/?deployment-type=atlas&interface=atlas-ui&embedding=auto` |
| Expected size   | `~4531KB` per test prompt; `curl` and `python3` escalated retrieval across runs ranged from `4,640,208` to `4,848,853` chars, no single stable value confirmed |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/private/tmp` writable; project accessible as working directory |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.5`, `GPT-5.4-Mini` |
| Runs            | 8 |
| Chunks returned | N/A |

This URL replaces `BL-3`'s original `T1` target, retired after MongoDB restructured its Atlas Search docs. The replacement introduces a multi-parameter query string and a page roughly
800 times larger than `BL-2`'s reference document, making this run set as much a stress test of retrieval at scale as a test of query parameter handling.

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Low` | `149`, error text only | `~38` | No body to truncate | `tlas&embedding=auto&interface=atlas-ui: Cache miss` | `web.run`, `curl`, `node` | No | `web.run` returned cache miss; `curl` failed DNS resolution and wasn't retried with elevated permission; no page body was ever retrieved; `node` used locally only to measure the error text; named `Test web retrieval behavior`; 22 seconds |
| `GPT-5.4-Mini Medium` | `4,640,208` | `~1.16M` | No | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.open`, `web.search_query`, `curl`, `wc`, `node` | Yes | `web.open` returned cache miss; sandboxed `curl` failed DNS, permission-escalated fetch succeeded; saved to `/private/tmp/mongo-doc.XXXXXX.html`; byte count `4,640,388` against char count `4,640,208`, a 180 unit gap consistent with multi-byte characters; asked permission for `curl` twice and `node` twice; named `Test web retrieval`; 1 minute 40 seconds |
| `GPT-5.4-Mini High` | `~60,000`, `web.open` extract on a substituted URL | `~15,000` | Implicit, not flagged as truncation | `L446: * Learning Summary\nL447: * Next Steps` | `web.open`, `curl`, `mcp__node_repl`, `turn2view0`, `turn3view0` | No | the query parameter URL returned cache miss on `web.open`, DNS failure on `curl`, and a fetch failure on `mcp__node_repl`; the agent silently substituted the canonical URL without query parameters, so this run's metrics don't reflect the actual target URL; reported "no obvious truncation" despite the extract ending cleanly at a line boundary, `L447`; named `Test web retrieval behavior`; 2 minutes 29 seconds |
| `GPT-5.4-Mini Extra High` | `4,676,652` | `~1,169,163` | No | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.open`, `mcp__node_repl.js`, `python3` | No | `web.open` returned cache miss; `mcp__node_repl.js` fetch failed; a `python3` syntax error was corrected and the retry succeeded on the exact target URL; only run in the full set to retrieve content without `curl`; asked permission for `python3` twice; named `Test web retrieval`; 2 minutes 53 seconds |
| `GPT-5.5 Low` | `4,848,853` | `~1.21M` | Mixed, saved file no, terminal display yes | `next_f.push([1,"5:null\n"])</script></body></html>` | `web`, `curl`, `wc`, `tail`, `file`, `rg`, `sort`, `uniq` | Yes | `web` returned cache miss; an unsaved `curl` attempt was clipped mid stream by the terminal display, a separate truncation event from the saved file; escalated `curl -o` saved the complete body to `/private/tmp/bl-3-mongodb.html`; file verified directly at `4,849,033` bytes, `4,848,853` chars, single `</html>` close; first confirmed double rendering of the output report on a non `Mini` model in `T2`; asked permission for `curl` twice; named `Test web retrieval behavior`; 1 minute 7 seconds |
| `GPT-5.5 Medium` | `4,848,853` | `~1,212,213` | No | `next_f.push([1,"5:null\n"])</script></body></html>` | `curl`, `wc`, `tail`, `file`, `rg` | Yes | bypassed `web` entirely, the first `BL-3` run to do so; sandboxed `curl` failed DNS, escalated `curl -o` succeeded and saved to `/private/tmp/bl-3-response.txt`; byte count identical to `GPT-5.5 Low`; asked permission for `curl` only once, fewer requests than usual; double rendering continued; named `Test web retrieval`; 45 seconds |
| `GPT-5.5 High` | `4,848,853` | `~1.21M` | No | `next_f.push([1,"5:null\n"])</script></body></html>` | `curl`, `wc`, `tail` | No | bypassed `web` entirely again; sandboxed `curl` failed DNS, escalated fetch succeeded; the leanest `BL-3` run, only 3 commands despite `High` reasoning; byte count matched `GPT-5.5 Low` and `GPT-5.5 Medium` for a third consecutive run; asked permission for `curl` only once; double rendering continued; named `Test web retrieval BL-3`; 46 seconds |
| `GPT-5.5 Extra High` | `4,724,953` | `~1,181,239` to `~1.35M` | No | `next_f.push([1,"5:null\n"])</script></body></html>` | `web.run`, `open`, `curl`, `wc`, `tail`, `node`, `rg` | Yes | `web.run` with `open` returned cache miss; sandboxed `curl` failed DNS, escalated `curl` with `-D` for headers and `-o` for body succeeded; wrote `/private/tmp/bl3_headers.txt`, `/private/tmp/bl3_response`, and `/private/tmp/bl3_response.html`, the latter two confirmed byte-for-byte identical; the only run to capture HTTP headers, confirming `200` status and a Netlify Edge cache hit at `age: 867`; char count about `124,000` lower than the three prior `GPT-5.5` runs, explained by the differing cache snapshot age rather than a retrieval problem; ran the most rigorous structural check of the set, with explicit `hasTruncatedWord: false` and `hasOmittedMarker: false`; asked permission for `curl` once; named `Fetch MongoDB docs response`; 2 minutes 32 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

`BL-3` can evaluate this hypothesis where `BL-2` couldn't. At `4.5` to `4.85` million characters per successful fetch, the page is large enough to stress a proposed
 `10` to `100 KB` ceiling many times over, and no run hit one. Six runs escalated past the `web` tool to a raw HTTP fetch via `curl` or `python3`, and all six returned
 the complete multi-megabyte body with no cutoff.

`GPT-5.4-Mini High`'s `~60,000` character `web.open` extract falls inside the hypothesized range, but per the Truncation Taxonomy's layer separation, `web` output
measures the Viewer Window layer, not the HTTP Response Body, and that run also substituted a different URL than the target. It's excluded from the formal verdict and
logged as a Viewer Window observation instead.

**Combined verdict: `H1` no. Six runs retrieved `4.6` to `4.85` million characters with no truncation at any point near the proposed ceiling, the strongest direct evidence against `H1` collected to date.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Same outcome as `H1`. Every curl-escalated run returned an estimated token count between roughly `1.16` million and `1.21` million, several orders of magnitude past
the proposed `2,000` token threshold, with no truncation observed. `GPT-5.4-Mini High`'s `web.open` extract alone came in around `~15,000` tokens, also well past the
threshold, though it's excluded from the formal verdict for the same Viewer Window and URL substitution reasons as `H1`.

**Combined verdict: `H2` no. No truncation occurred anywhere near a `2,000` token ceiling across any escalated run.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Two genuine truncation events occurred across the 8 runs, at two different taxonomy layers, with conflicting signal.

`GPT-5.4-Mini High`'s `web.open` extract cut off cleanly at `L447: * Next Steps`, a heading and list item boundary rather than a mid-word or mid-sentence position.
That's consistent with structure-aware behavior at the Viewer Window layer, though weakened by both the agent's failure to recognize it as truncation at all and the
underlying URL substitution.

`GPT-5.5 Low`'s unsaved `curl` stdout clipped mid-CSS, inside a `@media` query, by the terminal display. That's an arbitrary position with no structural alignment,
evidence against structure-aware truncation at the Terminal Display layer.

No truncation occurred at the HTTP Response Body layer in any of the 8 runs, so that layer offers no boundary evidence either way.

**Combined verdict: `H3` partially. One layer shows a boundary-aligned cutoff, one layer shows an arbitrary cutoff, and the layer that matters most for retrieval ceiling
testing never truncated at all. The mixed signal doesn't confirm or rule out structure-aware truncation.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Untested by design. The original `T1` target for `BL-3` was retired when MongoDB restructured its Atlas Search docs, so no `T1` baseline exists for this replacement URL.
Unlike `BL-2`, where a char count comparison against `T1` was at least possible, `BL-3` has no comparable `T1` run to set against any `T2` result.

**Combined verdict: `H4` untested. No `T1` baseline exists for this URL, ruling out comparison by design rather than by data quality.**

---

## `H5`: Agent auto-chunks or auto-paginates

Not supported. Every run that successfully retrieved the page did so in a single `curl` or `python3` call, pulling the full multi-megabyte body in one shot. Multi-step tool
chains appeared in all 8 runs, but they served failure recovery and measurement, `web` cache miss, sandboxed DNS failure, escalated retry, then `wc`, `tail`, `file`, or `node`
verification passes, not chunked or paginated content retrieval.

**Combined verdict: `H5` no. Single-fetch retrieval once a working method found, across all runs that retrieved content. Multi-step chains reflect reactive recovery from tool
failures, not auto-chunking.**

---

## Emergent Findings

1. **Replacement URL functions as a stress test in three different ways at once.** It carries a multi-parameter query string, a page roughly 800 times larger than `BL-2`'s
reference document, and zero `T1` baseline to compare against. `BL-3` `T2` data answers different questions than `BL-3` `T1` did, not just the surface question.

2. **Target URL returned a `web` cache miss in every single run.** All 8 runs hit a one-line `Cache miss` failure on the exact query parameter URL via `web.run` or
`web.open`, a 100 percent failure rate for the built-in web tool against this URL pattern. No run examined or diagnosed the cause; every run named the failure in passing
and pivoted directly to shell-level retrieval.

3. **Two-tier sandboxed and escalated network pattern held across every run that attempted a direct fetch.** First `curl` or `python3` attempt failed with a DNS resolution
error inside the sandbox; a permission-escalated retry then succeeded. This mirrors the same pattern documented in `BL-2`.

4. **`GPT-5.4-Mini High` is the only run whose retrieval evidence doesn't reflect the actual target URL.** After the query parameter URL failed across three tools, the agent
silently substituted the canonical URL without query parameters and reported size and truncation metrics as though they answered the `BL-3` question. They don't, and this
run's `H1` through `H3` contributions are accordingly weaker than the other 7.

5. **Page size varied meaningfully between runs that did retrieve the actual target URL.** `GPT-5.4-Mini Medium` and `GPT-5.4-Mini Extra High` differed by about `36,000`
characters on the identical URL. `GPT-5.5 Low`, `Medium`, and `High` returned an identical `4,848,853` characters three runs in a row, then `GPT-5.5 Extra High` came in about
`124,000` characters lower. `Extra High`'s captured headers explain the gap as a different cache snapshot age rather than a retrieval problem, but it means this page not
treated as a fixed-size baseline the way `BL-2`'s `5,805` char document could.

6. **Only one run captured HTTP response headers.** `GPT-5.5 Extra High` confirmed a clean `200` status, a Netlify Edge cache hit at `age: 867`, and a CloudFront pass-through
miss in front of it, along with the `Next.js` and `istio-envoy` server stack. This is the only run with header-level confirmation against the Truncation Taxonomy's
"Wrong Resource Returned" layer for `BL-3`. No other run performed independent header inspection.

7. **`curl` functioned as the reliable default escalation path, not a last resort.** `GPT-5.5 Extra High` explicitly framed its own result as "retrieval behavior under failure
conditions," then used `curl` to retrieve the complete `4.7` million character page in the same turn. Across the full run set, `curl` succeeded in 6 of 8 runs, with `python3`
succeeding once and only `GPT-5.4-Mini Low` never retrieving a body at all. The "failure conditions" framing undersells how consistently the shell-level escalation resolves
the `web` tool's limitation.

8. **Two distinct truncation events surfaced, and neither sat at the HTTP Response Body layer.** `GPT-5.4-Mini High`'s `web.open` extract showed a Viewer Window cutoff at a
structural boundary. `GPT-5.5 Low`'s unsaved `curl` stdout showed a Terminal Display cutoff at an arbitrary position. Disambiguating these by layer, per the Truncation Taxonomy,
was necessary to assess `H3` meaningfully for this test ID.

9. **Artifact creation was inconsistent across the 8 runs.** No artifact appeared in `GPT-5.4-Mini Low`, `GPT-5.4-Mini High`, `GPT-5.4-Mini Extra High`, or `GPT-5.5 High`. A
single saved file appeared in `GPT-5.4-Mini Medium`, `GPT-5.5 Low`, and `GPT-5.5 Medium`. `GPT-5.5 Extra High` produced three files, including a byte-for-byte duplicate pair,
`bl3_response` and `bl3_response.html`, with no file extension distinguishing them functionally. Total artifact count across the set is 6, all in `/private/tmp`.

10. **No run wrote an artifact to the project workspace, despite most runs verbally confirming workspace access.** Every run except `GPT-5.4-Mini Extra High` named the project
path, `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing`, directly in its surface awareness answer, yet all 6 saved files landed in the session-scoped `/private/tmp`
instead. Stated capability and used capability diverged consistently.

11. **`web`-first behavior wasn't consistent within `GPT-5.5`.** `GPT-5.5 Low` and `GPT-5.5 Extra High` attempted `web` before escalating. `GPT-5.5 Medium` and `GPT-5.5 High`
bypassed `web` entirely and went straight to `curl`. The split doesn't track cleanly with intelligence level or with the `GPT-5.4-Mini` runs, which used `web.open` first in all
4 cases.

12. **Double rendering extended to `GPT-5.5` within `T2` `BL-3`.** First confirmed on a non `Mini` model in `GPT-5.5 Low`, then continuing in `GPT-5.5 Medium` and `GPT-5.5 High`.
Consistent with the existing `T2` double rendering pattern, no new handling required beyond the established methodology of treating runtime capture as the primary record.

13. **Byte and character counts diverged by a consistent margin whenever both were measured on a full fetch.** `GPT-5.4-Mini Medium` showed a 180 unit gap between `wc -c` and the
saved character count; `GPT-5.5 Low` and `GPT-5.5 Medium` showed the identical 180 unit gap on what appears to be the same cached page snapshot. Likely reflects multi-byte
UTF-8 characters in the source page rather than a measurement inconsistency, but worth tracking if the gap ever shifts on a future run.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Fail | `FAIL, fail_reason_no_content_retrieved + web_run_cache_miss + curl_dns_failure_not_retried + no_body_retrieved + node_error_text_measured + 22 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_open_cache_miss + curl_4640208_chars + byte_char_180_gap + mongo_doc_html_private_tmp + 1 minute 40 seconds` |
| `GPT-5.4-Mini High` | Fail | `FAIL, fail_reason_wrong_resource_undisclosed + web_open_cache_miss + curl_dns_failure + mcp_node_repl_fetch_failed + url_substituted_canonical + web_open_60000_char_extract + implicit_truncation_L447 + 2 minutes 29 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, web_open_cache_miss + mcp_node_repl_fetch_failed + python3_urllib_4676652_chars + no_curl_used + target_url_match + 2 minutes 53 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, web_cache_miss + curl_4848853_chars + terminal_display_truncation + saved_file_no_truncation + double_rendering_first_non_mini + bl_3_mongodb_html_private_tmp + 1 minute 7 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, web_bypassed + curl_4848853_chars + identical_size_to_low_run + bl_3_response_txt_private_tmp + double_rendering + 45 seconds` |
| `GPT-5.5 High` | Pass | `PASS, web_bypassed + curl_4848853_chars + identical_size_third_match + leanest_run_3_commands + no_artifact + double_rendering + 46 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_open_cache_miss + curl_headers_captured + curl_4724953_chars + http_200_netlify_edge_hit + duplicate_response_files + three_artifacts_private_tmp + 2 minutes 32 seconds` |

>`GPT-5.4-Mini Low` fails for retrieving no document content at any point in the run.
>`GPT-5.4-Mini High` fails for silently substituting a different URL after the target URL failed across three tools, then reporting metrics against that substitution without disclosing the swap as a deviation from the test target.
>The remaining 6 runs pass on the same basis `BL-2`'s runs did: each escalated past an initial `web` failure and returned verified content from the actual target URL.
