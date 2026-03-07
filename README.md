# Agent Ecosystem Testing

**Overview**: Empirical tests of web fetch behavior across AI agent platforms, in support of the
[Agent-Friendly Documentation Spec](https://github.com/agent-ecosystem/agent-docs-spec)
and specifically contributes data to the
[Known Platform Limits](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits).
Full methodology and findings:
[testing methodology and results docs](https://rhyannonjoy.github.io/agent-ecosystem-testing/).

**Origin**: extension of Dachary Carey's
[Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/),
which documented Claude Code's web fetch pipeline in detail.

**Goal**: measure what actually happens between "agent fetches URL" and
"model sees content" - truncation limits, HTML processing, content
negotiation - for platforms that don't document these details.

---

## Platforms Tested

| Platform | Tool | Scripts | Results |
| -------- | ---- | ------- | ------- |
| Anthropic Claude API | web fetch tool | `claude-api/` | `claude-api/results/` |
| Google Gemini API | URL context tool | `gemini-url-context/` | `gemini-url-context/results/` |

Each platform has two tracks:

- **Interpreted** - the model is asked to reflect on what it retrieved; captures self-perception and estimation variance
- **Raw** - Python extracts measurements directly from the response object; produces citable, reproducible numbers

---

## Setup

### Prerequisites

- Python 3.8+
- API key for the platforms you want to test

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

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
export GOOGLE_GEMINI_API_KEY="your-key-here"  
```

### Run Tests

```bash
# Results print to the console, live in `claude-api/results/`
# Claude-interpreted
python claude-api/web_fetch_test.py
# Raw
python claude-api/web_fetch_test_raw.py

# Gemini-interpreted
python gemini-url-context/url_context_test.py
# Raw
python gemini-url-context/url_context_test_raw.py

# Each run saves to a timestamped subdirectory:
# gemini-url-context/results/gemini-interpreted/YYYY-MM-DDTHH-MM/
# gemini-url-context/results/raw/YYYY-MM-DDTHH-MM/
```

> _**Free tier limits**: Claude API not available on the free-tier, the API is pay-as-you-go;
5 RPM and 20 RPD limits for `gemini-2.5-flash`- running both tracks in the same day will exhaust
the daily quota; plan runs across days or use a paid tier; set `RATE_LIMIT_SLEEP_SECONDS = 0`
in the scripts if you're on a paid tier_

---

## Claude API Test Details

| Test | Question | What it fetches |
| ---- | -------- | --------------- |
| 1: Short HTML, no token limit | _Does the API tool have the same CSS-eating-content problem Dachary found in Claude Code? What's the effective default token limit?_ | Short docs page with substantial inline CSS before content begins |
| 2: Same page, Markdown version | _Does the API tool request or prefer Markdown? How much smaller is the token footprint?_ | `.md` URL variant of Test 1 - compares `input_tokens` directly |
| 3: Long page, no token limit | _At what point does content get truncated? Does the API tool behave differently than Claude Code, which truncated to ~100KB?_ | Long tabbed tutorial page, no `max_content_tokens` set |
| 4: Long page, explicit token limit | _Does `max_content_tokens=5000` work as documented? Is truncation clean or mid-sentence?_ | Same page as Test 3, with `max_content_tokens=5000` |

---

## Gemini API Test Details

| Test | Question | URLs / content |
| ---- | -------- | -------------- |
| 1: Single HTML page | _Baseline: what does a single successful fetch look like? What's the `tool_use_prompt_token_count`?_ | 1 HTML docs page |
| 2: Single PDF | _PDF is a documented supported type. Does it actually work?_ | 1 PDF - W3C WCAG 2.1 |
| 3: 5 URLs | _Multi-URL baseline. Does `url_context_metadata` preserve request order?_ | 5 Gemini API docs pages |
| 4: 20 URLs - at limit | _Does the tool handle the maximum documented URL count cleanly?_ | 20 Gemini API docs pages |
| 5: 21 URLs - over limit | _Is the limit a hard API error or silent truncation/dropping?_ | 21 Gemini API docs pages |
| 6: YouTube URL | _YouTube is documented as unsupported. Does the documented limitation match actual behavior?_ | 1 YouTube watch URL |
| 7: Google Doc URL | _Google Workspace is documented as unsupported. Does it fail at the API layer or the retrieval layer?_ | 1 Google Docs edit URL |
| 8: JSON API endpoint | _JSON is a documented supported type. Does it work for unauthenticated API endpoints?_ | 1 GitHub API endpoint |

---

## Contribute

If you run these tests and get results, please open an issue or PR with your findings.

>_Especially useful: Run the same tests from different network locations or at different times to
check for caching behavior vs live-fetch variation; run PDF tests against different source URLs to
distinguish server-blocking from tool limitations; run Gemini tests on a paid tier to get a complete
8-test run without hitting the daily quota_
