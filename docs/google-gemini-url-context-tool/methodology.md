---
layout: default
title: "Methodology"
nav_order: 1
permalink: /docs/google-gemini-url-context-tool/methodology
parent: Google Gemini URL Context
---

# Methodology

---

## Track Design

Empirical testing of the [Google Gemini URL context tool](https://ai.google.dev/gemini-api/docs/url-context),
a pre-retrieval URL fetching capability for the Gemini API. The URL context tool lets you pass URLs directly
in a Gemini API request. The model fetches content from those URLs before generating a response. The
documented hard limits are:

- **20 URLs maximum** per request
- **34 MB maximum** content size per URL
- **Supported types**: HTML, JSON, plain text, XML, CSV, RTF, PNG, JPEG, BMP, WebP, PDF
- **Unsupported type**s**: YouTube videos, Google Workspace files, video/audio files, paywalled content

These tests empirically validate each limit and surface undocumented behaviors, especially around limit
boundary conditions, retrieval status enum values, and the gap between what Gemini reports and what the
API actually returns.

| **Script** | **Track** | **Purpose** |
| ------ | ----- | ------- |
| `url_context_test.py` | Gemini-interpreted | Gemini reflects on what it retrieved |
| `url_context_test_raw.py` | Raw | Python measures `url_context_metadata` directly |

## Measurement Constraints

Gemini's URL context tool pre-fetches content before generation: retrieved content is injected
into the model's context window rather than returned as a testable field in the API response.
_There's no direct equivalent_ to
[the Claude API web fetch track's](../anthropic-claude-api-web-fetch-tool/methodology.md)
character-level truncation measurement. The API doesn't expose the text injection or where
truncation occurred.

`tool_use_prompt_token_count` from `usage_metadata` is the closest available proxy: it measures how
many tokens the retrieved content consumed, which is useful for cost estimation but doesn't
identify a truncation boundary. The 34 MB documented limit is a fetch ceiling; how much of that
content survives into the context window isn't documented and not empirically measurable with the
current API surface.

The `content.parts` field exposes what the model generated in response to the retrieved content,
_not the retrieved content itself_. There is no API field that returns the fetched text directly.
