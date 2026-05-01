---
layout: default
title: "Key Findings Claude's Web Fetch Tool - Raw"
permalink: /docs/anthropic-claude-api-web-fetch-tool/web-fetch-test-raw-findings
---

# Key Findings for Claude's Web Fetch Tool, Raw

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/claude-api/web_fetch_test_raw.py)

    1. Call Claude's API with the web fetch tool enabled
    2. Give Claude a minimal prompt, just enough to trigger the fetch
    3. Claude fetches page, but not asked to interpret or describe it
    4. Extract the raw content directly from the `web_fetch_tool_result`
       block in the response object
    5. Run analysis in Python: character counts, CSS indicator detection,
       boilerplate estimation, truncation detection
    6. Results saved to `claude-api/results/`

---

## Results Summary

| **Finding** | **Detail** |
| --------- | -------- |
| **CSS indicators:<br>0 across all tests** | API tool strips CSS effectively before content reaches the LLM. Unlike Claude Code, choked by inline CSS, no CSS indicators appeared in any test, including the short HTML page that broke Claude Code entirely. |
| **Boilerplate still significant** | Short HTML: 81% boilerplate before the first heading. Long HTML: 97.5%. Nav menus, image links, product listings consume the majority of the content budget before any docs appear. |
| **Markdown dramatically reduces boilerplate** | Short HTML: 25,925 chars, first heading at char 21,009 - 81% boilerplate. Short Markdown: 6,024 chars, first heading at char 314 - 5.2% boilerplate. Serving Markdown reduces total content by 77% and moves the first heading 98% earlier. |
| **`max_content_tokens` truncation approximate** | Setting `max_content_tokens=5000` reduced content from 20,696 to 17,186 chars, not 5,000. Consistent with the API docs noting the parameter is approximate, but the margin is substantial. |
| **`max_content_tokens` truncates mid-content** | Fourth test ends with `/docs/current`, a mid-URL cutoff. Truncation isn't clean and can occur inside a token, not at a sentence or element boundary. |
| **Truncation limit undocumented** | Third test with no `max_content_tokens` set still truncated at 20,696 chars, ending mid-word, last char: `'e'`. This suggests a default limit exists even with the parameter omitted, but it isn't mentioned in the API docs. |
