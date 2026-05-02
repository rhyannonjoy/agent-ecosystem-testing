---
layout: default
title: "Key Findings for Copilot's Web Fetch Behavior, Raw"
permalink: /docs/microsoft-github-copilot/copilot-test-findings-raw
parent: Microsoft GitHub Copilot
---

# Key Findings for Copilot's Web Fetch Behavior, Raw

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/copilot-web-content-retrieval/web_content_retrieval_testing_framework.py)

1. Run `python web_content_retrieval_testing_framework.py --test {test ID} --track raw`
2. Review terminal output
3. Copy the provided prompt asking Copilot to retrieve the URL, save the content<br>
   exactly as received, report file size, MD5 checksum, character/line/word/token<br>
   counts, code blocks, table rows, headers, hexdump of last 256 bytes, and any<br>
   visible tool/server identifiers
4. Open a new Copilot session in VS Code, paste the prompt into the chat window
5. Allow terminal tool calls; skip any requests for local script runs
6. Run the verifier: `python web_content_retrieval_verify_raw_results.py {test ID}`
7. Log both Copilot-reported, verifier-measured values as separate fields;
   <br>the delta between them is the finding
8. Ensure log results saved to `/results/raw/results.csv`

>*_Results logged as "Methods tested: `vscode-chat`" reflect a manually operated testing process in which prompts are copy-pasted into the Copilot
>chat window. The raw track captures the actual saved file independently of Copilot's self-report, enabling direct comparison; read [Friction Note](friction-note.md) for methodology complications._

---

## Platform Limit Summary

| **Limit** | **Observed** |
| ------- | ---------- |
| **Retrieval Mechanism** | _Unstable_: agent autonomously selects between `fetch_webpage` and `curl` with no prompt control; selection determines output format more than any other variable |
| **`fetch_webpage` Output** | _Relevance-ranked excerpts_: HTML-to-Markdown transformation with chunk-based reassembly, non-linear ordering, and `...` elision markers; never returns full sequential page content |
| **`curl` Output** | _Byte-perfect full retrieval_: complete file transfer confirmed by `content-length` matching saved file size; no transformation layer; delivers raw bytes in server format |
| **Retrieval Completeness** | _Format-dependent_: `curl` runs confirm 100% byte retrieval; `fetch_webpage` runs return relevance-ranked subset with no fixed character ceiling observed |
| **Truncation Pattern** | `fetch_webpage` - retrieval-layer excerpting , `curl` - complete retrieval with format-driven unreadability, and chat rendering cutoff |
| **Tool Substitution** | _Autonomous and model-dependent_: `curl` substitution occurs without prompt instruction and without disclosure; `GPT-5.4` substituted in all `EC-6``curl` runs; `Claude Sonnet 4.6` substituted after citing `fetch_webpage` limitations |
| **Self-reported Metrics** | _Mixed reliability_: file size and word count typically accurate; token estimates vary by methodology - chars/4 heuristic, word count substitution, `cl100k_base`; structural counts - code blocks, table rows are methodology-dependent and under-specified |
| **Agentic Over-Delivery** | _Consistent pattern_: agent autonomously produces unrequested artifacts including headers files, hexdump files, analysis reports, and verbatim content in chat; type correlates with retrieval mechanism |
| **Model Routing** | _Unstable_: `Auto` dispatches across model families within a single test series; tool selection behavior, metric accuracy, and output format all vary by model |

## Results Details

| --- | --- |
| **Model Selector** | `Auto` |
| **Models Observed** | `Claude Haiku 4.5`, `Claude Sonnet 4.6`, `GPT-4.1-Codex`,<br>`GPT-4.5-Codex`, `GPT-5.3-Codex`, `GPT-5.4` |
| **Total Tests** | 55 |
| **Distinct URLs** | 11 |
| **Input Size Range** | ~2 KB–256 KB |
| **Truncation Events** | Copilot self-reported 16 / 55 |
| **Average Output Size** | 787,084 chars |
| **Average Token Count** | 284,463 tokens |
| **Verification Method** | Python verification script measuring raw output;<br>delta between Copilot-reported and verified values |

>_Raw track average output size dramatically higher than the interpreted track average because curl substitution runs deliver
>complete files while `fetch_webpage` runs return relevance-ranked excerpts. Averaging across both mechanisms in the same figure
>produces a number that doesn't describe either._

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| **1** | **Tool selection primary variable in output type** | All tests | `fetch_webpage` produces relevance-ranked Markdown excerpts; `curl` produces byte-perfect raw files in server format; same URL, model, prompt produces either outcome non-deterministically | **`tools_used` field captures which retrieval mechanism used, which is more predictive of output format than URL, page size, model, or prompt wording** |
| **2** | **`fetch_webpage` performs HTML-to-Markdown transformation with non-linear reassembly** | `BL-3` `SC-1` `SC-4` | Raw output order doesn't match page reading order; intro appears near bottom, not top; `...` separators, repeated H1 headers are chunking artifacts not page content; UI elements stripped, footer preserved verbatim | **`fetch_webpage` performs structural transformation with chunk-based reassembly, not truncation or semantic filtering; output reflects tool's internal chunking format, not page structure** |
| **3** | **`curl` substitution delivers complete files but at the cost of readability** | `SC-3` `SC-4` `EC-1` `EC-3` runs<br>4–5, `EC-6` runs 1,<br>3–5 | `content-length` matches saved file size exactly across all `curl` runs; Wikipedia 793,987 bytes, `markdownguide.org` 65,622 bytes, `SPEC.md` 85,325 bytes all transferred completely; output is raw HTML, JSON, or Markdown with no transformation | **Complete retrieval and useful output are separable; `curl` achieves the former and fails the latter by design; the substitution is a presentation failure, not a retrieval failure** |
| **4** | **`fetch_webpage` output quality correlates with source HTML structure** | `SC-4` run 3 | `Claude Sonnet 4.6` via `fetch_webpage` on `markdownguide.org` produced well-formed processed Markdown; returned 29,984 bytes against a 65,622-byte HTML source | **Source HTML convertibility is a necessary condition for high-fidelity `fetch_webpage` output but not sufficient; tool selection remains outside prompt control and 3 of 5 `SC-4` runs produced raw HTML via `curl` on the same URL** |
| **5** | **Tool substitution changes identity Copilot presents to target servers** | `EC-3` runs 4–5 | `fetch_webpage` presents a fetch_webpage presents a full browser-style User-Agent identifying VS Code as `Code/1.113.0` running on Chrome, Electron; `curl` presents `curl/8.7.1`; `httpbin.org` `/get` echoes received headers, making the identity difference directly observable in the response payload | **Tool substitution has infrastructure implications beyond output format; servers that serve different content by User-Agent would return different responses to `fetch_webpage` vs `curl` runs on the same URL** |
| **6** | **Copilot-reported metric accuracy varies systematically by field type** | All tests | File size, word count: reliable; character counts: encoding-methodology dependent - `wc -c` vs Unicode code points; token counts: three distinct failure modes - chars/4 undercount, word count substitution, `cl100k_base`; structural counts: methodology-dependent on HTML vs Markdown content | **Metric fields aren't uniformly reliable; token count is least reliable and most dependent on which computation path the agent selects; verification script is the authoritative source for all counts** |
| **7** | **Structural count discrepancies reflect output format, not counting errors** | `SC-4` runs 4–5 | Copilot reported 24 code blocks and 35 table rows on raw HTML file; verifier reported 0 code blocks and 0 table rows; both are correct, as Copilot counted HTML `<pre>` and `<tr>` tags, verification script counted Markdown fence patterns and pipe rows | **Code block and table row counts aren't comparable across runs that produce different output formats; zeros in verification output mark runs where expected output format never arrived, not measurement failures** |
| **8** | **Agentic over-delivery escalates with workspace artifact accumulation** | `SC-3` `SC-4` `EC-1` `EC-6` | Agent produces unrequested artifacts - headers files, hexdump files, analysis reports, verbatim content in chat - at increasing rates across the run series; later runs reference prior run artifacts in reasoning chains and generate cross-run comparisons unprompted | **Workspace artifact volume is an uncontrolled session variable; later runs in a session are behaviorally different from earlier runs due to accumulated context; session ordering is a methodology confounder** |
| **9** | **Headers files are produced by two distinct mechanisms with different implications** | `BL-3` `SC-3` `SC-4` `EC-6` | `fetch_webpage` runs sometimes save HTTP metadata autonomously; `curl` runs produce headers as structural output of the tool when invoked with capture flags - expected behavior; both produce `.headers.txt` files but represent different phenomena | **Headers file presence isn't a uniform signal; confirm which retrieval mechanism produced it before interpreting as agentic over-delivery; `curl` headers expose direct CDN infrastructure details invisible through `fetch_webpage`'s abstraction layer** |
| **10** | **Redirect chains followed transparently; JSON payloads subject to intra-value truncation** | `EC-3` | 5-level redirect chain followed silently to `/get`; returned JSON structurally complete, but User-Agent value internally truncated with `...` in `fetch_webpage` tool response; saved file contained complete value, suggesting silent reconstruction from prior knowledge | **`fetch_webpage`'s `...` elision operates at field-value level, not only at chunk-boundary level; saved file, tool response may differ; reconstruction undetectable without tool response log** |

## Retrieval Mechanism Distribution

| **Mechanism** | **Runs Observed** | **Output Format** | **File Completeness** |
| --- | --- | --- | --- |
| `fetch_webpage` | ~20 runs | Relevance-ranked Markdown excerpts with `...` elision | _Partial_, excerpted<br>subset of page |
| `curl` | ~30 runs | Raw bytes in server format - HTML, JSON, or Markdown | Complete; byte-perfect transfer confirmed |
| `fetch_webpage` + `curl` - sequential | ~5 runs | `fetch_webpage` attempted first, `curl` used for file save | File complete; chat content may differ |

>_Counts approximate; some runs used hybrid approaches where `fetch_webpage` retrieved content and `curl` used separately for headers
>or verification. The `tools_used` field is the authoritative source per run._

---

## Verifier Delta Summary

| **Test** | **Copilot-reported Size** | **Verified Size** | **MD5 Match?** | **Token<br>Delta** | **Structural<br>Count** |
| --- | --- | --- | --- | --- | --- |
| `EC-3` runs 1–3 | 868–869 bytes | 868–869 bytes | ✓ | chars/4 or word-count substitution | 0 code blocks, 0 table rows, 0 headers - JSON |
| `EC-3` runs 4–5 | 254 bytes | 254 bytes | ✓ | chars/4 undercount<br>by ~45 | Smaller payload;<br>minimal headers |
| `SC-4` run 3 | 29,984 bytes | 29,984 bytes | ✓ | +35 chars - multi-byte UTF-8 | Code blocks: 48 vs 25; table rows: omitted |
| `SC-4` runs 2,4 | 65,622 bytes | 65,622 bytes | ✓ | HTML-dense; heuristic undercounts | Code blocks: HTML vs Markdown methodology mismatch |
| `EC-6` runs 3–5 | 85,325 bytes | 85,325 bytes | ✓ | Node regex ~27 tokens under `cl100k_base` | Code blocks:<br>1 vs 4, column-1<br>pattern only |
| `EC-1` run 5 | 138,715 bytes | 138,715 bytes | ✓ | Word count substituted for token estimate - 5x undercount | 0 code blocks, 0 table rows, 0 headers<br>raw HTML |

>_Across all runs, Copilot self-reported no truncation regardless of whether the saved file was a relevance-ranked excerpt, a complete raw HTML file, or a
>byte-perfect Markdown transfer. "No truncation reported" isn't a reliable signal for any of the three retrieval outcomes. The verification script and the
>saved file are the only authoritative record._
