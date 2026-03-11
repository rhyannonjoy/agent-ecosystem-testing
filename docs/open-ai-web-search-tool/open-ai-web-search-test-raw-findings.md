---
layout: default
title: "Key Findings OpenAI Web Search, Raw"
nav_order: 4
parent: OpenAI Web Search
---

## Key Findings OpenAI Web Search, Raw

**Raw Test Workflow**:

    1. Call the Responses API with `gpt-4o` + `web_search_preview` tool enabled
    2. Give the model a minimal prompt; just enough to trigger retrieval
    3. The model may or may not `invoke web_search_preview` depending on the query
    4. Extract raw outcomes directly from response.output items:
       - `web_search_call` items: type, `action.query` - the internal search query issued
       - message items: `output_text`
    5. Extract sources list from `response.sources` - all URLs consulted, not just cited
    6. Extract token accounting from `response.usage`
    7. Run all analysis in Python: tool invocation flag, source counts, latency
    8. The model never interprets or reflects on the retrieval results
    9. Results are saved to `open-ai-web-search/results/raw/`

---

## Results Summary
