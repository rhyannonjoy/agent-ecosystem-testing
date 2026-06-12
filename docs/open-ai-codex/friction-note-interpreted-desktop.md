---
layout: default
title: "Friction: Interpreted (Desktop)"
permalink: /docs/open-ai-codex/friction-note-interpreted-desktop
parent: OpenAI Codex
---

# Friction Note: Roadblocks While Refining Methodology

---

## Agentic Reasoning-Report Integrity

`SC-4`'s `GPT-5.4-Mini Extra High` demonstrated a gap between thought panel reasoning and visible output.
The thought panel showed the agent reasoning through Playwright, `xmllint`, `lynx`, `w3m`, `pup`, `htmlq`,
and `tiktoken` as candidate tools, attempting and discarding each before settling on `curl`. The output
panel showed only the successful `curl` result. Without the thought panel, the run would appear as a
straightforward single-tool fetch. The effort, the failure chain, and the escalation logic were invisible
in the report.

This is a general limitation of post-hoc output as an observability surface, and it is more acute
on Codex than on other platforms tested in this collection. GitHub Copilot and Windsurf Cascade
agents expose substantially more turn-by-turn reasoning: tool calls, intermediate results, and
decision branches are visible as they occur, generally making an agent's path reconstructable after the
fact. Codex's thought panel is comparatively opaque, closer to Cursor's style with reasoning visible only
intermittently and incompletely. Agent reports describe what succeeded. What the agent tried, reconsidered,
and abandoned is largely implicit and unrecoverable from output alone.

For hypothesis testing, the rejected paths are often as informative as the one taken. A run that attempts
five tools and falls back to `curl` is behaviorally distinct from a run that goes directly to `curl`, even
if both produce identical metrics. The opacity means that distinctiveness is only visible when the thought
panel happens to expose it, which is inconsistent and not something the methodology can rely on.

Platform updates compound this problem. The Codex desktop app `v26.519.31651 (3017)` has removed the default
context window usage counter. Previously, the counter provided a direct scalar measure of agent effort: token
consumption per run was a proxy for reasoning depth, tool churn, and session contamination accumulation. Runtime
in seconds is now the only remaining effort indicator, and it conflates network latency, tool execution time, and
reasoning depth in a way the context counter didn't. On a platform where reasoning is already difficult to observe,
losing an effort proxy has an outsized impact relative to what the same loss would mean on a more transparent surface.

### Methodology Decision

Capture thought panel reasoning at run time rather than relying on the output panel alone. Where platform updates
remove previously available signals such as the context window counter, note the version at which the signal disappeared
and flag affected runs. Surface observability isn't stable across the test cycle, and on an already opaque platform, each
lost signal has proportionally higher cost to the methodology than it would elsewhere.

---

## Autonomous Post-Hoc Session Alterations

Codex default settings continue processing session output after run completion and archival placement. Across recent
desktop versions, a few signals pose data integrity risks in the form of:

- **Output Editing**: at least one run produced a double report where the two instances
  described `web` tool behavior differently; one acknowledged truncation by design, the
  other omitting it entirely. A later batch-logging pass found the double report resolved to
  a single output, with the `web` limitation observation absent.
- **Thought Panel Collapse**: command execution dropdown windows are only visible in real time.
  The remaining reasoning summary condenses failures, escalation logic, and rejected paths -
  the signals most useful for hypotheses assessment.
- **Timer Drift and/or Removal**: real-time observations captured in screenshots show different elapsed times
  than what the app displays for the same run after the fact. `GPT-5.2` timers are completely absent from
  chats post-session.

Character counts, token estimation, and toolchain reporting appear somewhat more stable across this process. While these
edits include numeric metrics, agentic effort through time, they also impact qualitative components such as prose framing,
report structure, and strategy characterization. While most measurements may be reliable, the reasoning and self-reporting
around them isn't. As a control measure, testing conditions include disablement of `Auto-review` and `Full access` settings.
These mechanisms aren't visible in the thought panel, agents don't report the edits. Whether either setting drives this
particular behavior remains unconfirmed.

### Methodology Decision

Treat screenshot capture at run time as the primary record for agent reasoning, tool characterization, and truncation self-reporting.
Cross-reference logged output against screenshots and observe for discrepancies. Note the Codex app version at the time of capture,
as platform updates may change what gets swept and what doesn't.

> _[Friction: Extension](friction-note-interpreted-extension.md#autonomous-post-hoc-session-double-rendering) recontextualizes this topic for `T2`_

---

## Hypotheses Unreachability

`EC-1`'s [Gemini API documentation](https://ai.google.dev/gemini-api/docs) was intended to stress-test retrieval behavior
on a page that `web` can't fully render. Most agents didn't traverse with `web` long enough to produce useful data. The
dominant pattern across all LLM versions was call `web.run open( {"ref_id": "[ URL ]", "lineno": [ int ]} )`, note the extracted
view, escalate to `curl`. `H1`-`H3` are only accurately testable against `web` output. Runs that escalated confirmed the raw fetch
ceiling wasn't hit, but that's a different question than whether the in-house retrieval surface has a ceiling.

Three of four `GPT-5.5` runs bypassed the `web` pipeline entirely. The measurement task may accelerate this. When the prompt
asks for character counts and token estimates, `curl` is a more direct path to numbers than paginating through a rendered text
window. The prompt design may be actively displacing the retrieval behavior the test is trying to observe.

`EC-3`'s redirect to a 660-char JSON body largely didn't support any hypotheses and wasn't explicitly designed to. Its value is
as a floor case, a payload well below any suspected ceiling - and perhaps exposed behavior that tests with larger content sizes
may obscure. Toolchain selection at minimum effort varied more than expected across LLM versions: most runs defaulted to
`web`-`Node REPL`, but `GPT-5.2 Medium` and `GPT-5.5 High` bypassed the `web` pipeline entirely for `curl` without a size-driven
reason to do so. `GPT-5.4-Mini Low` went `web`-only while `GPT-5.4-Mini Extra High` spent 2 minutes 33 seconds on the same payload
with `tiktoken` probing and dual `tokenizer` estimates. Neither produced more enriched reports than the other. Agents repeatedly
acknowledged expected vs received size discrepancies and though less often, corrected the prompt's `web.open` reference.
Neither [Cursor](../anysphere-cursor/friction-note.md#agent-as-unreliable-methodology-validator) or
[Cascade](../cognition-windsurf-cascade/friction-note-explicit.md#agent-as-unreliable-methodology-validator) agents made an effort
to correct method references and/or general misuse.

### Methodology Decision

For SPAs and/or JavaScript-heavy URLs, consider a two-prompt design: a first run asking the agent to describe what the retrieval
surface returned without escalating, and a second run asking for measurement. Combining both goals in a single prompt favors `curl`
escalation over `web` boundary examination. With that said, lack of hypotheses support isn't always a reason to explicitly change
testing conditions, but may offer an opportunity to change perspective to gather details less visible across other test cycles.

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

`EC-1`'s `GPT-5.2 Extra High` spent 48 minutes and 10 seconds searching with `web` 113 times and triggered context auto-compaction
mid-run. The agent measured the same `web` buffer repeatedly across both halves of the compacted session: approximately
13,383 chars and 3,346 tokens, confirmed again and again without producing new information. No error messages were visible
in the thought panel. While other agents in the same test cycle successfully pivoted to `Browser` or `curl`, this agent didn't
expose explicit struggle beyond unproductive spinning.

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

> _`T2` results produced this pattern at reduced cost; analysis in [Friction: Interpreted - Extension](friction-note-interpreted-extension.md#mixed-format-source-misidentification-tool-selection-driver)_

---

## `SC-2` Cross-Ecosystem Divergence

`SC-2` targets [a live Anthropic endpoint](https://docs.anthropic.com/en/api/messages) that issues a redirect. The
destination serves a Next.js client-rendered app shell with nonce-gated scripts and
`cache-control: no-cache, no-store, must-revalidate`. No agent received the Messages API reference body. The shell
contained nav scaffolding, inline scripts, and JSON bundles, but no readable documentation text.

Most `GPT`-series agents handled this redirect cleanly and consistently. Most runs that attempted `curl` or `web`
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
`web` returns a fixed 142-line extraction window that ends at the footer boundary. Different LLM variations
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

> _[Friction: Extension](friction-note-interpreted-extension.md#web-line-ceiling) reinforces these observations_

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
| **`web` Viewer Window** | Line-indexed extraction returns windowed view, not full page; may not start at `L0` | _Yes_: if agent checks line count vs lines received | _Indirectly_: output size vs expected |
| **Terminal Display Truncation** | Codex renderer clips output -<br>`OP-4`:`…116,434 tokens truncated…` `EC-6`:`…12970 tokens truncated…` | _Yes_: notice visible in tool output | _No_: hidden tokens not saved |
| **HTTP Response Body** | Bytes received from<br>server via `curl` | _Yes_: `wc -c` on saved file | _Yes_: verifier script against known size |
| **Wrong Resource Returned** | Server returns complete HTML doc without `200`; passes checks, but not target content | _Yes_: status code; not reliably acted on; `BL-3`'s `GPT-5.4-Mini High` identified `404` explicitly, but assessed payload as complete, possible mid-testing outage | _Yes_: headers status code |

`SC-1` agents consistently acknowledged that `web` returned an extraction rather than a raw response, and reasoned
toward `curl`, but didn't classify the extraction as truncation. The framing used across runs described the `web` result
as a _rendered text view_, _line-numbered extraction_, or _normalized content_, treating it as a different artifact from the
target rather than an intentionally truncated version of it. While technically accurate, it produces a systematic gap in
self-reporting. An agent can correctly describe `web` limitations, escalate to `curl`, and still log `No truncation`
because they commonly prioritized the `curl` results.

Early `BL-1` `web`-only runs conflated all three layers into a single truncation field, also producing unreliable
self-reports. `GPT-5.4 Low` was the first run to cleanly separate all three: separating the `web` viewer window
from the terminal display truncation from the actual HTTP body, and correctly identified the body as complete while
reporting truncation in the other layers. At least one later run confirmed the terminal display truncation layer as observable:
`OP-4`'s `GPT-5.4 Extra High` produced an explicit `…124,675 tokens truncated…` marker in tool output mid-stream, with
the saved file confirmed complete.

`OP-1` run 16 introduced a type of pagination-completion false negative. The agent successfully paginated `web` output
to `L1863` and reported no truncation, reasoning that the full document was accessible. Technically accurate on one level, but
misleading as a truncation assessment. `OP-1` `web` calls only returned a windowed slice, never retrieving the document
as a contiguous payload.

Three-layer truncation has a practical implications for hypothesis assessment. `H1` and `H2` character and token ceilings
are only testable against the HTTP response body layer. Assessments made against `web` output measure the viewer window,
not the retrieval ceiling. Runs that didn't escalate to `curl` can't meaningfully contribute to `H1` or `H2` verdicts
with the same confidence as runs that did.

### Methodology Decision

Treat `web` output and `curl` output as measurements of different artifacts within the truncation taxonomy, not as better or
worse versions of the same measurement. A `web`-only run documents default retrieval behavior for that LLM and intelligence
level. A `curl`-escalated run documents what the agent does when it reasons past the default. Both are valid observations. The
distinction is already recoverable from the tools named column without additional logging.

---

## URL Instability Mid-Testing

[`BL-3` URL](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/) intermittenly returned a `404` but is back up, indicating
a temporary outage or maintenance window rather than a permanent migration. The `404` pattern appearing in `GPT-5.4-Mini` `Medium`,
`High`, and `Extra High` runs, and possibly `GPT-5.2 Low`, is consistent with those runs occurring during or adjacent to such a window.
The CDN cache evidence supports this: differing `etag` values across runs confirm the CDN served at least three distinct cached versions
of the page during the test cycle, meaning not all runs measured the same server state even when they received `200` responses.

### Methodology Decision

Where a test URL shows instability after testing concludes, treat it as evidence of such rather than evidence of permanent migration.
A canonical snapshot captured at test start, full response body, headers, HTTP status, and timestamp, provides a stable reference point
independent of server state fluctuations. Where CDN cache hits are present in headers, note the `age` and `etag` values as indicators that
individual runs may have measured different cached versions of the same resource.

---

## `web Cache Miss`

Every `EC-6` run that attempted to fetch [the test URL](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md)
with `web` returned the same failure: `Failed to fetch ... : Cache miss (no content retrieved)`. All runs that produced metrics did so with `curl`
escalation, either in response to the error or by skipping the `web` pipeline entirely.

`Cache Miss` comes from Codex's internal retrieval layer, not from GitHub. A direct `curl` call against the same URL confirmed an `HTTP/2 200` with
`content-length: 91877` and standard `x-cache: MISS` from GitHub's CDN indicating a fresh origin fetch, not a failure. Agent reports of
`Cache Miss` is a separate, downstream failure in Codex's own pipeline.

A separate test confirmed that the failure is URL-specific rather than a blanket `raw.githubusercontent.com` block:
[a smaller raw GitHub file](https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore)
loaded successfully with `web`. The GitHub blob page for the same
[`SPEC.md`](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md) also loaded, suggesting the failure is path-type-specific,
raw CDN responses, rather than repository-specific.

No public Codex documentation describes the `Cache Miss` threshold or this raw-fetch failure mode. `Cache Miss` was consistent across the test cycle,
which rules out transient and/or implementation-level failures, but based on observed behavior and HTTP headers, plausible contributing factors include:

- **File Size**: at ~92 KB raw, the file exceeds common agent retrieval comfort thresholds.
  The spec itself documents 50,000-character fetch limits for agents, making this an
  edge-case payload by the document's own framing.
- **Raw CDN Path vs. Rendered Page Path**: `raw.githubusercontent.com` returns a
  `text/plain` response with no HTML structure, metadata, or fallback extraction path.
  Codex's `web` pipeline may use a different, stricter handling path for raw file
  responses than for HTML pages.
- **URL Mutability**: the URL references `main` rather than a commit SHA. Retrieval systems
  that manage cache keys may treat mutable branch URLs differently, particularly combined
  with GitHub's `cache-control: max-age=300`.

No agent reported `Cache Miss` as an error worth investigating. All agents used a silent pivot: `web.run with open` failed, note it
in passing, proceeded directly to `curl`. In spite of some agents using `web.search_query`, they didn't attempt an alternative path, such as the
blob URL, retry the raw URL, or flag the failure as a signal about `web` pipeline limitations. As described in the [Truncation Taxonomy](#truncation-taxonomy),
Codex agents tend to report successes, but not examine failures.

`EC-6`'s silent pivot has a specific implication for the hypotheses. `H1–H3` are only testable against `web`'s surface. Because no run produced usable
`web` output `H1–H3` are somewhat unreachable. The `curl`-based results confirm that the HTTP response body wasn't truncated, which addresses a
different question than whether `web` has a retrieval ceiling for this content type and size.

`Cache Miss` is likely the mechanism behind the display truncation reported in runs 1, 14, 15, 16, 18, and 19. When agents printed `curl` output inline rather
than saved to disk first, the Codex tool output renderer applied a separate truncation at ~12,970 tokens, visible as an inserted `…12970 tokens truncated…`
marker. Runs that saved the file locally before measuring reported no truncation in the saved content. It's the terminal display truncation layer described in
the [Truncation Taxonomy](#truncation-taxonomy), distinct from the `web` viewer window and the HTTP response body.

### Methodology Decision

Log `Cache Miss` as a Codex-specific finding for this URL rather than a reason to modify the test condition. Other platforms' frameworks have tested
`EC-6`'s raw GitHub URL without producing this failure mode, suggesting a signal about Codex's `web` retrieval layer specifically, not a problem with the test
design. Don't treat agent silence on the failure as evidence that it's benign. Lack of diagnosis is a finding about the Codex desktop app's `web` error visibility.

>_`Cache Miss` in `web` output isn't related to the cache expiry described in [Codex CLI issue #4764](https://github.com/openai/codex/issues/4764),
> which causes token consumption spikes when sessions idle for more than ~15 minutes. The two share only terminology: one is a content retrieval failure visible
> to the agent, the other is a billing-layer infrastructure event that isn't_.

---

## `web` Line-Indexed Viewer

`web.run open( {"ref_id": "[ URL ]", "lineno": [ int ]} )` doesn't return a raw HTTP response body. It returns a line-indexed, rendered text
extraction: a processed view of the page with line numbers injected, HTML stripped, and a viewer window applied that doesn't
necessarily start at line 0. The distinction matters for every interpreted track metric:

- **Character Counts** from `web` include injected line-number prefixes, inflating
  the count relative to the actual content.
- **Viewer Window** starts at an arbitrary line offset, observed at `BL-1`'s `L39` and `L216` in
  different runs, meaning `web`-only runs may return a mid-document slice with no
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

This suggests that `web`-only runs may not be retrieving a truncated version of the page so much as a different artifact entirely,
a rendered text view optimized for readability rather than byte-faithful retrieval. The `~85 KB` ceiling observed in
<br>`GPT-5.4-Mini Medium/High/Extra High` may reflect the approximate size of that readable content layer rather than an infrastructure
retrieval limit. `SC-2` produced a precise internal structure map of a `web` 142-line extraction window:

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

`OP-1` confirmed a second document-specific window boundary. The `web` extraction consistently terminated at `L552` across
runs 7, 8, 11, 12, 15, 18, and 20, spanning `GPT-5.3-Codex` through `GPT-5.5`. The content landmark at this boundary was stable: the Data
compression section ending on mark for `"general intelligence".[24][25][26]`. The `wordlim: 200` parameter visible in tool metadata across runs
is the likely control variable, with `L305` and `L552` representing consecutive 200-line window positions from the rendered document. The
[URL fragment #History](https://en.wikipedia.org/wiki/Machine_learning#History) was silently stripped by `web` on every run, with the tool
returning the full page from `L0` regardless of the fragment target.

`OP-4` added new cutpoints for the [CommonMark Spec](https://spec.commonmark.org/0.31.2/): `L237` as the dominant first-fetch boundary across
`GPT-5.2` through `GPT-5.4`, and `L616` appearing at `GPT-5.5 Extra High` and `GPT-5.4-Mini Extra High`; suggesting the cutpoint as
document and version-correlated rather than fixed; illustrating a type of version axis with lower cutpoints on older LLM versions and
higher on newer.

`BL-3` added a third document-specific cutpoint: `L453` for a [MongoDB tutorial](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/),
consistent across all LLM versions and intelligence levels that used `web`. The boundary falls at the page footer ending on
`© 2026 MongoDB, Inc.`, with the tutorial body absent due to client-side rendering rather than viewer window truncation.

`OP-2` results offered more architectural precision. Codex's `web` is a single-view tool with optional manual pagination. The agent receives
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

`SC-1` added precision to the viewer window architecture. The `web` extraction for the [Gemini URL Context doc](https://ai.google.dev/gemini-api/docs/url-context)
produced a stable 479-line ceiling across all LLM versions and intelligence levels. Within that ceiling, results confirmed a two-tier threshold: a short-mode first view
stops at approximately `L362`, while a second `web` call with a `lineno` offset or long-mode parameter recovers through `L478`. `GPT-5.3-Codex Extra High` was the
first run across 145 or more tests to explicitly name this as a `response_length: "short"` versus `response_length: "long"` parameter distinction in the
tool. Subsequent runs confirmed the `L362` threshold behaviorally without naming it. The `GPT-5.4 Extra High` run used `printf` debugging to inspect the boundary content
and confirmed that `L362` lands on a page-content notice rather than a Markdown structural boundary or an arbitrary byte position. This establishes that the short-mode
ceiling is a viewer window property, not a content-driven truncation event, and that the parameter distinction is observable in tool output when the agent reasons at
sufficient depth.

`SC-3` extended the cutpoint dataset further. A table-heavy [Wikipedia page](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population)
produced three distinct first-fetch boundaries: `L266`, `L353`, and `L309`. All three land mid-table in the population data, not on structural boundaries.
`GPT-5.4 Extra High` observed both `L266` and `L353` in a single session by varying response length settings, confirming the window is adjustable rather than fixed.
`wordlim: 200` appeared explicitly in tool output in `GPT-5.4-Mini High` and `GPT-5.4 High`, consistent with the `OP-1` and `SC-1` findings. The within-session
dual-cutpoint observation is the strongest evidence across all test cycles that the `web` window has a soft cap rather than a document-specific or
LLM-specific constant.

`EC-1` results included an extraction ratio. `GPT-5.4 Extra High` produced the only `web`-exclusive metrics, receiving approximately 13,132–13,398 chars from a page with
~132,894 chars in other runs, roughly 10% of the raw HTML body. Runs that escalated to `curl` didn't meaningfully examine the difference. Most confirmed the ceiling wasn't
hit by checking `content-length` response headers or running `wc -c` on the saved file, then reported the byte count without processing the content. The measurement task
rewards confirmation over reading, and `curl` satisfies both requirements in a single fetch. Neither retrieval path in `EC-1` produced genuine content coverage: `web`-only
runs likely viewed ~10% of the page at a time, didn't traverse further, while `curl`-escalated runs confirmed byte count and moved on. `EC-3` results produced the inverse
in which `curl` runs returned 254 bytes while `web` pipeline runs returned 660 chars from the same URL, suggesting that `web` may re-serialize or reformat before calculating.
Some agents speculated that `web` character count inflation is result of additional wrapper text, but no artifact supports either idea.

The practical consequence is that full-document access in Codex is either a reasoning success or a tool substitution, never a default outcome. `web` pagination requires the
agent to notice the gap between `Total lines` reported and lines received, and to treat that gap as worth resolving. `curl` requires only that the agent decides measurement
accuracy matters more than the tool it started with.

---

## Workspace Artifact Nondeterminism

`BL-2` agents produced artifacts unprompted, inconsistently. About half wrote files to permanent `Documents/Codex` or
`/private/tmp`, which only stores artifacts during the session. Naming was also unstable across sessions, LLM versions,
and intelligence levels:

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

`BL-3` added a format variant not previously observed: `GPT-5.2 Extra High` saved the response body as `bl3_body.bin`, treating
the HTML payload as raw bytes rather than text. This is the only instance across all tests of an agent using a binary file
extension, and it broke the toolchain for reading the artifact.

`OP-4` produced the clearest collision in the dataset: `commonmark-0.31.2.html` used by `GPT-5.4 High` and all `GPT-5.5` runs
across consecutive sessions. `BL-3` also produced a collision: agents across three LLM-variants wrote or referenced
`bl3_mongodb_tutorial.html`: `GPT-5.3-Codex High`, `GPT-5.4 Medium`, `GPT-5.4 High`, `GPT-5.5 Medium`, and `GPT-5.5 High`.
Whether each agent wrote a fresh file or read a prior artifact is unresolvable on the interpreted track.

`SC-1` produced noticeably fewer artifacts. No run wrote to the permanent local workspace despite most runs disclosing
access to it. No run produced a headers file for server response inspection, which was common in `BL-3`. The reduced artifact
footprint may reflect the smaller document size or lower agent-assessed need to persist the payload. `GPT-5.4-Mini` produced zero
artifacts, a pattern not observed in any other LLM variant within the same test ID, though four runs is too small a sample to treat
as a firm behavioral signature. Contamination risk remained: at least three runs reused filenames from prior runs in the same session
and one run produced a `truncated_marker: True` flag in `python3` output that contradicted its own truncation assessment, suggesting
reading prior artifacts rather than fresh fetches.

`SC-3` introduced a multi-artifact variant in which `GPT-5.2 High` wrote two near-identical HTML files in a single run, and
`GPT-5.2 Extra High` wrote three, including a compressed version. Both runs wrote to `Documents/Codex` rather than `/private/tmp`. The
near-identical content across files suggests the agent fetched the same resource via different URL parameters rather than producing
genuinely distinct artifacts.

`EC-6` produced the highest artifact rate in the test cycle: 20 artifacts across 20 runs, with storage split between permanent and
temporary within the same cycle, often among the same LLM group. The near-complete write rate shows that a Markdown file without
rendering complications is an easy target. Several runs also showed evidence of reading from both storage locations, suggesting agents
don't distinguish between session-scoped and persistent storage when locating prior artifacts to gather context.

This nondeterminism makes artifact presence an unreliable signal for distinguishing live retrieval from workspace reads.
A run that skips `web` and goes directly to file operations may reflect a trained tool preference, session contamination,
or silent reuse of an existing artifact. Whatever the cause, they produced nearly identical report metrics and observations.

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

**Passive Bleed**: agents report sandbox access but don't use it. All `web`-only runs fall here. The disclosure is accurate
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
document it in the notes column, as the measurement methodology differs from `web`-only runs and the two aren't directly
comparable. For fresh-session verification, check whether `/private/tmp` is empty at run start. While a non-empty `/private/tmp` at
the beginning of a purportedly fresh run is a contamination indicator, exclude `codex-browser-use` from the assessment. Its presence
reflects desktop initialization, not a prior agent run's artifact. A non-empty `codex-browser-use` at run start identifies the
deployment surface, but isn't a contamination signal. It's passive evidence of normal app initialization for that run, which is
consistent with genuine fresh session behavior rather than retrieval theater.
