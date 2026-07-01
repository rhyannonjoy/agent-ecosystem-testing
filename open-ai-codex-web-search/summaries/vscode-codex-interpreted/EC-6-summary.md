# EC-6 Summary

## Test Conditions

|                 | **EC-6** |
| --------------- | -------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md` |
| Expected size   | ~60KB per prompt; actual confirmed 91,869 characters, 91,877 bytes via `curl`, ~23,000 tokens |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing` writable; `/private/tmp` also writable |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5` |
| Runs            | 13 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------- | ----------- | --------- | -------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Light` | 91,869 | ~23,000 | No | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command` with `curl`, `tee`, `wc`, `tail`, `sed` | Yes, `/private/tmp/ec6_spec.md` | named `Test web retrieval`; skipped `web` entirely; first `curl` attempt hit `0` bytes, retry succeeded; asked permission once; 29 seconds, rollout audit 34.5 seconds |
| `GPT-5.4-Mini Medium` | 91,869 | ~23,000 | No, streamed preview only | `— Notable exclusions with rationale (Appendix B).` | `curl`, `wc`, `tail`, `python3` via `functions.exec_command` | Yes, `/private/tmp/ec6_spec.md` | named `Test web retrieval SPEC fetch`; distinguished streamed terminal preview from saved body without prompting; asked permission twice; 1 minute 19 seconds, rollout audit 1 minute 24.1 seconds |
| `GPT-5.4-Mini High` run 1 | N/A, task incomplete | N/A | Indeterminate, no content retrieved | N/A | `web`, browser skill, `Playwright`, `Node fetch`, `curl` attempted without permission | No | named `Test web retrieval`; spun through five tool paths without landing on one; hit a model capacity message; over 3 minutes, timer didn't render |
| `GPT-5.4-Mini High` run 2 | 91,869 | ~23,000 | Body no, `web.open` yes at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `wc`, `tail`, `python3` | Yes, `/private/tmp/spec.XXXXXX.md` | named `Test web retrieval behavior`; explicitly re-fetched with `curl` after confirming the `web` clip; asked permission twice; 1 minute 40 seconds, rollout audit 1 minute 46.3 seconds |
| `GPT-5.4-Mini Extra High` | ~12,000 visible slice | ~3,000 | Yes, cut mid-line at `L54`, `curl` never succeeded | `to a page *about* `llms.txt`), JSON-LD metadata, ` | `web.open`, `curl` attempted repeatedly, `Playwright`, `Node fetch`, browser control skill | No | named `Test web retrieval`; the most expensive run in the cycle; sought the blob URL as an alternate path; 11 minutes 37 seconds, rollout audit 11 minutes 43.7 seconds |
| `GPT-5.4 Light` | 91,877 | ~23,000 | Body no, `web.open` yes at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `wc`, `tail`, `rg`, `od` | No | named `Test web retrieval`; asked permission for `curl` six times, well above the typical one or two; 1 minute 49 seconds, rollout audit 2 minutes 0.1 seconds |
| `GPT-5.4 Medium` | 91,869 | ~22,967 | Body no, `web.open` yes at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `python3` | No | named `Test web retrieval`; explicitly framed the `web` clip as a reason to escalate before running `curl`; asked permission four times; 1 minute 7 seconds, rollout audit 1 minute 14.5 seconds |
| `GPT-5.4 High` | 16,012 visible slice | ~4,003 | Yes, stopped at `L54`, `curl` never invoked | `xt` supposed to be the _solution_ to discovery. | `web.open`, `python3` | No | named `Test web retrieval`; the first run in the cycle to complete without touching `curl` at all; paginated with line offsets; 3 minutes 20 seconds, rollout audit 3 minutes 30.4 seconds |
| `GPT-5.4 Extra High` | ~26,000 visible slice | ~6,500 | Yes, stopped at `L54`, `curl` never invoked | `to a page _about_ `llms.txt`), JSON-LD metadata, ` | `web.open`, `rg`, local file read, `multi_tool_use.parallel` | No | named `Test web retrieval behavior`; checked the local repo for a matching copy of the spec before reporting; 4 minutes 15 seconds, rollout audit 4 minutes 26.3 seconds |
| `GPT-5.5 Light` | 91,869 | ~23,000 | Body no, `web.open` yes at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `wc`, `tail` | Claimed, `/private/tmp/ec6_spec.md`, contamination risk | named `Test web retrieval behavior`; asked permission once; 22 seconds, rollout audit 30.5 seconds |
| `GPT-5.5 Medium` | 91,869 | ~22,968 | Body no, `web.open` yes at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `wc`, `tail`, `rg`, `node` | Yes, `/private/tmp/ec6-spec.md` | named `Fetch SPEC.md`; asked permission once; 48 seconds, rollout audit 56.4 seconds |
| `GPT-5.5 High` | 91,869 | ~23,000 | Body no, `web.open` yes at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `wc`, `tail`, `rg` | Claimed, `/private/tmp/ec6-spec.md`, contamination risk | named `Test web retrieval`; asked permission once; no `Cache miss` language reported; 1 minute 4 seconds, rollout audit 1 minute 12 seconds |
| `GPT-5.5 Extra High` | 91,869 | ~22,968 | Body no, `web.open`/`web.run` yes at `L54` | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `curl`, `node` | Claimed, `/private/tmp/ec6_SPEC.md`, contamination risk | named `Test web retrieval`; asked permission once; 1 minute 43 seconds, rollout audit 1 minute 50.8 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported for the HTTP response body layer. Every run that completes a `curl` fetch, nine of the thirteen, lands
on the identical `91,869` characters or `91,877` bytes, well above any plausible ten to one hundred kilobyte ceiling.
The `web.open` surface tells a different story. Ten of the thirteen runs hit the exact same cutoff at line `54`,
right after `JSON-LD metadata,`, regardless of model or reasoning level. That's a fixed, repeatable ceiling in that
surface, distinct from the HTTP body layer it sits in front of.

**Combined verdict: `H1` no for the HTTP body. Partially to yes for the `web.open` surface, where a positionally
identical cutoff appears in ten of thirteen runs spanning every model and reasoning level in the cycle.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Every completed `curl` fetch returns roughly `23,000` tokens intact. Even the partial `web.open`
views that do get cut, in the `Extra High` `Mini` run and both uncurled `GPT-5.4 High` and `Extra High` runs, still
surface several thousand tokens before the clip lands. No run shows evidence of a ceiling anywhere near `2,000`
tokens on either layer.

**Combined verdict: `H2` no. Token counts on both the complete body and the partial surfaced views run far past the
proposed ceiling before any truncation occurs.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported. Wherever the `L54` cutoff appears, it lands mid sentence inside the same detection considerations
bullet in the `llms-txt-directive-html` section, never on a heading, list break, or code fence. This is the most
consistent negative evidence for `H3` across the entire cycle, since the cutoff point itself never moves.

**Combined verdict: `H3` no. The identical mid-sentence cutoff across ten runs rules out a structure-aware boundary.**

---

## `H4`: Surface context, VS Code-Codex Extension changes retrieval behavior against `T1`

Partially to yes. Most runs, nine of the thirteen, closely track `T1` in tooling, duration, and outcome, differing
mainly in minor tool sequencing. Four runs diverge sharply. The first `GPT-5.4-Mini High` attempt fails to complete
the task at all, something no `T1` `EC-6` run does across its full twenty runs. `GPT-5.4-Mini Extra High` takes
eleven minutes thirty seven seconds chasing `Playwright`, `Node fetch`, and browser control paths that never resolve.
`GPT-5.4 High` and `GPT-5.4 Extra High` both complete the test without ever invoking `curl`, relying entirely on
`web.open` and repeated view calls instead, a strategy no `T1` run uses.

**Combined verdict: `H4` partially to yes. Divergence concentrates at higher reasoning levels and in the `GPT-5.4`
subset, where three runs abandon or fail the `curl`-first strategy that dominates both `T1` and the rest of `T2`.**

---

## `H5`: Agent auto-chunks or auto-paginates

Partially. Support concentrates in four runs. The second `GPT-5.4-Mini High` run explicitly re-fetches after
confirming the `web` clip. `GPT-5.4-Mini Extra High` makes ten separate `web` search attempts before giving up.
`GPT-5.4 High` and `GPT-5.4 Extra High` both make multiple `web.open` calls with line offsets to view further into
the document after the initial clip. The remaining nine runs treat the clip as a signal to escalate to `curl` in a
single step rather than to paginate through the `web` surface itself.

**Combined verdict: `H5` partially. Pagination-like behavior appears in four runs concentrated at `High` and `Extra
High` reasoning levels, but doesn't generalize across the cycle.**

---

## Emergent Findings

1. **The `web.open` surface cuts off at the identical position, `L54`, right after `JSON-LD metadata,`, in ten of
thirteen runs.** The pattern holds across `GPT-5.4-Mini`, `GPT-5.4`, and `GPT-5.5`, and across every reasoning level
from `Light` through `Extra High`. No other test ID in the cycle shows a cutoff this consistent.

2. **No run reports a `Cache Miss` error the way nearly every attempting `T1` run does.** Instead, the `T2`
`web.open` surface returns a windowed, line-numbered view that clips at `L54` rather than failing outright. This is
a meaningfully different failure mode between the two surfaces even though the downstream effect, escalating to
`curl`, often looks the same.

3. **Two runs, `GPT-5.4 High` and `GPT-5.4 Extra High`, complete the test without ever invoking `curl`.** Both rely
entirely on `web.open` and repeated view calls to work around the clip, and both take substantially longer than any
`curl`-based run in the cycle, three minutes twenty seconds and four minutes fifteen seconds respectively.

4. **One run fails to complete the task entirely.** The first `GPT-5.4-Mini High` attempt spins through `curl`,
`Playwright`, `Node fetch`, and browser automation before the session ends on a model capacity message. This is the
only outright failure across the full `EC-6` cycle in either track.

5. **The two-tier sandboxed DNS failure followed by a permission-escalated retry appears in nearly every run that
uses `curl`.** Per established methodology, this counts as expected `T2` surface behavior rather than `H4` evidence
on its own.

6. **Artifact naming collisions recur across the cycle.** `GPT-5.4-Mini Light` and `GPT-5.4-Mini Medium` both write
to `/private/tmp/ec6_spec.md`. Three of the four `GPT-5.5` runs write to near identical filenames, `ec6_spec.md`,
`ec6-spec.md`, and `ec6_SPEC.md`, raising a contamination flag each time.

7. **Duration varies enormously and doesn't track cleanly with reasoning level.** `GPT-5.4-Mini Extra High` takes
eleven minutes thirty seven seconds, nearly seven times longer than the next most expensive run, driven by
exhausting every available tool path rather than reasoning depth on the content itself.

8. **`tiktoken` isn't installed in the workspace**, confirmed when `GPT-5.4-Mini Light` probes for it and gets a
`ModuleNotFoundError`. Every token estimate across the cycle relies on a characters divided by four heuristic
instead.

9. **Test naming varies more in this cycle than in the matched `T1` runs**, appearing as `Test web retrieval`,
`Test web retrieval SPEC fetch`, `Test web retrieval behavior`, and `Fetch SPEC.md` across otherwise similar runs.

10. **`multi_tool_use.parallel` appears once in this cycle, in `GPT-5.4 Extra High`.** No `GPT-5.5` run in this
cycle shows it, which breaks from the `EC-3` pattern where the identifier was exclusive to `GPT-5.5`. It does match
`T1`'s own `EC-6` finding that `GPT-5.4 Extra High` was the first run outside the `5.5` family to use it, so the
same model and reasoning level combination produces this identifier independent of track.

11. **Every run that completes a full `curl` fetch retrieves the identical underlying payload, but not every run
measures it the same way.** Runs that call `wc -m` or `python3`'s `len` report `91,869` characters distinct from
`91,877` bytes. `GPT-5.4 Low` only calls `wc -c`, so its report labels the byte count, `91,877`, as the character
count and never surfaces `91,869` at all. The measurement is consistent; the label attached to it isn't.

12. **Pagination-like behavior, multiple `web.open` calls or explicit line offset requests, concentrates at `High`
and `Extra High` reasoning levels.** No `Light` or `Medium` run in the cycle attempts to view further into the
document after hitting the initial clip; all of them escalate straight to `curl` instead.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Light` | Pass | `PASS, curl_91869_chars + no_web_used + no_truncation + ec6_spec_md_private_tmp + 29 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, curl_91869_chars + streamed_preview_distinguished_from_body + no_truncation + ec6_spec_md_private_tmp + 1 minute 19 seconds` |
| `GPT-5.4-Mini High run 1` | Fail | `FAIL, multi_tool_spin + curl_blocked_no_permission + playwright_and_node_fetch_failed + model_at_capacity + no_report + over 3 minutes` |
| `GPT-5.4-Mini High run 2` | Pass | `PASS, curl_91869_chars + web_open_clip_confirmed_l54 + spec_XXXXXX_md_private_tmp + 1 minute 40 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, web_open_clip_l54 + curl_never_succeeded + playwright_and_node_fetch_attempted + no_artifact + 11 minutes 37 seconds` |
| `GPT-5.4 Light` | Pass | `PASS, curl_91877_bytes + web_open_clip_l54 + permission_asked_x6 + no_artifact + 1 minute 49 seconds` |
| `GPT-5.4 Medium` | Pass | `PASS, curl_91869_chars + web_open_clip_l54 + escalation_reasoned_explicitly + no_artifact + 1 minute 7 seconds` |
| `GPT-5.4 High` | Pass | `PASS, web_open_clip_l54 + curl_never_invoked + line_offset_pagination + no_artifact + 3 minutes 20 seconds` |
| `GPT-5.4 Extra High` | Pass | `PASS, web_open_clip_l54 + curl_never_invoked + local_repo_checked + no_artifact + 4 minutes 15 seconds` |
| `GPT-5.5 Light` | Pass | `PASS, curl_91869_chars + web_open_clip_l54 + ec6_spec_md_private_tmp + possible_contamination + 22 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, curl_91869_chars + web_open_clip_l54 + ec6_dash_spec_md_private_tmp + 48 seconds` |
| `GPT-5.5 High` | Pass | `PASS, curl_91869_chars + web_open_clip_l54 + no_cache_miss_language + possible_contamination + 1 minute 4 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, curl_91869_chars + web_open_web_run_clip_l54 + possible_contamination + 1 minute 43 seconds` |
