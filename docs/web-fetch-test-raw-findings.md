# Key Findings: Web fetch tool - raw

Summary from [web_fetch_test_raw.py](../claude-api/web_fetch_test_raw.py) results -

| Finding | Detail |
| --------- | -------- |
| CSS indicators: 0 across all tests | The API tool strips CSS effectively before content reaches the model. Unlike Claude Code, which was choked by inline CSS, no CSS indicators appeared in any test - including the short HTML page that broke Claude Code entirely. |
| Boilerplate is still significant | Short HTML: 81% boilerplate before the first heading. Long HTML: 97.5%. Nav menus, image links, and product listings consume the majority of the content budget before any documentation appears. |
| Markdown dramatically reduces boilerplate | Short HTML: 25,925 chars, first heading at char 21,009 - 81% boilerplate. Short Markdown: 6,024 chars, first heading at char 314 - 5.2% boilerplate. Serving markdown reduces total content by 77% and moves the first heading 98% earlier. |
| `max_content_tokens` truncation is approximate | Setting `max_content_tokens=5000` reduced content from 20,696 to 17,186 chars - not 5,000. Consistent with the API docs noting the parameter is approximate, but the margin is substantial. |
| `max_content_tokens` truncates mid-content | Test 4 ends with `/docs/current` - a mid-URL cutoff. Truncation isn't clean and can occur inside a token, not at a sentence or element boundary. |
| Default truncation limit is undocumented | Test 3 - no `max_content_tokens` set - still truncated at 20,696 chars, ending mid-word, last char: `'e'`. This suggests a default limit exists even when the parameter is omitted - but this limit isn't documented anywhere in the API docs. |
