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
   - Inspect Cascade's web search behavior &rarr; examine agent output

4. **Assess Hypotheses**

   Before logging test results, assess the run against each hypothesis based on
   the model's self-reported metrics and tool visibility output:

   | **ID** | **Description** | **Question** |
   | --- | --- | --- |
   | `H1` | Character-based truncation<br>at fixed limit | _Is there a ceiling at ~10–100 KB?_ |
   | `H2` | Token-based truncation | _Is there a ceiling at ~2,000 tokens?_ |
   | `H3` | Structure-aware truncation | _Does truncation fall on Markdown boundaries rather than arbitrary<br>byte positions?_ |
   | `H4` | `@web` directive changes retrieval ceiling, tool chain, or<br>chunking behavior | _Is Cascade's `@web` redundant<br>as Cursor's `@Web`?_ |
   | `H5` | `view_content_chunk` auto-paginates via `DocumentId` without explicit prompting | _Does the agent fetch with<br>auto-chunking, or only when reasoned into it?_ |

5. **Log Results**

   Run the interactive logger and follow the prompts. Fields are grouped by track: session fields first, then track-specific
   output fields, then hypothesis and notes. Quotation marks not necessary; optional fields can be skipped with `Enter` -

   ```bash
   # Call the logger
   python web_search_log_results.py

   # Logger prompts and validates fields before confirmation
   ✓ Result logged to results/{track name}/results.csv
   ```

   > _Verify key metrics before logging raw track runs: `python web_search_verify_raw_results.py {test ID}`_

   > _If a log command fails before completing, the CSV may be written without headers.
   > Run `python web_search_add_csv_headers.py --track {track name}` to recover._

   **Framework fields logged per track**:

   | **Column** | **Description** | **Example** |
   | --- | --- | --- |
   | `test_id` | Test identifier | `BL-1`, `SC-2`, `EC-1` |
   | `timestamp` | `ISO 8601` format | `2026-03-16T17:05:02.998376` |
   | `date` | Date tested | `2026-03-16` |
   | `url` | Full URL tested | `https://www.mongodb.com/docs...` |
   | `track` | Test track | `interpreted`, `raw`, `explicit` |
   | `method` | Retrieval method | `cascade-implicit`*,<br>`cascade-explicit`* |
   | `model_selector` | Model selector setting | `Hybrid Arena` |
   | `model_observed` | Model invoked | `SWE-1.5`, `Claude Sonnet 4.5` |
   | `approval_required` | Fetch approval prompted? | `yes`/`no`/`unknown` |
   | `pagination_observed` | `view_content_chunk` invoked? | `yes-auto`/`yes-prompted`/`no`/`unknown` |
   | `input_est_chars` | Expected input size in characters | `87040` |
   | `hypothesis_match` | Hypothesis success/failure | `H1-no`, `H2-yes`, `H3-partial` |
   | `windsurf_version` | Windsurf-Cascade version | `1.9600.40-pro` |
   | `notes` | Observations | `Auto-paginated...` |
   | `output_chars` | Interpreted/explicit: Cascade-measured output length | `27890` |
   | `truncated` | Interpreted/explicit: truncation detected | `yes`/`no` |
   | `truncation_char_num` | Interpreted/explicit: character position if truncated | `5857` |
   | `tokens_est` | Interpreted/explicit: estimated token count | `16890` |
   | `tools_used`** | Raw: observed<br>tool chain |`read_url_content, view_content_chunk` |
   | `tools_blocked`** | Raw: tools requested but blocked/skipped | `search_web` |
   | `execution_attempts`** | Raw: total tool calls including fallbacks | `3` |
   | `cascade_reported_output_chars`** | Raw: Cascade-measured output character count | `9876` |
   | `cascade_reported_truncated`** | Raw: Cascade-measured truncation status | `yes`/`no` |
   | `cascade_reported_truncation_point`** | Raw: Cascade-measured truncation position | `9876` |
   | `cascade_reported_tokens_est`** | Raw: Cascade-estimated token count | `2469` |
   | `cascade_reported_file_size_bytes`** | Raw: Cascade-measured file size in bytes | `4817` |
   | `cascade_reported_md5_checksum`** | Raw: Cascade-measured MD5 checksum | `abc123...` |
   | `cascade_reported_lines`** | Raw: Cascade-measured line count | `143` |
   | `cascade_reported_words`** | Raw: Cascade-measured word count | `564` |
   | `cascade_reported_code_blocks`** | Raw: Cascade-measured code block count | `2` |
   | `cascade_reported_table_rows`** | Raw: Cascade-measured table row count | `57` |
   | `cascade_reported_headers`** | Raw: Cascade-measured header count | `4` |
   | `verified_file_size_bytes`** | Raw: Verifier-measured file size in bytes | `4817` |
   | `verified_md5_checksum`** | Raw: Verifier-measured MD5 checksum | `d6ad8451d3778bf3544574...` |
   | `verified_total_lines`** | Raw: Verifier-measured line count | `143` |
   | `verified_total_words`** | Raw: Verifier-measured word count | `564` |
   | `verified_tokens`** | Raw: Verifier-measured token count | `197` |
   | `verified_chars_per_token`** | Raw: Verifier-measured chars/token ratio | `4.43` |
   | `verified_code_blocks`** | Raw: Verifier-measured code block count | `2` |
   | `verified_table_rows`** | Raw: Verifier-measured table row count | `57` |
   | `verified_headers`** | Raw: Verifier-measured header count | `4` |

   > _*`cascade-implicit` is used for interpreted and raw tracks, no `@web`;
   > `cascade-explicit` is used for the explicit track, `@web` prefixed_.

   > _**Optional field, raw track only. `cascade_reported` fields may reflect tool output or payload estimates;
   > `web_search_verify_raw_results.py` calculates values against `raw_output_{test_id}.txt` files_.

---

## Baseline Testing Path

1. Run **interpreted** track to identify baseline behavioral patterns
2. Run **explicit** track to isolate `@web` directive effect against **interpreted** baseline
3. Run **raw** track for ground truth measurements, verify previous tracks
4. Run test a minimum of 5 times/track to capture variance:

| **Test IDs** | **Purpose** | **Key Question** |
| --- | --- | --- |
| `BL-1`<br>`BL-2` | Baseline truncation threshold<br>on small pages | _What is the interpreted vs explicit delta?_ |
| `SC-2` | Code blocks,<br>HTML-to-Markdown conversion | _How does `read_url_content`<br> handle code structure?_ |
| `OP-1` | Fragment identifier navigation | _Does Cascade jump to specific section via URL fragment?_ |
| `OP-4` | Auto-pagination<br>hypothesis | _Does `view_content_chunk` invoke<br>automatically via `DocumentId`?_ |
| `BL-3` | Hard ceiling | _What is the absolute output limit<br>across `read_url_content` runs?_ |
| `SC-1`<br>`SC-3`<br>`SC-4` | Structured content | _Does truncation respect<br>Markdown boundaries?_ |
| `EC-1`<br>`EC-3`<br>`EC-6` | Edge cases | _What are the failure modes and<br>approval-gating edge behaviors?_ |

>_**Raw track only**: rename raw output files to capture variance;
>if results are consistent, remove files to prevent test contamination between runs_

---

## Analyzing Results

Examine truncation analysis, method and track comparison, hypothesis matching:

```bash
# Single track — full analysis or summary
python web_search_results_analyzer.py --csv results/cascade-interpreted/results.csv --full
python web_search_results_analyzer.py --csv results/cascade-interpreted/results.csv --summary
python web_search_results_analyzer.py --csv results/cascade-explicit/results.csv --summary
python web_search_results_analyzer.py --csv results/raw/results.csv --full

# Filter by method
python cascade_web_search_results_analyzer.py \
   --csv results/cascade-interpreted/results.csv --method "cascade-explicit"

# Compare implicit and explicit tracks to observe @web effect
python web_search_results_analyzer.py \
   --csv results/cascade-interpreted/results.csv results/cascade-explicit/results.csv --full

# Compare all three tracks
python web_search_results_analyzer.py \
   --csv results/cascade-interpreted/results.csv \
         results/raw/results.csv \
         results/explicit/results.csv --full
```

>_Provide full relative path, including subdirectory: `results/cascade-interpreted/results.csv`,
>`results/raw/results.csv`, or `results/cascade-explicit/results.csv`_