# BL-2 Summary

## Test Conditions

|                 | **BL-2** |
| --------------- | -------- |
| URL             | `https://www.mongodb.com/docs/manual/reference/change-events/create.md` |
| Expected size   | 5,805 chars / ~1,450 tokens confirmed via `curl` across all 8 runs; `content-type: text/markdown; charset=UTF-8` confirmed via HTTP headers in Run 3; agents cited size expectation |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/private/tmp` writable; project accessible as working directory |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.5`, `GPT-5.4-Mini` |
| Runs            | 8 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Low` | 5,805 | ~1,450 | Display no, `curl` no | `,"key": { _id: 1 }, "name": "_id_" } } } + closed JSON fence` | `web.run`, `open`, `search_query`, `functions.exec_command`, `curl` | No | `web.open` returned fetch failure; sandboxed `curl` failed DNS, permission-approved fetch succeeded; asked permission for `curl` 3 times; web searches x4; named `Test web retrieval BL-2`; 50 seconds |
| `GPT-5.4-Mini Medium` | 5,805 | ~1,450 | Display no, `curl` no | same as Run 1 | `web.run`, `web.open`, `turn0search0`, `turn1view0`, `functions.exec_command`, `curl`, `wc`, `python3` | Yes | `web.open` returned internal fetch error; sandboxed `curl` failed DNS, escalated fetch succeeded; `python3` `pathlib` for exact tail check; wrote `mongodb_create.md` to `/private/tmp`; asked permission once; named `Fetch MongoDB docs`; 53 seconds |
| `GPT-5.4-Mini High` | 5,805 | ~1,450 | Display no, `curl` no | same as Run 1 | `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `file`, `grep`, `multi_tool_use.parallel` | Yes | `web.open` returned internal fetch error; escalated `curl` succeeded; HTTP headers surfaced including `content-type: text/markdown`, Netlify Edge cache hit, CloudFront miss, `SEA900-P10` Seattle PoP; `file` identified content as HTML document text due to embedded HTML table markup; `grep` confirmed heading and fence structure; `multi_tool_use.parallel` for inspection commands; wrote `bl2_create.md` to `/tmp`; asked permission twice; named `Test web retrieval BL-2`; 1 minute 3 seconds |
| `GPT-5.4-Mini Extra High` | 5,805 | ~1,450 | Display no, `curl` no | same as Run 1 | `web.search_query`, `web.open`, `turn1search0`, `turn2view0`, `functions.exec_command`, `curl`, `wc`, `mcp__node_repl.js` | Yes | `web.open` returned internal fetch error; sandboxed `curl` failed DNS, escalated fetch succeeded; probed `tiktoken`, `@dqbd/tiktoken`, `gpt-tokenizer`, all unavailable; `hasTableClose: true` and `hasCodeFenceOpen: 2` confirmed via final structure check; `ce-create## Summary` formatting artifact flagged and investigated before concluding "weird but complete"; wrote `mongo_create.md` to `/private/tmp`; asked permission 3 times; named `Test web retrieval response`; 4 minutes 38 seconds |
| `GPT-5.5 Low` | 5,805 | ~1,450 | Display no, `curl` no | same as Run 1 | `web.run`, `open`, `functions.exec_command`, `curl` | No | `web.open` returned fetch failure; sandboxed `curl` failed DNS, escalated fetch succeeded; size discrepancy vs ~20KB acknowledged; asked permission 3 times; web search x1; no artifact; named `Test web retrieval`; 55 seconds |
| `GPT-5.5 Medium` | 5,805 | ~1,450 | Display no, `curl` no | same as Run 1 | `web.open`, `web.run`, `functions.exec_command`, `curl`, `wc`, `tail`, `awk`, `sed`, `file` | Yes | `web.open` returned internal fetch error; compound `curl` command encoded `wc -m`, `tail -c 50`, and `awk` fence count in a single invocation; DNS failure then escalated; `file` confirmed HTML document text classification; wrote `bl-2-create.md` to `/private/tmp`; asked permission once; named `Test web retrieval BL-2`; 41 seconds |
| `GPT-5.5 High` | 5,805 | ~1,450 | Display no, `curl` no | same as Run 1 | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `xxd`, `head`, `multi_tool_use.parallel` | Yes | `web.open` returned fetch error; sandboxed `curl` failed DNS, escalated fetch succeeded; `wc -m` and `wc -c` both 5,805 confirming ASCII body; `xxd` hex dump of final 80 bytes; `wc -w` returned 663 words; code fence located at lines 235 to 250; wrote `BL-2-create.md` to `/tmp`, filename collision risk with Run 6 on case-insensitive filesystem; asked permission once; named `Test web retrieval`; 56 seconds |
| `GPT-5.5 Extra High` | 5,805 | ~1,450 | Display no, `curl` no | same as Run 1 | `functions.exec_command`, `curl`, `wc`, `tail`, `head`, `rg`, `file`, `multi_tool_use.parallel` | Yes | bypassed web tools entirely; sandboxed `curl` failed DNS, escalated fetch succeeded; `wc -c` and `wc -m` both 5,805 confirming ASCII body; `rg` fence pattern hit shell quoting error, fell back to alternate search; `wc -w` returned 663 words; `file` confirmed HTML document text classification; wrote `bl-2-create.md` to `/private/tmp`, filename collision risk with Runs 6 and 7 on case-insensitive filesystem; asked permission once; named `Test web retrieval`; 1 minute 35 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

BL-2 can't evaluate this hypothesis. The source document is 5,805 chars, well below the proposed 10-100KB ceiling. No truncation occurred in any run and no ceiling stressed.
The page is too small to distinguish between "no ceiling exists" and "ceiling exists but wasn't reached."

**Combined verdict: `H1` indeterminate. The page is too small to stress any character-based ceiling. No truncation occurred across all 8 runs.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported in either direction. ~1,450 tokens across all 8 runs, well below the proposed 2,000-token threshold. The same constraint applies as for `H1`: the document is small
enough that the threshold was never approached. Token estimates remained a rough 4 chars/token heuristic throughout; `tiktoken` and related packages were unavailable in the sandbox.

**Combined verdict: `H2` indeterminate.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Can't assess. No truncation occurred in any run. Several runs performed programmatic structural verification, including fence balance counting via `awk`, heading marker searches via
`grep`, hex inspection via `xxd`, and explicit line-number location of the code fence at lines 235 to 250. All confirmed complete markdown structure. Without a truncation event,
boundary-type assessment isn't possible.

**Combined verdict: `H3` indeterminate. No truncation to assess boundary type. Structural completeness was confirmed more rigorously in BL-2 than in BL-1, but no truncation edge arose to evaluate.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Partially supported, with caveats. `T2` consistently returned 5,805 chars across all 8 runs while comparable `T1` runs returned 6,024 chars, a difference of 219 chars. Toolchain differences
observed across the tracks: `T2` doesn't have access to `Browser` use, `GPT-5.5 Extra High` bypassed web tools entirely while its `T1` counterpart used `web.run` and `open`, and instrumentation
approaches varied.

The 219-char count difference can't be attributed to surface behavior alone. A content update to the source endpoint between `T1` and `T2` collection windows is equally plausible and not ruled
out without a concurrent `T1` replication run. Model-version drift between collection windows also isn't detectable from run artifacts alone.

**Combined verdict: `H4` partially, with page-update and model-version drift caveats. Toolchain behavioral differences confirmed. The char count gap likely reflects a source update rather than surface-specific retrieval behavior.**

---

## `H5`: Agent auto-chunks or auto-paginates

Not supported. All 8 runs used single-fetch retrieval. Multi-command tool sequences served measurement and verification, not chunked content retrieval. `multi_tool_use.parallel` appeared in 3 runs
but grouped inspection commands in parallel, not sequential fetch steps. Run 3 HTTP headers confirmed the server supports byte-range requests via `accept-ranges: bytes`, but no run invoked this capability.

**Combined verdict: `H5` no. Single-fetch retrieval across all 8 runs. Parallel tool use served inspection, not pagination.**

---

## Emergent Findings

1. **5,805 chars confirmed stable across all 8 `T2` runs.** Every run returned the same character count regardless of model version or intelligence level. This is the strongest internal consistency
signal in the `T2` series to date. Runs that checked both `wc -c` and `wc -m` received identical values, confirming pure ASCII content with no multi-byte characters.

2. **`content-type: text/markdown; charset=UTF-8` confirmed via HTTP headers.** Run 3 surfaced a Netlify Edge cache hit, CloudFront miss at `SEA900-P10` Seattle PoP,
`cache-control: public,max-age=0,must-revalidate` overridden by Netlify with `age: 3534`, and an explicit `text/markdown` content type. The server serves this endpoint as raw markdown, not a rendered
page. Only Run 3 surfaced headers; no other run performed independent header inspection.

3. **`file` utility misclassifies the source as HTML document text.** Across multiple runs, `file /path/to/saved.md` returned `HTML document text, ASCII text, with very long lines (527)`. The embedded
HTML table markup in the markdown source triggers this misclassification. The `527` value reflects the longest line length in characters, not line count. `wc -l` returned 251 lines.

4. **`ce-create## Summary` is a formatting artifact present in the source document, not a retrieval artifact.** `GPT-5.4-Mini Extra High` flagged the concatenated label and heading on one line as a
structural oddity and investigated it before concluding "weird but complete." This artifact is present in the raw `.md` file at the endpoint.

5. **Two-tier sandboxed/escalated network pattern held across all 8 runs.** Every run encountered a sandboxed DNS resolution failure on the first `curl` attempt, then succeeded after permission-escalated
network access. This pattern was consistent across both model families and all intelligence levels. Agents correctly identified the failure as a network restriction rather than a content problem.

6. **`GPT-5.5 Extra High` bypassed web tools entirely, the only `T2` run to do so.** All other runs attempted `web.open` or `web.run` first before escalating to `curl`. The `T1` counterpart used `web.run`
and `open`. Web tool errors weren't examined or diagnosed by any run; agents noted them in passing and pivoted to `curl` without investigating the cause.

7. **Verification sophistication scaled with intelligence level but retrieval outcome didn't.** Low runs used basic `tail` and `wc` checks. Medium introduced compound commands with `awk` fence counting in
a single invocation. High added `xxd` hex dumps and precise line-number code fence location. Extra High probed tokenizer packages and ran a final structure check with boolean flags. All 8 runs returned
identical metrics.

8. **`tiktoken` and related tokenizer packages are unavailable in the `T2` sandbox.** `GPT-5.4-Mini Extra High` probed `tiktoken`, `@dqbd/tiktoken`, and `gpt-tokenizer`, all returned module not found errors.
Token estimation remained a rough 4 chars/token heuristic across all 8 runs.

9. **`accept-ranges: bytes` confirmed in HTTP headers but not used by any run.** The server supports byte-range requests, confirmed in Run 3 headers. No run invoked this capability. A chunking mechanism was
available at the transport layer but wasn't auto-invoked, adding weight to the `H5` no verdict.

10. **Timer drift and duplicate report output observed across all 8 runs.** Each run produced an initial complete output, then Codex continued and added a duplicate report offering no new content. This is a
consistent `T2` BL-2 pattern across every run, not an isolated event. Screenshot capture at run time is the primary record per established methodology.

11. **Filename collision contamination risk across Runs 6, 7, and 8.** Runs 6 and 8 wrote `bl-2-create.md` and Run 7 wrote `BL-2-create.md` to `/private/tmp` and `/tmp` respectively, which resolve to the same
path on a macOS case-insensitive filesystem. Metrics remained consistent across runs, suggesting identical file content, but clean-fetch verification isn't available for Runs 7 and 8.

12. **The 219-char difference between `T1` and `T2` likely reflects a source update.** Seven of eight comparable `T1` runs reported 6,024 chars; all 8 `T2` runs reported 5,805 chars. The difference is consistent
across all model and intelligence combinations, making surface-level retrieval divergence an unlikely sole explanation. A content change to the endpoint between collection windows is the most parsimonious
interpretation. Concurrent `T1` replication would needed to isolate surface effects from page-content changes.

13. **Unprompted Markdown formatting in report items 5 to 8 appeared across most runs.** This pattern appeared in `GPT-5.4-Mini High`, `GPT-5.4-Mini Extra High`, `GPT-5.5 Low`, `GPT-5.5 Medium`, and `GPT-5.5 High`.
It didn't appear in `GPT-5.4-Mini Low`, `GPT-5.4-Mini Medium`, or `GPT-5.5 Extra High`. The pattern doesn't correlate cleanly with intelligence level or model family and wasn't agent-explained or acknowledged in any run.

14. **6 of 8 runs wrote artifacts to `/private/tmp`, a session-scoped location not persistent across sessions.** No run wrote to the project workspace directory. This contrasts with `T2` BL-1 Run 7, where `GPT-5.4-Mini High`
wrote to `Documents/GitHub/agent-ecosystem-testing`. Filenames were inconsistent across runs and the prompt didn't request artifacts in any run.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Pass | `PASS, web_open_fetch_failure + curl_5805_chars + web_search_x4 + no_artifact + 50 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_open_fetch_error + curl_5805_chars + python3_pathlib_tail + mongodb_create_md_private_tmp + 53 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, web_open_fetch_error + curl_5805_chars + http_headers_surfaced + content_type_text_markdown + multi_tool_use_parallel + bl2_create_md_tmp + 1 minute 3 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, web_open_fetch_error + curl_5805_chars + tiktoken_false + hasTableClose_true + ce_create_artifact_noted + mongo_create_md_private_tmp + 4 minutes 38 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, web_open_fetch_failure + curl_5805_chars + size_discrepancy_noted + no_artifact + 55 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, web_open_fetch_error + curl_5805_chars + compound_command + bl_2_create_md_private_tmp + 41 seconds` |
| `GPT-5.5 High` | Pass | `PASS, web_open_fetch_error + curl_5805_chars + xxd_hex_dump + ascii_confirmed + wc_w_663 + BL_2_create_md_tmp_contamination_risk + 56 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_bypassed + curl_5805_chars + ascii_confirmed + rg_quoting_error + wc_w_663 + bl_2_create_md_private_tmp_contamination_risk + 1 minute 35 seconds` |
