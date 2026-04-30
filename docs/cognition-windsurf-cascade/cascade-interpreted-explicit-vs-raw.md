---
layout: default
title: "Interpreted and Explicit vs Raw"
permalink: /docs/cognition-windsurf-cascade/cascade-interpreted-explicit-vs-raw
parent: Cognition Windsurf Cascade
---

## Cascade-Interpreted and Explicit vs Raw

---

## Topic Guide

- [Truncation Testing Lossy Architecture](#truncation-testing-lossy-architecture)
- [Track Design](#track-design)
- [Key Observations](#key-observations)
- [Implications for Agent Developers](#implications-for-agent-developers)

---

## Truncation Testing Lossy Architecture

The Cascade testing framework is the most complex in this collection, and the one that most directly exposes the limits of
truncation as a research question. With that said, prior platforms didn't resolve this cleanly either. Cursor's data suggests
a ceiling, but its architecture is the most opaque in the series; no thought panel, no tool visibility, just filesystem output,
so what reads as a confident measurement may reflect the limits of observation as much as the limits of the platform. Copilot's
`fetch_webpage` performs relevance-ranked excerpting with no detectable fixed ceiling. Across all three, the pipeline between a
URL and a model response is partially observable at best.

Cascade makes the problem legible in a different way. [Colly](https://github.com/gocolly/colly) scrapes the page. Cascade
processes that output into a chunk index organized by headers, summaries, and metadata. The summaries themselves carry explicit
truncation notices flagging bytes hidden per section. An agent reading the chunk index is already working from a lossy representation.
Testing for a character or byte ceiling assumes content arrives intact. In this pipeline, it does not. When agents across both Copilot
and Cascade testing recognized this, that the pipeline was returning filtered, restructured content rather than the source, some
switched to `curl` as a workaround. `curl` retrieval produces output closer to complete in byte terms, but raw HTML or JavaScript
skeletons are not semantically meaningful for a human reader trying to answer a development question from public docs. Completeness and
usability aren't the same measurement, and neither track alone captures both.

This is likely not a Cascade-specific design. Based on observed agent behavior across this testing series, content transformation
before chat output generation appears to be a general characteristic of agentic web fetch. While their systems may include retrieving web
crawler content, agents don't perform web crawling on demand by default. The pipeline between a URL and an agent response typically passes
through layers that filter, restructure, and/or summarize content before it reaches the primary LLM.

The three tracks still produce findings, though not the ones the hypothesis framework assumed. The interpreted track and the explicit track
expose chunk selection behavior, extraction ratio gaps, and self-report fidelity under common use conditions. The explicit track was designed
to isolate a second retrieval path: Cascade's `@web` directive was expected to route to `search_web`, but it didn't. Agents defaulted to
`read_url_content` with a URL provided in all but one run across 66, confirming that `@web` is a routing hint and not a retrieval modifier;
`search_web` isn't a meaningful retrieval path in this context.

The raw track adds a write task, which brought the most unexpected finding: agents can claim to have read content they largely can't reproduce.
The gap between pagination depth and write outcome is the clearest signal in this dataset about the limits of agentic comprehension, and about
what it means to test a platform against a task it perhaps wasn't designed to perform. That negative result is itself the specification.

---

## Track Design

Three test tracks measure Cascade web fetch behavior from different angles.

The **interpreted** track captures what the agent believes it retrieved: character count, token
estimate, truncation status, content completeness, and Markdown formatting integrity. No file
is written. This is the agent's self-report against `read_url_content` and `view_content_chunk`
output only.

The **explicit** track extends the interpreted track with an `@web` directive prepended to the
URL. It tests whether the directive changes retrieval behavior, tool routing, or agent self-report.
The finding is that it does not: `@web` is a routing hint, redundant with a URL, and maps to
`read_url_content` across all agents in all runs.

The **raw** track adds a write task: the agent is instructed to retrieve the URL and save output
exactly as received to a specified path. The verification script then measures the saved file
against ground truth via byte count, MD5 checksum, and token count. The gap between pagination
depth and write outcome is itself a finding.

The gap between the interpreted and explicit tracks is narrow: `@web` produced no behavioral
change. The gap between either of those tracks and the raw track is more subtle than it first
appears. Claiming full retrieval was common across all three tracks — in the raw track, roughly
20 of 66 runs reported reading 100% of available chunks. Proving it was not: only approximately
17 of those runs produced a successful write output. The write task was designed to test whether
retrieval claims held under output accountability. For most agents, on most large-chunk sources,
they did not.

| | Interpreted Track | Explicit Track | Raw Track |
| - | ---------------------- | ---------------------- | -------------------------- |
| **Directive** | URL only | `@web` + URL | URL only |
| **Write Task** | None | None | Save to `raw_output_{test_id}.txt` |
| **Measures** | Agent self-report of retrieval | Agent self-report with `@web` routing | Filesystem measurements of saved output |
| **Character Counts** | Agent estimates | Agent estimates, tool wrapper preamble may inflate | `wc -c` on disk — exact, reproducible |
| **Completeness** | Agent prose assessment | Agent prose assessment | MD5 comparison, byte count, verification script |
| **Token Counts** | Agent estimates; chars/4 heuristic or word count substitution | Agent estimates | `cl100k_base` — exact tokenizer |
| **Reproducibility** | High variance; chunk selection agent-dependent | High variance; same behavior as interpreted | Byte-identical within same agent and URL; failure modes distinguishable by MD5 |
| **Output Format** | Chat UI rendering | Chat UI rendering | Raw file on disk, `raw_output_{test_id}.txt` |
| **Best For** | Understanding chunk selection behavior and `read_url_content` pipeline limits | Confirming `@web` routing semantics; wider agent pool | Citable measurements; write failure taxonomy; retrieval mechanism confirmation |

---

## Key Observations

1. **`@web` is redundant with a URL**

    The explicit track was designed to test whether the `@web` directive changes retrieval
    behavior. It does not. Across all 66 explicit runs, `@web` mapped to `read_url_content`
    in every case. `search_web` was called once by `GLM-5.1` during `SC-2` as an independent
    verification attempt, not as `@web`-driven routing, and returned near-empty results. No
    agent flagged the redundancy unprompted.

    Agent descriptions of `@web` semantics ranged from non-recognition to pipeline-depth
    awareness, but none said the obvious: that in this context, calling it would produce no
    behavioral difference.

2. **Chunk selection is the primary behavioral variable across interpreted and explicit tracks**

    Both tracks use the same two-stage pipeline. `read_url_content` returns a positional index
    with summaries. Content requires sequential `view_content_chunk` calls per position. Output
    size, truncation self-report, and content completeness all track chunks fetched, not any
    tool-imposed byte ceiling. No fixed character or token ceiling was detected in either track.

    A tractability threshold is visible across both tracks: agents tend toward full retrieval
    on chunk counts of 14 or fewer and toward sparse sampling on counts of 50 or more, with
    33 to 38 chunks as the transition zone where model families diverge. `Claude Opus` and
    `SWE` show the most consistent full-retrieval behavior. `GPT-5.3-Codex`, `Gemini 3.1`,
    and `Kimi K2.5` default to sparse sampling more frequently than other agents.

3. **Read-write asymmetry is the dominant structural finding of the raw track**

    The raw track confirms that `view_content_chunk` retrieval is reliable. Most agents
    successfully paginated all chunks across most tests. Write success was substantially lower
    across the same tests. Tests where pagination depth was high but write outcomes were spotty
    include `BL-3`, `OP-1`, `OP-4`, and `SC-3`. `EC-3` was the only test with a clean success
    sweep, and only because the URL content was below the chunking threshold entirely.

    The raw track average output size was 1,129,230 chars, with a range of 275 to 56,256,891
    chars, compared to 37,600 chars on the interpreted track and 43,441 chars on the explicit
    track. The divergence reflects write strategy variation, not retrieval ceiling differences.

4. **Write outcomes in the raw track cluster into four categories**

    Outcome in the raw track does not cluster around a single mechanism. Four categories
    were observed:

    - **Pipeline acceptance**: agent retrieved chunks, assembled content, produced a valid output
      file. Content quality varies — output may be structurally complete but semantically thin,
      depending on extraction ratio and chunk selection depth.
    - **`curl` bypass**: agent correctly diagnosed that Cascade returns processed Markdown rather
      than raw content and switched to `curl`. Output files pass verification script checks but
      contain raw HTML or JavaScript skeletons without semantic prose content.
    - **False completion**: agent reported metrics and a file path for content that was never
      written. Observed across `Gemini`, `GPT-5.3-Codex`, and `SWE` on `BL-1`, `BL-3`, `EC-6`,
      `SC-3`, and `OP-1`.
    - **Cross-agent file reuse**: once a plausible file exists in the workspace, agents may satisfy
      the persistence requirement by reference rather than by writing. Confirmed at MD5 checksum
      level on `BL-2`, `BL-3`, `EC-6`, and `OP-1`. `Gemini`'s thought panel narrated retrieval
      while making no corresponding tool calls, and its output file matched `GLM`'s checksum exactly.

5. **Truncation self-report accuracy differs across tracks**

    In both the interpreted and explicit tracks, agents report truncation accurately for the
    chunks they fetched, but not accurately for the document. Agents that sampled three chunks
    from a 33-chunk corpus reported no truncation. Agents that fetched all 33 chunks found
    byte-level display notices at four positions. The self-report is accurate for content seen
    and unreliable for content missed.

    In the raw track, explicitly reported truncation events dropped to five of 66 runs. This
    reflects the chunked architecture's design: agents acknowledge the pipeline as lossy by
    construction rather than flagging specific truncation events.

6. **Per-chunk display truncation is a second independent layer, invisible to all three tracks**

    `view_content_chunk` hides the middle portion of large chunks with an explicit byte-count
    notice. This layer is independent of chunk selection depth. Full chunk retrieval does not
    guarantee full content delivery. On `BL-1`, `Claude Opus` found 132 KB hidden across 51 of
    54 chunks. On `SC-4`, 3,736 bytes were hidden across four positions. Neither the interpreted
    nor the explicit track surfaces this layer. The raw track captures it only when agents
    transcribe the byte-count notices into the output file.

7. **Two truncation layers produce compounding content loss on large sources**

    The `BL-3` tutorial test illustrates the combined effect. The source is approximately 256 KB.
    `Claude Opus` retrieved all 53 chunks in the raw track and produced approximately 7.4 KB of
    output. The per-chunk display ceiling suppressed the middle portion of most chunks. `GLM` and
    `Gemini` bypassed the pipeline via `curl` and produced approximately 468 KB of raw HTML,
    which is structurally complete but contains no tutorial body content due to Cascade's CSS
    extraction failure on MongoDB's LeafyGreen framework. The interpreted track characterized
    this as double truncation. The raw track confirmed it at the file level.

8. **CSS-heavy sources and SPAs produce extraction failure, not truncation**

    Go Colly, identified as Cascade's fetch backend across the explicit and raw tracks, is a
    static scraper. It strips HTML and does not execute JavaScript. This produces two documented
    extraction gap patterns:

    - **SPA sources**: Go Colly delivers approximately 20 to 35 percent of expected rendered page
      size. The gap is architectural and consistent across runs, not stochastic. Agents evaluate
      completeness within the tool output frame and characterize the gap as a pipeline transformation
      rather than content loss.
    - **CSS-heavy sources**: MongoDB's LeafyGreen CSS dominated chunk content across all three
      tracks on three distinct MongoDB URLs. Tutorial body content was absent across all 53 chunks
      in all `BL-3` runs regardless of agent or retrieval depth. Navigation and chrome were
      recovered. Article content was not.

9. **SC-2 redirect behavior: successful redirect, unusable payload**

    In all three tracks, no agent retrieved the target content at
    `docs.anthropic.com/en/api/messages`. The URL redirected to `llms-full.txt` —
    a format deliberately designed for LLM consumption — and the redirect completed
    successfully. No literal error codes or HTTP status metadata confirmed the layer
    responsible for the redirect, so whether it originated inside `read_url_content`
    or from Anthropic's server remains unresolved. Agents across all three tracks
    attributed the failure to a `read_url_content` tool bug — a characterization that
    `SWE-1.6` constructed most explicitly — without considering that the redirect may
    have been intentional. The `EC-3` test confirmed that 5-hop redirect chains
    returning small JSON payloads completed cleanly. Scale, not redirect behavior,
    is what made `SC-2` fail.

    The redirect destination is not the problem. The scale of what it delivers is.
    `llms-full.txt` is the full Anthropic docs corpus. No agent across any track could
    complete a targeted retrieval task against a payload that large. `Kimi` followed
    the redirect in the raw track and produced a 53.65 MB output file. VS Code
    tokenization, syntax highlighting, and scroll were disabled on open. The file
    exists; the retrieval task did not succeed.

    The `llms-full.txt` pattern is well-intentioned — a single LLM-optimized resource
    is a reasonable design for general agent consumption. But for targeted page
    retrieval, granularity matters. A redirect that delivers the entire docs corpus
    when a specific endpoint is requested may work at the network level while still
    failing the agent trying to answer a specific development question. This suggests
    that page-level `llms.txt` files, where they exist, may serve targeted agentic
    retrieval better than a corpus-level redirect.

10. **Agent self-report cannot distinguish retrieval mechanisms without verification**

    The raw track is the only track that confirms which tool ran and what the output contained.
    Agent self-report in the interpreted and explicit tracks does not surface `curl` bypass, file
    reuse, or false completion. Thought panel cross-reference is required to identify these failure
    modes. The verification script's byte count and MD5 checksum are the only consistently reliable
    signals across all three tracks.

---

## Implications for Agent Developers

Chunk count matters more than prompt, model, or directive. The tractability threshold visible
across all three tracks means that retrieval completeness is determined by index size and agent
family, not by how the fetch is requested. `@web` adds no retrieval advantage. A URL alone
produces identical pipeline behavior.

Write failure is independent of retrieval success. An agent that paginated all chunks in the
interpreted or explicit track is not guaranteed to produce a valid output file in the raw track.
The read-write asymmetry is the most important practical finding in this dataset for developers
building pipelines that depend on Cascade writing retrieved content to disk.

The verification script is not optional. Agent self-report, output size, and path compliance
are insufficient to distinguish genuine retrieval from `curl` bypass, deliberate elision, or
retrieval theater without cross-agent checksum comparison and thought panel inspection.

| **Use Case** | **Interpreted Track** | **Explicit Track** | **Raw Track** |
| --- | --- | --- | --- |
| **Retrieval Mechanism Identification** | _Partial_ — agent describes tool usage in prose; `curl` bypass not reliably surfaced | _Partial_ — `@web` routing described consistently; bypass not confirmed | ✓ `curl` bypass confirmed by file content and thought panel; `tools_used` equivalent is chunk count vs write outcome divergence |
| **File Integrity Verification** | ✗ No saved file; agent estimates only | ✗ No saved file; agent estimates only | ✓ MD5 checksums, byte counts, hexdump tail analysis |
| **Format Classification** | _Partial_ — agent describes output format in prose | _Partial_ — agent describes output format; tool wrapper preamble may distort | ✓ Verification script detects pipeline Markdown vs `curl` HTML vs JSON from saved file |
| **Ground Truth Baselines** | ✗ Self-report only | ✗ Self-report only | ✓ What Cascade actually saved vs what the agent claims |
| **Model Perception Gaps** | ✓ Reveals chunk selection bias, extraction ratio misreporting, and truncation layer conflation | ✓ Same gaps as interpreted; `@web` redundancy gap added | _Partial_ — verifier confirms file integrity but not agent interpretation |
| **`@web` Behavior Characterization** | ✗ Not applicable | ✓ `@web` confirmed redundant with URL; routing semantics documented across nine agent families | ✗ Not applicable |
| **Write Failure Taxonomy** | ✗ No write task | ✗ No write task | ✓ Four failure modes documented: pipeline acceptance, `curl` bypass, false completion, cross-agent file reuse |
| **Chunk Selection Behavior** | ✓ Primary behavioral variable; tractability threshold visible | ✓ Same threshold visible; wider agent pool confirms consistency | ✓ Write task may increase motivation to paginate; full pagination more common than in interpreted or explicit tracks |
| **User-facing Experience** | ✓ Reflects what a developer interacting with Cascade in chat actually sees | ✓ Reflects chat experience with `@web` directive | ✗ Saved file diverges from chat display; write outcome is not visible in the Cascade chat UI |
