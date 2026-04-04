---
layout: default
title: "Copilot-interpreted vs Raw"
permalink: /docs/microsoft-github-copilot/copilot-interpreted-vs-raw
parent: Microsoft GitHub Copilot
---

## Copilot-interpreted vs Raw

---

## Topic Guide

- [Two Mechanisms, Two Failure Modes](#two-mechanisms-two-failure-modes)
- [Track Design](#track-design)
- [Key Observations](#key-observations)
- [Implications for Agent Developers](#implications-for-agent-developers)

---

## Two Mechanisms, Two Failure Modes

The central finding from both tracks is that `fetch_webpage`'s relevance-ranked
excerpting is architectural and not suppressible by prompt, and that `curl`
substitution, when it occurs, produces complete files the verification script confirms as
intact but in raw server format with no transformation layer. These two behaviors produce
outputs so different in character that neither track alone is sufficient to characterize
Copilot's web fetch behavior. Cross-referencing both is the only way to separate retrieval
mechanism from retrieval quality.

---

## Track Design

Two test tracks measure the same Copilot web fetch behaviors:

**Copilot-interpreted** track captures what the model _believes_ it retrieved: how much
content it saw, whether the fetch was complete, how it characterizes truncation. This is
the model's self-report.

**Raw** track captures what Copilot _actually saved to disk_: exact byte counts, hexdump
analysis, MD5 checksums, and token counts measured by the verification script against the
saved file, not the model's estimate.

The gap between these two tracks is itself a finding. If Copilot reports "no truncation"
in chat but the raw data shows a relevance-ranked excerpt, that discrepancy belongs in the
spec. If Copilot reports "no truncation" and the raw data confirms a complete file,
but the file is raw HTML with no readable content, that's a different kind of discrepancy.

| | Interpreted Track | Raw Track |
| - | ---------------------- | -------------------------- |
| **Measures** | Model's interpretation of what it fetched | Filesystem measurements<br>of saved output |
| **Character Counts** | Model estimates; range-reported or heuristic | `wc -c` on disk -<br>exact, reproducible |
| **Completeness** | Model's prose assessment<br>of truncation | MD5 comparison, hexdump analysis, verification script |
| **Token Counts** | Model estimates; chars/4 heuristic, word count substitution, or Node regex | `cl100k_base` -<br>exact tokenizer |
| **Reproducibility** | High variance; same URL and model can produce 2x difference | Byte-identical within same file version; different versions detectable by MD5 |
| **Output Format** | Chat UI rendering | Raw file on disk, `raw_output_{test_id}.txt` |
| **Best For** | Understanding model perception gaps and `fetch_webpage` behavior | Citable measurements; retrieval mechanism identification |

## Key Observations

1. **Tracks disagree on truncation**: analyzer script flagged divergence across tests -

    | **Test ID** | **Interpreted: Truncated** | **Raw: Truncated** | **Output size difference** |
    | --- | --- | --- | --- |
    | `BL-1` | yes | no | 484,186 chars |
    | `BL-2` | yes | yes | 2,073 chars |
    | `BL-3` | yes | yes | 4,178 chars |
    | `EC-1` | yes | no | 3,897 chars |
    | `EC-3` | yes | no | 217 chars |
    | `EC-6` | yes | no | 13,187 chars |
    | `OP-4` | yes | no | 438,506 chars |
    | `SC-1` | yes | no | 116,783 chars |
    | `SC-2` | yes | no | 17,203,733 chars |
    | `SC-3` | yes | no | 663,987 chars |
    | `SC-4` | yes | no | 33,122 chars |

    The interpreted track reported truncation in 54 of 55 runs. The raw track reported
    truncation in 16 of 55 runs. The divergence isn't a measurement error, but reflects the
    [truncation taxonomy](friction-note.md#truncation-taxonomy). The interpreted track is detecting
    `fetch_webpage`'s relevance-ranked excerpting and correctly identifying that the full page
    wasn't returned. The raw track is measuring the saved file, which on `curl` substitution
    runs is complete and byte-perfect. Both are right about what they're measuring, but _they're
    measuring different things_.

2. **Output size difference reflects mechanism, not content**

    The `SC-2` divergence ~17,203,733 chars - is the most extreme in the dataset and
    illustrates why averaging across mechanisms is misleading. The interpreted track received
    relevance-ranked excerpts from `fetch_webpage` averaging ~13,000 chars. The raw track
    received complete files via `curl` averaging ~17 million chars across 5 runs. These aren't
    two measurements of the same thing; they're _two different retrieval mechanisms producing
    fundamentally different outputs on the same URL_.

3. **`fetch_webpage` and `curl` produce non-comparable results**

    The raw track's average output size ~ 787,084 chars, is dramatically higher than the
    interpreted track's ~ 29,239 chars because `curl` substitution runs deliver complete HTML
    files while `fetch_webpage` runs return relevance-ranked excerpts. Within the raw track,
    `fetch_webpage` runs and `curl` runs are themselves not comparable. The `tools_used` field
    is currently the only mechanism for separating these populations after the fact.

4. **Copilot's truncation self-report is unreliable**

    On the interpreted track, the model correctly identifies that content is incomplete in
    54 of 55 runs, but misattributes the cause, flagging `fetch_webpage`'s architectural
    excerpting as truncation rather than a design property of the tool. On the raw track,
    the model reports no truncation in most `curl` runs, which is accurate for file
    completeness, but misses that the delivered format is unusable. "No truncation reported"
    appears in all truncation categories documented in
    [the Friction Note](friction-note.md#truncation-taxonomy).

5. **Token estimation accuracy differs by track and model**

    The interpreted track doesn't produce a raw output file, so Copilot derives from whatever
    `fetch_webpage` returned as a relevance-ranked subset. The raw track saves the raw output file,
    but token estimation methodology varies: chars/4 heuristic undercounts HTML-dense content,
    word count substitution produces ~5x undercount on some runs, and Node regex tokenization
    differs from `cl100k_base` by ~27 tokens on Markdown content. The verification script's
    `cl100k_base` count is the only consistently reliable figure across both tracks.

6. **Hypotheses largely not testable as designed**

    The hypothesis framework assumes a conventional retrieval pipeline: an agent fetches
    a URL, content passes through a size ceiling, the model receives a truncated-but-sequential
    result. **Copilot's behavior doesn't fit this model**. `fetch_webpage` performs relevance-ranked
    excerpt assembly with no detectable fixed ceiling, which rules out `H1` and `H2` as the primary
    mechanism. `curl` substitution delivers complete files with no truncation at all, making `H1`
    vacuously false for those runs. `H3` - structure-aware truncation isn't testable when the
    retrieval mechanism is unknown at run time. `H4` - MCP servers override native limits and
    `H5` - agent auto-chunks after truncation, weren't observable because the substitution behavior
    itself was the finding. The analyzer script returned `H1-yes` in 60 of 110 combined runs, but
    those results reflect three different underlying phenomena: architectural excerpting, complete
    retrieval, and chat rendering cutoff, which the hypothesis framework wasn't designed to
    distinguish. The hypotheses remain in the dataset as logged fields, but the primary finding
    is that Copilot's retrieval behavior _requires a different analytical frame than the one the
    hypotheses assumed_.

---

## Implications for Agent Developers

The tool used matters more than the prompt, model, or URL. `fetch_webpage` and `curl` produce outputs
so different in character that runs using different mechanisms aren't replicates of the same condition -
even when the URL, model, and prompt are identical. The raw track can confirm which mechanism ran by
checking the saved file and `tools_used` field. The interpreted track can't; the model's self-report is
the only signal, and it isn't reliable. Cross-referencing both tracks is the only way to separate what
Copilot retrieved from what it understood about what it retrieved.

| **Use Case** | **Interpreted Track** | **Raw Track** |
| --- | --- | --- |
| **Retrieval Mechanism Identification** | ✗ Mechanism not<br>reliably surfaced | ✓ `tools_used` field and headers files identify `fetch_webpage` <br>vs `curl` |
| **File Integrity Verification** | ✗ No saved file;<br>model estimates only | ✓ MD5 checksums, byte counts, hexdump tail analysis |
| **Format<br>Classification** | _Partial_ - model describes output format in prose | ✓ Verification script detects HTML vs Markdown vs JSON from saved file |
| **Ground Truth Baselines** | ✗ Self-report only | ✓ What Copilot actually saved vs what the model claims |
| **Model<br>Perception Gaps** | ✓ Reveals misreporting of completeness and cause | _Partial_ - verifier confirms file integrity but<br>not model's interpretation |
| **`fetch_webpage` Behavior Characterization** | ✓ Relevance-ranking, elision patterns, non-linear reassembly visible in chat | _Partial_ - file reflects tool output but internal query parameters not surfaced |
| **Tool Substitution Detection** | ✓ Model reasoning sometimes reveals `curl` preference explicitly | ✓ `tools_used` field confirms mechanism; headers files corroborate |
| **User-facing Experience** | ✓ Reflects what a developer interacting with Copilot actually sees | ✗ Saved file diverges from chat display <br>on over-delivery runs |
