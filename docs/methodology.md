# Methodology

## How this testing differs from Dachary's spelunking

[Dachary Carey's Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/)
article documented Claude Code's web fetch behavior by interacting with Claude directly in a chat
interface. This testing took a different approach, targeting a different tool.

**Dachary** talked to Claude Code directly in a chat interface, asked it to fetch pages
and report back what it received, then observed the outputs. Claude Code's web fetch has a
summarization model in the middle - so what Dachary was measuring was what the summarization model,
Claude 3.5 Haiku, reported back after processing the fetched content. The data was filtered through
two layers of AI interpretation before Dachary saw it.

**This testing** uses a Python script to call the Anthropic API directly, with the
`web_fetch` tool enabled. The API tool doesn't have an intermediate summarization model; the
fetched content goes straight into the main model's context as a document block. The second script,
`web_fetch_raw.py`, goes one step further and extracts the raw content directly from the response
object in Python, bypassing Claude's interpretation entirely. Character counts and boilerplate
percentages are measured by Python string operations, not estimated by a model.

**Why this matters for the spec**: Dachary was documenting Claude Code's behavior. This testing
documents the Claude API `web_fetch` tool's behavior. These are genuinely different implementations
with different pipelines, which is exactly the gap in
[the Known Platform Limits table](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits)
that this testing fills. Dachary's CSS problem - the summarization model seeing only CSS -
doesn't reproduce in the API tool because the pipeline is different. That isn't a contradiction, but
evidence that the two tools work differently, which is a useful finding for tech writers who may be
using one or the other.

---

## Claude-interpreted vs Raw

Two scripts were used to test the same URLs: `web_fetch_test.py` - Claude-interpreted - and
`web_fetch_raw.py` - raw programmatic measurement. The conclusions are similar: both confirm no CSS
indicators, heavy boilerplate, cleaner markdown, and mid-content truncation from `max_content_tokens`
— but the two scripts produce meaningfully different data in three ways:

1. **Measurement accuracy is completely different.** The Claude-interpreted script estimated
13,700–14,200 chars for the short HTML page. The raw script measured 25,925 chars, nearly double.
Claude was significantly underestimating. For the spec, only the raw numbers are citable.

2. **The raw script found something the interpreted script missed.** The default truncation limit
finding - that Test 3 truncated at 20,696 chars even with no `max_content_tokens` set - only appears
in the raw results. Claude attributed the missing content to JavaScript rendering rather than a
character limit. Both were actually happening simultaneously, but Claude only noticed one cause.

3. **The raw script quantifies boilerplate precisely.** "81% boilerplate before the first heading" and
"97.5%" are exact, reproducible measurements. Claude's equivalent estimates - "~60-65%" - varied between
runs of the same test. For the spec PR, the raw numbers are what belongs in the Known Platform Limits
table.

The interpreted script is still useful as a record of what the model _perceives_ it received, which
is arguably what matters most for tech writers. A model that receives 25,925 chars but estimates
13,700 is working with a distorted picture of the content, and that gap itself is a finding worth
noting.

---

## Script comparison

| | `web_fetch_test.py` | `web_fetch_raw.py` |
| - | --------------------- | --------------------- |
| What it measures | Claude's interpretation of fetched content | Raw content extracted directly from response object |
| Character counts | Claude estimates - vary between runs - | Python `len()` on raw string - exact, reproducible |
| Boilerplate detection | Claude's subjective assessment | CSS indicator strings counted programmatically |
| Truncation detection | Claude reports what it perceives | Exact char position, end character, clean/unclean flag |
| Token cost per run | Higher - Claude writes long assessments | Lower  - minimal prompt, `max_tokens=128` |
| Best used for | Understanding what the model perceives | Citable measurements for the spec |
