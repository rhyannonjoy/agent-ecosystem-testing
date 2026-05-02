---
layout: default
title: "Gemini-interpreted vs Raw"
nav_order: 2
permalink: /docs/google-gemini-url-context-tool/gemini-interpreted-vs-raw
parent: Google Gemini URL Context
---

# Gemini-interpreted vs Raw

---

## Track Design

**Gemini-interpreted** captures what Gemini _believes_ it retrieved: how much content it saw, whether a fetch
felt complete, how it characterizes a failure. This is the agent's self-report. The **raw track** captures
what the API _actually returned_: exact `url_retrieval_status` codes, token counts from `usage_metadata`,
URL counts in `url_context_metadata`. These are Python `len()` calls and dictionary lookups and not agent
estimates.

The gap between these two tracks is itself a finding. If Gemini reports a successful fetch in prose but the raw
`url_retrieval_status` is `URL_RETRIEVAL_STATUS_ERROR`, that discrepancy belongs in the spec.

| | `url_context_test.py` | `url_context_test_raw.py` |
| - | ---------------------- | -------------------------- |
| **Measures** | Gemini's interpretation of what it fetched | Raw metadata extracted directly<br>from response object |
| **URL Counts** | Gemini estimates may vary between runs | Python `len()` on `url_context_metadata.url_metadata` |
| **Retrieval Status** | Gemini's prose description of success/failure | `url_retrieval_status`<br>API string, enum value |
| **Token Counts** | Gemini may reference or ignore token usage | `usage_metadata.tool_use_prompt_token_count`<br>reproducible |
| **`max_output_tokens`** | _Not set_, Gemini writes full assessments | Set to `128`, minimal output,<br>metadata is the signal |
| **Token Cost<br>per Run** | _Higher_, Gemini writes long self-assessments | _Lower_, minimal prompt,<br>capped output |
| **Best For** | Understanding what the agent perceives it received | Citable measurements<br>for the spec |

## Gemini URL Context vs Claude Web Fetch

[The Claude web fetch track](../anthropic-claude-api-web-fetch-tool/methodology.md) tests
`web_fetch` - a [mid-generation tool call](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#how-web-fetch-works):

1. Claude decides when to fetch based on prompts and/or URL availability
2. Claude API retrieves the content
3. The content comes back as a tool result
4. Claude continues generation, interpreting the tool result

Gemini's URL context tool completes retrieval _before_ generation begins:

1. Gemini API attempts to fetch each URL from an internal index cache
2. If not cached, the API falls back to a live fetch
3. URL context tool injects retrieved content into the `gemini-2.5-flash` context window
4. `gemini-2.5-flash` generates a response from the pre-loaded content

This architecture makes the raw track cleaner to implement than the Claude track, as
`url_context_metadata` is a first-class response field rather than something extracted from tool use
blocks, and token accounting splits between text prompt: `prompt_token_count` and
retrieved URL content: `tool_use_prompt_token_count`; the two cost components are already
separated in the response object.

## Character Count Estimation Variation Hypothesis

Unlike Claude Code, where Haiku summarizes before the main agent sees the content,
Claude's web fetch and Gemini's URL context handle summarization in-agent.
In this test suite, `gemini-2.5-flash` is doing _both the retrieval orchestration and the
generation_ - receives the retrieved content directly and summarizes in one step. Claude's web fetch
similarly filters fetched content via code execution rather than delegating to a separate agent
and exposes truncation behavior through observable cutoffs and `max_content_tokens`.
Gemini's URL context, by contrast, treats summarization as a use case rather than a pipeline stage -
with no equivalent parameter or cutoff boundary - making it harder to test whether summarization is
truncating characters or simply rephrasing them.

Without a field exposing content injected into the context window, run-to-run differences can't be
definitively attributed;
[Gemini's two-step retrieval process](https://ai.google.dev/gemini-api/docs/url-context#how-it-works)
means internal cache vs. live fetch could deliver different content across runs. But the raw token
counts being stable - <1% variance - suggest the retrieved content was consistent, pointing to
`gemini-2.5-flash` summarizing the same content differently across runs rather than receiving
different content.

---

## Known Platform Limits

The following details are appropriate data for the Agent-Friendly Documentation Spec:

### URL Limits

- Maximum 20 URLs per request, enforced at the API layer before retrieval. Exceeding the limit returns
  `400 INVALID_ARGUMENT` with zero tokens consumed. _This isn't truncation or silent dropping_.

### Retrieval Status

- `url_retrieval_status` is the authoritative signal. Don't rely on agent prose to determine success or failure -
  the interpreted and raw tracks diverged on characterization while the status enum was consistent.
- Two distinct failure modes exist: API-layer rejection - `400`, hard error, zero tokens, no metadata vs.
  retrieval-layer failure - request completes, `URL_RETRIEVAL_STATUS_ERROR` recorded in `url_context_metadata`,
  minimal tool tokens consumed.
- PDF retrieval fails consistently for the W3C WCAG 2.1 URL across both tracks and all runs despite PDF being
  a documented supported type. _Follow-up with a different PDF source required before drawing a general conclusion_.
- Google Docs return `URL_RETRIEVAL_STATUS_ERROR` at the retrieval layer consistently across both tracks.
- YouTube returns `URL_RETRIEVAL_STATUS_SUCCESS` consistently across both tracks despite documented as
  unsupported as of March 2026 on `gemini-2.5-flash`.
- JSON API endpoints are non-deterministic. The GitHub API endpoint succeeded in raw runs 1-2, failed in run 4-5.
  Don't treat JSON support as reliable without testing the specific endpoint.

### Token Accounting

- `tool_use_prompt_token_count` is the only reproducible proxy for retrieved content size. Gemini's
  interpreted character count estimates varied up to 60% across runs on the same URL; raw token counts
  varied <1%.
- Tool tokens dominate cost at scale: ~86% of total at 1 URL, ~98.6% at 5 URLs, ~98.9% at 20 URLs.
- `url_context_metadata` entry order doesn't reflect input order and varies between runs. Match
  by `retrieved_url` string, not array index.

### Rate Limits - Free Tier,`gemini-2.5-flash`

- 5 requests per minute, `GenerateRequestsPerMinutePerProjectPerModel-FreeTier`
- 20 requests per day, `GenerateRequestsPerDayPerProjectPerModel-FreeTier`
- The 8-test suite requires a minimum of 8 requests per run with no headroom for retries. A paid tier
  required to complete both tracks reliably in a single day.
