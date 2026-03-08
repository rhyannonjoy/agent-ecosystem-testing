---
layout: default
title: "Gemini-interpreted vs Raw"
nav_order: 2
parent: Google Gemini URL Context
---

## Gemini-interpreted vs Raw

Two Python scripts test the same URL context behaviors:

**Gemini-interpreted** captures what Gemini _believes_ it retrieved: how much content it saw, whether a fetch
felt complete, how it characterizes a failure. This is the model's self-report, while the **raw track** captures
what the API _actually returned_: exact `url_retrieval_status` codes, exact token counts from `usage_metadata`,
exact URL counts in `url_context_metadata`. These are Python `len()` calls and dictionary lookups and not model
estimates.

The gap between these two tracks is itself a finding. If Gemini reports a successful fetch in prose but the raw
`url_retrieval_status` is `URL_RETRIEVAL_STATUS_ERROR`, that discrepancy belongs in the spec.

| | `url_context_test.py` | `url_context_test_raw.py` |
| - | ---------------------- | -------------------------- |
| Measures | Gemini's interpretation of what it fetched | Raw metadata extracted directly from response object |
| URL counts | Gemini estimates may vary between runs | Python `len()` on `url_context_metadata.url_metadata`- exact |
| Retrieval status | Gemini's prose description of success/failure | `url_retrieval_status` string from API - exact enum value |
| Token counts | Gemini may reference or ignore token usage | `usage_metadata.tool_use_prompt_token_count` - exact, reproducible |
| `max_output_tokens` | Not set - Gemini writes full assessments | Set to `128` - minimal output, metadata is the signal |
| Token cost per run | Higher - Gemini writes long self-assessments | Lower - minimal prompt, capped output |
| Best used for | Understanding what the model perceives it received | Citable measurements for the spec |

## Gemini URL Context vs Claude Web Fetch

[The Claude API web fetch track](../anthropic-claude-api-web-fetch-tool/methodology.md) tests a tool where
Claude _is_ the model doing the fetching and the interpretation. Here, the architecture is slightly different:

- **URL context tool** is a pre-retrieval step; Gemini fetches content before generating a response, rather than
as a tool call mid-generation
- **`url_context_metadata`** object is a first-class response field, not something extracted from tool use blocks;
this makes the raw track cleaner to implement
- **Token accounting is split** - `prompt_token_count` covers the text prompt, while `tool_use_prompt_token_count`
covers retrieved URL content; the raw script records both separately

### Character Count Estimation Variation Hypothesis

Unlike Claude Code, where Haiku summarizes before the main model sees the content, Gemini doesn't use
a named intermediate model; `gemini-2.5-flash` is doing _both the retrieval orchestration and the generation_ -
receives the retrieved content directly and summarizes in one step. The URL context docs list summarization
as a use case rather than a pipeline step.

Without a field exposing content injected into the context window, run-to-run differences can't be
definitively attributed;
[Gemini's two-step retrieval process](https://ai.google.dev/gemini-api/docs/url-context#how-it-works)
means internal cache vs. live fetch could deliver different content across runs. But the raw token
counts being stable - <1% variance - suggest the retrieved content was consistent, pointing to
`gemini-2.5-flash` summarizing the same content differently across runs rather than receiving
different content.

---

## Agent Docs Spec - Known Platform Limits

Both tracks agree on the following and are the citable findings for the spec:

### URL Limits

- Maximum 20 URLs per request, enforced at the API layer before retrieval. Exceeding the limit returns
  `400 INVALID_ARGUMENT` with zero tokens consumed. _This isn't truncation or silent dropping_.

### Retrieval Status

- `url_retrieval_status` is the authoritative signal. Don't rely on model prose to determine success or failure -
  the interpreted and raw tracks diverged on characterization while the status enum was consistent.
- Two distinct failure modes exist: API-layer rejection (`400`, hard error, zero tokens, no metadata) vs.
  retrieval-layer failure (request completes, `URL_RETRIEVAL_STATUS_ERROR` recorded in `url_context_metadata`,
  minimal tool tokens consumed).
- PDF retrieval fails consistently for the W3C WCAG 2.1 URL across both tracks and all runs despite PDF being
  a documented supported type. _Follow-up with a different PDF source required before drawing a general conclusion_.
- Google Docs return `URL_RETRIEVAL_STATUS_ERROR` at the retrieval layer consistently across both tracks.
- YouTube returns `URL_RETRIEVAL_STATUS_SUCCESS` consistently across both tracks despite documented as
  unsupported as of March 2026 on `gemini-2.5-flash`.
- JSON API endpoints are non-deterministic. The GitHub API endpoint succeeded in raw r1 and r2, failed in r4
  and r5. Don't treat JSON support as reliable without testing the specific endpoint.

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
