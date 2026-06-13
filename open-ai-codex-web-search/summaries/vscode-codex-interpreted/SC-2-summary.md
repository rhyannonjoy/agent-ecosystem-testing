# SC-2 Summary

## Test Conditions

|                 | **SC-2** |
| --------------- | -------- |
| URL             | `https://docs.anthropic.com/en/api/messages` |
| Expected size   | ~80KB API docs with code blocks ~578,000 chars of hydrated HTML/Next.js app shell, redirects to `https://platform.claude.com/docs/en/api/messages` |
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
| `GPT-5.4-Mini Low` | ~6KB visible excerpt | ~1.5k to 2k | Yes | `www.anthropic.com L139: *` | `web.open`, `curl` | No | `web.open` returned line-rendered excerpt ending at `L139` on footer links; sandboxed `curl` failed DNS and uniquely didn't request escalation; truncation report yes; named `Test web retrieval`; 18 seconds |
| `GPT-5.4-Mini Medium` | 578,234 | ~144,559 | Display no, `curl` no | `,\"$L45\",null,{}]]}]\n"])</script></body></html>` | `functions.exec_command`, `curl`, `node` | No | bypassed `web` pipeline entirely; single compound command with inline `node` measurement, uniquely efficient for this cycle; clean `</body></html>` close confirmed; size discrepancy vs ~80KB acknowledged; asked permission once; named `Test web retrieval`; 49 seconds |
| `GPT-5.4-Mini High` | 578,233 | ~145k | `curl` no, `web.open` partial | same as Run 2 | `web.open`, `turn0view0`, `node`, `functions.exec_command`, `curl`, `wc`, `tail` | Yes | `web.open` surfaced 140 lines only; local `node` fetch failed DNS with error uniquely visible in thought panel; escalated `curl` saved `sc2-anthropic-messages.html` to `/private/tmp`; report uniquely truncated, missing item 8 on surface awareness; asked permission once; named `Test web retrieval`; 1 minute 42 seconds |
| `GPT-5.4-Mini Extra High` | 578,234 | ~145k | `curl` no, `web.open` partial | same as Run 2 | `web.open`, `turn0view0`, `functions.exec_command`, `curl`, `node`, `wc`, `mcp__node_repl.js` | Yes | `web.open` returned hydrated shell; `node` fetch failed DNS; escalated `curl` saved `sc2_messages.html` to `/private/tmp`; dual cross-checks via `wc -m` and codePoints count; probed for `tiktoken` and `gpt-tokenizer`, unavailable; redirect to `platform.claude.com` surfaced in tool result; asked permission once; named `Test web retrieval`; 3 minutes 46 seconds |
| `GPT-5.5 Low` | 578,275 | ~145,000 | Display yes, `curl` no | same as Run 2 | `functions.exec_command`, `curl`, `web.run`, `web.open`, `wc`, `tail`, `grep` | Yes | sandboxed `curl` failed DNS first, fell back to `web`, then approved direct retry succeeded; saved `sc-2-anthropic-messages.html` to `/private/tmp`; terminal display reported `134804 tokens truncated` mid-output, a new display-layer truncation surface; terminal also reported `Original token count: 144884`; asked permission twice; named `Test web retrieval`; 52 seconds |
| `GPT-5.5 Medium` | 2,693 visible, reported as 140 lines | ~500 to 700 visible | Yes | `* Terms of service: Consumer * Usage policy` | `web.run`, `web.open` | No | uniquely never used `curl`; single `web` retrieval accepted as final despite recognized incompleteness; explicitly reported redirect to `platform.claude.com`; content dominated by navigation and `Loading...` placeholders; named `Test web retrieval`; 31 seconds |
| `GPT-5.5 High` | 578,274 | ~144,600 | `curl` no, `web.open` partial | same as Run 2 | `web.open`, `curl`, `wc`, `tail`, `head`, `file`, `rg`, `multi_tool_use.parallel` | Yes | `web.open` stalled at `Loading...` state after redirect; sandboxed `curl` failed DNS, escalated fetch saved `sc2_response.html` to `/private/tmp`; `file` classified payload as HTML document text with very long lines, `47776`; three content presence searches grounded the completeness call; `rg` fence pattern hit shell quoting error; asked permission once; uniquely named `Fetch Anthropic messages docs`; 1 minute 12 seconds |
| `GPT-5.5 Extra High` | 2,693 | ~674 | Yes | `.com \n *` | `web.run`, `open`, `mcp__node_repl.js` | No | uniquely for `GPT-5.5` never used `curl`, deliberately declined a second network fetch; precise counting of received extraction via `node_repl`, codepoints, utf16, bytes, estimated tokens; `Loading...` placeholders located at lines 21 to 76 then footer navigation; redirect source link shown; named `Test web retrieval`; 1 minute 38 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported on the raw path. Five runs retrieved the full ~578,000 char payload via escalated `curl` with verified closing tags, far past the proposed
10 to 100KB ceiling. The `web.open` surface consistently cut at roughly 140 rendered lines regardless of payload size, which points at a line-count extraction
ceiling rather than a character ceiling. The three web-only runs returned excerpts of roughly 2,700 to 6,000 chars, sized by line count, not bytes.

**Combined verdict: `H1` no. No character ceiling on the raw fetch path. The `web.open` cutoff is better explained by a fixed line ceiling near `L140`, consistent with the line ceiling friction note candidate.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Escalated fetches retrieved ~145,000 tokens intact, well past the proposed 2,000-token threshold. Web-only runs measured visible excerpts at
roughly 500 to 700 tokens, below the threshold rather than at it, again consistent with the line ceiling sizing the output. Token estimates remained a rough
4 chars/token heuristic throughout; `GPT-5.4-Mini Extra High` probed for tokenizer packages and found none available. Run 5 surfaced a distinct token-denominated
truncation in the terminal display layer, `134804 tokens truncated`, which truncates what's shown, not what's retrieved.

**Combined verdict: `H2` no. No token ceiling on retrieval. The display layer truncates in token units, a separate mechanism from retrieval truncation.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Partially supported, with a competing explanation. Every `web.open` cutoff landed on structurally clean territory, footer links, navigation, or `Loading...`
placeholder bands, never mid code block. `GPT-5.5 Extra High` mapped the placeholders to lines 21 to 76 inside an otherwise intact shell. But a fixed line
ceiling that consistently lands past the page chrome mimics structure awareness without being it, and no run produced a cut at an arbitrary byte position that
would falsify the line ceiling explanation. The raw `curl` payload was HTML, not Markdown, so Markdown boundary assessment doesn't apply to the raw path.

**Combined verdict: `H3` partially. Cut points appear structurally clean but are indistinguishable from a fixed line extraction window. The hydrated shell never contained the docs prose to truncate.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Supported. The two-tier sandboxed/escalated network pattern dominated: `T1` runs largely resolved `docs.anthropic.com` directly while every `T2` raw fetch
first hit a sandboxed DNS failure and required permission-escalated access. `T1` `GPT-5.4-Mini High` deployed Browser Use with a `tab.*` Playwright toolchain;
no `T2` run had browser tooling available, consistent with the Browser Use friction note. Strategy inversions appeared at matched levels: `T1` `GPT-5.5 Medium`
ran roughly 11 `curl`-centric commands while `T2` `GPT-5.5 Medium` used `web` once and stopped. The one convergence was `GPT-5.5 Extra High`, where
both tracks deliberately skipped `curl` and measured only the received extraction, suggesting model disposition dominates surface effects at that level.

Raw payload sizes differ across tracks, roughly 512,000 to 520,000 chars in `T1` against ~578,000 chars in `T2`, and drifted slightly within `T2` itself,
578,233 to 578,275 across runs. A content update to the endpoint between collection windows is the most parsimonious explanation for the cross-track gap, and the
within-cycle drift confirms the payload is dynamic. Size comparisons across tracks aren't attributable to surface behavior.

**Combined verdict: `H4` yes. Network sandboxing, tool availability, and escalation requirements differ materially by surface. Payload size differences carry the page-update caveat.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported. Five runs self-initiated multi-step retrieval chains after recognizing the `web` result as incomplete: fallback fetches, permission escalation,
local saves, and measurement passes, all unprompted. That's adaptive multi-step retrieval. But no run chunked or paginated content, and the chains served verification
rather than fuller extraction of the rendered surface. Two runs, `GPT-5.5 Medium` and `GPT-5.5 Extra High`, recognized incompleteness and made no retrieval adaptation
at all, and `GPT-5.4-Mini Low` let its failed `curl` stand without escalation.

**Combined verdict: `H5` partially. Multi-step retrieval adaptation is common but chunking and pagination never appeared. Three of eight runs made no adaptation after a failed or partial fetch.**

---

## Emergent Findings

1. **The endpoint no longer serves an ~80KB docs page; it returns a ~578,000 char hydrated HTML/Next.js app shell.** Every successful raw fetch
confirmed scripts and embedded routing data rather than readable API reference prose. The Messages API content the test designed around isn't
present in the raw payload, it loads client-side after hydration.

2. **The URL redirects from `docs.anthropic.com` to `platform.claude.com`.** Only three runs surfaced the redirect explicitly,
`GPT-5.4-Mini Extra High`, `GPT-5.5 Medium`, and `GPT-5.5 High`. No run inspected HTTP headers, contrasting with BL-2 where Run 3 surfaced full
header detail.

3. **The `web.open` line ceiling held at roughly 140 lines across all runs that used it.** Reported values clustered at `L139`, 140 lines, and
`L140` regardless of model or level. This extends the line ceiling friction note candidate from BL-1 with the most consistent evidence yet.

4. **`Loading...` placeholders occupy a fixed band inside the rendered shell.** `GPT-5.5 Extra High` located them at lines 21 to 76, framed by
intact navigation above and footer below. No run examined the placeholders or attempted to explain the missing Messages API prose; agents noted
the shell and pivoted.

5. **A third truncation surface appeared: terminal display truncation denominated in tokens.** Run 5's terminal reported `134804 tokens truncated`
and `Original token count: 144884` mid-output. This is distinct from retrieval truncation and from the `web.open` line ceiling, and the agent
correctly worked around it by measuring from the saved file.

6. **Report truncation observed for the first time.** `GPT-5.4-Mini High` delivered its report missing item 8 on surface awareness, alongside a
thought panel error message that's also rarely visible. Given the documented post-hoc session alteration pattern, a later duplicate render could
silently complete such a report, making capture timing matter even more.

7. **The two-tier sandboxed/escalated network pattern held wherever raw fetches attempted but wasn't universal.** Five runs escalated successfully.
`GPT-5.4-Mini Low` let its sandboxed DNS failure stand without requesting escalation, and the two web-only `GPT-5.5` runs never attempted a raw fetch.

8. **`GPT-5.5` showed the widest strategy variance in the cycle.** Low and High escalated to full raw fetches, Medium accepted a single truncated
`web` result, and Extra High deliberately measured only the received extraction. `GPT-5.4-Mini` was more uniform, with three of four runs converging
on the escalated `curl` path.

9. **Raw payload char counts drifted within the cycle, 578,233 to 578,275.** The variance across same-day runs confirms dynamic payload content and
rules out exact char count matching as a cross-run integrity check for this URL, unlike BL-2's stable 5,805.

10. **Tokenizer packages remain unavailable in the `T2` sandbox.** `GPT-5.4-Mini Extra High` searched `npm` globals for `tiktoken` and `gpt-tokenizer`
without success. All token figures are 4 chars/token estimates.

11. **No artifact renaming or filename collision risk this cycle, uniquely.** The four artifact-producing runs wrote four distinct filenames to
`/private/tmp`: `sc2-anthropic-messages.html`, `sc2_messages.html`, `sc-2-anthropic-messages.html`, and `sc2_response.html`. This contrasts with the
`BL-2` collision pattern.

12. **Double identical report output continued.** The post-hoc duplicate render pattern documented in BL-1 and BL-2 persisted through this cycle,
alongside timer drift. Screenshot capture at run time remains the primary record per established methodology.

13. **Truncation reports were mostly mixed and split by retrieval path.** Runs that reached the raw body reported no for `curl` and partial for
`web.open`. Web-only runs reported yes. The split is consistent and interpretable, but the surface produces no single truncation answer for this URL,
which is itself a retrieval-characterization finding.

14. **Test naming held at `Test web retrieval` for seven of eight runs.** `GPT-5.5 High` uniquely broke the pattern with `Fetch Anthropic messages docs`.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Pass | `PASS, web_open_L139_excerpt + curl_dns_fail_no_escalation + truncation_yes + no_artifact + 18 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_bypassed + curl_578234_chars + single_compound_command + inline_node_measurement + no_artifact + 49 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, web_open_140_lines + node_dns_fail_thought_panel_error + curl_578233_chars + report_truncated_item_8_missing + sc2_anthropic_messages_html_private_tmp + 1 minute 42 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, web_open_shell + curl_578234_chars + dual_count_cross_check + tiktoken_false + redirect_surfaced + sc2_messages_html_private_tmp + 3 minutes 46 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, curl_dns_fail_first + web_fallback + approved_retry_578275_chars + display_truncation_134804_tokens + sc_2_anthropic_messages_html_private_tmp + 52 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, web_only + no_curl + 140_line_shell_accepted + redirect_reported + truncation_yes + no_artifact + 31 seconds` |
| `GPT-5.5 High` | Pass | `PASS, web_open_loading_state + curl_578274_chars + content_presence_checks_x3 + rg_quoting_error + sc2_response_html_private_tmp + unique_test_name + 1 minute 12 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_only + no_curl_deliberate + node_repl_precise_count_2693_chars + loading_lines_21_to_76 + truncation_yes + no_artifact + 1 minute 38 seconds` |
