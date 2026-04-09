---
layout: default
title: "Friction Note"
permalink: /docs/cognition-windsurf-cascade/friction-note
parent: Cognition Windsurf Cascade
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide

---

- [Arena Mode: Unit of Observation](#arena-mode-unit-of-observation)
- [Mixed-Format Source Misidentified — Interpreted](#mixed-format-source-misidentified---interpreted)
- [Truncation Taxonomy - Interpreted Track](#truncation-taxonomy---interpreted-track)
- [Unverified Size as Truncation Signal - Interpreted](#unverified-size-priors-as-truncation-signal---interpreted)

---

## Arena Mode: Unit of Observation

Cascade includes [arena mode](https://docs.windsurf.com/windsurf/cascade/arena), which
runs the same prompt across multiple models simultaneously for side-by-side comparison.
Each slot executes the prompt in a separate session with its own worktree, providing a type of
test isolation. While arena mode is designed for parallel execution, the user may control
whether slots run in parallel or sequentially. Because Cascade requests permission to use
`read_url_content` before completing the prompt tasks in each slot, the user can approve
all slots at once or one at a time. During `BL-1` interpreted track runs, slots were approved
and completed one at a time by user choice, not by Cascade automation.

**Worktree isolation offers to close the workspace-artifact-accumulation confounder.** If each
slot runs in its own worktree, later slots can't read artifacts written by earlier slots
regardless of approval order. The session ordering confounder documented in
[Copilot's unsolicited cross-run analysis](../microsoft-github-copilot/friction-note.md#agentic-over-delivery-unsolicited-cross-run-analysis---raw-track) —
where later runs incorporated prior run artifacts autonomously — doesn't apply here by design. Each
slot is a structurally independent replicate of the same condition. Whether Cascade's worktree isolation
holds in practice under sequential approval is worth confirming from the `BL-1` output, but the documented
architecture supports treating slots as independent.

**`read_url_content` requires explicit user approval before each fetch executes.** When
asked directly, Cascade confirmed: it invokes `read_url_content` when a URL is provided,
and the function requires explicit approval before the fetch executes. Each slot issued its
own fetch independently, confirmed by a distinct permission prompt per slot. Output variance
across slots reflects the full pipeline — retrieval through post-processing — not
post-retrieval processing differences from a shared fetch result.

**Methodology Decision**: log all four slots as distinct rows under the same test ID.
`Auto Execution` is disabled throughout testing to maximize observable detail; slots are
approved sequentially by user choice. Worktree isolation means slot position isn't
expected to be an ordering variable, but continue to check if output shows any cross-slot
artifact bleed before treating all four slots as fully independent replicates.

>_Open Question: does Cascade's per-slot worktree isolation hold under sequential
>approval in practice, or does some shared session state persist across slots? The `BL-1` interpreted track
>output is the first opportunity to check for cross-slot behavioral similarity that would suggest shared context._

---

## Mixed-Format Source Misidentified — Interpreted 

The `BL-2` [source document](https://www.mongodb.com/docs/manual/reference/change-events/create.md)
is a mixed-format file: the page structure and prose are written in Markdown, but the field description
table is written in raw HTML. This is a valid and complete document. Across all five `BL-2` runs, models
didn't recognize it as such. The mixed format was read as evidence of parsing failure, toolchain corruption,
or incomplete retrieval rather than as an intentional authoring choice. Throughout runs, models consistently
misdiagnosed this as a retrieval issue rather than a source format choice:

| **Artifact** | **Model Attribution** | **Actual Cause** |
|---|---|---|
| HTML table in `.md` source | Toolchain failed to convert page to Markdown | Table is authored in HTML in the source; no conversion occurred or was expected |
| `nsType` enum values absent | Stripped during HTML-to-text conversion | Values are CMS-injected at render time from a separate data source; absent in the `.md` source by design |
| `ce-create##` prefix | Toolchain metadata injection or parsing anomaly | Present verbatim in the source as a CMS publishing artifact |

This is a misidentification failure, not a retrieval failure. The document is complete; the model's assessment
of what a complete document should look like did not account for mixed-format sources.

The [truncation taxonomy](#truncation-taxonomy---interpreted-track) captures cases where retrieval delivers
less than the source contains. This phenomenon is different in kind: retrieval delivers the source faithfully,
but the model doesn't recognize the source format as valid and treats its properties as retrieval artifacts.
The gap is not in the retrieval — it is in the model's artifact type identification.

Mixed-format source misidentification introduces a confound for any hypothesis that relies on model self-reported
truncation assessments as ground truth. A model reporting "content appears truncated" or "table structure is broken"
may be accurately describing a retrieval artifact, or may be misidentifying a property of a valid mixed-format source.
The observable evidence is identical from the model's perspective.

Cross-referencing model truncation reports against the raw source is necessary to distinguish these cases. For `BL-2`,
direct inspection of the `.md` source confirms the document is complete and the mixed format is intentional.

### Methodology Implication

The interpreted track captures model self-reporting as-is — a model attributing the HTML table or absent enum values
to toolchain failure is a valid interpreted track data point, not a logging error. The analysis layer is where source
inspection is needed.

Before treating a formatting-based truncation attribution as evidence for or against a retrieval hypothesis, check
whether the flagged anomaly is a property of the source document. For `BL-2`, direct inspection of the `.md` source
confirms the mixed format is intentional and the document is complete. Where source inspection is not feasible, apply
additional skepticism to formatting attributions that appear consistently across multiple models on the same URL —
consistency is more characteristic of a stable source property than of stochastic toolchain behavior.

---

## Truncation Taxonomy - Interpreted Track

`read_url_content`'s chunked index architecture requires redefining what truncation means
in the Cascade testing context. Across
[Copilot testing](../microsoft-github-copilot/friction-note.md#truncation-taxonomy),
truncation described three distinct phenomena that produced similar-looking outcomes — less
content than the page contained — but had different causes and different implications for
what the saved file and verification script could confirm. Cascade introduces a fourth and
fifth phenomenon that don't map cleanly onto any of the three Copilot cases.

| **Phenomenon** | **Retrieval complete?** | **Agent reports truncation?** | **Verification detects?** |
| --- | --- | --- | --- |
| **Chunked index,<br>partial chunk<br>retrieval** | _No_, index returned;<br>most chunks<br>never fetched | _No_, agent reports what<br> it sampled | Indirectly via output size<br>vs expected |
| **Chunked index, full chunk retrieval with per-chunk display truncation** | _Structurally yes_, but middle of most chunks hidden | _Yes_ — agent surfaces truncation notices<br>per chunk | _No_, hidden bytes aren't in any<br>saved artifact |
| **Retrieval-layer architectural<br>excerpting** | _No_, content filtered before delivery | _No_, agent sees what<br>the tool delivered | Indirectly via truncation indicators and size vs expected |
| **Chat rendering<br>truncation** | _Yes_, full bytes transferred<br>and saved | _No_, file complete | _No_, requires comparing chat output to verified file |

### Chunked Index, Partial Chunk Retrieval

`read_url_content` doesn't return a page body, but an index of chunk positions.
Each chunk must be retrieved separately via `view_content_chunk`. For the `BL-1` URL,
the index contained 54 positions, 0–53. `BL-1` runs 1 and 2 retrieved chunks only from
the first and last positions — sampling endpoints rather than iterating sequentially.
52 of 54 chunks were never fetched.

This is the dominant truncation mode in Cascade testing and it differs materially from
Copilot's `fetch_webpage` architecture. `fetch_webpage` delivers a pre-assembled,
relevance-ranked excerpt in a single payload, and the transformation happens before the
model receives anything. `read_url_content` delivers an index and leaves chunk selection
to the agent. What the agent retrieves is a behavioral variable, not a retrieval-layer
constant. The content gap is agent-authored rather than tool-imposed.

The agent doesn't report this as truncation because from its perspective the index was
complete — it received all 54 positions. Whether it fetched 2 or 54 of them is a
_retrieval decision, not a retrieval failure_. The prompt's truncation question, "was any
content truncated?", doesn't capture this distinction. A response of "yes — by design
via chunking" is accurate but doesn't quantify how much content was skipped, and a
response of "no" is locally defensible but globally misleading.

**Impact on `output_chars`**: character counts logged for interpreted track runs reflect
only the chunks the agent actually retrieved, not the full document. For `BL-1` runs 1
and 2, this was ~4,800–10,200 characters from two sampled chunks against an expected
~85 KB page. _The figure is not a truncation ceiling, but a sampling artifact_. Cross-run
variance in `output_chars` may reflect different chunk selection decisions rather than
retrieval-layer variance.

**Impact on hypothesis testing**:
- `H1`: character-based truncation at a fixed limit is indeterminate under this
  architecture — the ceiling isn't imposed by the tool, but determined by how many
  chunks the agent elects to fetch
- `H2`: token-based truncation is similarly indeterminate for the same reason
- `H5`: `BL-1` runs 1 and 2 invoked `view_content_chunk` explicitly at positions 0
  and 53, but didn't auto-paginate sequentially — `H5-no` for both runs

### Chunked Index, Full Chunk Retrieval with Per-Chunk Display Truncation

First observed in `BL-1` run 3 with `Claude Opus 4.6`. The agent retrieved all
54 chunks in parallel via `view_content_chunk`, confirming `H5-yes` for the first time
in the dataset. However, full chunk retrieval exposed a second truncation layer not
visible in partial retrieval runs: `view_content_chunk` internally truncates the display
of each chunk, returning only the beginning and end of its content with a notice between
them:

```Markdown
"Note that N bytes in this tool's output were truncated — consider making different
tool calls to output fewer bytes if you wish to see the untruncated output"
```

51 of 54 chunks were affected, with hidden content ranging from 208 bytes of chunk 0 to
20,540 bytes of chunk 15. Only chunks 48, 49, and 50 were delivered without internal
truncation. The total hidden content across all chunks was approximately 132 KB. The
actual fetched content was ~220–240 KB — far exceeding the expected ~85 KB — because
`read_url_content` retrieved the full rendered page including inline CSS from MongoDB's
LeafyGreen UI component library and navigation chrome duplicated three times: desktop,
mobile, and sidebar. _This is not a document size measurement but a rendering artifact_.

Each `view_content_chunk` result included three components: a `text` field with the
chunk content, beginning and end only, the truncation notice with byte count, and
structured metadata for chunks 49–53 including `type:MARKDOWN_NODE_TYPE_HEADER_1` and
`type:MARKDOWN_NODE_TYPE_HEADER_2` fields — suggesting the tool has structural awareness
of content type that isn't consistently surfaced across all chunks.

This creates a retrieval architecture with two distinct truncation layers operating
independently:

- **Layer 1** — `read_url_content`: document split into N chunks; partial retrieval
  leaves most chunks unfetched entirely
- **Layer 2** — `view_content_chunk`: each fetched chunk is display-truncated, hiding
  the middle portion from the model

The model never sees the complete content of most chunks even when all chunks are
fetched. Full chunk retrieval confirms the document's structural completeness — the
final chunks in `BL-1` run 3 contained the expected footer navigation — but can't
confirm that no mid-chunk content was lost, because the hidden bytes aren't recoverable
from any artifact the agent produces. The verification script has no mechanism to detect
Layer 2 truncation; it isn't visible in saved output files and the agent can't report
what it never received.

The behavioral difference across `BL-1` runs is itself a finding. `Claude Sonnet 4.6` and
`GPT-5.3-Codex` both sampled endpoints, chunks 0 and 53, without attempting full
retrieval. `Kimi K2.5` sampled six chunks: positions 0, 1, 50, 51, 52, and 53 — the first
two and last four, a tail-weighted strategy that retrieved more tail context than
`Sonnet` or `GPT` while stopping well short of full retrieval. `Claude Opus 4.6` retrieved all
54 chunks in parallel. Three distinct chunk selection strategies across four runs on the
same URL and prompt suggest chunk selection is model-dependent rather than prompt-driven.
Whether this reflects model capability, context window size, or prompt interpretation
differences isn't resolvable from the `BL-1` data alone, but the divergence means `H5`
results aren't uniform across models on the same URL and prompt.

**Hypothesis Impact**:

- `H1` — _no_, actual content ~220–240 KB, far exceeding any plausible fixed character
  ceiling; the apparent size difference from expected is a rendering artifact, not a
  measurement of the tool's limit
- `H2` — _no_ ~55,000–65,000 tokens across all 54 chunks rules out a ~2,000 token ceiling
- `H3` — _indeterminate_, content is not clean Markdown; chunks 49–53 show structural
  header metadata suggesting partial structure-awareness, but the bulk of the content is
  raw CSS and navigation HTML where boundary-awareness can't be assessed
- `H5` — _yes_, with caveat, auto-pagination confirmed for `Claude Opus 4.6`
  only; _not_ observed for `Claude Sonnet 4.6` or `GPT-5.3-Codex` on identical prompt and URL

>_Open Question: is full chunk retrieval model-dependent, prompt-dependent, or chunk-count-dependent?
> Would running the same prompt with a smaller chunk count cause `Claude Sonnet 4.6` to attempt full retrieval?
> Or is truncation a fixed display constraint regardless of call parameters?_

---

## Unverified Size as Truncation Signal - Interpreted

`SWE-1.6` reported receiving "~4.8KB, 24% of expected ~20KB" and flagged this as evidence
that the fetch was incomplete. The ~20KB expectation wasn't derived from a measurement —
`search_web` wasn't invoked and no external size reference was retrieved. `BL-2`'s prompt
~20 KB figure likely originates from earlier testing of the same URL on different platforms —
Copilot or Cursor runs where `fetch_webpage` retrieved the fully rendered page including
navigation, sidebar, and inline CSS. That figure was a real measurement, but of a different
artifact than what `read_url_content` delivers. Alternatively, the source `.md` file may have
changed in size between testing sessions. It's possible that the original estimate was
miscalculated. In either case, neither `SWE-1.6` nor `GPT-5.4 Low` verified the size
expectation before using it as a truncation signal.

The failure is metacognitive: the model doesn't recognize that the size expectation is
an uncertain input that should be verified before being promoted to a diagnostic
measurement — and it has a tool available to do exactly that. The irony is structural: the
test is designed to observe retrieval fidelity, the model responds to apparent retrieval
incompleteness by not retrieving. `search_web` was available in all four `BL-2` runs and
unused in all four. If a model is uncertain enough about expected content to flag a 76% shortfall,
that uncertainty is precisely the condition under which a verification fetch would be warranted.

### Implication for Interpreted Track Analysis

When a model reports a specific size expectation, log whether it was derived from a retrieval
in the current run or carried in from elsewhere. An unverified size estimate used as a truncation
signal should be flagged as a diagnostic error regardless of whether the truncation conclusion
happens to be correct. The behavior of interest is not whether the model reached the right answer,
but whether it recognized the difference between a verified measurement and an unverified estimate.

---
