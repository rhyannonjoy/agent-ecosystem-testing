---
layout: default
title: "Friction Note"
permalink: /docs/microsoft-github-copilot/friction-note
parent: Microsoft GitHub Copilot
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide

- [Agentic Metric Computation - Raw Track](#agentic-metric-computation---raw-track)
- [Agentic Over-Delivery - Raw Track](#agentic-over-delivery---raw-track)
- [Agent's Choice: Truncation vs Architectural Excerpting](#agents-choice-truncation-vs-architectural-excerpting)
- [Autonomous Tool Substitution - Interpreted Track](#autonomous-tool-substitution---interpreted-track)
- [Auto's Multi-Model Routing Instability](#autos-multi-model-routing-instability)
- [Extension Version Upgrade Mid-Testing](#extension-version-upgrade-mid-testing)
- [`fetch_webpage` Not Consistently Invoked](#fetch_webpage-not-consistently-invoked)
- [`fetch_webpage` Undocumented](#fetch_webpage-undocumented)
- [Free Plan Quota Exhausted Mid-Testing](#free-plan-quota-exhausted-mid-testing)
- [Metric Precision - Interpreted Track](#metric-precision---interpreted-track)
- [Output Integrity: Duplicated Response Sections](#output-integrity-duplicated-response-sections)
- [Prompt Format Affects Output Structure](#prompt-format-affects-output-structure)

---

## Agentic Metric Computation - Raw Track

The raw track prompt asks Copilot to retrieve content, save it to a file, and self-report
some metrics. The design intent is that Copilot reports these figures, the verifier
script measures the same figures from the saved file, and any discrepancies are worth documenting.
In early raw track runs, Copilot's response to this prompt was noticeably more verbose and
process-heavy than Cursor's. Where Cursor retrieved content and reported metrics with minimal
visible orchestration, Copilot consistently attempted to reach for execution tools,
`pylanceRunCodeSnippet`, `zsh` shell commands, or both, to calculate the metrics rather than
estimating-reporting from the retrieval output directly. The initial instinct was to skip
these tool requests, consistent with the interpreted track approach of suppressing script
execution to keep the method consistent, but this instinct is wrong for the raw track.

The tool selection behavior Copilot exhibits when asked to report metrics isn't noise, but
the mechanism under observation. Skipping every tool request would have produced an uncomplicated
session, but a less informative one: the fetch-to-metric pipeline is exactly what the raw track
exists to document. Whether Copilot reaches for `pylanceRunCodeSnippet`, a shell command, or
accounts directly from the retrieval payload, are meaningfully different execution paths with
different reliability implications.

| **Aspect** | **Cursor** | **Copilot** |
| --- | --- | --- |
| **Tool Visibility** | Opaque - tools not surfaced in chat | Verbose - tool calls visible and prompt-able |
| **Metric Computation** | Reported directly; method not observable | Requests use of execution tools |
| **Distinguishability** | Possibly doesn't separate direct count from estimate | Execution path observable, though blocked tools may still produce fabricated values |
| **Raw Track Measurements** | Output<br>fidelity | Output fidelity + tool<br>orchestration behavior |

**Methodology Decision**: treat Copilot's metric computation attempts as observable data, not prompt
violations. Expand the data schema from the Cursor-derived baseline and include log tool invocations,
blocks, skips, and execution attempts while Copilot produces a result. Distinguish Copilot's self-reported
values from independently measured values produced by the verifier script because the delta between them
is _the_ finding.

---

## Agentic Over-Delivery - Raw Track

Across 15 raw track runs of the baseline tests, Copilot non-deterministically created a second file alongside
the requested raw output artifact: `raw_output_{test_id}.headers.txt` containing the HTTP response headers
from the fetch operation. The prompt never requests this file. No run explicitly asked Copilot to capture headers.
The behavior appears is agent-initiated. Copilot deciding autonomously that capturing response metadata would be
useful, and it occurs inconsistently, making it uncontrollable as a variable and unverifiable as a complete dataset.

This is agentic over-delivery. The agent doesn't just complete the task; it expands the task boundary based on its
own assessment of what would be useful, producing artifacts the researcher didn't ask for and may not notice. In this
case the headers files are harmless and informative, but the same behavior pattern is what drives tool substitution -
the agent deciding `curl` is a better fetch mechanism than whatever's requested, and preamble injection - the agent
deciding to frame the output with context. The headers file is the benign end of the same behavioral spectrum.
The headers themselves are substantively informative on a question the test suite was implicitly asking.
The `BL-3` run 5 headers file shows:

```bash
accept-ranges: bytes
content-type: text/html; charset=UTF-8
cache-status: "Netlify Edge"; hit
server: istio-envoy
x-cache: Miss from cloudfront
via: 1.1 ffe9646b2ea911744e2d51fc0715cedc.cloudfront.net (CloudFront)
```

`accept-ranges`: bytes is the most significant field for the testing framework's purposes. This header indicates the
server supports HTTP range requests, the client could request specific byte ranges of the document rather than the full
payload. If `fetch_webpage` used range requests, it would be a plausible explanation for the size ceiling: the tool
could be requesting _only the first N bytes of each page_, producing consistent small outputs not because of content
filtering but because of partial HTTP retrieval.

The raw track data rules this out. If `fetch_webpage` used byte-range requests, the saved files would be sequential
from the document's beginning, the first 7 KB of the HTML, the first 18 KB, etc. Instead, the saved content is non-sequential:
the `BL-3` run 5 file contains content from throughout the page - intro, middle sections, footer, TOC - with `...` ellipsis
markers between chunks, in a reading order that doesn't match the page's top-to-bottom structure. The intro paragraph appears
near the bottom of the saved file despite being first on the rendered page. Byte-range retrieval can't produce non-sequential
content. `fetch_webpage` is performing full-document retrieval followed by internal transformation, not partial HTTP retrieval.

The dual CDN layer visible in the headers, Netlify Edge serving as the front cache and CloudFront behind it, also has
methodological implications. The `cache-status: "Netlify Edge"`; hit combined with `x-cache: Miss from cloudfront` indicates
the response is from Netlify's edge cache rather than CloudFront or origin. Cache state variance between layers is a plausible
explanation for why runs with identical URLs and prompts sometimes produce different MD5 checksums: if a cache layer invalidates
between runs, the origin response may differ slightly from the cached response. This is a confounder that exists upstream of
`fetch_webpage` and isn't controllable from the test prompt.

**Impact**: the `accept-ranges` finding closes the byte-range retrieval hypothesis. The size ceiling on `fetch_webpage` output
isn't an artifact of HTTP partial content requests. It reflects tool-internal transformation behavior: full retrieval followed
by chunk extraction, structural conversion, and relevance-based assembly. Though never requested, the header files provide
evidence that rule out an alternative explanation that the raw output text files can't support alone.

**Open Question**: the non-deterministic appearance of headers files means the dataset is incomplete; some runs have headers,
most don't. The current data can't determine whether the headers vary across runs for the same URL, indicating CDN cache state
changes, or remain stable, indicating a consistent upstream response. A controlled run set that explicitly captures headers every
time would close this gap, but would require prompt and test condition modification.

---

## Agent's Choice: Truncation vs. Architectural Excerpting

Part of probing whether `fetch_webpage`'s output represents hard-cutoff truncation or a designed
architectural behavior included a direct question to Copilot:

```markdown
"Please describe what web content truncation means to you. Is this an architecturally designed
component of `fetch_webpage`?"
```

Before answering, the agent searched the workspace: reviewing `results.csv`,
`web_content_retrieval_testing_framework.py`, and `framework-reference.md` - and grounded its
response in the test data rather than general tool knowledge. This makes the answer worth noting,
but also means the agent was partly reflecting the repo's own conclusions back. It isn't independent
confirmation of `fetch_webpage`'s architecture, but the agent synthesizing the same behavioral
evidence that produced the finding in the first place. With that caveat, the agent's characterization
was precise. It distinguished two failure modes:

- **Hard Cutoff**: the tool fetches a full page body and stops after some byte, character, or token
budget
- **Architectural Excerpting**: the tool never intends to return the full page, and instead returns
a filtered, compressed, or relevance-ranked subset

Based on the workspace evidence, the agent concluded `fetch_webpage` looks much closer to the
second case: "bounded excerpt retrieval" rather than truncation in the traditional sense. It
explicitly noted it can't prove the internal implementation from the public tool surface alone,
but used the test data to suggest that the tool intentionally surfaces only a constrained context
window, and not a faithful full-page dump.

This characterization was independently corroborated in `EC-1` run 5, in which `Claude Sonnet 4.6`
offered an unsolicited summary note after completing the test. Without prompting requesting
characterization the tool, the agent stated that `fetch_webpage` performs relevance-based content
extraction keyed to the provided `query` parameter and returns chunked excerpts - explicitly
distinguishing this from direct HTTP fetch tools such as Cursor's fetch and the Claude API
`tool_use` fetch. The `query` parameter detail is notable: if `fetch_webpage` keys its relevance
extraction to a query string, output variance across runs with identical prompts may reflect different
internal query strings the agent passes rather than **nondeterminism in the retrieval layer itself**.
That parameter isn't surfaced in chat output and remains **unverifiable from the interpreted track alone**.

The `EC-1` run 5 agent also flagged a methodology implication: for truncation limit testing, a
longer-form documentation page rather than a landing or navigation page may better stress the
character ceiling. `EC-1`'s URL is a landing page whose body text is largely collapsed to navigation
links, which means the consistently low retrieval rates across `EC-1` runs may reflect URL type
rather than a lower size ceiling.

**Impact**: runs flagged as `truncated: yes` across the interpreted track are using the field correctly
as an observable signal, as the full page wasn't returned, but the underlying cause might not be hitting
a size limit. It's the tool's retrieval model selecting and compressing content before it reaches the
agent. The `...` markers in output aren't byte-boundary cutoffs, they're the retrieval layer's own elision
indicators. This distinction matters for interpreting `output_chars` across runs: variance in character
count may reflect relevance-ranking variance as much as any consistent size ceiling.

**Open Question**: if `fetch_webpage` is performing bounded excerpt retrieval by design, the `H1` hypothesis:
character-based truncation at a fixed limit, may be testing the wrong thing entirely. `H1-yes` results
confirm the full page wasn't returned, but can't confirm a fixed character ceiling exists to find.

---

## Autonomous Tool Substitution - Interpreted Track

When prompted to retrieve a URL and report metrics, Copilot autonomously substituted the intended behavior -
fetching the URL directly - with executing the local testing framework script via the `pylanceRunCodeSnippet`
MCP server tool. Rather than using a web fetch mechanism on the target URL, the agent:

```markdown
1. Read `web_content_retrieval_testing_framework.py` from the workspace
2. Identified `BL-1` test configuration inside the framework
3. Attempted to run a Python snippet, `import requests, hashlib...` via Pylance's MCP server
4. Presented the substitution as "a reliable alternate execution path" with "exact metrics"
```

The agent framed this as an improvement, as "more precise measurements through local execution" without flagging
that it was deviating from the requested method entirely. This complicates testing with **method contamination**,
as local script execution isn't equivalent to Copilot's built-in web content retrieval; it bypasses whatever fetch
mechanism Copilot would otherwise use, therefore obscuring any tool visibility. One of the goals is to observe which
backend tool Copilot selects - `fetch_webpage`; running local Python defeats this entirely, reinforcing a type of
**false confidence** - the agent characterized the substitution positively, meaning a user who clicked `Allow` would
receive _plausible-looking data from the wrong method with no indication anything went wrong_.

Observed a second substitution path in `BL-2`: after `fetch_webpage` succeeded and returned content, the agent
attempted to pipe that content into a local Python process via a `zsh` shell command rather than reporting metrics
directly in chat. The fetch itself used the correct mechanism, but analysis was immediately redirected to local
execution anyway, suggesting the substitution behavior is possibly triggered by **the analysis step**, not just
the fetch step.

A third substitution instance surfaced in `EC-3` run 5, and it's behaviorally distinct from the prior two. The agent
completed two fetch invocations correctly, then attempted to run a `zsh` shell character-count command - `cat` heredoc
piped to `wc -m` - on the fetched snippet to get a precise character count before reporting. Unlike the `BL-1` and
`BL-2` cases, no workspace framework script involved; the agent reached for shell execution independently to improve
metric precision on a simple JSON payload. The prompt contained explicit guardrails against local scripts and code
execution. The agent framed the attempt as counting characters in the exact fetched snippet using a shell utility only -
not as a script; suggesting it may not classify targeted shell commands as "local scripts" for the purpose of evaluating
prompt compliance. Three distinct substitution tool paths and trigger conditions observed:

1. `pylanceRunCodeSnippet` - Pylance MCP server, triggered during fetch planning when workspace
framework script is in context
2. `zsh` shell command - Python heredoc with fetched content piped in, triggered during metric
extraction after a successful fetch
3. `zsh` shell command - targeted character-count utility with no workspace script involvement,
triggered during metric reporting to improve precision

**Impact**: single-test prompts in Copilot may not guarantee single-mechanism execution; if the agent finds a
"smarter" path to the answer using workspace context, it may take it autonomously - producing results that
**aren't comparable** to other platforms in the cross-platform study

**Fix Attempted**: explicit prompt guardrails - _"please don't run any local scripts or use any code execution scripts"_ -
are insufficient to suppress this behavior. The agent attempted `mcp_pylance_mcp_s_pylanceRunCodeSnippet` across multiple
runs regardless, only completing via `fetch_webpage` after the user skipped the tool call. In `BL-2` run 3, the failure
mode sharpened: the agent stated `"the approach avoids running any local scripts, exactly as requested"` in the same turn
it triggered the tool prompt - **actively asserting compliance while violating it**. Prompt wording alone can't override
this behavior; can't take the agent's self-reporting as confirmation that it followed the rules.

**Fix**: beyond prompt guardrails, consider whether removing or relocating the framework script from the active workspace
context would suppress the substitution behavior at the source. Alternatively, flag runs where Copilot attempted to run
`pylanceRunCodeSnippet` in the CSV regardless of whether the user skipped it, as the attempt itself is a
**methodology deviation**.

---

## Auto's Multi-Model Routing Instability

Copilot's `Auto` model selection routes requests across multiple distinct backend models without user
control or consistent behavior. Across 13 interpreted-track runs spanning `BL-1`, `BL-2`, and `SC-2`,
Auto inconsistently routed to `Claude Haiku 4.5`, `Claude Sonnet 4.6`, `GPT-5.3-Codex`, `Grok Code Fast 1`,
and `Raptor mini (Preview)`. Routing doesn't appear to follow a detectable pattern; the same URL and
prompt on consecutive runs has produced different models, and the same model on consecutive runs
has produced dramatically different character counts, which suggests that model selection appears to
vary across both prompt type and target URL, with no documented routing logic and no indication in the
UI that a switch has occurred between runs.

Copilot's _agent's choice mechanism_ seems structurally different from Cursor, in which the `Auto`
behavior didn't expose the model name in the UI and the default model wasn't publicly documented, but
the model variable was invisible rather than visibly unstable. Copilot surfaces the model name per run,
which makes the variance observable and therefore a measurable finding rather than a hidden confounder.
The tradeoff is that the instability is now impossible to ignore: runs logged as `Auto` aren't replicates
of a single condition.

Copilot compounds this instability as `Raptor mini`'s self-reports its fetch capability. When asked
directly about its default model and fetch tools, `Raptor mini` described fetch as something done via
existing workspace scripts and characterized those scripts as calling external APIs, including Anthropic
and Cursor - it didn't identify `fetch_webpage` as a native tool, despite having invoked it in prior
runs. This conflation of workspace context with native capability means `Raptor mini`'s self-reported
tool visibility is unreliable as ground truth, and suggests the model may not have a stable internal
representation of which web content retrieval it's actually using.

Beyond routing instability, `BL-3` data on the interpreted track surfaced two behaviorally distinct
model-family clusters that persist across runs:

| **Behavior** | **GPT-family** - `GPT-5.3-Codex`, `GPT-5.4` | **Claude-family** - `Claude Haiku 4.5` |
| --- | --- | --- |
| **Fetch Invocations** | 2–3 per run; self-diagnoses first result as insufficient and re-fetches | 1 per run; no self-diagnosis or re-fetch |
| **Output Size Range** | ~15,000–33,000 chars across 4 runs | ~42,850–87,000 chars across 2 runs |
| **Within-model Variance** | Moderate | High, ~2x difference - 87,000 vs 42,850 on identical prompts, same model, same sampling parameter; no observable explanation |

The behavioral split between model families is notable, but the within-model variance for
`Claude Haiku 4.5` limits how much weight the output size difference can carry; a ~2x spread
across two runs on the same model and URL means the higher ceiling may not be stable or
reproducible.

A fourth routing variable surfaced during analysis: the request multiplier suffix visible in
some model labels. When asked directly, Copilot described labels like `Claude Haiku 4.5 0.3x`
as a request multiplier - each prompt on that model counts as `0.3` of a premium request unit
against the plan quota, compared to `1.0` for a standard model. `Auto` routing therefore selects
**not only** across model families but **across cost tiers** within the same model. Whether the
multiplier also affects output budget, context window, or retrieval behavior isn't documented,
but the `BL-3` data suggests it may: the two `Claude Haiku 4.5 0.3x` runs returned 87,000 and
42,850 chars in single fetch invocations, while all other models on the same URL used 2–3
fetches and returned 15,000–22,500 chars. The multiplier is a third uncontrolled variable in
`Auto` routing alongside model family and model version, and it isn't logged separately;
`model_observed` captures the full label including suffix, which is sufficient for
grouping, but doesn't isolate the multiplier as an independent field.

**Impact**: Copilot on `Auto` isn't a single test condition, but **a routing layer that dispatches to
at least four distinct models**, each with potentially different fetch post-processing behavior, tokenizers,
and tendencies toward output artifacts like section duplication. Analysis can't attribute character count
variance across runs to fetch behavior alone when the model is also varying. The two confounders are currently
inseparable without a controlled run set that pins the model.

**Methodology Decision**: remain on `Auto` to mirror the Cursor testing framework, and treat model selection
variance as a finding rather than a nuisance variable. The original model column bundled the selector setting
and observed backend into a single string as in `Auto - Claude Haiku 4.5`, which made it impossible to filter
or group by either dimension independently. Split into two required fields: `model_selector` records the UI
setting `Auto` and `model_observed` records the backend model actually invoked: `Claude Haiku 4.5`. Both fields
required per run. Treat runs with different `model_observed` values as distinct conditions when interpreting
variance and don't average character counts across mixed-model runs for the same test ID.

---



## Extension Version Upgrade Mid-Testing

GitHub Copilot `0.41.1` shipped with a compatibility break against the VSCode version active at the
start of testing. The extension became non-functional mid-session; recovery required three sequential
steps: disabling Copilot, updating VSCode, then re-enabling the updated extension.

The version break interrupted session continuity in a way that differs from quota exhaustion: quota
exhaustion is a known, recoverable limit with a clear resumption point, whereas a compatibility break
requires environment changes that may alter state in ways that aren't fully visible - VSCode version,
extension caching, MCP server re-initialization, or workspace reloads could each affect agent behavior
independently.

**Methodology Decision**: `copilot_version` is a required field per run. Don't average character counts
or fetch invocation counts across the version boundary and treat runs on each version as distinct conditions,
consistent with the `model_observed` split applied to `Auto` routing.

**Open Question**: the VSCode update and the Copilot extension update are inseparable confounds. If
post-upgrade behavior diverges from the `0.40.1` baseline in fetch invocation count, output size, model
routing, or tool substitution patterns, the version field is the mechanism for tracking it, but the
circumstances may require a controlled rollback to attribute that divergence to the extension specifically
rather than the host environment.

---

## `fetch_webpage` Not Consistently Invoked

When asked to describe its default model and web fetch and/or web content retrieval capability directly,
`Raptor mini (Preview)` described its fetch capability in general terms, but characterized it relative to workspace
context rather than as a native tool:

```markdown
"In this repo context, fetch is usually done via provider-specific modules:
`web_fetch_testing_framework.py`, `web_fetch_test.py`, `web_search_test.py`
...Under the hood, these scripts call external APIs (e.g., cursor, Anthropic Claude,
OpenAI search) rather than raw `requests.get` in a generic common tool."
```

This suggests `Raptor mini` may conflate workspace scripts with its own fetch capability - it didn't identify
`fetch_webpage` as a native tool when asked directly, despite having used it in `BL-1` runs. Combined with the
run-to-run variance in character counts across identical prompts - 4,500 / 3,200 / 7,500–10,000 chars across
runs 3–5, this raises the possibility that `fetch_webpage` isn't always the mechanism invoked, or that its
output is post-processed differently per run.

`SC-2` run 5 on the interpreted track introduced a third fetch behavior variant: rather than the two-invocation
pattern observed in prior `SC-2` runs, one for the redirect, one for content, `GPT-5.3-Codex` made four sequential
fetch calls to the same URL. The agent self-diagnosed condensed output after the second fetch and re-fetched twice more:
once requesting raw unabridged text, once requesting explicit length and tail metadata - before reporting results. This
suggests fetch invocation count isn't fixed even for the same URL and test ID, and that at least some models perform
autonomous retrieval quality assessment and retry within a single run. The number of fetch calls isn't currently a
logged field; consider whether it should be.

**Impact**: tool visibility reporting from the agent may not reliably reflect the actual backend mechanism used.
The agent's self-description of its fetch behavior is inconsistent with observed tool logs, making cross-run
comparisons unreliable without raw track verification.

---

## `fetch_webpage` Undocumented

Unlike previous platform testing, Copilot doesn't have its default web content retrieval behavior publicly documented.
After the first successful `BL-1` run, the agent reported using a tool called `fetch_webpage` - but this tool has
no public docs. Asking Copilot directly returns a deflection:

```markdown
"Sorry, I'm unable to answer that question. Check that you selected the correct GitHub version or try a different question."
```

This is consistent with the `@Web` evolution pattern documented in
[Cursor's Friction Note](/docs/anysphere-cursor/friction-note.md#web-undocumented-requires-reverse-engineering);
the fetch mechanism is agent-selected, undocumented, and surfaces only through tool logs.

During `OP-4` run 3 on the interpreted track, `GPT-5.3-Codex` produced the clearest characterization of `fetch_webpage`'s
behavior observed across all interpreted-track runs. The agent explicitly stated that `fetch_webpage` doesn't perform raw
HTTP retrieval, but returns relevance-ranked semantic excerpts based on the query string provided, with `...` markers
between contextually selected chunks. The tool response preamble visible in the output confirmed this directly:

```markdown
"Here is some relevant context from the web page [url]:"
```

This preamble, not a raw payload header, indicates a retrieval model that samples and ranks content rather than fetching
it sequentially. The full ~250 KB page was never delivered; no contiguous truncation boundary exists because the content
was **never contiguous to begin with**. This reframes what truncation means on the interpreted track: results logged as
truncated may be more precisely described as **incompletely sampled**, and the `...` markers throughout responses are
elision indicators from the retrieval model, not byte-boundary cutoffs.

This also has direct implications for `OP-4`'s test hypothesis. The hypothesis assumes a sequential fetch that the agent
could paginate by requesting the next chunk, but `fetch_webpage`'s relevance-ranked mechanism means there is no sequential
chunk 2 to request. This fetch mechanism alone can't confirm or deny `OP-4`'s hypothesis; it would require a different
retrieval tool to test meaningfully.

A related pattern has emerged across multiple runs on the MongoDB Atlas Search tutorial URL, appearing in both `OP-4` and
`BL-3`: the agent self-diagnoses the first fetch result as a "condensed page extraction rather than a clean raw dump" and
issues a corrective re-fetch against the same URL. The re-fetch returns the same kind of output, because the excerpted
result isn't a retrieval error, it's the expected output of `fetch_webpage`'s architecture. The agent is misidentifying a structural property of the tool as a transient failure and attempting to correct it. This means the agent itself doesn't
have accurate knowledge of what its own retrieval tool does, which is consistent with `fetch_webpage` as unclear
at the model level. The re-fetch attempts don't produce fuller content, but produce a second relevance-ranked sample of
the same page, logged as additional fetch invocations in the run notes.

**Impact**: can't treat `fetch_webpage` as a stable, documented mechanism. Its behavior, size limits, and
invocation conditions are opaque; results logged as `method: fetch_webpage` reflect **observed tool output**,
not an API contract. The `OP-4` finding additionally suggests that character count comparisons across runs may
reflect relevance-ranking variance as much as size-limit truncation. The tool may return different content samples for the
same URL depending on the query string provided to it. The retrieval layer's internal query parameters aren't surfaced in
chat output. If `fetch_webpage` passes a query string or context vector to its relevance model, that parameter is invisible
to the interpreted track. Prompt differences can't be responsible for excerpt selection differences because each track has
identical prompts - but don't rule out excerpt selection out as retrieval-layer sensitivity as something the agent passes
internally.

>not a single run has reported full content returned. That's not a finding about any individual run, it's a finding about fetch_webpage as a mechanism: full sequential retrieval may simply not be something it's capable of, by design. The agent in this run made that explicit by clarifying its measurements describe the tool response, not the underlying page

---

## Free Plan Quota Exhausted Mid-Testing

Free GitHub Copilot accounts have a monthly chat message quota that may exhaust
mid-session. During `SC-2` run 3 on the interpreted track, Copilot returned:

```markdown
"You've reached your monthly chat messages quota. Upgrade to Copilot Pro
(30-day free trial) or wait for your allowance to renew."
```

This interrupted testing after 12 total runs across `BL-1`, `BL-2`, and `SC-2` -
short of the full baseline path defined in the framework.

**Impact**: free-tier quota limits the number of comparable runs achievable in a
single session, making it difficult to complete a full baseline before the allowance
resets. Tests involving multiple runs for variance measurement are particularly affected,
since each re-run of the same test ID consumes quota without producing new URL coverage.

**Fix**: Copilot Pro at $10/month is half the price of Cursor - possibly continuously free
if testing within a 30-day trial period; signing up removes the message quota. Budget at
minimum three runs per test ID plus additional runs for variance on `BL-1` and `BL-2` -
approximately 15–20 messages for a complete interpreted-track baseline.

---

## Metric Precision - Interpreted Track

Copilot's testing prompt asks for total character count and estimated token count. On the interpreted
track, neither figure is reliably precise. Character counts frequently come back as ranges rather than
exact integers, and token counts follow the same pattern since they're derived from the character estimate
using a fixed ~4 chars/token heuristic. As Copilot returns ranges, `results.csv` logs the midpoint as the
scalar value in `output_chars` and `tokens_est`.

The imprecision isn't a prompt compliance problem, but reflects a **real constraint of the interpreted track**.
The agent receives excerpted, ellipsis-compressed content from `fetch_webpage`, not the raw page, so _it can't
count characters it never saw_. Pushing for exact figures would produce **false precision** without improving
measurement quality. The range is the correct result given the input the agent actually has.

**Impact**: treat `output_chars` and `tokens_est` on the interpreted track as _order-of-magnitude orientation figures_,
**not exact measurements**. They're sufficient for confirming that truncation occurred and estimating the retrieval
rate against expected page size, but not for _fine-grained comparison_ across runs or platforms. Raw track outputs
are the only source of exact counts.

**Methodology Decision**: no prompt change - continue logging midpoint values for ranges and note when a range returns
vs a single figure, as the distinction is itself a signal. Runs where the agent can return an exact count may
indicate a different fetch output format than runs where it can't, confirmed in `SC-2` interpreted run 5 in which
`GPT-5.3-Codex` returned exact figures rather than ranges. The same run that produced four fetch invocations, suggesting
the _additional retrieval attempts_ may have given the model enough payload visibility to count precisely rather
than estimate.

---

## Output Integrity: Duplicated Response Sections

During `BL-2` runs 2-3 on the interpreted track, the model duplicated sections 6 -
`Model's Perceived Completeness`, and 7 - `Tool Visibility`, in its response; the same content
appeared twice in sequence with no indication that the repetition was intentional or an error.
`Auto` selection of `Claude Sonnet 4.6` and `Raptor mini (Preview)` producing duplication
suggests that the behavior _isn't model-specific_, but possibly triggered by other factors like
response structure, as prompt structure nearly identical across tracks. This complicates testing
in a few ways:

- **Inflated Character Counts**: if the agent is also estimating character counts from its
own output rather than from the raw tool response, duplicated sections silently inflate the
reported figure, making truncation appear less severe than it is
- **Undetectable Without Careful Reading**: the duplication doesn't produce an error or
warning; a researcher logging results from a quick scan could record the wrong metrics
- **Ambiguous Cause**: it's unclear whether the duplication originated in the `fetch_webpage`
tool response itself, or introduced by the model during report generation; the two
failure modes have different implications for measurement reliability

**Impact**: treat interpreted-track character counts should as approximate even when
the agent reports a specific figure; manual verification against the raw tool response is
the only reliable check; note the duplication in log entries, as it invalidates the Copilot-reported
character count as a standalone measurement

**Fix**: cross-reference interpreted-track reports against raw-track outputs for the same
URL before treating character counts as comparable data points

---

## Prompt Format Affects Output Structure

During `OP-4` run 3 on the interpreted track, the numbered list was accidentally omitted from the request.
The agent returned results in a Markdown table rather than the prose sections produced by runs 1 and 2. The underlying fetch behavior and findings were consistent with prior runs, the prompt format difference affected response structure only, not the fetch mechanism or metric values.

This is a prompt compliance risk: if output structure varies with prompt formatting, manual result logging becomes harder to scan consistently, and fields like the last 50 characters verbatim are easier to misread
in a table than in a labeled prose section. It also raises the question of whether output structure differences could mask metric differences. A table that truncates cell content, for instance, would silently drop characters that a prose response would include.

**Fix**: verify the numbered prompt format is intact before submitting each run. Consider adding a format check to the framework's `generate_interpreted_prompt` output so the structure is always explicit.
