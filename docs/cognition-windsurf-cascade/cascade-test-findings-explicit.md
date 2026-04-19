---
layout: default
title: "Key Findings for Cascade's Web Search Behavior, Explicit"
permalink: /docs/cognition-windsurf-cascade/cascade-test-findings-explicit
parent: Cognition Windsurf Cascade
---

## Key Findings for Cascade's Web Search Behavior, Explicit `@web`

---

## [Cascade-explicit Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/windsurf-cascade-web-search/web_search_testing_framework.py)

1. Run `python web_search_testing_framework.py --test {test ID} --track explicit`
2. Review the terminal output
3. Copy the provided prompt asking the agent to report on fetch results:
   character count, token estimate, truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
4. Open a new Cascade session in Windsurf and paste the prompt into the chat window
5. Approve web fetch calls, but skip requests for runs of local scripts
6. Capture the agent's full response and observations as the explicit finding;
   the gap between the agent's self-report and actual fetch behavior is a finding
7. Log structured metadata as described in `framework-reference.md`
8. Ensure log results are saved to `/results/cascade-explicit/results.csv`

> _This track adds `@web` directive to test if it meaningfully changes retrieval behavior. Across all runs `@web` mapped to `read_url_content` → `view_content_chunk`;
> `search_web` called once. [Friction: @web Semantics](friction-note-explicit.md#web-semantics-prompt-tool-misalignment)
> for analysis._

---

## Platform Limit Summary

| **Limit** | **Observed** |
|---|---|
| **Hard Character Limit** | _None detected_: `read_url_content` returns a chunked index, not raw content with a byte ceiling; output chars reflect agent chunk selection depth from a pipeline that has no full-page retrieval path |
| **Hard Token Limit** | _None detected_: estimates ranged from ~82 to ~65,000 tokens; no run hit a fixed ceiling |
| **Output Consistency** | _Agent-dependent_: same URL and prompt produces 0–161,000 chars depending on agent and chunk selection |
| **Content Selection Behavior** | _Two-stage chunked retrieval_: `read_url_content` returns a positional index with summaries; content requires sequential `view_content_chunk` calls per position |
| **Truncation Pattern** | _Two independent truncation layers_: agent chunk selection, most large page content never fetched; per-chunk display ceiling variable by chunk, remainder hidden with byte-count notice |
| **Redirect Chains** | _Consistent_: tested 5-level redirect chain; returned inline without triggering chunked pipeline |
| **Self-reported Completeness** | _Inconsistent_: agents with identical content report contradictory truncation assessments; disagreement tracks chunk selection depth, not actual content loss |
| **Chunk Summary Population** | _URL-dependent_: well-structured pages return populated summaries providing navigational signal; CSS-heavy or SPAs may return empty summaries collapsing skimming into blind sampling |
| **SPA extraction** | _Lossy by design_: Go Colly static scraper delivers ~25–30% of raw HTML as extracted text; scripts, styles, and metadata discarded before delivery |
| **`@web` directive** | _Redundant for URL fetch tasks_: `@web` maps to `read_url_content` across all agents and all runs; `search_web` invoked once (`GLM-5.1` during `SC-2`) as a secondary verification attempt; returned no usable content |
| **Agent Self-Reporting Fidelity** | _Unreliable_: thought panels reveal batch reads, collapsed passes, and re-reads not disclosed in output; fidelity failures documented across SC-2, OP-4, BL-3, SC-1, and SC-4 |

---

## Results Details

| | |
|---|---|
| **Agent Selector** | Hybrid Arena — 5 slots per run |
| **Agents Observed** | `Claude Sonnet 4.6 Thinking`, `Claude Opus 4.7`, `GPT-5.3-Codex`, `GPT-5.4`, `GPT-5.4 High Thinking`, `Kimi K2.5`, `SWE-1.6`, `GLM-5.1`, `Gemini 3.1 Pro High Thinking`, `o3` |
| **Total Runs** | 66 |
| **Distinct URLs** | 11 |
| **Input Size Range** | ~2 KB – 256 KB |
| **Truncation Events** | 35 / 66 |
| **Average Output Size** | 43,441 chars |
| **Average Token Count** | 13,320 tokens |
| **Approval-gated Fetch** | 58 / 66 runs prompted for approval |
| **Auto-pagination** | 35 runs auto-paginated; 1 run paginated when prompted |
| **Complete Retrieval Failure** | `SC-2` URL rewriting bug |

---

## Agentic Pagination Depth

Agents consistently use `read_url_content` to fetch URLs, but depending on the state of the chunk
index, they reason whether individual calls to `view_content_chunk` is worth it. While it determines
output size and truncation self-report, chunks fetched is the primary behavioral variable in this
dataset. The tractability threshold is visible across tests: agents tend toward full retrieval on
chunk counts ≤14 and toward sparse sampling on larger ones ≥50, with 33–38 chunks as the transition
zone where model families diverge. `SWE-1.6` shows the most consistent full-retrieval behavior;
`GPT-5.3-Codex` and `Kimi K2.5` default to sparse sampling regardless of chunk count.

| Test | Chunks | Agent | Fetched | Strategy |
|---|---|---|---|---|
| `BL-2` | 3 | All agents | 3 | Floor effect — 3 chunks indistinguishable from full retrieval |
| `EC-1` | 10 | All agents | 10 | Full retrieval unanimous; below suppression threshold |
| `SC-1` | 14 | All agents | 9–14 | Full retrieval in 3 of 5; chrome exclusion in 2 |
| `SC-4` | 33 | `SWE-1.6`, `o3` | 33 | Full; `Gemini`, `GPT-5.4` stopped at index |
| `EC-6` | 38 | `SWE-1.6` | 38 | Full; `GLM` partial; `Opus`, `GPT-5.4` index only |
| `BL-3` | 53 | `Kimi`, `GLM`, `Sonnet` | 1–19 | Sparse; `GPT`, `SWE` stopped early |
| `OP-4` | 53 | `SWE-1.6` | 53 | Full; all others sparse or index only |
| `BL-1` | 54 | `Opus` | 54 | Full; all others 2–9 chunks |
| `SC-3` | 60 | All agents | 1–6 | Suppressed across all runs |
| `OP-1` | 91 | All agents | 1–5 | Suppressed across all runs |

---

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
|---|---|---|---|---|
| 1 | **`read_url_content` returns chunk index** | All tests | Requires `view_content_chunk` × N; no single-call full-page retrieval path | **Output chars reflect chunks fetched, not retrieval ceiling; variance is behavioral, not architectural** |
| 2 | **No fixed character or token ceiling detected** | `BL-1`<br>`EC-6`<br>`SC-4` | `BL-1` `Opus` estimated ~170,000–200,000 chars across 54 chunks; `EC-6` `SWE` measured 61,921 chars with no cutoff; `SC-4` `o3` summed 34,200 chars across 33 chunks | **If ceiling exists, no test hit it; constraint is chunks fetched, not a tool-imposed byte limit** |
| 3 | **Per-chunk display truncation is a second independent layer** | `BL-1`<br>`SC-4`<br>`OP-4` | `view_content_chunk` hides middle portion of large chunks with explicit byte-count notice; `SC-4` `SWE` found 3,766 bytes hidden across 4 positions; `OP-4` `SWE` found truncation warnings on all 53 chunks ranging 367–24,204 bytes | **Full chunk retrieval doesn't guarantee full content delivery; internal truncation invisible to partial-retrieval agents** |
| 4 | **Truncation self-report tracks chunks fetched, not content loss** | `SC-4`<br>`BL-3`<br>`SC-3` | Agents sampling 3 chunks reported no truncation; agents retrieving all 33 found byte-level notices at 4 positions; `SWE`/`o3` full-retrieval contradiction on identical source | **Self-reported truncation accurate for chunks seen, globally misleading for document; agents conflate retrieval completeness with content fidelity** |
| 5 | **Chunk summary population determines retrieval strategy quality** | `SC-1`<br>`SC-3`<br>`BL-3`<br>`OP-4` | `SC-1` populated summaries enabled chrome exclusion before fetching; `BL-3` and `OP-4` empty summaries (`"/"`) collapsed skimming to blind sampling; `SC-3` populated summaries present but unused above ~50 chunks | **Index-guided targeting requires populated summaries; populated summaries provide signal but don't guarantee targeted retrieval above the suppression threshold** |
| 6 | **SPA sources produce an extraction ratio gap, not a truncation event** | `EC-1` | Go Colly static scraper delivers ~20–35% of raw HTML as extracted text; ~70KB gap on a ~100KB page consistent across all 5 runs | **Gap is architectural and consistent, not stochastic; agents evaluate completeness within tool output frame and characterize gap as pipeline transformation, not content loss** |
| 7 | **Routing bypasses chunked pipeline for small payloads** | `EC-3` | `read_url_content` returned 5-redirect-chain terminal JSON response inline ~353–367 chars body; `view_content_chunk` not called in any run | **Chunked architecture has at least two modes; small payloads return inline without triggering the two-fetch process** |
| 8 | **`@web` is redundant for URL fetch tasks** | All explicit<br>track tests | `search_web` not invoked in any of 66 explicit track runs; all agents used `read_url_content` → `view_content_chunk` — identical to interpreted track | **`@web` produced no change in retrieval ceiling, toolchain, or chunking behavior when a specific URL was provided; H4 confirmed redundant across all tests** |
| 9 | **`@web` conditional routing is consistently described** | `SC-1`<br>`SC-4`<br>`EC-6` | Across 66 runs, agents converged on the same conditional: `@web` + URL → `read_url_content`; `@web` + query → `search_web`; no agent invoked both in the same run | **`@web` is a routing hint, not a distinct tool; conditional routing description is stable across model families** |
| 10 | **Agent self-reporting fidelity is a systematic confound** | `SC-2`<br>`OP-4`<br>`BL-3`<br>`SC-1`<br>`SC-4` | Five distinct fidelity failure patterns identified: batch reads collapsed into stated positions; partial position reporting; quantified undercounting (~32% in `GLM`); parallel execution opacity; thought panel over-reporting | **Tool visibility tables from agent self-report cannot be treated as complete behavioral records without thought panel cross-reference; see [Agent Self-Reporting Fidelity](friction-note-explicit.md#agent-self-reporting-fidelity)** |
| 11 | **Index size suppresses auto-pagination above ~50 chunks** | `SC-3`<br>`OP-1`<br>`BL-3`<br>`OP-4` | Maximum chunks retrieved: 6 of 60 (`SC-3`), 5 of 91 (`OP-1`), 19 of 53 (`BL-3`), 53 of 53 (`OP-4` `SWE` only) | **Tractability threshold is agent-dependent and index-size-sensitive; 33–38 chunks is the transition zone where model families diverge** |
| 12 | **CSS-heavy sources produce content extraction failure, not truncation** | `BL-1`<br>`BL-3`<br>`OP-4` | MongoDB LeafyGreen CSS dominated chunk content across all runs on three distinct MongoDB URLs; tutorial body content absent across all 53 chunks in all BL-3 runs | **"Structurally complete, semantically incomplete" — page navigation and chrome recovered; article content inaccessible regardless of retrieval depth** |
| 13 | **Tool wrapper preamble inflates character counts** | `EC-3` | `Claude Opus 4.7` identified and quoted the preamble string `"Here is the content of the article at [URL]:\n\n"` prepended by `read_url_content`; explains ~70-char cross-run variance on identical content | **Character count variance between runs on identical content reflects tool wrapper inclusion rules, not retrieval differences; body-only counts are the reliable cross-run metric** |
| 14 | **Colly identified as fetch backend** | `EC-3` | `GLM-5.1` and `Claude Opus 4.7` independently identified `User-Agent: colly — https://github.com/gocolly/colly` from httpbin's echoed request headers | **Windsurf's `read_url_content` tool uses the Colly Go scraping library; static scraper explains SPA extraction gap and CSS extraction failures** |

---

## Perception Gap

| **Test** | **Expected** | **Received** | **Retrieval rate** | **Agent characterization** |
|---|---|---|---|---|
| **`EC-6`<br>Raw Markdown** | ~61 KB | 61,921 chars<br>`SWE` full retrieval | ~97% | _"No truncation, structurally complete — tool transforms content before delivery"_ |
| **`SC-4`<br>Markdown Guide** | ~30 KB | ~15,500–34,200 chars; full retrieval runs | ~52–114%* | _"Complete but contradicted — `SWE` found truncation at 4 positions; `o3` found none on identical content"_ |
| **`EC-1`<br>SPA** | ~100 KB | ~20,100–35,500 chars extracted | ~20–36% | _"Extraction ratio, not truncation — HTML stripped and JavaScript not executed before delivery"_ |
| **`SC-3`<br>Wikipedia** | ~100 KB | ~4,900 chars index to ~150,000 chars extrapolated | varies by method | _"No truncation, index complete — vs — yes, 57/60 chunks never fetched"_ |
| **`BL-3`<br>CSS Tutorial** | ~256 KB | ~2,598–350,000 chars across runs | indeterminate | _"Structurally complete, semantically incomplete — tutorial body absent across all chunks"_ |
| **`EC-3`<br>Redirect JSON** | ~2 KB | ~353–367 chars body | ~15–18% of expected | _"Complete — JSON payload is the full response; size gap reflects redirect chain delivering terminal response only"_ |

> _* `SC-4` variance above 100% reflects counting method differences between full-retrieval runs,
> not over-retrieval. `SWE-1.6` and `o3` retrieved identical content and produced estimates
> differing by ~18,700 chars — the largest same-source, same-depth variance in the dataset._

> _Implication: output chars aren't an appropriate truncation ceiling metric for Cascade; they
> reflect chunk count, content transformation, and tool wrapper inclusion rules. None is
> observable from agent self-report alone._