---
layout: default
title: "Friction Note"
permalink: /docs/cognition-windsurf-cascade/friction-note-interpreted
parent: Cognition Windsurf Cascade
---

# Friction Note: Roadblocks While Refining Methodology

---

## Arena Mode: Unit of Observation

Cascade includes [arena mode](https://docs.windsurf.com/windsurf/cascade/arena), which
runs the same prompt across multiple agents simultaneously for side-by-side comparison.
Each slot executes the prompt in a separate session with its own worktree, providing a type of
test isolation. While arena mode is designed for parallel execution, the user may control
whether slots run in parallel or sequentially. Because Cascade requests permission to use
`read_url_content` before completing the prompt tasks in each slot, the user can approve
all slots at once or one at a time. During `BL-1` interpreted track runs, slots approved
and completed one at a time by user choice, not by Cascade automation.

_Worktree isolation offers to close the workspace-artifact-accumulation confounder_. If each
slot runs in its own worktree, later slots can't read artifacts written by earlier slots
regardless of approval order. The session ordering confounder documented in
[Copilot's unsolicited cross-run analysis](../microsoft-github-copilot/friction-note.md#agentic-over-delivery-unsolicited-cross-run-analysis---raw-track) -
where later runs incorporated prior run artifacts autonomously - doesn't apply here by design.
Testing results suggest that Cascade's per-slot worktree isolation does hold under sequential
approval in practice, as later slots didn't appear to incorporate artifacts from earlier slots. It's
more likely that Cascade reads from the workspace across all slots for common context, without
constituting a type of cross-slot state contamination. For example, in `EC-6`, `Claude Sonnet 4.6`
flagged the prompt as suspicious and refused to proceed while the other agents completed the test tasks
with no issues. 

_`read_url_content` requires explicit user approval before each fetch executes_. When
asked directly, Cascade confirmed: it invokes `read_url_content` when a prompt includes a URL,
and the function requires explicit approval before the fetch executes. Each slot issued its
own fetch independently, confirmed by a distinct permission prompt per slot. Output variance
across slots reflects the full pipeline, retrieval through post-processing, not
post-retrieval processing differences from a shared fetch result.

### Methodology Decision

Log all five slots as distinct rows under the same test ID. `Auto Execution` turned off throughout testing
to maximize observable detail; slots approved sequentially by user choice. Worktree isolation means slot
position isn't expected to be an ordering variable.

> _Windsurf `v1.9600.38` introduced the [`Adaptive` model router](https://windsurf.com/changelog) that dynamically
>selects the underlying model per task like that of Copilot and Cursor's `Auto` settings. All interpreted track tests
>used explicitly named models in hybrid arena mode, never triggering the `Adaptive` model router._

---

## Mixed-Format Source Misidentified

The `BL-2` [source document](https://www.mongodb.com/docs/manual/reference/change-events/create.md)
is a mixed-format file: the page structure and prose are Markdown, but the field description
table is raw HTML. Across all five `BL-2` runs, agents read the mixed format as evidence of
parsing failure, toolchain corruption, or incomplete retrieval rather than as a stable source.
Throughout runs, agents consistently diagnosed this as a retrieval issue:

| **Artifact** | **Agent Attribution** | **Possible Cause** |
| --- | --- | --- |
| HTML table in `.md` source | Toolchain failed to convert page to Markdown | Table authored in HTML in the source; no conversion occurred or expected |
| `nsType` enum values absent | Stripped during<br>HTML-to-text conversion | Values absent in the `.md` source;<br>CMS-injected at rendering |
| `ce-create##` prefix | Toolchain metadata injection or parsing anomaly | Present verbatim in the source as<br>a CMS publishing artifact |

The [truncation taxonomy](#truncation-taxonomy) captures cases where retrieval delivers
less than the source contains. This phenomenon is different in kind: retrieval delivers the source faithfully,
but the agent doesn't recognize the source format as valid and treats its properties as retrieval artifacts.
The gap isn't in the retrieval, but in the agent's artifact type identification.

Mixed-format source misidentification introduces a confound for any hypothesis that relies on agent self-reported
truncation assessments. An agent reporting _"content appears truncated"_ or _"table structure is broken"_ may be
accurately describing a retrieval artifact or misidentifying a property of a valid mixed-format source.
The observable evidence is identical from the agent's perspective. Cross-referencing agent truncation reports
against the raw source is necessary to distinguish these cases.

### Methodology Implication

The interpreted track captures agent self-reporting as-is. An agent attributing the HTML table or absent enum values
to toolchain failure is a valid interpreted track data point, not a logging error. The agentic analytical layer requires
source inspection.

Before treating a formatting-based truncation attribution as evidence for or against a retrieval hypothesis, check
whether the flagged anomaly is a property of the source document. For `BL-2`, direct inspection of the `.md` source
confirms the mixed format is present, but whether the document is complete by design or incomplete by artifact remains
unverified. Where source inspection isn't feasible, apply additional skepticism to formatting attributions that appear
consistently across multiple agents on the same URL. Consistency is more characteristic of a stable source property
than of toolchain conjecture.

---

## Prompt Injection Suspicion

`OP-4` run 2 used `Claude Sonnet 4.6` and flagged the tool visibility request as a probable prompt injection attempt.
The agent's reasoning, surfaced in the thought expander, identified three features of the request as suspicious:

- Prompt names `read_url_content`, `view_content_chunk`, `search_web` _explicitly_
- Framing "Agent Ecosystem Testing" as _legitimacy signal used to lower resistance_
- Asking agent to enumerate internal tool names as _known extraction pattern_

The agent declined to report internal system identifiers, reporting only the tools it had directly invoked from its own
tool call history.

The irony is straightforward: the tool names are [publicly documented](https://docs.windsurf.com). A user reading the docs
before designing a test protocol is indistinguishable, from the agent's perspective, from an adversary who has
reverse-engineered the tool surface. This creates a methodology confounder: perhaps the more precise the prompt,
the more likely it's to trigger safety heuristics. A vague prompt - _"what tools did you use?"_ may elicit fuller
disclosure than a precise prompt that references tools by name.

This is the inverse of the `GPT-4.5` behavior in `SC-2` run 3, which leaked `CORTEX_STEP_TYPE_READ_URL_CONTENT` unsanitized.
Across two runs, the two failure modes are symmetric: one agent over-reports undocumented internal metadata; another refuses
to report documented tools. Neither behavior is useful for logging.

`EC-6` run 2 produced a full refusal, again from an agent using `Claude Sonnet 4.6`. Unlike `OP-4`, where the agent
completed the retrieval task but declined to report tool names, this run refused the fetch entirely. The reasoning surfaced
four suspicion signals:

- Named tool identifiers in the prompt, _again_
- [Source URL](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md) flagged by repository
name as potential _prompt injection payload_
- Framing `"don't proceed to other tests"` as _social engineering pattern_
- Test metadata: ID, file size, empirical findings - as _false legitimacy signals_

The URL flag is new. `OP-4` triggered on prompt content alone; `EC-6` triggered on the fetch target itself. According to the
agent, a URL that accurately describes the testing project is indistinguishable from one constructed to manipulate behavior
after injestion. The refusal didn't hold across execution contexts. A single retry of the same prompt, same URL completed
without a hitch: full retrieval of all chunks.

### Methodology Implication

The prompt's tool visibility item may need two variants: one that names tools explicitly for agents that don't flag extraction
heuristics, and one that uses generic language for agents that do. Alternatively, accept that tool visibility self-reporting
is unreliable. Treat it as a soft signal rather than a primary observation. Cross-referencing against Cascade's tool approval
prompts, which are user-visible regardless of agent reporting, is a more reliable source of tool visibility.

`OP-4` run 3 used `GPT-4.5` and adds a counterpoint. Its internal reasoning independently arrived at the same architectural
description the prompt used, that `read_url_content` returns chunk metadata rather than page body, that character counts from
the index response aren't meaningful, and that exact counts are unavailable due to tool limitations, by reasoning from the tool
response itself, not from prompt-supplied framing. The knowledge `Sonnet` flagged as suspicious in the prompt is recoverable
from the tool output by a different agent's analysis - this knowledge isn't injected, but derivable. Agentic analysis may
match the prompt, because the prompt uses accurate terminology.

---

## `read_url_content` - Fetch Architecture, Parsing Limits

[Windsurf's documentation](https://docs.windsurf.com/windsurf/cascade/web-search#reading-pages)
describes `read_url_content`'s retrieval behavior as intentionally selective:

> _"We break pages up into multiple chunks, very similar to how a human would read a page:
> for a long page we skim to the section we want then read the text that's relevant.
> This is how Cascade operates as well."_

Targeted skimming is relatable. Human readers often reference docs rather than study them from start
to finish. Informed by a precise prompt, an agent navigates to the relevant section, reads it, and
skips the rest. It's reasonable design for long pages where a full retrieval would be expensive.

The gap between intent and observed behavior is the chunk index quality. Targeted skimming requires
navigational signal: a human skimming a page uses headers, section titles, and visual hierarchy to
locate the relevant section. `read_url_content` provides a chunk index to serve this role, but across
all five `OP-4` runs the index returned empty summaries `" "` or `""` for all 53 positions. Without
populated summaries, chunk selection is blind. The tool's skimming is structurally identical to
random sampling: any chunk is as likely to contain CSS as tutorial prose, and there's no metadata to
distinguish them before fetching. The docs acknowledges this directly:

> _"It's worth noting that not all pages can be parsed. We are actively working on
> improving the quality of our website reading."_

The [MongoDB Atlas Search tutorial](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/) is an
instance of this failure mode. The tool scraped the full rendered DOM rather than the article body,
so chunk boundaries cut across CSS definitions and navigation markup rather than document sections. Empty
summaries are a consequence: there's no recoverable article structure to summarize. As a documentation gap
Windsurf acknowledges, this is an expected failure mode for certain page types and shifts how it should be
characterized as a worst case, but not a testing anomaly.

The name `read_url_content` isn't misleading, it's accurate to the intent. What it actually fetches on the
first call is metadata, not plain text content. Content requires subsequent `view_content_chunk` calls, and
what those return depends entirely on whether the page's DOM parsed into recoverable article structure. For
well-structured pages this may work as documented. For CSS-heavy rendered pages, the fetch succeeds, but
the content may be absent. While this complicates hypotheses assessment because this tool limitation doesn't
guarantee testability, it doesn't invalidate the test design. 

In the case of empty summaries, the architecture gets the cost savings of selective retrieval without delivering
the navigational benefit that would justify it: agent doesn't read the whole page and can't target what it does
read. If populated summaries are required to satisfy the _"human skim"_ behavior documented, then empty summaries
return blind sampling that's invisible to the user and, based on `OP-4` runs, sometimes invisible to the agents
themselves. An agent that sampled 2 of 53 chunks didn't report reading 4% of the page, it reported on what it
found. There's no externally visible signal distinguishing "answered from retrieved content" from "answered from
priors, fetch call in the log for grounding." Logging which URLs produce readable content verses empty summaries
is useful data, characterizing the tool's current parsing envelope and tracking whether its improves across
Windsurf versions.

---

## `read_url_content` Internal URL Rewriting

`SC-2` tests truncation behavior on a valid, live endpoint, an
[Anthropic Messages API page](https://docs.anthropic.com/en/api/messages). All runs failed to retrieve the target
content. These weren't retrieval failures, network access issues, or dead URLs, but they uncovered a `read_url_content`
bug, in which the tool silently rewrites the URL before executing the fetch. The rewritten URL redirects to an
`llms-full.txt` and returned a `404`. The requested path `/en/api/messages` is never fetched. No agent received the
target content because no agent was ever issued a request for it. `read_url_content` substituted a different resource
before the network call was made, making most of the hypotheses untestable. The five agents' error output meaningfully diverged -

| **Session** | **Agent** | **Tools Called**| **Fallback Behavior** | **Output** |
| --- | --- | --- | --- | --- | --- |
| **1** | `Codex` | `read_url_content` ×2 | Followed redirect, <br>reported error verbatim | 164 chars |
| **2** | `Sonnet` | `read_url_content` ×2 | Acknowledged failure explicitly | 0 chars |
| **3** | `GPT` | `read_url_content` ×2 | Surfaced `CORTEX_STEP_TYPE_READ_URL_CONTENT` | 0 chars |
| **4** | `Opus` | `read_url_content` ×3 | Third attempt `platform.claude.com`;<br>received `404` HTML | ~35–40 KB |
| **5** | `SWE` | `read_url_content` ×3 <br>`search_web`<br>×1 | Unique `search_web` call;<br>identified URL rewriting as root cause | 0 chars |

`SWE-1.6` is the only agent across 61 interpreted track runs to call `search_web`. After two failed fetch attempts, the output
included reasoning that led to an alt-retrieval strategy rather than stopping. While Cognition's agents have consistently
performed a type of most-confident, most-wrong pattern, during this test run, this case revealed possible trained familiarity to
produce the clearest root cause diagnosis of any session:

> _"`read_url_content` appears to have an internal URL rewriting issue that transforms `https://docs.anthropic.com/en/api/messages`
> into `https://docs.anthropic.com/llms-full.txt`, which then redirects to a non-existent endpoint."_

`Claude Opus 4.6` made a third fetch attempt against the original URL and received a response, which wasn't the target
content, but a complete `404` error page rendered as `Next.js` HTML. While not useful for hypotheses assessment, it did
confirm that `read_url_content` can return substantial payloads under this error condition, and that the tool's ceiling
wasn't reached at this size.

`GPT-4.5` named Cascade's undocumented `CORTEX_STEP_TYPE_READ_URL_CONTENT`, which suggests that result metadata passes through
to the agent context without sanitization in at least some error conditions.

`SC-2` doesn't require a source URL change. A rerun after a Windsurf update or anti-redirect prompt may yield different
results. Treat the rewriting behavior as a testable tool property, not a permanent URL constraint.

> _The [Friction: Explicit content](friction-note-explicit.md#sc-2-url-redirect-behavior) recharacterizes this failure mode._

---

## Retrieval Collapse, Indexing Masking Absence, Truncation Cacophany

Across the testing suite, agents running identical prompts on identical URLs produce contradictory truncation assessments.
`SC-4` was no different: five agents, same source, same tool calls, truncation reports ranging from "no truncation detected"
to byte-level notices at four specific chunk positions. These contradictions appear wherever agents self-report retrieval
fidelity, and the variance reflects retrieving at different depths - they're just not reporting on the same evidence. This
isn't a test design failure, as it reveals that agent-reported truncation tracks chunk selection more than it tracks raw
content loss, which itself is a finding about Cascade's default retrieval behavior.

`read_url_content` → `view_content_chunk` is a two-stage pipeline. While agents acknowledge calls to each function as separate
steps, they often describe it as a single event in their truncation reporting. The first call returns a chunk index with summaries
of positions and structural metadata, not raw page content. Content requires subsequent, individual `view_content_chunk` calls,
each returning a processed, transformed representation of one chunk. According to agent descriptions, the expected flow is:

1. `read_url_content` → chunk index: structural metadata, no body content
2. Agent reasons over index → selects chunks to retrieve
3. `view_content_chunk` × N → processed text per chunk: HTML stripped,<br>code flattened,
   tables may be absent
4. Agent aggregates retrieved chunks → forms completeness assessment
5. Agent reports on retrieval fidelity

A collapse often happens between steps 1 and 4. An agent that receives a complete index, with all positions present and summaries
populated, is in an epistemically comfortable position. When it then retrieves all chunks and finds no mid-sentence cutoffs, the
comfort extends: nothing _looks_ truncated. The content transformation that occurred at the tool layer, any stripping or flattening
or replacing is often invisible, because the agent has no unprocessed baseline to compare against. It may not be able to distinguish
_"chunking stripped this table"_ from _"this page never had a table here."_ This is a structurally cognitive limitation: the
agent sees what the tool delivered, but has _no access to what the tool discarded_. Three factors interact to produce a cross-agent
disagreement observed in `SC-4`:

| **Factor** | **Mechanism** | **Report Impact** |
| --- | --- | --- |
| **Chunk Selection Depth** | Agent samples positions 0, 20, 32<br>never encounters truncation notices<br>at 13, 17, 18, 25 | _`"No truncation"` may be locally accurate for chunks seen, not globally accurate for the document_ |
| **Truncation Notice Interpretation** | `view_content_chunk` surfaces explicit byte-count notices within individual chunk retrieval responses; agents differ on whether this constitutes truncation | _Same notice produces `"truncated at position N"` in one agent and no flag in another; both defensible_ |
| **Content Transformation Visibility** | Tool pipeline strips HTML, flattens code, removes tables before delivery; agent has no unprocessed baseline | _Losses undetectable without knowledge of source structure; agent reports received as what exists_ |

The self-report truncation field conflates at least three distinct assessments:

| **Assessment** | **Measurement** |
| --- | --- |
| _Initial fetch truncated?_ | Whether `read_url_content` returned partial index |
| _Any individual<br>chunk truncated?_ | Whether `view_content_chunk` returned <br>byte-count notices |
| _Full content delivered?_ | Whether pipeline preserved source fidelity |

An agent `"no"` may be accurate on all three, accurate on one and wrong on two, or accurately describing a transformed-but-complete
delivery, while missing that transformation _is_ a form of content loss. `Claude Opus 4.6`'s `SC-4` formulation:
_"substantially complete, but not byte-for-byte faithful"_ is the most precise observed, because it separates structural coverage
from content fidelity, but it's also the exception. This isn't a logging limitation or prompt ambiguity, but the signal that
the interpreted track intends to capture. The raw track is where the self-reports become accountable.

---

## SPA Extraction: Duplication, Code Block Fidelity

`EC-1` used an SPA and revealed content fidelity issues not observed on static pages:

| **Issue** | **Mechanism** | **Agent-recoverable?** |
| --- | --- | --- |
| **Code Block Stripping** | Triple-backtick fences preserved but<br>language identifiers dropped: `python` becomes **```**<br>output is syntactically valid Markdown with no<br>truncation notice surfaced | _No_, nothing distinguishes stripped identifier from absent one |
| **Responsive DOM Duplication** | Nav elements rendered per breakpoint - desktop, mobile, sidebar - extracted as text; not de-duplicated before delivery; repeated nav blocks and code blocks appearing in both pre-render and post-render form | _No_, no de-duplication signal in chunk output |
| **Selective Semantic Processing** | Tool applies semantic transformation to prose: stripping HTML to Markdown, summarizing chunk content in index, but passes page structure through verbatim; processing boundary falls at article body: content is transformed, shell appears extracted raw | _No_, agents can't comment on processing boundary |

All issues are invisible to agents without a raw source baseline to compare against, and produced the sharpest Markdown quality
assessment disagreement in the dataset: `Claude Sonnet 4.6`, `GPT-5.3-Codex`, and `SWE-1.6` reported clean, complete Markdown;
`Claude Opus 4.6` and `Kimi K2.5` flagged duplication on identical chunk content. For SPAs, Markdown formatting assessment seems
unreliable as a retrieval fidelity signal. Disagreement across agents on the same content may reflect whether an agent
cross-referenced chunks rather than assessed each in isolation. This is the type of gap that the raw track intends to close.

---

## Test Objective Unreachability

`SC-3` tests table row and column preservation at truncation boundaries using a Wikipedia page with a large population table spanning
chunk positions 3–13. Across all five runs, no agent fetched any chunk within that range. All five runs defaulted to endpoint sampling -
positions 0 and 58, or 0, 30, and 58 - leaving the test objective untested in every run.

The chunk index summaries returned populated and correctly identified the table content's position range. `SWE-1.6` mapped positions 3–13
as `"main article content (Method, Sovereign states table)"` from the index alone. Navigational signal was present; no agent acted on
it for targeting purposes.

This distinguishes `SC-3` from `OP-4` and `BL-3`, where empty summaries made targeted retrieval impossible by design. On `SC-3`, targeted
retrieval was architecturally viable, but behaviorally absent. The hypothesis isn't untestable in principle, it's untestable under current
default sampling behavior on pages with 50+ chunks. A prompt explicitly directing agents to retrieve the table-containing chunks may resolve
this, but would also change measurement.

The interpreted track documents default agent behavior under realistic conditions: what agents do when given a URL and a reporting
task. `SC-3`'s essentially _null_ result isn't a test design failure, but confirms that on pages exceeding ~50 chunks, default sampling behavior
doesn't reach interior content even when the chunk index provides sufficient signal to do so. That's itself a finding about the
architecture's practical ceiling for content targeting: the tool supports it, the agents don't tend to use it at this scale.

>_The explicit track replicated this finding. Like `SWE`, `GLM-5.1` identified the table position from the index without retrieving it_.

---

## Truncation Taxonomy

`read_url_content`'s chunked index architecture requires redefining what truncation means
in the Cascade testing context. Across
[Copilot testing](../microsoft-github-copilot/friction-note.md#truncation-taxonomy),
truncation described three distinct phenomena that produced similar-looking outcomes, less content than the page contained,
but had different causes and different implications for what the verification script could confirm. Cascade introduces new
phenomena that don't map cleanly onto any of the three Copilot cases.

| **Phenomenon** | **Retrieval<br>complete?** | **Agent reports truncation?** | **Verification detects?** |
| --- | --- | --- | --- |
| **Chat rendering<br>truncation** | _Yes_, full bytes transferred<br>and saved | _No_, file complete | _No_, requires comparing chat<br>output to<br>verified file |
| **Chunked index,<br>partial chunk<br>retrieval** | _No_, index returned;<br>most chunks<br>never fetched | _No_, agent reports<br>what it sampled | _Indirectly_ via<br>output size<br>vs expected |
| **Chunked index,<br>full chunk retrieval with per-chunk display truncation** | _Structurally yes_, but middle of most chunks hidden | _Yes_ , agent surfaces truncation notices per chunk | _No_, hidden bytes aren't in any saved artifact |
| **Chunked index,<br>full chunk retrieval,<br>incorrect<br>self-report** | _Structurally yes_, per-chunk display truncated | _No_, CSS completeness mistaken for content completeness | _No_, no metadata to<br>cross-reference against |
| **Chunked index,<br>empty summaries,<br>blind sampling** | _No_, index<br>complete but<br>summaries uninformative | _No_, agent reports<br>what it sampled | _No_, no metadata to<br>cross-reference against |
| **Retrieval-layer architectural<br>excerpting*** | _No_, content filtered before delivery | _No_, agent sees what<br>the tool delivered | _Indirectly_ via truncation indicators,<br>size vs expected |

> *_Explicit track's `EC-1` results reinforced this pattern: ~100 KB page returned ~20,000-35,000 chars with no agent-reported
> truncation. Agents evaluating truncation within tool response, not against the source, have no signal that ~65-80 KB was never delivered_.

### Chunked Index, Partial Chunk Retrieval

`read_url_content` doesn't return a page body, but an index of chunk positions. Each chunk must be retrieved
separately via `view_content_chunk`. For the `BL-1` URL, the index contained 54 positions, 0–53. `BL-1` runs
1 and 2 retrieved chunks only from the first and last positions - sampling endpoints rather than iterating
sequentially. 52 of 54 chunks were never fetched.

This is the dominant truncation mode in Cascade testing and it differs dramatically from Copilot's `fetch_webpage`
architecture. `fetch_webpage` delivers a pre-assembled, relevance-ranked excerpt in a single payload, and the
transformation happens before the agent receives anything. `read_url_content` delivers an index and leaves chunk
selection up to interpretation. What the agent retrieves is a behavioral variable, not a retrieval-layer constant.
The content gap is agent-authored rather than tool-imposed.

The agent doesn't report this as truncation because from its perspective the index was complete - it received all
54 positions. Whether it fetched 2 or 54 of them is a _retrieval decision, not a retrieval failure_. The prompt's
truncation question, _"was any content truncated?"_, doesn't capture this distinction. A response of
_"yes - by design via chunking"_ is accurate, but doesn't quantify how much content Cascade skips, and a response of
_"no"_ is locally defensible but globally misleading.

Character counts logged for interpreted track runs reflect only the chunks the agent actually retrieved, not the full
document. For `BL-1` runs 1 and 2, this was ~4,800–10,200 characters from two sampled chunks against an expected ~85 KB page.
_The figure is not a truncation ceiling, but a sampling artifact_. Cross-run variance in `output_chars` may reflect different
chunk selection decisions rather than retrieval-layer variance.

| **Hypothesis** | **Verdict** | **Defense** |
| --- | --- | --- |
| `H1` | _Indeterminate_ | Char ceiling not tool-imposed; determined by<br>agent chunk selection |
| `H2` | _Indeterminate_ | Same reason as `H1` - token ceiling unobservable<br>under chunked architecture |
| `H5` | _No_ | `BL-1` run 1-2 only called `view_content_chunk` at<br>positions 0, 53; no sequential, auto-pagination |

### Chunked Index, Full Chunk Retrieval with Per-Chunk Truncation

`BL-1` run 3 used `Claude Opus 4.6` and retrieved all 54 chunks in parallel via `view_content_chunk`, confirming
`H5-yes` for the first time in the dataset. However, full chunk retrieval exposed a second truncation layer not
visible in partial retrieval runs: `view_content_chunk` internally truncates the display of each chunk, returning
only the beginning and end of its content with a notice between them:

```Markdown
"Note that N bytes in this tool's output were truncated - consider making different
tool calls to output fewer bytes if you wish to see the untruncated output"
```

First, the prompt doesn't request that any specific tool be used, just that tools-used reported. Second, 51 of 54
chunks were affected, with hidden content ranging from 208 bytes of chunk 0 to 20,540 bytes of chunk 15. Only chunks
48, 49, and 50 were delivered without internal truncation. The total hidden content across all chunks was approximately
132 KB. The actual fetched content was ~220–240 KB, far exceeding the expected ~85 KB, because
`read_url_content` retrieved the full rendered page including inline CSS and navigation chrome duplicated three times:
desktop, mobile, and sidebar. _This isn't a document size measurement but a rendering artifact_.

Each `view_content_chunk` result included three components: a `text` field with the chunk content, beginning and end
only, the truncation notice with byte count, and structured metadata for chunks 49–53 including
`type:MARKDOWN_NODE_TYPE_HEADER_1` and `type:MARKDOWN_NODE_TYPE_HEADER_2` fields, suggesting the tool has structural
awareness of content type that isn't consistently surfaced across all chunks. This creates a retrieval architecture
with two distinct truncation layers operating independently:

- **Layer 1** `read_url_content`: doc split &rarr; N chunks; partial retrieval, most unfetched
- **Layer 2** `view_content_chunk`: fetched chunk display-truncated, hiding middle portion

The agent never sees the complete content of most chunks even when all chunks are fetched. Full chunk retrieval confirms
the document's structural completeness, the final chunks in `BL-1` run 3 contained the expected footer navigation, but
can't confirm that no mid-chunk content was lost, because the hidden bytes aren't recoverable from any artifact the agent
produces. The verification script has no mechanism to detect **Layer 2** truncation; it isn't visible in saved output files
and the agent can't report what it never received.

The behavioral difference across `BL-1` runs is itself a finding. `Claude Sonnet 4.6` and `GPT-5.3-Codex` both sampled
endpoints, chunks 0 and 53, without attempting full retrieval. `Kimi K2.5` sampled six chunks: positions 0, 1, 50, 51, 52,
and 53, the first two and last four, a strategy that retrieved more tail context than `Sonnet` or `GPT` while stopping well
short of full retrieval. `Claude Opus 4.6` retrieved all 54 chunks in parallel. Three distinct chunk selection
strategies across four runs on the same URL and prompt suggest _chunk selection is agent-dependent rather than prompt-driven_.
Whether this reflects agent capability, context window size, or prompt interpretation differences isn't resolvable from the
`BL-1` data alone, but the divergence means `H5` results aren't uniform across agents on identical URLs and prompts.

### Chunked Index, Empty Summaries, Blind Sampling

`OP-4` run 4 used `Claude Opus 4.6` and `read_url_content` returned an index of 53 chunk positions, but all chunk summaries
were empty, `" "` or `""`. The response is structurally complete, all positions are present, but not helpful. an agent attempting
to retrieve only article body content has no metadata to select against.

This collapses the available retrieval strategies to two: sample blind, accepting that any chunk may contain CSS or navigation
rather than tutorial content, or retrieve all 53 chunks exhaustively. `Opus` output stated that an exhaustive retrieval wasn't
worth it, given the signal-to-noise ratio observed in sampled chunks; a correct assessment, but one that leaves the article body
largely unread. In addition, `Opus` reported that the tool scraped the full rendered DOM, rather than the article body, so the
chunk boundaries cut across CSS class definitions and navigation markup rather than document sections. According to `Opus`,
there's no article structure for the tools to summarize; this is a _parsing/extraction failure at the tool layer_, not a size-based
truncation issue, and likely not agent behavior that a prompt can correct. Architectural truncation impacts the hypotheses in
different ways:

| **Hypothesis** | **Verdict** | **Defense** |
| --- | --- | --- |
| `H1` Character Ceiling |  _No_ | ~220–240 KB actual content far exceeds any plausible fixed ceiling; apparent size variance is a rendering artifact, not a tool limit |
| `H2` Token Ceiling | _No_ | ~55,000–65,000 tokens across all 54 chunks rules out a ~2,000 token ceiling |
| `H3` Structure-aware Truncation | _Indeterminate_ | Chunks can show `MARKDOWN_NODE_TYPE_HEADER` metadata suggesting partial structure-awareness, but bulk content raw CSS/nav HTML, boundary behavior not assessed |
| `H5` Auto-pagination | _Partial_ | Confirmed for `Opus` only; not observed for `Sonnet` or `GPT-Codex` on identical prompt/URL |

> _Interpreted track captures self-report variance; while `H1` and `H2` verdicts can be read as document-level, `view_content_chunk`
> imposes a separate per-chunk display ceiling, ~2K visible > chars;
> see [Chunked Index, Full Chunk Retrieval with Per-Chunk Truncation](#chunked-index-full-chunk-retrieval-with-per-chunk-truncation);
> `BL-3` `Opus` estimated ~56% retrieval loss from this layer stacking across 53 positions. ~2K ceiling configurability is unconfirmed_.

### Continuous Variable Pagination Depth

`BL-3` produced four distinct pagination depths across five runs on the same 53-chunk URL, revealing that `H5`
as currently framed doesn't capture the full behavioral range observed -

| **Depth** | **Agent** | **Chunks Fetched** |
| --- | --- | --- |
| **None** | `Claude Sonnet 4.6` | 0, index only |
| **Endpoint Sampling** | `GPT-5.3-Codex` | 2 |
| **Distributed Sampling** | `Kimi K2.5` | ~11 |
| **Full** | `Claude Opus 4.6`, `SWE-1.6` | 53 |

The stopping condition is as informative as the depth. `Sonnet` cited empty chunk summaries as its rationale for not
paginating, which isn't an uncommon interpretation that reasons an early exit. This makes pagination depth _rationalization-dependent_,
not purely capability-dependent: the same chunk index with populated summaries might produce a different depth outcome for the same agent.
Empty summaries don't prevent retrieval; they remove the navigational signal that would motivate it.

Pagination depth is a behavioral variable layered on top of a fixed retrieval structure. The chunk index architecture is deterministic:
`read_url_content` consistently returns the same 53-chunk index across all runs and agents. What varies is entirely downstream: agent
chunk selection.

---

## Unverified Size, Truncation Signal

`SWE-1.6` reported receiving _"~4.8 KB, 24% of expected ~20 KB"_ and flagged this as evidence that the fetch was
incomplete. The ~20 KB expectation wasn't derived from a measurement, `search_web` wasn't invoked and no external
size reference was retrieved. `BL-2`'s prompt ~20 KB figure likely originates from earlier testing of the same URL
on different platforms, Cursor, or Copilot runs where `fetch_webpage` retrieved the fully rendered page including
navigation, sidebar, and inline CSS. That figure was a real measurement, but of a different artifact than what
`read_url_content` delivers. Alternatively, the source `.md` file may have changed in size between testing sessions.
It's possible that the original estimate was miscalculated. In either case, neither `SWE-1.6` nor `GPT-5.4` verified
the size expectation before using it as a truncation signal.

It's a metacognitive failure: the agent doesn't recognize that the size expectation is an uncertain input that should
be verified before being promoted to a diagnostic measurement, and it has a tool available to do exactly that. The
irony is structural: the test intends to observe retrieval fidelity, the agent responds to apparent retrieval
incompleteness by _not retrieving_. `search_web` was available in all four `BL-2` runs and unused in all four. If an
agent is uncertain enough about expected content to flag a 76% shortfall, that uncertainty is exactly the condition
under which a verification fetch would be warranted.

When an agent reports a specific size expectation, log whether it as current run retrieval or carried in from elsewhere.
Regardless of the source, if the agent uses an unverified size estimate as a truncation signal, flag it as a diagnostic
error. The behavior of interest isn't whether the agent reached the right answer, but whether it recognized the difference
between a verified measurement and an unverified estimate.

---

## URL Fragment Targeting

During `OP-1` run 3, `Claude Opus 4.6` reported no truncation, citing the architecture:

> _"The `read_url_content` and `view_content_chunk` system uses a two-phase chunked retrieval agent,
> not a single monolithic fetch. This means: no single-response truncation limit applies in the traditional
> sense; the ~40 KB expected payload is never delivered as one blob; full content recovery requires 91 sequential
> `view_content_chunk` calls for this document; truncation is structurally avoided by chunking, but the tradeoff
> is that full content requires N+1 tool calls."_

While correct, the description obscures a failure mode. `OP-1` tests whether agents navigate to a URL fragment target,
`#History` in a [machine learning Wikipedia entry](https://en.wikipedia.org/wiki/Machine_learning#History).
The assumption is that the chunked-index architecture should support this: `read_url_content` returns a chunk index,
and an agent attending to the fragment could select the chunk corresponding to `#History` rather than sampling
arbitrarily. 4 of 5 runs didn't retrieve the target section. `GPT-5.3-Codex`, `GPT-5.4` and `Opus` sampled without
reference to the fragment. `Claude Sonnet 4.6` identified the target in its reasoning, but didn't call
`view_content_chunk` to retrieve it; the intent was there, the follow-through wasn't.

`SWE-1.5` is the only agent that successfully isolated `#History` - fetching chunks 0, 1, 16, 89, and 90,
and confirming its index position at 16; demonstrating that fragment-targeting via the chunk index is achievable. The
navigational structure is there, and at least one agent used it. That makes the 4-of-5 miss rate a
_behavioral finding rather than an architectural limitation_. The chunk index supports fragment-targeting; most agents
just don't attempt it by default.

> _The [Friction: Raw content](friction-note-raw.md#url-fragment-targeting) also discusses this failure mode._
