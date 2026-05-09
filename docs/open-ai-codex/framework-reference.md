---
layout: default
title: "Framework Reference"
permalink: /docs/open-ai-codex/framework-reference
parent: OpenAI Codex
---

# Codex Framework Reference

>_This framework generates standardized test prompts and logs CSV results,
>enabling consistent testing across cases, measurement tracking over time,
>truncation pattern identification, and web retrieval behavior comparisons
>across four tracks: T1 (Codex IDE interpreted), T2 (VS Code-Codex interpreted),
>T3 (Codex IDE raw), and T4 (VS Code-Codex raw)_<br>
>_**Requirements**: Python 3.8+, [OpenAI Codex](https://openai.com/codex/) or
>[Codex in VS Code](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)_

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

# Navigate to the Codex testing directory
cd codex-web-search
```

>_For whatever reason, such as incompatible Python versions or some accidental corruption,
>use `rm -rf venv` to remove the `venv` and start over_

---

## Workflow

1. **List Available Tests and Tracks**

   ```bash
   python framework.py --list-tests
   python framework.py --list-tracks
   ```

2. **Generate Test Prompt for a Single Test**

   Print a formatted test harness with a structured prompt to copy
   into the Codex chat window, fields requiring values, and
   expected size reference:

   ```bash
   # T1 — GPT-interpreted, Codex IDE (no workspace)
   python framework.py --test BL-1 --track t1_codex_interpreted

   # T2 — GPT-interpreted, VS Code-Codex (workspace present)
   python framework.py --test BL-1 --track t2_vscode_interpreted

   # T3 — Raw verbatim output, Codex IDE
   python framework.py --test BL-1 --track t3_codex_raw

   # T4 — Raw verbatim output, VS Code-Codex
   python framework.py --test BL-1 --track t4_vscode_raw
   ```

3. **Copy Prompt → Run in Codex**

   - Review the terminal output &rarr; copy the prompt
   - Open the Codex IDE or VS Code-Codex chat window &rarr; paste the prompt
   - Inspect retrieval behavior &rarr; examine agent output

4. **Assess Hypotheses**

   Before logging test results, assess the run against each hypothesis based on
   the agent's self-reported metrics and tool visibility output:

   | **ID** | **Description** | **Question** |
   | --- | --- | --- |
   | `H1` | Character-based truncation<br>at fixed limit | _Is there a ceiling at ~10–100 KB?_ |
   | `H2` | Token-based truncation | _Is there a ceiling at ~2,000 tokens?_ |
   | `H3` | Structure-aware truncation | _Does truncation fall on Markdown boundaries rather than arbitrary byte positions?_ |
   | `H4` | Surface context changes retrieval ceiling, tool chain, or chunking behavior | _Does the Codex IDE vs VS Code-Codex surface produce different retrieval behavior?_ |
   | `H5` | Agent auto-chunks above the truncation ceiling | _Does the agent fetch with multi-step tool chains, or only when reasoned into it?_ |

5. **Log Results**

   Run the interactive logger and follow the prompts. Fields are grouped by track:
   session fields first, then track-specific output fields, then hypothesis and notes.
   Quotation marks are not necessary; skip optional fields with `Enter`:

   ```bash
   # Call the logger
   python log.py

   # Logger prompts and validates fields before writing
   ✓ Result logged to results/codex-{track}/results.csv
   ```

   > _Verify key metrics before logging T3 or T4 raw track runs:_
   > ```bash
   > python verify.py BL-1               # both surfaces
   > python verify.py BL-1 --surface codex
   > python verify.py BL-1 --surface vscode
   > ```

   **Framework fields logged per track**:

   | **Column** | **Description** | **Example** |
   | --- | --- | --- |
   | `test_id` | Test identifier | `BL-1`, `SC-2`, `EC-1` |
   | `timestamp` | `ISO 8601` format | `2026-03-16T17:05:02.998376` |
   | `date` | Date tested | `2026-03-16` |
   | `url` | Full URL tested | `https://www.mongodb.com/docs...` |
   | `track` | Test track | `t1_codex_interpreted`, `t3_codex_raw` |
   | `surface` | Deployment surface | `codex`, `vscode_codex` |
   | `method` | Retrieval method | `gpt-interpreted`, `raw` |
   | `workspace_present` | Workspace available to agent? | `true`/`false` |
   | `model_selector` | Model selector setting | `o4-mini`, `o3` |
   | `model_observed` | LLM reported in output | `o4-mini`, `o3` |
   | `model_intelligence_level` | Intelligence level setting | `low`, `medium`, `high`, `auto` |
   | `input_est_chars` | Expected input size in characters | `87040` |
   | `hypothesis_match` | Hypothesis success/failure | `H1-no`, `H2-yes`, `H4-untested` |
   | `codex_version` | Codex version string | `1.0.0` |
   | `notes` | Observations | `web tool invoked; no workspace substitution` |
   | `tools_named` | Tool names reported in agent output | `web`, `web.open`, `curl` |
   | `workspace_substitution` | Agent used local execution instead of web fetch? | `yes`/`no`/`unknown` |
   | `output_chars` | T1/T2: agent-measured output length | `27890` |
   | `truncated` | T1/T2: truncation detected | `yes`/`no` |
   | `truncation_char_num` | T1/T2: character position if truncated | `5857` |
   | `tokens_est` | T1/T2: estimated token count | `16890` |
   | `tools_used`* | T3/T4: observed tool chain | `web -> web.open` |
   | `tools_blocked`* | T3/T4: tools requested but blocked/skipped | `curl` |
   | `execution_attempts`* | T3/T4: total tool calls including fallbacks | `3` |
   | `agent_reported_output_chars`* | T3/T4: agent-measured output character count | `9876` |
   | `agent_reported_truncated`* | T3/T4: agent-measured truncation status | `yes`/`no` |
   | `agent_reported_truncation_point`* | T3/T4: agent-measured truncation position | `9876` |
   | `agent_reported_tokens_est`* | T3/T4: agent-estimated token count | `2469` |
   | `agent_reported_file_size_bytes`* | T3/T4: agent-measured file size in bytes | `4817` |
   | `agent_reported_md5_checksum`* | T3/T4: agent-measured MD5 checksum | `abc123...` |
   | `agent_reported_lines`* | T3/T4: agent-measured line count | `143` |
   | `agent_reported_words`* | T3/T4: agent-measured word count | `564` |
   | `agent_reported_code_blocks`* | T3/T4: agent-measured code block count | `2` |
   | `agent_reported_table_rows`* | T3/T4: agent-measured table row count | `57` |
   | `agent_reported_headers`* | T3/T4: agent-measured header count | `4` |
   | `verified_file_size_bytes`* | T3/T4: verifier-measured file size in bytes | `4817` |
   | `verified_md5_checksum`* | T3/T4: verifier-measured MD5 checksum | `d6ad8451d3778bf3544574...` |
   | `verified_total_lines`* | T3/T4: verifier-measured line count | `143` |
   | `verified_total_words`* | T3/T4: verifier-measured word count | `564` |
   | `verified_tokens`* | T3/T4: verifier-measured token count | `197` |
   | `verified_chars_per_token`* | T3/T4: verifier-measured chars/token ratio | `4.43` |
   | `verified_code_blocks`* | T3/T4: verifier-measured code block count | `2` |
   | `verified_table_rows`* | T3/T4: verifier-measured table row count | `57` |
   | `verified_headers`* | T3/T4: verifier-measured header count | `4` |

   > _*Optional field, T3/T4 raw tracks only. `agent_reported_*` fields reflect the agent's
   > own measurements from its output; `verify.py` calculates `verified_*` values against
   > `raw_output_{test_id}_codex.txt` or `raw_output_{test_id}_vscode.txt` files._

---

## Baseline Testing Path

1. Run **T1** (Codex IDE interpreted) to establish surface-isolated behavioral baseline
2. Run **T2** (VS Code-Codex interpreted) to isolate workspace effect against T1
3. Run **T3** (Codex IDE raw) for ground truth retrieval measurements, verify T1
4. Run **T4** (VS Code-Codex raw) to isolate surface effect on raw retrieval, verify T2
5. Run each test a minimum of 5 times per track to capture variance

| **Test IDs** | **Purpose** | **Key Question** |
| --- | --- | --- |
| `BL-1`<br>`BL-2` | Baseline truncation threshold<br>on small pages | _What is the T1 vs T2 surface delta?_ |
| `SC-2` | Code blocks,<br>API documentation | _How does the web toolchain handle code structure?_ |
| `OP-1` | Fragment identifier<br>navigation | _Does Codex jump to a specific section via URL fragment?_ |
| `OP-4` | Auto-chunking above<br>the BL-3 ceiling | _Does the agent fetch above the truncation ceiling with multi-step tool chains?_ |
| `BL-3` | Hard ceiling | _What is the absolute output limit across retrieval runs?_ |
| `SC-1`<br>`SC-3`<br>`SC-4` | Structured content | _Does truncation respect Markdown boundaries?_ |
| `EC-1`<br>`EC-3`<br>`EC-6` | Edge cases | _What are the failure modes and workspace substitution edge behaviors?_ |

>_Rename raw output files to capture variance across runs; if results are
>consistent, remove files to prevent test contamination between runs_

---

## Analyzing Results

Examine hypothesis matching, surface and workspace effects, perception gap, and truncation analysis:

```bash
# Single track — full analysis or summary
python analyze.py --csv results/codex-t1_codex_interpreted/results.csv --summary
python analyze.py --csv results/codex-t3_codex_raw/results.csv --full

# Filter by track
python analyze.py --csv results/codex-t1_codex_interpreted/results.csv --track t1_codex_interpreted

# Compare interpreted tracks (T1 vs T2) — isolates workspace effect
python analyze.py \
   --csv results/codex-t1_codex_interpreted/results.csv \
         results/codex-t2_vscode_interpreted/results.csv --full

# Compare raw tracks (T3 vs T4) — isolates surface effect on retrieval ceiling
python analyze.py \
   --csv results/codex-t3_codex_raw/results.csv \
         results/codex-t4_vscode_raw/results.csv --full

# Compare all four tracks
python analyze.py \
   --csv results/codex-t1_codex_interpreted/results.csv \
         results/codex-t2_vscode_interpreted/results.csv \
         results/codex-t3_codex_raw/results.csv \
         results/codex-t4_vscode_raw/results.csv --full
```

>_Provide the full relative path including subdirectory, e.g.
>`results/codex-t1_codex_interpreted/results.csv`_

---

## Generating Summary Templates

Generate pre-structured Markdown summary templates to fill in after each test series:

```bash
# Single test, single track
python template.py --test BL-1 --track t3_codex_raw

# All four tracks for a single test
python template.py --test BL-1 --all-tracks

# All tests for a single track
python template.py --track t3_codex_raw --all-tests

# All 48 combinations
python template.py --all-tests --all-tracks

# Preview without writing a file
python template.py --test BL-1 --track t3_codex_raw --preview
```

Templates are written to `summaries/{track}/{test_id}_summary.md`. Each template
pre-populates the test conditions table, run results table with track-appropriate
columns, H1–H5 hypothesis sections with verdict placeholders, an emergent findings
scaffold, and a log label summary table. Verdict reasoning, emergent findings prose,
and log labels are left as `<!-- TODO -->` placeholders for human completion.

>_Use `--overwrite` to regenerate a template after changes to `TEST_URLS` or `TRACKS`
>in `framework.py`_
