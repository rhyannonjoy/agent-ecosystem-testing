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
- [File Persistence Failures](#file-persistence-failures)
- [`read_url_content` Redirect Halt Behavior](#read_url_content-redirect-halt-behavior)
- [URL Fragment Targeting](#url-fragment-targeting)

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

---

## File Persistence Failures

Agents struggled to create files and save them during `BL-2` runs. The prompt explicitly required saving output to
`results/raw/raw_output_BL-2.txt`. Only `GLM-5.1` and `xAI Grok-3` wrote standalone project files to the correct path.
`Gemini 3.1`, `SWE-1.6`, and `Kimi K2.6` each produced output that appeared in the chat window with a file reference,
but it wasn't persisted as a discrete project artifact. Most runs required manual intervention to product a verifiable
file in the face of chat-window artifact substituion, cross-agent file reuse, and silent content truncation.

`SC-2` runs displayed a shift in this pattern from directory ambiguity to scale-driven abandonment: four of six agents
bypassed the Cascade pipeline entirely via `curl`, producing files that were either not persisted as project artifacts
or grew to sizes that degraded the development environment itself. `Kimi`'s output with the full `llms-full.txt` corpus
at 53.65 MB caused VS Code to disable tokenization, syntax highlighting, and scroll features for the file. The file existed,
but was effectively unworkable as a project artifact.

A file being present at the correct path isn't sufficient evidence of a successful retrieval. `GLM`'s `SC-2` output was
structured agent analysis rather than raw content; `Claude Sonnet 4.6`'s was a chunk index with a single header. Both passed
path verification while containing no target page content.

| **Agent** | **`BL-2`** | **`SC-2`** | **Results** |
|---|---|---|---|
| `Gemini` | _Chat only_ | _Chat only_ | `curl` output; manual copy required both runs |
| `GLM` | _Yes_ | _Yes_ | Saved; content: agent analysis, chunk index,<br>not entirely raw retrieval |
| `Grok` | _Yes_ | N/A | `BL-2` only; wrote file, only captured<br>2 of 3 chunks |
| `Kimi` | _Chat only_ | _Chat only_ | 53.65 MB; VS Code feature degradation on open |
| `Sonnet` | N/A | _Yes_ | Correct path; content: agent analysis, chunk index,<br>chunk position 0 summary |
| `SWE` | _No_ | _Yes_ | First run failed entirely; retry used `curl`;<br>saved stipped HTML only |

### Methodology Implication

The prompt directs agents to save output to `raw/`, which does't exist; `cascade-raw/` does. This ambiguity is intentional:
it tests whether agents reason about directory structure or resolve path instructions literally. `GLM` responded correctly
by creating `raw/` as a new directory. Later agents diverged; some wrote into `cascade-raw/` treating it as equivalent, others
failed to persist a file at all. Cross-agent file reuse, `SWE` pointing to `Gemini`'s output, suggests that once a plausible
file exists in the workspace, some agents will satisfy the persistence requirement by reference rather than by writing. The
prompt ambiguity is retained as a test variable for subsequent runs for observing path compliance and content fidelity.

---

## `read_url_content` Redirect Halt Behavior

The [interpreted track](friction-note-interpreted.md#read_url_content-internal-url-rewriting) and
[explicit track](friction-note-explicit.md#sc-2-url-redirect-behavior) both documented that no agent received the target content 
from `https://docs.anthropic.com/en/api/messages`, and left open whether the cause was tool-layer URL rewriting or a server-side redirect. `SC-2` runs on the raw track provide additional perspective.

Across six raw track agents, the redirect destination `https://platform.claude.com/docs/llms-full.txt` appeared consistently in the 
error payload with enough fidelity that three agents, `GLM-5.1`, `Kimi K2.6`, and `Claude Sonnet 4.6` successfully called 
`read_url_content` a second time against the redirect target and received valid chunked responses. This pattern is inconsistent 
with silent pre-network URL substitution: if the tool were rewriting before the request was made, the redirect destination wouldn't 
be actionable through a follow-up call. The more consistent explanation is that `read_url_content` makes the network call, receives 
a server-side redirect, identifies the destination in the error response, and halts rather than following automatically. Agent
interpretation of this information diverged:

| **Agent** | **Response** |
|---|---|
| `Gemini` | Bypassed pipeline entirely via `curl` |
| `GLM` | Followed redirect via second `read_url_content` call;<br>spent most time trying to find original target |
| `Kimi` | Followed redirect, then bypassed via `curl` for full corpus |
| `Sonnet` | Followed redirect, read chunk index, first position only |
| `SWE` | Hybrid Arena attempt; treated as terminal; attempted `search_web` fallback |
| `SWE` | Single retry; Bypassed via `curl`, but called it tool malfunction |

`SWE`'s first run remains notable for its fallback strategy and root cause diagnosis. It wasn't the only agent
to use `search_web`. `GLM` called it on the explicit track as a verification attempt, but it also didn't return any
usable results. `SWE` is the only agent to explicitly characterize the behavior as a tool-level bug on the raw track.
That diagnosis was reasonable given the absence of HTTP status codes in the agent's visible context, but the raw track's
successful follow-up calls suggest the mechanism is a redirect halt, not URL rewriting. Whether the redirect halt
originates from Cascade or Anthropic's server remains unconfirmed without HTTP-level instrumentation.

---

## URL Fragment Targeting

`OP-1` tests how agents handle URL fragments and whether they navigate to a target. `SWE-1.5` successfully isolated the target
section on the [interpreted track](friction-note-interpreted.md#url-fragment-targeting), suggesting fragment-targeting is
behavioral rather than architectural. In the raw track's first five `OP-1` runs all agents defaulted to full-document retrieval
and didn't acknowledge the target section:

| **Agent** | **Chunks<br>Analyzed** | **Context<br>Window** | **Fragment<br>Targeted?** | **File<br>Created?** |
|---|---|---|---|---|
| `Gemini` | 54 | ~1%<br>15K/1M | _No_ | _No_ |
| `GLM` | 92 | ~61%<br>123K/200K | _No_| _Yes_, chunk index,<br>HTML shell only |
| `GPT` | ~10 | ~9%<br>38K/400K | _No_ | _No_, terminal error |
| `Opus` | 92 | ~17%<br>173K/1M | _No_ | _No_, terminal error |
| `SWE` | 92 | ~28%<br>57K/200K | _No_ | _No_, chat headings only |

Secondary failures diverged significantly by agent. `GLM-5.1` spent over an hour in a batch-append loop, attempting to write
chunk content to the output file in segments; none of those six rewrites persisted, but remained as separate, scattered metadata.
`Gemini 3.1` completed without user permission, and when facing uncertainty about whether "exactly as received" referred to chunked
pipeline output or raw HTML, began exploring `curl` as an alternative, the same spiral documented in
[Agentic Task Drift, Token Overflow](#agentic-task-drift-token-overflow). `SWE-1.6` read all of the chunks, but closed the run in chat
with a list of headings, ignoring the bulk of the prompt and ending with:
"raw content has been successfully retrieved and is now available for comprehensive analysis or further use."
`GPT-5.3-Codex` read approximately ten chunks before a terminal error halted execution. `Claude Opus 4.7` retrieved all of the chunks
and attempted to write concatenated output in multiple steps, but the terminal command errored before any file was persisted.

### Methodology Implication

While the chunk index offers navigational structure, agents don't consult it for fragment resolution by default. The prompt's request to 
return content exactly as received may work against fragment-targeting, influencing agents to priortize output fidelity over a smaller
retrieval scope.
