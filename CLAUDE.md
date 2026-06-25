# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a Jekyll-published research site (GitHub Pages) plus a collection of Python test harnesses that empirically measure how different AI platforms fetch and transform web content. The goal is to produce reproducible, citable findings for the [Agent-Friendly Documentation Spec](https://agentdocsspec.com/).

The site lives in the Jekyll source files (`index.md`, `docs/`, `blogs/`, `_layouts/`, `_config.yml`). The test harnesses live in per-platform directories (`claude-api/`, `open-ai-web-search/`, `gemini-url-context/`, `cursor-web-fetch/`, `copilot-web-content-retrieval/`, `windsurf-cascade-web-search/`, `open-ai-codex-web-search/`).

## Common Commands

### Setup

```bash
# Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ruby/Jekyll dependencies (for the site)
bundle install

# API keys (variable names only; values are in .env, which is gitignored)
export ANTHROPIC_API_KEY="..."
export GOOGLE_GEMINI_API_KEY="..."
export OPEN_AI_API_KEY="..."
```

The `.env` file at the repo root contains the actual keys. It is tracked in the working tree but excluded from Jekyll builds (`_config.yml` `exclude`) and from git (`.gitignore`). Load it with `source .env` before running API tests, but do not commit it.

### Site

```bash
# Serve locally
bundle exec jekyll serve
# http://localhost:4000

# Build only
bundle exec jekyll build

# Clear build artifacts and cache
rm -rf _site .jekyll-cache
```

### Lint / Style

```bash
# Lint prose with Vale (Google style, configured in .vale.ini)
vale docs/ blogs/ index.md README.md
```

### Run Tests

Platforms split into two groups: **fully automated API tests** and **manual IDE/hybrid tests**. The API tests call the platform directly; the IDE tests generate prompts and log results that the user must run inside the IDE.

#### Automated API Tests

Run each script from the repo root. Each produces JSON results and a Markdown summary under the platform's `results/` directory.

```bash
# Claude API
python claude-api/web_fetch_test.py         # interpreted
python claude-api/web_fetch_test_raw.py     # raw

# OpenAI Web Search
python open-ai-web-search/web_search_test.py      # interpreted (Chat Completions)
python open-ai-web-search/web_search_test_raw.py  # raw (Responses API)

# Gemini URL Context
python gemini-url-context/url_context_test.py      # interpreted
python gemini-url-context/url_context_test_raw.py  # raw
```

#### Manual IDE Tests

These frameworks generate prompts but cannot drive the IDE. The `--test` argument is a test ID like `BL-1`, `SC-3`, `OP-2`, or `EC-6`. Use `--list-tests` to see options.

```bash
# Cursor
python cursor-web-fetch/web_fetch_testing_framework.py --list-tests
python cursor-web-fetch/web_fetch_testing_framework.py --test BL-1 --track interpreted
python cursor-web-fetch/web_fetch_testing_framework.py --test BL-1 --track raw
python cursor-web-fetch/web_fetch_verify_raw_results.py BL-1
python cursor-web-fetch/web_fetch_results_analyzer.py --csv results/raw/results.csv --full

# Copilot
python copilot-web-content-retrieval/web_content_retrieval_testing_framework.py --list-tests
python copilot-web-content-retrieval/web_content_retrieval_testing_framework.py --test BL-1 --track interpreted
python copilot-web-content-retrieval/web_content_retrieval_testing_framework.py --test BL-1 --track raw
python copilot-web-content-retrieval/web_content_retrieval_verify_raw_results.py BL-1
python copilot-web-content-retrieval/web_content_retrieval_results_analyzer.py --csv results/raw/results.csv --full

# Windsurf Cascade (three tracks: interpreted, explicit, raw)
python windsurf-cascade-web-search/web_search_testing_framework.py --list-tests
python windsurf-cascade-web-search/web_search_testing_framework.py --test BL-1 --track interpreted
python windsurf-cascade-web-search/web_search_testing_framework.py --test BL-1 --track explicit
python windsurf-cascade-web-search/web_search_testing_framework.py --test BL-1 --track raw
python windsurf-cascade-web-search/web_search_verify_raw_results.py BL-1
python windsurf-cascade-web-search/web_search_results_analyzer.py \
  --csv results/cascade-interpreted/results.csv results/cascade-explicit/results.csv --full

# OpenAI Codex (four tracks, manual IDE sessions)
python open-ai-codex-web-search/framework.py --list-tests
python open-ai-codex-web-search/framework.py --test BL-1 --track codex-interpreted
python open-ai-codex-web-search/framework.py --test BL-1 --track vscode-codex-interpreted
python open-ai-codex-web-search/framework.py --test BL-1 --track codex-raw
python open-ai-codex-web-search/framework.py --test BL-1 --track vscode-codex-raw
python open-ai-codex-web-search/verify.py BL-1 --all
python open-ai-codex-web-search/analyze.py \
  --csv results/codex-interpreted/results.csv results/codex-raw/results.csv --full

# Query Track 1 results for a test ID and format selected fields as Markdown
python open-ai-codex-web-search/scripts/query.py --test SC-1 --models GPT-5.4-Mini,GPT-5.5

# Inspect Codex .jsonl rollout logs
python open-ai-codex-web-search/scripts/rollout_audit.py results/{track}/artifacts/rollouts/*/*.jsonl --csv audit.csv
python open-ai-codex-web-search/scripts/rollout_decode.py results/{track}/artifacts/rollouts/{test}/rollout-*.jsonl --timeline
python open-ai-codex-web-search/scripts/session_reader.py results/{track}/artifacts/rollouts/{test}/rollout-*.jsonl -o report.html
```

### Run a Single Test

For API tests, each script typically defines a `main()` that runs its own fixed test suite; there is no per-test CLI selector. For IDE tests, run a single test ID with `--test {ID}` and `--track {track}` as shown above. Use `--list-tests` to see the available IDs for that platform.

## High-Level Architecture

### Two-Track Methodology

Every platform is tested with two tracks:

- **Interpreted** — ask the agent to describe what it retrieved. Captures self-perception, reasoning, and variance.
- **Raw** — extract measurements directly from the response object (API) or from verbatim saved output (IDE). Produces citable, reproducible numbers.

Cascade adds a third track, **explicit**, which is identical to interpreted but prefixes the prompt with `@web` to test whether the explicit directive changes retrieval behavior. Codex uses four tracks to isolate deployment surface (Codex IDE vs VS Code-Codex extension) and workspace presence.

### Site vs. Harness

- **Jekyll site** (`_config.yml`, `_layouts/default.html`, `index.md`, `docs/`, `blogs/`, `static/`) publishes the findings to GitHub Pages. `_config.yml` defines the navigation tree, markdown processor, and excluded directories. The Codex Framework Reference is documented in `docs/open-ai-codex/framework-reference.md`.
- **Python harnesses** run the tests and emit results. The site does not read results automatically; findings are written into `docs/` and `blogs/` by hand based on the harness output.

### Automated vs. IDE Tests

- **Automated** (`claude-api/`, `open-ai-web-search/`, `gemini-url-context/`): Python scripts call the platform SDK directly, save JSON and Markdown, and run end-to-end without human intervention.
- **IDE/hybrid** (`cursor-web-fetch/`, `copilot-web-content-retrieval/`, `windsurf-cascade-web-search/`, `open-ai-codex-web-search/`): Python scripts generate prompts and log results, but the actual agent interaction happens inside the IDE. The user copies the generated prompt into the IDE, captures the agent's output, and the framework logs it to CSV. The `*_verify_raw_results.py` scripts then compute metrics (bytes, characters, lines, words, tokens, MD5, code blocks, tables, headers) from the saved raw output files.

### Shared Test Corpus for IDE Platforms

Cursor, Copilot, Cascade, and Codex share the same `TEST_URLS` dictionary keyed by category and test ID:

- `BL` — baseline (progressive HTML/Markdown size from MongoDB docs)
- `SC` — structured content (tables, code blocks, nested headings, JS-rendered pages)
- `OP` — offset/pagination (fragment navigation, auto-chunking)
- `EC` — edge cases (redirect chains, SPAs, raw Markdown, JSON endpoints)

Sharing IDs and URLs enables direct cross-platform comparison.

### Results Pipeline

1. **Run**: API scripts write JSON + Markdown; IDE frameworks write CSV rows and raw text files.
2. **Verify**: `*_verify_raw_results.py` computes ground-truth metrics from saved raw output.
3. **Analyze**: `*_results_analyzer.py` (or `open-ai-codex-web-search/analyze.py`) normalizes interpreted and raw CSV schemas and compares them against a set of hypotheses (H1–H5).
4. **Document**: Findings are written into `docs/` and `blogs/` as Markdown for Jekyll to publish.

### Key Conventions

- API tests save under `results/{timestamp}/` or `results/{track}/{timestamp}/`. IDE tests append to `results/{track}/results.csv` and save raw output to `results/raw/raw_output_{test_id}.txt`.
- Token counts for IDE platforms use `tiktoken` with `cl100k_base`; API platforms use the platform's native token accounting.
- Rate-limit sleeps are hardcoded for free tiers. For paid tiers, set `RATE_LIMIT_SLEEP_SECONDS = 0` in the relevant script.
- The `.git-com.yaml` file configures an interactive commit-message helper with change-type prefixes, code-section labels, and ticket numbers. It is not a CI config.
