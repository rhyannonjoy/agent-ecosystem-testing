---
layout: default
title: "Framework Reference"
permalink: /docs/open-ai-codex/framework-reference
parent: OpenAI Codex
---

# Codex Framework Reference

>_This framework generates standardized test prompts and logs CSV results, enabling consistent testing
>across cases, measurement tracking over time, truncation pattern identification, and retrieval behavior
>comparisons across tracks:<br>Codex and VS Code-Codex interpreted, Codex and VS Code-Codex raw_.
><br>
>_**Requirements**: Python 3.8+, [OpenAI Codex Desktop](https://openai.com/codex/), and
>[VS Code Codex Extension](https://marketplace.visualstudio.com/items?itemName=openai.chatgpt)_

---

## Installation

```bash
# Clone and/or navigate to agent-ecosystem-testing directory
cd agent-ecosystem-testing

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to Codex testing directory
cd open-ai-codex-web-search
```

>_In the event of incompatible Python versions or corruption, use `rm -rf venv` to remove the `venv` to start over_

---

## Baseline Testing Path

1. Run `T1` to establish surface-isolated behavioral baseline
2. Run `T2` to isolate workspace effect against `T1`
3. Run `T3` for ground truth retrieval measurements, verify `T1`
4. Run `T4` to isolate surface effect on raw retrieval, verify `T2`
5. Run each test a minimum of 5x/track to capture variance

| **Test IDs** | **Purpose** | **Key Question** |
| --- | --- | --- |
| `BL-1`<br>`BL-2` | Baseline truncation threshold<br>on small pages | _What's the T1 vs T2 surface delta?_ |
| `SC-2` | API docs - code blocks | _How does the web toolchain handle code structure?_ |
| `OP-1` | Fragment identifier navigation | _Does Codex jump to a specific section via URL fragment?_ |
| `OP-2` | Midrange reference - <br>headings, code blocks | _Does behavior change at midrange size with structured content?_ |
| `OP-4` | Auto-chunking above<br> `BL-3` ceiling | _Does the agent fetch with multi-step tool chains?_ |
| `BL-3` | Hard ceiling | _What's the absolute output limit across retrieval runs?_ |
| `SC-1`<br>`SC-3`<br>`SC-4` | Structured content -<br>API docs, table-heavy,<br>nested headings | _Does truncation respect Markdown boundaries?_ |
| `EC-1`<br>`EC-3`<br>`EC-6` | Edge cases - line-wrapping,<br>JSON redirect, SPA | _What are the failure modes and workspace substitution edge behaviors?_ |

>_Rename output files to capture variance; if results are consistent, remove files to prevent contamination_

---

## Workflow

1. **List Available Tests and Tracks**

   ```bash
   python scripts/framework.py --list-tests
   python scripts/framework.py --list-tracks
   ```

2. **Generate Test Prompt for a Single Test**

   ```bash
   # T1: GPT-interpreted, Codex Desktop
   python scripts/framework.py --test BL-1 --track codex-interpreted

   # T2: GPT-interpreted, Codex Extension
   python scripts/framework.py --test BL-1 --track vscode-codex-interpreted

   # T3: Raw verbatim output, Codex Desktop
   python scripts/framework.py --test BL-1 --track codex-raw

   # T4: Raw verbatim output, Codex Extension
   python scripts/framework.py --test BL-1 --track vscode-codex-raw
   ```

3. **Copy Prompt → Run in Codex**

   - Review the terminal output &rarr; copy the prompt
   - Open the Codex IDE or VS Code-Codex chat window &rarr; paste the prompt
   - Inspect retrieval behavior &rarr; examine agent output

4. **Assess Hypotheses Against Agent Output**

   | **ID** | **Description** | **Question** |
   | --- | --- | --- |
   | `H1` | Character-based truncation at fixed limit | _Is there a ceiling at ~10–100 KB?_ |
   | `H2` | Token-based truncation | _Is there a token ceiling at ~2K?_ |
   | `H3` | Structure-aware truncation | _Does truncation fall on Markdown boundaries rather than<br>arbitrary byte positions?_ |
   | `H4` | Surface impact on retrieval behavior | _Does the Codex IDE versus VS Code-Codex surface<br>produce different retrieval behavior?_ |
   | `H5` | Auto-chunking and/or pagination | _Does the agent fetch with multi-step tool chains, or<br>only when reasoned into it?_ |

5. **Examine, Log, Analyze**

   - Examine Codex rollout logs, details in [Rollout Observability](#rollout-observability)
   - Log results with `log.py`, read [Logging & Verification](#logging--verification)
   - Analyze results with `analyze.py`, visit [Analysis](#analysis)

---

## Rollout Observability

>_Examine `~/.codex/sessions/rollouts` logs for session structure and anomalies.
> Point scripts at `results/{track}/artifacts/rollouts` for parsing._

```text
results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-2026-06-11T14-08-50-....jsonl
```

### Session Overview

`read_session.py` produces a structured report from one or more rollouts including
session metadata, model, sandbox policy, skills, token usage, tool calls, reasoning
presence, and the conversation.

```bash
# Text report to stdout
python scripts/read_session.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl

# HTML report
python scripts/read_session.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl -o report.html

# List sessions and filter by ID
python scripts/read_session.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl --list-sessions
python scripts/read_session.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl --session-id <id>
```

### Rollout Audit

`rollout_audit.py` checks logs for duplicate emissions, timing drift, live event stream and transcript
mismatches, post-completion records, and tool-call counts. Any anomaly exits with nonzero. For each
session, the audit reports:

| **Category** | **Reported** |
| --- | --- |
| Identity | Session id, LLM, reasoning effort, CLI version, test prompt ID if present |
| Emission Counts | User messages, commentary updates, final answers, reasoning blocks |
| API Call Counts | `web_search` calls, function/tool calls, by tool name |
| Duplicate Detection | Any final answer generated more than once, whether `event_msg`,<br>`response_item`, `task_complete.last_agent_message` copies match |
| Post-completion Records | Anything appended after the last `task_complete` |
| Timing | Duration, time to first token, wall clock between first-last record |
| Token Usage | From final `token_count` event |

```bash
# Audit a test's rollouts
python scripts/rollout_audit.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl

# Audit all rollouts for a track, write a CSV
python scripts/rollout_audit.py results/vscode-codex-interpreted/artifacts/rollouts/*/*.jsonl --csv audit.csv
```

### Rollout Decode

`rollout_decode.py` converts logs into three readable views:

- `--timeline`, _default_: chronological summary of events, tool calls, and messages
- `--census`: record and payload type inventory with field frequencies
- `--pretty`: full indented JSON of every record, with encrypted reasoning blobs elided

>_`timeline` output distinguishes UI-facing events (`AGENT`, `WEB`, `SHELL`) from the
>LLM-facing transcript copies (`AGENT*`, `WEB*`, `FINAL*`). `THINK` blocks encrypted
>and unreadable; `TOKENS` rows are cumulative session usage checkpoints._

```bash
# Timeline for a test
python scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl --timeline

# Census: what record and payload types exist in logs
python scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl --census

# Pretty-print only web_search_call records
python scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl --pretty --grep web_search_call

# Write timeline to a Markdown file
python scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl --timeline --md decoded.md
```

### Artifact Watcher

Codex rollouts don't log temp-file creation or workspace writes. `artifacts_watcher.py` records filesystem events while Codex agents
write logs of `created`, `modified`, `moved`, and `deleted` events under `~/.codex` and the macOS temp directories; correlate with
`session_id` and timestamp; ignores macOS service noise such as `com.apple.*`, `.icloud`, `TemporaryItems`:

```bash
# Start before test
python scripts/artifacts_watcher.py --test SC-4 --track vscode-codex-interpreted

# Stop with Ctrl-C after turn completes; output lands at
# results/{track}/artifacts/fs-events/{test}/fs-events-{timestamp}.jsonl
```

```json
{
    "timestamp": "2026-06-27T02:15:03.123456+00:00",
    "event_type": "modified",
    "src_path": "/private/tmp/codex-.../data.html",
    "dest_path": null,
    "size": 64659,
    "is_directory": false,
    "test_id": "SC-4",
    "track": "vscode-codex-interpreted"
}
```

### Failure-Mode Detection

Codex rollouts don't emit structured error events; failures appear as plain text inside tool outputs.
`scripts/failure_classifier.py` detects the following patterns deterministically so the harness counts failures
without relying on the agent self-reports:

| **Category** | **Pattern** |
| --- | --- |
| `browser_unavailable` | `Browser is not available: iab` |
| `dns_blocked` | `curl: (6) Could not resolve host: …` |
| `fetch_failed` | `fetch failed`, `getaddrinfo ENOTFOUND`, other nonzero `curl` exits |
| `sandbox_empty_response` | `Process exited with code 0` but `Output:` section is empty, whitespace-only,<br>or exactly `0`; indicates sandboxed network command that agent recovered<br>via escalation |
| `cache_miss` | One-line `Cache miss` tool response |
| `command_not_found` | exit 127, `command not found`, `ModuleNotFoundError` |
| `runtime_error` | Python traceback, HTTP errors |
| `ui_truncation` | `Truncated content`, `was UI-truncated` |

Rollout scripts include classifier content while counting failures separately; if a turn reaches
`task_complete`, its raw failure categories are still reported, but `recovered_failure_count` records how many of them
occurred inside a completed turn.

| **Script** | **Output** |
| --- | --- |
| `rollout_audit.py` | Adds `failure_count_*`, `failure_categories`, `recovered_failure_count`, `has_failure`, `first_failure_category`, `first_failure_detail` columns to CSV with `FAILURES_DETECTED` |
| `rollout_decode.py` | Tags failed tool outputs as `FAIL [category]` in `--timeline`; prints a `FAILURES:` summary block |
| `read_session.py` | Renders per-turn failure badges, dedicated **Issues** panel in HTML report |

## Logging

Run the interactive logger and follow the prompts. Fields grouped by track:
session fields first, then track-specific output fields, then hypothesis and notes.
Quotation marks not necessary; skip optional fields with `Enter`:

```bash
# Call logger
python scripts/log.py

# Logger prompts-validates fields before writing
✓ Result logged to results/codex-{track}/results.csv
```

> _Verify key metrics before logging raw track runs with `python scripts/verify.py {test_id}`._
> _When logging Track 2 results, pull the matching Track 1 record with `python scripts/query.py --test {test_id} --models {model}`._

### Framework Fields

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
| `permission_level` | Agent permission setting | `default`, `auto-review`, `full-access` |
| `model_observed` | LLM reported in output | `GPT-5.5` |
| `model_intelligence_level` | LLM intelligence setting | `low`, `medium`, `high`, `extra high` |
| `input_est_chars` | Expected input size in characters | `87040` |
| `hypothesis_match` | Hypothesis success/failure | `H1-no`, `H2-yes`, `H4-untested` |
| `codex_version` | Codex version string | `1.0.0` |
| `notes` | Observations | `web tool invoked` |
| `tools_named` | Tool names reported in agent output | `web`, `web.open`, `curl` |
| `workspace_substitution` | _Local execution instead of web fetch?_ | `yes`/`no`/`unknown` |
| `output_chars` | `T1`/`T2`: agent-measured output length | `27890` |
| `truncated` | `T1`/`T2`: truncation status | `yes`/`no`/`mixed`/`implicit` |
| `truncation_note` | `T1`/`T2`: location, layer, or characterization | `web.open partial, curl complete` |
| `tokens_est` | `T1`/`T2`: estimated token count | `16890` |
| `tools_used`* | `T3`/`T4`: observed tool chain | `web -> web.open` |
| `tools_blocked`* | `T3`/`T4`: tools requested, but skipped | `curl` |
| `execution_attempts`* | `T3`/`T4`: total tool calls, fallbacks | `3` |
| `escalation_trigger`* | `T3`/`T4`: what drove tool escalation | `automatic`, `contaminated`, `none`, `reasoned` |
| `artifact_path`* | `T3`/`T4`: path of agent-written file | `/private/tmp/bl1_response.html` |
| `artifact_size_bytes`* | `T3`/`T4`: agent-written file size | `505339` |
| `last_50_chars`* | `T3`/`T4`: retrieved content verbatim;<br>cross-reference via `verify.py` | `])</script></body></html>` |
| `agent_reported_output_chars`* | `T3`/`T4`: agent-measured char count | `9876` |
| `agent_reported_truncated`* | `T3`/`T4`: agent-measured truncation status | `yes`/`no`/`mixed`/`implicit` |
| `agent_reported_truncation_note`* | `T3`/`T4`: agent-reported location,<br>layer or characterization | `curl complete, web.open partial at L477` |
| `agent_reported_tokens_est`* | `T3`/`T4`: agent-estimated token count | `2469` |
| `agent_reported_file_size_bytes`* | `T3`/`T4`: agent-measured file size | `4817` |
| `agent_reported_md5_checksum`* | `T3`/`T4`: agent-measured MD5 | `abc123...` |
| `agent_reported_lines`* | `T3`/`T4`: agent-measured line count | `143` |
| `agent_reported_words`* | `T3`/`T4`: agent-measured word count | `564` |
| `agent_reported_code_blocks`* | `T3`/`T4`: agent-measured code block count | `2` |
| `agent_reported_table_rows`* | `T3`/`T4`: agent-measured table row count | `57` |
| `agent_reported_headers`* | `T3`/`T4`: agent-measured header count | `4` |
| `verified_file_size_bytes`* | `T3`/`T4`: verifier-measured file size | `4817` |
| `verified_md5_checksum`* | `T3`/`T4`: verifier-measured MD5 | `d6ad8451d3778bf3544574...` |
| `verified_total_lines`* | `T3`/`T4`: verifier-measured line count | `143` |
| `verified_total_words`* | `T3`/`T4`: verifier-measured word count | `564` |
| `verified_tokens`* | `T3`/`T4`: verifier-measured token count | `197` |
| `verified_chars_per_token`* | `T3`/`T4`: verifier-measured chars/token ratio | `4.43` |
| `verified_code_blocks`* | `T3`/`T4`: verifier-measured code block count | `2` |
| `verified_table_rows`* | `T3`/`T4`: verifier-measured table row count | `57` |
| `verified_headers`* | `T3`/`T4`: verifier-measured header count | `4` |

> _*Optional field, raw tracks only. `agent_reported*` fields reflect tool output or payload estimates.
> <br>`verify.py` calculates `verified*` values against `raw_output_{test_id}.txt` files._

---

## Analysis

Examine hypothesis matching, surface-workspace effects, perception gap, and truncation analysis:

```bash
# Single track full analysis or summary
python scripts/analyze.py --csv results/codex-interpreted/results.csv --summary
python scripts/analyze.py --csv results/codex-raw/results.csv --full

# Filter by track
python scripts/analyze.py --csv results/codex-interpreted/results.csv --track t1_codex_interpreted

# Compare interpreted tracks T1 vs T2
python scripts/analyze.py \
   --csv results/codex_interpreted/results.csv \
         results/vscode-codex-interpreted/results.csv --full

# Compare raw tracks T3 vs T4
python scripts/analyze.py \
   --csv results/codex_raw/results.csv \
         results/vscode-codex-raw/results.csv --full

# Compare all tracks
python scripts/analyze.py \
   --csv results/codex-interpreted/results.csv \
         results/vscode-codex-interpreted/results.csv \
         results/codex-raw/results.csv \
         results/vscode-codex-raw/results.csv --full
```

>_Provide the full relative path including subdirectory, `results/codex-interpreted/results.csv`_
