# OP-1 Summary

## Test Conditions

|                 | **OP-1** |
| --------------- | -------- |
| URL             | `https://en.wikipedia.org/wiki/Machine_learning#History` |
| Expected size   | ~40KB rendered article text; raw HTML ~743KB; fragment `#History` is client-side only, doesn't scope the HTTP response |
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
| `GPT-5.4-Mini Low` | ~100k to 130k visible est. | ~25k to 32k | Implied, no explicit report | `` `Machine learning \n90 languages Add topic` `` | `web.open`, `curl`, `node` | No | `web.open` clipped at `L304` of `1941`; `curl` and `node fetch` both failed DNS; char and token counts are agent estimates from rendered view; truncation implied by tail content, not explicitly reported; named `Test web retrieval`; 28 seconds |
| `GPT-5.4-Mini Medium` | ~40,000 | ~10,000 | `web.open` yes at `L304`, full page recoverable | `Machine learning \n90 languages Add topic` | `web.open`, `turn0view0` through `turn3view0`, `curl`, `mcp__node_repl.js` | No | first confirmed auto-chunking in `T2` testing; `web.open` clipped at `L304`, subsequent calls paged to `L1940`; `curl` failed DNS, no escalation; `Browser` attempted, returned `Browser is not available: iab`; suggests chunking triggered by `curl` failure; asked permission once; named `Test web retrieval`; 1 minute 53 seconds |
| `GPT-5.4-Mini High` | ~58,000 | ~14,000 | `web.open` implied, no explicit report | `ine learning\nL1939: \nL1940: 90 languages Add topic` | `web.open`, `turn1view0`, `turn2view0`, `mcp__node_repl.js` | No | `web.open` clipped at `~L304`, second call reached `L1940`; `fetch` and `curl` both failed; truncation reported as no at page level, but `web.open` display clipping acknowledged; named `Test web retrieval`; 2 minutes 23 seconds |
| `GPT-5.4-Mini Extra High` | 133,083 readable text, 743,312 raw HTML | ~33k readable | `web.open` display only, raw fetch no | `f contents Machine learning 90 languages Add topic` | `web.open`, `turn0view0`, `turn1view0`, `curl`, `xmllint`, `perl`, `wc`, `tail`, `mcp__node_repl.js` | No | most sophisticated toolchain in cycle; `curl` succeeded after asking permission once; `xmllint` used for tag stripping, `perl` for whitespace normalization; `Browser` attempted, returned `Browser is not available: iab`; char counts from actual fetched content rather than agent inference; named `Test web retrieval`; 6 minutes 42 seconds |
| `GPT-5.5 Low` | ~45,000 | ~11k to 12k | Yes at `L556` | `hine learning[] .[ ]` | `web.open`, `web`, `open` | No | single `web.open` call only, no commands executed; truncated mid-article in "Data compression" subsection; `#History` fragment ignored; named `Test web retrieval`; 11 seconds |
| `GPT-5.5 Medium` | 740,370 chars, 743,312 bytes via `curl` | ~185,000 | `curl` no, `web.open` display yes at `L556` | `t explicit instructions"}</script>\n</body>\n</html>` | `web.open`, `web`, `curl`, `perl`, `functions.exec_command` | No | dual-path measurement; `web.open` clipped at `L556`, `curl` returned full raw HTML with clean closing tags; `perl` used for precise char counting and last-50 extraction; asked permission once; named `Fetch Wikipedia machine learning`; 39 seconds |
| `GPT-5.5 High` | 740,370 chars, 743,312 bytes via `curl` | ~185,000 | `curl` no | `t explicit instructions"}</script>\n</body>\n</html>` | `web.run`, `web.open`, `curl`, `wc`, `tail`, `multi_tool_use.parallel`, `functions.exec_command` | Yes | uniquely saved `/private/tmp/op1_machine_learning_response.html` (743 KB); sandboxed `curl` failed DNS first, escalated retry succeeded; `#History` fragment noted as client-side only; asked permission once; named `Test web retrieval OP-1`; 1 minute 8 seconds |
| `GPT-5.5 Extra High` | ~44k to 50k visible | ~11k to 13k | Yes at `L556` | `ompression $ Machine learning[] .[ ]` | `web.run`, `web.open`, `open`, `turn0view0` | No | no commands executed, unique for Extra High across either track; single `web.open` call accepted as final; truncated mid-article in "Data compression" section; content type `text/html`, ref `turn0view0`; named `Fetch Wikipedia metrics`; 1 minute 13 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Partially supported on the `web.open` path, not supported on the raw fetch path. Two runs retrieved the full raw HTML via escalated `curl`, measuring ~743KB with clean closing tags,
far past any 10 to 100KB ceiling. The `web.open` surface showed a consistent line ceiling rather than a character ceiling, but the ceiling differed by model: all four `GPT-5.4-Mini`
runs clipped at `~L304`, while all four `GPT-5.5` runs clipped at `~L556`. That model-dependent split argues against a single fixed character limit and toward a line-count window
sized differently per model or reasoning configuration.

**Combined verdict: `H1` partially. No character ceiling on the raw fetch path. The `web.open` line ceiling is real but model-dependent, not a fixed cross-model character limit.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Runs that escalated to `curl` retrieved ~185,000 tokens of raw HTML, far past the proposed threshold. Runs relying on `web.open` alone estimated 11,000 to 32,000
visible tokens depending on model, also well above 2,000. No run produced a cutoff at or near the 2,000-token mark. Token estimates throughout used a rough 4 chars per token heuristic;
no tokenizer packages were available in the sandbox.

**Combined verdict: `H2` no. No 2,000-token ceiling on any retrieval path.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Partially supported, with a competing explanation. Every `web.open` cutoff fell near consistent line positions rather than at arbitrary byte positions, and the tail content
across runs ended with navigation fragments rather than mid-prose cuts in the article body. However, the retrieved content rendered plain text from HTML, not Markdown, so Markdown
boundary assessment doesn't directly apply. The consistent `~L304` and `~L556` ceilings per model are better explained by fixed line windows than by structure awareness. The `curl`
path returned raw HTML with clean closing tags in every successful run, which is structurally complete but also not Markdown.

**Combined verdict: `H3` partially. Cut points are consistent and not arbitrary, but the model-dependent line ceiling is a more parsimonious explanation than structure awareness.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Supported. Tool availability differed materially by surface: `Browser` attempted twice in `T2` and returned `Browser is not available: iab` both times, consistent with the `Browser Use`
Friction Note, while `T1` runs had no such constraint. The sandboxed DNS failure pattern appeared in `T2` raw fetch attempts but didn't dominate `T1` in the same way. The `web.open`
line ceiling also appears surface-independent for the `web.open` path specifically, as `T1` and `T2` runs for matching models truncated at similar line positions, but the strategy used
to recover from that truncation differed substantially. `T1` runs tended toward `curl` with more commands from the start, while `T2` runs relied on `web` more heavily and attempted
`Browser` before falling back. The most striking convergence point was `GPT-5.5 High`, where both tracks used escalated `curl`, measured similar byte counts, and noted the `#History`
fragment as client-side only, suggesting model disposition can override surface effects at higher reasoning levels.

**Combined verdict: `H4` yes. Tool availability, network sandboxing, and default retrieval strategy differ by surface. Convergence at High and Extra High levels suggests model reasoning partially offsets surface constraints.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially supported. `GPT-5.4-Mini Medium` is the only run that produced clear auto-chunking behavior, issuing multiple sequential `web.open` calls (`turn0view0` through `turn3view0`)
to page through the full article; `curl` failure may trigger rather than default reasoning. `GPT-5.4-Mini High` and Extra High issued two `web.open` calls each but
didn't produce a systematic pagination chain. The remaining four runs issued a single retrieval event and stopped, including `GPT-5.5 Extra High`, the highest reasoning level, which
explicitly declined a second fetch.

**Combined verdict: `H5` partially. Chunking appeared once across eight runs and may have been `curl`-failure-triggered rather than a default behavior. No run produced systematic content pagination.**

---

## Emergent Findings

1. **The `#History` URL fragment was ignored across all eight runs.** Every agent retrieved the full `Machine_learning` page HTML rather than scoping to the History section.
This is technically correct HTTP behavior since URL fragments are client-side only, but no run commented on the implications for the test design or attempted to isolate the
History section content. `T1` behavior was identical. The fragment appears to be a non-factor for agent retrieval across both tracks.

2. **The `web.open` line ceiling is model-dependent, not uniform.** All four `GPT-5.4-Mini` runs clipped at `~L304`, and all four `GPT-5.5` runs clipped at `~L556`. The split
is clean and consistent, making this the strongest evidence yet for a per-model or per-reasoning-configuration line window rather than a surface-level ceiling. This extends
and sharpens the line ceiling friction note candidate from BL-1.

3. **`Browser` attempted twice and failed both times with `Browser is not available: iab`.** Both attempts came from `GPT-5.4-Mini` runs at Medium and Extra High levels.
No `GPT-5.5` run attempted `Browser`. This is consistent with every prior `T2` cycle observation and confirms the friction note on Browser Use unavailability on the VS Code-Codex
extension surface.

4. **Artifact creation was rare and typically metric-driven.** Only `GPT-5.5 High` wrote a file to `/private/tmp`, saving the full raw HTML response as
`op1_machine_learning_response.html` (743 KB). This contrasts with `T2` BL-1 and BL-2 cycles where write-save-calculate paths appeared in roughly half of runs.
`GPT-5.4-Mini Extra High` used shell instrumentation extensively but didn't write a saved artifact, which is unusual for that level.

5. **`curl` DNS failures followed the two-tier sandboxed/escalated pattern established in prior cycles.** Sandboxed DNS failed on first attempt in multiple runs. Some runs
escalated successfully with permission, others let the failure stand without requesting escalation. `GPT-5.4-Mini Low` and Medium both hit DNS failures and didn't escalate.
`GPT-5.5 High` escalated after sandboxed failure. The escalation decision appears to vary by model and level rather than being consistently applied.

6. **Named failures weren't examined.** Across runs that hit `curl` DNS failures, `fetch failed` responses, or `Browser is not available: iab` errors, agents consistently
named the failure and moved on without inspecting error detail or attempting to interpret the error message. This pattern has appeared in prior `T2` cycles and persists here.

7. **Test naming was more consistent than prior cycles but not uniform.** Six of eight runs used `Test web retrieval`. `GPT-5.5 High` used `Test web retrieval OP-1` and
`GPT-5.5 Extra High` used `Fetch Wikipedia metrics`. The `Test web retrieval` default continues to dominate across `T2` testing.

8. **Rollout log sizes ranged from 22KB to 308KB.** The `GPT-5.4-Mini Extra High` run produced the largest log (308KB), consistent with its extended toolchain. `GPT-5.5 Low`
produced the smallest (22KB), consistent with its single `web.open` call and no commands. Log size correlates roughly with command count and total tool activity.

9. **Timer drift and double-rendering of output reports continued.** Chat timer and rollout log timer disagreed by a few seconds across several runs. The post-hoc duplicate
render pattern documented in `BL-1` and `BL-2` persisted. Screenshot capture at run time remains the primary record per established methodology.
See [Seeing Double](https://rhyannonjoy.github.io/agent-ecosystem-testing/blogs/seeing-double) for the documented pattern.

10. **`GPT-5.5 Extra High` was the only run to execute zero commands.** This is unique not just for the Extra High intelligence level but across all eight runs and across prior
`T2` cycles, where Extra High runs consistently produce the highest command counts. The run completed the full `OP-1` report from a single `web.open` call, accepted truncation at
`L556` without attempting recovery, and explicitly declined a second network fetch. Model disposition appears to have overridden the default escalation pattern at this level.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Low` | Pass | `PASS, web_open_L304_implied_truncation + curl_dns_fail_no_escalation + node_fetch_dns_fail + no_artifact + 28 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_open_L304 + auto_chunk_turn0_to_turn3 + curl_dns_fail_no_escalation + browser_unavailable_iab + no_artifact + 1 minute 53 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, web_open_L304 + two_web_open_calls_to_L1940 + fetch_fail + curl_fail + no_artifact + 2 minutes 23 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, web_open_L304 + curl_743312_bytes + xmllint_perl_instrumentation + browser_unavailable_iab + no_artifact + 6 minutes 42 seconds` |
| `GPT-5.5 Low` | Pass | `PASS, web_open_L556_truncated + single_call_no_recovery + no_commands + no_artifact + 11 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, web_open_L556 + curl_743312_bytes + perl_measurement + dual_path_metrics + no_artifact + 39 seconds` |
| `GPT-5.5 High` | Pass | `PASS, web_open_partial + curl_dns_fail_escalated + curl_743312_bytes + op1_machine_learning_response_html_private_tmp + 1 minute 8 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_open_L556_truncated + zero_commands + no_curl_deliberate + single_call_accepted + no_artifact + 1 minute 13 seconds` |
