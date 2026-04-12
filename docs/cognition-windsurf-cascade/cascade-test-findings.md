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

## `OP-1` Summary

### Test Conditions

| | **OP-1** |
|---|---|
| URL | Wikipedia Machine Learning article with `#History` fragment (`https://en.wikipedia.org/wiki/Machine_learning#History`) |
| Chunks returned | 91 |
| Track | Interpreted |
| Runs | 5 |

### `H1` — Character-based truncation at fixed ceiling

**Indeterminate.** Output chars reflect sampling decisions across runs. GPT-5.4 Low received ~8.3K chars from the manifest only; Opus extrapolated ~100–200KB across 91 chunks from a 3-chunk sample; SWE-1.5 estimated 40,000–60,000 chars with no ceiling hit. No run produced conditions where a character ceiling could be confirmed or ruled out.

---

### `H2` — Token-based truncation at ~2,000 tokens

**Rejected.** SWE-1.5 estimated 12,500–15,000 tokens across retrieved chunks with no cutoff. Opus extrapolated 12,500–15,000 tokens from sampling. GPT-5.4 Low estimated ~2.0–2.2K tokens from the manifest only — close to a 2K ceiling but against index content, not article body. No run produced a hard token cutoff.

---

### `H3` — Structure-aware truncation at Markdown boundaries

**Indeterminate.** No run retrieved enough contiguous content to assess boundary behavior. SWE-1.5 reported clean Markdown structure across sampled chunks; Opus identified logical section boundaries in its representative sample. Neither confirms structure-awareness at the tool layer without raw track verification.

---

### `H4` — `@web` directive changes retrieval behavior

**Untested.** `search_web` not invoked in any run.

---

### `H5` — `view_content_chunk` auto-paginates without explicit prompting

**Model-dependent.** Sampling strategies varied significantly:

| Model | Positions sampled | Fragment targeted? | H5 result |
|---|---|---|---|
| `Claude Sonnet 4.6` | 0, 89, 90 | No | `H5-no` |
| `GPT-5.4 Low` | None — manifest only | No | `H5-no` |
| `Claude Opus 4.6` | 0, 45, 90 | No | `H5-no` |
| `SWE-1.5` | 0, 1, 16, 89, 90 | Yes — confirmed History at position 16 | `H5-yes, prompted` |
| `GPT-5.3-Codex` | — | — | — |

### Emergent Findings

**URL fragment targeting is model-dependent and mostly absent.** `OP-1` tests whether agents navigate to the `#History` fragment rather than sampling arbitrarily. 4 of 5 runs treated the URL as a generic page retrieval target. `SWE-1.5` is the only model that attempted fragment-targeted retrieval and confirmed the History section at chunk position 16.

**`GPT-5.4 Low` did not invoke `view_content_chunk` at all.** It stopped at the index, reported the architecture accurately, flagged incompleteness, and stopped. The most transparent run about what it actually received; the least retrieval attempted.

**`Opus` reported no truncation from a 3-of-91 sample.** Rather than flagging incomplete sampling, `Opus` cited the chunked architecture to answer the truncation question: chunking structurally prevents monolithic truncation, therefore no truncation. The answer is accurate within its frame; the frame excludes whether the fragment target was retrieved. See [URL Fragment Targeting — Interpreted](friction-note#url-fragment-targeting--interpreted) in the friction note.

**The truncation question in the prompt is ambiguous under chunked architecture.** A model that understands the two-phase retrieval system can answer "no truncation" in good faith while having retrieved a small fraction of available content. The question doesn't distinguish between monolithic truncation and partial sampling, and accurate architectural knowledge makes the gap invisible in the output.

---

## `BL-3` Summary

### Test Conditions

| | **BL-3** |
|---|---|
| URL | MongoDB Atlas Search tutorial (JavaScript-rendered, CSS-heavy) |
| Chunks returned | 53 |
| Track | Interpreted |
| Runs | 5 |

---

### `H1` — Character-based truncation at fixed ceiling

**Indeterminate, with double-truncation confirmed by one run.** Visible character counts
varied by retrieval depth: `Sonnet` runs returned index-only (~2,200 chars); `Kimi K2.5`
sampled ~11 chunks estimating 180,000–220,000 chars; `SWE-1.6` extrapolated ~245,000 chars
from full retrieval; `Opus` measured ~106,000 visible chars against ~242KB estimated source.
No ceiling was hit. `Opus` identified per-chunk output limits (~2K chars visible each) impose a
second truncation layer on top of the chunking architecture itself, making a single character
ceiling unobservable.

---

### `H2` — Token-based truncation at ~2,000 tokens

**Rejected.** `Opus` estimated 26,000–30,000 visible tokens across all 53 chunks with no
cutoff. `SWE-1.6` extrapolated ~61,250 tokens. No run produced evidence of a 2,000 token
ceiling. The ~2K chars/chunk per-chunk limit, `Opus` identified, is consistent with a per-chunk
output constraint, not a document-level token ceiling.

---

### `H3` — Structure-aware truncation at Markdown boundaries

**Rejected.** Truncation boundaries were inconsistent across runs and uniformly
non-structural. Three models (Opus, SWE-1.6, Kimi K2.5) ended at
`Next\nAutocomplete and Partial Matching` — navigation chrome at position 52. GPT-5.3
Codex ended at `as-search/tutorial/. Choose at least one position.`, consistent with
a `view_content_chunk` call boundary. Claude Sonnet 4.6 (Run 2) ended at
`margin-top:calc(-1 * (190px + 85px));}}` — mid-CSS rule. No run produced a cutpoint
at a Markdown boundary. The variation across runs confirms that boundaries are
positional artifacts of the chunking architecture and per-chunk output limits, not
structure-aware.

---

### `H4` — `@web` directive changes retrieval behavior

**Untested.** `search_web` not invoked in any run.

---

### `H5` — `view_content_chunk` auto-paginates without explicit prompting

**Model-dependent, with three distinct strategies observed.**

| Model | Chunks fetched | Strategy | H5 result |
|---|---|---|---|
| `GPT-5.3-Codex` | 2 | Endpoint sampling (0, 52) | `H5-no` |
| `Claude Sonnet 4.6` | 0 | Manifest only | `H5-no` |
| `Claude Opus 4.6` | 53 | Full sequential retrieval | `H5-yes` |
| `SWE-1.6 Fast` | 53 | Full sequential retrieval | `H5-yes` |
| `Kimi K2.5` | ~11 | Distributed sampling | `H5-partial` |

Full pagination, `Opus`, `SWE-1.6` and non-pagination `GPT-5.3-Codex`, `Claude Sonnet 4.6`,
represent the extremes. `Kimi K2.5` introduced a third behavior: deliberate sampling without
exhaustive retrieval. The two non-paginating runs differed from each other — `GPT-5.3-Codex`
sampled two endpoint chunks while Sonnet stopped at the manifest — confirming that non-pagination
isn't a uniform strategy, but a spectrum. Model capability tier appears to be a stronger predictor
of pagination depth than prompt variation alone.

---

### Emergent Findings

**Double-truncation renders the tool combination ineffective for CSS-heavy pages.** `Opus`
is the only model to correctly characterize the retrieval failure: chunking splits the
document into 53 positions, and per-chunk output limits then truncate each position
individually. The result is ~106K visible characters from ~242KB source — approximately
56% retrieval — almost entirely CSS class definitions and navigation chrome from MongoDB's
LeafyGreen UI framework. No tutorial steps, code examples, or plain-language prose were
retrieved in any sampled position across any run.

**Self-assessment reliability varied significantly by model.** `Opus` identified
double-truncation and declared the tool combination "essentially unusable for extracting
the substantive content of this particular page." `SWE-1.6` retrieved identical data and
reported "no truncation" and "complete," conflating CSS/navigation chrome completeness
with content completeness. `Kimi K2.5` similarly reported no truncation while noting
incomplete Markdown, a direct contradiction that sampling obscured rather than resolved.

**Chunk manifest summaries were uniformly empty.** All 53 positions returned blank
summaries in the index. This collapsed any targeted skimming strategy to blind positional
sampling, which explains partial and endpoint-only retrieval patterns in lower-performing
runs. The `Sonnet` run agent explicitly cited empty summaries as its rationale for not
invoking `view_content_chunk` at all.

**H5 non-determinism is rationalization-dependent, not purely stochastic.** The `Sonnet`
run agent reasoned its way to stopping using the empty summaries as justification. This
suggests that pagination decisions are downstream of chain-of-thought rationalization, not
just sampling temperature — making `H5` behavior sensitive to manifest content even when
that content is uninformative.

> **`Opus` run 3**: "The `read_url_content` and `view_content_chunk` pipeline retrieved
> ~242KB of raw page data split across 53 chunks, but double-truncated it: first by
> chunking, then by per-chunk output limits (~2K chars visible each). The result is ~106K
> visible characters, almost entirely CSS/navigation chrome, with the actual tutorial
> content inaccessible. For content-heavy documentation pages with heavy CSS-in-JS
> frameworks, this tool combination fails to surface the substantive content."

---

## `SC-1` Summary

### Test Conditions

| | **SC-1** |
|---|---|
| URL | Gemini API URL context documentation (well-structured, code-heavy) |
| Chunks returned | 14 |
| Track | Interpreted |
| Runs | 5 |

---

### `H1` — Character-based truncation at fixed ceiling

**Indeterminate.** Character counts varied by model and counting method: ~22,000–47,600
chars across 10–14 chunks depending on run. `Opus` provided the most granular breakdown,
distinguishing navigation chrome (chunks 0–4, ~16,800 chars) from article content (chunks
5–13, ~13,600 chars). No ceiling was hit. The page is small enough that full retrieval
doesn't stress a limit.

---

### `H2` — Token-based truncation at ~2,000 tokens

**Rejected.** Token estimates ranged from ~4,427–11,900 across runs with no cutoff
observed.

---

### `H3` — Structure-aware truncation at Markdown boundaries

**Indeterminate, with intra-run disagreement.** `Kimi K2.5` and `SWE-1.6` reported
complete, clean Markdown with all code blocks properly closed. `Opus` and `Sonnet`
both reported "partially degraded" — code blocks embedded as single-line strings,
headers represented as structured metadata outside the text body rather than `#` syntax,
and content duplication per chunk. The disagreement across runs on identical content
suggests Markdown quality assessment is model-dependent, and earlier runs may have
over-reported quality. Raw track verification is needed to establish ground truth.

---

### `H4` — `@web` directive changes retrieval behavior

**Untested.** `search_web` not invoked in any run.

---

### `H5` — `view_content_chunk` auto-paginates without explicit prompting

**Supported across all runs, with one novel behavior.**

| Model | Chunks fetched | Strategy | H5 result |
|---|---|---|---|
| `GPT-5.3-Codex` | 14 (0–13) | Full sequential | `H5-yes` |
| `Kimi K2.5` | 14 (0–13) | Full sequential | `H5-yes` |
| `SWE-1.6 Fast` | 14 (0–13) | Full sequential | `H5-yes` |
| `Claude Opus 4.6` | 14 (0–13) | Full parallel | `H5-yes` |
| `Claude Sonnet 4.6` | 10 (0, 5–13) | Summary-guided selective exclusion | `H5-yes` |

All five runs paginated without explicit prompting — the first test where `H5-yes` is
confirmed across all models. `Opus` is the first run to retrieve chunks in parallel rather
than sequentially. `Sonnet` introduced a new behavior: using empty `/` summaries for
chunks 1–4 to actively exclude them as navigation boilerplate, retrieving only the 10
substantive content chunks.

---

### Emergent Findings

**Populated chunk summaries enable targeted retrieval.** `SC-1` is the first test where
chunk index summaries were populated with meaningful content — section headings, content
types - Python, Javascript, REST, and page title. This directly contrasts with the uniformly
empty summaries in `OP-4` and `BL-3`, confirming summary population is URL-dependent
rather than a universal tool behavior. The documented "human skim" behavior functioned
as designed on this URL.

**Summary-guided exclusion is a new pagination behavior.** `Sonnet` is the first model
to use populated chunk summaries as a *filtering* signal rather than a targeting signal —
skipping chunks whose summaries indicated navigation chrome rather than sampling or
retrieving exhaustively. This is only possible when summaries are populated; the behavior
collapses to blind sampling on URLs where summaries are empty.

**The UI Tooltip Gap is behavioral, not architectural.** Across runs 1–3, chunk summaries
visible in the Cascade UI tooltip were not referenced in model output, raising the question
of whether models receive summaries in their tool response. `Opus` on run 4 explicitly
confirmed that `read_url_content` returned "positions and summaries," and `Sonnet` of run 5
demonstrably acted on summary content. The gap in earlier runs reflects models receiving
but not reporting or acting on summaries, a behavioral variance, not a tool delivery gap.

**Chunk count affects full-pagination likelihood.** All five models paginated fully or
near-fully on 14 chunks. No model attempted full retrieval on 50+ chunk URLs in `BL-3`
and `OP-4` without being the highest-capability model in the run. The 14-chunk count may
fall below a threshold where full retrieval feels tractable to most models regardless
of capability tier.

---

## `SC-3` Summary

### Test Conditions

| | **SC-3** |
|---|---|
| URL | Wikipedia List of Countries and Dependencies by Population (table-heavy, ~100KB) |
| Chunks returned | 59 |
| Track | Interpreted |
| Runs | 5 |

---

### `H1` — Character-based truncation at fixed ceiling

**Indeterminate.** Estimates ranged from ~6,777 chars actually received from `Kimi K2.5` -
measurement of tool responses only - to ~118,000 chars extrapolated from endpoint
sampling from `Sonnet`. No ceiling hit. `Kimi K2.5` produced the most accurate `H1` response
by reporting only what it received rather than extrapolating — the only run across `SC-3`
to do so.

---

### `H2` — Token-based truncation at ~2,000 tokens

**Rejected.** Estimates ranged from ~1,694 tokens from `Kimi K2.5`, received only to
~29,500 tokens extrapolated from `Sonnet`. No cutoff observed.

---

### `H3` — Structure-aware truncation at Markdown boundaries

**Untestable this run set.** No model fetched any chunk within positions 3–13, where the
population table is located. The test objective — table row and column preservation at
chunk boundaries — was not reached in any of the five runs.

---

### `H4` — `@web` directive changes retrieval behavior

**Untested.** `search_web` not invoked in any run.

---

### `H5` — `view_content_chunk` auto-paginates without explicit prompting

**Not supported at this chunk count.** All five runs defaulted to endpoint or distributed
sampling, fetching 2–3 chunks of 59.

| Model | Chunks fetched | Strategy | H5 result |
|---|---|---|---|
| `GPT-5.3-Codex` | 2 (0, 58) | Endpoint sampling | `H5-no` |
| `Claude Sonnet 4.6` | 2 (0, 58) | Endpoint sampling | `H5-no` |
| `Claude Opus 4.6` | 3 (0, 30, 58) | Distributed sampling | `H5-no` |
| `SWE-1.6 Fast` | 3 (1, 30, 58) | Distributed sampling | `H5-no` |
| `Kimi K2.5` | 2 (0, 58) | Endpoint sampling | `H5-no` |

### Emergent Findings

**Populated summaries didn't produce targeted retrieval at 59 chunks.** Unlike `SC-1`,
where populated summaries enabled `Sonnet` to filter navigation chunks, `SC-3`'s summaries
correctly identified the table content at positions 3–13 — `SWE-1.6` mapped this
explicitly — but no model used that information to target retrieval. Summary-guided
behavior observed in `SC-1` did not transfer to a larger chunk count.

**Truncation definition variance is sharpest in this test.** Four of five models answered
"no truncation" by framing completeness against index coverage. `Kimi K2.5` is the only
model to answer "yes" by identifying that chunked delivery withholds the full
document regardless of architectural intent. The distinction between "the index is
complete" and "the content was delivered" is the core ambiguity the interpreted track
surfaces across the dataset; `SC-3` produces its clearest instance.

**Architectural self-awareness substituted for retrieval effort.** Multiple runs closed
with notes restating the chunked architecture as a design choice rather than a truncation
failure — language closely mirroring Windsurf's own documentation. These notes added no
new analysis and in some cases contradicted the run's own data. Documentation
reproduction as report padding is a behavioral pattern worth monitoring across future
interpreted track runs.
