# Agent Ecosystem Testing

**Overview**: empirically tests web fetch behavior across agentic platforms to contribute to the
[Agent-Friendly Documentation Spec](https://github.com/agent-ecosystem/agent-docs-spec) -
specifically the [Known Platform Limits](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits);
full methodology and findings in [the docs](https://rhyannonjoy.github.io/agent-ecosystem-testing/)

**Origin**: programmatic extension of Dachary Carey's
[Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/)

**Goal**: measure what happens between _"agent fetches URL"_ and _"user sees output"_ -
retrieval mechanism behavior, content transformation, architectural constraints. Observes the
URL-to-response pipeline through layers platforms don't disclose.

---

## Platforms Tested

| Platform | Tool | Scripts, Results |
| -------- | ---- | ------- |
| Anthropic Claude API | [web fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) | `claude-api/` |
| Anysphere Cursor IDE | [`@Web` context attachment](https://cursor.com/docs/agent/prompting) | `cursor-web-fetch/` |
| Cognition Windsurf<br>Cascade IDE | `read_url_content`,<br>[`@web` directive](https://docs.windsurf.com/windsurf/cascade/web-search) | `windsurf-cascade-web-search/` |
| Google Gemini API | [URL context](https://ai.google.dev/gemini-api/docs/url-context) | `gemini-url-context/` |
| Microsoft GitHub<br>Copilot Extension | `fetch_webpage` | `copilot-web-content-retrieval/` |
| OpenAI APIs<br>Chat Completions,<br>Responses | [web search](https://developers.openai.com/api/docs/guides/tools-web-search) | `open-ai-web-search/` |

Each platform has two tracks:

- **Interpreted** - ask the agent to reflect on what it retrieved; captures self-perception and estimation variance
- **Raw** - Python extracts measurements directly from the response object; produces citable, reproducible numbers

> _Cursor, Copilot and Cascade testing use a hybrid approach: raw track saves verbatim output to disk
> for programmatic analysis; interpreted track asks the agent to self-report metrics from
> fetched content. Visit the
> [Cursor Friction Note](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/anysphere-cursor/friction-note)
> and
> [Copilot Friction Note](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/microsoft-github-copilot/friction-note)
> for methodology challenges unique to IDE-based testing_.
>
> _Cascade adds a third track: **explicit** - identical to interpreted, but prefixed with `@web`; designed to test whether it changes retrieval ceiling, tool chain, or chunking behavior; [Cascade Friction: Explicit](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/cognition-windsurf-cascade/friction-note-explicit) analysis._

---

## Setup

### Prerequisites

- Python 3.8+
- API keys for the applicable platforms
- Copilot extension-chat, Cursor and/or Windsurf-Cascade IDEs if applicable

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
# Cascade-interpreted, no `@web`
python windsurf-cascade-web-search/web_search_testing_framework.py --test {test ID} --track interpreted
# Explicit, `@web` prefixed
python windsurf-cascade-web-search/web_search_testing_framework.py --test {test ID} --track explicit
# Raw
python windsurf-cascade-web-search/web_search_testing_framework.py --test {test ID} --track raw

# ChatGPT-interpreted
python open-ai-web-search/web_search_test.py
# Raw
python open-ai-web-search/web_search_test_raw.py

# Claude-interpreted
python claude-api/web_fetch_test.py
# Raw
python claude-api/web_fetch_test_raw.py

# Copilot-interpreted
python copilot-web-content-retrieval/web_content_retrieval_testing_framework.py --test {test ID} --track interpreted
# Raw
python copilot-web-content-retrieval/web_content_retrieval_testing_framework.py --test {test ID} --track raw

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
the daily quota; plan runs across days or use a paid tier; Cascade, Copilot, and Cursor tests
available on Pro Plan; OpenAI requires a minimum credit top-up (~$5) before any API call succeeds
regardless of agent - `insufficient_quota` is an account-level block, not a rate limit; set
`RATE_LIMIT_SLEEP_SECONDS = 0` in the scripts if you're on a paid tier_

---

## Cascade Test Details

Like Copilot and Cursor, Cascade testing uses manual chat sessions in the Windsurf IDE.
The framework generates prompts, but execution requires copy-paste into the Cascade chat
panel. Cascade is the first platform in this collection with a user-invocable web directive,
`@web`, making it the primary variable under test alongside the standard truncation questions.
All 11 URLs run across three tracks; interpreted and explicit track results compared
directly to isolate the `@web` effect.

| Category | Question | Source |
| --- | --- | --- |
| Baseline | _What does Cascade retrieve by default? Does `@web` change the ceiling/output size on the same URL?_ | MongoDB docs ~20KB–256KB; HTML, Markdown URL variants |
| Structured Content | _How does Cascade handle tables, code blocks, nested headings, and JavaScript-rendered pages?_ | Wikipedia, Anthropic API docs, Markdown Guide, Gemini docs |
| Offset/<br>Pagination | _Does `view_content_chunk` auto-paginate after truncation, or only when prompted?_ | 256KB MongoDB tutorial; fragment navigation via URL `#` identifier |
| Edge<br>Cases | _How does Cascade handle redirect chains, SPAs, raw Markdown files, and JSON endpoints?_ | 5-hop redirect chain, Gemini landing page, GitHub raw `.md` |

> _Cascade self-reported three tools: `read_url_content` for
> URL fetch, `view_content_chunk` for paginating documents via `DocumentId`, and `search_web`
> for query-based lookup. `read_url_content` requires approval before execution,
> a behavior with no Copilot or Cursor equivalent._

---

## Claude API Test Details

Both tracks test the same four URLs. The **Claude-interpreted track** asks the agent to
describe what it received; the **raw track** extracts character counts, CSS indicators,
and truncation signals programmatically from the `web_fetch_tool_result` block.

| Category | Question | Source |
| ---- | -------- | --------------- |
| Short HTML, no token limit | _Does the API tool have the same CSS-eating-content problem Dachary found in Claude Code? What's the effective default token limit?_ | Short docs page with substantial inline CSS before content begins |
| Same page, Markdown version | _Does the API tool request or prefer Markdown? How much smaller is the token footprint?_ | `.md` URL variant of first test, compares `input_tokens` directly |
| Long page, no token limit | _At what point does content get truncated? Does the API tool behave differently than Claude Code, which truncated to ~100KB?_ | Long tabbed tutorial page, no `max_content_tokens` set |
| Long page, explicit token limit | _Does `max_content_tokens=5000` work as documented? Is truncation clean or mid-sentence?_ | Same page as Test 3, with `max_content_tokens=5000` |

---

## Copilot Test Details

Unlike API-based platforms, Copilot testing uses manual chat sessions in the VS Code IDE.
The framework generates prompts, but execution requires copy-paste into the Copilot chat
window. Both tracks test 11 distinct URLs across baseline, structured content, offset,
and edge case categories. The primary finding is that Copilot autonomously selects between
two retrieval mechanisms -`fetch_webpage` and `curl` - with no prompt control, and the
mechanism selected determines output format more than any other variable.

| Category | Question | Source |
| --- | --- | --- |
| Baseline | _What does Copilot retrieve by default? How does output vary across agent routing and HTML vs Markdown URLs?_ | MongoDB docs pages at 20KB–256KB; HTML and Markdown URL variants |
| Structured Content | _How does Copilot handle tables, code blocks, nested headings, and JavaScript-rendered pages?_ | Wikipedia, Anthropic API docs, Markdown Guide, Google Gemini docs |
| Offset/Pagination | _Does Copilot auto-chunk after apparent truncation? Can it paginate a large document?_ | 256KB MongoDB tutorial; fragment navigation |
| Edge Cases | _How does Copilot handle redirect chains, SPAs, raw Markdown files, and JSON endpoints?_ | 5-level redirect chain, Gemini landing page, GitHub raw `.md`, `httpbin.org` |

> _Copilot has no publicly documented web fetch mechanism. `fetch_webpage` surfaced
> through tool logs. When `curl` substitution occurs, it happens without disclosure
> in the chat UI. Read the
> [Friction Note](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/microsoft-github-copilot/friction-note)
> for analysis._

---

## Cursor Test Details

Unlike testing platforms with API web fetch tools, Cursor testing uses manual chat sessions with the Cursor IDE. The framework
generates prompts, but execution is intentionally not automated and requires copy-paste into the Cursor IDE. Interpreted track asks Cursor to self-report; raw track saves outputs to disk for measurement. Both tracks test 13 distinct URLs. Tests focus on truncation behavior, backend routing variance, content conversion patterns, and reproducibility.

| Category | Question | Source |
| --- | --- | --- |
| Baseline | _What's the reproducibility baseline? Do same URLs always return identical content?_ | Small docs pages (4-20KB), tested multiple times to measure variance |
| Structure-Aware | _Does Cursor truncate intelligently at content boundaries, or cut mid-content?_ | Wikipedia pages, Markdown guides, docs with complex structure |
| Output Pattern | _What triggers Markdown conversion vs raw HTML?_ | Large tutorials, JavaScript-heavy SPAs, timeout scenarios |
| Edge Cases | _How does Cursor handle redirects, JSON endpoints, raw Markdown files, and version drift?_ | 5-level redirect chains, API endpoints, GitHub raw `.md` URLs |

---

## Gemini API Test Details

Both tracks test the same eight URLs and content types. The **Gemini-interpreted track**
asks the agent to characterize each retrieval; the **raw track** reads `url_retrieval_status`
enums and `tool_use_prompt_token_count` directly from the response object.

| Category | Question | Source |
| ---- | -------- | -------------- |
| Single HTML page | _Baseline: what does a single successful fetch look like? What's the `tool_use_prompt_token_count`?_ | Gemini docs |
| Single PDF | _PDF is a documented supported type. Does it actually work?_ | W3C WCAG 2.1 |
| 5 URLs | _Multi-URL baseline. Does `url_context_metadata` preserve request order?_ | Gemini API docs |
| 20 URLs,<br>at limit | _Does the tool handle the maximum documented URL count cleanly?_ | Gemini API docs |
| 21 URLs,<br>over limit | _Is the limit a hard API error or silent truncation/dropping?_ | Gemini API docs |
| "Unsupported" | _YouTube documented as unsupported. Does the documented limitation match actual behavior?_ | YouTube music video |
| "Unsupported" | _Google Workspace documented as unsupported. Does it fail at the API layer or the retrieval layer?_ | Google Docs edit URL |
| JSON API endpoint | _JSON is a documented supported type. Does it work for unauthenticated API endpoints?_ | GitHub API |

---

## OpenAI API Test Details

Two tracks test the same queries through different API surfaces. The **ChatGPT-interpreted track**
uses the Chat Completions API with `gpt-4o-mini-search-preview` in which search is always implicit.
The **raw track** uses the Responses API with `gpt-4o` + `web_search_preview` in which tool invocation
is conditional, explicitly observable.

| Category | Question | Track |
| ---- | -------- | ----- |
| Live Data | _Does the tool always invoke for live data? Is citation count a reliable proxy for search depth?_ | Both |
| Recent Event | _How consistent are citation counts and source quality for a recent but stable fact?_ | Both |
| Static Fact | _Does the agent skip the tool for a static fact? Is that behavior consistent across runs?_ | Both |
| Trivial Math | _Is tool invocation skipped for a query that needs no retrieval whatsoever?_ | Raw |
| Open-ended<br>Research | _Do internal search queries reflect the current date? Does `search_queries_issued` show stale date strings?_ | Both |
| `search_context_size` Low | _What's the latency and source count at `low`?_ | Both |
| `search_context_size` High | _Does `high` produce more sources or lower latency than `low`? Is the tradeoff consistent across runs?_ | Both |
| Domain Filter<br>Allow List | _Does `allowed_domains` actually constrain sources returned? Does it work on `web_search` vs `web_search_preview`?_ | Raw |
| Domain filter<br>Block List | _Does `blocked_domains` work? What parameter name does the API accept?_ | Raw |
| Ambiguous<br>Query | _How does the agent resolve "Python release" - programming language, animal, or both? Is disambiguation stable?_ | Both |

---

## Contribute

If you run these tests and get results, please open an issue or PR with your findings.

>_Especially useful: Run the same tests from different network locations or at different times to
check for caching behavior vs live-fetch variation; run PDF tests against different source URLs to
distinguish server-blocking from tool limitations; run Cursor tests with explicit agent selection to
measure agent-specific variance; test Cursor's MCP server integration vs native web fetch behavior_
