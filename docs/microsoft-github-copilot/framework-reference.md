---
layout: default
title: "Framework Reference"
permalink: /docs/microsoft-github-copilot/framework-reference
parent: Microsoft GitHub Copilot
---

## Copilot Framework Reference

>_This framework generates standardized test prompts and logs CSV results,
>enabling consistent testing across cases, measurement tracking over time,
>truncation pattern identification, and web content retrieval method comparisons_<br>
>_**Requirements**: Python 3.8+, [VS Code GitHub Copilot Extension](https://code.visualstudio.com/docs/copilot/overview)_

---

## Topic Guide

- [Installation](#installation)
- [Workflow](#workflow)
- [Baseline Testing Path](#baseline-testing-path)
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

# Navigate to the Copilot testing directory
cd copilot-web-content-retrieval
```

>_For whatever reason, such as incompatible Python versions or some accidental corruption,
>use `rm -rf venv` to remove the `venv` and start over_

## Workflow

1. **List Available Tests**

   ```bash
   python web_content_retrieval_testing_framework.py --list-tests
   ```  

2. **Generate Test Prompt for a Single Test**

   Print a formatted test harness with a structured prompt to copy
   into the Copilot chat window, fields requiring values, and
   expected size reference:

   ```bash
   # Copilot-interpreted track - ask model to report measurements
   python web_content_retrieval_testing_framework.py --test BL-1 --track interpreted

   # Raw track - request verbatim output
   python web_content_retrieval_testing_framework.py --test BL-1 --track raw
   ```

3. **Copy Prompt → Run in Copilot**

   - Review the Terminal output &rarr; copy the prompt
   - Open Copilot chat window &rarr; paste the prompt
   - Review Copilot's web content retrieval behavior &rarr; examine the response

4. **Log Results**

   Depending on the track, results stored in
   `copilot-web-content-retrieval/results/{track}/results.csv` with the following fields:

   | **Column** | **Description** | **Example** |
   | --- | --- | --- |
   | `test_id` | Test identifier | `BL-1`, `SC-2`, `EC-1` |
   | `timestamp` | ISO 8601 format | `2026-03-16T17:05:02.998376` |
   | `date` | Date tested | `2026-03-16` |
   | `url` | Full URL tested | `https://www.mongodb.com/docs...` |
   | `method` | Retrieval method | `vscode-chat`* |
   | `model_selector` | UI model selector setting | `Auto` |
   | `model_observed` | Backend model invoked by Auto | `Claude Haiku 4.5`, `GPT-5.3-Codex` |
   | `input_est_chars` | Expected input size in characters | `87040` |
   | `hypothesis_match` | Hypothesis success/failure | `H1-no`, `H2-yes`, `H3-partial` |
   | `copilot_version` | Copilot extension version | `0.40.1`, `0.41.1-pro` |
   | `notes` | Observations, findings | `Pro-plan retry: successfully...` |
   | `output_chars` | Interpreted track: Copilot-measured output length | `27890` |
   | `truncated` | Interpreted track: truncation detected | `yes`/`no` |
   | `truncation_char_num` | Interpreted track: character position if truncated | `5857` |
   | `tokens_est` | Interpreted track: estimated token count | `16890` |
   | `tools_used`** | Raw track: requested tool chain | `fetch_webpage -> pylanceRunCodeSnippet` |
   | `tools_blocked`** | Raw track: tools requested but blocked or skipped | `curl (default), terminal execution` |
   | `execution_attempts`** | Raw track: total tool calls including fallbacks | `3` |
   | `copilot_reported_output_chars`** | Raw track: Copilot-measured output character count | `9876` |
   | `copilot_reported_truncated`** | Raw track: Copilot-measured truncation status | `yes`/`no` |
   | `copilot_reported_truncation_point`** | Raw track: Copilot-measured truncation position | `9876` |
   | `copilot_reported_tokens_est`** | Raw track: Copilot-estimated token count | `2469` |
   | `copilot_reported_file_size_bytes`** | Raw track: Copilot-measured file size in bytes | `4817` |
   | `copilot_reported_md5_checksum`** | Raw track: Copilot-measured MD5 checksum | `abc123...` |
   | `copilot_reported_lines`** | Raw track: Copilot-measured line count | `143` |
   | `copilot_reported_words`** | Raw track: Copilot-measured word count | `564` |
   | `copilot_reported_code_blocks`** | Raw track: Copilot-measured code block count | `2` |
   | `copilot_reported_table_rows`** | Raw track: Copilot-measured table row count | `57` |
   | `copilot_reported_headers`** | Raw track: Copilot-measured header count | `4` |
   | `verified_file_size_bytes`** | Raw track: Verifier-measured file size in bytes | `4817` |
   | `verified_md5_checksum`** | Raw track: Verifier-measured MD5 checksum | `d6ad8451d3778bf3544574...` |
   | `verified_total_lines`** | Raw track: Verifier-measured line count | `143` |
   | `verified_total_words`** | Raw track: Verifier-measured word count | `564` |
   | `verified_tokens`** | Raw track: Verifier-measured token count | `197` |
   | `verified_chars_per_token`** | Raw track: Verifier-measured chars/token ratio | `4.43` |
   | `verified_code_blocks`** | Raw track: Verifier-measured code block count | `2` |
   | `verified_table_rows`** | Raw track: Verifier-measured table row count | `57` |
   | `verified_headers`** | Raw track: Verifier-measured header count | `4` |

   > _\*`vscode-chat` describes an intentionally manual testing process in which the
   > user copy-pastes prompts into the Copilot chat window; Copilot has no documented
   > backend web content retrieval mechanism; analysis in the
   >[Friction Note](friction-note.md#fetch_webpage-undocumented)_

   > _\*\*Optional field, raw track only. `copilot_reported` fields capture values
   > measured by Copilot and may reflect execution tool output or payload estimates;
   > `verify_raw_results` script calculates `verified` fields against saved output files._

   ---

   **Key Hypotheses**:

   - `H1`: Character-based truncation at fixed limit, _~10-100KB?_
   - `H2`: Token-based truncation, _~2000 tokens?_
   - `H3`: Structure-aware truncation, respects Markdown boundaries
   - `H4`: MCP servers override native `vscode-chat` limits*
   - `H5`: Agent auto-chunks after truncation, requests next chunk automatically

   >*_`H4` not testable through `vscode-chat` alone; analysis in the [Friction Note](friction-note.md)_

   ```bash
   # Log interpreted track result
   python web_content_retrieval_testing_framework.py --log BL-1 \
   --track interpreted \
   --method vscode-chat \
   --model_selector Auto \
   --model_observed "Raptor mini (Preview)"* \
   --copilot_version 0.40.1 \
   --output_chars 48500 \
   --truncated no \
   --tokens 12000 \
   --hypothesis "H1-no" \
   --notes "Full content returned, no truncation observed..."
   ```

   >*_Quotations are only required when the value contains spaces or special
   >characters that the shell would otherwise split or misinterpret_

   ```bash
   # Verify key metrics before logging raw track runs
   python web_content_retrieval_verify_raw_results.py BL-1

   # Log raw track result
   python web_content_retrieval_testing_framework.py --log BL-1 \
   --track raw \
   --method vscode-chat \
   --model_selector Auto \
   --model_observed "Raptor mini (Preview)" \
   --copilot_version 0.41.1 \
   --copilot_reported_output_chars 9876 \
   --copilot_reported_truncated yes \
   --copilot_reported_truncation_point 9876 \
   --copilot_reported_tokens_est 2469 \
   --copilot_reported_file_size_bytes 4817 \
   --copilot_reported_md5_checksum abc123 \
   --copilot_reported_lines 143 \
   --copilot_reported_words 564 \
   --copilot_reported_code_blocks 2 \
   --copilot_reported_table_rows 57 \
   --copilot_reported_headers 4 \
   --tools_used "fetch_webpage -> pylanceRunCodeSnippet" \
   --tools_blocked "terminal execution" \
   --execution_attempts 2 \
   --verified_file_size_bytes 4817 \
   --verified_md5_checksum d6ad8451d3778bf3544574431203a3a7 \
   --verified_total_lines 143 \
   --verified_total_words 564 \
   --verified_tokens 197 \
   --verified_chars_per_token 4.43 \
   --verified_code_blocks 2 \
   --verified_table_rows 57 \
   --verified_headers 4 \
   --hypothesis "H1-yes" \
   --notes "vscode-chat returns converted..."
   ```

   >_Ensure to provide all required flags: `--method`, `--model`, `--copilot-version`,
   ><br>`--output-chars`, `--truncated`, `--tokens`, `--hypothesis`_
   ><br>
   >_Raw track only: consider renaming raw output text files to capture variance;
   >upon consistent results, remove files from the project to prevent test contamination between runs_

---

## Baseline Testing Path

Complete the interpreted track first to establish behavioral observations, then run
the raw track for exact measurements. Run each test ID a minimum of 5 times to capture
variance. `Auto` routing selects different models across runs, and output size can vary
2–6x on identical prompts. Run both tracks for each test ID:

1. `BL-1`, `BL-2` - baseline truncation threshold on small pages
2. `SC-2` - code blocks, HTML-to-Markdown conversion behavior
3. `OP-4` - auto-chunking hypothesis; establishes key ecosystem testing gap
4. `BL-3` - hard ceiling; identify absolute output limit across model families
5. `SC-1`, `SC-3`, `SC-4` - structured content; structure-aware truncation hypothesis
6. `EC-1`, `EC-3`, `EC-6` - edge cases; failure modes and unusual inputs

While the interpreted track captures Copilot's self-report and perceived completeness,
the raw track provides ground truth measurements for validation. Cross-referencing
reveals where Copilot's self-assessment diverges from reality. Comprehensive
truncation pattern analysis requires both datasets.

---

## Analyzing Results

Examine truncation threshold analysis, method comparison, interpretive vs raw
track comparisons, hypothesis matching -

```bash
# Generate full analysis report
python web_content_retrieval_results_analyzer.py --csv results.csv --full

# Generate summary
python web_content_retrieval_results_analyzer.py --csv results.csv --summary

# Analyze specific methods
python web_content_retrieval_results_analyzer.py --csv results.csv --method "vscode-chat"
```

>_Provide the full relative path to the CSV file when running the analyzer,
> including the subdirectory: `results/copilot-interpreted/results.csv` or `results/raw/results.csv`_
