---
layout: default
title: "Copilot-interpreted vs Raw"
permalink: /docs/microsoft-github-copilot/copilot-interpreted-vs-raw
parent: Microsoft GitHub Copilot
---

## Copilot-interpreted vs Raw

Two test tracks measure the same Copilot web fetch behaviors:

**Copilot-interpreted** track captures what the model _believes_ it retrieved: how much
content it saw, whether the fetch was complete, how it characterizes truncation. This is
the model's self-report.

**Raw** track captures what Copilot _actually saved to disk_: exact byte counts, hexdump
analysis, MD5 checksums, and token counts measured by the verification script against the
saved file, not the model's estimate.

The gap between these two tracks is itself a finding. If Copilot reports "no truncation"
in chat but the raw data shows a relevance-ranked excerpt, that discrepancy belongs in the
findings. If Copilot reports "no truncation" and the raw data confirms a complete file,
but the file is raw HTML with no readable content, that's a different kind of discrepancy.

| | Interpreted Track | Raw Track |
| - | ---------------------- | -------------------------- |
| **Measures** | Model's interpretation of what it fetched | Filesystem measurements of saved output |
| **Character Counts** | Model estimates; range-reported or heuristic | `wc -c` on disk - exact, reproducible |
| **Completeness** | Model's prose assessment of truncation | MD5 comparison, hexdump analysis, verification script |
| **Token Counts** | Model estimates; chars/4 heuristic, word count substitution, or Node regex | `cl100k_base` - exact tokenizer |
| **Reproducibility** | High variance; same URL and model can produce 2x difference | Byte-identical within same file version; different versions detectable by MD5 |
| **Output Format** | Chat UI rendering | Raw file on disk, `raw_output_{test_id}.txt` |
| **Best For** | Understanding model perception gaps and `fetch_webpage` behavior | Citable measurements; retrieval mechanism identification |

---

## Key Observations

1. **Tracks disagree on truncation**

    The analyzer flagged divergence on truncation status across 8 of 11 test IDs:

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
    runs is complete and byte-perfect. Both are right about what they're measuring, but they're
    measuring different things.

2. **Output size difference reflects mechanism, not content**

    The `SC-2` divergence, 17,203,733 chars - is the most extreme in the dataset and
    illustrates why averaging across mechanisms is misleading. The interpreted track received
    relevance-ranked excerpts from `fetch_webpage` averaging ~13,000 chars. The raw track
    received complete files via `curl` averaging ~17 million chars across 5 runs. These aren't
    two measurements of the same thing; they're two different retrieval mechanisms producing
    fundamentally different outputs on the same URL.

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
    appears in all three truncation categories documented in
    [the Friction Note](friction-note.md#truncation-taxonomy).

5. **Token estimation accuracy differs by track and model**

    The interpreted track has no access to the actual file, so Copilot derives from whatever
    `fetch_webpage` returned as a relevance-ranked subset. The raw track has the complete file,
    but token estimation methodology varies: chars/4 heuristic undercounts HTML-dense content,
    word count substitution produces ~5x undercount on some runs, and Node regex tokenization
    differs from `cl100k_base` by ~27 tokens on Markdown content. The verification script's
    `cl100k_base` count is the only consistently reliable figure across both tracks.

6. **Hypothesis H1 result differs by track**

    The interpreted track returned `H1-yes` in 54 of 55 runs because the model received less than
    the full page. The raw track returned `H1-yes` in only 16 of 55 runs because the saved file was
    flagged as truncated. Tool use explains this difference: `curl` substitution runs produce
    complete files, so the raw track verifier finds no truncation indicators, while the interpreted
    track model received excerpts from `fetch_webpage` and correctly flagged them as incomplete.
    `H1-yes` on the interpreted track means "the model didn't receive the full page." `H1-yes` on the
    raw track means "the saved file contains truncation indicators." These are different claims.

---

## Implications for Agent Developers

| **Use Case** | **Interpreted Track** | **Raw Track** |
| --- | --- | --- |
| Retrieval mechanism identification | ✗ mechanism not reliably surfaced | ✓ `tools_used` field and headers files identify `fetch_webpage` vs `curl` |
| File integrity verification | ✗ no saved file; model estimates only | ✓ MD5 checksums, byte counts, hexdump tail analysis |
| Format classification | Partial - model describes output format in prose | ✓ verification script detects HTML vs Markdown vs JSON from saved file |
| Ground truth baselines | ✗ self-report only | ✓ what Copilot actually saved vs what the model claims |
| Model perception gaps | ✓ reveals misreporting of completeness and cause | Partial - verifier confirms file integrity but not model's interpretation |
| `fetch_webpage` behavior characterization | ✓ relevance-ranking, elision patterns, non-linear reassembly visible in chat | Partial - file reflects tool output but internal query parameters not surfaced |
| Tool substitution detection | ✓ model reasoning sometimes reveals `curl` preference explicitly | ✓ `tools_used` field confirms mechanism; headers files corroborate |
| User-facing experience | ✓ reflects what a developer interacting with Copilot actually sees | ✗ saved file diverges from chat display on over-delivery runs |

> **Critical takeaway**: the tool used matters more than the prompt, model, or URL.
> `fetch_webpage` and `curl` produce outputs so different in character that runs using different mechanisms
> can't be treated as replicates of the same condition. The interpreted track sees only
> `fetch_webpage` output. The raw track sees both, mixed non-deterministically. Neither
> track alone is sufficient to characterize Copilot's web fetch behavior;
> cross-referencing both is the only way to separate retrieval mechanism from retrieval
> quality.

---

## Platform Architecture Comparison

| **Step** | **Copilot-interpreted** | **Copilot Raw** |
| --- | --- | --- |
| **Retrieval** | `fetch_webpage` invoked; model receives relevance-ranked excerpt | `fetch_webpage` or `curl` invoked; mechanism not disclosed in chat |
| **Content** | Relevance-ranked Markdown excerpts with `...` elision markers | Raw bytes in server format - HTML, JSON, or Markdown - depending on mechanism |
| **Completeness Signal** | Model flags `...` markers and section gaps as truncation | Verification script checks file size, MD5, hexdump tail, truncation indicators |
| **Token counts** | Heuristic estimate from excerpt; underreports actual page size | `cl100k_base` on saved file; reflects actual content type density |
| **Reproducibility** | High variance; same URL and model produce 2x difference across runs | Byte-identical within same file version on `curl` runs; `fetch_webpage` runs vary |
| **Key Finding** | `fetch_webpage` excerpting is architectural, not suppressible by prompt | Tool substitution is the primary variable; `curl` produces complete but unusable output |
