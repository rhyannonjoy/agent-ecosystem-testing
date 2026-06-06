# BL-1 Summary

## Test Conditions

|                 | **BL-1** |
| --------------- | -------- |
| URL             | `https://www.mongodb.com/docs/manual/reference/change-events/create/` |
| Expected size   | ~85KB per prompt; actual confirmed 509,025 chars / ~127,000 tokens via `curl`, discrepancy reflects inline CSS and Gatsby runtime payload; semantic content is ~85KB equivalent |
| Surface         | VS Code-Codex Extension      |
| Workspace       | Session-scoped sandbox; no `/private/tmp/codex-browser-use` or `Documents/Codex`; project accessible as working directory |
| Track           | T2 VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.5`, `GPT-5.4-Mini` |
| Runs            | 8 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.5 Low` | 509,025 | ~127,000 | Display yes, `curl` no | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `multi_tool_use.parallel` | Yes | `web.open` viewport-limited at `L420` of `L545`; `curl` fallback; DNS sandbox failure then approved fetch; asked permission for `curl` twice; wrote `mongodb-create.html` to `/private/tmp`; named `Test web retrieval`; 51 seconds |
| `GPT-5.5 Medium` | ~85,000 est. | ~21,000 | Display yes, no `curl` | `L543: * Summary  L544: * Description  L544: * Example` rendered view | `web.run`, `web.open`, `turn0view0`, `turn1view0` | No | `web.open` only; didn't escalate to `curl`; two-pass view for truncation verification at `L420`; named `Test web retrieval BL-1`; 28 seconds |
| `GPT-5.5 High` | 509,025 | ~127,000 | Display yes, `curl` no | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `head` | Yes | `web.open` then `curl` with explicit escalation reasoning; `rg` pattern attempt failed; `head -c 80` integrity check; wrote `bl1_create.html` to `/private/tmp`; named `Test web retrieval`; 1 minute 10 seconds |
| `GPT-5.5 Extra High` | ~85,000 est. | ~21,000 | Display yes, no `curl` | `L543: * Summary  L544: * Description  L544: * Example`, rendered view | `web.run`, `web.open`, `mcp__node_repl.js` | No | `web.open` only; didn't escalate to `curl`; two-pass view; JS suffix counting via `mcp__node_repl.js`; named `Test web retrieval`; 2 minutes 41 seconds |
| `GPT-5.4-Mini Low` | 509,025 | ~127,000 | Display yes, `curl` no | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | No | `web.open` then `curl`; asked permission for `curl` twice; noted ~85KB expected vs 509KB actual size discrepancy; named `Test web retrieval`; 23 seconds |
| `GPT-5.4-Mini Medium` | 509,025 | ~127,000 | Display yes, `curl` no | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.open`, `web.find`, `functions.exec_command`, `curl`, `wc`, `tail`, `node_repl` | Yes | `web.open` then Browser attempt, `Browser is not available: iab`; fallback to `curl`; wrote `mongodb-create.html` to `/private/tmp`; filename collision with Run 1, contamination risk; named `Test MongoDB retrieval BL-1`; 1 minute 45 seconds |
| `GPT-5.4-Mini High` | 509,025 | ~127,000 | Display yes, `curl` no | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail` | Yes | `web.open` then `curl`; wrote `mdb_create.html` to `Documents/GitHub/agent-ecosystem-testing`, only T2 run to write to project directory; post-session duplicate report and timer drift from 1 minute 45 seconds to 1 minute 50 seconds; named `Test web retrieval`; 1 minute 45 seconds |
| `GPT-5.4-Mini Extra High` | 509,025 | ~127,000 | Display yes at `L119`, `curl` no | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web.run`, `web.open`, `functions.exec_command`, `curl`, `node` | No | `web.open` then `curl`; initial DNS sandbox fetch returned empty body; HTTP headers surfaced in thought panel, Netlify Edge hit, CloudFront miss, `SEA900-P10` Seattle PoP, cache age 3,934 seconds; `tiktoken` unavailable; `node` for precise character counting; named `Fetch MongoDB docs`; 4 minutes 11 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported at the HTTP response layer. Six runs retrieved 509,025 chars intact via `curl`, well above any proposed 10–100 KB ceiling. The two `web.open`-only runs returned an estimated ~85,000 rendered chars, but this reflects the `web.open`
viewport extraction, not a raw HTTP response body. Five of the six `web.open`-accessible runs reported display truncation at `L420` of `L545`; `GPT-5.4-Mini Extra High` reported truncation at `L119`, confirming the line-count ceiling isn't
consistent across runs, don't treat as a fixed infrastructure limit.

**Combined verdict: `H1` no for HTTP retrieval. `web.open` display truncation is a viewport-layer phenomenon, not a character-based fetch ceiling. The `--></body></html>` tail on all `curl`-path runs confirms retrieval completeness.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. `curl`-path runs returned ~127,000 tokens intact. `web.open`-only runs estimated ~21,000 tokens from the rendered view. Both figures are well above the proposed 2,000-token threshold.

**Combined verdict: `H2` no.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Can't assess at the HTTP retrieval layer, no `curl` run produced truncation. `web.open` display truncation at `L420` appears to be a line-count viewport limit rather than a structural boundary; the underlying page rendered HTML rather than
Markdown. `GPT-5.4-Mini Extra High` reported truncation at `L119`, a substantially different position, further undermining a fixed structural explanation.

**Combined verdict: `H3` indeterminate. No `curl`-path truncation makes boundary-type assessment impossible. `web.open` line-count cutoffs don't map cleanly to Markdown structure on an HTML-rendered page.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Supported across all eight runs. Every T2 run differed from its T1 equivalent in toolchain composition, output size, or retrieval strategy. The most consistent cross-surface signals are the absence of `/private/tmp/codex-browser-use`
initialization, confirming the Browser Use IPC socket isn't provisioned by the VS Code extension and the retrieval gap between `web.open`-only runs and `curl`-path runs. `GPT-5.5 Medium` and `GPT-5.5 Extra High` stayed `web.open`-only
in T2 while T1 counterparts used `curl`; all four `GPT-5.4-Mini` T1 intelligence levels also stayed `web.open`-only while all four T2 counterparts escalated to `curl`.

LLM-version drift not ruled out. Both models available for T2 were also available during T1 collection, but intra-version behavioral changes between collection dates aren't detectable from run artifacts alone.

**Combined verdict: `H4` yes, with model-version drift caveat.**

---

## `H5`: Agent auto-chunks or auto-paginates

Not supported. Every run used a single `curl` fetch or a single `web.open` session. Multi-pass `web.open` views in two runs served truncation verification rather than systematic pagination. No run split the fetch, requested byte ranges,
or chained retrieval calls for coverage.

**Combined verdict: `H5` no. Single-fetch retrieval across all eight runs.**

---

## Emergent Findings

1. **Two retrieval outcomes emerge by intelligence level for `GPT-5.5`.** `GPT-5.5 Medium` and `GPT-5.5 Extra High` stayed `web.open`-only, returning ~85,000 rendered chars. `GPT-5.5 Low` and `GPT-5.5 High` escalated to `curl`,
returning 509,025 raw chars. For `GPT-5.4-Mini`, all four intelligence levels escalated to `curl`. The pattern isn't monotonic, higher intelligence doesn't reliably yield fuller retrieval, but does appear to correlate with
more elaborate self-reporting and verification steps.

2. **`web.open` display truncation isn't at a fixed line count.** Five runs reported truncation at `L420` of `L545`. `GPT-5.4-Mini Extra High` reported truncation at `L119`. The variable cutoff suggests the viewport ceiling is
context-dependent rather than a fixed infrastructure limit and shouldn't be treated as a stable measurement boundary across runs.

3. **`Browser` tool attempt and failure in Run 6 is an infrastructure-level surface difference.** `GPT-5.4-Mini Medium` attempted to invoke a Browser tool and received `Browser is not available: iab`. The VS Code-Codex extension
doesn't initialize the IPC socket that the Codex desktop app creates at launch, and there's no obvious path to configure Browser functionality in the extension settings. This is an architectural difference between surfaces, not
a behavioral one.

4. **Artifacts written in 4 of 8 runs, with inconsistent placement.** Three runs wrote to `/private/tmp` session-scoped and not persistent across sessions. `GPT-5.4-Mini High` wrote to the VS Code project directory
`Documents/GitHub/agent-ecosystem-testing`, the only T2 run to demonstrate workspace-aware file placement. The prompt didn't request artifacts in any run.

5. **One contamination risk from filename collision, Runs 1 and 6.** Both wrote `mongodb-create.html` to `/private/tmp` at 509,025 bytes. Whether Run 6 performed a fresh network fetch or measured the existing file from Run 1
can't confirm from available evidence. Run 6 metrics flagged with a light contamination note.

6. **HTTP response headers surfaced in Run 8 only.** `GPT-5.4-Mini Extra High` used `curl -D -` to dump headers alongside the main fetch, exposing a Netlify Edge and CloudFront CDN stack, a `SEA900-P10` Seattle PoP consistent
with the Bellevue testing location, and a cache age of 3,934 seconds confirming content consistency across the test window. No other run performed independent header inspection.

7. **Post-session output editing confirmed in T2 for the first time.** `GPT-5.4-Mini High` showed a duplicate report appear after session completion and elapsed timer drift from 1 minute 45 seconds in the screenshot to 1 minute
50 seconds post-session. This matches the autonomous session alteration behavior described in the Track 1 Friction Note. Screenshot capture at run time is the primary record per established methodology.

8. **`multi_tool_use.parallel` appeared only in Run 1.** Present in `GPT-5.5 Low` but absent from all other T2 BL-1 runs. In T1, this identifier appeared consistently across `GPT-5.5` instances. Its absence from T2 `GPT-5.5 Medium`,
`GPT-5.5 High`, and `GPT-5.5 Extra High` is a surface-level divergence from T1 behavior.

9. **Toolchains were consistent but not elaborate.** Every run followed the same basic pattern: attempt `web.open`, escalate to `curl` if needed, run light verification commands. No run used specialized retrieval strategies,
byte-range requests, or multi-step fetch chaining. Additional tooling in higher-intelligence runs served measurement and verification rather than retrieval.

10. **Truncation self-reporting was consistent and unprompted.** Every run that used `curl` explicitly distinguished between `web.open` display truncation and `curl` response completeness. No run conflated the two. The `web.open`-only
runs characterized their output as a rendered viewport excerpt rather than a raw dump, without prompting.

11. **Model retirement reduced test coverage relative to T1.** Five models were available for T1 BL-1 across 20-plus runs; only `GPT-5.5` and `GPT-5.4-Mini` remain for T2. The reduction to 8 runs limits statistical depth and makes
per-model patterns harder to assess with confidence. Cross-track comparisons carry a correspondingly wider uncertainty margin.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.5 Low` | Pass | `PASS - web_open_L420_truncated + curl_509025_chars + multi_tool_use_parallel + mongodb_create_html_private_tmp + 51 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS - web_open_L420_truncated + web_only_85k_rendered + no_curl + 28 seconds` |
| `GPT-5.5 High` | Pass | `PASS - web_open_L420_truncated + curl_509025_chars + explicit_escalation_reasoning + bl1_create_html_private_tmp + 1 minute 10 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS - web_open_L420_truncated + web_only_85k_rendered + no_curl + mcp_node_repl_js + 2 minutes 41 seconds` |
| `GPT-5.4-Mini Low` | Pass | `PASS - web_open_truncated + curl_509025_chars + size_discrepancy_noted + 23 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS - web_open_truncated + browser_not_available_iab + curl_509025_chars + mongodb_create_html_private_tmp + contamination_risk + 1 minute 45 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS - web_open_truncated + curl_509025_chars + mdb_create_html_project_dir + post_session_duplicate_report + timer_drift + 1 minute 45 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - web_open_L119_truncated + curl_509025_chars + http_headers_surfaced + cdn_stack_exposed + tiktoken_false + node_counting + 4 minutes 11 seconds` |
