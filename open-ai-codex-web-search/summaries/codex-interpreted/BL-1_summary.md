## BL-1 GPT-interpreted Track Summary

### Test Conditions

|                 | **BL-1**                                                              |
| --------------- | --------------------------------------------------------------------- |
| URL             | `https://www.mongodb.com/docs/manual/reference/change-events/create/` |
| Expected size   | ~85KB                                                                 |
| Surface         | Codex IDE                                                             |
| Workspace       | No workspace, session-scoped sandbox only                             |
| Track           | `T1` GPT-interpreted, Codex IDE                                       |
| Method          | GPT-interpreted                                                       |
| Runs            | 20                                                                    |
| Chunks returned | _N/A, interpreted track_                                              |

---

### Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ------------ | ------------ | ------------ | ------------ | -------------- | ------------ |
| `GPT-5.4-mini Low` | ~19,000 | ~4,500 | Yes mid-page | `* Summary\n * Description\n * Example` | `web`, `web.open` | Unknown | Single fetch; line-windowed excerpt |
| `GPT-5.4-mini Medium` | ~85,000 | ~20,000 | Yes tool display | `* Summary\n * Description\n * Example` | `web`, `web.open` | Unknown | Multiple view IDs; identical tail to Low |
| `GPT-5.4-mini High` | ~85,000 | ~21,000 | Yes tool display | `* Summary\n * Description\n * Example` | `web`,`web.open` | Unknown | Fewer tool calls than Medium despite higher level |
| `GPT-5.4-mini Extra High` | ~85,000 | ~20,000 | Yes tool display | `* Summary\n * Description\n * Example` | `web`,`web.open` | Unknown | 3-part fetch strategy; 85 s runtime; same yield as Medium/High |
| `GPT-5.2 Low` | ~1,600 `wordlim` | ~250–450 | Yes `wordlim: 200` | `when the change stream uses \n\n` | `web`,`web.open` | Yes empty | First explicit cap mechanism surfaced; cuts mid-page |
| `GPT-5.2 Medium` | ~24,500 | ~2,000–6,000 | Yes (L477/542) | `New in version 6.0.\n\n` | `web`,`web.open` | Yes, empty | L477 cutoff; agent aware of 65 missing lines, no pagination |
| `GPT-5.2 High` | 505,339 `curl` | ~126,000 | No `curl`; Yes `web.open` | `slice-end id="_gatsby-scripts-1" --></body></html>` | `web`, `web.open`, `curl`, `wc`, `tail`, `perl`, `python3` | Yes `/private/tmp` | First `curl` escalation; `wordlim: 200` confirmed on `web.open` |
| `GPT-5.2 Extra High` | 505,339 `curl` | ~126,335 | No (curl); Yes (web.open) | `slice-end id="_gatsby-scripts-1" --></body></html>` | web, web.open, curl, wc, tail, perl, python3 | Yes (/private/tmp) | 18 web searches; no permission prompt; web.open starts at L39 or L216 |
| `GPT-5.3-Codex Low` | ~28,000–35,000 | ~7,000–9,000 | Yes (~L140) | `page\n * Summary\n * Description\n * Example` | web, web.open, web.find | Yes (sandbox) | Default open→find two-step pattern |
| `GPT-5.3-Codex Medium` | ~24,500 | ~6,100 | Yes (~L140) | `page\n * Summary\n * Description\n * Example` | web, web.open (lineno=520) | Yes (sandbox) | L140 cut identical to Low; lineno=520 tail fetch; Medium < Low |
| `GPT-5.3-Codex High` | ~60,000 | ~15,000 | Yes (L477) | `L539: * Summary\nL540: * Description\nL541: * Example` | web, web.open (lineno variants) | Yes (sandbox) | 7 fetches; meta-reasons about ~85KB ceiling; L477 reappears |
| `GPT-5.3-Codex Extra High` | ~61,000 | ~15,000 | Yes (L477) | `events .】\nL475: \nL476: New in version 6.0.\nL477:` | web, web.open, web.run, Node REPL | Yes (sandbox) | Node REPL for tail calc; 28% context used; line numbers in output contaminate char count |
| `GPT-5.4 Low` | 505,339 (curl) | ~126,000 | No (curl); Yes (terminal display ~116K tokens truncated) | `slice-end id="_gatsby-scripts-1" --></body></html>` | web, web.open, curl, python3/urllib | Yes (/private/tmp) | Three truncation layers disambiguated; curl escalation at Low |
| `GPT-5.4 Medium` | 505,339 (curl) | ~126,000 | No (curl); Yes (terminal display) | `slice-end id="_gatsby-scripts-1" --></body></html>` | web, web.open, curl, python3/urllib | Yes (/private/tmp) | Near-identical to Low; curl escalation stable across levels |
| `GPT-5.4 High` | 505,339 (curl) | ~126,000 | No (curl); Yes (terminal display) | `slice-end id="_gatsby-scripts-1" --></body></html>` | web, web.open, curl, python3 | Yes (/private/tmp) | DNS sandbox failure on first curl; self-corrected with network escalation |
| `GPT-5.4 Extra High` | 505,339 (curl) | ~126,000 | No (curl); Yes (terminal display) | `slice-end id="_gatsby-scripts-1" --></body></html>` | web, web.open, curl, python3 | Yes (/private/tmp) | Session contamination confirmed; 42 s runtime from strategy reuse |
| `GPT-5.5 Low` | 505,339 (curl) | ~126,335 | No (curl); Yes (terminal display) | `slice-end id="_gatsby-scripts-1" --></body></html>` | curl, wc, tail, file, grep (no web/web.open) | Yes (/private/tmp) | First run to skip web.open entirely; curl as primary default |
| `GPT-5.5 Medium` | 505,339 (curl) | ~126,335 | No (curl); Yes (terminal display) | `slice-end id="_gatsby-scripts-1" --></body></html>` | curl, wc, tail, grep, file (no web/web.open) | Yes (/private/tmp) | Saves to temp file before measuring; session contamination likely |
| `GPT-5.5 High` | 505,339 (curl) | ~126,335 | No (curl); Yes (terminal display) | `slice-end id="_gatsby-scripts-1" --></body></html>` | curl, wc, tail, grep, file (no web/web.open) | Yes (/private/tmp) | "Fresh fetch" claim contradicted by filename and 20 s runtime; contaminated |
| `GPT-5.5 Extra High` | 505,339 (curl) | ~126,335 | No (curl); Yes (terminal display) | `slice-end id="_gatsby-scripts-1" --></body></html>` | curl, multi_tool_use.parallel, wc, tail, grep, file | Yes (/private/tmp) | Parallel tool execution first observed; context 40K; all 5.5 runs contaminated |

---

### `H1`: Character-based truncation at a fixed ceiling

**Partially supported, model-stratified.** Output sizes varied significantly by model and intelligence level rather than converging on a single fixed ceiling. `web.open`
imposed a tool-layer ceiling not infrastructure: ~19K chars for `GPT-5.4-mini` Low, ~85K for `GPT-5.4-mini` Medium/High/Extra High, ~1,600 for `GPT-5.2 Low` `wordlim: 200`,
~24.5K for `GPT-5.2` Medium, ~28–35K for `GPT-5.3-Codex` Low, ~60–61K for `GPT-5.3-Codex` High/Extra High. Models capable of `curl` escalation, `GPT-5.2` High+, `GPT-5.4`
all levels, `GPT-5.5` all levels retrieved 505,339 chars consistently, confirming the true page size and that `web.open` ceilings are tool constraints, not server limits.

**Combined verdict: `H1` partially supported. A ceiling exists within `web.open` but is model- and level-dependent, not a fixed universal limit. `curl` bypasses it entirely.**

---

### `H2`: Token-based truncation ~2,000 tokens ≈ 8,000 chars

**Not supported.** No run approached a 2,000-token ceiling. Token counts ranged from ~250–450, `GPT-5.2 Low`, `wordlim`-constrained to ~126,335 `curl`-capable models.
`GPT-5.4-mini` Medium/High/Extra High returned ~20,000 tokens via `web.open` alone. No evidence of token-based gating at any threshold tested.

**Combined verdict: `H2` not supported.**

---

### `H3`: Structure-aware truncation, respects Markdown boundaries

**Not supported.** All observed `web.open` truncations cut at arbitrary line offsets `L140`, `L477` with no relationship to Markdown structure. The retrieved content is a
line-indexed HTML-to-text extraction, not Markdown, making boundary-aware truncation structurally impossible on this surface. The `L477` cutoff appeared across `GPT-5.2`
Medium, `GPT-5.3-Codex` High, and `GPT-5.3-Codex` Extra High, suggesting a shared infrastructure constant rather than content-adaptive behavior.

**Combined verdict: `H3` not supported. Truncation is line-offset based on a rendered text extraction; Markdown boundaries aren't a factor.**

---

### `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval ceiling

**Untested.** All runs conducted on the Codex IDE surface. Cross-surface comparison data not yet collected.

**Combined verdict: `H4` untested.**

---

### `H5`: Agent auto-chunks/auto-paginates

**Partially supported, reasoning-dependent not automatic.** Multi-step retrieval observed in several runs, but varied significantly by model and level.
`GPT-5.4-mini` Extra High used a deliberate 3-part fetch strategy - head, tail, middle-  but produced identical yield to single-fetch runs.
`GPT-5.2` High and Extra High used multi-tool `curl`-based chaining to overcome `web.open` limits. `GPT-5.3-Codex` models used a default `open→find` or
`open→open(lineno=N)` two-step, appearing templated rather than reasoned. `GPT-5.4` and `GPT-5.5` escalated to `curl` with varying degrees of deliberation.
No model demonstrated automatic pagination in the absence of reasoning; chaining required either explicit gap detection or a baked-in retrieval template.

**Combined verdict: `H5` partially supported. Multi-step chaining occurs but is model-specific, reasoning-triggered, and doesn't reliably increase yield
beyond the `web.open` ceiling without `curl` escalation.**

---

### Emergent Findings

1. **`web.open` is a line-indexed text extraction viewer, not a raw HTTP response.** It returns a rendered, line-numbered extraction of page content
`Total lines: 542` for this URL, with a viewer window that doesn't start at `L0` and imposes a model-stratified ceiling. This fundamentally differs from
what agents describe as "fetching a URL" and contaminates all character/token count comparisons that rely on `web.open` output alone.

2. **`L477` is a probable shared infrastructure cutoff constant.** The identical line offset appeared across `GPT-5.2` Medium, `GPT-5.3-Codex` High, and
`GPT-5.3-Codex` Extra High without model coordination, suggesting a hardcoded viewer window limit in the `web.open` tool layer rather than content-adaptive
or model-specific behavior.

3. **`curl` escalation capability is model-gated, not intelligence-level-gated for higher models.** `GPT-5.2` required High intelligence to attempt
`curl`; `GPT-5.4` escalated at Low; `GPT-5.5` skipped `web.open` entirely at all levels. This represents a progressive capability shift across model generations
where terminal tool access becomes an increasingly default rather than fallback behavior.

4. **Higher intelligence doesn't reliably produce higher yield, and Extra High levels consistently show cost/yield regression.** `GPT-5.4-mini` Extra High spent
85 seconds on a 3-part strategy that matched Medium's 24-second single-fetch output. `GPT-5.3-Codex` Extra High used `Node REPL` and 8 fetches to match High's
result. This corroborates OpenAI's own documentation warning that higher reasoning effort on tasks with open-ended tool access and weak stopping criteria can
produce overthinking and output quality regression.

5. **Session contamination is a significant confound for within-session intelligence-level comparisons.** Later runs within the same session showed context window
accumulation, evidenced by growing token counts, filename awareness from prior runs, and strategy reuse that compressed runtimes implausibly. `GPT-5.4` Extra High
completed in 42 seconds vs 1m46s for Low on an identical task; `GPT-5.5` High completed in 20 seconds with a "fresh fetch" claim contradicted by the output filename. Intelligence level isn't an independent variable within a shared session; future runs should use isolated sessions per level.

6. **Three distinct truncation layers exist and must be disambiguated.** `GPT-5.4` Low was the first run to cleanly separate: `web.open` viewer truncation, terminal display
truncation ~116,434 tokens truncated in tool output, and the actual HTTP response body, complete at 505,339 chars. Earlier runs conflated these layers, making their reported character counts unreliable as measures of retrieval completeness.

7. **The workspace sandbox is consistently present but inert.** All runs acknowledged local filesystem access at a session-scoped path
`/Users/rhyannonjoy/Documents/Codex/2026-05-09/i-m-testing-codex-s-web-2`, despite the test prompt stating no workspace. The sandbox exists but contains no user files.
This isn't deceptive agent behavior but a gap between the prompt condition and the actual Codex environment configuration; note as a surface characteristic for `H4` cross-surface comparisons.

---

### Log Label Summary

| Agent | Result | Label |
| ----------------------- | ------- | -------------------------------------------------------- |
| `GPT-5.4-mini Low` | Partial | `PARTIAL — web.open_ceiling + single_fetch + line_window` |
| `GPT-5.4-mini Medium` | Partial | `PARTIAL — web.open_ceiling + multi_view + identical_tail` |
| `GPT-5.4-mini High` | Partial | `PARTIAL — web.open_ceiling + reduced_tool_calls` |
| `GPT-5.4-mini Extra High` | Partial | `PARTIAL — web.open_ceiling + overthink + cost_yield_regression` |
| `GPT-5.2 Low` | ✗ | `FAIL — wordlim_200 + mid_page_cut + no_pagination` |
| `GPT-5.2 Medium` | Partial | `PARTIAL — L477_cut + agent_aware_gap + no_pagination` |
| `GPT-5.2 High` | ✓ | `PASS — curl_escalation + full_body + three_truncation_layers` |
| `GPT-5.2 Extra High` | ✓ | `PASS — curl_escalation + full_body + autonomy_flag + 18_searches` |
| `GPT-5.3-Codex Low` | Partial | `PARTIAL — open_find_template + L140_cut + two_step_default` |
| `GPT-5.3-Codex Medium` | Partial | `PARTIAL — open_lineno_template + L140_cut + medium_less_than_low` |
| `GPT-5.3-Codex High` | Partial | `PARTIAL — L477_cut + meta_ceiling_reasoning + 7_fetches` |
| `GPT-5.3-Codex Extra High` | Partial | `PARTIAL — L477_cut + node_repl + line_numbers_contaminate_count` |
| `GPT-5.4 Low` | ✓ | `PASS — curl_default + three_layers_disambiguated + full_body` |
| `GPT-5.4 Medium` | ✓ | `PASS — curl_default + full_body + stable_profile` |
| `GPT-5.4 High` | ✓ | `PASS — curl_default + dns_sandbox_retry + full_body` |
| `GPT-5.4 Extra High` | ✓* | `PASS* — curl_default + full_body + session_contamination_flag` |
| `GPT-5.5 Low` | ✓ | `PASS — curl_primary + no_web_open + full_body` |
| `GPT-5.5 Medium` | ✓* | `PASS* — curl_primary + temp_file_measure + session_contamination_flag` |
| `GPT-5.5 High` | ✓* | `PASS* — curl_primary + full_body + session_contamination_flag` |
| `GPT-5.5 Extra High` | ✓* | `PASS* — curl_primary + parallel_tools + session_contamination_flag` |
