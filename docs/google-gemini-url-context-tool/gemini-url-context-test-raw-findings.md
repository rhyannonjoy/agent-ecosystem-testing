---
layout: default
title: Key Findings Gemini's URL context tool - Raw
permalink: /gemini-url-context-test-raw-findings/
nav_order: 4
parent: Google Gemini URL Context
---

**[Raw Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/gemini-url-context/url_context_test_raw.py)**:

1. Call the Gemini API with the URL context tool enabled
2. Give Gemini a minimal prompt - just enough to trigger URL retrieval
3. Gemini fetches each URL via its pre-retrieval step, but isn't asked
   to interpret, describe, or reflect on what it received
4. Extract raw retrieval outcomes directly from `url_context_metadata`
   in the response object -`retrieved_url` and `url_retrieval_status`
   per URL
5. Extract token accounting from `usage_metadata` —
   `tool_use_prompt_token_count` (URL content tokens) and
   `prompt_token_count` (text prompt tokens) are recorded separately
6. Run all analysis in Python: URL counts, status enum enumeration,
   success/failure rates, token breakdowns
7. Gemini never interprets or reflects on the retrieval results
8. Results are saved to `google-gemini-url-context/results/raw/`

---
