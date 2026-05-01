---
layout: default
title: "Claude-interpreted vs Raw"
permalink: /docs/anthropic-claude-api-web-fetch-tool/claude-interpreted-vs-raw
---

## Claude-interpreted vs Raw

The conclusions are similar: both confirm agentic aversion to CSS, boilerplate is heavy, Markdown is
cleaner, and `max_content_tokens` cuts mid-content, but the two scripts produce meaningfully different
data in three ways:

1. **Measurement accuracy is completely different**. The Claude-interpreted script estimated
   13,700–14,200 chars for the short HTML page. The raw script measured 25,925 chars, nearly double.
   Claude was significantly underestimating. For the spec, only the raw numbers are citable.

2. **The raw script found something the interpreted script missed**. The default truncation limit
   finding, that the third test truncated at 20,696 chars even with no `max_content_tokens` set, only
   appears in the raw results. Claude didn't flag this in its interpretation because it attributed the
   missing content to JavaScript rendering rather than a character limit. Both were actually happening
   simultaneously, but Claude only noticed one cause.

3. **The raw script quantifies boilerplate precisely**. _"81% boilerplate before the first heading"_ and
   _"97.5%"_ are exact, reproducible measurements. Claude's equivalent estimates _"~60-65%"_, varied
   between runs of the same test. The raw numbers are what belong in the Agent-Friendly Documentation Spec,
   Known Platform Limits table.

The interpreted script is still useful as a record of what the agent _perceives it received_, which
is arguably what matters most for agent developers and docs teams. A model that receives 25,925 chars but
estimates 13,700 is working with a distorted picture of the content, and that gap itself is a finding worth
noting.
