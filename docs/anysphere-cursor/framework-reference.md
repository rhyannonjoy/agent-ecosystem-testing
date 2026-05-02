---
layout: default
title: "Framework Reference"
permalink: /docs/anysphere-cursor/framework-reference
parent: Anysphere Cursor
---

# Cursor Framework Reference

>_This framework generates standardized test prompts and logs CSV results,
>enabling consistent testing across cases, measurement tracking over time,
>truncation pattern identification, and fetch method comparisons_<br>
>_**Requirements**: Python 3.8+, [Cursor IDE](https://cursor.com/download)_

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
><br>use `rm -rf venv` to remove the `venv` and start over_

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
   - Inspect Cursor's fetch behavior &rarr; examine the agent output

4. **Assess Hypotheses**

   Before logging test results, assess the run against each hypothesis based on the model’s
   self-reported metrics and tool visibility output:

   | **ID** | **Description** | **Question** |
   | --- | --- | --- |
   | `H1` | Character-based truncation<br>at fixed limit | _Is there a ceiling at ~10–100 KB?_ |
   | `H2` | Token-based truncation | _Is there a ceiling at ~2,000 tokens?_ |
   | `H3` | Structure-aware truncation | _Does truncation fall on Markdown boundaries<br>rather than arbitrary byte positions?_ |
   | `H4`* | `@Web` invocation | _Does `@Web` impact web fetch behavior?_ |
   | `H5` | Agentic auto-chunking | _Does the agent fetch chunks automatically,<br>or only when reasoned into it?_ |

   >*_`@Web` may route to `mcp_web_fetch`; mechanism is agent's choice,
   >not user-controllable; `H4` not testable through `@Web` alone, visit
   >[Friction Note](friction-note.md#web-is-a-context-mention-not-a-tool) for analysis._

5. **Log Results**

   Store results in `cursor-web-fetch/results/{track}/results.csv` with the following fields:

   | Column | Description | Example |
   | --- | --- | --- |
   | `test_id` | Test identifier | `BL-1`, `SC-2`, `EC-1` |
   | `timestamp` | `ISO 8601` timestamp | `2026-03-16T17:05:02.998376` |
   | `date` | Date tested | `2026-03-16` |
   | `url` | Full URL tested | `https://www.mongodb.com/docs...` |
   | `method` | Fetch method | `@Web`* |
   | `model`*** | Model used | `Auto` - Cursor's agent router |
   | `input_est_chars` | Expected input size | `87040` |
   | `output_chars` | Character count via `wc -m` | `27890` |
   | `truncated` | Truncation detected | `yes`/`no` |
   | `truncation_char_num` | Character position if truncated | `5857` |
   | `tokens_est` | Token estimation or<br>count via `tiktoken` | `16890` |
   | `hypothesis_match` | Hypothesis matched | `H1-no`, `H2-yes`, `H3-yes` |
   | `notes` | Observations and findings | `Pro-plan retry: successfully...` |
   | `track` | Test track | `interpreted`/`raw` |
   | `cursor_version` | Cursor IDE version | `2.6.19`, `2.6.19-pro` |
   | `file_size_bytes`** | File size calculation `ls -l` | `28158` |
   | `md5_checksum`** | MD5 of saved output file | `d542d945f2b5dc15c5254d...` |
   | `total_lines`** | Line count | `979` |
   | `total_words`** | Word count | `4871` |
   | `code_blocks`** | Fenced code block count | `24` |
   | `table_rows`** | Table row count | `87` |
   | `headers`** | Header count | `63` |

   >_*`@Web` is a Cursor UI composer feature, the underlying mechanisms are `WebFetch` and/or `mcp_web_fetch`,
   > more in [Friction Note](friction-note.md#web-evolution-from-manual-context-to-automatic-agent-capability)_<br>
   <br>
   >_**Optional field, measurement for raw track results only_<br>
   <br>
   >***_Cursor's `Auto` setting doesn't disclose specific model used_

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
   python web_fetch_testing_framework.py --log BL-1 \
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

   >_Provide all required flags: `--method`, `--model`, `--cursor-version`,
   >`--output-chars`, `--truncated`,<br>`--tokens`, `--hypothesis`_<br>
   <br>
   >_Rename raw output files to capture variance;
   >if results are consistent, remove files to prevent test contamination between runs_

---

## Baseline Testing Path

1. Run **interpreted** track to identify baseline behavioral patterns
2. Run **raw** track for ground truth measurements, verify **interpreted** baseline
3. Run each test ID a minimum of 5 times/track to capture variance:

| **Test IDs** | **Purpose** | **Key Question** |
| --- | --- | --- |
| `BL-1`<br>`BL-2` | Baseline truncation threshold<br>on small pages | _What is the interpreted vs raw delta?_ |
| `SC-2` | Code blocks,<br>HTML-to-Markdown conversion | _How does Cursor handle<br>code structure?_ |
| `OP-3` | `@Web` vs MCP | _Do MCP servers have different limits?_* |
| `OP-4` | Auto-pagination<br>hypothesis | _Does Cursor auto-chunk content?_ |
| `BL-3` | Hard ceiling | _What is the absolute output<br> limit across runs?_ |
| `SC-1`<br>`SC-3`<br>`SC-4` | Structured content | _Does truncation respect<br>Markdown boundaries?_ |
| `EC-1`<br>`EC-3`<br>`EC-6` | Edge cases | _What are the failure modes and<br>approval-gating edge behaviors?_ |

>*_**`OP-3`** not executable as designed; `@Web` may route to `mcp_web_fetch`;
>the two "sides" of the comparison aren't separable through `@Web` alone;
>read more in [Friction Note](friction-note.md#web-evolution-from-manual-context-to-automatic-agent-capability)._

---

## Analyzing Results

Review hypotheses matching, tracking comparisons, and truncation analysis:

```bash
# Generate full analysis report
python web_fetch_results_analyzer.py --csv results.csv --full

# Generate summary
python web_fetch_results_analyzer.py --csv results.csv --summary

# Analyze specific methods
python web_fetch_results_analyzer.py --csv results.csv --method "@Web"
```

>_Provide full relative path, including subdirectory:<br>
>`results/cursor-interpreted/results.csv` or `results/raw/results.csv`_
