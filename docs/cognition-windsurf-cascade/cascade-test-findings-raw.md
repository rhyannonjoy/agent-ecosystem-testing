---
layout: default
title: "Key Findings for Cascade's Web Search Behavior, Raw"
permalink: /docs/cognition-windsurf-cascade/cascade-test-findings-raw
parent: Cognition Windsurf Cascade
---

## Key Findings for Cascade's Web Search Behavior, Raw

---

## [Raw Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/windsurf-cascade-web-search/web_search_testing_framework.py)

1. Run `python web_search_testing_framework.py --test {test ID} --track raw`
2. Review the terminal output
3. Copy the provided prompt instructing the agent to retrieve the URL and return
   content exactly as received, saving output to `results/raw/raw_output_{test_ID}.txt`
4. Open a new Cascade session in Windsurf and paste the prompt into the chat window
5. Approve web fetch calls and terminal commands; cancel if any run loops hang
6. Run the verification script against the saved file; capture path compliance,
   file size, checksum, and truncation indicators
7. Log structured metadata as described in `framework-reference.md`
8. Ensure log results are saved to `/results/cascade-raw/results.csv`

> _Raw output file presence, path compliance, and content fidelity are tracked. Claiming a save without writing a file, referencing another
> agent's file, or generating structurally accurate but semantically unmeaningful content all describe distinct failure modes;
> analysis in [Friction: Raw](friction-note-raw.md)._

---

## Platform Limit Summary

| **Limit** | **Observed** |
|---|---|
| **Hard Character Limit** | _None detected_: output sizes ranged from 275-56,256,891 chars; ceilings agent-imposed or write-stage failures, not explicitly platform-imposed byte limits |
| **Hard Token Limit** | _None detected_: token counts ranged from 52-12,782,469; `BL-3`'s `SWE-1.6` appears to hit a write ceiling |
| **Output Consistency** | _Agent- and strategy-dependent_: same URL, prompt produces 275 B -`EC-3` to 56 MB - `SC-2 Kimi` depending on agent, pipeline acceptance, write method |
| **Content Selection Behavior** | _Two-stage chunked retrieval_: identical to interpreted track; all agents used `read_url_content` → `view_content_chunk`; no agent called `search_web` for verification |
| **Truncation Pattern** | _Write-stage asymmetry_: `view_content_chunk` retrieval reliable across agents, chunk counts; dominant failure modes were write-related: heredoc errors, token ceiling, false completions, file reuse |
| **Redirect Chains** | _Size-influenced, behavior dependent_: `EC-3` 5-hop redirect chain followed cleanly by all agents; `SC-2` single cross-domain redirect caused `read_url_content` to halt, name destination in error message |
| **Auto-pagination** | _Consistent up to ~60 chunks; abandoned at 1,026_: agents auto-paginated at chunk counts ≤ 60; no agent paginated beyond position 0 at `SC-2`'s 1,026-chunk corpus, confirming size threshold |
| **False Completion Claims** | _Distinct failure mode_: observed across `BL-1`, `OP-1` - `SWE-1.6`; `BL-3`, `SC-3` - `GPT-5.3-Codex`; `EC-6` - `Gemini 3.1`; agents reported saved files with content metrics that was never written |
| **Cross-Agent File Reuse** | _Confirmed via `EC-6` MD5 checksum_: once a plausible file exists in the workspace, subsequent agents satisfy the persistence requirement by reference rather than by writing; confirmed across `BL-2`, `BL-3`, `OP-1`, `EC-6` |
| **`curl` as Fidelity Escape Hatch** | _Consistent pattern_: agents that correctly diagnose the Cascade pipeline as returning processed Markdown rather than raw HTML switch to `curl`; resulting files are architecturally correct, but contain raw HTML skeletons without prose |

---

## Results Details

| | |
|---|---|
| **Agent Selector** | Hybrid Arena — 5 slots per run; some tests ran two arena rounds |
| **Agents Observed** | `Claude Opus 4.7`, `Claude Sonnet 4.6 Thinking`, `GLM-5.1`, `Gemini 3.1 Pro`, `GPT-5.3-Codex`, `GPT-5.4`, `GPT-5.5`, `Kimi K2.6`, `Minimax M2.5`, `SWE-1.6`, `SWE-1.6 Fast`, `xAI Grok-3` |
| **Total Runs** | 66 |
| **Distinct URLs** | 10 |
| **Input Size Range** | ~2 KB – 256 KB (estimated rendered); actual pipeline output: 275B – 56MB depending on retrieval method |
| **Truncation Events** | 5 / 66 |
| **Average Output Size** | 1,129,230 chars |
| **Output Size Range** | 275 – 56,256,891 chars |
| **Average Token Count** | 266,105 tokens |
| **Token Count Range** | 52 – 12,782,469 tokens |
| **Approval-gated Fetch** | 56 / 66 runs prompted for approval |
| **Auto-pagination** | 48 run(s) auto, 0 run(s) prompted |
| **Complete Retrieval Failure** | `SC-2` redirect halt; `OP-4` all 5 agents retrieved chunks but none produced clean output |
| **URL Fragment Handling** | `OP-1` — 1 of 10 agents (Grok-3) intentionally targeted `#History`; 1 hit it incidentally; 8 defaulted to full-document retrieval |

---

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
|---|---|---|---|---|
| 1 | **No fixed character or token ceiling detected at retrieval stage** | All tests | Output sizes ranged from 275B (`EC-3`) to 56MB (`SC-2 Kimi`); no run hit a tool-imposed byte ceiling during `view_content_chunk` retrieval | **Where ceilings appeared, they were self-imposed (deliberate elision), write-stage failures (output token limit), or environment degradation (VS Code). The retrieval pipeline has no confirmed upper bound.** |
| 2 | **Output token ceiling confirmed as a write-stage failure mechanism** | `BL-3` | `SWE-1.6` hit the model's output token limit explicitly mid-write, visible in the thought panel in real time; the first direct observation of this ceiling across any Cascade track | **The ceiling is real but write-stage, not retrieval-stage. Prior tracks inferred it; BL-3 observed it directly.** |
| 3 | **Read-write asymmetry is the dominant structural finding** | `SC-3`, `SC-4`, `BL-3`, `OP-4` | All or most agents successfully retrieved all chunks in every test; write success was substantially lower across the same tests | **Retrieval via `view_content_chunk` is reliable; the obstacle is reassembling and persisting ~200KB+ of distributed chunk output through shell heredocs or Python scripts at scale.** |
| 4 | **Auto-pagination is confirmed but does not predict output success** | All tests | 48 of 66 runs auto-paginated without explicit prompting; 3 of 4 auto-paginating runs in BL-1 still failed to produce a valid output file | **H5 yes across the dataset. The behavior is robust; it does not guarantee file persistence or content fidelity.** |
| 5 | **Auto-pagination has a behavioral threshold around 1,026 chunks** | `SC-2` vs `BL-2`/`EC-3` | Agents fully paginated at ≤60 chunks in every test; no agent paginated beyond position 0 at SC-2's 1,026-chunk corpus | **A behavioral threshold exists between small and large document sets. Its exact boundary is unconfirmed but falls between 60 and 1,026 chunks.** |
| 6 | **`curl` as a fidelity escape hatch produces semantically empty output** | `BL-1`, `BL-3`, `SC-2`, `SC-3`, `EC-1`, `EC-6` | Agents that correctly diagnose the pipeline as returning processed Markdown switch to `curl`; resulting files contain raw HTML or JS skeletons — architecturally correct but without semantic page content | **Pipeline abandonment is the dominant response to fidelity instinct. Agents that accept the pipeline output succeed; agents that treat it as a shortfall to correct produce files that pass verification while missing target content.** |
| 7 | **Cross-agent file reuse is confirmed at checksum level** | `EC-6`, `BL-2`, `BL-3`, `OP-1` | `Gemini 3.1` and `GLM-5.1` produced EC-6 output files with an identical MD5 checksum; GLM ran earlier and wrote first; Gemini's thought panel narrated retrieval while making no corresponding tool calls | **Path compliance and content fidelity are independent variables. File presence at the correct path does not confirm independent retrieval. Per-agent checksum comparison within the same arena run is required to detect reuse.** |
| 8 | **False completion claims are a distinct failure mode from task drift** | `BL-1`, `BL-3`, `SC-3`, `OP-1`, `EC-6` | `SWE-1.6`, `GPT-5.3-Codex`, and `Gemini 3.1` each reported saved files — with metrics, checksums, and file paths — for content that was never written | **Confident incorrect assertions with no visible uncertainty signal are structurally different from spirals and early stops. All three failure modes produce the same outcome: no valid output file.** |
| 9 | **Redirect halt behavior is confirmed as server-side, not tool-layer rewriting** | `SC-2` | Three agents successfully called `read_url_content` a second time against the redirect destination surfaced in the error payload and received valid chunked responses; this is inconsistent with silent pre-network URL substitution | **`read_url_content` makes the network call, receives a redirect, and halts rather than following automatically. The destination is actionable via a follow-up call. Confirmed as redirect halt, not URL rewriting.** |
| 10 | **Chunking pipeline does not engage below a size threshold** | `EC-3` | 5-hop redirect chain returned 366B JSON inline via `read_url_content` alone; `view_content_chunk` not called in any run | **Chunked delivery has at least two modes; small payloads return inline without triggering the two-fetch pipeline. Lower bound confirmed: 366 bytes. Upper bound unconfirmed but between 366B and ~30KB.** |
| 11 | **URL fragment targeting is behavioral, not architectural** | `OP-1` | 8 of 10 agents retrieved all 92 chunks rather than targeting `#History` at chunk position 17; the chunk index exposes the section header; Grok-3 is the only agent to have used it for navigation | **Fragment-targeting is achievable via the chunk index, absent by default. The write-fidelity instruction may actively suppress targeting: agents attending to output completeness default to full-document collection.** |
| 12 | **Prompt size estimates act as a confound for fidelity-sensitive agents** | `BL-1`, `OP-4` | The ~85KB size expectation in BL-1's prompt is architecturally unreachable: Cascade returns ~8–32KB of filtered Markdown; `curl` returns ~508KB of raw HTML. Agents with strong output-fidelity monitoring spiraled or truncated trying to reach the target | **Size expectations in prompts should be omitted or post-hoc only. No available tool produces the estimated size, making the estimate an irresolvable constraint rather than a verification guide.** |
| 13 | **"Exactly as received" is underspecified and resolved silently** | `SC-3`, `SC-4`, `BL-1`, `OP-4` | Agents interpreted the instruction as Cascade's chunk output with metadata wrappers, raw HTTP response via `curl`, or semantic Markdown — without flagging the ambiguity or asking for clarification in most runs | **Instruction underspecification is resolved silently across agent families. Only `Claude Opus 4.7` surfaced the tradeoff to the user before committing to a write strategy, across two separate tests.** |
| 14 | **`search_web` was not invoked as a primary retrieval mechanism in any run** | All tests | Zero `search_web` calls across 66 raw track runs; `SWE-1.6`'s SC-2 call on the explicit track was a fallback after retrieval failure, not enrichment | **H4 untested across the entire raw track. URL provision alone does not activate `search_web`.** |

---

## Perception Gap

| **Test** | **Expected** | **Received (pipeline)** | **Delivery Ratio** | **Agent Characterization** |
|---|---|---|---|---|
| **`EC-6` Raw Markdown** | ~94 KB | ~95.5–96.4KB (4 agents, independent writes) | ~100% | _"Complete — chunk assembly variation within ±858 chars; elision markers are source false positives"_ |
| **`SC-4` Markdown Guide** | ~30 KB | 30.44KB (`Sonnet`), 32.33KB (`Minimax`) | ~100% | _"Complete — breadcrumb heading injection at chunk boundaries inflates Minimax output; 6 elision markers present but may be tool-layer assembly artifacts"_ |
| **`SC-1` Gemini API Docs** | ~14 chunks | 38–44KB chunk cluster; 10.25KB via direct fetch | ~97% (chunk); ~60% (direct) | _"Chunk cluster structurally identical across agents; direct fetch cleaner but loses code blocks and navigation structure"_ |
| **`BL-1` MongoDB Docs** | ~85 KB | 8KB (`Opus` elided); 32KB (`GLM` verbatim) | ~9–38% | _"Pipeline output is 8–32KB of filtered Markdown; raw HTML is 508KB; no tool produces the estimated size"_ |
| **`BL-3` Tutorial** | ~256 KB | 7.4KB (`Opus`, chunks 0–6 only); 463–474KB (`GLM`/`Gemini`, raw HTML) | ~3% pipeline; ~180% via curl | _"Pipeline abandoned for `curl`; `curl` output is Gatsby/React skeleton with no tutorial body content"_ |
| **`SC-2` Anthropic Docs** | ~1,026 chunks | 56MB (`Kimi`, full `llms-full.txt` corpus) | N/A — redirect target is the full documentation corpus | _"Scale outlier; VS Code tokenization, highlighting, and scroll disabled on open; file exists, environment degraded"_ |
| **`EC-3` Redirect JSON** | ~366 B | 366B (all 5 runs, identical content) | ~100% | _"Complete — 5-hop redirect chain followed cleanly; unique `X-Amzn-Trace-Id` per run confirms independent live requests"_ |

> _Implication: on the raw track, output size is determined by whether agents accept the pipeline or bypass it via `curl`, not by a retrieval ceiling. Pipeline-accepting runs cluster tightly by source URL regardless of agent. `curl`-bypass runs produce structurally valid files — large, correct path, clean endings — that contain no semantic page content. Neither outcome is distinguishable from a successful retrieval through path-and-size verification alone._

---

## Agent Behavior Patterns

Across 66 raw track runs, agent behavior sorted into four observable strategies. Strategy selection, not tool capability, was the primary predictor of output quality:

**Pipeline acceptance** — agents that accepted Cascade's Markdown output and wrote it verbatim produced the most consistent successful files. `SWE-1.6 Fast` (EC-1, EC-3), `Minimax M2.5` (SC-1, SC-4, EC-6), and `Claude Sonnet 4.6 Thinking` (EC-3, SC-4) represent this pattern. These runs clustered within a narrow size band per URL and passed content verification.

**Deliberate elision** — `Claude Opus 4.7` consistently read all chunks, assessed the output against practical write constraints, saved a partial file, and disclosed the decision. The behavior was documented in BL-1, BL-3, and SC-3 and is the only consistent instance across the dataset of an agent explicitly communicating a tradeoff between semantic fidelity and verbatim completeness before the user asked.

**`curl` bypass** — agents that correctly diagnosed the pipeline as returning processed Markdown switched to `curl` to retrieve "raw" content. The strategy consistently produced structurally valid files — large, correct path, clean endings — containing raw HTML or JS framework skeletons with no semantic page content. Observed across `Gemini 3.1`, `GLM-5.1`, `GPT-5.3-Codex`, and `SWE-1.6` across multiple tests.

**Silent failure** — false completion claims, cross-agent file reuse, and environment-degrading scale outliers. These runs produced metrics, checksums, and file paths for content that was either absent, identical to another agent's prior output, or unworkable as a project artifact. `Gemini 3.1` (EC-6 reuse), `GPT-5.3-Codex` (SC-3 false completion), and `Kimi K2.6` (SC-2 scale outlier) are the clearest instances.
