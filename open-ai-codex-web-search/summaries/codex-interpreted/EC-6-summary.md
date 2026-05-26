# EC-6 Summary

## Test Conditions

|                 | **EC-6**                                                                                      |
| --------------- | --------------------------------------------------------------------------------------------- |
| URL             | `https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md`              |
| Expected size   | ~60KB per prompt; actual confirmed 91,869 chars / 91,877 bytes via `curl` / ~22,967 tokens    |
| Surface         | Codex IDE                                                                                     |
| Workspace       | Session-scoped sandbox; `/private/tmp` cleared between sessions; `Documents/Codex` persistent |
| Track           | `T1` GPT-interpreted, Codex IDE                                                               |
| Method          | GPT-interpreted                                                                               |
| Runs            | 20                                                                                            |
| Chunks returned | N/A, codex-interpreted track                                                                  |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Workspace sub. | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------------- | ----- |
| `GPT-5.2 Low` | 91,869 | ~22,967 | Display yes, file no | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `functions.exec_command`, `curl`, `python3` | Yes | `web.run` cache miss; `curl` fallback; display truncation with `…20470 tokens truncated…` marker; wrote `EC-6_SPEC.md` to `/private/tmp`; 54 seconds |
| `GPT-5.2 Medium` | 91,869 | ~22,967 | No | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `functions.exec_command`, `curl`, `wc`, `tail` | Yes | `web.run` cache miss; `curl` fallback; `Content-Length` not verified; wrote `EC-6_SPEC.md` to `/private/tmp`; possible contamination from run 1; 43 seconds |
| `GPT-5.2 High` | 91,877 | ~22,967 | No | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `web.search_query`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | Yes | `web.run` cache miss; `curl` fallback; `tiktoken False`; searched web three times; wrote `EC-6_SPEC.md` to `/private/tmp`; possible contamination; 2 minutes 12 seconds |
| `GPT-5.2 Extra High` | 91,869 | ~22,967 | No | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `web.search_query`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3`, `node` | Yes | `web.run` cache miss with `open`, `search_query`, and `click` sequence; fetched `Content-Length` headers separately; `tiktoken` unavailable; wrote `SPEC_fetched.md` to workspace and `spec_headers.txt` to `/private/tmp`; 3 minutes 26 seconds |
| `GPT-5.3-Codex Low` | 91,869 | ~22,967 | No | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command`, `curl`, `python3` | Yes | bypassed `web` pipeline entirely; `curl` with DNS failure then retry; wrote `ec6_spec.md` to `/private/tmp`; 41 seconds |
| `GPT-5.3-Codex Medium` | 91,877 | ~22,970 | No | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `awk` | Yes | `web.open` cache miss; `curl` fallback; possible workspace substitution rather than fresh fetch; contamination flag; named test `Fetch SPEC.md URL`; 24 seconds |
| `GPT-5.3-Codex High` | 91,869 | ~17,000 | No | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `web.search_query`, `functions.exec_command`, `curl`, `wc`, `tail`, `python3` | Yes | `web.run` cache miss; `curl` fallback; word-based token heuristic produces divergent estimate from chars/4; wrote `EC-6_SPEC.md` to workspace; app refresh mid-run caused command detail loss; 1 minute 16 seconds |
| `GPT-5.3-Codex Extra High` | 91,869 | ~22,967 | No | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `web.search_query`, `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `node` | Yes | most elaborate `web.run` attempt in `5.3-Codex` track with `open`, `search_query`, and `click`; `tiktoken` unavailable; possible workspace contamination; wrote `ec6_spec.md` to `/private/tmp`; 2 minutes 33 seconds |
| `GPT-5.4-Mini Extra High` | 91,869 | ~22,967 | No | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `functions.exec_command`, `curl`, `node` | Yes | `web.open` cache miss; `curl` fallback; two script syntax errors before successful analysis; used `node -e` rather than `python3`; wrote `SPEC.md` to workspace; 1 minute 44 seconds |
| `GPT-5.4-Mini High` | 91,869 | ~22,967 | No | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `functions.exec_command`, `curl`, `python3` | Yes | `web.open` cache miss; `curl` fallback; checked `START50` alongside `LAST50`; acknowledged ~60KB size discrepancy; wrote `agent-docs-spec-SPEC.md` to `/private/tmp`; 31 seconds |
| `GPT-5.4-Mini Medium` | 91,869 | ~17,000 | No | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `node`, `python3` | Yes | `web.open` cache miss; `curl` fallback; most permission-heavy run with `curl` twice, `node` twice, `wc -w` twice; used both `node` and `python3` for inspection; possible contamination via filename reuse; 1 minute 59 seconds |
| `GPT-5.4-Mini Low` | 91,869 | ~23,000 | No | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `functions.exec_command`, `curl`, `python3` | Yes | `web.run` cache miss; `curl` fallback; used `tee` to simultaneously stream and save; acknowledged ~60KB size discrepancy; wrote `spec.md` to `/private/tmp`; 23 seconds |
| `GPT-5.4 Low` | 91,877 | ~23,000 | No | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `python3` | Yes | `web.open` cache miss; `curl` fallback; used `rg` for fence searching; proactively flagged ~60KB discrepancy as empirical log note; wrote `EC-6_SPEC.md` to workspace; 40 seconds |
| `GPT-5.4 Medium` | 91,869 | ~22,970 | Display yes, file no | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `web.search_query`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `file`, `node` | Yes | display truncation at `…12970 tokens truncated…` mid-document near `Who Actually Uses llms.txt?` section; saved file complete; `Original token count: 22970` reported by tool metadata; wrote `EC-6-SPEC.md` to workspace; 1 minute 11 seconds |
| `GPT-5.4 High` | 91,869 | ~22,970 | Display yes, file no | `— Notable exclusions with rationale (Appendix B).` | `web.open`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `node` | Yes | display truncation at `…12970 tokens truncated…`; cut mid-word near `...ticate with, adding a docs subcommand…` after `GPTBot`, `ClaudeBot`, `PerplexityBot` line; most forensically precise truncation report in cycle; wrote `EC-6-SPEC.md` to workspace; 2 minutes 35 seconds |
| `GPT-5.4 Extra High` | 91,869 | ~22,970 | Display yes, file no | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `functions.exec_command`, `curl`, `wc`, `tail`, `sed`, `rg`, `xxd`, `node`, `multi_tool_use.parallel` | Yes | display truncation at `…12970 tokens truncated…`; same cut section as runs 14 and 15; used `xxd` for hex-level byte inspection; `multi_tool_use.parallel` invoked; wrote `ec6_spec.md` to `/private/tmp`; possible contamination via filename reuse; 2 minutes 22 seconds |
| `GPT-5.5 Low` | 91,869 | ~22,968 | No | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `node` | Yes | bypassed `web` pipeline entirely; `curl -I` for independent header fetch; `Content-Length` match verified without prompting; node JSON output with `estTokensByChars` key; wrote `ec-6-spec.md` to `/private/tmp`; possible contamination; 45 seconds |
| `GPT-5.5 Medium` | 91,869 | ~22,968 | Display yes, file no | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `node`, `multi_tool_use.parallel` | Yes | `web.run` cache miss; display truncation confirmed; cut point not precisely identified; `multi_tool_use.parallel` for validation; explicitly framed tool UI truncation vs HTTP response truncation; wrote `SPEC.md` to workspace; 1 minute 4 seconds |
| `GPT-5.5 High` | 91,869 | ~22,970 | Display yes, file no | `— Notable exclusions with rationale (Appendix B).` | `web.run`, `functions.exec_command`, `curl`, `wc`, `tail`, `rg`, `node`, `multi_tool_use.parallel` | Yes | `web.run` cache miss; display truncation in `curl` output near `Truncation` terminology section; `Original token count: 22970` confirmed; `multi_tool_use.parallel` invoked; wrote `SPEC.md` to workspace; 1 minute 17 seconds |
| `GPT-5.5 Extra High` | 91,869 | ~23,000 | No | `— Notable exclusions with rationale (Appendix B).` | `functions.exec_command`, `curl`, `wc`, `tail`, `sed`, `rg`, `python3`, `multi_tool_use.parallel` | Yes | bypassed `web` pipeline entirely; `curl --write-out` for programmatic HTTP metadata; `http_code=200` and `size_download=91877` verified cleanly; `tiktoken_available: False`; wrote `ec-6-spec.md` to `/private/tmp`; possible contamination; 2 minutes 9 seconds |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported for the HTTP response body layer. All 20 runs retrieved 91,869 chars or 91,877 bytes intact via `curl`, well above any proposed 10–100 KB ceiling.
However, six runs observed display truncation in the `curl` tool output rendered inline in the Codex chat interface. This is the terminal display truncation
layer described in the Truncation Taxonomy, not an HTTP retrieval ceiling.

**Combined verdict: `H1` no for HTTP retrieval. Display truncation is a separate phenomenon consistent with a ~12,970 token tool output renderer ceiling, not a
character-based fetch limit.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported as a retrieval ceiling. All `curl`-path runs retrieved ~22,967 tokens intact. The display truncation observed in runs 1, 14, 15, 16, 18, and 19 carried
an explicit `…12970 tokens truncated…` marker, confirming a token-based display ceiling well above 2,000 tokens but below the full document size. The threshold was
consistent across three independent `GPT-5.4` runs and two `GPT-5.5` runs.

**Combined verdict: `H2` no for retrieval ceiling. Display truncation is token-based at approximately 12,970 tokens, not 2,000, and applies to tool output rendering
rather than the HTTP response body.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported. `GPT-5.4 High` identified the display truncation cut point most precisely: mid-word near `...ticate with, adding a docs subcommand…` after a line mentioning
`GPTBot`, `ClaudeBot`, and `PerplexityBot` in the `Who Actually Uses llms.txt?` subsection. The mid-word cut confirms an arbitrary token position rather than a Markdown boundary.
Runs where no truncation occurred can't contribute to this assessment.

**Combined verdict: `H3` no. Mid-word truncation at a fixed token position is the strongest evidence against structure-aware truncation across the full test cycle.**

---

## `H4`: Surface context, Codex IDE versus VS Code-Codex changes retrieval behavior

Untested for cross-surface comparison. All 20 runs used the Codex IDE surface exclusively.

**Combined verdict: `H4` untested.**

---

## `H5`: Agent auto-chunks or auto-paginates

Not supported. Every run used a single `curl` fetch with no multi-step retrieval chaining. Runs with more complex toolchains were applying measurement instrumentation rather
than retrieval strategy. No run attempted to paginate the `web` output or split the fetch.

**Combined verdict: `H5` no. Single fetch across all 20 runs. No adaptive retrieval behavior observed.**

---

## Emergent Findings

1. **`web.run` consistently hit `Cache Miss` on the raw GitHub URL across every run that attempted it.** Seventeen of 20 runs attempted `web.open` or `web.run` on the raw URL
and received `Failed to fetch ...: Cache miss (no content retrieved)`. No run recovered usable content from the `web` path. Three runs bypassed `web` entirely. The failure is
systematic rather than transient and appears URL-class-specific to `raw.githubusercontent.com` for this payload. A control test within the cycle confirmed a smaller
`raw.githubusercontent.com` file loaded successfully, ruling out a blanket host block. See the Cache Miss section in the Friction Note for full characterization.

2. **Display truncation at ~12,970 tokens is the strongest cross-run finding in this cycle.** Six runs independently observed the same `…12970 tokens truncated…` marker in `curl`
tool output rendered inline. The threshold was consistent across `GPT-5.2 Low`, `GPT-5.4 Medium`, `GPT-5.4 High`, `GPT-5.4 Extra High`, `GPT-5.5 Medium`, and `GPT-5.5 High`. Saved
files were complete in all cases. This is the terminal display truncation layer in the Truncation Taxonomy and is independent of both the `web` viewer window and the HTTP response body.

3. **Artifact production high relative to other test IDs.** Twenty artifacts written across 20 runs: nine to `Documents/Codex` and seven to `/private/tmp`. Several runs reused filenames
from prior runs, including `ec6_spec.md`, `EC-6_SPEC.md`, and `agent-docs-spec-SPEC.md`. `GPT-5.3-Codex Medium` is the only run with a plausible workspace substitution rather than a
fresh fetch. The high artifact rate may reflect the file being a complete, well-formed Markdown document with no rendering complications, making it a natural save target.

4. **Only one run fetched HTTP headers independently.** `GPT-5.2 Extra High` wrote a separate `spec_headers.txt` file containing the full HTTP response headers including `Content-Length`,
`ETag`, and CDN metadata. No other run performed independent header inspection. This is consistent with `BL-3` findings where header fetching was common in some LLM families but not others.

5. **No run diagnosed or investigated `Cache Miss`.** Every run that hit the error silently pivoted to `curl` without examining the failure, attempting the blob URL as an alternate, or
flagging the error as a signal about `web` pipeline limitations. This is consistent with the Truncation Taxonomy finding that agents report what succeeded, not what failed.

6. **Token estimate diverges across runs due to inconsistent heuristics.** Most runs used the chars/4 heuristic producing ~22,967 tokens. `GPT-5.3-Codex High` and `GPT-5.4-Mini Medium`
used word-based counting and reported ~17,000 tokens from the same document. `GPT-5.5 Low` reported `estTokensByChars: 22968` via a node JSON structure. The schema instability in `EC-3`
is present here as well, but with a meaningful numeric divergence rather than just key name variation.

7. **`multi_tool_use.parallel` appears in `GPT-5.5` runs and `GPT-5.4 Extra High` only.** Consistent with `EC-3` findings where this identifier was exclusive to `GPT-5.5`. Its appearance
in `GPT-5.4 Extra High` is the first instance outside the `5.5` family across the test cycle.

8. **`GPT-5.5` bypasses `web` entirely more often than other LLMs.** Both `GPT-5.5 Low` and `GPT-5.5 Extra High` went directly to `curl` without attempting `web.run`. `GPT-5.5 Medium`
and `GPT-5.5 High` attempted `web.run` but moved on immediately after the `Cache Miss`. The tendency to bypass `web` is more pronounced in `GPT-5.5` than in any other LLM in this cycle.

9. **`GPT-5.4 High` produced the most forensically precise truncation report in the cycle.** The run identified the cut section, the resumed mid-word text, and explicitly distinguished
tool-display truncation from actual fetch completeness. This level of self-reporting wasn't prompted and didn't appear in any other run at comparable detail. `GPT-5.4 Medium` and
`GPT-5.4 Extra High` reported the same truncation marker but without the section-level and word-level precision.

10. **The ~60KB expected size prompt prior acknowledged in several runs but not consistently.** Runs 9, 10, 11, 13, 16, and 20 explicitly noted the discrepancy between the ~60KB prompt
expectation and the actual ~92 KB received. Other runs didn't comment on it. Unlike `EC-3` where the size mismatch prompted mechanistic hypotheses about normalization, no `EC-6` run
offered an explanation for the discrepancy beyond noting it.

11. **`GPT-5.4 Extra High` is the only run to use `xxd` for hex-level byte inspection.** This is also the only run across the full test cycle to use `xxd` at all. It appeared alongside
`sed` and `rg` as part of a tail-end byte verification pass. The additional tooling didn't produce different measurements from simpler approaches.

12. **Truncation self-reporting was explicit in all cases where it occurred.** Unlike `EC-3` where truncation was always `no` and an implicit truncation argument was possible, `EC-6`
produced explicit `yes`, `no`, and `mixed` reports. No run logged implicit truncation while using `curl` as a proxy for incompleteness. Runs that observed display truncation said so
directly, and runs that didn't observe it said so as well.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.2 Low` | Pass | `PASS - web_cache_miss + curl_91877_bytes + display_truncation_20470_tokens + EC6_SPEC_md_private_tmp + 54 seconds` |
| `GPT-5.2 Medium` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + EC6_SPEC_md_private_tmp + possible_contamination + 43 seconds` |
| `GPT-5.2 High` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + tiktoken_false + EC6_SPEC_md_private_tmp + possible_contamination + 2 minutes 12 seconds` |
| `GPT-5.2 Extra High` | Pass | `PASS - web_cache_miss_open_search_click + curl_91877_bytes + no_truncation + headers_artifact + SPEC_fetched_md_workspace + spec_headers_txt_private_tmp + 3 minutes 26 seconds` |
| `GPT-5.3-Codex Low` | Pass | `PASS - web_bypassed + curl_91877_bytes + no_truncation + ec6_spec_md_private_tmp + 41 seconds` |
| `GPT-5.3-Codex Medium` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + possible_workspace_substitution + contamination_flag + 24 seconds` |
| `GPT-5.3-Codex High` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + word_based_token_divergence + EC6_SPEC_md_workspace + timer_data_lost + 1 minute 16 seconds` |
| `GPT-5.3-Codex Extra High` | Pass | `PASS - web_cache_miss_open_search_click + curl_91877_bytes + no_truncation + tiktoken_unavailable + ec6_spec_md_private_tmp + possible_contamination + 2 minutes 33 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + node_analysis + syntax_errors_recovered + SPEC_md_workspace + 1 minute 44 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + start50_checked + 60kb_discrepancy_noted + agent_docs_spec_SPEC_md_private_tmp + 31 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + word_based_token_divergence + permission_heavy + node_and_python3_both_used + possible_contamination + 1 minute 59 seconds` |
| `GPT-5.4-Mini Low` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + tee_stream_save + 60kb_discrepancy_noted + spec_md_private_tmp + 23 seconds` |
| `GPT-5.4 Low` | Pass | `PASS - web_cache_miss + curl_91877_bytes + no_truncation + rg_fence_search + 60kb_discrepancy_noted + EC6_SPEC_md_workspace + 40 seconds` |
| `GPT-5.4 Medium` | Pass | `PASS - web_cache_miss + curl_91877_bytes + display_truncation_12970_tokens + who_actually_uses_llms_cut + EC6_SPEC_md_workspace + 1 minute 11 seconds` |
| `GPT-5.4 High` | Pass | `PASS - web_cache_miss + curl_91877_bytes + display_truncation_12970_tokens + mid_word_cut_ticate_with + most_precise_truncation_report + EC6_SPEC_md_workspace + 2 minutes 35 seconds` |
| `GPT-5.4 Extra High` | Pass | `PASS - web_cache_miss + curl_91877_bytes + display_truncation_12970_tokens + xxd_hex_inspection + multi_tool_use_parallel + ec6_spec_md_private_tmp + possible_contamination + 2 minutes 22 seconds` |
| `GPT-5.5 Low` | Pass | `PASS - web_bypassed + curl_91877_bytes + no_truncation + curl_I_headers + content_length_verified + estTokensByChars_key + ec6_spec_md_private_tmp + possible_contamination + 45 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS - web_cache_miss + curl_91877_bytes + display_truncation_confirmed + cut_point_imprecise + multi_tool_use_parallel + SPEC_md_workspace + 1 minute 4 seconds` |
| `GPT-5.5 High` | Pass | `PASS - web_cache_miss + curl_91877_bytes + display_truncation_near_truncation_section + original_token_count_22970 + multi_tool_use_parallel + SPEC_md_workspace + 1 minute 17 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS - web_bypassed + curl_91877_bytes + no_truncation + curl_write_out_http_metadata + tiktoken_false + ec6_spec_md_private_tmp + possible_contamination + 2 minutes 9 seconds` |
