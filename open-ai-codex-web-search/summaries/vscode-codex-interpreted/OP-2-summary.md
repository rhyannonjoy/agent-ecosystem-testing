# OP-2 Summary

## Test Conditions

|                 | **OP-2** |
| --------------- | -------- |
| URL             | `https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array` |
| Expected size   | ~120KB |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox, `/private/tmp` writable, project accessible as working directory |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.5`, `GPT-5.4-Mini` |
| Runs            | 8 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Low` | ~105,000 visible est. | ~26,000 | No, explicit report | `able under [cite]226†a Creative Commons license[] .` | `web.open`, `web.run`, `curl` | No | `curl` returned 0 bytes, reported as a sandbox failure rather than examined, no DNS detail surfaced at this level, `web.open` reached the footer and license line, agent perceived this as complete, named `Test MDN retrieval output`, 46 seconds |
| `GPT-5.4-Mini Medium` | ~41,000 visible | ~10,000 | Yes, explicit report | `L590: Adds and/or removes elements from an array.` | `web.open`, `curl`, `node_repl`, `fetch` | No | `curl` returned 0 bytes, didn't ask permission to escalate, cutoff landed mid-section in `Array.prototype.splice()`, agent correctly identified the response as incomplete against the page's reported `Total lines: 1268`, named `Fetch MDN Array page`, 1 minute 27 seconds |
| `GPT-5.4-Mini High` | ~70,000 visible | ~17,000 | Yes, mixed report | `Content available under a Creative Commons license.` | `web.open`, `curl`, `node_repl`, browser bootstrap | No | `curl` failed with DNS resolution, didn't ask permission, browser bootstrap attempted and returned `Browser is not available: iab`, first `web.open` chunk cut off near `Array.prototype.splice()`, a follow-up chunk reached the footer at `L1240` to `L1267`, named `Test web retrieval`, 3 minutes 35 seconds |
| `GPT-5.4-Mini Extra High` | 241,720 via direct `curl` | ~60,000 | No for raw fetch, yes for `web.open` display | `able under [cite]226†a Creative Commons license[] .` | `web.run`, `web.open`, `curl`, `node_repl`, `python3`, browser bootstrap | Yes | uniquely wrote-saved `/private/tmp/mdn_array.html`, 242KB, asked permission to use `curl` for the first time across this model's runs, first `web.open` chunk stopped at `L318`, a later chunk reached `L1267` and the footer, exposed full HTTP response headers in the thought panel but didn't save them as an artifact, browser bootstrap returned `Browser is not available: iab`, named `Fetch MDN Array page`, 7 minutes 59 seconds |
| `GPT-5.5 Low` | Not exposed, page reported `Total lines: 1268` | ~18,000 to 25,000 | Yes, explicit report | `.` | `web`, `web.run`, `open` | No | only used the `web` pipeline, no terminal commands executed, first `web.open` chunk showed `L0` to `L591`, a second chunk near the end showed `L903` to `L1267`, leaving a gap of `L592` to `L902` unrendered between the two visible chunks, named `Test web retrieval`, 18 seconds |
| `GPT-5.5 Medium` | 241,720 via direct `curl` | ~60,430 | No for `curl` body, yes for `web.open` display | `able under [cite]226†a Creative Commons license[] .` | `web.run`, `web.open`, `curl`, `tail`, `wc`, `file` | Yes | asked permission to use `curl`, uniquely wrote-saved `/private/tmp/mdn_array_op2.html`, 242KB, but didn't report the write-save-calculate strategy explicitly, `web.open` window stopped around `L591`, a follow-up open reached the footer through `L1267`, named `Test web retrieval response size`, 41 seconds |
| `GPT-5.5 High` | 241,720 via direct `curl` | ~60,430 | No for `curl` body, yes for `web.open` display | `able under [cite]226†a Creative Commons license[] .` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `rg`, `od` | Yes | asked permission to use `curl` once, wrote-saved `/private/tmp/op2_mdn_array.html`, 242KB, `web.open` visible output stopped at `L591` against a reported `Total lines: 1268`, no second `web.open` chunk documented, named `Fetch MDN Array page`, 1 minute 17 seconds |
| `GPT-5.5 Extra High` | 241,720 via direct `curl` | ~60,430 | No for `curl` body, yes for `web.open` display | `able under [cite]226†a Creative Commons license[] .` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `file`, `multi_tool_use.parallel` | Yes | asked permission to use `curl` once, wrote-saved `/private/tmp/op-2-mdn-array.html`, 242KB, first `web.open` chunk stopped at `L591`, a follow-up chunk reached the footer through `L1267`, run ended early when the free tier rate limit hit, named `Fetch MDN Array page`, 2 minutes 41 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. Four runs escalated to a direct `curl` fetch and each measured 241,720 characters with closing `</body>` and `</html>` tags intact, far past any 10 to 100KB ceiling.
No two runs that lacked a raw fetch path produced a matching character count either, `GPT-5.4-Mini Low` estimated ~105,000, `GPT-5.4-Mini Medium` estimated ~41,000, and `GPT-5.4-Mini High`
estimated ~70,000, all from the same URL. That spread argues against a single fixed character limit governing the `web.open` display, and the runs with a successful raw fetch confirm
there's no server-side or sandbox-level byte ceiling either.

**Combined verdict: `H1` no. No character ceiling on the raw fetch path, and no consistent character ceiling across `web.open`-only runs.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Runs that escalated to `curl` retrieved roughly 60,000 tokens of raw HTML, far past the proposed threshold. Runs relying on `web.open` alone estimated 10,000 to 26,000
visible tokens depending on model and level, also well above 2,000. No run produced a cutoff at or near the 2,000-token mark. Token estimates throughout used a rough 4 chars per token
heuristic, no tokenizer packages were available in the sandbox.

**Combined verdict: `H2` no. No 2,000-token ceiling on any retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Partially supported, with a competing explanation. The raw `curl` body was never truncated in any of the four successful escalations, so structural boundary assessment doesn't apply
there, the response is HTML, not Markdown, and ends cleanly with closing tags. On the `web.open` path, cutoffs consistently landed mid-section, most often inside or near
`Array.prototype.splice()`, rather than at a clean section or Markdown boundary. `GPT-5.5 Low`'s gap between `L592` and `L902` is the clearest evidence against structure awareness,
an arbitrary skip rather than a boundary-respecting jump. Several runs did eventually reach the footer through a follow-up `web.open` call, which suggests the tool is capable of
reaching a true structural endpoint, but the initial cut isn't choosing that endpoint deliberately.

**Combined verdict: `H3` partially. Cutoffs aren't tied to Markdown or section boundaries on the first chunk, but follow-up chunks can reach the document's actual end.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Partially supported -  model-level dependent. At `Low` and `Medium`, `T2` showed sharp divergence from `T1`. `GPT-5.4-Mini Low` reported a `curl` failure as a sandbox issue with no DNS detail,
while `T1` at the same level didn't escalate at all. `GPT-5.4-Mini Medium` didn't ask permission to escalate `curl`, while `T1` asked permission three times. `GPT-5.5 Low` relied
exclusively on `web.run` with no `curl` attempt and no permission request, while `T1` bypassed `web` entirely and used `curl` directly with permission asked three times. At High
and above, the pattern reversed toward convergence. `GPT-5.4-Mini High` showed `curl` attempting and failing without permission, contrasted against `T1`'s permission-gated approach,
but `GPT-5.4-Mini Extra High` successfully completed a raw `curl` fetch for the first time across this model's runs, something `T1` never achieved at any level. `GPT-5.5 Medium`,
`GPT-5.5 High`, and `GPT-5.5 Extra High` all showed close alignment with their `T1` counterparts, `curl` blocked then succeeded with permission, `web.open` independently windowed
around the same line range, suggesting model disposition can override surface effects at higher reasoning levels within this model.

**Combined verdict: `H4` mixed. Surface effects are strongest at lower reasoning levels and for `GPT-5.4-Mini`, while `GPT-5.5` at Medium and above showed consistent behavior
across both tracks, indicating model and level matter as much as surface alone.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported. Five of eight runs showed at least a second `web.open` call reaching further into the document after an initial windowed cutoff, `GPT-5.4-Mini High`,
`GPT-5.4-Mini Extra High`, `GPT-5.5 Low`, `GPT-5.5 Medium`, and `GPT-5.5 Extra High` all paged from an initial cutoff to a later chunk reaching or approaching the footer.
None of these formed an extensive multi-step chain comparable to `T1`'s `GPT-5.4-Mini Medium` run, which issued four sequential calls, this was typically a single follow-up jump.
`GPT-5.4-Mini Low` and `GPT-5.5 High` showed no second `web.open` call, accepting the first windowed view or switching to `curl` instead of paginating within `web.open`.
`GPT-5.4-Mini Medium` also showed no recovery attempt, leaving the cutoff at `L590` unaddressed.

**Combined verdict: `H5` partially. Single-jump pagination appeared in most runs, but no run reproduced `T1`'s extensive multi-step auto-chunking pattern.**

---

## Emergent Findings

1. **Artifact creation was infrequent and clustered by model.** Only four of eight runs wrote a saved file beyond the standard rollout log, `GPT-5.4-Mini Extra High`,
`GPT-5.5 Medium`, `GPT-5.5 High`, and `GPT-5.5 Extra High`. All four used the same pattern, escalate to `curl`, write the response to `/private/tmp`, then calculate metrics
against the saved file. No `GPT-5.4-Mini` run below Extra High produced an artifact.

2. **The `web.open` window consistently centered near `L590` for runs that didn't escalate or that escalated and still checked the display path.** `GPT-5.4-Mini Medium` cut
at `L590`, `GPT-5.5 Low` cut at `L591`, `GPT-5.5 Medium` cut at `L591`, `GPT-5.5 High` cut at `L591`, and `GPT-5.5 Extra High` cut at `L591`. `GPT-5.4-Mini High` and
`GPT-5.4-Mini Extra High` cut earlier, near `L317` and `L318`. This is consistent with the `T1` `OP-1` observation that the line ceiling is model-dependent, and extends it,
suggesting `GPT-5.5` may default to a wider window than `GPT-5.4-Mini` at lower reasoning levels for this surface.

3. **Failure modes were rarely examined.** Across runs that hit `curl` failures, whether reported as zero bytes, a sandbox block, or DNS resolution failure, no run inspected
the underlying error in detail before moving to a workaround. This matches the pattern from `OP-1` and prior cycles, named failures aren't interpreted by default.

4. **`Browser` was attempted twice and failed both times with `Browser is not available: iab`.** Both attempts came from `GPT-5.4-Mini` runs, at High and Extra High. No
`GPT-5.5` run attempted `Browser`. This continues the pattern from `BL-1`, `BL-2`, and `OP-1` and reinforces the Friction Note on Browser Use unavailability on the VS Code-Codex
extension surface.

5. **Test naming showed no dominant default for this cycle.** Names included `Test MDN retrieval output`, `Fetch MDN Array page` three times, `Test web retrieval` twice, and
`Test web retrieval response size`. `Fetch MDN Array page` was the closest to a repeated default, unlike `OP-1`'s strong lean toward `Test web retrieval`.

6. **Total tokens per run, from the rollout audit, ranged from 33,160 to 849,246.** `GPT-5.4-Mini Extra High` used by far the most at 849,246, consistent with its
14 function calls and longest runtime. `GPT-5.5 Low` used the fewest at 33,160, consistent with zero function calls and a single `web.open` event. Rollout log size in
KB tracks loosely with token count but isn't a reliable proxy on its own, `GPT-5.4-Mini High` ran 5 function calls for 238,073 tokens while `GPT-5.5 High` ran 10 function
calls for 163,678 tokens, so command count alone doesn't predict token volume either.

7. **The rollout audit's `function_calls` count mostly matches commands observed in chat, with one exception.** Across seven of eight runs, the audited function call
count lines up with the number of shell commands counted from the chat thought panel. `GPT-5.5 High` is the outlier, the audit logs 10 function calls against 7 commands
visible in chat, suggesting some tool calls during that run weren't surfaced in the panel. This is consistent with the broader pattern that the chat display doesn't
fully represent everything the agent executed, and that the rollout log is the more complete record.

8. **Rollout duration consistently runs ahead of the chat-displayed timer, by 3 to 14 seconds depending on run.** `GPT-5.4-Mini Low` showed 51.7 seconds in the audit
against 46 seconds in chat, `GPT-5.5 High` showed 88.1 seconds against 77 seconds in chat. This matches the timer drift pattern described in
[Seeing Double](https://rhyannonjoy.github.io/agent-ecosystem-testing/blogs/seeing-double), where the chat's live counter and the rollout's `duration_ms` measure
different endpoints rather than disagreeing due to error.

9. **The free tier rate limit was reached during `GPT-5.5 Extra High`, the eighth run of this cycle.** `T1` completed roughly 261 runs on the desktop app without hitting a
limit, while `T2` hit a limit at approximately 40 runs into this extension-based track. As documented in
[Seeing Double](https://rhyannonjoy.github.io/agent-ecosystem-testing/blogs/seeing-double), the double-rendering pattern observed earlier in `T2` testing is a presentation
layer artifact confirmed byte-identical across the three rollout log copies, not a session re-trigger. Whether double-rendering contributes to reaching the rate limit faster
on this surface is worth further investigation, since the rendering bug itself doesn't write additional records to the log.

10. **HTTP response headers, when manually inspected for `GPT-5.4-Mini Extra High`, confirmed server-side completeness.** `content-length` and `x-goog-stored-content-length`
both reported 241,856 bytes, matching the locally measured `curl` download. This cross-check confirms truncation observed across this cycle is a client-side rendering or
windowing behavior, not a server or network-layer cutoff.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Pass | `PASS, web_open_no_explicit_truncation + curl_0_bytes_unexamined + footer_reached + no_artifact + 46 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_open_L590_truncated + curl_0_bytes_no_escalation_request + no_artifact + 1 minute 27 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, web_open_L317_chunk + second_chunk_to_L1267_footer + curl_dns_fail_no_permission + browser_unavailable_iab + no_artifact + 3 minutes 35 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, curl_241720_chars_first_success + web_open_L318_to_L1267 + headers_exposed_not_saved + browser_unavailable_iab + mdn_array_html_private_tmp + 7 minutes 59 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, web_open_L0_to_L591 + gap_L592_to_L902 + second_chunk_L903_to_L1267 + no_commands + no_artifact + 18 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, curl_241720_chars + web_open_L591_to_L1267 + write_save_calculate_unreported + mdn_array_op2_html_private_tmp + 41 seconds` |
| `GPT-5.5 High` | Pass | `PASS, curl_241720_chars + web_open_L591_no_second_chunk + op2_mdn_array_html_private_tmp + 1 minute 17 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, curl_241720_chars + web_open_L591_to_L1267 + rate_limit_hit_at_run_end + op-2-mdn-array_html_private_tmp + 2 minutes 41 seconds` |
