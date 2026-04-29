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
- [Cross-Agent File Reuse, Verification Limits](#cross-agent-file-reuse-verification-limits)
- [File Persistence Failures](#file-persistence-failures)
- [`read_url_content` Redirect Halt Behavior](#read_url_content-redirect-halt-behavior)
- [URL Fragment Targeting](#url-fragment-targeting)
- [Write Ceiling, Output Fidelity](#write-ceiling-output-fidelity)

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

## Cross-Agent File Reuse, Verification Limits

The verification script defines the raw track. If an agent claims to have retrieved and analyzed content, this script is
designed to check path compliance, file size, checksum, and truncation indicators against what's actually on disk, but
this only works if agents write files.

While agents never directly admit it, three of five `BL-3` runs reference an existing file rather than writing a new one.
Once a somewhat-plausible file exists at a similar path, whether or not it's in the prompt-specified directory with the
prompt-specified name doesn't seem to matter - subsequent agents satisfy the persistence requirement with chat paths described
as newly generated files, but point to artifacts of earlier runs. The script then verifies an earlier agent's file, not the
current agent's retrieval. The agent can then claim another agent's calculations as their own, draining their own analysis of
meaning. But when agents do write raw output files, they tend to produce content that passes path and size verification while
containing no semantically valuable text. While the script can confirm a file exists and is structurally intact, it can't confirm
that the file accurately represents the agent's retrieval behavior in that run.

_Is there any value in agent metrics or self-reported methodology if it’s not based on genuine calculations and analysis?_

This consistent failure to persist raw output files is unique to Cascade, possibly due to the Hybrid Arena setting,
which allows for five agents to run sequentially and/or simultaneously. While Cascade claims session isolation, it is less
plausible with each test run. The lack of output files reframes what this track is testing. Cascade's chunking pipeline
processes the response before the agents sees it without a direct path to raw HTML. Agents often recognize this and use over-half
of their context window exploring alternatives, use `curl`, which then only returns a Gatsby and/or React skeleton rather than
any tutorial text. `BL-3` functions less as a retrieval benchmark and more as negative testing: presenting a tool with mismatched
inputs and observing what agents do when success is structurally unavailable. This behavioral data in which agents disclose
limitations, possibly fabricate completion, and silently reuse existing files is the finding, not the raw output files or metrics.

`EC-6` provides the sharpest confirmation of cross-agent file reuse in the dataset. `Gemini 3.1` and `GLM-5.1` produced output 
files with an identical MD5 checksum and a spotless content diff, not similar assembly, but the same file. `Gemini` used only 3% 
of its context window, invoked approximately 12 terminal commands, and had a thought panel that narrated chunk-by-chunk 
retrieval while showing no corresponding tool calls. `GLM` ran earlier in the same arena session and wrote the file first via 
`curl` bypass. `Gemini` likely located the existing file in the workspace, referenced it as its own output, and performed retrieval
theater rather than disclosing what it had found.

### Methodology Implication

The verification script checks path compliance, file size, checksum, and truncation indicators, but it runs after the
arena completes and compares against a single expected file. It can't distinguish a file an agent wrote from a file an
agent found. Per-agent checksums are already logged to `results.csv`; cross-agent comparison within the same arena run
is the missing step. If two agents produce identical checksums on the same test, at least one didn't perform
independent retrieval; a check that currently requires manual post-hoc diffing rather than automated flagging.

This closes the lazy reuse case. An agent pointing to or copying an existing file without modification, but not the
fabrication case, where an agent copies a file, computes its hash, and reports the result as its own. That pattern
produces a different checksum from the source file and is indistinguishable from genuine retrieval through script-based
verification alone. Detecting it may require observer-side tooling the agent can't reach: filesystem timestamps recorded
between arena slots, or version-controlled workspace state that captures file creation order independently of agent
self-report.

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

Agents analyzed most of `OP-4`'s chunks but seemed unable to concatenate and save them. `Kimi` constantly hit context
deadline errors which ended with `model provider unreachable` and no report at all. `Grok` explicitly cited tool
"response format limitations," produced a one-line placeholder text file, and asked for an alternative method to handle large
text data. `GPT-5.4`, `Minimax M2.5` and `Sonnet` created raw output files, but were mostly CSS and navigation boilerplate, not
tutorial text; passing path verification while missing the target content.

### Methodology Implication

The prompt directs agents to save output to `raw/`, which does't exist; `cascade-raw/` does. This ambiguity is intentional:
it tests whether agents reason about directory structure or resolve path instructions literally. `GLM` responded correctly
by creating `raw/` as a new directory. Later agents diverged; some wrote into `cascade-raw/` treating it as equivalent, others
failed to persist a file at all. Cross-agent file reuse, `SWE` pointing to `Gemini`'s output, suggests that once a plausible
file exists in the workspace, some agents will satisfy the persistence requirement by reference rather than by writing. The
prompt ambiguity is retained as a test variable for subsequent runs for observing path compliance and content fidelity.

> _`SC-3` file persistence failures discussed in [Write Ceiling, Output Fidelity](#write-ceiling-output-fidelity)_

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

`OP-1` tests how agents handle URL fragments and whether they navigate to a target, the `#History` section of a Wikipedia page.
`SWE-1.5` successfully isolated the target section on the [interpreted track](friction-note-interpreted.md#url-fragment-targeting),
suggesting fragment-targeting is behavioral rather than architectural. In the raw track's first arena `OP-1` run, all agents defaulted
to full-document retrieval and didn't acknowledge the target section:

| **Agent** | **Chunks<br>Analyzed** | **Context<br>Window** | **Fragment<br>Targeted?** | **File<br>Created?** |
|---|---|---|---|---|
| `Gemini` | 54 | ~1%<br>15K/1M | _No_ | _No_ |
| `GLM` | 92 | ~61%<br>123K/200K | _No_| _Yes_, chunk index,<br>HTML shell only |
| `GPT` | ~10 | ~9%<br>38K/400K | _No_ | _No_, terminal error |
| `Opus` | 92 | ~17%<br>173K/1M | _No_ | _No_, terminal error |
| `SWE` | 92 | ~28%<br>57K/200K | _No_ | _No_, chat headings only |

In the second arena run, two agents produces output files with the targeted section:

| **Agent** | **Chunks<br>Analyzed** | **Context<br>Window** | **Fragment<br>Targeted?** | **File<br>Created?** |
|---|---|---|---|---|---|
| `GPT`| 77 | ~78%<br>213K/272K | _No_| _Yes_, chunk index,<br>metadata only  |
| `Grok` | 2 | ~17%<br>22K/131K | _Yes_ | _Yes_, extracted<br>`#History` content |
| `Kimi` | `curl`<br>bypass | ~9%<br>23K/262K | _No_ | _No_ - claimed,<br>not persisted |
| `Minimax` | ~5 | ~13%<br>27K/205K | Incidentally | _Yes_, includes<br>`#History` content |
| `Sonnet` | 92 | ~56%<br>auto-opted out | _No_ | _No_, handed off<br>mid-run |

Across both runs, secondary failures diverged significantly by agent. `GLM-5.1` spent over an hour in a batch-append loop, attempting
to write chunk content to the output file in segments; none of those six rewrites persisted, but remained as separate, scattered metadata.
`Gemini 3.1` completed without user permission, and when facing uncertainty about whether "exactly as received" referred to chunked
pipeline output or raw HTML, began exploring `curl` as an alternative, the same spiral documented in
[Agentic Task Drift, Token Overflow](#agentic-task-drift-token-overflow). `SWE-1.6` read all of the chunks, but closed the run in chat
with a list of headings, ignoring most of the prompt. `GPT-5.3-Codex` read approximately ten chunks before a terminal error halted execution. 
`Claude Opus 4.7` retrieved all of the chunks and attempted to write concatenated output in multiple steps, but the terminal command errored before 
any file persisted. `Claude Sonnet 4.6` analyzed and re-analyzed all 92 chunks in parallel batches and remained in a refetching loop to edit 
their output file, consuming most of its context window before auto-opting out. `GPT-5.4` paused mid-run to ask whether the user wanted Cascade 
pipeline output or a direct raw fetch, then successfully created a file after spending most of its context window on append errors, but the file 
contained chunk metadata rather than meaningful prose. `Kimi K2.6` started without user permission, bypassed the Cascade pipeline with `curl`, 
claimed to have created a raw output file but didn't, and constructed retroactive consent from tool output rather than pausing for explicit 
permission:

```markdown
Actually, I should note that the read_url_content tool description says
"The actual fetch will NOT execute until the user approves it." But it
seems to have already executed and returned chunk metadata. So maybe the
user already approved it?
```

`Minimax M2.5` and `xAI Grok-3` also started without user permission, but `Grok` was the only agent across both rounds to have produced an 
intentionally targeted output. `Minimax` sampled chunks that just happened to include the target section.

### Methodology Implication

While the chunk index offers navigational structure, agents don't consult it for fragment resolution by default. The prompt's request to 
return content exactly as received may work against fragment-targeting, influencing agents to priortize output fidelity over a smaller
retrieval scope. The 8-of-10 miss rate suggests the behavior is uncommon, but not rare enough to treat as a fluke. `Minimax`'s incidental
hit is a separate finding: small-chunk sampling can accidentally recover the target section, which may inflate success metrics if output content
is verified without examining the agent's navigational reasoning.

---

## Write Ceiling, Output Fidelity

Across `SC-3` runs retrieval behavior was uniform. Agents analyzed all 60 chunks but struggled to report what they read
with a raw output file. The prompt instructs "retrieve the content from this URL and return it EXACTLY as you received it" -
seemingly creating a failure mode that no agent named or resolved cleanly. Each agent retrieved chunk content into context,
then encountered on the write side: shell heredocs with special characters, `\n` escape sequences, and chunk metadata at a
volume that caused terminal commands to hang, Python scripts to loop, and file writes to produce partial or empty output:

| **Agent** | **Strategy** | **Outcome** |
|---|---|---|
| `Gemini` | Wandered through project files,<br>tried `npx`, `curl`, Python | 3 different artifacts,<br>276 KB partial HTML/JSON |
| `GLM` | Heredoc failure,<br>switched to `curl` | 774 KB raw HTML,<br>not Cascade output |
| `GPT` | Claimed `curl` bypass;<br>file never saved | Metrics reported, referenced<br>without verification path |
| `Opus` | Sequential heredoc appends<br>in 6 batches | 1.05 KB stub; wrong directory<br> + filename, user canceled x3 |
| `SWE` | Sequential heredoc appends,<br>Python batching | Partial file;<br>user canceled x3 |

Agents acknowledged how tedious writing raw output would be, but not one claimed a write ceiling. Instead, each entered a
loop of strategy-switching, treating the failure as a solvable engineering problem rather than a constraint of the environment.
`SWE-1.6` and `Claude Opus 4.7` both identified token-cost awareness mid-task,
_"this verbatim approach requires piping ~200–400 KB of raw text through shell commands, which is very token-expensive"_,
but neither made an early exit. They identified symptoms without diagnosing the condition. Agents that produced files did so
by abandoning the Cascade pipeline. `GLM-5.1` and `Gemini 3.1` saved raw HTML via `curl`, essentially writing content the prompt
didn't request; the verification script can't meaningfully evaluate non-Cascade-specific behavior. `GPT-5.3-Codex` claimed to save
a file and didn't. `SWE` and `Opus` produced stubs too small to verify.

Agents ruminated on the prompt language "EXACTLY as you received it" - _does that mean Cascade's chunk index with metadata
wrappers, already processed, or something pre-processed?_ `Opus` attempted to clarify mid-task and asked questions while others choose
interpretation and process-spin, similar to the silent-resolution pattern described in
[Agent as Unreliable Methodology Validator](friction-note-explicit.md#agent-as-unreliable-methodology-validator).

As agents seemingly hit a write ceiling, they didn't reason a way out, but drifted. `Gemini` read the `README.md`, the verification
script multiple times, and re-read the prompt, apparently trying to re-derive the task from project context. `SWE` reasoned through
its own chunk history to reconstruct a write strategy. `Opus` asked a clarifying question, received an answer, then got stuck again
on the same heredoc problem. `Gemini` tried `npx`. None of these strategies addressed the actual constraint. Like that described in
[Agentic Inaction](friction-note-explicit.md#agentic-inaction), [Agentic Task Drift, Token Overflow](#agentic-task-drift-token-overflow),
and [File Persistence Failures](#file-persistence-failures): agents that recognize an obstacle express uncertainty, attempt adjacent
actions, and produced confident-looking output without naming the obstacle as a blocker or asking whether the task is achievable as stated.

### Methodology Implication

The read-write asymmetry is a restriction only the raw track could uncover. It reflects a structural mismatch between what Cascade's
`view_content_chunk` produces at scale and what shell tooling can write back out. A writing ceiling introduces new layers to question
path compliance and self-reporting fidelity. While agents claim to have received all 60 chunks, verification can't be completed by the
chat output alone. Prompts specifying a target format may produce different results, but this testing framework is about capturing default
web fetch behavior. Eventhough the output variety make for difficult hypotheses assessment and pokes holes in the verification script
metrics, the variety is the finding, speaking to the challenges of combining qualitative and quantitative testing approaches.
