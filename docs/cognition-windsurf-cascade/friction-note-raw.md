---
layout: default
title: "Friction Note"
permalink: /docs/cognition-windsurf-cascade/friction-note-raw
parent: Cognition Windsurf Cascade
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide - Raw Track

- [Agentic Task Drift, Token Overflow](#agent-task-drift-token-overflow)

---

## Agentic Task Drift, Token Overflow

`Gemini 3.1`'s `BL-1` run began on track. It analyzed all chunks from the URL, but once it recognized that
the pipeline returns a processed response and not a raw one, it exceeded the session token limit trying to
correct that, and ultimately failed to generate an output file for verification. `Gemini` used `curl` to fetch the raw
source, received 508 KB, significantly larger than the prompt's ~85 KB estimate, then kept exploring alternative methods
to reconcile the size discrepancy. Alongside the size mismatch, the thought panel displayed content resembling a chunk
index with empty summaries, suggesting that the absence of navigational signal also contributed to this overcorrection*.
Having exhausted tool-based solutions, the agent treated adjacent codebase artifacts as methodology documentation, a
reasonable inference in a research project, but also, incorrect here. The Copilot framework's raw output files
are just that: outputs, not specifications. The sequence below is reconstructed from thought panel snapshots, but the
loop count is unknown; steps likely repeated:

| **Step** | **Behavior** | **Detail** |
|------|----------|--------|
| **1** | **Successful Retrieval** | Reads all 54 chunks via `read_url_content`, `view_content_chunk`; summaries empty |
| **2** | **Diagnoses Correctly** | Recognizes pipeline returns processed Markdown, not raw HTML; switches to `curl` |
| **3** | **Acknowledges Size Mismatch** | `curl` returns 508 KB; prompt ~85KB; no available tool<br>produces expected size |
| **4** | **Manual Intervention** | User cancels stuck terminal commands; agent ruminates on canceled commands, chunk index |
| **5** | **False Block** | Claims output file already exists, but incorrect |
| **6** | **Attempts<br>Re-retrieval** | _"Searched web"_ without claiming `search_web`; re-analyzes chunks |
| **7** | **Probes<br>`curl`** | Tries `curl` with varied headers, flags including<br>`Accept: application/json` |
| **8** | **Searches<br>MCP Cache** | Investigates whether `read_url_content` writes a local cache; searches `~/.windsurf` for stored page content |
| **9** | **Codebase<br>Drift** | Locates different testing framework artifacts; <br>`copilot-web-content-retrieval/results/raw/raw_output_EC-6_run_3.txt` |
| **10** | **Misreads Artifact** | Reads `EC-6` output as methodology guidance;<br>attempts `npx afdocs`; command canceled |
| **11** | **Prohibited Tool Use** | Examines `web_search_verify_raw_results.py` despite<br>instructions restricting use |
| **12** | **Pivots to `write_to_file`** | Considers assembling chunks via `write_to_file`; considers if ~21,000 tokens exceeds Cascade's limit |
| **13** | **Searches System** | Inspects `/User/History`, `state.vscdb`, `/tmp`, `Windsurf.log`<br>for cached raw content |
| **14** | **Mines<br>Log** | Finds previous response in `Windsurf.log`; attempts to<br>extract `leafygreen-ui` segment |
| **15** | **Loses<br>Context** | Can no longer locate original user prompt;<br>speculates instructions truncated |
| **16** | **Exceeds<br>Token Limit** | Aborts output generation mid-run |
| **17** | **Generates Report** | Apologizes for CSS bloat; asks how to proceed |

### Methodology Implication

The prompt's size estimation may act as a confound in this track. If no available tool produces that size, agents
with output-fidelity monitoring may spiral rather than approximate. Consider whether the size expectation belongs in the
prompt at all, or only in post-hoc analysis.

> *_Empty summaries' impact on pagination explored in [Friction: Interpreted](friction-note-interpreted.md#read_url_content--fetch-architecture-and-parsing-limits)_
