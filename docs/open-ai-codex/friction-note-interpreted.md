---
layout: default
title: "Friction Note"
permalink: /docs/open-ai-codex/friction-note-interpreted
parent: OpenAI Codex
---

# Friction Note: Roadblocks While Refining Methodology

---

## LLM × Intelligence Matrix

Codex exposes a two-dimensional agent configuration space unique among the platforms tested: five LLM variants
<br>`GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-mini`, `GPT-5.4`, and `GPT-5.5` each available at four intelligence levels `Low`,
`Medium`, `High`, and `Extra High`. Coverage of the matrix produces 20 runs per test ID compared to this
collection's standard five.

The combinatorial cost produces more overhead, but collapsing the matrix introduces a different problem. Intelligence
level isn't a passive configuration, but materially changes retrieval strategy, tool selection, runtime, and in some
cases output quality. `GPT-5.2` required `High` intelligence to escalate to `curl` while `GPT-5.4` did so at `Low`.
`GPT-5.4-mini Extra High` spent 85 seconds on a three-part fetch strategy that produced the same yield as a 24-second
single-fetch at `Medium`. Sampling one or two levels per LLM would have missed these divergences entirely.

[Codex's documentation](https://developers.openai.com/api/docs/guides/latest-model) offers a relevant caution about
intelligence levels, stated for `GPT-5.5` but applicable generally:

> _"Higher reasoning effort isn't automatically better. If the task has conflicting
> instructions, weak stopping criteria, or open-ended tool access, higher effort can lead
> to overthinking, unnecessary searching, or output quality regressions. Increase effort
> only when evals show a measurable quality gain."_

`BL-1` data confirms this empirically. `Extra High` produced cost/yield regressions in both `GPT-5.4-mini` and
`GPT-5.3-Codex`: more tool calls, longer runtimes, and identical or lower output quality compared to `Medium` or `High`.
The retrieval task has weak stopping criteria by design. The prompt asks for measurements, not a specific content target.
`web` provides open-ended tool access with no built-in completion signal, risking LLM overthinking.

### Methodology Decision

Log all LLM × intelligence level combinations as distinct rows. The matrix is the unit of observation for Codex testing.
Where session contamination confirmed or suspected, flag affected rows rather than dropping them. The contaminated behavior
is itself a finding about how Codex manages context across runs.

Where full matrix coverage is impractical for a given test ID, prioritize `Low` and `High` per LLM as the most informative
contrast pair. `Low` reflects default or minimal reasoning behavior while `High` captures the escalation threshold without the
`Extra High` overthinking regression. `Medium` and `Extra High` add resolution, but rarely change the verdict.

---

## Session Contamination

Running each intelligence level with an LLM sequentially in the same Codex session in `BL-1` introduced a contamination vector.
Later runs could read artifacts written by earlier runs, observe prior tool outputs in context, and carry forward retrieval
strategies without re-deriving them. Across `GPT-5.4` and `GPT-5.5` runs, three signals co-occurred:

- **Explicit Language** referring to prior runs: _"I'm running the direct fetch again"_,
  _"I'll run a fresh direct fetch for this BL-1 pass"_, phrasing that only makes sense
  if the agent knows it has run before.
- **Anomalous Runtimes**: `GPT-5.5 High` completed in 20 seconds including a `curl`
  fetch of a 505 KB file; `GPT-5.4 Extra High` completed in 42 seconds on the same
  task that took `GPT-5.4 Low` 1 minute and 46 seconds.
- **Increasing Context Window Usage** across levels within the same
  session: `GPT-5.5` consumed 35K → 36K → 38K → 40K tokens across `Low` through
  `Extra High`, consistent with accumulated session state rather than independent runs.

This rules out any possibility of treating intelligence level as an independent variable within shared sessions, as efficiency
gains at higher levels may reflect strategy reuse rather than superior reasoning. The convergence observed across all<br>`GPT-5.4`
levels - identical character counts, token counts, tools, and last-50 characters, is consistent with both genuine LLM stability
and session memory flattening real variance. The data itself can't distinguish these from within the session.

### Methodology Decision

Run each intelligence level in a fresh Codex session. Where session isolation is impractical, run levels in ascending order to
ensure at least the `Low` run's uncontaminated, and flag all subsequent runs in the same session with a contamination qualifier.
Don't interpret runtime compression or strategy convergence at higher levels as evidence of capability without ruling out context
inheritance. Filenames written to the sandbox by earlier runs are a particularly reliable contamination signal: if a later run
references a file it didn't create in its own tool call log, the session likely contaminated.

---

## Truncation Taxonomy

Some platforms presented truncation as a single phenomenon: the tool returned less than the page contained.
`BL-1` runs revealed three distinct truncation layers that operate independently that require disambiguation
before any truncation assessment logging:

| **Layer** | **Mechanism** | **Agent-detectable?** | **Verification-detectable?** |
| --- | --- | --- | --- |
| **`web.open` Viewer Window** | Line-indexed extraction returns a windowed excerpt,<br>not the full page; window may start at `L39` or `L216`<br>and not `L0` | Yes, if agent checks line count vs lines received | Indirectly, via output size vs expected |
| **Terminal Display Truncation** | Tool output printed inline truncated by the Codex transcript interface; `…116,434 tokens truncated…`<br>notice in some runs | Yes, notice visible in tool output | No, hidden tokens not any saved artifact |
| **HTTP Response Body** | Actual bytes received from the server via `curl` | Yes, via `wc -c`<br>on saved file | Yes, via verifier script against known size |

Early `web.open`-only runs conflated all three layers into a single truncation field, producing unreliable
self-reports. `GPT-5.4 Low` was the first run to cleanly separate all three: separating the `web.open` viewer window
from the terminal display truncation from the actual HTTP body, and correctly identified the body as complete while
reporting truncation in the other layers.

The three-layer LLM has a practical implication for hypothesis assessment. `H1` and `H2` character and token ceilings
are only testable against the HTTP response body layer. Assessments made against `web.open` output measure the viewer window,
not the retrieval ceiling. Runs that didn't escalate to `curl` can't meaningfully contribute to `H1` or `H2` verdicts
with the same confidence as runs that did.

### Methodology Decision

Treat `web.open` output and `curl` output as measurements of different artifacts within the truncation taxonomy, not as better or
worse versions of the same measurement. A `web.open`-only run documents default retrieval behavior for that LLM and intelligence
level. A `curl`-escalated run documents what the agent does when it reasons past the default. Both are valid observations. The
distinction is already recoverable from the tools named column without additional logging.

---

## `web.open` Line-Indexed Viewer, Not Raw Fetch

`web.open` doesn't return a raw HTTP response body. It returns a line-indexed, rendered text extraction: a processed view of the page
with line numbers injected, HTML stripped, and a viewer window applied that doesn't necessarily start at line 0. The distinction matters
for every measurement in the interpreted track:

- **Character Counts** from `web.open` include injected line-number prefixes, inflating
  the count relative to the actual content.
- **Viewer Window** starts at an arbitrary line offset, observed at `BL-1`'s `L39` and `L216` in
  different runs, meaning `web.open`-only runs may return a mid-document slice with no
  skipping signal for previous content.
- **Line Count** - agents consistently reported `Total lines: 542`, but it's a property of the
  extracted text representation, not the raw HTML.
- **Truncation at `L477`** appeared across `GPT-5.2 Medium`, `GPT-5.3-Codex High`, and
  `GPT-5.3-Codex Extra High`. Whether this is a hardcoded viewer window limit, a
  pagination boundary, or a property of the document's line structure at that point
  isn't resolvable from interpreted track data alone; the raw track write task is
  the appropriate place to test this.

`GPT-5.4 Low` offered the clearest documentation of this finding:

> _"`web.open` did not return the raw 505 KB page body. It returned a line-extracted,
> partially normalized page view (`Total lines: 542`) centered on readable content,
> while a direct terminal fetch returned the full HTML."_

This suggests that `web.open`-only runs may not be retrieving a truncated version of the page so much as a different artifact entirely, a
rendered text view optimized for readability rather than byte-faithful retrieval. The `~85 KB` ceiling observed in
<br>`GPT-5.4-mini Medium/High/Extra High` may reflect the approximate size of that readable content layer rather than an infrastructure retrieval
limit. Subsequent test cycles may determine whether this holds across other URLs and page types.

---

## Workspace Sandbox Bleed

All `BL-1` runs acknowledged access to a local workspace or filesystem. The disclosed path was consistent across sessions:
`/Users/rhyannonjoy/Documents/Codex/2026-05-09/i-m-testing-codex-s-web-2`.

Direct inspection confirmed the sandbox exists but is empty. Agents weren't lying: the sandbox is a session-scoped
environment with read/write capability. The prompt condition _"no workspace"_ describes the absence of this test collection's
project files, not the absence of the sandbox itself. The gap is between the framework's intent and the Codex environment's
actual configuration. The bleed takes two forms with different implications:

**Passive Bleed**: agents report sandbox access but don't use it. All `web.open`-only runs fall here. The disclosure is accurate
and doesn't affect retrieval behavior.

**Active Bleed**: agents write artifacts to `/private/tmp` or the sandbox path during retrieval, then read those artifacts to
compute measurements. `GPT-5.2 High` and `Extra High`, `GPT-5.4` across all levels, and `GPT-5.5` across all levels used this
pattern. The artifact-then-measure approach produces more accurate character counts than reading from tool display output, but it
also means later runs in the same session may find artifacts from earlier runs in the sandbox, compounding
[the session contamination problem](#session-contamination).

A subtler form appeared in the `GPT-5.5` runs: the agents executed no `web` or `web.open` calls at all, going directly to `curl`
and local file operations. The data alone can't determine whether this reflects `GPT-5.5`'s trained preferences, session-inherited
strategy, or awareness of prior artifacts in the sandbox. The outcome, correct retrieval with terminal tools, is indistinguishable
from learned behavior, session memory, or finding a prior run's cached file.

### Methodology Decision

Log workspace disclosure as a surface characteristic, not a test anomaly. Distinguish passive disclosure from active artifact creation
in the tool visibility field. For runs where measurements derive from sandbox artifacts rather than direct tool output, document it in
the notes column, as the measurement methodology differs from `web.open`-only runs and the two aren't directly comparable. For fresh-session
verification, check whether `/private/tmp` is empty at run start; a non-empty `/private/tmp` at the beginning of a purportedly fresh run is
a contamination indicator.
