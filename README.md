# agent-ecosystem-testing

Empirical tests of web fetch behavior across AI agent platforms, in support of the
[Agent-Friendly Documentation Spec](https://github.com/agent-ecosystem/agent-docs-spec).

**Goal**: measure what actually happens between "agent fetches URL" and "model sees
content" - truncation limits, HTML processing, content negotiation - for
platforms that don't document these details.

**Origin**: contribution to
[Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/)
by Dachary Carey, which documented Claude Code's web fetch pipeline in detail. This repo
extends that work to the **Claude API's `web_fetch` tool**, which is a distinct
implementation from Claude Code's client-side fetch.

## Structure

```shell
agent-ecosystem-testing/
└── claude-api/
    └── web_fetch_test.py
└── docs
├── .gitignore
├── README.md
├── requirements.txt
```

## Running the Claude API Tests

### Prerequisites

- Python 3.8+
- An Anthropic API key

### Setup

```bash
# Clone the repo
git clone https://github.com/rhyannonjoy/agent-ecosystem-testing.git
cd agent-ecosystem-testing

# Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Run

```bash
python claude-api/web_fetch_test.py
```

Results print to the console and live in `claude-api/results/`
as JSON files with timestamps.

## Tests

### Test 1 - Short HTML page with heavy CSS, no token limit set

_Does the API tool have the same CSS-eating-content problem Dachary
found in Claude Code? What's the effective default token limit?_

Fetches a short docs page served as HTML. The page is known to have
substantial inline CSS before the content begins. Logs the raw `input_tokens`
count to establish the default behavior when `max_content_tokens` isn't set.

### Test 2 - Same page, markdown version

_Does the API tool request/prefer markdown? How much smaller is
the token footprint of the markdown version?_

Fetches the `.md` URL variant of the same page. Compares `input_tokens` to Test 1.

### Test 3 - Long page, no token limit

_At what point does the content get truncated? Does the API tool behave
differently than Claude Code (which truncated to ~100KB and passed through a
summarization model)?_

Fetches a long tabbed tutorial page without a `max_content_tokens` limit.

### Test 4 - Long page, explicit token limit

_Does the parameter work as documented? Is truncation clean or does it
cut mid-sentence?_

Same long page but with `max_content_tokens=5000` set explicitly.

## Contributing

If you run these tests and get results, please open an issue or
PR with your findings. _Especially useful_: running the same tests
from different network locations or at different times to check for
caching behavior.

Findings from this repo are contributions to the
[Known Platform Limits](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md#known-platform-limits)
table in the Agent-Friendly Docs Spec.
