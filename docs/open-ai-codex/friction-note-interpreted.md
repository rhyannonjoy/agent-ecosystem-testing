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
<br>`GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`, `GPT-5.4`, and `GPT-5.5` each available at four intelligence levels `Low`,
`Medium`, `High`, and `Extra High`. Coverage of the matrix produces 20 runs per test ID compared to this
collection's standard five.

The combinatorial cost produces more overhead, but collapsing the matrix introduces a different problem. Intelligence
level isn't a passive configuration, but materially changes retrieval strategy, tool selection, runtime, and in some
cases output quality. `GPT-5.2` required `High` intelligence to escalate to `curl` while `GPT-5.4` did so at `Low`.
`GPT-5.4-Mini Extra High` spent 85 seconds on a three-part fetch strategy that produced the same yield as a 24-second
single-fetch at `Medium`. Sampling one or two levels per LLM would have missed these divergences entirely.

[Codex's documentation](https://developers.openai.com/api/docs/guides/latest-model) offers a relevant caution about
intelligence levels, stated for `GPT-5.5` but applicable generally:

> _"Higher reasoning effort isn't automatically better. If the task has conflicting
> instructions, weak stopping criteria, or open-ended tool access, higher effort can lead
> to overthinking, unnecessary searching, or output quality regressions. Increase effort
> only when evals show a measurable quality gain."_

`BL-1` data confirms this empirically. `Extra High` produced cost/yield regressions in both `GPT-5.4-Mini` and
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

## Mixed-Format Source Misidentification, Tool Selection Driver

`BL-2`'s URL leads to a mixed-format file with Markdown text and HTML tags. This pattern was previously observed in
[Cascade-interpreted track testing](../cognition-windsurf-cascade/friction-note-interpreted.md#mixed-format-source-misidentified),
where it produced reporting errors as agents flagged format anomalies in their completeness assessments.
Codex's response to `BL-2` uncovered that misidentification didn't just corrupt the report, it actively drove
tool selection with measurable cost consequences.

The clearest instance was `GPT-5.4-Mini` `Extra High`, which attempted `Browser Use` after determining the
content was _"buried inside a large HTML document."_ The agent read the embedded HTML table tags as evidence
that it needed a browser rendering pass to extract the real content, which led to `net::ERR_BLOCKED_BY_CLIENT`.
The run then fell back to `curl`, which retrieved the same 6,024-char plain-text Markdown body that most runs
returned, in under a minute, at a fraction of the cost. The `Browser Use` attempt consumed 63K context tokens.
The misidentification added no retrieval value and introduced a tool failure that didn't need to happen.

A subtler version appeared in `GPT-5.4` `Low`, which reported truncation while simultaneously confirming clean
code fence closure and the correct character count. The sole evidence for truncation was the ~20 KB size expectation
vs the 6,024-char actual. That expectation was itself inflated by the mixed format: an agent encountering HTML
table markup inside a `.md` file may model the source as a rendered page with nav chrome rather than a compact raw
document, producing a larger prior on document size and a lower threshold for declaring the retrieval incomplete.

Across runs, the `ce-create## Summary` heading artifact and the embedded HTML table agents flagged as toolchain
corruption, parsing failure, or CMS injection. No agent identified these as stable source properties. Without access
to the raw source for cross-reference, the misidentification isn't recoverable from agent output alone.

### Methodology Decision

Cross-reference agent truncation and formatting assessments against the known source structure before logging. A false
positive truncation report driven by format mismatch is a distinct finding from a true retrieval ceiling. Where
misidentification produces tool escalation, not just a bad report, log the escalation path and its context cost as a
direct consequence of the source format property.

---

## `SC-2` Cross-Ecosystem Divergence

`SC-2` targets [a live Anthropic endpoint](https://docs.anthropic.com/en/api/messages) that issues a redirect. The
destination serves a Next.js client-rendered app shell with nonce-gated scripts and
`cache-control: no-cache, no-store, must-revalidate`. No agent received the Messages API reference body. The shell
contained nav scaffolding, inline scripts, and JSON bundles, but no readable documentation text.

Most `GPT`-series agents handled this redirect cleanly and consistently. Most runs that attempted `curl` or `web.open`
acknowledged the `301` and named the destination correctly. No agent characterized the redirect as failure attributable to
its own toolchain. Agents treated the redirect as a server property, noted, and incorporated into the two-path fetch strategy
most runs adopted by `Medium` intelligence level or higher.

[Cascade agents handling the same URL produced a materially different pattern](../cognition-windsurf-cascade/friction-note-interpreted.md#read_url_content-internal-url-rewriting).
Agents cited divergent redirect destinations, characterized the behavior as a `read_url_content` internal URL rewriting bug,
and in the clearest case, `SWE-1.6` identified the mechanism as tool-layer path substitution pre-network call rather than a `301`.

The `GPT` data doesn't entirely resolve that question either, but it does narrow it. `GPT` agents received redirect metadata in their
tool output and acted on it correctly, which is consistent with `read_url_content` making the network call, receiving the redirect,
and naming the destination. That pattern fits server-side redirect behavior more cleanly than silent pre-network URL substitution.
The Cascade characterization may reflect a difference in how `read_url_content` reports redirect information to different agent
contexts rather than a difference in the underlying network behavior.

### Truncation Consensus

`SC-2`'s URL is a stress test for size, as it
[led Cascade agents to Anthropic's full docs corpus](../cognition-windsurf-cascade/friction-note-interpreted.md#read_url_content-internal-url-rewriting).
The outcome instead produced a cross-ecosystem finding about `GPT` truncation reporting consistency.

`GPT` agents converged on the same characterization: `curl` returns a structurally complete HTML shell,
`web.open` returns a fixed 142-line extraction window that ends at the footer boundary. Different LLM variations
at different intelligence levels agreed on this framing with very little difference.

[Cascade agents across testing cycles reported truncation very differently](../cognition-windsurf-cascade/friction-note-interpreted.md#truncation-taxonomy) -
different truncation states, different redirect paths, and characterized failure modes differently across sessions.
The cross-agent consensus in `GPT` runs versus the cross-agent disagreement in Cascade runs is a meaningful signal
about how each ecosystem identify tool output to agent context. `GPT` agents may receive more consistent, structured
tool metadata, including redirect status and response size, enabling convergent self-reporting even when the underlying
content is identical. Cascade agents may simply fail louder. <br>`SC-2` testing anticipated hard error codes and Codex's
much more opaque thought panel reasoning may obscure those.

### Methodology Decision

Log the `docs.anthropic.com` → `platform.claude.com` redirect as a confirmed server-side `301` based on `GPT`-track header
evidence from run 8, which captured the full HTTP response chain. Treat Cascade's tool-layer rewriting characterization as
an agent hypothesis, not a confirmed finding, consistent with the existing redirect section's framing. Where future runs
against this URL produce divergent redirect descriptions across agents or ecosystems, treat the divergence as a signal about
tool output consistency or failure recovery, rather than a signal about the URL's behavior.

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

`BL-2` results suggested wider contamination as session folders created on the same date, with artifact files present in
non-sequential sessions: `web-2`, `web-3`, `web-4`, `web-7`, `web-10`, `web-12`, `web-13` and empty folders for
`web-5`, `web-6`, `web-8`, `web-9`, and `web-11`. The gap pattern doesn't correspond to intelligence level order, ruling
out sequential contamination as the sole mechanism. Run 14 also reported a workspace path from session `i-m-testing-codex-s-web-11`
during what should have been a fresh `-web-14` session.

`SC-2` agents report access to `private/tmp` and appear to read `/codex-browser-use`, possibly expecting skill content that no prior
run had populated. It's more likely that these aren't agent-initiated reads. `/tmp/codex-browser-use` is the Codex Desktop app's
IPC, inter-process communication socket path for its `Browser Use` backend, initialized at launch regardless of whether the prompt
includes `@Browser`. The app touches this directory, not the agent. Attributing the empty read to agent preparation behavior
misidentifies infrastructure activity as agentic intent. Affected runs should be re-examined for whether the missing browser skill
context hypothesis holds if the agent never issued the read.

### Methodology Decision

Run each intelligence level in a fresh Codex session. Where session isolation is impractical, run levels in ascending order to
ensure at least the `Low` run's uncontaminated, and flag all subsequent runs in the same session with a contamination qualifier.
Log empty skill directory reads as a contamination-adjacent event distinct from artifact reuse and flag affected runs accordingly.
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
reporting truncation in the other layers. At least one later run confirmed the terminal display truncation layer as observable:
`OP-4`'s `GPT-5.4 Extra High` produced an explicit `…124,675 tokens truncated…` marker in tool output mid-stream, with
the saved file confirmed complete.

`OP-1` run 16 introduced a type of pagination-completion false negative. The agent successfully paginated `web.open` output
to `L1863` and reported no truncation, reasoning that the full document was accessible. Technically accurate on one level, but
misleading as a truncation assessment. `OP-1` `web.open` calls only returned a windowed slice, never retrieving the document
as a contiguous payload.

Three-layer truncation has a practical implications for hypothesis assessment. `H1` and `H2` character and token ceilings
are only testable against the HTTP response body layer. Assessments made against `web.open` output measure the viewer window,
not the retrieval ceiling. Runs that didn't escalate to `curl` can't meaningfully contribute to `H1` or `H2` verdicts
with the same confidence as runs that did.

### Methodology Decision

Treat `web.open` output and `curl` output as measurements of different artifacts within the truncation taxonomy, not as better or
worse versions of the same measurement. A `web.open`-only run documents default retrieval behavior for that LLM and intelligence
level. A `curl`-escalated run documents what the agent does when it reasons past the default. Both are valid observations. The
distinction is already recoverable from the tools named column without additional logging.

---

## `web.open` Line-Indexed Viewer

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

This suggests that `web.open`-only runs may not be retrieving a truncated version of the page so much as a different artifact entirely,
a rendered text view optimized for readability rather than byte-faithful retrieval. The `~85 KB` ceiling observed in
<br>`GPT-5.4-Mini Medium/High/Extra High` may reflect the approximate size of that readable content layer rather than an infrastructure
retrieval limit. `SC-2` produced a precise internal structure map of a `web.open` 142-line extraction window:

| **Zone** | **Lines** | **Content** |
| --- | --- | --- |
| **Nav Header** | `L0–L22` | Site navigation, search, login, API reference label |
| **`Loading...` Placeholder Block** | `L23–L84` | Repeated `Loading...` entries, no content |
| **Footer, Nav Links** | `L85–L141` | Solutions, Partners, Company, Terms and policies, Usage policy |

Run 16 mapped the `Loading...` block to `L28–L84`. Run 20 confirmed `Loading...` starts at `L23`. The terminal boundary across all runs was
`Terms and policies → Usage policy`, which multiple agents named explicitly as the last visible content. No agent observed a mid-line cut or
an arbitrary byte boundary within this window.

This structure identifies the 142-line ceiling as a fixed extraction window property rather than a content-driven truncation event. The window
captures a pre-hydration snapshot of the page: the content that exists in the raw HTML before client-side JavaScript executes. The nonce-based
CSP confirmed in run 8's headers file suggests that each script tag carries a per-request nonce that the extractor doesn't hold authorization
to run. The `Loading...` placeholders may not be a retrieval failure, but represent the page's own loading state at the moment of extraction.

`OP-1` confirmed a second document-specific window boundary. The `web.open` extraction consistently terminated at `L552` across
runs 7, 8, 11, 12, 15, 18, and 20, spanning `GPT-5.3-Codex` through `GPT-5.5`. The content landmark at this boundary was stable: the Data
compression section ending on mark for `"general intelligence".[24][25][26]`. The `wordlim: 200` parameter visible in tool metadata across runs
is the likely control variable, with `L305` and `L552` representing consecutive 200-line window positions from the rendered document. The
[URL fragment #History](https://en.wikipedia.org/wiki/Machine_learning#History) was silently stripped by `web.open` on every run, with the tool
returning the full page from `L0` regardless of the fragment target.

`OP-4` added new cutpoints for the [CommonMark Spec](https://spec.commonmark.org/0.31.2/): `L237` as the dominant first-fetch boundary across
`GPT-5.2` through `GPT-5.4`, and `L616` appearing at `GPT-5.5 Extra High` and `GPT-5.4-Mini Extra High`; suggesting the cutpoint as
document and version-correlated rather than fixed; illustrating a type of version axis with lower cutpoints on older LLM versions and
higher on newer.

`OP-2` results offered more architectural precision. Codex's `web.open` is a single-view tool with optional manual pagination. The agent receives
a windowed excerpt and must infer incompleteness from metadata visible in the tool output, primarily the gap between `Total lines: 1269` and lines
actually received. Whether it issues a `lineno` offset call to advance the window depends entirely on whether it notices and acts on that gap.
Pagination is an emergent reasoning behavior, but not an architectural guarantee.

For comparison, [Cascade's retrieval architecture](../cognition-windsurf-cascade/friction-note-interpreted.md#read_url_content---fetch-architecture-parsing-limits)
separates the decision layer from the read layer: a first fetch returns a chunk index with summaries, and the agent decides whether individual chunks
are worth reading based on document size and signal-to-noise. The decision to paginate is structural rather than inferred.

The metric requests likely accelerate `curl` escalation. When prompts ask the agent for character and token counts, `curl` becomes the more
direct path to accurate answers than paginating through rendered text windows. The measurement task may actively displace reading behavior: agents become
more concerned with metric accuracy than content coverage, and `curl` satisfies both requirements in a single fetch. Pagination is most likely to occur
when the agent has no easier path to the numbers.

The practical consequence is that full-document access in Codex is either a reasoning success or a tool substitution, never a default outcome. `web.open`
pagination requires the agent to notice the gap between `Total lines` reported and lines received, and to treat that gap as worth resolving. `curl` requires
only that the agent decides measurement accuracy matters more than the tool it started with.

---

## Workspace Artifact Nondeterminism

`BL-2` agents produced artifacts unprompted, inconsistently. About half wrote files to the local workspace or `/private/tmp`, which
only stores artifacts for a day at a time. Agentic naming was also unstable across sessions and LLM versions:

- `GPT-5.2` `Medium`: `BL-2_create.md.html`
- `GPT-5.2`, `GPT-5.3-Codex` - `High`: `BL-2_create.md`
- `GPT-5.2` `Extra High`: `bl-2-create.md`
- `GPT-5.4`, `GPT-5.5` - `High`: `bl2_create.md`
- `GPT-5.4` `Extra High`: `bl2_mongodb_create.md`
- `GPT-5.4-Mini` `Medium`: `mongo_create.md`
- `GPT-5.4 Extra High`: `bl2_headers.txt` with`.md` artifact

The format also shifted across runs: `GPT-5.2 Medium` saved an HTML extraction while subsequent runs saved Markdown.
`GPT-5.4 Extra High` uniquely saved a separate headers file alongside the content artifact. No run produced the same
filename as another run in the same LLM family without evidence of workspace contamination. Format shifted among the
output as well in which agents produced reports in half-Markdown, some with syntax highlighting, most of it not.

Artifact presence in the chat output was equally inconsistent. Some runs identified the saved file as a clickable attachment
in the Codex response panel, but most didn't, even when the shell log confirmed a successful write. The path disclosed in
surface awareness reports didn't always match the session number - run 14 reported path `i-m-testing-codex-s-web-11` which
should have been `-web-14`.

`OP-4` produced the clearest collision in the dataset: `commonmark-0.31.2.html` used by `GPT-5.4 High` and all `GPT-5.5` runs
across consecutive sessions. Whether each run wrote a fresh file or read a prior artifact is unresolvable on the interpreted track.

This nondeterminism makes artifact presence an unreliable signal for distinguishing fresh retrieval from workspace reads.
A run that skips `web.open` and goes directly to file operations may reflect a trained tool preference, session contamination,
or silent reuse of a prior artifact. Whatever the cause, they produced nearly identical report metrics and observations.

### Methodology Decision

Check `/private/tmp` and the session workspace path at run start before any fetch operations. A non-empty workspace at the start
of a purportedly fresh run is a contamination indicator and log as such. Record artifact filename and format as a contamination
signal for subsequent runs in the same session. Don't treat artifact absence as evidence that no retrieval occurred. The unprompted
write behavior is too inconsistent to use as a retrieval proxy. This is exactly the type of complexity the raw track intends
to test.

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

`GPT-5.5` agents executed no `web` calls at all, going directly to `curl` and local file operations, suggesting that agents may not
be discovering issues fresh. The data alone can't determine whether this reflects `GPT-5.5`'s trained preferences, session-inherited
strategy, or awareness of prior artifacts in the sandbox. The outcome, correct retrieval with terminal tools, is indistinguishable
from learned behavior, session memory, or finding a prior run's cached file.

### Methodology Decision

Log workspace disclosure as a surface characteristic, not a test anomaly. Distinguish passive disclosure from active artifact
creation in the tool visibility field. For runs where measurements derive from sandbox artifacts rather than direct tool output,
document it in the notes column, as the measurement methodology differs from `web.open`-only runs and the two aren't directly
comparable. For fresh-session verification, check whether `/private/tmp` is empty at run start. While a non-empty `/private/tmp` at
the beginning of a purportedly fresh run is a contamination indicator, exclude `codex-browser-use` from the assessment. Its presence
reflects desktop initialization, not a prior agent run's artifact. A non-empty `codex-browser-use` at run start identifies the
deployment surface, but isn't a contamination signal. It's passive evidence of normal app initialization for that run, which is
consistent with genuine fresh session behavior rather than retrieval theater.
