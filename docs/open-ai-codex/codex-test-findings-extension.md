---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Extension"
permalink: /docs/open-ai-codex/codex-test-findings-extension
parent: OpenAI Codex
---

# Key Findings for Codex's Web Search Behavior, GPT-interpreted - Extension

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Run `python scripts/framework.py --test {test_id} --track vscode-codex-interpreted`
2. Review terminal output
3. Copy the provided prompt asking agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
4. Open a new session in VS Code Codex, paste the prompt into the chat window
5. Approve `curl` escalation and shell permission requests; skip requests for runs of local scripts
6. Capture the agent's full response; observe the gap between self-report and actual retrieval behavior<br>as the interpreted finding
7. Log structured metadata as described in [`framework-reference.md`](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/framework-reference#workflow)
8. Ensure results saved to [`/results/vscode-codex-interpreted/results.csv`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/vscode-codex-interpreted/results.csv)

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard<br>Character<br>Limit** | _None detected via `curl`_: fetches returned payloads from `EC-3`'s 254 chars to `BL-3`'s 4,848,853 chars;<br>`web` path reflects a line-indexed window, not a byte ceiling |
| **Hard<br>Token<br>Limit** | _None detected via `curl`_: counts ranged from 38 to 1,212,213; `SC-2`'s `134804 tokens truncated` marker against an `Original token count: 144884` largest display cap, terminal-rendering cap independent of HTTP retrieval, consistent with [`T1`'s `EC-6` finding](codex-test-findings-desktop.md#platform-limit-summary), different threshold |
| **Output<br>Consistency** | _LLM-and-level-stratified_: same URL + reasoning level regularly produce distinct retrieval strategies, output;<br>`BL-1`'s `GPT-5.5 Medium`,`Extra High` `web`-only at ~85K chars while `Light (Low)`, `High` escalate to 509,025 chars with same LLM |
| **Content<br>Selection<br>Behavior** | _Two-tier retrieval_: `web` returns a rendered, line-indexed extraction; full content requires `curl` escalation with network permissions; `OP-4`'s `GPT-5.4-Mini Extra High` first `T2` run to expose `wordlim:200` parameter in tool trace, confirming [`T1`'s `SC-1` inference of agent-adjustable soft-default](codex-test-findings-desktop.md#platform-limit-summary) rather than fixed extraction size |
| **Truncation<br>Pattern** | _At least three independent layers_: `web` line-indexed window, LLM-page-dependent; terminal display cap,<br>`SC-2`'s `134804 tokens truncated` marker; `curl` response body, never truncated on successful escalations;<br>`BL-3` shows window cutpoint on structural boundary against terminal display cutpoint arbitrary |
| **`web`<br>Line-Indexed<br>Window** | _Page-architecture-dependent, sharper than `T1`_: `EC-6`:`L54` across runs with most LLM + reasoning levels, `SC-2`:`L139-140`, `SC-3`:`L353` comparably tight; LLM splits elsewhere - `OP-1`:`L304`/`L556`, `OP-2`:`L317-318`/`L590-591`, `OP-4`:`L237`/`L616`; `BL-1`:`L420` mostly holds with `L119` outlier; `SC-1`:`L344`; `SC-4`:`L657` |
| **`curl`<br>Escalation** | _Dominant, not universal_: `curl` use 99/119 runs; success often led to saving full HTTP response; `BL-2`, `BL-3`, `OP-4`, `OP-2`, `SC-1` heavy `curl` use; `EC-3` rare due to small size; `BL-3`, `SC-2` retrieve full bodies only JS-rendered scaffolding, not prose; attempts with `Browser`, headless Chrome, `Playwright` failed |
| **Session<br>Contamination** | _Structurally reduced, not eliminated_: `/private/tmp` clears between `T2` sessions, no run wrote to a project-persistent directory; `SC-4`'s `GPT-5.4-Mini Extra High` displayed workspace substitution; filename collision risk from independently fetched runs sharing path often, most heavily `EC-6`, `OP-4` |
| **Post-Session Auto-Editing** | _Data integrity risk, reversed from `T1`_: confirmed across most runs; all `BL-1`, `BL-2`, `EC-1` 12/13 runs,  half of `OP-4`, `SC-4`, `OP-4`; `T1` double report resolves during cleanup, `T2` single report doubles; screenshot capture at runtime remains primary record |
| **JS-Rendered<br>Pages** | _Structural retrieval failure_: `SC-2`, Next.js hydrated shell ~578,000 chars with prose absent regardless of path or reasoning level; `BL-3` different tutorial page than `T1`, same pattern at ~4.5 to 4.85 million chars |
| **`Cache Miss`<br>Failure** | _No longer systematic for the URL that defined it_: only 1/13 `EC-6` runs emitted `Cache Miss` versus 17/20 in `T1`; most return windowed `L54` extraction instead of failure; `BL-3` `Cache Miss` 6/8 `web` attempts |
| **Self-reported Completeness** | _Failure abstraction, mirrors `T1`_: agents sanitize issues into success language rather than debugging or correcting misuse, users lose learning opportunities, analysis in [Retrieved-Report Mismatches](friction-note-interpreted-extension.md#retrieved-report-mismatches); explicit examples `BL-3` `GPT-5.5 Extra High`, `GPT-5.4-Mini Low` runs |

## Results Details

| | |
| --- | --- |
| **Track** | `T2` GPT-interpreted, VS Code-Codex Extension |
| **Agents Observed** | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5` |
| **Intelligence Levels** | `Light` - `Low`, renamed mid-track - `Medium`, `High`, `Extra High` |
| **Total Runs** | 119 |
| **Distinct URLs** | 13 |
| **Input Size Range** | `EC-3`: ~660 chars, `web.open` path, 254 chars via `curl`, to `BL-3`: ~4.85M chars |
| **Truncation Events** | 82 / 119 - 69% of runs report truncation in some form<br>- `yes`, `web.open` hit, reported explicitly: 22<br>- `mixed`, both paths used, `web.open` limits named: 44<br>- `implicit`, escalated to `curl` without naming the `web.open` limit: 16<br>- `no`, `curl`-only or no truncation signal: 37 |
| **Average Output Size** | 429,563 chars |
| **Output Size Range** | 149 - 4,849,033 chars |
| **Average Token Use** | 102,606 tokens |
| **Token Count Range** | 38 - 1,212,213 tokens |
| **Workspace Substitution** | 1 / 119 runs confirmed; filename collision risk flagged in at least 16 additional runs |
| **`curl` Escalation** | Dominant retrieval path where attempted, present in 68 / 119 runs, 57% |
| **`web` Bypass** | `GPT-5.5` skipped `web` completely on at least one intelligence level in `BL-3`, `OP-4`, `EC-1`, `EC-6`, and `SC-1`; `GPT-5.4-Mini` and `GPT-5.4` bypass occasionally but less consistently |

_The three-model roster, down from `T1`'s five, reflects OpenAI's retirement of `GPT-5.2`, `GPT-5.3-Codex`, and `GPT-5.4` from
Codex between tracks; `GPT-5.4` reappeared partway through `T2` collection and has data for only `EC-1`, `EC-3`, and `EC-6`. See
the Friction Note's LLM Retirement section for the full methodology decision._

_The tool's own threshold analysis pairs each run against the test prompt's flat expected-size figure rather than a measured
baseline, so "in → out" comparisons in the raw data, for example `EC-6`'s `61,440 chars in → 91,869 chars out`, reflect a
prompt estimate rather than an actual size discrepancy._

## Content Access x Intelligence

As in `T1`, agentic task completion isn't a useful signal for page readability on `T2`. Retrieval strategy still governs content
accessibility more than intelligence level does: `web.open` returns a line-indexed rendered extraction, and it's up to the agent
to escalate past it, which most agents eventually did but not consistently. Where `T2` diverges from `T1` is in how tightly the
`web.open` ceiling holds across models on several test IDs. `EC-6`'s identical `L54` cutoff across 10 of 13 runs, and `SC-2`'s and
`SC-3`'s comparably tight `L139-140` and `L353` clusters, suggest the ceiling is set by page structure or a fixed extraction
default at least as often as by the calling LLM, sharpening rather than overturning `T1`'s own model-version-correlated window
finding from `OP-1` and `OP-2`, both of which still show real per-model splits within `T2` itself.

The same three-tier grouping from `T1` still separates the 13 test IDs cleanly on content accessibility. `EC-3`, `BL-2`, `EC-6`,
`SC-4`, and `SC-1` are readable static payloads where either retrieval path returns usable prose. `BL-1`, `OP-2`, `OP-1`, `SC-3`,
and `OP-4` are large static HTML where `web.open` truncates but `curl` remains fully readable. `EC-1`, `BL-3`, and `SC-2` are
JS-rendered or SPA pages where `curl` returns scaffolding rather than prose regardless of tool sophistication or reasoning
level. `BL-3`'s specific URL changed between tracks after the original was retired, but the replacement lands in the identical
accessibility tier, confirming the JS-rendered failure mode isn't tied to one specific page.

> _A retrieval-path heatmap and a truncation-tier heatmap, mirroring `T1`'s visual but split into two grids rather than one
> blended scheme, are planned as a follow-up to this section. The truncation-tier grid is buildable directly from each test
> ID's `Truncated` column; the retrieval-path grid requires hand-classifying the fragmented `tools_named` field per run, since
> it doesn't collapse into stable categories on its own. A separate small-multiples chart normalizing each test ID's
> line-ceiling cutoff against its own total line count, so `EC-6`'s `L54` and `SC-4`'s `L657` are comparable as percentages
> rather than misleadingly compared as raw numbers, is planned as a third pass after those two._

---

## Truncation Analysis

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`web.open` returns a line-indexed rendered text extraction window, not the full page** | All tests | Returns a line-numbered extraction; `wordlim:200` confirmed directly in `OP-4`'s tool trace; `Total lines: N` reported for most URLs | **Output chars on the `web.open` path reflect viewport depth, not retrieval ceiling; `curl` remains the only path to the raw HTTP body** |
| 2 | **No fixed character or token ceiling detected on the `curl` path** | `BL-1` `BL-3`<br>`OP-1` `OP-2`<br>`OP-4` `SC-3` `EC-6` | `BL-3`: `GPT-5.5 Low`, `Medium`, and `High` all retrieved ~4.85M chars; `OP-4`: six of eight runs retrieved 514,092 chars, several in under a minute | **Char/token access is escalation-and-test-ID-gated, not architecturally defined** |
| 3 | **Truncation layers now conflict within a single test ID, not just diverge across test IDs** | `EC-6` `SC-2` `BL-3` | `EC-6` confirms the `web.open` line ceiling as independent from the HTTP body; `SC-2`'s terminal display shows a token-count marker independent of both; `BL-3` shows a Viewer Window cutoff at a structural boundary in direct tension with a Terminal Display cutoff at an arbitrary position in the same 8-run set | **Self-reported truncation stays tool-dependent, and disambiguating layers now requires per-run, not just per-test-ID, attention** |
| 4 | **`curl` escalation success is test-ID-dependent as much as LLM-version-dependent** | All tests, manually verified | 68 of 119 runs, 57%, confirmed successful; ranges from `EC-3`'s 2/12 to `BL-2`'s 8/8 depending on whether the payload needs escalation at all | **Unlike `T1`'s cleaner per-version threshold, the same `T2` LLM bypasses `web` entirely on one test ID and fails to escalate at all on another** |
| 5 | **Higher intelligence levels continue to show diminishing or inconsistent returns** | `BL-3` `EC-6`<br>`SC-1` `SC-3` | `EC-6`'s `GPT-5.4-Mini Extra High` spent 11 minutes 37 seconds across three failed tool paths and retrieved nothing, while `Light` completed the same test in 29 seconds; `SC-3`'s `GPT-5.5 Extra High` ran the simplest tool chain in its series despite the highest reasoning level | **`Extra High` doesn't reliably improve retrieval outcomes and in several test IDs actively underperforms `Light`/`Low` on the identical URL** |
| 6 | **Session contamination reduced in structure but not eliminated** | `EC-6` `OP-4`<br>`BL-1` `BL-2` `EC-1` | Confirmed workspace substitution in 1/119 runs, `SC-4`'s `GPT-5.4-Mini Extra High`; filename collision risk recurs across at least 16 runs spanning 5 test IDs, most heavily `EC-6` and `OP-4`'s two independent collision pairs | **`/private/tmp` clearing between sessions reduces but doesn't eliminate contamination risk; collisions now arise more from repeated default filenames across independent fresh fetches than from genuine cross-session artifact reuse** |
| 7 | **JS-rendered pages remain a structural retrieval failure, confirmed on a new URL** | `SC-2` `BL-3` | `SC-2`: Next.js hydrated shell, ~578,000 chars, prose absent across all 8 runs; `BL-3`: a replacement URL, different from `T1`'s retired original, independently reproduces the same JS-rendered tutorial-body-absent pattern | **Neither `web.open` nor `curl` returns prose for CSP-gated or client-hydrated pages regardless of surface, and the pattern holds even when the underlying URL changes entirely** |
| 8 | **`Cache Miss` is no longer systematic for the URL that originally defined it** | `EC-6` `BL-3` | Only 1 of 13 `EC-6` runs shows the literal `Cache Miss` string, versus 17/20 in `T1`; the other 12 return a windowed `L54` extraction instead. `BL-3`'s replacement URL produces `Cache Miss` in 8 of 8 attempts | **The failure signature is URL-specific rather than a stable property of raw or large payloads; the same URL that anchored `T1`'s `Cache Miss` finding now mostly fails silently into a windowed view on this surface instead** |
| 9 | **`web.open` line ceiling is overwhelmingly page-architecture-driven on the most-replicated test IDs, sharpening `T1`'s finding** | `EC-6` `SC-2` `SC-3` | `EC-6`'s `L54` cutoff replicates identically across 10 of 13 runs spanning all 3 LLM families and all 4 reasoning levels; `SC-2`'s `L139-140` and `SC-3`'s `L353` show comparably tight cross-model clustering | **Where `T1` found LLM-version-correlated windows, `T2`'s tightest test IDs show the opposite: the same ceiling regardless of model. `OP-1`, `OP-2`, and `OP-4` still show real model-family splits, so both mechanisms coexist depending on the page** |
| 10 | **`wordlim:200` confirmed directly in a `T2` tool trace, not just inferred from agent language** | `OP-4` | `GPT-5.4-Mini Extra High`'s tool trace lists `wordlim:200` explicitly alongside `web.open` and `turn0view0` | **Confirms `T1`'s `SC-1` inference, a soft default, agent-adjustable parameter, with a literal parameter name rather than a reconstruction from reasoning text** |
| 11 | **`multi_tool_use.parallel` reappears outside the `GPT-5.5` family at the identical model-and-level pairing `T1` first observed it at** | `EC-6` | Confirmed once, in `EC-6`'s `GPT-5.4 Extra High` run, matching `T1`'s own `EC-6` finding that the same combination was first to break `GPT-5.5` exclusivity | **The identifier's appearance tracks a specific model-and-reasoning-level pairing independent of surface, suggesting it's gated by LLM-version-and-level rather than by track** |

## Retrieval Outcomes

Output chars on the `web.open` surface aren't a retrieval ceiling metric, but reflect how far the agent traversed through a
line-indexed renderer before stopping or escalating. Artifact write-saves were less consistent than in `T1`; several runs wrote
files without referencing them in the final report, a pattern documented across `SC-1` through `SC-4`. Rows below organized by
page architecture:<br> _raw files → static HTML → reference/wiki → JS-rendered/SPA_

{: .table-perception}
| **Test** | **Expected** | **Received** | **Content Accessibility** | **Agent Characterization** |
| --- | --- | --- | --- | --- |
| **[`EC-3`](https://httpbin.org/redirect/5)<br>Redirect JSON** | ~2 KB | `web.open`: 660 chars<br>`curl`: 254 chars | 100% | _Complete on both paths_: `GPT-5.4-Mini` favors `curl` as the authoritative measurement path at `Medium` and `High`, the inverse of its own `T1` pattern at those levels |
| **[`BL-2`](https://www.mongodb.com/docs/manual/reference/change-events/create.md)<br>Raw Markdown** | ~20 KB | 5,805 chars, all 8 runs | 100% | _Complete and internally consistent_: the 219-char gap against `T1`'s 6,024 chars most likely reflects a source update between collection windows, not surface behavior |
| **[`EC-6`](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md)<br>Raw GitHub Markdown** | ~60 KB | `curl`: 91,869 chars, 9/13 runs<br>`web.open`: `L54` cutoff, 10/13 runs | ~100% body where `curl` succeeds; line-capped elsewhere | _No HTTP-layer truncation on any successful `curl` run_: the `L54` `web.open` cutoff is the single most consistent finding across the whole `T2` corpus, identical regardless of model or reasoning level; one run failed to retrieve any content at all |
| **[`SC-4`](https://www.markdownguide.org/basic-syntax/)<br>Markdown Guide** | ~30 KB | `curl`: 64,527 chars, most runs<br>`web.open`: `L657` of 752 | `curl` 100%, `web.open` ~87% | _Complete via `curl`_: `L657` ceiling consistent across `GPT-5.5` runs; `GPT-5.4-Mini Extra High` sourced metrics from a prior rollout log rather than fetching, a fallback mode not seen in `T1` |
| **[`SC-1`](https://ai.google.dev/gemini-api/docs/url-context)<br>Gemini<br>API Docs** | ~40 KB | `curl`: 125,248-125,252 chars, 3/8 runs<br>`web.open`: 16,390-34,000 chars | `curl` 100%, `web.open` 13-27% | _Complete via `curl` where attempted_: `GPT-5.4-Mini` shows four different retrieval strategies across its four intelligence levels, the widest intra-model spread in the `T2` corpus |
| **[`OP-2`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)<br>MDN Reference** | ~120 KB | `curl`: 241,720 chars, 4/8 runs | `curl` 100%, `web.open` 13-25% | _Complete via `curl`_: line ceiling splits by model, `~L317-318` for `GPT-5.4-Mini High`/`Extra High` versus `~L590-591` for `Medium` and all `GPT-5.5` runs, extending `T1`'s `OP-1` finding that the ceiling can be model-dependent |
| **[`BL-1`](https://www.mongodb.com/docs/manual/reference/change-events/create/)<br>MongoDB Reference** | ~85 KB | `curl`: 509,025 chars, 6/8 runs | `curl` 100%, `web.open` ~15-17% | _Complete via `curl`_: the `L420` ceiling isn't as tightly held as `EC-6`'s `L54` - one run, `GPT-5.4-Mini Extra High`, cut at `L119` instead, so this test ID's ceiling is real but less deterministic than the corpus's strongest cases |
| **[`OP-4`](https://spec.commonmark.org/0.31.2/)<br>CommonMark Spec** | ~500 KB | `curl`: 514,092 chars, 6/8 runs | `curl` 100%, `web.open` 2-3% | _Complete via `curl`_: two clean line-ceiling clusters, `L237` for `GPT-5.4-Mini Medium`/`Extra High` and `L616` for `GPT-5.5 Low`/`High`; two independent filename-collision pairs recurred in this test ID alone |
| **[`OP-1`](https://en.wikipedia.org/wiki/Machine_learning#History)<br>Wikipedia<br>with URL Fragment** | ~40 KB | `curl`: 740,370 chars, 3/8 runs | `curl` 100%, `web.open` ~0.5-4% | _Complete via `curl`_: `#History` silently dropped on every run, consistent with `T1`; the corpus's clearest model-family split, `L304` for `GPT-5.4-Mini` versus `L556` for `GPT-5.5`, held across all 4 intelligence levels each |
| **[`SC-3`](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population)<br>Wikipedia<br>Table-Heavy** | ~100 KB | `curl`: 786,213 chars, 5/9 runs | `curl` 100%, `web.open` 1-3% | _Complete via `curl`_: `L353` ceiling holds across every model and level where observable, one of the tightest single-value clusters in the corpus alongside `EC-6`'s `L54`; one run failed outright on a model capacity error |
| **[`EC-1`](https://ai.google.dev/gemini-api/docs)<br>Gemini<br>API Docs** | ~100 KB | `curl`: 119,785-120,001 chars, 8/13 runs | `curl` 100%, `web.open` 7-18% | _Complete via `curl`_: one run, `GPT-5.4-Mini Light`, is a full task failure with zero usable metrics; one run reached content via headless Chrome rather than `curl`, the corpus's only instance of that recovery path |
| **[`SC-2`](https://docs.anthropic.com/en/api/messages)<br>Anthropic API Docs** | ~80 KB | `curl`: 578,233-578,275 chars, 5/8 runs | Not accessible | _Complete HTML shell, prose absent regardless of path_: JS-hydrated reference content never appears in any run's output; `L139-140` ceiling on `web.open` near-universal; a token-denominated terminal display truncation, `134,804 tokens truncated`, appeared for the first time in the `T2` corpus |
| **[`BL-3`](https://www.mongodb.com/docs/vector-search/tutorials/quick-start/?deployment-type=atlas&interface=atlas-ui&embedding=auto)<br>MongoDB Vector Search Tutorial** | ~4,531 KB | `curl`: 4,640,208-4,848,853 chars, 5/8 runs | Not accessible | _Complete HTML shell, prose absent_: every `web` attempt returned a literal `Cache Miss`, unlike `EC-6`'s mostly windowed failure mode; one run silently substituted the canonical URL without query parameters, weakening its contribution to every hypothesis; no `T1` baseline exists for this replacement URL |
