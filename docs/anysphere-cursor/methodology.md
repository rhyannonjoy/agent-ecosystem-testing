---
layout: default
title: "Methodology"
permalink: /docs/anysphere-cursor/methodology
parent: Anysphere Cursor
---

## Methodology

---

_**Chat-based measurement through interaction, without direct code instrumentation**_

>_software instrumentation is the process of adding code to a system
to collect data about how it works; while the Cursor chat is public and accessible,
testing it is different than calling an API to extract measurements programmatically_

---

_**Testing a closed consumer application vs an open API**_

Rather than target specific API endpoints with documented interfaces, 
Cursor testing targets consumer application with proprietary chat
behavior and multiple fetch mechanisms. Cursor's `@web` and MCP
implementations don't have a public API; `@web` specifically operates
through a built-in chat feature, proprietary fetch pipeline, and is only
observable through chat output while MCP servers are user-configured,
implementations vary - mcp-server-fetch, fetch-browser-mcp, third-party -
and are observable through Cursor's agent behavior, but not
instrumentable. Compare to this collection's
[Claude API Web Fetch testing](/docs/anthropic-claude-api-web-fetch-tool/methodology.md) -

| **Aspect** | **Claude API Testing** | **Cursor Testing** |
|--------|-------------------|-----------------|
| **Interface** | Python API call, response object available | Chat interface, observable only through output |
| **Layers** | Single: URL → fetch → return | Two: URL → fetch → @web output, then model interprets |
| **Instrumental Access** | Full: can inspect `ToolResult.content` directly | Partial: can only read model's output or manually copy @web result |
| **Repeatability** | High: same URL yields identical API response | Medium: model interpretation varies, but @web raw content should be stable |
| **Fetch Mechanisms** | One (web_fetch tool) | Multiple (@web, mcp-server-fetch, fetch-browser-mcp, third-party) |
| **Best Findings** | Hard limits (Claude API truncates at ~100KB) | Comparative limits (does MCP override @web? Does agent auto-chunk?) |

**Goal**: use Cursor IDE directly with two complementary tracks -
Cursor-interpreted track catches perception gaps, while the raw track
produces reproducible numbers for documentation -

| | **Cursor-interpreted Track** | **Raw Track** |
| - | -------------------- | ------------- |
| **Question** | *What does Cursor report back? Does it accurately perceive truncation? Are there systematic estimation errors?* | *What actually came through the `@web` command? Where exactly does truncation occur? Is the boundary consistent?* |
| **Method** | Chat prompt asks `@web` to fetch URL and report measurements | Chat prompt asks `@web` to fetch URL and return output verbatim, human manually extracts measurements |
| **Captures** | Cursor's, and the underlying model's, interpretation of truncation and completeness | Actual response content from `@web` command, post-processing, exact character boundaries |
| **Measurements** | Model estimates: "appears truncated," "approximately X KB," "markdown seems complete" | Manual: character count via `len()`, token count via tiktoken, exact truncation point, last 50 characters |
| **Repeatability** | Varies between runs due to model variance | Reproducible - same URL fetched multiple times yields consistent content |
| **Best For** | Understanding what developers experience; surfacing perception gaps | Citable baseline measurements for the Agent Docs Spec |

### Cursor-Specific Unknowns
 
| **Question** | **Details** | **Approach** | **Value** |
|----------|---------|------------------|----------------|
| **Multiple Fetch Mechanisms** | `@web` - native, proprietary; mcp-server-fetch - configurable; fetch-browser-mcp - headless browser; third-party MCP servers, such as Oxylabs | Compare side-by-side on identical URLs, Test 3.4 | Determines if one mechanism has different limits; unique to Cursor, addresses ecosystem testing gap |
| **HTML-to-Markdown Conversion Timing** | **_Does Cursor truncate before or after HTML→markdown conversion?_** | Tests SC-1 through SC-4: measure truncation relative to content structure | **Pre-conversion**: lose 40-50% of characters to HTML/CSS overhead; **Post-conversion**: Markdown smaller but structure may break at boundary |
| **Agent Auto-chunking** | **_After truncation, does `@web` automatically request next chunk or require manual request?_** | Test OP-4, Agent Retry Pattern: observe unprompted follow-up fetches for large URLs | Not well-explored in Claude API testing; key gap in ecosystem methodology, shapes DX with large docs |
| **Model Variability** | Cursor supports Claude `3.5 Sonnet`, `GPT-4o`, local models | Run tests with single consistent model, documented per run | Isolates fetch behavior from model inference variance; divergences documented separately |

### Test Execution: Standardized Harness

```markdown
<!--Each test follows a consistent format across both tracks -->
Test: [ID] - [Description]
Date: YYYY-MM-DD
Cursor Version: [from "About Cursor" or CLI]
Model: [Claude 3.5 Sonnet]
Method: [`@web` / mcp-server-fetch / fetch-browser-mcp]

Input:
  URL: [exact URL tested]
  Expected Size: [estimated from curl or prior measurement]
  Prompt: [exact prompt sent to Cursor]

Output (Interpreted Track):
  Model Report: [Cursor's description of what it received]
  Estimated Length: [model's estimate in KB or characters]
  Truncation Perceived: [yes/no, where]
  Formatting Assessment: [markdown integrity, code block completeness]

Output (Raw Track):
  Actual Length: [len() of fetched content in characters]
  Actual Length (KB): [for consistency with other platforms]
  Tokens (estimated): [tiktoken count]
  Truncation Detected: [yes/no, exact character position]
  Last 50 Characters: [verbatim, to verify boundary]
  Clean Truncation: [yes/no - mid-word? mid-tag?]

Analysis:
  Truncation Rule Match: [H1/H2/H3/H4/H5 hypothesis]
  Comparison to Baseline: [vs BL-1, vs Claude API, vs Gemini]
  Anomalies: [timeouts, errors, unexpected behavior]
```

---

### Data Collection: CSV Format

```shell
<!-- `/results` populate a time-series CSV for trend analysis -->
<!-- Multiple runs capture model variance; identical results validate deterministic to fetch, not model -->

test_id,date,url,method,model,input_est_chars,output_chars,truncated,truncation_char_num,tokens_est,hypothesis_match,notes
BL-1,2025-03-14,en.wikipedia.org/wiki/Python,@web,claude-sonnet-4,50000,48500,no,NULL,12000,H1-no,Full content returned
BL-2,2025-03-14,en.wikipedia.org/wiki/History,@web,claude-sonnet-4,120000,9876,yes,9876,2469,H1-yes,"Character boundary confirmed"
OP-3-web,2025-03-15,httpbin.org/html,@web,claude-sonnet-4,5000,5000,no,NULL,1250,comparison,"@web returned full"
OP-3-mcp,2025-03-15,httpbin.org/html,mcp-server-fetch,claude-sonnet-4,5000,5000,no,NULL,1250,comparison,"MCP returned full - same limit"
```

---

### Comparison to Claude API Testing

| Aspect | Claude API Testing | Cursor Testing |
|--------|-------------------|-----------------|
| **Interface** | Python API call, response object available | Chat interface, observable only through output |
| **Layers** | Single: URL → fetch → return | Two: URL → fetch → @web output, then model interprets |
| **Instrumental Access** | Full: can inspect `ToolResult.content` directly | Partial: can only read model's output or manually copy @web result |
| **Repeatability** | High: same URL yields identical API response | Medium: model interpretation varies, but @web raw content should be stable |
| **Fetch Mechanisms** | One (web_fetch tool) | Multiple (@web, mcp-server-fetch, fetch-browser-mcp, third-party) |
| **Best Findings** | Hard limits (Claude API truncates at ~100KB) | Comparative limits (does MCP override @web? Does agent auto-chunk?) |

### Known Limitations of This Approach

1. **Model interpretation variance**: Interpreted track results vary between runs. We control for this by running each test multiple times and looking for consensus, but some variation is expected.

2. **No direct response object access**: Unlike Claude API testing, we cannot programmatically inspect Cursor's internal `ToolResult` equivalent. Raw track relies on manually copying @web output and analyzing it in Python.

3. **Configuration dependency**: Cursor's behavior may vary with:
   - MCP server version (`mcp-server-fetch` package.json version documented per run)
   - Cursor IDE version (captured at test time)
   - Model selection (held constant per test series)
   
   If behavior changes between Cursor versions, we document it as a finding, not a contradiction.

4. **Authentication wall**: Some test URLs (GitHub API, Stripe docs) may be gated. We note which tests hit auth walls and substitute public alternatives when available.

### Success Criteria

Testing is complete and spec-ready when:

- ✅ **Truncation threshold identified** to ±5% confidence (same threshold as Claude API testing)
- ✅ **Both tracks converge**: Interpreted and raw track agree on truncation point (or documented divergence is explained)
- ✅ **MCP variants compared**: Testing shows if mcp-server-fetch differs from @web, with specific measurements
- ✅ **Chunking behavior characterized**: Clear yes/no answer on whether agent auto-chunks after truncation
- ✅ **Edge cases explored**: Failure modes, content-type effects, redirect chains documented
- ✅ **Reproducible findings**: Raw track measurements can be verified by another tester running same URLs with same Cursor version

---

## Integration with Agent Ecosystem Testing

This Cursor testing extends the existing framework:

- **Claude API testing** established that web fetch limits are real and measurable (~100KB observed, varies by content type)
- **Gemini URL context testing** showed that limits vary by platform (20 URL max, PDFs supported, etc.)
- **OpenAI web search testing** revealed that fetch behavior differs between API surfaces (Chat Completions vs Responses API)
- **Cursor @web and MCP testing** (this project) will document whether Cursor's proprietary implementations have their own limits, and whether developers can work around them via MCP configuration

