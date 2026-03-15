---
layout: default
title: "Methodology"
permalink: /anysphere-cursor/methodology/
parent: Anysphere Cursor
---

## Methodology

Rather than target specific API endpoints with documented interfaces, 
Cursor IDE testing targets consumer application with proprietary chat
behavior and multiple fetch mechanisms. Cursor's `@web` and MCP
implementations don't have a public API. `@web` specifically operates
through a built-in chat feature, proprietary fetch pipeline, and is only
observable through chat output. MCP servers are user-configured,
implementations vary - mcp-server-fetch, fetch-browser-mcp, third-party -
and are observable through Cursor's agent behavior, but not
instrumentable. Measurement mirrors Dachary's experiments with
Claude Code - not with Python and inspecting response objects,
but chat-based measurement through interaction.

****This testing uses Cursor IDE directly**, in two tracks:**

**Goal**: use Cursor IDE directly with two complementary tracks;
interpreted track catches perception gaps, while the raw track
produces reproducible numbers for documentation -

| | **Cursor-interpreted Track** | **Raw Track** |
| - | -------------------- | ------------- |
| Question | *What does Cursor report back? Does it accurately perceive truncation? Are there systematic estimation errors?* | *What actually came through the @web command? Where exactly does truncation occur? Is the boundary consistent?* |
| Method | Chat prompt asks `@web` to fetch URL and report measurements | Chat prompt asks `@web` to fetch URL and return output verbatim, human manually extracts measurements |
| Captures | Cursor's, and the underlying model's, interpretation of truncation and completeness | Actual response content from `@web` command, post-processing, exact character boundaries |
| Measurements | Model estimates: "appears truncated," "approximately X KB," "markdown seems complete" | Manual: character count via `len()`, token count via tiktoken, exact truncation point, last 50 characters |
| Repeatability | Varies between runs due to model variance | Reproducible - same URL fetched multiple times yields consistent content |
| Best sed for | Understanding what developers experience; surfacing perception gaps | Citable baseline measurements for the Agent Docs Spec |

### Cursor-Specific Considerations

#### Multiple Fetch Mechanisms

Unlike Claude's single `web_fetch` tool, Cursor offers:
- **@web command** (native, proprietary)
- **mcp-server-fetch** (configurable, documented limits but Cursor's integration is not)
- **fetch-browser-mcp** (headless browser, different truncation behavior)
- **Third-party MCP servers** (e.g., Oxylabs, variable behavior)

Testing compares these side-by-side on identical URLs (Test 3.4) to determine if one mechanism has different limits. This is unique to Cursor and addresses a gap in the ecosystem testing.

#### Model Variability

Cursor supports multiple models (Claude 3.5 Sonnet, GPT-4o, local models). Testing runs with a **single, consistent model** (documented in results) to isolate fetch behavior from model inference variance. If Cursor's truncation differs between models, that's documented separately.

#### HTML-to-Markdown Conversion Timing

Critical unknown: **Does Cursor truncate before or after converting HTML to markdown?**
- Pre-conversion: You lose ~40-50% of characters to HTML/CSS overhead, reducing effective content limit
- Post-conversion: Markdown is smaller, but structure might be broken at truncation boundary

Tests SC-1 through SC-4 directly probe this by measuring truncation point relative to content structure.

#### Agent Behavior After Truncation

Another Cursor-specific question: **If @web truncates, does the Cursor agent automatically request the next chunk, or does the user have to manually ask?**

This is tested via OP-4 (Agent Retry Pattern) by observing whether Cursor makes unprompted follow-up fetches for large URLs. Not well-explored in Claude API testing (which documents offset parameters but doesn't test automatic chunking).

### Test Execution: Standardized Harness

Each test follows a consistent format across both tracks:

```
Test: [ID] - [Description]
Date: YYYY-MM-DD
Cursor Version: [from "About Cursor" or CLI]
Model: [e.g., Claude 3.5 Sonnet]
Method: [@web / mcp-server-fetch / fetch-browser-mcp]

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

### Data Collection: CSV Format

Results populate a time-series CSV for trend analysis:

```
test_id,date,url,method,model,input_est_chars,output_chars,truncated,truncation_char_num,tokens_est,hypothesis_match,notes
BL-1,2025-03-14,en.wikipedia.org/wiki/Python,@web,claude-sonnet-4,50000,48500,no,NULL,12000,H1-no,Full content returned
BL-2,2025-03-14,en.wikipedia.org/wiki/History,@web,claude-sonnet-4,120000,9876,yes,9876,2469,H1-yes,"Character boundary confirmed"
OP-3-web,2025-03-15,httpbin.org/html,@web,claude-sonnet-4,5000,5000,no,NULL,1250,comparison,"@web returned full"
OP-3-mcp,2025-03-15,httpbin.org/html,mcp-server-fetch,claude-sonnet-4,5000,5000,no,NULL,1250,comparison,"MCP returned full - same limit"
```

Multiple runs per test (2-3 times) capture model variance. Identical results across runs validate that truncation point is **deterministic to fetch, not to model inference**.

### Comparison to Claude API Testing

| Aspect | Claude API Testing | Cursor Testing |
|--------|-------------------|-----------------|
| **Interface** | Python API call, response object available | Chat interface, observable only through output |
| **Layers** | Single: URL → fetch → return | Two: URL → fetch → @web output, then model interprets |
| **Instrumental access** | Full: can inspect `ToolResult.content` directly | Partial: can only read model's output or manually copy @web result |
| **Repeatability** | High: same URL yields identical API response | Medium: model interpretation varies, but @web raw content should be stable |
| **Fetch mechanisms** | One (web_fetch tool) | Multiple (@web, mcp-server-fetch, fetch-browser-mcp, third-party) |
| **Best findings** | Hard limits (Claude API truncates at ~100KB) | Comparative limits (does MCP override @web? Does agent auto-chunk?) |

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

The methodology mirrors existing tests (interpreted + raw tracks) while accounting for Cursor's unique architecture (chat-based, multiple mechanisms, no direct API access).
