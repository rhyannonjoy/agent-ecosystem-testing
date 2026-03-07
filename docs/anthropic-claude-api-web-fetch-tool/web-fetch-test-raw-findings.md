---
layout: default
title: Key Findings Claude's web fetch tool - Raw
permalink: /web-fetch-test-findings-raw/
---

## Key Findings for Claude's Web Fetch Tool, Raw

---

**[Raw Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/claude-api/web_fetch_test_raw.py)**:

    1. Call Claude's API with the web fetch tool enabled
    2. Give Claude a minimal prompt — just enough to trigger the fetch
    3. Claude fetches the page, but isn't asked to interpret or describe it
    4. Extract the raw content directly from the `web_fetch_tool_result` block
       in the response object
    5. Run analysis in Python: character counts, CSS indicator detection,
       boilerplate estimation, truncation detection
    6. Claude never sees or interprets the content
    7. Results are saved to `claude-api/results/`

---

**Results Summary**:

| Finding | Detail |
| --------- | -------- |
| CSS indicators: 0 across all tests | The API tool strips CSS effectively before content reaches the model. Unlike Claude Code, which was choked by inline CSS, no CSS indicators appeared in any test - including the short HTML page that broke Claude Code entirely. |
| Boilerplate is still significant | Short HTML: 81% boilerplate before the first heading. Long HTML: 97.5%. Nav menus, image links, and product listings consume the majority of the content budget before any documentation appears. |
| Markdown dramatically reduces boilerplate | Short HTML: 25,925 chars, first heading at char 21,009 - 81% boilerplate. Short Markdown: 6,024 chars, first heading at char 314 - 5.2% boilerplate. Serving markdown reduces total content by 77% and moves the first heading 98% earlier. |
| `max_content_tokens` truncation is approximate | Setting `max_content_tokens=5000` reduced content from 20,696 to 17,186 chars - not 5,000. Consistent with the API docs noting the parameter is approximate, but the margin is substantial. |
| `max_content_tokens` truncates mid-content | Test 4 ends with `/docs/current` - a mid-URL cutoff. Truncation isn't clean and can occur inside a token, not at a sentence or element boundary. |
| Default truncation limit is undocumented | Test 3 - no `max_content_tokens` set - still truncated at 20,696 chars, ending mid-word, last char: `'e'`. This suggests a default limit exists even when the parameter is omitted - but this limit isn't documented anywhere in the API docs. |
