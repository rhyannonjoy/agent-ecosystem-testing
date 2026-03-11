---
layout: default
title: "Key Findings OpenAI Web Search, ChatGPT-interpreted"
nav_order: 3
parent: OpenAI Web Search
---

## Key Findings OpenAI Web Search, ChatGPT-interpreted

---

**ChatGPT-interpreted Test Workflow**:

    1. Call the Chat Completions API with `gpt-4o-search-preview`
    2. Give the model a detailed prompt asking it to describe what it retrieved -
       result quality, recency, completeness, any failures
    3. The model always searches before generating a response; no tool plumbing
       exposed to the caller
    4. Capture the model's full text response as the interpreted finding
    5. Also capture inline `url_citation` annotations from `message.annotations`
       for cross-referencing against the raw track
    6. The gap between the model's self-report and raw citation counts is itself
       a finding — discrepancies belong in the spec
    7. Results are saved to `open-ai-web-search/results/chatgpt-interpreted/`

---

## Results Summary
