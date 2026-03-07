---
layout: default
title: "Gemini-interpreted vs Raw"
nav_order: 2
parent: Google Gemini URL Context
---

## Gemini-interpreted vs Raw

Two Python scripts test the same URL context behaviors:

**Gemini-interpreted** captures what Gemini _believes_ it retrieved: how much content it saw, whether a fetch felt complete, how it characterizes a failure. This is the model's self-report, while the **raw track** captures what the API _actually returned_: exact `url_retrieval_status` codes, exact token counts from `usage_metadata`, exact URL counts in `url_context_metadata`. These are Python `len()` calls and dictionary lookups and not model estimates.

The gap between these two tracks is itself a finding. If Gemini reports a successful fetch in prose but the raw `url_retrieval_status` is `URL_RETRIEVAL_STATUS_ERROR`, that discrepancy belongs in the spec.

| | `url_context_test.py` | `url_context_test_raw.py` |
| - | ---------------------- | -------------------------- |
| Measures | Gemini's interpretation of what it fetched | Raw metadata extracted directly from response object |
| URL counts | Gemini estimates may vary between runs | Python `len()` on `url_context_metadata.url_metadata`- exact |
| Retrieval status | Gemini's prose description of success/failure | `url_retrieval_status` string from API - exact enum value |
| Token counts | Gemini may reference or ignore token usage | `usage_metadata.tool_use_prompt_token_count` - exact, reproducible |
| `max_output_tokens` | Not set - Gemini writes full assessments | Set to `128` - minimal output, metadata is the signal |
| Token cost per run | Higher - Gemini writes long self-assessments | Lower - minimal prompt, capped output |
| Best used for | Understanding what the model perceives it received | Citable measurements for the spec |

## Key differences from the Claude web fetch track

[The Claude API web fetch track](../../claude-api/) tests a tool where Claude _is_ the model doing the fetching and the interpretation. Here, the architecture is slightly different:

- The **URL context tool** is a pre-retrieval step; Gemini fetches content before generating a response, rather than as a tool call mid-generation.
- The **`url_context_metadata`** object is a first-class response field, not something extracted from tool use blocks. This makes the raw track cleaner to implement.
- **Token accounting is split**: `prompt_token_count` covers the text prompt, while `tool_use_prompt_token_count` covers retrieved URL content. The raw script records both separately.

---

## Results structure

```shell
google-gemini-url-context/
  results/
    gemini-interpreted/
      test_1_single_html.json
      test_2_single_pdf.json
      ...
      _summary.json
    raw/
      test_1_single_html.json
      test_2_single_pdf.json
      ...
      _summary.json
```

Each result file contains the full request context, all metadata fields, and computed measurements. The `_summary.json` files aggregate all runs for cross-test comparison.
