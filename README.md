# Agent Ecosystem Testing

**Overview**: Empirical tests of web fetch behavior across AI agent platforms, in support of the
[Agent-Friendly Documentation Spec](https://github.com/agent-ecosystem/agent-docs-spec)
and specifically contributes data to the
[Known Platform Limits](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits).
Full methodology and findings:
[testing results docs](https://rhyannonjoy.github.io/agent-ecosystem-testing/).

**Origin**: extension of Dachary Carey's
[Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/),
which documented Claude Code's web fetch pipeline in detail.

**Goal**: measure what actually happens between "agent fetches URL" and
"model sees content" - truncation limits, HTML processing, content
negotiation - for platforms that don't document these details.

---

## Platforms Tested

| Platform | Tool | Scripts, Results |
| -------- | ---- | ------- |
| Anthropic Claude API | [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) | `claude-api/` |
| Anysphere Cursor IDE | `@Web` context attachment | `cursor-web-fetch/` |
| Google Gemini API | [URL context](https://ai.google.dev/gemini-api/docs/url-context) | `gemini-url-context/` |
| OpenAI: Chat Completions API, Responses API | [web search](https://developers.openai.com/api/docs/guides/tools-web-search) | `open-ai-web-search/` |

Each platform has two tracks:

- **Interpreted** - ask the model to reflect on what it retrieved; captures self-perception and estimation variance
- **Raw** - Python extracts measurements directly from the response object; produces citable, reproducible numbers

> _Cursor testing uses a hybrid approach: raw track saves verbatim output to disk for programmatic analysis; interpreted track asks
> Cursor to self-report metrics from `@Web`-attached content; visit the
> [Cursor Friction Note](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/anysphere-cursor/friction-note)
> for methodology challenges unique to IDE-based testing_

---

## Setup

### Prerequisites

- Python 3.8+
- API keys for the applicable platforms
- Cursor IDE if applicable

### Install

```bash
# Clone the repo
git clone https://github.com/rhyannonjoy/agent-ecosystem-testing.git
cd agent-ecosystem-testing

# Create and activate a virtual environment
python3 -m venv venv
# On Windows: venv\Scripts\activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="key-here"
export GOOGLE_GEMINI_API_KEY="key-here"
export OPEN_AI_API_KEY="key-here"
```

### Run Tests

```bash
# Claude-interpreted
python claude-api/web_fetch_test.py
# Raw
python claude-api/web_fetch_test_raw.py

# ChatGPT-interpreted
python open-ai-web-search/web_search_test.py
# Raw
python open-ai-web-search/web_search_test_raw.py

# Cursor-interpreted
python cursor-web-fetch/web_fetch_testing_framework.py --test {test ID} --track interpreted
# Raw
python cursor-web-fetch/web_fetch_testing_framework.py --test {test ID} --track raw

# Gemini-interpreted
python gemini-url-context/url_context_test.py
# Raw
python gemini-url-context/url_context_test_raw.py
```

> _**Free Tier Limits**: Claude API not available on the free-tier, the API is pay-as-you-go;
5 RPM and 20 RPD limits for `gemini-2.5-flash` - running both tracks in the same day exhaust
the daily quota; plan runs across days or use a paid tier; Cursor tests available on Pro Plan;
OpenAI requires a minimum credit top-up (~$5) before any API call succeeds regardless of model -
`insufficient_quota` is an account-level block, not a rate limit; set `RATE_LIMIT_SLEEP_SECONDS = 0`
in the scripts if you're on a paid tier_

---

## Claude API Test Details

Both tracks test the same four URLs. The **Claude-interpreted track** asks the model to
describe what it received; the **raw track** extracts character counts, CSS indicators,
and truncation signals programmatically from the `web_fetch_tool_result` block.

| Test | Question | What it fetches |
| ---- | -------- | --------------- |
| 1: Short HTML, no token limit | _Does the API tool have the same CSS-eating-content problem Dachary found in Claude Code? What's the effective default token limit?_ | Short docs page with substantial inline CSS before content begins |
| 2: Same page, Markdown version | _Does the API tool request or prefer Markdown? How much smaller is the token footprint?_ | `.md` URL variant of Test 1 - compares `input_tokens` directly |
| 3: Long page, no token limit | _At what point does content get truncated? Does the API tool behave differently than Claude Code, which truncated to ~100KB?_ | Long tabbed tutorial page, no `max_content_tokens` set |
| 4: Long page, explicit token limit | _Does `max_content_tokens=5000` work as documented? Is truncation clean or mid-sentence?_ | Same page as Test 3, with `max_content_tokens=5000` |

---

## Cursor IDE Test Details

Unlike API testing, Cursor testing uses manual chat sessions with the Cursor IDE. The framework
generates prompts, but execution requires copy-paste into the Cursor IDE. Raw track saves outputs
to disk for measurement; interpreted track asks Cursor to self-report. Both tracks test 13 distinct
URLs. Tests focus on truncation behavior, backend routing variance, content conversion patterns,
and reproducibility.

| Test Category | Question | What it tests |
| --- | --- | --- |
| Baseline | *What's the reproducibility baseline? Do same URLs always return identical content?* | Small docs pages (4-20KB), tested multiple times to measure variance |
| Structure-Aware | *Does Cursor truncate intelligently at content boundaries, or cut mid-content?* | Wikipedia pages, Markdown guides, docs with complex structure |
| Output Pattern | *What triggers Markdown conversion vs raw HTML?* | Large tutorials, JavaScript-heavy SPAs, timeout scenarios |
| Edge Cases | *How does Cursor handle redirects, JSON endpoints, raw Markdown files, and version drift?* | 5-level redirect chains, API endpoints, GitHub raw `.md` URLs |

---

## Gemini API Test Details

Both tracks test the same eight URLs and content types. The **Gemini-interpreted track**
asks the model to characterize each retrieval; the **raw track** reads `url_retrieval_status`
enums and `tool_use_prompt_token_count` directly from the response object.

| Test | Question | URLs / content |
| ---- | -------- | -------------- |
| 1: Single HTML page | _Baseline: what does a single successful fetch look like? What's the `tool_use_prompt_token_count`?_ | 1 HTML docs page |
| 2: Single PDF | _PDF is a documented supported type. Does it actually work?_ | 1 PDF - W3C WCAG 2.1 |
| 3: 5 URLs | _Multi-URL baseline. Does `url_context_metadata` preserve request order?_ | 5 Gemini API docs pages |
| 4: 20 URLs - at limit | _Does the tool handle the maximum documented URL count cleanly?_ | 20 Gemini API docs pages |
| 5: 21 URLs - over limit | _Is the limit a hard API error or silent truncation/dropping?_ | 21 Gemini API docs pages |
| 6: YouTube URL | _YouTube documented as unsupported. Does the documented limitation match actual behavior?_ | 1 YouTube watch URL |
| 7: Google Doc URL | _Google Workspace documented as unsupported. Does it fail at the API layer or the retrieval layer?_ | 1 Google Docs edit URL |
| 8: JSON API endpoint | _JSON is a documented supported type. Does it work for unauthenticated API endpoints?_ | 1 GitHub API endpoint |

---

## OpenAI API Test Details

Two tracks test the same queries through different API surfaces. The **ChatGPT-interpreted track**
uses the Chat Completions API with `gpt-4o-mini-search-preview` - search is always implicit.
The **raw track** uses the Responses API with `gpt-4o` + `web_search_preview` - tool invocation
is conditional and explicitly observable.

| Test | Question | Track |
| ---- | -------- | ----- |
| 1: Live data | _Does the tool always invoke for live data? Is citation count a reliable proxy for search depth?_ | Both |
| 2: Recent event | _How consistent are citation counts and source quality for a recent but stable fact?_ | Both |
| 3: Static fact | _Does the model skip the tool for a static fact? Is that behavior consistent across runs?_ | Both |
| 4: Trivial math | _Is tool invocation skipped for a query that needs no retrieval whatsoever?_ | Raw only |
| 5: Open-ended research | _Do internal search queries reflect the current date? Does `search_queries_issued` show stale date strings?_ | Both |
| 6: `search_context_size`: low | _What's the latency and source count at `low`?_ | Both |
| 7: `search_context_size`: high | _Does `high` produce more sources or lower latency than `low`? Is the tradeoff consistent across runs?_ | Both |
| 8: Domain filter, allow-list | _Does `allowed_domains` actually constrain sources returned? Does it work on `web_search` vs `web_search_preview`?_ | Raw only |
| 9: Domain filter, block-list | _Does `blocked_domains` work? What parameter name does the API accept?_ | Raw only |
| 10: Ambiguous query | _How does the model resolve "Python release" - programming language, animal, or both? Is disambiguation stable?_ | Both |

---

## Contribute

If you run these tests and get results, please open an issue or PR with your findings.

>_Especially useful: Run the same tests from different network locations or at different times to
check for caching behavior vs live-fetch variation; run PDF tests against different source URLs to
distinguish server-blocking from tool limitations; run Cursor tests with explicit model selection to
measure model-specific variance; test Cursor's MCP server integration vs native web fetch behavior_
