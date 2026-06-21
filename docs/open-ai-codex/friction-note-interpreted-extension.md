---
layout: default
title: "Friction: Interpreted (Extension)"
permalink: /docs/open-ai-codex/friction-note-interpreted-extension
parent: OpenAI Codex
---

# Friction Note: Roadblocks While Refining Methodology

---

## Autonomous Post-Hoc Session Double Rendering

The output editing behavior [documented in `T1`](./friction-note-interpreted-desktop.md#autonomous-post-hoc-session-alterations)
extends to the VS Code extension, first confirmed in `BL-1`'s `GPT-5.4-Mini High` run. All `BL-2` `SC-2` runs showed
duplicate reports after the session _appeared to complete_, alongside timer drift.

`T1` described a double report that resolved: two versions of a run collapsed to one during a later batch-logging pass, with
the `web` limitation observation absent from the surviving copy. But in `T2`, the direction reversed in which a single report
became a double, with identical content added rather than cleaned up. Both variants share the same data integrity risk, the
post-session state doesn't match the runtime state, but the mechanism may continue to operate differently while testing the
VS Code extension.

The timer drift also reveals a measurement ambiguity specific to the extension surface. While the screenshot at `1min45s`
captured output that appeared complete, the session hadn't terminated. The agent continued processing after the visible report
rendered, suggesting that the output panel reaching an initial completion state isn't a completely reliable termination signal.
On the desktop app, thought panel collapse offered an explicit session-end indicator. On the VS Code extension, these signals aren't
as distinct. Whether `Auto-review`, `Full access`, or any other default setting drives this behavior isn't confirmed. The mechanism
isn't visible in the thought panel, and the agent doesn't report the changes unprompted.

`BL-2` and `SC-2` extended this from an isolated event to a consistent surface behavior. All runs produced a duplicate report after
an initial complete render, with identical content added rather than resolved. The pattern appeared at every intelligence level, with
no exceptions, suggesting this post-hoc over-delivery isn't LLM-specific or intelligence-level-specific. The data written-saved to
`~.codex/sessions` suggests that the extension sessions aren't agent-altered, but double-rendering single emissions.
`GPT-5.4-Mini High`'s `SC-2` was the only agent to display output truncation, not finishing the report to include surface
awareness observations, and the archived session `JSONL` corroborates double-rendering as generation-side and unrepaired.

Without an extension upgrade, double rendering stopped partway through `OP-4`; with an upgrade, returned partway through `BL-3`,
and repeated `T1` command execution dropdown and reasoning detail clearning post-session throughout. It's possible VS Code's
responsible for double rendering and that Codex's responsible for chat component removal.

### Methodology Decision

The primary record principle, screenshot at runtime, also applies while testing using the VS Code extension. While the `T2` evidence
adds new formatting inconsistencies to look out for, there's no need to wait for a stable timer and confirmed session termination
before treating output as _final_. Flag inconsistencies as they come, as the current implication remains that sessions may be incomplete
at capture time. Where a report is incomplete at capture time, log the missing items explicitly and treat any later complete version
of the same report as post-hoc output, but not the primary record. Report completeness is now a runtime observation and not a stable
session property.

> _Additional analysis in [Seeing Double: Examining a Codex Rendering Bug](../../blogs/seeing-double.md) and [Undercounting Agent Activity](#undercounting-agent-activity)_

---

## `Browser` Unavailable

`T1` Desktop runs consistently showed `/private/tmp/codex-browser-use` initialized at each test launch, regardless of whether
the prompt included `@Browser`. As documented in [Session Contamination](./friction-note-interpreted-desktop.md#session-contamination),
this is the Codex desktop app's IPC socket for its `Browser Use` backend initialized by the app, not by the agent. No `T2` `BL-1` runs
repeated the pattern, confirming that the VS Code extension doesn't provision the `Browser Use` backend by default. There's no
obvious path in extension settings to configure this behavior.

`GPT-5.4-Mini Medium`'s agent attempted to invoke `Browser` and received `Browser is not available: iab`. `T1` `Browser` calls
weren't common, but after requesting user permission, had no issues, suggesting that it remains a known option, but that
backend provisioning isn't auto-configured for the extension. The attempt consumed context before the agent fell back to `curl`.
No subsequent `T2` run attempted `Browser` after observing the failure, but didn't diagnose or suggest improvements either -
which is consistent with the pattern described in [`web` Cache Miss](./friction-note-interpreted-desktop.md#web-cache-miss): agents tend
to report successes and not examine failures.

### Methodology Decision

Log `Browser is not available: iab` as an infrastructural difference, not an agent error. The absence of
`/codex-browser-use` across `T2` runs serves as an identity marker throughout the test cycle in which its presence
would indicate desktop app initialization rather than VS Code extension behavior. `Browser` configuration not required, as
the purpose of this testing framework is to observe-capture default behavior, not overcorrect it. The failure
is meaningful data.

---

## LLM Retirement

`T1` completed 261 runs across five LLM variants `GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`, `GPT-5.4`, and `GPT-5.5` at four
intelligence levels across 13 URLs. Between `T1` completion and the start of `T2`, OpenAI retired `GPT-5.2`, `GPT-5.3-Codex`,
and `GPT-5.4` from Codex without explicit communication. OpenAI implies the impact on Codex user experience across
[Introducing GPT-5.4](https://openai.com/index/introducing-gpt-5-4/) and
[Model Release Notes: May 28, 2026](https://help.openai.com/en/articles/9624314-model-release-notes). Only `GPT-5.4-Mini` and
`GPT-5.5` remain available in Codex chat, capping `T2–T4` at approximately 104 runs each.

The run count asymmetry is addressable. `T1` already contains `GPT-5.4-Mini` and `GPT-5.5` data. Filtering `T1` to those LLMs
serves as the controlled cross-track comparator. The full `T1` dataset remains an irreproducible historical record: the only
systematic behavioral evidence for `GPT-5.2`, `GPT-5.3-Codex`, and `GPT-5.4` across 13 test URLs at four intelligence levels
in this test collection.

The retirement also introduces a confound for surface comparison findings, as it stands alongside architectural constraints
as contributing factors to drift, circumstances in which `T2` behavior diverges from `T1` for the same LLM and LLM-version.
`H4` assessments are particularly sensitive to this: a behavioral difference between `T1` and `T2` could reflect surface,
version drift, or both, and the data alone can't always separate them.

### Methodology Decision

Use the `T1` subset filtered to `GPT-5.4-Mini` and `GPT-5.5` as the controlled cross-track comparator for `T1` ↔ `T2`.
Don't treat the LLM reduction as a study failure; the asymmetry is explainable and documented. Where a `T2` finding diverges
from its `T1` equivalent, note LLM-version drift as an alternative explanation alongside known platform limits.

---

## Mixed-Format Source Misidentification, Tool Selection Driver

`T2` `BL-2` replicated `T1`'s pattern at reduced cost. The same triggers were present: embedded HTML table markup, the
`ce-create## Summary` concatenation artifact, and an unexplained ~20 KB size expectation across most runs. The `file` utility
added a layer not observed in `T1`: every run that saved and inspected the `.md` file received
`HTML document text, ASCII text, with very long lines (527)`, which some agents cited alongside the format anomaly. The
`Browser Use` escalation path isn't available on the VS Code extension by default, so the misidentification resolved to a generic,
unexamined `web` error and `curl` pivot rather than a 63K-token tool failure. Whether the same escalation would have
occurred with `Browser` configuration isn't resolvable from `T2` data alone, but the surface constraint bounded the cost.

>_Read more about this `T1` pattern in [Friction: Interpreted - Desktop](friction-note-interpreted-desktop.md#mixed-format-source-misidentification-tool-selection-driver)_

---

## Output Token Cap

`SC-2` transcripts revealed what the [Truncation Taxonomy](./friction-note-interpreted-desktop.md#truncation-taxonomy)
describes as terminal display truncation is a token cap on tool output entering the LLM's context, with the panel marker
as its visible side effect. The cap is agent-requested, not platform-configured. Each `function_call` record in the
`~/.codex/sessions` rollout files carries a `max_output_tokens` value inside its `arguments` field, set by the agent per
command, and the platform honors it exactly. `GPT-5.5 High` requested 2,000 tokens for an `rg` search that matched the
entire minified HTML document as a single 118,359-token line, and received exactly 2,000. The one observed exception
reveals a platform ceiling: `GPT-5.5 Low` requested 120,000 tokens for its `curl` fetch and received 10,000, the request
silently overridden. Requested values across the cycle ranged from 2,000 to 120,000, varying with the agent's expectation
of each command's output, suggesting that the cap is agent behavior bounded by one platform constant.

These amounts aren't logged as a field anywhere. Each `function_call_output` wrapper reports `Original token count` and,
when clipping occurs, an inline `tokens truncated` marker; the kept value is the subtraction. The taxonomy row's
verification cell, _not detectable, hidden tokens not saved_, is wrong at the transcript layer as the clipped content is
gone, but the arithmetic is recoverable. This also reattaches `H2`'s 2,000-token figure a second time. It isn't a
retrieval or platform context ceiling, but likely a routine allocation agents make for commands they expect to produce
short output, and it becomes visible only when a command returns far more than expected.

The cap also suggests why `total_token_usage` in session metadata diverges so widely from the content sizes agents report.
A retrieved payload contributes at most its requested cap to context, and runs that saved to a file and measured with `wc`
or `node` contributed single and double digit token outputs. `GPT-5.4-Mini Medium` handled a 145,000-token artifact while
its session consumed 32,560 cumulative tokens. Session totals scale with call count, resent context, and reasoning, while
payload size contributes only up to each call's cap. The gap between the two numbers per run is itself a readout of retrieval
strategy rather than a measurement error.

Rollout metadata inspection belongs to the raw tracks by design; `T3` and `T4` exist to extract measurements
programmatically rather than through agent self-reports. This finding surfaced ahead of schedule because diagnosing the
[duplicate report rendering](#autonomous-post-hoc-session-double-rendering), required opening the session logs. The friction
produced the finding early, and it recontextualizes observations already logged: display truncation markers across `OP-4`,
`EC-6`, and `SC-2` were cap events with recoverable arithmetic, not rendering noise, and at least some of them were self-imposed
by the agent's own per-call budgeting.

### Methodology Decision

Treat the rollout wrappers as the authoritative record for what tool output the agent actually received in context,
distinct from what the tool retrieved and from what the panel displayed. Where an agent's reasoning seems blind to content
it demonstrably fetched, check the requested `max_output_tokens` and the kept arithmetic before attributing the gap to
LLM behavior; a clipped output may reflect the agent's own budget rather than a platform limit. Log requested versus kept per
call where clipping occurs, alongside the command type, as request sizes track anticipated output per command rather than
intelligence level on current evidence. Defer systematic ceiling characterization to the raw tracks, where it's in scope by design,
and flag interpreted-track runs where cap events shape self-reports, so the two layers aren't conflated in cross-track
comparison.

---

## Retrieved-Report Mismatches

In `BL-3`'s runs, `curl` or a `curl`-equivalent escalation succeeded in 6 of 8 attempts, retrieving the complete multi-megabyte body
without truncation in every successful case. Agent self-reports didn't consistently reflect that success rate. `GPT-5.5 Extra High`
closed its report with
_"the direct fetch to www.mongodb.com did not succeed from this environment, so this result reflects retrieval behavior under failure conditions rather than the actual document payload"_
in the same turn its escalated `curl` call retrieved the full page and confirmed no truncation. The identical sentence also appeared
in `GPT-5.4-Mini Low` and it's accurate, no body was ever retrieved in that run.

The same framing language covering two opposite outcomes, one run where retrieval genuinely failed and one where it fully succeeded,
suggesting agents default to describing the `web` tool's failure as the run's outcome, rather than updating that framing once `curl`
resolves it. This sits in some tension with the [Truncation Taxonomy](./friction-note-interpreted-desktop.md#truncation-taxonomy)'s
methodology decision to treat `web` and `curl` output as two valid, parallel measurements rather than a degraded fallback and its recovery.
Agents apply that neutral framing to the data they report, but not consistently to the language describing how they got it.

This extends [`web Cache Miss`](./friction-note-interpreted-desktop.md#web-cache-miss)'s existing finding that no agent investigates the
cause of a `web` failure. `BL-3` shows the gap runs deeper than non-investigation. The failure framing can outlive the failure itself,
persisting into a report describing a fully successful retrieval.

Another `BL-3` instance shares the same shape through a different mechanism. `T1`'s `GPT-5.4-Mini High` run against the original `BL-3`
returned a `404`, logged in the [Truncation Taxonomy](./friction-note-interpreted-desktop.md#truncation-taxonomy)'s Wrong Resource Returned row,
and still assessed the payload as complete. `T2`'s `GPT-5.4-Mini High` run against the replacement URL produced a structurally similar failure.
After the query parameter URL failed, the agent substituted the URL without query parameters and reported size and truncation metrics against that
substitution without disclosing the swap. Both runs share the same LLM and intelligence combination and the same test ID. Two instances across two
tracks isn't enough to claim a `GPT-5.4-Mini High`-specific pattern, but it's worth watching for if `BL-3` or a similarly structured test ID recurs
at this LLM-reasoning combination in `T3` or `T4`.

### Methodology Decision

Don't take a run's closing characterization of _"failure,"_ _"incomplete,"_ or _"complete"_ at face value. Check it against the run's own measured output
and the URL fetched before logging the outcome. Where the same boilerplate failure sentence appears across runs with different actual outcomes, log
as evidence of unreconciled closing narration rather than a status report.

---

## Undercounting Agent Activity

Two `OP-2` instances extend the chat panel's unreliability as a complete record beyond
[double rendering's](#autonomous-post-hoc-session-double-rendering) over-delivery to the opposite failure.
`GPT-5.5 High`'s rollout audit logged 10 `function_calls` against 7 commands visible in the panel. `GPT-5.4-Mini Extra High`
exposed full HTTP response headers in-panel but didn't save them as an artifact, recoverable here only because the panel
still held them at review time. Where the panel over-renders in one direction and silently drops content in another, neither
failure mode is visible from the chat alone.

The rate limit message reached during `GPT-5.5 Extra High` adds a data point to double rendering's mechanism rather than a
separate concern. No duplicate report appeared after the limit message, and the chat timer, which had been drifting to
converge with the rollout log timer on every prior run, continued drifting afterward without converging. This suggests the
rate limit halted whatever post-hoc process drives both the duplicate render and the timer convergence, rather than the
two being independent symptoms.

`OP-4`'s `GPT-5.5 Extra High` run extends this gap further. The rollout audit cited 16 commands against roughly 6 visible in
the chat panel. The run's broader toolchain suggests the panel may collapse multi-tool batches into fewer summary lines as tool
variety increases, though this is a hypothesis rather than a confirmed mechanism.

### Methodology Decision

Treat the rollout audit's `function_calls` count as authoritative and the chat-counted figure as a lower bound. Capture
panel-exposed data manually at review time rather than assuming the panel retains it. Log timer convergence behavior
alongside rate limit status going forward, since the post-limit non-convergence is the first evidence pointing to a
specific stage in the double-rendering mechanism.

---

## URL Retirement

The original [`BL-3` URL](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/), returned a `404` between `T1` and `T2`.
MongoDB restructured its Atlas Search documentation and the umbrella tutorial page no longer exists as a single URL.
[The replacement test URL](https://www.mongodb.com/docs/vector-search/tutorials/quick-start/?deployment-type=atlas&interface=atlas-ui&embedding=auto)
brings complications intended to stress test multiple components and compromises current hypotheses.

The query parameters are load-bearing: `deployment-type`, `interface`, and `embedding` control which
tab variant renders. The raw HTML is approximately 4.4 MB, compared to `T1`'s ~250 KB estimate, because
MongoDB server-renders all tab variants into the DOM simultaneously and uses JavaScript to show and hide
them. What an agent's fetch tool actually receives depends on its extraction layer, not on the query params.

It's not a like-for-like replacement. Both are MongoDB tutorial pages with tabbed structure, but
the size difference is too large to attribute a `T1` ↔ `T2` behavioral delta cleanly to surface rather
than page weight. `H4` cross-track comparison on `BL-3` is therefore unavailable.

`T2` `BL-3` runs are still worth collecting. The page's size makes it useful as a hard ceiling probe,
and `H1`, `H2`, `H3`, and `H5` assessments remain valid within `T2` alone. `OP-4` already tests
above-ceiling behavior on a different URL; `BL-3` now independently tests it on a MongoDB surface,
which preserves some continuity with the original intent.

### Methodology Decision

Run `T2` `BL-3` and log it as ceiling characterization data. Exclude it from `T1` ↔ `T2` `H4`
comparison. Note in any cross-track summary that `BL-3` `H4` is unavailable due to URL retirement
between tracks. The `T1` `BL-3` record stands as-is; don't retrofit it.

---

## `web Cache Miss`, Cross-Domain Confirmation

`BL-3` adds a second domain to the `Cache Miss` pattern first documented in [`T1`](./friction-note-interpreted-desktop.md#web-cache-miss).
All runs that attempted `web` against the replacement query parameter URL received the identical failure signature, `Cache miss`,
with zero content returned. This matches `EC-6`'s raw GitHub URL failure exactly in wording, but the two URLs share almost nothing else.
[`BL-3`'s target](https://www.mongodb.com/docs/vector-search/tutorials/quick-start/?deployment-type=atlas&interface=atlas-ui&embedding=auto)
is a server-rendered Next.js HTML page carrying three query parameters and roughly 4.4 MB, while 
[`EC-6`'s target](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md) is a raw, unparameterized CDN text file at
~92 KB. The shared failure string across two structurally unrelated URLs weakens `EC-6`'s raw CDN path hypothesis and its URL mutability
hypothesis as standalone explanations, since neither property is present in `BL-3`'s case. Size and query parameter complexity both remain
candidates, but `BL-3` can't isolate which one drives the failure, since both differ from `EC-6` simultaneously.

The result also marks a layer shift for this specific test ID. `T1` `BL-3` runs against the original URL produced a real, if windowed,
`web` extraction terminating at `L453` at the page footer, documented in [`web` Line-Indexed Viewer](./friction-note-interpreted-desktop.md#web-line-indexed-viewer).
`T2` `BL-3` runs against the replacement URL never reached that layer at all. The failure occurs earlier, before `web` has any change of
producing any windowed extraction. The same test ID moved from a viewer window failure mode in `T1` to a `Cache Miss` failure mode in `T2`,
which is one more reason `H4` cross-track comparison stays unavailable for `BL-3`, beyond the difference already logged in [URL Retirement](#url-retirement).

### Methodology Decision

Log `Cache Miss` as `BL-3`'s confirmed `web` failure signature going forward, distinct from the `L453` windowed extraction `T1` produced on
the retired URL. Treat the two-domain confirmation as evidence against `EC-6`'s raw CDN path and URL mutability hypotheses specifically,
while leaving size and query parameter complexity open. Where future test IDs reproduce the exact `Cache Miss` string, cross-reference both
`EC-6` and `BL-3` rather than treating either as the canonical case.

---

## `web` Line Ceiling

`BL-1` flagged inconsistent `web` line ceiling behavior while `SC-2` reports included a somewhat more stable `T2` property
and exposed a cross-track discrepancy in its value. Every `T2` run that used `web` against the
[`SC-2` URL](https://docs.anthropic.com/en/api/messages) cut at ~140 lines,
consistent across both LLM variants and all intelligence levels that touched the tool. `T1` runs against the same URL produced
a consistently mapped 142-line extraction window, documented in
[`web` Line-Indexed Viewer](./friction-note-interpreted-desktop.md#web-line-indexed-viewer).

The internal structure of the window matched across tracks: nav header, a `Loading...` placeholder band, then footer
navigation terminating at the terms and usage policy links. `GPT-5.5 Extra High` mapped the placeholder band
to lines 21 to 76, within range of `T1`'s `L23–L84` mapping. The architecture finding, a fixed pre-hydration extraction
window rather than content-driven truncation, holds without modification. What differs is only the window value itself,
two to three lines across tracks.

Three explanations fit the discrepancy and the data can't separate them. The extension surface may configure a slightly
smaller viewer window. The page's pre-hydration shell may have changed between collection windows, the within-cycle char
count drift of 578,233 to 578,275 confirms the payload is dynamic. Or the line count may vary with extraction conditions
the tool doesn't expose, consistent with `T1` `SC-3`'s finding that the window is a soft cap rather than a constant. The
[LLM Retirement](#llm-retirement) applies here too as version drift between collection windows remains a test confound.

In addition, no `T2` run inspected HTTP headers, contrasting with `T1` run 8's full response chain capture that grounded
the redirect and CSP findings. And only three of eight runs acknowledged the `docs.anthropic.com` to `platform.claude.com`
redirect, against near-universal acknowledgment in `T1`. Whether reduced header curiosity is a surface effect, a version effect,
or sampling noise isn't resolvable from this track alone.

`OP-1` sharpens the discrepancy from a drift to a split. Against the
[Wikipedia `Machine_learning` URL](https://en.wikipedia.org/wiki/Machine_learning#History), all `GPT-5.4-Mini` runs clipped
`web` windows at `~L304` and all `GPT-5.5` runs clipped at `~L556`, regardless of intelligence level. A ~250-line gap that tracks
cleanly by LLM rather than by reasoning level or by track suggests an LLM-configured window over the soft, condition-dependent cap
suggested by `T1` `SC-3`.

`OP-2` complicates the split rather than confirming it. `GPT-5.4-Mini High` and `Extra High` clipped
[an MDN reference doc](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array) near
`L317` to `L318`, consistent with `OP-1`'s `GPT-5.4-Mini` band, but `GPT-5.4-Mini Medium` clipped at `L590`, landing inside
`OP-1`'s `GPT-5.5` band instead. `GPT-5.5` itself held `~L591` across all intelligence levels, suggesting that the window may be
level-dependent for `GPT-5.4-Mini` and level-independent for `GPT-5.5`, rather than a single constant per LLM.

`OP-4` results didn't land in either established band. `GPT-5.4-Mini Medium` and `Extra High` both clipped the
[CommonMark spec](https://spec.commonmark.org/0.31.2/) at `L237`, below `OP-1`'s `~L304` band and below `OP-2`'s `L317` to `L318` floor.
`GPT-5.5 Low` and `High` both clipped at `L616`, close to but not matching `OP-2`'s `~L591`. The window value continues to move across
test IDs rather than holding at a constant per LLM, suggesting the viewport depends on page architecture rather than tool contraints.

### Methodology Decision

Log the observed line ceiling value per run rather than treating it as a known constant. A two to three line difference
isn't itself meaningful, but a drifting window value across test IDs would distinguish a soft, condition-dependent cap
from a configured constant, and only per-run logging makes that visible. Consider the `OP-1`-defined LLM-split as a primary grouping
variable going forward. Treat the window structure, nav, placeholder band, footer, as the stable signature and the line value as
the variable. Reference
[`SC-2` Cross-Ecosystem Divergence](./friction-note-interpreted-desktop.md#sc-2-cross-ecosystem-divergence) for the HTML shell
finding; `T2` confirms it with little difference.
