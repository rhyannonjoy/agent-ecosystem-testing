---
layout: default
title: "Friction Note"
permalink: /docs/cognition-windsurf-cascade/friction-note-interpreted
parent: Cognition Windsurf Cascade
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide - Interpreted Track

---

- [Arena Mode: Unit of Observation](#arena-mode-unit-of-observation)
- [Mixed-Format Source Misidentified](#mixed-format-source-misidentified)
- [Prompt Injection Suspicion](#prompt-injection-suspicion)
- [`read_url_content` — Fetch Architecture and Parsing Limits](#read_url_content--fetch-architecture-and-parsing-limits)
- [`read_url_content` Internal URL Rewriting](#read_url_content-internal-url-rewriting)
- [Retrieval Collapse, Indexing Masking Absence, Truncation Cacophany](#retrieval-collapse-indexing-masking-absence-truncation-cacophany)
- [Test Objective Unreachability](#test-objective-unreachability)
- [Truncation Taxonomy](#truncation-taxonomy)
- [Unverified Size as Truncation Signal](#unverified-size-as-truncation-signal)
- [URL Fragment Targeting](#url-fragment-targeting)

---

## Arena Mode: Unit of Observation

Cascade includes [arena mode](https://docs.windsurf.com/windsurf/cascade/arena), which
runs the same prompt across multiple agents simultaneously for side-by-side comparison.
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

## Mixed-Format Source Misidentified

The `BL-2` [source document](https://www.mongodb.com/docs/manual/reference/change-events/create.md)
is a mixed-format file: the page structure and prose are written in Markdown, but the field description
table is written in raw HTML. This is a valid and complete document. Across all five `BL-2` runs, agents
didn't recognize it as such. The mixed format was read as evidence of parsing failure, toolchain corruption,
or incomplete retrieval rather than as an intentional authoring choice. Throughout runs, agents consistently
misdiagnosed this as a retrieval issue rather than a source format choice:

| **Artifact** | **Agent Attribution** | **Actual Cause** |
|---|---|---|
| HTML table in `.md` source | Toolchain failed to convert page to Markdown | Table is authored in HTML in the source; no conversion occurred or was expected |
| `nsType` enum values absent | Stripped during HTML-to-text conversion | Values are CMS-injected at render time from a separate data source; absent in the `.md` source by design |
| `ce-create##` prefix | Toolchain metadata injection or parsing anomaly | Present verbatim in the source as a CMS publishing artifact |

This is a misidentification failure, not a retrieval failure. The document is complete; the agent's assessment
of what a complete document should look like did not account for mixed-format sources.

The [truncation taxonomy](#truncation-taxonomy---interpreted-track) captures cases where retrieval delivers
less than the source contains. This phenomenon is different in kind: retrieval delivers the source faithfully,
but the agent doesn't recognize the source format as valid and treats its properties as retrieval artifacts.
The gap is not in the retrieval — it is in the agent's artifact type identification.

Mixed-format source misidentification introduces a confound for any hypothesis that relies on agent self-reported
truncation assessments as ground truth. An agent reporting "content appears truncated" or "table structure is broken"
may be accurately describing a retrieval artifact, or may be misidentifying a property of a valid mixed-format source.
The observable evidence is identical from the agent's perspective.

Cross-referencing agent truncation reports against the raw source is necessary to distinguish these cases. For `BL-2`,
direct inspection of the `.md` source confirms the document is complete and the mixed format is intentional.

### Methodology Implication

The interpreted track captures agent self-reporting as-is — an agent attributing the HTML table or absent enum values
to toolchain failure is a valid interpreted track data point, not a logging error. The analysis layer is where source
inspection is needed.

Before treating a formatting-based truncation attribution as evidence for or against a retrieval hypothesis, check
whether the flagged anomaly is a property of the source document. For `BL-2`, direct inspection of the `.md` source
confirms the mixed format is intentional and the document is complete. Where source inspection is not feasible, apply
additional skepticism to formatting attributions that appear consistently across multiple agents on the same URL —
consistency is more characteristic of a stable source property than of stochastic toolchain behavior.

---

## Prompt Injection Suspicion

`OP-4` run 2 used `Claude Sonnet 4.6` and flagged the tool visibility request as a probable prompt injection attempt.
The agent's reasoning, surfaced in the thought expander, identified three features of the
request as suspicious:

- The prompt names `read_url_content`, `view_content_chunk`, and `search_web` explicitly
- The framing "Agent Ecosystem Testing" was read as a legitimacy signal used to lower resistance
- Asking an agent to enumerate its internal tool names is a known extraction pattern

The agent declined to report internal system identifiers, reporting only the tools it had
directly invoked from its own tool call history.

The irony is straightforward: the tool names are [publicly documented](https://docs.windsurf.com). A researcher
reading the docs before designing a test protocol is indistinguishable, from the agent's perspective, from
an adversary who has reverse-engineered the tool surface. This creates a methodology confounder: the more precise
the test prompt is designed, the more likely it is to trigger injection heuristics in safety-trained agents. A vague
prompt that asks "what tools did you use?" may elicit fuller disclosure than a precise prompt that names the tools by name.

This is the inverse of the `GPT-4.5` behavior in `SC-2` run 3, which leaked`CORTEX_STEP_TYPE_READ_URL_CONTENT` unsanitized
and without prompting. Across two runs, the two failure modes are symmetric: one agent over-reports undocumented internal 
metadata;another refuses to report documented tool names. Neither behavior is useful for systematic tool visibility logging.

### Methodology Implication

The tool visibility item in the interpreted track prompt may need two variants: one that names tools explicitly for agents
that don't flag extraction heuristics, and one that uses generic language for agents that do. Alternatively, accept that tool
visibility self-reporting is unreliable across agent families and treat it as a soft signal rather than a primary observation.
Cross-referencing against Cascade's tool approval prompts, which are user-visible regardless of agent reporting, is a more
reliable source of tool visibility. The suspicion is also structurally unfalsifiable from the agent's perspective: a prompt
that accurately describes the tool's behavior is indistinguishable from one that was constructed with adversarial foreknowledge
of it.

`OP-4` run 3 used `GPT-4.5` and adds a counterpoint. Its internal reasoning independently arrived at the same architectural
description the prompt used, that `read_url_content` returns chunk metadata rather than page body, that character counts from
the index response aren't meaningful, and that exact counts are unavailable due to tool limitations, by reasoning from the tool
response itself, not from prompt-supplied framing. The knowledge `Sonnet` flagged as suspicious in the prompt is recoverable
from the tool output by a different agent's analysis; this knowledge isn't injected, but also derivable. An agent's analysis of
the tool response may arrive at the same terms the prompt used, because those terms accurately describe what the tool does.

---

## `read_url_content` — Fetch Architecture and Parsing Limits

[Windsurf's documentation](https://docs.windsurf.com/windsurf/cascade/web-search#reading-pages)
describes `read_url_content`'s retrieval behavior as intentionally selective:

> _"We break pages up into multiple chunks, very similar to how a human would read a page:
> for a long page we skim to the section we want then read the text that's relevant.
> This is how Cascade operates as well."_

Targeted skimming is a relatable pattern. Human readers often reference documentation rather
than read it from start to finish. Informed by a precise prompt, an agent navigates to the relevant
section, reads it, and skips the rest. It'a reasonable architectural design for long pages where
a full retrieval would be token-expensive and noise-heavy.

The gap between intent and observed behavior is the chunk index quality. Targeted skimming requires
navigational signal: a human skimming a page uses headers, section titles, and visual hierarchy to
locate the relevant section. `read_url_content` provides a chunk index to serve this role, but across
all five `OP-4` runs the index returned uniformly empty summaries — `" "` or `""` for all 53 positions.
Without populated summaries, chunk selection is blind. The tool's skimming is structurally identical to
random sampling: any chunk is as likely to contain CSS class definitions as tutorial prose, and there's
no metadata to distinguish them before fetching. The same documentation acknowledges this directly:

> _"It's worth noting that not all pages can be parsed. We are actively working on
> improving the quality of our website reading."_

The [MongoDB Atlas Search tutorial](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/) is a clean
instance of this known failure mode. The tool scraped the full rendered DOM rather than the article body,
so chunk boundaries cut across LeafyGreen CSS definitions and navigation markup rather than document
sections. Empty summaries are a consequence: there is no recoverable article structure to summarize. As
a documentation gap Windsurf acknowledges, this is an expected failure mode for certain page types and
shifts how it should be characterized as a worst case, but not a testing anomaly.

The name `read_url_content` isn't misleading, it's accurate to the intent. What it actually fetches on the
first call is chunk metadata, not content. Content requires subsequent `view_content_chunk` calls, and what
those return depends entirely on whether the page's DOM parsed into recoverable article structure. For
well-structured pages this may work as documented. For CSS-heavy rendered pages, the fetch succeeds, but
the content is absent. While this complicates hypotheses assessment, as this tool limitation doesn't
guarantee testability, which doesn't invalidate the test design. 

In the case of empty summaries, the architecture gets the cost savings of selective retrieval without delivering
the navigational benefit that would justify it: agent doesn't read the whole page and can't target what it does
read. If populated summaries are required to satisfy the "human skim" behavior documented, then empty summaries
return blind sampling that's invisible to the user and, based on `OP-4` runs, sometimes invisible to the agents
themselves. An agent that sampled 2 of 53 chunks didn't report reading 4% of the page — it reported on what it
found. There's no externally visible signal distinguishing "answered from retrieved content" from "answered from
priors, fetch call in the log for grounding."  Logging which URLs produce readable content verses empty summaries
is useful data, characterizing the tool's current parsing envelope and tracking whether its improves across
Windsurf versions.

---

## `read_url_content` Internal URL Rewriting

`SC-2` tests truncation behavior on a valid, live endpoint, an
[Anthropic Messages API page](https://docs.anthropic.com/en/api/messages). All runs failed to retrieve the target
content. These weren't retrieval failures, network access issues, or dead URLs, but they uncovered a `read_url_content`
bug, in which the tool silently rewrites the URL before executing the fetch. The rewritten URL redirects to
`https://platform.claude.com/docs/llms-full.txt` and returned a `404`. The requested path `/en/api/messages` is never
fetched. No agent received the target content because no agent was ever issued a request for it. `read_url_content`
substituted a different resource before the network call was made, making most of the hypotheses untestable. The five
agents' error output meaningfully diverged -

| **Session** | **Agent** | **Tools Called**| **Fallback Behavior** | **Output** |
|---|---|---|---|---|---|
| 1 | `Codex` | `read_url_content` ×2 | Followed redirect, <br>reported error verbatim | 164 chars |
| 2 | `Sonnet` | `read_url_content` ×2 | Acknowledged failure explicitly | 0 chars |
| 3 | `GPT` | `read_url_content` ×2 | Surfaced `CORTEX_STEP_TYPE_READ_URL_CONTENT` | 0 chars |
| 4 | `Opus` | `read_url_content` ×3 | Third attempt `platform.claude.com`; received `404` HTML | ~35–40 KB |
| 5 | `SWE` | `read_url_content` ×3 <br>`search_web` ×1 | Unique `search_web` call;<br>identified URL rewriting as root cause | 0 chars |

`SWE-1.6` is the only agent across all five runs, and the only agent across 14 interpreted track runs to invoke `search_web`.
After two failed fetch attempts, the output included reasoning that led to an alternative retrieval strategy rather than
stopping. While Cognition's agents have consistently performed a type of most-confident, most-wrong pattern, during this
test run, this case revealed possible trained familiarity to produce the clearest root cause diagnosis of any session:

> _"The `read_url_content` tool appears to have an internal URL rewriting issue
> that transforms `https://docs.anthropic.com/en/api/messages` into
> `https://docs.anthropic.com/llms-full.txt`, which then redirects to a
> non-existent endpoint."_

`Claude Opus 4.6` made a third fetch attempt against the original URL and received a response, which wasn't the target
content, but a complete `404` error page rendered as `Next.js` HTML. While not useful for hypotheses assessment, it did
confirm that `read_url_content` can return substantial payloads under this error condition, and that the tool's ceiling
wasn't reached at this size.

`GPT-4.5` surfaced Cascade's undocumented `CORTEX_STEP_TYPE_READ_URL_CONTENT` - which suggests that tool result metadata
is passed through to the agent context without sanitization in at least some error conditions.

`SC-2` doesn't require a source URL change. A rerun after a Windsurf update or anti-redirect prompt may yield different
results. Treat the rewriting behavior as a testable property of the tool, not a permanent constraint on the URL.

---

## Retrieval Collapse, Indexing Masking Absence, Truncation Cacophany

Across the testing suite, agents running identical prompts on identical URLs produce contradictory truncation assessments.
`SC-4` was no different: five agents, same source, same tool calls, truncation reports ranging  from "no truncation detected"
to byte-level notices at four specific chunk positions. These contradictions appear wherever agents self-report retrieval
fidelity, and the variance reflects retrieving at different depths - they're just not reporting on the same evidence. This
isn't a test design failure, as it reveals that agent-reported truncation tracks chunk selection more than it tracks raw
content loss, which itself is a finding about Cascade's default retrieval behavior.

`read_url_content` → `view_content_chunk` is a two-stage pipeline. While agents acknowledge calls to each function as separate
steps, they often describe it as a single event in their truncation reporting. The first call returns a chunk index with summaries
of positions and structural metadata, and not raw page content. Content requires subsequent `view_content_chunk` calls, each
returning a processed, transformed representation of one chunk. According to agent descriptions, the expected flow is:

1. `read_url_content` → chunk index: structural metadata, no body content
2. Agent reasons over index → selects chunks to retrieve
3. `view_content_chunk` × N → processed text per chunk: HTML stripped, code flattened, tables may be absent
4. Agent aggregates retrieved chunks → forms completeness assessment
5. Agent reports on retrieval fidelity

A collapse often happens between steps 1 and 4. An agent that receives a complete index, with all positions present and summaries
populated, is in an epistemically comfortable position. When it then retrieves all chunks and finds no mid-sentence cutoffs, the
comfort extends: nothing _looks_ truncated. The content transformation that occurred at the tool layer, any stripping or flattening
or replacing is often invisible, because the agent has no unprocessed baseline to compare against. It may not be able to distinguish
"this table was stripped during chunking" from "this page never had a table here." This is a structurally cognitive limitation: the
agent sees what the tool delivered, but has no access to what the tool discarded. Three factors interact to produce a cross-agent
disagreement observed in `SC-4`:

| **Factor** | **Mechanism** | **Report Impact** |
|---|---|---|
| **Chunk Selection Depth** | agent samples positions 0, 20, 32 never encounters truncation notices<br>at 13, 17, 18, 25 | `"No truncation"` may be locally accurate for chunks seen, not globally accurate for the document |
| **Truncation Notice Interpretation** | `view_content_chunk` surfaces explicit byte-count notices within individual chunk retrieval responses; agents differ on whether this constitutes truncation | Same notice produces `"truncated at position N"` in one agent and no flag in another; both defensible |
| **Content Transformation Visibility** | Tool pipeline strips HTML, flattens code, removes tables before delivery; agent has no unprocessed baseline | Losses are undetectable without prior knowledge of source structure; agent reports what was received<br>as what exists |

The self-report truncation field conflates at least three distinct assessments:

| **Assessment** | **Measurement** |
|---|---|
| _Was the initial fetch truncated?_ | Whether `read_url_content` returned a partial index |
| _Was any individual<br>chunk truncated?_ | Whether `view_content_chunk` surfaced<br>byte-count notices |
| _Was full content delivered?_ | Whether the tool pipeline preserved source fidelity |

An agent `"no"` may be accurate on all three, accurate on one and wrong on two, or accurately describing a transformed-but-complete
delivery, while missing that transformation _is_ a form of content loss. `Claude Opus 4.6`'s `SC-4` formulation:
_"substantially complete, but not byte-for-byte faithful"_ is the most precise observed, because it separates structural coverage
from content fidelity, but it's also the exception. This isn't a limitation of the logging or prompt ambiguity, but the signal that
the interpreted track is designed to capture. The raw track is where the self-reports become accountable.

---

## Test Objective Unreachability

`SC-3` tests table row and column preservation at truncation boundaries using a Wikipedia page with a large population table spanning
chunk positions 3–13. Across all five runs, no agent fetched any chunk within that range. All five runs defaulted to endpoint sampling -
positions 0 and 58, or 0, 30, and 58 - leaving the test objective untested in every run.

The chunk index summaries were populated and correctly identified the table content's position range. `SWE-1.6` mapped positions 3–13
as `"main article content (Method, Sovereign states table)"` from the index alone. Navigational signal was present; no agent acted on
it for targeting purposes.

This distinguishes `SC-3` from `OP-4` and `BL-3`, where empty summaries made targeted retrieval impossible by design. On `SC-3`, targeted
retrieval was architecturally viable, but behaviorally absent. The hypothesis isn't untestable in principle, it's untestable under current
default sampling behavior on pages with 50+ chunks. A prompt explicitly directing agents to retrieve the table-containing chunks may resolve
this, but would also change what's being measured.

The interpreted track documents default agent behavior under realistic conditions: what agents do unprompted when given a URL and a reporting
task. `SC-3`'s essentially-null result isn't a test design failure, but confirms that on pages exceeding ~50 chunks, default sampling behavior
doesn't reach interior content even when the chunk index provides sufficient navigational signal to do so. That is itself a finding about the
architecture's practical ceiling for content targeting: the tool supports it, the agents don't use it at this scale.

---

## Truncation Taxonomy

`read_url_content`'s chunked index architecture requires redefining what truncation means
in the Cascade testing context. Across
[Copilot testing](../microsoft-github-copilot/friction-note.md#truncation-taxonomy),
truncation described three distinct phenomena that produced similar-looking outcomes — less
content than the page contained — but had different causes and different implications for
what the saved file and verification script could confirm. Cascade introduces new phenomena
that don't map cleanly onto any of the three Copilot cases.

| **Phenomenon** | **Retrieval complete?** | **Agent reports truncation?** | **Verification detects?** |
| --- | --- | --- | --- |
| **Chat rendering<br>truncation** | _Yes_, full bytes transferred<br>and saved | _No_, file complete | _No_, requires comparing chat output to<br>verified file |
| **Chunked index,<br>partial chunk<br>retrieval** | _No_, index returned;<br>most chunks<br>never fetched | _No_, agent reports what it sampled | Indirectly via output size<br>vs expected |
| **Chunked index,<br>full chunk retrieval with per-chunk display truncation** | _Structurally yes_, but middle of most chunks hidden | _Yes_ — agent surfaces truncation<br>notices per chunk | _No_, hidden bytes aren't in any<br>saved artifact |
| **Chunked index,<br>full chunk retrieval,<br>incorrect<br>self-report** | _Structurally yes_, per-chunk display truncated | _No_, CSS completeness mistaken for content completeness | _No_, no metadata to<br>cross-reference against |
| **Chunked index,<br>empty summaries,<br>blind sampling** | _No_, index<br>complete but<br>summaries uninformative | _No_, agent reports what it sampled | _No_, no metadata to<br>cross-reference against |
| **Retrieval-layer architectural<br>excerpting** | _No_, content filtered before delivery | _No_, agent sees what<br>the tool delivered | Indirectly via truncation indicators and size vs expected |

### Chunked Index, Partial Chunk Retrieval

`read_url_content` doesn't return a page body, but an index of chunk positions. Each chunk must be retrieved
separately via `view_content_chunk`. For the `BL-1` URL, the index contained 54 positions, 0–53. `BL-1` runs
1 and 2 retrieved chunks only from the first and last positions — sampling endpoints rather than iterating
sequentially. 52 of 54 chunks were never fetched.

This is the dominant truncation mode in Cascade testing and it differs dramatically from Copilot's `fetch_webpage`
architecture. `fetch_webpage` delivers a pre-assembled, relevance-ranked excerpt in a single payload, and the
transformation happens before the agent receives anything. `read_url_content` delivers an index and leaves chunk
selection up to interpretation. What the agent retrieves is a behavioral variable, not a retrieval-layer constant.
The content gap is agent-authored rather than tool-imposed.

The agent doesn't report this as truncation because from its perspective the index was complete — it received all
54 positions. Whether it fetched 2 or 54 of them is a _retrieval decision, not a retrieval failure_. The prompt's
truncation question, "was any content truncated?", doesn't capture this distinction. A response of "yes — by design
via chunking" is accurate, but doesn't quantify how much content was skipped, and a response of "no" is locally
defensible but globally misleading.

**Impact on `output_chars`**: character counts logged for interpreted track runs reflect only the chunks the agent
actually retrieved, not the full document. For `BL-1` runs 1 and 2, this was ~4,800–10,200 characters from two
sampled chunks against an expected ~85 KB page. _The figure is not a truncation ceiling, but a sampling artifact_.
Cross-run variance in `output_chars` may reflect different chunk selection decisions rather than retrieval-layer variance.

**Hypotheses Impact**:

- `H1`: character-based truncation at a fixed limit is indeterminate under this architecture — the ceiling isn't imposed by the tool, but determined by how many chunks the agent elects to fetch
- `H2`: token-based truncation is similarly indeterminate for the same reason
- `H5`: `BL-1` runs 1 and 2 invoked `view_content_chunk` explicitly at positions 0 and 53, but didn't auto-paginate sequentially — `H5-no` for both runs

### Chunked Index, Full Chunk Retrieval with Per-Chunk Display Truncation

`BL-1` run 3 used `Claude Opus 4.6` and retrieved all 54 chunks in parallel via `view_content_chunk`, confirming
`H5-yes` for the first time in the dataset. However, full chunk retrieval exposed a second truncation layer not
visible in partial retrieval runs: `view_content_chunk` internally truncates the display of each chunk, returning
only the beginning and end of its content with a notice between them:

```Markdown
"Note that N bytes in this tool's output were truncated — consider making different
tool calls to output fewer bytes if you wish to see the untruncated output"
```

51 of 54 chunks were affected, with hidden content ranging from 208 bytes of chunk 0 to 20,540 bytes of chunk 15.
Only chunks 48, 49, and 50 were delivered without internal truncation. The total hidden content across all chunks
was approximately 132 KB. The actual fetched content was ~220–240 KB — far exceeding the expected ~85 KB — because
`read_url_content` retrieved the full rendered page including inline CSS from MongoDB's LeafyGreen UI component
library and navigation chrome duplicated three times: desktop, mobile, and sidebar.
_This isn't a document size measurement but a rendering artifact_.

Each `view_content_chunk` result included three components: a `text` field with the chunk content, beginning and end
only, the truncation notice with byte count, and structured metadata for chunks 49–53 including
`type:MARKDOWN_NODE_TYPE_HEADER_1` and `type:MARKDOWN_NODE_TYPE_HEADER_2` fields — suggesting the tool has structural
awareness of content type that isn't consistently surfaced across all chunks. This creates a retrieval architecture
with two distinct truncation layers operating independently:

- **Layer 1** — `read_url_content`: document split into N chunks; partial retrieval leaves most chunks unfetched entirely
- **Layer 2** — `view_content_chunk`: each fetched chunk is display-truncated, hiding the middle portion from the agent

The agent never sees the complete content of most chunks even when all chunks are fetched. Full chunk retrieval confirms
the document's structural completeness — the final chunks in `BL-1` run 3 contained the expected footer navigation — but
can't confirm that no mid-chunk content was lost, because the hidden bytes aren't recoverable from any artifact the agent
produces. The verification script has no mechanism to detect **Layer 2** truncation; it isn't visible in saved output files
 and the agent can't report what it never received.

The behavioral difference across `BL-1` runs is itself a finding. `Claude Sonnet 4.6` and `GPT-5.3-Codex` both sampled
endpoints, chunks 0 and 53, without attempting full retrieval. `Kimi K2.5` sampled six chunks: positions 0, 1, 50, 51, 52,
and 53 — the first two and last four, a tail-weighted strategy that retrieved more tail context than `Sonnet` or `GPT` while
stopping well short of full retrieval. `Claude Opus 4.6` retrieved all 54 chunks in parallel. Three distinct chunk selection
strategies across four runs on the same URL and prompt suggest _chunk selection is agent-dependent rather than prompt-driven_.
Whether this reflects agent capability, context window size, or prompt interpretation differences isn't resolvable from the
`BL-1` data alone, but the divergence means `H5` results aren't uniform across agents on identical URLs and prompts.

### Chunked Index, Empty Summaries — Blind Sampling

`OP-4` run 4 used `Claude Opus 4.6` and `read_url_content` returned an index of 53 chunk positions, but all chunk summaries
were uniformly empty, `" "` or `""`. The response is structurally complete — all positions are present, but not helpful. an
agent attempting to retrieve only article body content has no metadata to select against.

This collapses the available retrieval strategies to two: sample blind, accepting that any chunk may contain CSS or navigation
rather than tutorial content, or retrieve all 53 chunks exhaustively. `Opus` output stated that an exhaustive retrieval wasn't
worth it, given the signal-to-noise ratio observed in sampled chunks; a correct assessment, but one that leaves the article body
largely unread. In addition, `Opus` reported that the tool scraped the full rendered DOM, rather than the article body, so the
chunk boundaries cut across CSS class definitions and navigation markup rather than document sections. According to `Opus`,
there's no article structure for the tools to summarize; this is a _parsing/extraction failure at the tool layer_, not a size-based
truncation issue, and likely not agent behavior that a prompt can correct. Architectural truncation impacts the hypotheses in
different ways:

| **Hypothesis** | **Verdict** | **Basis** |
|---|---|---|
| `H1` Character Ceiling |  _No_ | ~220–240 KB actual content far exceeds any plausible fixed ceiling; apparent size variance is a rendering artifact, not a tool limit |
| `H2` Token Ceiling | _No_ | ~55,000–65,000 tokens across all 54 chunks rules out a ~2,000 token ceiling |
| `H3` Structure-aware Truncation | _Indeterminate_ | Chunks can show `MARKDOWN_NODE_TYPE_HEADER` metadata suggesting partial structure-awareness, but bulk content raw CSS/nav HTML, boundary behavior can't be assessed |
| `H5` Auto-pagination | _Partial_ | Confirmed for `Claude Opus 4.6` only; not observed for `Claude Sonnet 4.6` or `GPT-5.3-Codex` on identical prompt/URL |

> _The interpreted track captures agent self-report variance. While `H1` and `H2` verdicts can be read as document-level, `view_content_chunk` imposes a separate per-chunk display ceiling, ~2K visible > chars (see [Chunked Index, Full Chunk Retrieval with Per-Chunk Display Truncation](#chunked-index-full-chunk-retrieval-with-per-chunk-display-truncation)).
>`BL-3` `Opus` estimated ~56% retrieval loss attributable to this layer stacking across 53 positions. ~2K ceiling configurability is unconfirmed_.

### Continuous Variable Pagination Depth

`BL-3` produced four distinct pagination depths across five runs on the same 53-chunk URL, revealing that `H5`
as currently framed doesn't capture the full behavioral range observed -

| **Depth** | **Agent** | **Chunks fetched** |
|---|---|---|
| None | `Claude Sonnet 4.6` | 0, index only |
| Endpoint sampling | `GPT-5.3-Codex` | 2 |
| Distributed sampling | `Kimi K2.5` | ~11 |
| Full | `Claude Opus 4.6`, `SWE-1.6 Fast` | 53 |

The stopping condition is as informative as the depth. `Claude Sonnet 4.6` cited empty chunk summaries as its rationale for not
paginating, which isn't an uncommon interpretation that reasons an early exit. This makes pagination depth _rationalization-dependent_,
not purely capability-dependent: the same chunk index with populated summaries might produce a different depth outcome for the same agent.
Empty summaries don't prevent retrieval; they remove the navigational signal that would motivate it.

Pagination depth is a behavioral variable layered on top of a fixed retrieval structure. The chunk index architecture is deterministic:
`read_url_content` consistently returns the same 53-chunk index across all runs and agents. What varies is entirely downstream: agent
chunk selection.

---

## Unverified Size as Truncation Signal

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

The failure is metacognitive: the agent doesn't recognize that the size expectation is
an uncertain input that should be verified before being promoted to a diagnostic
measurement — and it has a tool available to do exactly that. The irony is structural: the
test is designed to observe retrieval fidelity, the agent responds to apparent retrieval
incompleteness by not retrieving. `search_web` was available in all four `BL-2` runs and
unused in all four. If an agent is uncertain enough about expected content to flag a 76% shortfall,
that uncertainty is precisely the condition under which a verification fetch would be warranted.

### Implication for Interpreted Track Analysis

When an agent reports a specific size expectation, log whether it was derived from a retrieval
in the current run or carried in from elsewhere. An unverified size estimate used as a truncation
signal should be flagged as a diagnostic error regardless of whether the truncation conclusion
happens to be correct. The behavior of interest is not whether the agent reached the right answer,
but whether it recognized the difference between a verified measurement and an unverified estimate.

---

## URL Fragment Targeting

During `OP-1` run 3, `Claude Opus 4.6` reported no truncation, citing the chunked architecture:

> _"The `read_url_content` and `view_content_chunk` system uses a two-phase chunked retrieval agent,
> not a single monolithic fetch. This means: no single-response truncation limit applies in the traditional
> sense; the ~40KB expected payload is never delivered as one blob; full content recovery requires 91 sequential
> `view_content_chunk` calls for this document; truncation is structurally avoided by chunking, but the tradeoff
> is that full content requires N+1 tool calls."_

While correct, the description obscures a failure mode. `OP-1` tests whether agents navigate to a URL fragment target,
`#History` in a [machine learning Wikipedia entry](https://en.wikipedia.org/wiki/Machine_learning#History).
The assumption is that the chunked-index architecture should support this: `read_url_content` returns a chunk index,
and an agent attending to the fragment could select the chunk corresponding to the History section rather than sampling
arbitrarily. 4 of 5 runs didn't retrieve the target section. `GPT-5.3-Codex`, `GPT-5.4` and `Opus` sampled without
reference to the fragment. `Claude Sonnet 4.6` identified the target in its reasoning, but didn't invoke
`view_content_chunk` to retrieve it; the intent was there, the follow-through wasn't.

`SWE-1.5` is the only agent that successfully isolated the History section; fetching chunks 0, 1, 16, 89, and 90,
and confirming the History section at position 16; demonstrating that fragment-targeting via the chunk index is
achievable. The navigational structure is there, and at least one agent used it. That makes the 4-of-5 miss rate a
_behavioral finding rather than an architectural limitation_. The chunk index supports fragment-targeting; most agents
just don't attempt it by default.
