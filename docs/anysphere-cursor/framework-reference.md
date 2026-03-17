---
layout: default
title: "Framework Reference"
permalink: /docs/anysphere-cursor/framework-reference
parent: Anysphere Cursor
---

## Cursor Framework Reference

>_This framework generates standardized test prompts and logs CSV results,
enabling consistent testing across cases, measurement tracking over time,
truncation pattern identification, and fetch method comparisons_<br>
>_**Requirements**: Python 3.8+, [Cursor IDE](https://cursor.com/download)_

---

## Installation

```bash
# Clone and/or navigate to `agent-ecosystem-testing` directory
cd agent-ecosystem-testing/cursor-web-fetch

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Workflow

1. **List Available Tests**

   ```bash
   python web_fetch_testing_framework.py --list-tests
   ```  

2. **Generate Test Prompt for a Single Test**

   Print a formatted test harness with a structured prompt to copy
   into the Cursor chat window, fields requiring values, and
   expected size reference:

   ```bash
   # Cursor-interpreted track - ask model to report measurements
   python web_fetch_testing_framework.py --test BL-1 --track interpreted

   # Raw track - request verbatim output
   python web_fetch_testing_framework.py --test BL-2 --track raw
   ```

3. **Copy Prompt → Run in Cursor**

   - Review the Terminal output, copy the prompt
   - Open Cursor chat window, paste the prompt
   - Review Cursor's fetch behavior
   - Examine the response

4. **Log Results**

   Depending on the track, results are stored in
   `cursor-web-fetch/results/{track}/results.csv` with the following fields:

   | Column | Description | Example |
   | --- | --- | --- |
   | `test_id` | Test identifier | BL-1, SC-2, EC-1 |
   | `timestamp` | ISO 8601 timestamp | 2026-03-16T17:05:02.998376 |
   | `date` | Date tested | 2026-03-16 |
   | `url` | Full URL tested | https://www.mongodb.com/docs...|
   | `method` | Fetch method | `@Web`*, `mcp-server-fetch` |
   | `model` | Model used | `Auto` - Cursor's agent router |
   | `input_est_chars` | Expected input size | 87040 |
   | `output_chars` | Actual output length | 5857 |
   | `truncated` | Truncation detected | yes/no |
   | `truncation_char_num` | Character position if truncated | 5857 |
   | `tokens_est` | Estimated token count | 1464 |
   | `hypothesis_match` | Hypothesis matched | H1-no, H2-yes, H3-yes |
   | `notes` | Observations and findings | Pro-plan retry: successfully... |
   | `track` | Test track | interpreted/raw |
   | `cursor_version` | Cursor IDE version | 2.6.19, 2.6.19-pro |

   >_*`@Web` is a Cursor UI composer feature, but the underlying mechanism is `web_search` -
   > more information in the [Friction Note](friction-note.md#web-is-a-context-mention-not-a-tool)_

   ---

   **Key Hypotheses**:

   - **H1**: Character-based truncation at fixed limit, _~10-100KB?_
   - **H2**: Token-based truncation, _~2000 tokens?_
   - **H3**: Structure-aware truncation, respects Markdown boundaries
   - **H4**: MCP servers override native `@Web` limits
   - **H5**: Agent auto-chunks after truncation, requests next chunk automatically

   ```bash
   # Log interpreted track result
   python web_fetch_testing_framework.py --log BL-1 \
   --track interpreted \
   --method @Web \
   --model "Auto" \
   --cursor-version "2.6.19" \
   --output-chars 48500 \
   --truncated no \
   --tokens 12000 \
   --hypothesis "H1-no" \
   --notes "Full content returned, no truncation observed"

   # Log raw track result with truncation
   python web_fetch_testing_framework.py --log BL-2 \
   --track raw \
   --method @Web \
   --model "Auto" \
   --cursor-version "2.6.19" \
   --output-chars 9876 \
   --truncated yes \
   --truncation-point 9876 \
   --tokens 2469 \
   --hypothesis "H1-yes" \
   --notes "Truncated mid-paragraph at 9876 characters"
   ```

   >_Ensure all required flags are provided: `--method`, `--model`, `--cursor-version`,
   >`--output-chars`, `--truncated`, `--tokens`, `--hypothesis`

---

## Baseline Testing Path, Single-Run Reproducible Strategy

1. **BL-1, BL-2**: baseline, quick wins establish basic truncation threshold
2. **SC-2**: code blocks, tests HTML-to-Markdown conversion
3. **OP-3**: `@Web` vs MCP, _do MCP servers have different limits?_
4. **OP-4**: auto-chunking, determines DX and key ecosystem testing gap   
5. **BL-3**: hard ceiling to identify absolute limit   
6. **SC-1, SC-3, SC-4**: structured content to test structure-aware truncation hypothesis
7. **EC-1, EC-3, EC-6**: edge cases to identify failure modes and unusual inputs

---

## Extended Testing, _Optional_

- **Run raw track** on key tests BL-1, SC-2, OP-4 for exact measurements
- **Rerun interpreted** on 2-3 tests to measure variance across runs

---

## Analyzing Results

Examine truncation threshold analysis, method comparison, interpretive vs raw
track comparisons, hypothesis matching -

```bash
# Generate summary
python web_fetch_results_analyzer.py --csv results.csv --summary

# Generate full analysis
python web_fetch_results_analyzer.py --csv results.csv --full

# Analyze specific methods
python web_fetch_results_analyzer.py --csv results.csv --method "@Web"

# Export as Markdown
python web_fetch_results_analyzer.py --csv results.csv --markdown
```

>_**Remember** to always provide the full relative path to the CSV file when running the analyzer,
> including the subdirectory: `results/cursor-interpreted/results.csv` or `results/raw/results.csv`_
