## BL-2 GPT-interpreted Track Summary

### Test Conditions

|                 | **BL-2**                                                                        |
| --------------- | ------------------------------------------------------------------------------- |
| URL             | `https://www.mongodb.com/docs/manual/reference/change-events/create.md`         |
| Expected size   | ~20 KB assumed; actual 6,024 chars / ~1,500 tokens                              |
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
| `GPT-5.2 Low` | 95 error | ~24 | N/A fetch fail | `change-events/create.md: (400) OK` | `web.open`, `web.search_query`, `Node REPL` | Yes empty | 400 fetch failure; no curl attempt; 22 s |
| `GPT-5.2 Medium` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `curl`, `wc`, `tail`, `python3` | Yes HTML file saved | curl escalation; saved `.html` file unprompted; 1m39s |
| `GPT-5.2 High` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `curl`, `wc`, `tail`, `python3`, `tiktoken attempt` | Yes `.md` file saved | curl escalation; saved `.md` file; tiktoken import failed; 1m59s |
| `GPT-5.2 Extra High` | 6,024 | ~1,506 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `curl`, `wc`, `head`, `tail`, `python3` | Yes `.md` file saved | Header inspection via `curl -I`; pre-permission curl execution; 4m49s |
| `GPT-5.3-Codex Low` | 95 error | ~24 | N/A fetch fail | `change-events/create.md: (400) OK` | `web.open`, `web.search_query`, `Node REPL` | Yes empty | Near-identical to GPT-5.2 Low; 13 s |
| `GPT-5.3-Codex Medium` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `curl`, `wc`, `tail` | Yes empty | Fastest successful run; 50 s; Markdown-formatted output |
| `GPT-5.3-Codex High` | 6,022 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `curl -iL`, `wc`, `tail`, `python3` | Yes empty | First `curl -iL` combined header+body fetch; 2-byte variance noted; 1m10s |
| `GPT-5.3-Codex Extra High` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `curl`, `wc`, `tail`, `sed`, `rg`, `multi_tool_use.parallel` | Yes empty | Parallel tool execution; 13 commands; 4 searches; 1m57s |
| `GPT-5.4-Mini Low` | N/A rendered | ~2,000-2,300 | Yes partial | trailing nav/footer chrome | `web.run`, `web.search_query`, `web.find`, `curl` | Yes empty | First truncation report; curl DNS fail; rendered page view not raw; 23 s |
| `GPT-5.4-Mini Medium` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.run`, `curl`, `wc`, `tail`, `Node REPL` | Yes `/private/tmp` | Sandboxed curl 0 bytes then escalated; 59 s |
| `GPT-5.4-Mini High` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.run`, `curl`, `Node REPL`, `od`, `tail` | Yes `/private/tmp` | `od -An -t x1 -c` hex dump for tail verification; shell-quoting error self-corrected; 1m45s |
| `GPT-5.4-Mini Extra High` | 6,024 | ~1,400 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.run`, `web.search_query`, `web.find`, `curl`, `Node REPL`, `Browser Use attempt` | Yes `/private/tmp` | Browser Use attempt unique to this run; `net::ERR_BLOCKED_BY_CLIENT`; 4m36s; 63K context |
| `GPT-5.4 Low` | 95 error then 6,024 | ~1,500 | Yes reported false positive | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `curl`, `wc`, `tail`, `sed`, `rg` | Yes `/private/tmp` | False truncation report based on size expectation vs actual; 1m8s |
| `GPT-5.4 Medium` | 95 error | ~24 | N/A fetch fail | `change-events/create.md: (400) OK` | `web.open`, `web.search_query`, `Node REPL` | Yes workspace path mismatch | Regression to Low-tier behavior; workspace path from prior session; 35 s |
| `GPT-5.4 High` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.open`, `web.search_query`, `web.open on result`, `web.find`, `curl`, `wc`, `tail`, `rg`, `sed` | Yes `bl2_create.md` | Explicit surface-split report; internal tool IDs visible; 2m11s |
| `GPT-5.4 Extra High` | 6,024 | ~1,506 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.run`, `curl`, `wc`, `tail`, `sed`, `rg`, `file`, `Node REPL` | Yes `bl2_mongodb_create.md` + `bl2_headers.txt` | Headers file saved; `cache-status: Netlify Edge fwd=stale`; CDN layer confirmed; 2m34s |
| `GPT-5.5 Low` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.run`, `curl`, `python3` | Yes `/tmp/bl-2-create.md` | Two-tier curl documented explicitly; size caveat noted; 55 s |
| `GPT-5.5 Medium` | 6,024 | 1,506-1,629 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `web.run`, `curl`, `Node REPL`, `wc`, `tail` | Yes `bl-2-create.md` | HTML tag inventory counted; first token range estimate; 1m2s |
| `GPT-5.5 High` | 6,024 | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `curl`, `wc`, `tail`, `file`, `awk`, `cmp`, `sed`, `rg` | Yes `bl2_create.md` | Skipped `web.open` entirely; possible workspace read masquerading as fresh fetch; 1m40s |
| `GPT-5.5 Extra High` | 6,024 decompressed | ~1,500 | No | `, "key": { _id: 1 }, "name": "_id_" }` | `curl --compressed`, `perl`, `wc`, `tail`, `file`, `node`, `python3`, `multi_tool_use.parallel` | Yes `/private/tmp` | `content-encoding: gzip` confirmed; `age: 0` fresh CDN hit; perl regex against possibly nonexistent file; 4m51s |

---

### `H1`: Character-based truncation at a fixed ceiling

**Not supported for this URL.** The BL-2 source document is 6,024 chars / ~1,500 tokens, well below any plausible ceiling threshold. No run
encountered a character-based ceiling. Runs that reported truncation did so based on size expectation mismatch vs the known ~20KB estimate, not
evidence of a mid-content cut. The true document size was consistently confirmed at 6,024 chars across all successful retrievals regardless of
model or intelligence level.

**Combined verdict: `H1` indeterminate. Document too small to test any ceiling. No ceiling pressure observed across 20 runs.**

---

### `H2`: Token-based truncation ~2,000 tokens

**Not supported for this URL.** Successful runs consistently returned ~1,500 tokens, below the 2,000-token threshold. No run approached or
hit a token ceiling. GPT-5.4-Mini Low estimated 2,000-2,300 tokens from a rendered page view with nav chrome, but this reflects surface inflation
not a token gate.

**Combined verdict: `H2` indeterminate. Document too small to test the hypothesis.**

---

### `H3`: Structure-aware truncation, respects Markdown boundaries

**Partially supported.** All successful runs confirmed clean closure after the final JSON code fence, with balanced triple-backtick counts confirmed
across multiple runs via regex, perl, and python3 verification. However, the `ce-create## Summary` malformed heading artifact appeared consistently
and misidentified by multiple agents as a truncation or parsing artifact rather than a source property. Structure-aware ending holds for the
document tail, but the mixed Markdown/HTML format introduced persistent misidentification across all model versions and levels.

**Combined verdict: `H3` partially supported for tail integrity. Mixed-format source misidentification is a significant confound.**

---

### `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

**Partially supported within-surface only.** All runs on the Codex IDE surface. Within this surface meaningful differences
observed across intelligence levels. `Low` levels stopped at fetch failures, `Medium` and higher escalated to `curl`, `Extra High` levels added
headers inspection, parallel tools, and `Browser Use` attempts. The two-tier network access pattern, sandboxed DNS failure followed by escalated
`curl` success consistent across all model families. Cross-surface VS Code-Codex comparison remains untested.

**Combined verdict: `H4` partially supported for within-surface intelligence-level effects. Cross-surface comparison untested.**

---

### `H5`: Agent auto-chunks/auto-paginates

**Not supported.** No run demonstrated automatic pagination or multi-target chunking. Multi-step tool chains observed in `Medium` and higher runs
were recovery-driven, responding to fetch failures, not proactive pagination. The most elaborate chains used 13 commands and 5 searches but
all targeted the same single document. No model at any level attempted to fetch the document in segments or recognize that a multi-part
retrieval strategy was appropriate.

**Combined verdict: `H5` not supported. Tool chaining is failure-recovery behavior, not auto-pagination.**

---

### Emergent Findings

1. **The BL-2 source document mixed Markdown/HTML and smaller than expected, making it a poor truncation test but a strong misidentification test.**
The 6,024-char document consistently fell below every plausible ceiling, so `H1` and `H2` not evaluated. However, the mixed format; Markdown
headings and prose with raw HTML table tags, caused persistent misidentification across all 20 runs. Agents at every level and from every model
family flagged the source as corrupted, truncated, or incompletely retrieved when it wasn't. This is a distinct failure mode from retrieval
truncation.

2. **Two-tier network access architecture** The consistent pattern of sandboxed `curl` returning 0 bytes or DNS failure, followed
by escalated `curl` succeeding, indicates that the Codex IDE environment has two distinct network access tiers. The web tool and sandboxed shell
operate on a restricted network path; escalated shell access uses a separate path capable of resolving external DNS. This is an infrastructure
property of the surface, not agent behavior, and is relevant to H4 cross-surface comparisons.

3. **CDN layer behavior affects retrieval consistency.** Run 16 confirmed the `BL-2` URL served via CloudFront with Netlify Edge caching.
`cache-status` varied across runs, stale in Run 16, fresh `age: 0` in Run 20. The `web.open` `400` failure that appeared in multiple runs
likely reflects CDN edge routing behavior specific to the web tool's fetch path, distinct from direct TCP via `curl`. This provides the first
concrete infrastructure explanation for the persistent 400 errors that no agent investigated or diagnosed across all 20 runs.

4. **Mixed-format misidentification actively drives tool selection.** `GPT-5.4-Mini` `Extra High` attempted `Browser Use` after determining the content
was "buried inside a large HTML document" - a misreading of the mixed Markdown/HTML source as a rendering problem. This is the strongest evidence
that source format misidentification influences the tool chain, not just self-reported completeness assessments.

5. **False truncation reporting emerges at lower model tiers based on size expectation.** `GPT-5.4 Low` and `GPT-5.4-Mini Low` both reported truncation
despite confirming clean code fence closure. The sole basis was the ~20KB size expectation vs the 6,024-char actual. This expectation-driven false
positive is a distinct error mode from evidence-based truncation detection - distinguish in future analysis.

6. **Intelligence level governs instrumentation sophistication more than retrieval outcome.** Across all model families, higher intelligence levels
produced more elaborate verification chains, hex dumps, parallel tools, headers inspection, regex structural audits, but consistently returned
identical 6,024-char results. The cost/yield regression observed in `BL-1` `Extra High` runs reappears here: `GPT-5.5 Extra High` spent 4m51s and 25K
context tokens for the same result as `GPT-5.5 Low` at 55 seconds.

7. **Workspace contamination confirmed as a recurring confound.** The Finder screenshot from Run 14 shows artifact files in sessions web-2,
web-3, web-4, web-7, web-10, web-12, and web-13 but empty folders for web-5, web-6, web-8, web-9, and web-11. Workspace paths reported by agents
don't always match the expected session number. `GPT-5.5 High` skipped `web.open` entirely and likely read a prior session artifact rather than
performing a live fetch. No agent across 20 runs checked the local workspace before fetching, confirming the absence of cache-before-fetch behavior
noted in `BL-1`.

8. **Task naming specificity scales with intelligence level.** Codex named tasks with increasing specificity at higher intelligence levels:
`Low` used "Test web retrieval," `Medium` used "Report retrieval stats," `High` used "Test web retrieval `BL-2`," and `Extra High` used
"Fetch MongoDB docs URL." This suggests intelligence level affects task-scoping behavior independently of retrieval outcome.

---

### Log Label Summary

| Agent | Result | Label |
| --------------- | ------- | --------------------------- |
| `GPT-5.2 Low` | ✗ | `FAIL - 400_fetch_failure + no_curl + error_only` |
| `GPT-5.2 Medium` | ✓ | `PASS - curl_escalation + html_artifact_saved + complete` |
| `GPT-5.2 High` | ✓ | `PASS - curl_escalation + md_artifact_saved + tiktoken_attempt` |
| `GPT-5.2 Extra High` | ✓ | `PASS - curl_escalation + header_inspection + pre_permission_curl` |
| `GPT-5.3-Codex Low` | ✗ | `FAIL - 400_fetch_failure + no_curl + identical_to_5.2_low` |
| `GPT-5.3-Codex Medium` | ✓ | `PASS - curl_escalation + fastest_successful + markdown_output` |
| `GPT-5.3-Codex High` | ✓ | `PASS - curl_iL_combined + 2byte_variance + reasoning_transparent` |
| `GPT-5.3-Codex Extra High` | ✓ | `PASS - parallel_tools + header_inspection + over_instrumented` |
| `GPT-5.4-Mini Low` | Partial | `PARTIAL - rendered_page_inflation + curl_dns_fail + false_truncation` |
| `GPT-5.4-Mini Medium` | ✓ | `PASS - sandboxed_then_escalated + html_tag_inventory + complete` |
| `GPT-5.4-Mini High` | ✓ | `PASS - od_hex_verify + shell_error_recovered + complete` |
| `GPT-5.4-Mini Extra High` | ✓ | `PASS - browser_use_attempt + blocked + curl_fallback + over_instrumented` |
| `GPT-5.4 Low` | Partial | `PARTIAL - false_truncation_report + size_expectation_mismatch + complete_body` |
| `GPT-5.4 Medium` | ✗ | `FAIL - 400_fetch_failure + workspace_path_mismatch + regression` |
| `GPT-5.4 High` | ✓ | `PASS - surface_split_report + internal_ids_visible + complete` |
| `GPT-5.4 Extra High` | ✓ | `PASS - headers_saved + cdn_confirmed + stale_cache_hit` |
| `GPT-5.5 Low` | ✓ | `PASS - two_tier_documented + size_caveat + complete` |
| `GPT-5.5 Medium` | ✓ | `PASS - html_tag_count + token_range_estimate + complete` |
| `GPT-5.5 High` | ✓* | `PASS* - web_open_skipped + possible_workspace_read + contamination_flag` |
| `GPT-5.5 Extra High` | ✓ | `PASS - gzip_confirmed + cdn_fresh_hit + perl_regex_suspect + over_instrumented` |
