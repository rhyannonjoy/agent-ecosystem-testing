---
layout: default
title: Friction note
nav_order: 5
parent: Google Gemini URL Context
---

_Friction_: this note includes descriptions to any roadblocks
while testing.

### Google Gemini / Google AI Studio API key

Process for getting a Google AI Studio API key was more straightforward than the
for the Claude API. The Gemini API URL context docs includes a tools bar on the top
right of the page with a `Get API key` section. Rate limiting not documented and got
an error on first run, and also hit the daily quota limit after running the test suite
three times.

- Runs 1 & 2: `GenerateRequestsPerMinutePerProjectPerModel-FreeTier`, limit: 5
- Run 3: `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit: 20
