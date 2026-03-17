# Cursor Web Fetch Testing Framework

Automated testing framework for measuring Cursor IDE's `@web` and MCP truncation behavior.

## Overview

This framework generates standardized test prompts and logs results to CSV, making it easy to:
- Run consistent tests across multiple test cases
- Track measurements over time
- Identify truncation patterns
- Compare different fetch methods (@web vs mcp-server-fetch)

## Setup

### Requirements

- Python 3.8+
- Cursor IDE installed locally
- No API keys needed (testing through chat interface)

### Installation

```bash
# Clone or navigate to your agent-ecosystem-testing directory
cd agent-ecosystem-testing/cursor

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install dependencies (if needed)
pip install -r requirements.txt
```

The framework uses only Python standard library, so no additional packages required.

## Quick Start

### 1. List Available Tests

```bash
python cursor_testing_framework.py --list-tests
```

This shows all 14 test cases organized by category:
- **Baseline (BL)**: Small, medium, large documents
- **Structured Content (SC)**: Markdown, API docs, tables, code
- **Offset/Pagination (OP)**: Fragment IDs, chunking, auto-retry
- **Edge Cases (EC)**: JavaScript, redirects, long lines

### 2. Generate Test Prompt for a Single Test

```bash
# Interpreted track (ask model to report measurements)
python web_fetch_testing_framework.py --test BL-1 --track interpreted

# Raw track (request verbatim output)
python web_fetch_testing_framework.py --test BL-2 --track raw
```

This prints a formatted test harness with:
- The exact prompt to copy into Cursor
- Fields you need to fill in
- Expected size reference

### 3. Copy Prompt → Run in Cursor

1. Copy the prompt printed to console
2. Open Cursor IDE
3. Paste prompt into chat
4. Let Cursor fetch the URL
5. Copy the response

### 4. Log Results

```bash
# Log interpreted track result
python cursor_testing_framework.py --log BL-1 \
  --track interpreted \
  --method @web \
  --model "Claude 3.5 Sonnet" \
  --cursor-version "0.36.0" \
  --output-chars 48500 \
  --truncated no \
  --tokens 12000 \
  --hypothesis "H1-no" \
  --notes "Full content returned, no truncation observed"

# Log raw track result with truncation
python cursor_testing_framework.py --log BL-2 \
  --track raw \
  --method @web \
  --model "Claude 3.5 Sonnet" \
  --cursor-version "0.36.0" \
  --output-chars 9876 \
  --truncated yes \
  --truncation-point 9876 \
  --tokens 2469 \
  --hypothesis "H1-yes" \
  --notes "Truncated mid-paragraph at 9876 characters"
```

Results are logged to `cursor-testing-results/results-YYYY-MM-DDTHH-MM.csv`

## Testing Workflow

### Step-by-Step for BL-1

```bash
# 1. Print test harness
python cursor_testing_framework.py --test BL-1 --track interpreted

# Expected output:
# TEST HARNESS: BL-1 - Small Wikipedia Article
# ...
# PROMPT TO COPY INTO CURSOR:
# [Copy this and paste into Cursor chat]

# 2. Open Cursor, paste prompt, run it

# 3. Review Cursor's response, note:
#    - Total character count
#    - Whether truncated
#    - Last 50 characters
#    - Formatting quality

# 4. Log the result
python cursor_testing_framework.py --log BL-1 \
  --track interpreted \
  --method @web \
  --model "Claude 3.5 Sonnet" \
  --cursor-version "0.36.0" \
  --output-chars 48500 \
  --truncated no \
  --tokens 12000 \
  --hypothesis "H1-no" \
  --notes "Full content, markdown complete"
```

### Testing Strategy

**Baseline Testing Path (Single-Run Reproducible)**

Run each test **once** in **interpreted track** only. This produces a reproducible baseline without follow-up runs.

1. **BL-1, BL-2** (baseline, quick wins) - ~30 min
   - Establishes basic truncation threshold
   - Single run each, interpreted track
   
2. **SC-2** (code blocks) - ~20 min
   - Tests HTML-to-markdown conversion
   - Single run, interpreted track
   
3. **OP-3** (@web vs mcp comparison) - ~20 min
   - Answers: Do MCP servers have different limits?
   - Single run, interpreted track
   
4. **OP-4** (auto-chunking) - ~30 min
   - Key ecosystem testing gap
   - Determines developer experience
   - Single run, interpreted track
   
5. **BL-3** (hard ceiling) - ~20 min
   - Find absolute limit
   - Single run, interpreted track
   
6. **SC-1, SC-3, SC-4** (structured content) - ~1 hour
   - Structure-aware truncation hypothesis
   - Single run each, interpreted track
   
7. **EC-1, EC-3, EC-6** (edge cases) - ~1 hour
   - Failure modes and unusual inputs
   - Single run each, interpreted track

### Optional: Extended Testing

After completing the baseline, you can optionally run additional tracks for richer analysis:
- **Raw track** on key tests (BL-1, SC-2, OP-4) for exact measurements
- **Rerun interpreted** on 2-3 tests to measure variance across runs
- Use the analyzer to compare interpreted vs raw results

This produces deeper findings but is not required for reproducibility or spec contribution.

## Analyzing Results

### View All Results

```bash
python cursor_testing_analyzer.py --csv results-2025-03-15T15-30.csv --summary
```

This generates:
- Truncation threshold analysis
- Method comparison (if testing multiple)
- Interpreted vs raw track comparison
- Hypothesis matching
- Markdown table for spec contribution

### Analyze Specific Method

```bash
python cursor_testing_analyzer.py --csv results.csv --method "@web"
```

### Export as Markdown

```bash
python cursor_testing_analyzer.py --csv results.csv --markdown
```

Outputs a markdown table suitable for GitHub/spec documentation.

## Two-Track Methodology

Each test is run in **two complementary tracks**:

### Interpreted Track
- **What**: Ask Cursor to describe what it received
- **Why**: Captures perception gaps, developer experience
- **Varies**: Results differ between runs (model variance)
- **Use for**: Understanding user experience, finding estimation errors

### Raw Track
- **What**: Request verbatim output, measure manually
- **Why**: Produces reproducible, exact measurements
- **Varies**: Should be consistent (same URL = same content)
- **Use for**: Citable spec documentation, hard data

Run both tracks on key tests (BL, OP, SC) to validate findings.

## CSV Output Format

Results are logged to CSV with columns:
- `test_id`: BL-1, SC-2, etc.
- `date`: YYYY-MM-DD
- `url`: Full URL tested
- `method`: @web, mcp-server-fetch, etc.
- `model`: Claude 3.5 Sonnet, GPT-4o, etc.
- `input_est_chars`: Expected input size
- `output_chars`: Actual output length
- `truncated`: yes/no
- `truncation_char_num`: Exact character position if truncated
- `tokens_est`: Estimated token count
- `hypothesis_match`: H1/H2/H3/H4/H5
- `notes`: Any observations
- `track`: interpreted/raw
- `cursor_version`: Cursor IDE version used

## Key Hypotheses to Test

- **H1**: Character-based truncation at fixed limit (~10-100KB?)
- **H2**: Token-based truncation (~2000 tokens?)
- **H3**: Structure-aware truncation (respects markdown boundaries)
- **H4**: MCP servers override native @web limits
- **H5**: Agent auto-chunks after truncation (requests next chunk automatically)

Log which hypothesis each test supports in the `--hypothesis` flag.

## Tips for Accurate Testing

### For Interpreted Track

1. Ask Cursor to be **specific** about lengths (not "approximately")
2. **Request token count estimation** - ask Cursor to estimate using 4 characters per token as baseline
3. Request **last 50 characters** to verify truncation point
4. Ask about **markdown completeness** (are code blocks closed?)
5. Run 2-3 times per test to capture variance

### For Raw Track

1. Copy Cursor's output **exactly as received**
2. Use Python `len()` to count characters: `len(content)`
3. Use `tiktoken` to count tokens accurately:
   ```python
   import tiktoken
   enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
   token_count = len(enc.encode(content))
   ```
4. Note **last 50 characters** to verify boundary
5. Check if truncation was **clean** (mid-word? mid-tag?)

### Token Count Logging

**Important**: Only log token counts that Cursor explicitly provided or you calculated.

- **If Cursor estimated it**: Use that number, note in the command that it's Cursor's estimate
- **If you calculated it**: Use the 4-character-per-token baseline: `chars / 4 = tokens`
- **If uncertain**: Use `0` and note in `--notes` that token count needs verification

Example:
```bash
# Cursor provided the estimate
python cursor-web-fetch/web_fetch_testing_framework.py --log OP-4 \
  --track interpreted \
  --method @web \
  --model "Claude 3.5 Sonnet" \
  --cursor-version "0.36.0" \
  --output-chars 245000 \
  --truncated no \
  --tokens 61250 \
  --hypothesis "H2-yes" \
  --notes "Token count estimated by Cursor using 4-char/token baseline"
```

### Environment Variables

Set these to avoid typing repeatedly:

```bash
export CURSOR_VERSION="0.36.0"
export CURSOR_MODEL="Claude 3.5 Sonnet"
```

Then use in commands:
```bash
python cursor_testing_framework.py --log BL-1 \
  --track interpreted \
  --method @web \
  --model "$CURSOR_MODEL" \
  --cursor-version "$CURSOR_VERSION" \
  ...
```

## Troubleshooting

### "Unknown test ID"
```bash
python cursor_testing_framework.py --list-tests  # Check valid IDs
```

### Results not logging
- Verify `cursor-testing-results/` directory exists (created automatically)
- Check that all required flags are provided: `--method`, `--model`, `--cursor-version`, `--output-chars`, `--truncated`, `--tokens`, `--hypothesis`

### Need to re-run a test
- Just run `--log` again with same test_id, date, track
- Script appends to CSV (doesn't overwrite)
- If you want fresh start: delete the CSV file

## Contributing Results

When you have meaningful findings, run analyzer to generate markdown table:
   
   ```bash
   python web_fetch_results_analyzer.py --csv results.csv --markdown

   python web_fetch_results_analyzer.py --csv results/cursor-interpreted/results.csv --full > results/cursor-interpreted/full-analysis.txt

   python web_fetch_results_analyzer.py --csv results/cursor-interpreted/results.csv --summary > results/cursor-interpreted/summary.txt
   ```
