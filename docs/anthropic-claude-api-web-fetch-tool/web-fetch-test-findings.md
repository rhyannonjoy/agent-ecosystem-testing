---
layout: default
title: "Key Findings Claude's Web Fetch Tool - Claude-interpreted"
permalink: /docs/anthropic-claude-api-web-fetch-tool/web-fetch-test-findings
---

# Key Findings for Claude's Web Fetch Tool, Claude-interpreted

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/claude-api/web_fetch_test.py)

1. Call Claude's API with the web fetch tool enabled
2. Give Claude a URL, ask it to fetch the page, describe what it got
3. Claude fetches the page, then reports back what it received
4. Results saved to `claude-api/results/`

---

## Results Summary

| **Finding** | **Detail** |
| --------- | -------- |
| **CSS indicators:<br>not detected in any test** | Claude reported no CSS or boilerplate in any fetch result, describing all HTML pages as _"a mix of boilerplate and actual documentation."_ This contrasts with Claude Code, where CSS consumed the entire content budget. The API tool appears to strip CSS before content reaches the model. |
| **Boilerplate present, but content survives** | For the short HTML page, Claude estimated the first ~60-65% of characters as navigation boilerplate, with the actual documentation fully intact in the remaining ~35-40%. Unlike Claude Code, the content wasn't lost, just buried. |
| **Markdown dramatically cleaner** | Claude estimated ~4,900-5,600 characters for the Markdown page vs ~13,700-14,200 for the HTML page, a reduction of roughly 60-65%. Claude described the markdown version as _"actual, substantive documentation content - not CSS or boilerplate"_ without any navigation chrome. |
| **JS-rendered pages return only a shell** | The long tutorial page returned only the page title, a preview notice, and a dropdown placeholder. Claude correctly identified that the tabbed driver content: mongosh, Python, Node.js, Java, C#, Go - was absent because it requires JavaScript execution to render, which web fetch doesn't support. |
| **`max_content_tokens` cuts before reaching content** | With `max_content_tokens=5000`, Claude confirmed the content ended mid-URL at `+ [Overview](/docs/current` - never reaching the tutorial body. The navigation chrome consumed the entire token budget. |
| **Claude's character counts estimates, not measurements** | Claude estimated 13,700 chars in one run and 14,200 in another for the same page. The raw script measured 25,925 chars for the same fetch. Claude is interpreting and estimating, not precisely measuring. Token counts from the `usage` block are the only objective data from this script. |
