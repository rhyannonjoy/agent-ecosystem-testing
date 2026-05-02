---
layout: default
title: "Framework Reference"
permalink: /docs/microsoft-github-copilot/framework-reference
parent: Microsoft GitHub Copilot
---

# Copilot Framework Reference

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

>_For whatever reason, such as incompatible Python versions or some accidental corruption,
><br>use `rm -rf venv` to remove the `venv` and start over_

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

   - Review the terminal output &rarr; copy the prompt
   - Open Copilot chat window &rarr; paste the prompt
   - Inspect Copilot's web content retrieval behavior &rarr; examine the agent's output

4. **Assess Hypotheses**

   Before logging test results, assess the run against each hypothesis based on the model’s
   self-reported metrics and tool visibility output:

   | **ID** | **Description** | **Question** |
   | --- | --- | --- |
   | `H1` | Character-based truncation<br>at fixed limit | _Is there a ceiling at ~10–100 KB?_ |
   | `H2` | Token-based truncation | _Is there a ceiling at ~2,000 tokens?_ |
   | `H3` | Structure-aware truncation | _Does truncation fall on Markdown boundaries<br>rather than arbitrary byte positions?_ |
   | `H4`* | MCP servers impact* | _Do MCP servers override native `vscode-chat` limits?_ |
   | `H5` | Agentic auto-chunking | _Does the agent fetch chunks automatically,<br>or only when reasoned into it?_ |

   >*_`H4` not testable through `vscode-chat` alone; analysis in the [Friction Note](friction-note.md)_

5. **Log Results**

   Depending on the track, store results in
   `copilot-web-content-retrieval/results/{track}/results.csv` with the following fields:

   | **Column** | **Description** | **Example** |
   | --- | --- | --- |
   | `test_id` | Test identifier | `BL-1`, `SC-2`, `EC-1` |
   | `timestamp` | `ISO 8601` format | `2026-03-16T17:05:02.998376` |
   | `date` | Date tested | `2026-03-16` |
   | `url` | Full URL tested | `https://www.mongodb.com/docs...` |
   | `method` | Retrieval method | `vscode-chat`* |
   | `model_selector` | Model selector setting | `Auto` |
   | `model_observed` | Model invoked by `Auto` | `Claude Haiku 4.5`,<br>`GPT-5.3-Codex` |
   | `input_est_chars` | Expected input size in characters | `87040` |
   | `hypothesis_match` | Hypothesis success/failure | `H1-no`, `H2-yes`,<br>`H3-partial` |
   | `copilot_version` | Copilot extension version | `0.40.1`, `0.41.1-pro` |
   | `notes` | Observations | `Pro-plan retry: successfully...` |
   | `output_chars` | Interpreted: Copilot-measured output length | `27890` |
   | `truncated` | Interpreted: truncation detected | `yes`/`no` |
   | `truncation_char_num` | Interpreted: character position if truncated | `5857` |
   | `tokens_est` | Interpreted: estimated token count | `16890` |
   | `tools_used`** | Raw: requested tool chain | `fetch_webpage -> pylanceRunCodeSnippet` |
   | `tools_blocked`** | Raw: tools requested but blocked/skipped | `curl`, terminal execution |
   | `execution_attempts`** | Raw: total tool calls including fallbacks | `3` |
   | `copilot_reported_output_chars`** | Raw: Copilot-measured output character count | `9876` |
   | `copilot_reported_truncated`** | Raw: Copilot-measured truncation status | `yes`/`no` |
   | `copilot_reported_truncation_point`** | Raw: Copilot-measured truncation position | `9876` |
   | `copilot_reported_tokens_est`** | Raw: Copilot-estimated token count | `2469` |
   | `copilot_reported_file_size_bytes`** | Raw: Copilot-measured file size in bytes | `4817` |
   | `copilot_reported_md5_checksum`** | Raw: Copilot-measured MD5 checksum | `abc123...` |
   | `copilot_reported_lines`** | Raw: Copilot-measured line count | `143` |
   | `copilot_reported_words`** | Raw: Copilot-measured word count | `564` |
   | `copilot_reported_code_blocks`** | Raw: Copilot-measured code block count | `2` |
   | `copilot_reported_table_rows`** | Raw: Copilot-measured table row count | `57` |
   | `copilot_reported_headers`** | Raw: Copilot-measured header count | `4` |
   | `verified_file_size_bytes`** | Raw: Verifier-measured file size in bytes | `4817` |
   | `verified_md5_checksum`** | Raw: Verifier-measured MD5 checksum | `d6ad8451d3778bf3544574...` |
   | `verified_total_lines`** | Raw: Verifier-measured line count | `143` |
   | `verified_total_words`** | Raw: Verifier-measured word count | `564` |
   | `verified_tokens`** | Raw: Verifier-measured token count | `197` |
   | `verified_chars_per_token`** | Raw: Verifier-measured chars/token ratio | `4.43` |
   | `verified_code_blocks`** | Raw: Verifier-measured code block count | `2` |
   | `verified_table_rows`** | Raw track: Verifier-measured table row count | `57` |
   | `verified_headers`** | Raw track: Verifier-measured header count | `4` |

   > _\*`vscode-chat` describes an intentionally manual process: user copy-pastes prompts into the
   > Copilot chat window; Copilot has no documented backend web content retrieval mechanism; analysis in the
   > [Friction Note](friction-note.md#fetch_webpage-undocumented)_

   > _\*\*Optional field, raw track only. `copilot_reported` fields may reflect execution tool output or payload estimates;
   > `web_content_retrieval_verify_raw_results.py` script calculates values against saved `raw_output_{test_id}.txt` files._

   ```bash
   # Log interpreted track result
   python web_content_retrieval_testing_framework.py --log BL-1 \
   --track interpreted \
   --method vscode-chat \
   --model_selector Auto \
   --model_observed "Raptor mini (Preview)"* \
   --copilot_version "0.40.1-pro" \
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
   --copilot_version "0.40.1-pro" \
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
   ><br>`--output-chars`, `--truncated`, `--tokens`, `--hypothesis`_<br>
   ><br>
   >_**Raw track only**: rename raw output files to capture variance;
   >if results are consistent, remove files to prevent test contamination between runs_

---

## Baseline Testing Path

1. Run **interpreted** track to identify baseline behavioral patterns
2. Run **raw** track for ground truth measurements, verify **interpreted** baseline
3. Run each test ID a minimum of 5 times/track to capture variance:

| **Test IDs** | **Purpose** | **Key Question** |
| --- | --- | --- |
| `BL-1`<br>`BL-2` | Baseline truncation<br>threshold on small pages | _What is the interpreted vs raw delta?_ |
| `SC-2` | Code blocks,<br>HTML-to-Markdown conversion | _How does `fetch_webpage` handle<br>code structure?_ |
| `OP-4` | Auto-chunking<br>hypothesis | _Does Copilot chunk automatically,<br>or is this a key ecosystem gap?_ |
| `BL-3` | Hard ceiling | _What is the absolute output<br>limit across model families?_ |
| `SC-1`<br>`SC-3`<br>`SC-4` | Structured content | _Does truncation respect<br>Markdown boundaries?_ |
| `EC-1`<br>`EC-3`<br>`EC-6` | Edge cases | _What are the failure modes<br>and unusual inputs?_ |

## Analyzing Results

Examine hypotheses matching, track comparison, and truncation analysis -

```bash
# Generate full analysis report
python web_content_retrieval_results_analyzer.py --csv results.csv --full

# Generate summary
python web_content_retrieval_results_analyzer.py --csv results.csv --summary

# Analyze specific methods
python web_content_retrieval_results_analyzer.py --csv results.csv --method "vscode-chat"

# Compare interpreted and raw results
python web_content_retrieval_results_analyzer.py \
        --csv results/copilot-interpreted/results.csv results/raw/results.csv --full
```

>_Provide full relative path, including subdirectory:
>`results/copilot-interpreted/results.csv`<br>or `results/raw/results.csv`_
