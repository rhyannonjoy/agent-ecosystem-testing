---
layout: default
title: "Methodology"
nav_order: 1
parent: Google Gemini URL Context
---

## Methodology

Empirical testing of the [Google Gemini URL context tool](https://ai.google.dev/gemini-api/docs/url-context),
a pre-retrieval URL fetching capability for the Gemini API. The URL context tool lets you pass URLs directly
in a Gemini API request. The model fetches content from those URLs before generating a response. The
documented hard limits are:

- **20 URLs maximum** per request
- **34 MB maximum** content size per URL
- Supported types: HTML, JSON, plain text, XML, CSV, RTF, PNG, JPEG, BMP, WebP, PDF
- Unsupported types: YouTube videos, Google Workspace files, video/audio files, paywalled content

These tests empirically validate each limit and surface undocumented behaviors, especially around limit
boundary conditions, retrieval status enum values, and the gap between what Gemini reports and what the
API actually returns.

| Script | Track | Purpose |
| ------ | ----- | ------- |
| `url_context_test.py` | Gemini-interpreted | Gemini reflects on what it retrieved |
| `url_context_test_raw.py` | Raw | Python measures `url_context_metadata` directly |
