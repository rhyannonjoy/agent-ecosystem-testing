---
layout: default
title: "Friction Note"
permalink: /docs/anthropic-claude-api-web-fetch-tool/friction-note
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide

- [Anthropic API Key](#anthropic-api-key)
- [API not available on the free-tier](#api-not-available-on-the-free-tier)
- [First Iteration: Interpreted Track Limitations](#first-iteration-interpreted-track-limitations)
- [Second Iteration: Raw Extraction Approach](#second-iteration-raw-extraction-approach)

---

## Anthropic API Key

The Claude docs AI assistant didn't return any results
when asked how to obtain an API key to test the
[web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#how-to-use-web-fetch).

```markdown
I don't have information about how to obtain an API key in the available sources. The documentation shows examples using the web fetch tool with an API key, but doesn't explain the process for acquiring one.

Check out these potentially useful sources that might help: Web fetch tool

Would you like me to try to provide a general answer based on my knowledge instead?
```

**Instructions**:

1. Go to [console.anthropic.com](https://platform.claude.com/dashboard) and sign up and/or log in
2. Once you're in, look for "API Keys" in the left sidebar
3. Click `Create Key`, give it a name like `web-fetch-testing`, and copy it immediately -
you won't be able to see it again after you close that dialog
4. Add key and value to the `.env` file
5. Run `source .env`
6. Run `python claude-api/web_fetch_test.py`

>_The name you give the key in the Claude console and your `.env` don't need to
match. The name you gave it in the console - `"agent-ecosystem-testing-claude-web-fetch"` -
is just a human-readable label to help you remember what it's for - it has no effect on how
the key works. `ANTHROPIC_API_KEY` is just the variable name the script uses to look it up
on your machine. These labels are two completely separate things: one is Anthropic's label
in their dashboard, the other is your local environment variable name. The script selects
the correct secret._

---

## API not available on the free-tier

This API requires a paid credit balance as there isn't a free tier for API access - which is
separate from the free tier on claude.ai. This API is pay-as-you-go, not a subscription. Add a
small amount of credits at [console.anthropic.com](https://platform.claude.com/dashboard);
otherwise run attempts will surface the following error:

```bash
anthropic.BadRequestError: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits.'}, 'request_id': 'req_01...'}
```
---

## First Iteration: Interpreted Track Limitations

The first iteration of the Claude API test script asked Claude to describe what it
received from each URL fetch in the form of character counts, truncation observations,
and content completeness. This produced usable data, but with a structural reliability
problem that only became apparent after reviewing the results.

Character counts varied slightly between runs on identical URLs, as Claude is interpreting
what it received, not calculating precisely from a raw source. The only objective,
non-interpreted data in the first-iteration results is the token counts in the `usage`
block, which come directly from API response metadata and don't pass through Claude's
interpretation at all.

The script attempted to capture raw content length directly from the
`web_fetch_tool_result` block via `fetch_content_length_chars`, bypassing Claude's
interpretation entirely. This didn't work: `fetch_content_length_chars` returned 0
across all runs. The raw extraction path existed in the script but wasn't producing
usable data.

**Impact**: first-iteration results are useful for order-of-magnitude orientation —
confirming truncation occurred, estimating retrieval rate against expected page size —
but not for precise cross-run comparison. The character count variance is an
artifact of the measurement method, not a property of the fetch tool.

---

## Second Iteration: Raw Extraction Approach

The second iteration strips Claude's interpretive role to the minimum required to
trigger a fetch. The prompt is just `"Fetch this URL: {url}"` with `max_tokens=128` —
Claude only needs to invoke the tool, not describe anything. This also substantially
reduces cost per run.

All analysis moves to Python. The `analyze_content()` function measures directly
from the raw string: exact character counts, CSS indicator detection in the first
2,000 characters, where the first heading appears, and whether content ends cleanly
or mid-word. No estimation, no interpretation.

Output files use `_raw_results.json` and `_raw_summary.md` suffixes to avoid
colliding with first-iteration files from `web_fetch_test.py`.

> _Raw content extraction depends on the `web_fetch_tool_result` block having a
> specific structure. If the API response format differs from what the script expects,
> `raw_content_chars` returns `None` — which is itself a finding worth documenting,
> as it indicates the extraction path assumption failed for that response._

**Methodology Decision**: treat second-iteration raw track measurements as the
authoritative source for citable figures. First-iteration interpreted results remain
in the dataset and are useful for documenting Claude's self-perception of truncation,
consistent with the interpreted track purpose across all platforms in this collection.
