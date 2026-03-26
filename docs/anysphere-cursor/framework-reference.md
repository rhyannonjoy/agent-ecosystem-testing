---
layout: default
title: "Framework Reference"
permalink: /docs/anysphere-cursor/framework-reference
parent: Anysphere Cursor
---

## Cursor Framework Reference

>_This framework generates standardized test prompts and logs CSV results,
>enabling consistent testing across cases, measurement tracking over time,
>truncation pattern identification, and fetch method comparisons_<br>
>_**Requirements**: Python 3.8+, [Cursor IDE](https://cursor.com/download)_

---

## Topic Guide

- [Installation](#installation)
- [Workflow](#workflow)
- [Baseline Testing Path - Single-Run Reproducible Strategy](#baseline-testing-path---single-run-reproducible-strategy)
- [Extended Testing, _Optional_](#extended-testing-optional)
- [Analyzing Results](#analyzing-results)

---

## Installation

```bash
# Clone and/or navigate to `agent-ecosystem-testing` directory
cd agent-ecosystem-testing

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to the Cursor testing directory
cd cursor-web-fetch
```

>_For whatever reason, such as incompatible Python versions or some accidental corruption,
>use `rm -rf venv` to remove the `venv` and start over_

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

   - Review the Terminal output &rarr; copy the prompt
   - Open Cursor chat window &rarr; paste the prompt
   - Review Cursor's fetch behavior &rarr; examine the response

4. **Log Results**

   Depending on the track, results stored in
   `cursor-web-fetch/results/{track}/results.csv` with the following fields:

   | Column | Description | Example |
   | --- | --- | --- |
   | `test_id` | Test identifier | BL-1, SC-2, EC-1 |
   | `timestamp` | ISO 8601 timestamp | 2026-03-16T17:05:02.998376 |
   | `date` | Date tested | 2026-03-16 |
   | `url` | Full URL tested | https://www.mongodb.com/docs...|
   | `method` | Fetch method | `@Web`* |
   | `model` | Model used | `Auto` - Cursor's agent router |
   | `input_est_chars` | Expected input size | 87040 |
   | `output_chars` | Actual output length, chars via `wc -m` | 27890 |
   | `truncated` | Truncation detected | yes/no |
   | `truncation_char_num` | Character position if truncated | 5857 |
   | `tokens` | Token count via `tiktoken` | 16890 |
   | `hypothesis_match` | Hypothesis matched | H1-no, H2-yes, H3-yes |
   | `notes` | Observations and findings | Pro-plan retry: successfully... |
   | `track` | Test track | interpreted/raw |
   | `cursor_version` | Cursor IDE version | 2.6.19, 2.6.19-pro |
   | `file_size_bytes`** | Exact file size via `ls -l` | 28158 |
   | `md5_checksum`** | MD5 of saved output file | d542d945f2b5dc15c5254d... |
   | `total_lines`** | Line count | 979 |
   | `total_words`** | Word count | 4871 |
   | `code_blocks`** | Fenced code block count | 24 |
   | `table_rows`** | Table row count | 87 |
   | `headers`** | Header count | 63 |

   >_*`@Web` is a Cursor UI composer feature, but the underlying mechanisms is `WebFetch` or `mcp_web_fetch` -
   > more information in the [Friction Note](friction-note.md#web-evolution-from-manual-context-to-automatic-agent-capability)_;<br>
   >**_Optional field, measurement for raw track results only_

   ---

   **Key Hypotheses**:

   - `H1`: Character-based truncation at fixed limit, _~10-100KB?_
   - `H2`: Token-based truncation, _~2000 tokens?_
   - `H3`: Structure-aware truncation, respects Markdown boundaries
   - `H4`: MCP servers override native `@Web` limits*
   - `H5`: Agent auto-chunks after truncation, requests next chunk automatically

   >*_`@Web` may route to `mcp_web_fetch` internally; mechanism is agent's choice and
   >not user-controllable; H4 not testable through `@Web` alone, visit the
   >[Friction Note](friction-note.md#web-is-a-context-mention-not-a-tool)_

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
   --notes "Full content returned, no truncation observed..."
   ```

   ```bash
   # Verify key metrics before logging raw track runs
   python web_fetch_verify_raw_results.py BL-1

   # Log raw track result
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
   --file-size-bytes 4817 \
   --md5-checksum "d6ad8451d3778bf3544574431203a3a7" \
   --total-lines 143 \
   --total-words 564 \
   --code-blocks 2 \
   --table-rows 57 \
   --headers 4 \
   --notes "@Web returns converted..."
   ```

   >_Ensure to provide all required flags: `--method`, `--model`, `--cursor-version`,
   ><br>`--output-chars`, `--truncated`, `--tokens`, `--hypothesis`_

---

## Baseline Testing Path - Single-Run Reproducible Strategy

1. `BL-1`, `BL-2`: baseline, quick wins establish basic truncation threshold
2. `SC-2`: code blocks, tests HTML-to-Markdown conversion
3. `OP-3`: `@Web` vs MCP, _do MCP servers have different limits?_*
4. `OP-4`: auto-chunking, determines DX and key ecosystem testing gap
5. `BL-3`: hard ceiling to identify absolute limit
6. `SC-1, SC-3, SC-4`: structured content to test structure-aware truncation hypothesis
7. `EC-1, EC-3, EC-6`: edge cases to identify failure modes and unusual inputs

>*_**OP-3** not executable as designed; `@Web` may route to `mcp_web_fetch` 
>internally; the two "sides" of the comparison aren't separable through `@Web` alone;
>see [Friction Note](friction-note.md#web-is-a-context-mention-not-a-tool)_

---

## Extended Testing, _Optional_

- **Run raw track** on key tests `BL-1`, `SC-2`, `OP-4` for exact measurements
- **Rerun interpreted** on 2-3 tests to measure variance across runs

---

## Analyzing Results

Examine truncation threshold analysis, method comparison, interpretive vs raw
track comparisons, hypothesis matching -

```bash
# Generate full analysis report
python web_fetch_results_analyzer.py --csv results.csv --full

# Generate summary
python web_fetch_results_analyzer.py --csv results.csv --summary

# Analyze specific methods
python web_fetch_results_analyzer.py --csv results.csv --method "@Web"
```

>_**Remember** to always provide the full relative path to the CSV file when running the analyzer,
> including the subdirectory: `results/cursor-interpreted/results.csv` or `results/raw/results.csv`_
