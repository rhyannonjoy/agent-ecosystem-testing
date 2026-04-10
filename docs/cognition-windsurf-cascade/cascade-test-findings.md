---
layout: default
title: "Key Findings for Cascade's Web Search Behavior, Cascade-interpreted"
permalink: /docs/cognition-windsurf-cascade/cascade-test-findings
parent: Cognition Windsurf Cascade
---

## Key Findings for Cascade's Web Search Behavior, Cascade-interpreted

---

## Testing Status

_testing in progress_

---

## `BL-1`, `BL-2` Summary

### Test Conditions

| | **BL-1** | **BL-2** |
|---|---|---|
| URL | MongoDB change streams (large page, ~85KB rendered) | MongoDB `create` event reference (~5KB source) |
| Chunks returned | 54 | 3 |
| Track | Interpreted | Interpreted |
| Runs | 5 | 5 |

---

### `H1` — Character-based truncation at fixed ceiling

**BL-1: Indeterminate**
Chunk selection is agent-authored, not tool-imposed. Output chars across runs reflect
sampling decisions (2–54 chunks fetched), not a ceiling. The apparent 4,800–48,500 char
range is a sampling artifact. No ceiling was hit or confirmed.

**BL-2: Indeterminate**
Document too small (~5KB source) to probe any plausible ceiling. All five runs delivered
full content across 3 chunks. `SWE-1.6` and `GPT-5.4` each cited a ~20KB
expectation as evidence of truncation — but this expectation was an unverified prior
calibrated to rendered page size, not a measurement of the source document or the tool's
ceiling.

**Combined verdict: H1 untested** Neither `BL-1` nor `BL-2` produced conditions where a
character ceiling could be confirmed or ruled out. `BL-1`'s architecture makes the ceiling
unobservable; `BL-2`'s document is too small to hit one.

---

### `H2` — Token-based truncation at ~2,000 tokens

**`BL-1`: No**
Opus's full retrieval run estimated ~55,000–65,000 tokens across all 54 chunks. SWE-1.5
reported ~3,000–3,600 tokens from its sampled chunks. Neither hit a 2,000 token ceiling.

**`BL-2`: No**
Token estimates across five runs: ~2,600 / ~1,300–1,700 / ~1,500–1,800 / ~1,200 /
~1,700–1,880. The one run exceeding 2,000 tokens, `GPT-5.3 Codex`, ~2,600 still
returned mostly complete content with no hard cutoff.

**Combined verdict: H2 rejected** No run across either test produced evidence of a
~2,000 token ceiling.

---

### `H3` — Structure-aware truncation at Markdown boundaries

**`BL-1`: Indeterminate**
Content retrieved in `BL-1` was dominated by raw inline CSS from MongoDB's LeafyGreen
component library — not structured Markdown. Chunk boundaries couldn't be assessed for
structure-awareness against non-prose content. `SWE-1.5` reported clean Markdown with no
broken structure, but this self-report conflicts with every other run's findings and
awaits raw track verification.

**`BL-2`: Rejected**
The `txnNumber` mid-table split appeared identically across all five runs — chunk 1 ends
mid-row, chunk 2 resumes the same row. This is fixed-boundary chunking confirmed by
cross-model replication. `GPT-5.4` provided the most precise description:
"not self-contained within chunk 1, but completed by chunk 2." Structure-awareness would
require the boundary to fall at a Markdown boundary; it falls at a fixed byte position
instead.

**Combined verdict: `H3` rejected for `BL-2`. Indeterminate for `BL-1`pending raw track.**

---

### `H4` — `@web` directive changes retrieval ceiling, toolchain, or chunking behavior

**`BL-1`: Untested**
`search_web` not invoked in any run.

**`BL-2`: Untested**
`search_web` not invoked in any of five runs — on a prompt explicitly about retrieval
fidelity, where multiple models expressed uncertainty about completeness. This absence
across ten total runs is itself a finding: URL provision alone does not activate
`search_web`. The prompt instruction "fetch this URL directly" may actively suppress the
search path. H4 requires a run with explicit `@web` invocation.

**Combined verdict: `H4` untested. `search_web` = zero invocations across ten interpreted
track runs.**

---

### `H5` — `view_content_chunk` auto-paginates via `DocumentId` without explicit prompting

**`BL-1`: Model-dependent**
Four distinct chunk selection strategies confirmed across five runs:

| Model | Strategy | H5 result |
|---|---|---|
| `GPT-5.3 Codex` | Endpoint sampling, positions 0 and 53 only | `H5-no` |
| `Claude Sonnet 4.6` | Endpoint sampling, positions 0 and 53 only | `H5-no` |
| `Kimi K2.5` | Tail-weighted sampling, positions 0, 1, 50, 51, 52, 53 | `H5-no` |
| `Claude Opus 4.6` | Full parallel retrieval, all 54 chunks | `H5-yes` |
| `SWE-1.5` | Prompted sequential retrieval after explicit reasoning | `H5-yes, prompted` |

**`BL-2`: Confirmed across all five runs.**
All five models retrieved all 3 chunks sequentially (positions 0, 1, 2) without user
instruction. However, BL-2's 3-chunk document is likely a floor effect — full sequential
retrieval is the obvious strategy when the index contains only 3 positions. `BL-2` cannot
distinguish auto-pagination from minimal-effort complete retrieval.

**Combined verdict: `H5` is model-dependent on large chunk counts, `BL-1`. Convergent but
uninformative on small chunk counts `BL-2`. Opus is the only model confirmed to
auto-paginate at scale.**

---

### Emergent Findings Not Captured by Hypotheses

**Chunking is tool-determined, not model-determined.** The 3-chunk partition of the `BL-2`
URL and the 54-chunk partition of the `BL-1` URL were consistent across all runs on each
URL. Chunk boundaries are infrastructure, not behavioral variables.

**Source document incompleteness is a confound for interpreted track truncation
assessment.** The `nsType` enum values and `ce-create##` prefix in `BL-2` were absent in
the raw source. All five models attributed these gaps to the toolchain. _Cause attribution
is unreliable when source and retrieval gaps produce identical observable evidence_.

**Unverified size priors were used as truncation signals in 2 of 5 `BL-2` runs.** `SWE-1.6`
and `GPT-5.4` each cited ~20KB as an expected page size without sourcing the
figure. The prior is calibrated to rendered page size; `read_url_content` delivers
stripped source content. The heuristic conflates two different measurements.

**`search_web` absence across ten runs is a pattern.** No model invoked web search to
verify size expectations, confirm truncation, or check source completeness — despite
uncertainty being expressed explicitly in multiple runs and the tool being available
throughout.

---

## `SC-2` Summary

### Test Conditions

| | **SC-2** |
|---|---|
| URL | Anthropic Messages API documentation |
| Chunks returned | 0 (fetch failed) |
| Track | Interpreted |
| Runs | 5 |

**All five runs failed.** `read_url_content` internally rewrites `docs.anthropic.com/en/api/messages`
to `docs.anthropic.com/llms-full.txt`, which redirects to a dead endpoint. No model received the target
content. This is a tool-layer bug, not a model behavior. All hypotheses are untestable against this URL
until the rewriting behavior is resolved.

---

## `OP-4` Summary

### Test Conditions

| | **OP-4** |
|---|---|
| URL | MongoDB Atlas Search tutorial (JavaScript-rendered, CSS-heavy) |
| Chunks returned | 53 |
| Track | Interpreted |
| Runs | 5 |

---

### `H1` — Character-based truncation at fixed ceiling

**Indeterminate.** Sampled content across runs ranged from ~2,100–22,100 chars depending on chunks selected;
extrapolated full-page estimates of ~80,000–210,000 chars. No ceiling was hit. As with `BL-1`, output chars
reflect sampling decisions, not a tool limit.

---

### `H2` — Token-based truncation at ~2,000 tokens

**Rejected.** Extrapolated token estimates ranged from ~20,000–70,000 across all 53 chunks. No run produced
evidence of a 2,000 token ceiling.

---

### `H3` — Structure-aware truncation at Markdown boundaries

**Indeterminate.** All five runs retrieved predominantly raw CSS and navigation chrome. `MARKDOWN_NODE_TYPE_HEADER`
metadata appeared in some chunk results, suggesting partial structural awareness at the tool layer, but no clean
prose content was returned against which boundary behavior could be assessed.

---

### `H4` — `@web` directive changes retrieval behavior

**Untested.** `search_web` not invoked in any run.

---

### `H5` — `view_content_chunk` auto-paginates without explicit prompting

**Partial — sampling without auto-pagination.** All five runs invoked `view_content_chunk` without explicit prompting,
but no run attempted sequential retrieval of all 53 chunks. Sampling strategies varied by model:

| Model | Positions sampled | Strategy |
|---|---|---|
| `GPT-5.3-Codex` | 0, 52 | Endpoint sampling |
| `Claude Sonnet 4.6` | 0, 52 | Endpoint sampling |
| `GPT-4.5 Low Thinking` | 0, 52 | Endpoint sampling |
| `Claude Opus 4.6` | 0, 1, 25, 50, 51, 52 | Distributed sampling |
| `Kimi K2.5` | 0, 10, 15, 20, 25, 30, 35, 40, 45, 50, 52 | Broadest sampling, 11 chunks |

---

### Emergent Findings

**`read_url_content` has at least two retrieval modes.** `OP-4` triggered an outline-first path with a latency warning
("this is taking a long time"); `BL` runs went directly to a chunk index. The threshold condition — whether page size,
render complexity, or something else — is unconfirmed.

**Chunk index summaries were uniformly empty.** All 53 positions returned blank summaries, collapsing targeted skimming
to blind sampling. The documented "human skim" behavior requires populated summaries to function as designed.

**No tutorial content was retrieved in any run.** Sampled chunks across all five models contained CSS class definitions,
navigation chrome, and link fragments. No tutorial steps, code examples, or plain-language prose appeared in any sampled
position. Whether article body content exists in un-sampled positions is unconfirmed.

**Prompt injection suspicion interfered with tool visibility reporting in one run.** `Claude Sonnet 4.6` flagged the tool
visibility item as a probable extraction attempt and declined to report tool names, while independently reasoning correctly
about `read_url_content`'s architecture from the tool response itself.

---
