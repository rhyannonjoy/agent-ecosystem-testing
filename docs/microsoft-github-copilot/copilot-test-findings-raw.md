---
layout: default
title: "Key Findings for Copilot's Web Fetch Behavior, Raw"
permalink: /docs/microsoft-github-copilot/copilot-test-findings-raw
parent: Microsoft GitHub Copilot
---

## Key Findings for Copilot's Web Fetch Behavior, Raw

---

`BL-1` run 5

1. `accept-ranges: bytes` - Yes, this is significant. It means the MongoDB server supports HTTP range requests (RFC 7233). GPT models could theoretically request partial content like Range: bytes=0-100000, but there's no evidence they're doing so - the full 508KB was downloaded in one shot.
2. Headers file capture - Copilot explicitly saved the HTTP response headers separately, showing it's aware of HTTP metadata. This is interesting behavior that didn't appear in earlier runs.
3. Self-report accuracy improved - This run shows Copilot correctly reporting 15,370 words (matching verifier), unlike run 4's 80,668 overestimate. Same model family, different accuracy - suggests nondeterministic counting logic or different execution path.
4. Structure detection - Copilot found HTML structures (code blocks, table rows, headers) that the verifier can't detect because it only knows Markdown syntax. This is expected but worth documenting.
5. CDN metadata visible - CloudFront delivery, Netlify Edge, cache miss - all potentially relevant for understanding how content is served and whether caching affects retrieval behavior.

---

`BL-2` run 1

Claude models may apply aggressive content filtering even on native Markdown URLs, not just
HTML-to-Markdown conversion

1. Truncation explicitly acknowledged - Copilot reported "content does NOT end cleanly" with ellipsis markers (...), confirming intentional summarization not accidental cutoff
2. execution_attempts = 5 - You're right to count action verbs: "Retrieved" (1), "Created" (2), "Ran" terminal command (3), "Ran" terminal again (4), "Ran content-agent" script (5) = 5 execution attempts
3. Mixed HTML/Markdown output - Table HTML preserved (<tr>) but surrounded by markdown structure, confirming Copilot isn't doing clean format conversion but selective filtering
4. CDN staging server - Content came from cdn.mongodb.com not production docs.mongodb.com, which could affect content/headers
5. Summarization markers - Ellipsis characters are literal truncation/summarization indicators, not natural content endings
6. Claude vs GPT divergence confirmed - Claude: 6.13KB filtered markdown with summarization; GPT (BL-1): 496KB raw HTML complete. Dramatic difference in retrieval strategy between model families on identical content (just different URL encoding).
7. Structure detection issues - Code blocks, table rows, headers all show divergence between Copilot's counts and verifier's, likely because: (a) Copilot counted HTML table syntax while verifier looks for markdown tables, and (b) summarization omitted sections the verifier could have counted

run 2

1. Consistent across runs - BL-2 run 1: 6,273 bytes; BL-2 run 2: 6,272 bytes. Only 1 byte difference, confirming deterministic summarization ceiling for Claude models on markdown URLs.
2. execution_attempts = 4 - Counted as: "Retrieved" (1), "Fetched" (2), "Saved" (3), "Created" file + "Ran" command twice (4). You're right - significantly fewer steps than BL-1's multi-tool chain.
3. Simpler tool chain - Only fetch_webpage used, no curl -> dd -> wc -> md5 -> python3 fallback chain. Markdown URLs trigger cleaner execution path.
4. MD5 match confirms integrity - Copilot and verifier agree on checksum aec771dbf406a02e09efba1c4bc8ac4e, validating file wasn't corrupted.
5. Ellipsis markers confirmed - Final 3 bytes are literal ASCII periods 2e 2e 2e (hexdump shows this), confirming intentional summarization markers not data corruption.
6. Staging CDN metadata - URLs point to mongodb-cdn-api.staging.corp.mongodb.com, revealing internal infrastructure details visible in href attributes.
7. Less noisy interaction: compare BL-1 (GPT, HTML): verbose multi-step terminal output, fallback chains, headers files. BL-2 (Claude, Markdown): concise report, single tool, clean output. Markdown URLs produce quieter, more deterministic behavior.
8. Structure count divergence pattern repeats - Same discrepancies as run 1: Copilot sees HTML table syntax (14 rows), verifier sees markdown (0 rows). Confirms these aren't random errors but systematic detection differences.

run 3

saved file begins with Copilot's own framing text rather than the raw payload; prompt compliance failure

---

SC-2

GPT family also uses the markdown with Copilot's own framing text rather than the raw payload; prompt compliance failure with HTML to Markdown conversion; semantically truncated/ellipsized rather than byte-truncated

---

OP-4

This is the opposite of every SC-2 run, where Copilot aggressively converted HTML to Markdown. Here Copilot saved the raw HTML verbatim with no conversion. Yet the plain language tutorial content is absent, the HTML is likely JavaScript-rendered content that was not executed, so only the HTML shell was captured, not the rendered text.

The failure mode is pre-truncation, the retrieval layer never got renderable content to begin with.

Run 3 adds the "Here is some relevant context from the web page" framing wrapper (same as SC-2 runs), which was absent in Run 2. Same model selector, same URL, different framing behavior, suggests the framing injection is non-deterministic at the retrieval layer level

---

Halfway into the raw track, Copilot started to make observations about its own tasks, started comparing the run raw outputs

---

BL-3

1. Order isn't preserved. The rendered page opens with the intro paragraph, the numbered overview steps, and "Time required: 15 minutes" - none of that appears at the top of the raw output. The raw output jumps straight to ## NOTE as the first content block, skipping the entire introductory section. The rendered page's NOTE box appears after the intro; in the raw output it's first.

2. The `...` separators between repeated # MongoDB Search Quick Start headers aren't in the rendered page at all. The page has one # MongoDB Search Quick Start H1 at the top. The raw output repeats it dozens of times as a section delimiter pattern, this is an artifact of the retrieval layer's chunking or context injection format, not a reflection of page structure. The rendered page uses a single H1 and then H2/H3 subheadings throughout.

3. Content is selectively extracted, not verbatim. The rendered page includes: the preview warning banner, deployment type/language selector UI, star rating widget, the "On this page" sidebar TOC, accordion expand/collapse UI elements, and the full footer. None of these appear in the raw output in their rendered form, they're either stripped entirely or converted to minimal text like `[Image: Chevron Right Icon]`

4. The accordion pattern is flattened. On the rendered page, "What is a Search Index?" and "What are Atlas Search queries?" are expandable accordions with chevron indicators. In the raw output they appear as ## What is a Search Index? followed by [Image: Chevron Right Icon] and then the content, the interactive structure is lost but the content is present.

5. The code blocks are present but reformatted. The rendered page shows syntax-highlighted JSON in a proper code editor widget with line numbers and a copy button. The raw output preserves these as Markdown code blocks or as pipe-delimited table rows, the content is there but the formatting is transformed.

6. The "On this page" TOC appears at the end, not the side. In the rendered page it's a fixed sidebar. In the raw output it appears near the bottom of the document as a flat list, the retrieval layer apparently appends it rather than stripping it.

7. The footer content is included verbatim. Careers, Investor Relations, Legal, Privacy Policy, GitHub, etc. all appear in the raw output. This is low-value boilerplate that a summarizer would typically strip, its presence confirms the retrieval layer is not doing semantic relevance filtering on footer content.

What kind of relevance/summarization is Copilot doing?

It isn't doing semantic summarization; the tutorial prose content is preserved with high fidelity. It is doing structural transformation: HTML-to-Markdown conversion, accordion flattening, sidebar repositioning, UI element stripping, and injecting the repeated # MongoDB Search Quick Start header pattern as a chunking artifact. The `...` ellipsis separators between sections appear to be the retrieval layer's way of indicating content gaps or section boundaries in its internal chunked representation, they aren't present in the source page.
The most significant finding: the order is partially preserved but the opening is truncated from the front. The rendered page's intro (the paragraph beginning "MongoDB Search is an embedded full-text search feature...") does appear in the raw output, but only near the bottom in the repeated TOC/summary section; not at the top where the page actually renders it. The retrieval layer appears to be injecting content in a non-linear order that reflects its internal document chunking rather than the page's visual reading order.

the framing wrapper is injected upstream of the retrieval result, not part of the page content, and that the underlying retrieved content is nearly identical between calls.

`fetch_webpage` performs HTML-to-Markdown structural transformation with chunk-based reassembly, not truncation or semantic filtering

The retrieval layer is doing chunked extraction with injected section headers as delimiters, non-linear reassembly (intro appears near the bottom, not the top), UI stripping (accordions flattened, widgets removed), and footer preservation (boilerplate included verbatim, no semantic relevance filtering). The ... separators and repeated # MongoDB Search Quick Start headers are chunking artifacts, not page content.

The headers file is genuinely informative. Looking at what's visible:

content-type: text/html; charset=UTF-8 - confirms the server returned HTML, not markdown. fetch_webpage's markdown conversion happens client-side in the tool layer, not server-side.
accept-ranges: bytes - the server supports range requests (HTTP 206 partial content). This is significant: it means byte-range fetching is technically possible, but fetch_webpage doesn't appear to use it - it requests the full document and then truncates/transforms internally.
cache-status: "Netlify Edge"; hit - the response was served from Netlify's edge cache, not origin. Combined with x-cache: Miss from cloudfront and the CloudFront via header, there are two CDN layers (Netlify Edge in front, CloudFront behind), which explains why the same URL can return slightly different content across runs if cache state varies.
etag: "720fd920e3b8e6c735a0b2e9c7c54138-ssl" - the etag is stable, suggesting the underlying content hasn't changed between runs, which supports the interpretation that output variance across runs reflects fetch_webpage's internal chunking behavior, not server-side content changes.

For the notes addition, I'd add something like this to the existing log:
"Copilot non-deterministically created a headers file (raw_output_BL-3.headers.txt) alongside the body artifact - behavior not requested by the prompt and not consistent across runs, suggesting the agent autonomously decided to capture HTTP response metadata. Headers confirm server returned text/html not markdown - fetch_webpage's conversion is tool-side not server-side. accept-ranges: bytes indicates the server supports partial content requests but fetch_webpage does not appear to use range requests, performing full-document retrieval with internal transformation instead. Dual CDN layer visible (Netlify Edge hit, CloudFront miss) - cache state variance across layers is a plausible explanation for output differences between runs where MD5 differs despite identical URL and prompt."

the headers file appearance is itself a behavioral data point about agentic over-delivery, and the accept-ranges finding directly addresses whether chunked HTTP retrieval could explain the size ceiling, and the answer is no.

---

SC- 1

`fetch_webpage` sometimes retrieves static HTML source without executing JS, so rendered documentation prose is absent despite full 125KB retrieval

nearly identical raw outputs 1-3, what starting to look at is the Method/identifier strings visible: generate_content, url_context_metadata, URL_RETRIEVAL_STATUS_SUCCESS, URL_RETRIEVAL_STATUS_UNSAFE

Fourth run chunk-based reassembly, not semantic filtering; the retrieval layer is doing HTML-to-text conversion that strips rendering but preserves material icon text nodes; sections are represented, but it's also summarizing/filtering in non-linear order; it's a combination of both, there is ellipsical `...`

Hypothesis: H3-yes is the strongest reading; the content ends cleanly, structure is preserved within sections, and the transformation respects markdown boundaries. But the non-linear order means it's not truly structure-aware in a reading-order sense.

---

SC-4

re: headers

It has no effect on what the client does with a complete response after receiving it. The header is passive infrastructure metadata; it doesn't constrain the agent's post-retrieval behavior in any way.

Complete retrieval and useful output are separable. The 65,622-byte transfer confirms curl got the whole page. The raw HTML output confirms nothing transformed it afterward. These are two independent outcomes that happened to co-occur, and the reason they co-occurred is the curl substitution itself; curl is a transport tool with no content transformation layer. It has no relevance model, no Markdown renderer, no excerpt assembler. It delivers bytes and stops. Whatever transformation fetch_webpage applies to produce readable output, curl simply doesn't have it.

The raw HTML output isn't a retrieval failure and it isn't caused by accept-ranges. It's the expected output of a tool that was never designed to produce anything else. The agent substituted a complete-retrieval tool for a transformation-capable tool, got complete retrieval, and delivered it verbatim. From a data fidelity standpoint the transfer is perfect. From a usability standpoint it's the wrong tool for the task.

`fetch_webpage` transforms aggressively and doesn't document what it discards. curl doesn't transform at all and doesn't document that it's being substituted. The agent's self-report that it can suppress summarization on request is inaccurate in both cases: you can't suppress fetch_webpage's transformation layer through prompting, and curl has no transformation layer to suppress or enable.

What the SC-series data is accumulating is evidence that the agent's tool selection for a "fetch this URL" task isn't stable, not documented, and not controllable from the prompt. fetch_webpage and curl produce outputs that are so different in character: relevance-ranked excerpts versus complete raw HTML; that they can't be treated as equivalent conditions in the same test series. Your run_notes field capturing which tool was invoked is doing the right work here; the tool used is currently the most important variable in predicting output type, more so than URL, model, or prompt wording.

## `fetch_webpage` Output Quality Correlates With Source HTML Structure

Across SC-series raw track runs on `fetch_webpage`, output quality varies with the
structural characteristics of the source page. SC-4 run 3 (`Claude Sonnet 4.6`) retrieved
markdownguide.org/basic-syntax/ via `fetch_webpage` and produced well-formed processed
Markdown: complete prose sections, code blocks, blockquotes, tables, and navigational
structure, at 29,984 bytes against a 65,622-byte HTML source, a 46% retrieval rate.
This is the highest-fidelity `fetch_webpage` output observed across the SC series.

markdownguide.org is structurally favorable for HTML-to-Markdown conversion: minimal
JavaScript, clean semantic HTML, content that maps directly onto Markdown primitives
(headings, fenced code blocks, tables, blockquotes), and no CDN-rendered or
JavaScript-dependent content sections. Pages with heavier JavaScript, navigation
chrome, or dynamic content have consistently produced lower-fidelity output across
other test IDs.

This finding suggests `fetch_webpage`'s transformation quality isn't uniform, it
reflects the convertibility of the source HTML as much as any fixed tool capability.
Retrieval rate and output fidelity comparisons across test IDs should account for
source page structure as a variable, not only URL length, page size, or content domain.

The conversion isn't lossless even on favorable source material: table column headers
were dropped, the top navigation panel was relocated to the bottom of the output, and
ad network content was included alongside page content. The 46% retrieval rate and
structural losses confirm that `fetch_webpage` is performing transformation, not
faithful reproduction, even under favorable conditions.

**Stability caveat**: 2 of 5 SC-4 runs produced transformed Markdown via `fetch_webpage`;
the remaining 3 produced raw HTML via `curl` substitution. The favorable output is
real but not reliable. Source HTML structure may be a necessary condition for
high-fidelity `fetch_webpage` output but isn't sufficient to guarantee it, since
tool selection remains outside prompt control.

---

SC-4 The agent solved for fidelity and lost readability, which is exactly the inverse failure mode.
