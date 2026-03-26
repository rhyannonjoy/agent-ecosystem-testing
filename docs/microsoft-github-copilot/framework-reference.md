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
   python web_content_retrieval_testing_framework.py --test BL-2 --track raw
   ```

3. **Copy Prompt → Run in Copilot**

   - Review the Terminal output &rarr; copy the prompt
   - Open Copilot chat window &rarr; paste the prompt
   - Review Copilot's web content retrieval behavior &rarr; examine the response

4. **Log Results**

   Depending on the track, results stored in
   `copilot-web-content-retrieval/results/{track}/results.csv` with the following fields:

   | Column | Description | Example |
   | --- | --- | --- |
   | `test_id` | Test identifier | BL-1, SC-2, EC-1 |
   | `timestamp` | ISO 8601 timestamp | 2026-03-16T17:05:02.998376 |
   | `date` | Date tested | 2026-03-16 |
   | `url` | Full URL tested | https://www.mongodb.com/docs...|
   | `method` | Retrieval method | `vscode-chat`* |
   | `model` | Model used | `Auto` - Copilot's agent router |
   | `input_est_chars` | Expected input size | 87040 |
   | `output_chars` | Actual output length, chars via `wc -m` | 27890 |
   | `truncated` | Truncation detected | yes/no |
   | `truncation_char_num` | Character position if truncated | 5857 |
   | `tokens` | Token count via `tiktoken` | 16890 |
   | `hypothesis_match` | Hypothesis matched | H1-no, H2-yes, H3-yes |
   | `notes` | Observations and findings | Pro-plan retry: successfully... |
   | `track` | Test track | interpreted/raw |
   | `copilot_version` | Copilot chat version | 0.40.1, 0.40.1-pro |
   | `file_size_bytes`** | Exact file size via `ls -l` | 28158 |
   | `md5_checksum`** | MD5 of saved output file | d542d945f2b5dc15c5254d... |
   | `total_lines`** | Line count | 979 |
   | `total_words`** | Word count | 4871 |
   | `code_blocks`** | Fenced code block count | 24 |
   | `table_rows`** | Table row count | 87 |
   | `headers`** | Header count | 63 |

   >_*`vscode-chat` describes an intentionally manual testing process in which the
   >user copy-pastes prompts into the Copilot chat window, as Copilot has no documented
   >backend web content retrieval mechanism - more information in the [Friction Note](friction-note.md)_;
   >**_Optional field, measurement for raw track results only_

   ---

   **Key Hypotheses**:

   - `H1`: Character-based truncation at fixed limit, _~10-100KB?_
   - `H2`: Token-based truncation, _~2000 tokens?_
   - `H3`: Structure-aware truncation, respects Markdown boundaries
   - `H4`: MCP servers override native `vscode-chat` limits*
   - `H5`: Agent auto-chunks after truncation, requests next chunk automatically

   >*_`vscode-chat` may route to different internally; mechanism is agent's choice and
   >not user-controllable; H4 not testable through `vscode-chat` alone, visit the
   >[Friction Note](friction-note.md)_

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

   >*_Quotations are only strictly required when the value contains spaces or special
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
   --copilot_version 0.40.1 \
   --output_chars 9876 \
   --truncated yes \
   --truncation_point 9876 \
   --tokens 2469 \
   --hypothesis "H1-yes" \
   --file_size_bytes 4817 \
   --md5_checksum "d6ad8451d3778bf3544574431203a3a7" \
   --total_lines 143 \
   --total_words 564 \
   --code_blocks 2 \
   --table_rows 57 \
   --headers 4 \
   --notes "vscode-chat returns converted..."
   ```

   >_Ensure to provide all required flags: `--method`, `--model`, `--copilot-version`,
   ><br>`--output-chars`, `--truncated`, `--tokens`, `--hypothesis`_

---

## Baseline Testing Path, Single-Run Reproducible Strategy

1. `BL-1`, `BL-2`: baseline, quick wins establish basic truncation threshold
2. `SC-2`: code blocks, tests HTML-to-Markdown conversion
3. `OP-4`: auto-chunking, determines DX and key ecosystem testing gap
4. `BL-3`: hard ceiling to identify absolute limit
5. `SC-1, SC-3, SC-4`: structured content to test structure-aware truncation hypothesis
6. `EC-1, EC-3, EC-6`: edge cases to identify failure modes and unusual inputs

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
python web_content_retrieval_results_analyzer.py --csv results.csv --full

# Generate summary
python web_content_retrieval_results_analyzer.py --csv results.csv --summary

# Analyze specific methods
python web_content_retrieval_results_analyzer.py --csv results.csv --method "vscode-chat"
```

>_**Remember** to always provide the full relative path to the CSV file when running the analyzer,
> including the subdirectory: `results/copilot-interpreted/results.csv` or `results/raw/results.csv`_
