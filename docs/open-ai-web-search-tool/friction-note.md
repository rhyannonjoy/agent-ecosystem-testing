---
layout: default
title: "Friction Note"
nav_order: 5
parent: OpenAI Web Search
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## OpenAI API key

Obtaining an OpenAI API key wasn't as straightforward as the
[Google AI Studio/Gemini API key process](../google-gemini-url-context-tool/friction-note.md),
but required digging around. I started on the
[the Web Search page](https://developers.openai.com/api/docs/guides/tools-web-search). There is
no obvious "get an API key here" or explicit instructions, but there is an "API Dashboard ↗"
button that hangs out by itself in the top right tools bar. I wandered around in the Get Started
sections Overview and Quickstart before clicking on "API Dashboard ↗" - which requires an
account with your full name and birthdate and tries to sell credits immediately - 
my assumption was that I wouldn't be able to use the endpoint for free and I was right.
My initial attempts to run the ChatGPT-interpreted path completely errored-out:

```shell
"Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}}"
```

## No credits = no API access at all

`insufficient_quota` is an **account-level** billing block, not a rate limit.
Switching to a cheaper model, like the `gpt-4o-mini-search-preview`, doesn't help -
the `429` error applies to every model on the account without credits.

**Fix**: Go to [platform.openai.com/settings/billing](https://platform.openai.com/settings/billing)
and add credits. A minimum top-up, $5–10, is enough to run both tracks in full.
The mini model _is_ cheaper per call (~10× vs `gpt-4o-search-preview`), so it's
worth using once credits are active to keep test costs low, but it can't
substitute for credits entirely.

**Contrast with Gemini**: free tier allows immediate API access with
only rate limiting - 13 second sleep between calls. OpenAI requires a paid account
before any API call succeeds, regardless of model.
