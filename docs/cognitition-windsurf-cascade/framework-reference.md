---
layout: default
title: "Framework Reference"
permalink: /docs/cognition-windsurf-cascade/framework-reference
parent: Cognition Windsurf Cascade
---

## Cascade Framework Reference

>_This framework generates standardized test prompts and logs CSV results,
>enabling consistent testing across cases, measurement tracking over time,
>truncation pattern identification, and web search behavior comparisons
>across three tracks: interpreted, explicit, and raw_<br>
>_**Requirements**: Python 3.8+, [Windsurf IDE](https://windsurf.com/)_

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

# Navigate to the Cascade testing directory
cd windsurf-cascade-web-search
```

>_For whatever reason, such as incompatible Python versions or some accidental corruption,
>use `rm -rf venv` to remove the `venv` and start over_

## Workflow

1. **List Available Tests**

   ```bash
   python web_search_testing_framework.py --list-tests
   ```

2. **Generate Test Prompt for a Single Test**

   Print a formatted test harness with a structured prompt to copy
   into the Cascade chat window, fields requiring values, and
   expected size reference:

   ```bash
   # Cascade-interpreted track - ask model to report measurements; no @web
   python web_search_testing_framework.py --test BL-1 --track interpreted

   # Explicit track - identical to interpreted track, prefixed with @web
   python web_search_testing_framework.py --test BL-1 --track explicit

   # Raw track - request verbatim output, no @web
   python web_search_testing_framework.py --test BL-1 --track raw
   ```

3. **Copy Prompt → Run in Cascade**

   - Review the terminal output &rarr; copy the prompt
   - Open Cascade chat window &rarr; paste the prompt
   - Review Cascade's web search behavior &rarr; examine the response

4. **Log Results**

   Depending on the track, results stored in
   `windsurf-cascade-web-search/results/{track}/results.csv` with the following fields:

   | **Column** | **Description** | **Example** |
   | --- | --- | --- |
   | `test_id` | Test identifier | `BL-1`, `SC-2`, `EC-1` |
   | `timestamp` | ISO 8601 format | `2026-03-16T17:05:02.998376` |
   | `date` | Date tested | `2026-03-16` |
   | `url` | Full URL tested | `https://www.mongodb.com/docs...` |
   | `track` | Test track | `interpreted`, `raw`, `explicit` |
   | `method` | Retrieval method | `cascade-implicit`*, `cascade-explicit`* |
   | `model_selector` | UI model selector setting | `Hybrid Arena` |
   | `model_observed` | Model invoked during run | `SWE-1`, `Cascade Base` |
   | `approval_required` | Whether fetch approval was prompted | `yes`/`no`/`unknown` |
   | `pagination_observed` | Whether `view_content_chunk` invoked | `yes-auto`/`yes-prompted`/`no`/`unknown` |
   | `input_est_chars` | Expected input size in characters | `87040` |
   | `hypothesis_match` | Hypothesis success/failure | `H1-no`, `H2-yes`, `H3-partial` |
   | `windsurf_version` | Windsurf/Cascade version | `1.9600.38-pro` |
   | `notes` | Observations, findings | `Approval gated; auto-paginated via DocumentId...` |
   | `output_chars` | Interpreted/explicit track: Cascade-measured output length | `27890` |
   | `truncated` | Interpreted/explicit track: truncation detected | `yes`/`no` |
   | `truncation_char_num` | Interpreted/explicit track: character position if truncated | `5857` |
   | `tokens_est` | Interpreted/explicit track: estimated token count | `16890` |
   | `tools_used`** | Raw track: observed tool chain | `read_url_content -> view_content_chunk` |
   | `tools_blocked`** | Raw track: tools requested but blocked or skipped | `search_web` |
   | `execution_attempts`** | Raw track: total tool calls including fallbacks | `3` |
   | `cascade_reported_output_chars`** | Raw track: Cascade-measured output character count | `9876` |
   | `cascade_reported_truncated`** | Raw track: Cascade-measured truncation status | `yes`/`no` |
   | `cascade_reported_truncation_point`** | Raw track: Cascade-measured truncation position | `9876` |
   | `cascade_reported_tokens_est`** | Raw track: Cascade-estimated token count | `2469` |
   | `cascade_reported_file_size_bytes`** | Raw track: Cascade-measured file size in bytes | `4817` |
   | `cascade_reported_md5_checksum`** | Raw track: Cascade-measured MD5 checksum | `abc123...` |
   | `cascade_reported_lines`** | Raw track: Cascade-measured line count | `143` |
   | `cascade_reported_words`** | Raw track: Cascade-measured word count | `564` |
   | `cascade_reported_code_blocks`** | Raw track: Cascade-measured code block count | `2` |
   | `cascade_reported_table_rows`** | Raw track: Cascade-measured table row count | `57` |
   | `cascade_reported_headers`** | Raw track: Cascade-measured header count | `4` |
   | `verified_file_size_bytes`** | Raw track: Verifier-measured file size in bytes | `4817` |
   | `verified_md5_checksum`** | Raw track: Verifier-measured MD5 checksum | `d6ad8451d3778bf3544574...` |
   | `verified_total_lines`** | Raw track: Verifier-measured line count | `143` |
   | `verified_total_words`** | Raw track: Verifier-measured word count | `564` |
   | `verified_tokens`** | Raw track: Verifier-measured token count | `197` |
   | `verified_chars_per_token`** | Raw track: Verifier-measured chars/token ratio | `4.43` |
   | `verified_code_blocks`** | Raw track: Verifier-measured code block count | `2` |
   | `verified_table_rows`** | Raw track: Verifier-measured table row count | `57` |
   | `verified_headers`** | Raw track: Verifier-measured header count | `4` |

   > _\*`cascade-implicit` is used for interpreted and raw tracks, no `@web`;
   > `cascade-explicit` is used for the explicit track, `@web` prefixed.
   > `read_url_content` may require approval fetch executed_

   > _\*\*Optional field, raw track only. `cascade_reported` fields capture Cascade-measured values, may
   > reflect tool output or payload estimates; `verify_raw_results.py` calculates values against
   > `raw_output_{test_id}.txt` files._

   ---

   **Key Hypotheses**:

   - `H1`: Character-based truncation at fixed limit, _~10-100KB?_
   - `H2`: Token-based truncation, _~2000 tokens?_
   - `H3`: Structure-aware truncation, respects Markdown boundaries
   - `H4`: `@web` directive changes retrieval ceiling, tool chain, or chunking behavior*
   - `H5`: `view_content_chunk` auto-paginates via `DocumentId` without explicit prompting**

   >*_`H4` is explicit track's central question; tests whether `@web` is redundant as Cursor's `@Web`_

   >**_`H5` tests whether Cascade autonomously chunks large docs or only paginates
   >when explicitly prompted; observable via `pagination_observed` field and `OP-1`, `OP-4` tests_

   ```bash
   # Log interpreted track result
   python web_search_testing_framework.py --log BL-1 \
   --track interpreted \
   --method cascade-implicit \
   --model_selector "Hybrid Arena" \
   --model_observed "SWE-1" \
   --windsurf_version "1.9600.38-pro" \
   --approval_required yes \
   --pagination_observed no \
   --output_chars 48500 \
   --truncated no \
   --tokens 12000 \
   --hypothesis "H1-no" \
   --notes "Full content returned via read_url_content, no truncation observed..."
   ```

   >*_Quotations are only required when the value contains spaces or special
   >characters that the shell would otherwise split or misinterpret_

   ```bash
   # Log explicit track result
   python web_search_testing_framework.py --log BL-1 \
   --track explicit \
   --method cascade-explicit \
   --model_selector "Hybrid Arena" \
   --model_observed "SWE-1" \
   --windsurf_version "1.9600.38-pro" \
   --approval_required yes \
   --pagination_observed no \
   --output_chars 51000 \
   --truncated no \
   --tokens 12750 \
   --hypothesis "H4-no" \
   --notes "@web prefix did not change output size materially..."
   ```

   ```bash
   # Verify key metrics before logging raw track runs
   python web_search_verify_raw_results.py BL-1

   # Log raw track result
   python web_search_testing_framework.py --log BL-1 \
   --track raw \
   --method cascade-implicit \
   --model_selector "Hybrid Arena" \
   --model_observed "SWE-1" \
   --windsurf_version "1.9600.38-pro" \
   --approval_required yes \
   --pagination_observed yes-auto \
   --cascade_reported_output_chars 9876 \
   --cascade_reported_truncated yes \
   --cascade_reported_truncation_point 9876 \
   --cascade_reported_tokens_est 2469 \
   --cascade_reported_file_size_bytes 4817 \
   --cascade_reported_md5_checksum abc123 \
   --cascade_reported_lines 143 \
   --cascade_reported_words 564 \
   --cascade_reported_code_blocks 2 \
   --cascade_reported_table_rows 57 \
   --cascade_reported_headers 4 \
   --tools_used "read_url_content -> view_content_chunk" \
   --tools_blocked "terminal execution x2" \
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
   --notes "read_url_content returned excerpted content; view_content_chunk auto-invoked..."
   ```

   >_Ensure to provide all required flags: `--method`, `--model_selector`, `--model_observed`,
   >`--windsurf_version`, `--approval_required`, `--hypothesis`_<br>
   ><br>
   >_**Raw track only**: output content saved as `raw_output_{test_id}.txt`; consider renaming files
   > to capture variance; upon consistent results, remove files from the project to prevent test
   >contamination between runs_

---

## Baseline Testing Path

1. Run **interpreted** track to identify baseline behavioral patterns
2. Run **explicit** track to isolate `@web` directive effect against **interpreted** baseline
3. Run **raw** track for ground truth measurements and verfication of previous tracks
4. Run test a minimum of **5 times** to capture variance

| **Test IDs** | **Purpose** | **Key Question** |
| --- | --- | --- |
| `BL-1`<br>`BL-2` | Baseline truncation threshold on small pages | _What is the interpreted vs explicit delta?_ |
| `SC-2` | Code blocks,<br>HTML-to-Markdown conversion | _How does `read_url_content` handle<br>code structure?_ |
| `OP-4` | Auto-pagination<br>hypothesis | _Does `view_content_chunk` invoke<br>automatically via `DocumentId`?_ |
| `BL-3` | Hard ceiling | _What is the absolute output limit<br>across `read_url_content` runs?_ |
| `SC-1`<br>`SC-3`<br>`SC-4` | Structured content | _Does truncation respect<br>Markdown boundaries?_ |
| `EC-1`<br>`EC-3`<br>`EC-6` | Edge cases | _What are the failure modes and<br>approval-gating edge behaviors?_ |

## Analyzing Results

Examine truncation threshold analysis, implicit vs explicit `@web` effect, three-track
comparison, approval-gating behavior, auto-pagination behavior, and hypothesis matching —

```bash
# Single track — full analysis or summary
python web_search_results_analyzer.py --csv results/cascade-interpreted/results.csv --full
python web_search_results_analyzer.py --csv results/cascade-interpreted/results.csv --summary
python web_search_results_analyzer.py --csv results/raw/results.csv --full
python web_search_results_analyzer.py --csv results/explicit/results.csv --summary

# Filter by method
python cascade_web_search_results_analyzer.py \
   --csv results/cascade-interpreted/results.csv --method "cascade-explicit"

# Compare implicit and explicit tracks to observe @web effect
python web_search_results_analyzer.py \
   --csv results/cascade-interpreted/results.csv results/explicit/results.csv --full

# Compare all three tracks
python web_search_results_analyzer.py \
   --csv results/cascade-interpreted/results.csv \
         results/raw/results.csv \
         results/explicit/results.csv --full
```

>_Provide the full relative path to the CSV file when running the analyzer,
>including the subdirectory: `results/cascade-interpreted/results.csv`,
>`results/raw/results.csv`, or `results/explicit/results.csv`_