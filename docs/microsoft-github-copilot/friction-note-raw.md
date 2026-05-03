---
layout: default
title: "Friction Note"
permalink: /docs/microsoft-github-copilot/friction-note-raw
parent: Microsoft GitHub Copilot
---

# Friction Note: Roadblocks While Refining Methodology

---

## Agentic Metric Computation

The raw track prompt asks Copilot to retrieve content, save it to a file, and self-report
some metrics. The plan: Copilot reports these figures, the verification
script measures the same figures from the saved file, and document any discrepancies.
In early raw track runs, Copilot's response to this prompt was noticeably more verbose and
process-heavy than Cursor's. Where Cursor retrieved content and reported metrics with minimal
visible orchestration, Copilot consistently requested permission to use execution tools,
`pylanceRunCodeSnippet`, `zsh` shell commands, or both, to calculate the metrics rather than
estimating-reporting from the retrieval output directly. The initial instinct was to skip
these tool requests, consistent with the interpreted track approach of suppressing script
execution to keep the method consistent, but this instinct is wrong for the raw track.

The tool selection behavior Copilot exhibits when asked to report metrics isn't noise, but
the mechanism under observation. Skipping every tool request would have produced an uncomplicated
session, but a less informative one: the fetch-to-metric pipeline is exactly what the raw track
exists to document. Whether Copilot reaches for shell commands or accounts directly from the
retrieval payload, they're meaningfully different execution paths with different reliability implications.

| **Aspect** | **Cursor** | **Copilot** |
| --- | --- | --- |
| **Tool<br>Visibility** | _Opaque_, tools not<br>named in chat | _Verbose_, tool calls visible<br>and prompt-able |
| **Metric Computation** | Reported directly,<br>method not observable | Requests use of<br>execution tools |
| **Distinguishability** | Possibly doesn't separate direct count from estimate | Execution path observable, though blocked tools may still produce fabricated values |
| **Raw Track Measurements** | Output fidelity | Output fidelity, tool<br>orchestration behavior |

`SC-4` run 3 used `Claude Sonnet 4.6` and `fetch_webpage` to produce the sharpest metric discrepancy
in the dataset. Copilot reported two separate code block counts in the same response -
`fenced code block delimiter lines: 48` and `code blocks (pairs): 24` without reconciling them or flagging
the inconsistency. The verification script measured 25, consistent with the pairs count but not the delimiter count.
The delimiter count likely reflects the agent counting opening and closing fence markers as individual lines
rather than as matched pairs, a counting methodology difference that the prompt doesn't specify. Copilot also
omitted table rows entirely from its report despite the prompt requesting them. The verification script measured 111.
The character count delta - Copilot: 29,984 vs verification script: 29,949, a difference of 35, Copilot output explains
that `wc -c` counts bytes rather than Unicode code points, with the gap representing multi-byte `UTF-8`
characters, including emojis. File size, word count, and header count matched exactly. The pattern suggests
metric precision varies by field type: size and word counts are reliable, character counts require encoding
disambiguation, and structural counts like code blocks and table rows are methodology-dependent and currently
not specified in the prompt.

**Methodology Decision**: treat Copilot's metric computation attempts as observable data, not prompt
violations. Expand the data schema from the Cursor-derived baseline and include log tool invocations,
blocks, skips, and execution attempts while Copilot produces a result. Distinguish Copilot's self-reported
values from independently measured values produced by the verification script because the delta between them
is the finding.

---

## Agentic Over-Delivery, Headers Generation

Across baseline tests Copilot nondeterministically created a second file alongside the requested raw output artifact:
_`raw_output_{test_id}.headers.txt`_ containing the HTTP response headers. The prompt never requests this file.
This behavior is agent-initiated. Copilot deciding autonomously that capturing response metadata would be
useful, inconsistently, makes it uncontrollable as a variable and unverifiable as a complete dataset.

This is agentic over-delivery. The agent doesn't just complete the task, it expands the task boundary based on its
own assessment of what would be useful, producing artifacts unprompted and if unchecked, no one may notice. In this
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
the `BL-3` run 5 file contains content from throughout the page - intro, middle sections, footer, TOC - with **`. . .`** ellipsis
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
evidence that rule out an alternative explanation that the raw output text files can't support alone. The nondeterministic appearance
of headers files means the dataset is incomplete. Some runs have headers, most don't. The current data can't determine whether the
headers vary across runs for the same URL, indicating CDN cache state changes, or remain stable, indicating a consistent upstream
response. A controlled run set that explicitly captures headers every time would close this gap, but would require prompt and test
condition modification.

### Headers Generation: Two Distinct Trigger Paths

`SC-3` run 5 produced a headers file on a Wikipedia URL, but the mechanism differs materially from the `BL-3` case. In `SC-3`,
runs 4 and 5 didn't use `fetch_webpage` at all. The agent substituted `curl` for the fetch step. Run 5's headers file is `curl`
output, not a `fetch_webpage` side artifact. `curl` invoked with response header capture flags returns headers as a natural part
of its output; this isn't agentic over-delivery in the same sense as the `BL-3` case. It's the expected behavior of a different
tool entirely. At least two distinct mechanisms can produce headers files in the dataset:

- **`fetch_webpage` Side Artifact**: the agent autonomously saves response metadata alongside the raw output file,
as observed in `BL-3`. The retrieval tool is `fetch_webpage`. The headers reflect whatever upstream infrastructure
`fetch_webpage` hit on that run.
- **`curl` Substitution Artifact**: the agent replaces `fetch_webpage` with a direct HTTP call. Headers are
a structural output of `curl` when invoked with header-capture flags, not an autonomous agent decision to
capture metadata. `curl` is a transport tool with no content transformation layer that delivers bytes and
stops. `SC-3` run 5 retrieved 793,987 bytes from Wikipedia and `SC-4` run 2 retrieved 65,622 bytes from
`markdownguide.org`, both byte-perfect transfers confirmed by `content-length` matching saved file size exactly.
Both produced raw HTML with no plain-language content. _Complete retrieval and useful output are separable_:
`curl` substitution achieves the former and fails the latter by design.

The two cases look identical in the filesystem, as both produce a `.headers.txt` file, but have different
implications. A headers file from a `fetch_webpage` run is incidental agent behavior. A headers file from
a `curl` run is evidence of tool substitution, and the headers themselves reflect different infrastructure:
direct origin or CDN response rather than whatever `fetch_webpage`'s internal retrieval layer contacts.

The `SC-3` run 5 headers are the most complete and include size details:

```bash
content-length: 793987
x-cache: cp4043 miss, cp4043 hit/8
age: 14495
cache-control: private, s-maxage=0, max-age=0, must-revalidate, no-transform
server: mw-web.eqiad.main-544b794998-564l7
x-client-ip: 50.147.232.34
```

`content-length: 793987` approximately 775 KB, is the full Wikipedia page as served by origin. Whatever
size ceiling `fetch_webpage` runs have been hitting on this URL, it isn't the server imposing it, as the call
transferred the whole document. Any reduction in `fetch_webpage` runs is entirely tool-internal.

`age: 14495` means the cached copy was approximately four hours old at fetch time. Combined with Wikipedia's
`last-modified` timestamp of March 28, cache age is a plausible source of content-length variance across
runs if maintainers edited the page between fetches. This is the same CDN confounder documented in the `BL-3`
analysis, with direct evidence of cache age now available.

`x-client-ip: 50.147.232.34` is the outbound IP as seen by Wikipedia's infrastructure, the IP of Copilot's
execution environment, not the local machine. This confirms `curl` ran in Copilot's sandboxed environment
rather than delegating to a local shell. The fetch originated from Copilot's own infrastructure regardless
of which retrieval mechanism in use.

`server: mw-web.eqiad.main-544b794998-564l7` identifies the specific Wikimedia backend pod in the `eqiad`
datacenter. This level of specificity is only visible because `curl` bypassed any retrieval abstraction
layer and contacted Wikipedia's infrastructure directly.

All five `SC-3` runs used the same prompt against the same URL, selected `GPT-5.3-Codex`, and produced
only raw HTML with plain language content completely absent. The tool substitution on runs 4 and 5 didn't
change the output; the all-HTML output isn't explained by `curl` bypassing `fetch_webpage`'s transformation
layer. The cause is elsewhere: possibly the URL type, Wikipedia's HTML structure, `GPT-5.3-Codex`'s handling
of that structure, or some interaction between them, which isn't resolvable from the `SC-3` data alone.

**Impact**: headers files in the dataset aren't a uniform signal. Before treating a headers file as evidence
of agentic over-delivery, confirm which retrieval mechanism produced it. `fetch_webpage` headers files and
`curl` headers files both appear as `.headers.txt` artifacts but represent different agent behaviors with
different methodological implications. The log `notes` field should distinguish these cases. The 3-in-30
approximate rate of headers file appearance across all runs may be a compound of both trigger paths rather
than a single nondeterministic behavior. It isn't established whether `curl` substitution always produces a
headers file, or only sometimes, and whether `fetch_webpage`'s headers-generation is query-dependent,
URL-dependent, or genuinely nondeterministic. A controlled run set that logs retrieval mechanism alongside
headers file presence for every run would separate the two populations and establish whether the 4/32 rate holds
within each mechanism or possibly driven by one of them. A second open question follows from the inverse
failure mode finding: whether any prompt condition, model, or configuration exists within Copilot's
current tooling that produces both complete retrieval and useful plain-language output in the same run.
The dataset has no confirmed instance of this.

---

## Agentic Over-Delivery, Unsolicited Cross-Run Analysis

Across `SC`-series runs `GPT-5.3-Codex` and `Claude Sonnet 4.6` intermittently
produced unsolicited cross-run comparison tables after completing the requested test. The
prompt asks only for retrieval, file saving, and metric reporting for the current run. No
run requested comparison with prior runs, historical analysis, or trend summaries. The agent
produced them anyway, likely reading prior run artifacts from the workspace and deciding
autonomously that a comparison would be useful.

This is the same behavioral pattern as headers file generation: the agent expanding the
task boundary based on its own assessment of utility, but more methodologically disruptive
in two ways. First, the comparison output consumes context window that the current run's
retrieval and metric reporting should occupy, potentially crowding out or compressing the
requested content. Second, the agent must be reading prior run files from the workspace to
generate the comparison, which means workspace artifact accumulation across runs is actively
influencing agent behavior in subsequent runs. This is the same workspace-context sensitivity
that drives `pylanceRunCodeSnippet` substitution: the agent finds relevant-looking data in the
workspace and incorporates it without prompting.

The unsolicited comparison output also creates a logging risk: a researcher scanning the
response quickly could mistake the agent-generated cross-run analysis for prompted output,
or record metrics from the comparison table rather than from the current run's figures.

`SC-4` run 3 selected `Claude Sonnet 4.6`and produced a comparison table contrasting the current
`fetch_webpage` run against prior `curl`-based `SC-4` runs across content type, size, headers
visibility, readable prose, and navigation structure. The comparison was somewhat accurate but
unsolicited, and it included a claim that `fetch_webpage` doesn't return header content in its
output, but `BL-3` run 5 produced a headers file attributed to `fetch_webpage`. The most likely
reconciliation is that the `SC-4` run 3 agent is generalizing from its own run history, in which
headers appeared only on `curl` runs, without access to the full dataset. The claim is locally
consistent, but globally incomplete, and it illustrates a risk of the agent's self-analysis: it
synthesizes from whatever workspace artifacts are visible, not from the complete record.

A structurally distinct instance of the same behavior appeared in `EC-1` run 5 with `GPT-5.3-Codex`.
The prompt requests a hexdump of the last 256 bytes as a reported metric but inline, as part of the
report. The agent saved it instead to `raw_output_EC-1.last256.hexdump.txt` in addition to printing
it in chat. No prior run across the raw track dataset persisted hexdump output as a file artifact.
The content is accurate and confirms clean HTML closure with no mid-character truncation. But the
delivery decision was autonomous: the agent determined that a diagnostic output explicitly requested
in one form would be more useful in another form, and acted on that without prompting. This differs
from the headers file cases, which are either tool-substitution side effects or unrequested
metadata capture. The hexdump artifact is the agent reformatting a prompted output, not adding an
unrequested one, which makes it a subtler instance of the same boundary-expansion behavior.

**Impact**: unsolicited cross-run analysis is a signal that workspace artifact accumulation
is becoming an active variable in agent behavior. As the results directory grows, the agent
has more prior data to incorporate, making later runs in a session behaviorally different
from earlier ones in a way that isn't attributable to the test condition. This is a session
ordering confounder: run 3 of `SC-4` has access to run 1 and run 2 artifacts; run 1 doesn't.

**Fix**: consider whether clearing or relocating prior run artifacts between sessions, or
running each test ID in a fresh workspace context may suppress this behavior. Alternatively,
treat unsolicited comparison output as a logged variable: note its presence in the results log
and flag which runs triggered it, as its appearance may correlate with workspace artifact
volume or specific model routing.

---

## Explicit Tool Substitution Reasoning

`SC-4` run 4 selected `GPT-5.3-Codex` to produce the first instance of explicit tool substitution
reasoning in the dataset. Prior `curl` substitution runs completed via `curl` without explanation.
Run 4 stated the reasoning directly:

>_"The fetch tool only returns a condensed 'relevant context' view with omissions, so to satisfy your 'exactly as received' requirement
>I'm now capturing the URL response bytes directly via terminal."_

The agent correctly diagnosed `fetch_webpage`'s architectural behavior - relevance-ranked
excerpts rather than raw bytes - and deliberately switched to `curl` to satisfy the
verbatim requirement. The diagnosis is accurate and consistent with the `fetch_webpage`
characterization across the dataset. The consequence is the one documented across `SC-3` and
`SC-4` runs 2 and 4: complete byte-faithful retrieval of raw HTML with no transformation.
The agent solved for the wrong half of the requirement. "Exactly as received" in the
context of a web content retrieval test _implies readable content_; the agent interpreted
it as byte fidelity. Both interpretations are defensible, and the prompt doesn't disambiguate them.

Throughout the raw track runs, the agent demonstrated cross-run workspace awareness explicitly in
its reasoning chain: it checked for an existing _`raw_output_SC-4.txt`_ before proceeding, found none,
and cited this as justification for writing a new file. The agent is reading prior run artifacts to
avoid overwriting, demonstrating prompt-compliant behavior, but the same workspace reading that
produced correct file-management behavior didn't produce correct metric computation behavior. Terminal
execution errors occurred intermittently during metric collection despite the agent having correctly
reasoned about the fetch step. Workspace awareness and execution reliability appear to be
independent: the agent can read and reason about prior artifacts without that reasoning carrying over
into reliable shell execution.

**Impact**: explicit tool substitution reasoning is a more observable failure mode than silent substitution,
but it **isn't a more controllable one**. The agent's diagnosis of `fetch_webpage`'s limitations is correct;
its solution produces the inverse failure mode documented across the `SC` series. A prompt that disambiguates
_"exactly as received"_, specifying whether this means byte fidelity or readable content, might produce different
tool selection, but given the architectural constraint that `fetch_webpage` can't satisfy both simultaneously,
any clarification forces a choice between the two halves of the requirement.

---

## Metric Underspecification

`SC-4` run 4 identified a metric counting ambiguity that raw HTML output exposes, but
processed Markdown output conceals. Copilot reported 24 code blocks and 35 table rows
from the raw HTML file; the verification script reported 0 code blocks and 0 table rows from the
same file. Both counts are correct within their respective methodologies:

- Copilot counted HTML structural elements: `<pre>` tags for code blocks, `<tr>` tags
  for table rows
- The verification script counted Markdown syntax patterns: fenced code blocks (` ``` `) for code
  blocks, pipe-delimited rows (`|`) for table rows

On a processed Markdown file, `SC-4` run 3, both methodologies converge because the
transformation layer has already converted HTML structure to Markdown syntax. On a raw
HTML file, they diverge completely. The prompt specifies neither methodology, making
the counts incomparable across runs that produce different output formats, which is
exactly the condition the `SC` series produces nondeterministically.

The token count discrepancy follows a related pattern. Copilot's `chars/4` heuristic
reported 16,485 tokens; the verification script's `cl100k_base` tokenizer measured 18,645, a gap
of 2,160. HTML is token-dense relative to prose because tag syntax, angle brackets,
attribute names, quoted values, it's likely to tokenize less efficiently than natural
language. The fixed heuristic underestimates this systematically, and the underestimate
scales with the proportion of HTML markup in the file. On processed Markdown output the
heuristic performs better because the markup density is lower.

**Impact**: the metric incomparability across `SC-4` runs is a symptom of a deeper framework
assumption failure. The verification script script, the prompt's metric definitions, and the cross-run
comparison structure all assume processed Markdown output, because that's what a web content
retrieval tool might produce. When `curl` substitution delivers raw HTML instead, that assumption
breaks silently: the verification script produces zeros, Copilot counts HTML structural elements, and neither
figure is wrong so much as answering a different question than the framework intended. The breakdown
isn't a measurement precision problem, but evidence that tool selection instability propagates upward
into the entire measurement layer. A framework designed to measure retrieval quality can't do that job
_when the retrieval mechanism is itself the uncontrolled variable_. Fixing the verification script to handle both
formats would recover some comparability, but it would also normalize a failure mode that the zeros
currently make visible. The zeros are informative: they mark the runs where the expected output never
arrived.

---

## Prompt Refinement Can't Suppress Retrieval-Layer Transformation

A direct test of whether prompt engineering can override `fetch_webpage`'s internal transformation behavior produced
a negative result: no wording, however explicit, recovers full sequential page content from `fetch_webpage`
because the transformation occurs before the model receives the payload.

The original raw track prompt instructs Copilot to retrieve a URL and return content exactly as received. After
observing output filtered for _"relevance"_ that results in non-linear, accordion-like, and structurally
reassembled rather than sequential, Copilot revised the prompt to better suppress this behavior. The revised prompt
was significantly more verbose and explicit, adding structured delimiters `BEGIN_RAW_CONTENT` / `END_RAW_CONTENT`,
explicit metadata fields, conditional flags - `TRANSFORMED_BY_RETRIEVAL_LAYER:YES`, `TRUNCATION_DETECTED:YES`, and
a direct instruction to report `RAW_BYTE_IDENTICAL_UNSUPPORTED` if byte-identical transfer isn't possible. **Both prompts
produced the same output for the same URL: non-sequential, ellipsis-compressed, structurally reassembled content**.

This result is consistent with the `fetch_webpage` architectural characterization documented in
[`fetch_webpage` Undocumented](friction-note-interpreted.md#fetch_webpage-undocumented). The agent-authored prompt revision
is better in format, in that it produces more parseable metadata and provides an explicit compliance exit ramp via
`RAW_BYTE_IDENTICAL_UNSUPPORTED`, but it doesn't and can't produce different retrieval content, because the instructions
reach the model after `fetch_webpage` has already processed and transformed the page. Telling the agent not to summarize is
downstream of the summarization.

When asked directly about its retrieval behavior, `GPT-5.3-Codex` confirmed this architecture while simultaneously
mischaracterizing it as suppressible:

>_"If you ask for raw or near-raw retrieval, I can avoid summarization-focused rewriting and return the fetched content with minimal transformation."_

>_"Practical note: some minimal handling may still occur for readability or tool-output shaping."_

The agent frames retrieval-layer transformation as a stylistic choice it can dial back on request, while simultaneously
acknowledging that some transformation is unavoidable. The framing obscures the distinction between two separate processes: the
model's post-retrieval rewriting, which prompt instructions can suppress, and `fetch_webpage`'s internal relevance-ranking and
excerpt assembly, which they can't. A user following the agent's own instructions, _"just ask for raw output,"_ would receive the
same transformed content with more **confident framing around it**, with no indication that the transformation is just architectural.

**Impact**: prompt refinement is the wrong tool for this problem. The revised Copilot prompt is more useful than the original for
metadata parsing and for giving the agent explicit language to signal when byte-identical retrieval isn't supported, but neither
prompt recovers content that `fetch_webpage` didn't return. Characterizing Copilot's output as _"summarized"_ or _"filtered by the model"_
is also imprecise. The more accurate characterization, consistent across multiple run observations, is that `fetch_webpage` performs
relevance-ranked excerpt assembly and the agent receives a pre-transformed payload. Agents layer post-retrieval behavior on top of
that and is the only layer prompt instructions reach.

>_Open Question: Copilot's self-report suggests the query parameter is agent-authored per invocation and not exposed in chat output.
>If the query string drives excerpt selection, variance in output content across identical runs may reflect query string variance rather
>than retrieval-layer nondeterminism. This parameter isn't currently loggable without access to tool
>call internals. A controlled test passing a fixed, explicit query string, if the tool surface allows it, would isolate whether query
>variance is a meaningful source of output variance_.

---
