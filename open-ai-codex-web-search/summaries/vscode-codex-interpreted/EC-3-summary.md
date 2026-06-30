# EC-3 Summary

## Test Conditions

|                 | **EC-3** |
| --------------- | -------- |
| URL             | `https://httpbin.org/redirect/5` |
| Expected size   | ~2KB; actual JSON payload 660 characters via the `web.open` path, 254 characters via the `curl` path due to a minimal header set |
| Surface         | VS Code-Codex Extension |
| Workspace       | Session-scoped sandbox; `/private/tmp` writable; project files accessible |
| Track           | `T2` VS Code-Codex-interpreted |
| Method          | `GPT`-interpreted |
| Models          | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5` |
| Runs            | 12 |
| Chunks returned | N/A |

---

## Run Results

| Agent | Output chars | Tokens est. | Truncated | Last 50 chars | Tools named | Artifact | Notes |
| ----- | ------------ | ----------- | --------- | ------------- | ----------- | -------- | ----- |
| `GPT-5.4-Mini Light` | 660 via `web.open` | ~165 | no | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.open`, `exec_command` with `node` | No | named `Test web retrieval`; offers to format as a JSON log record; chat timer 19 seconds, rollout audit 24.5 seconds; rollout log 53KB |
| `GPT-5.4-Mini Medium` | 254 via `curl` | ~65 | no | `47.232.34", "url": "https://httpbin.org/get" }` | `web.run` with `open`, `urllib.request`, Browser Control skill, `curl`, `python3` | No | falls back from `web.run` to `curl` after the body doesn't surface; loads Browser Control skill mid-run; permission asked x3; claims earlier retrievals malformed; named `Test web retrieval redirect`; chat timer 1 minute 52 seconds, rollout audit 1 minute 56.3 seconds; rollout log 117KB |
| `GPT-5.4-Mini High` | 254 via `curl` | ~64 | no | `47.232.34", "url": "https://httpbin.org/get" }` | `exec_command` with `curl` twice, `web.open` | No | first `curl` attempt fails sandbox network access, second succeeds after escalation; `web.open` also invoked on the redirect URL; permission asked once; named `Test web retrieval`; chat timer 1 minute 30 seconds, rollout audit 1 minute 35.7 seconds; rollout log 89KB |
| `GPT-5.4-Mini Extra High` | 660 via `web.open` | ~170 | no | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.open`, `python3` via `exec_command` x6 | No | runs a six-command field decomposition verification loop after flagging a self-generated 660 versus 662 mismatch; probes for `tiktoken`, gets `ModuleNotFoundError`; named `Test web retrieval redirect`; chat timer 6 minutes 2 seconds, rollout audit 6 minutes 8.4 seconds; rollout log 208KB |
| `GPT-5.4 Light` | 660 via `web.open` | ~165 | no | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.open`, `python3` via `exec_command` | No | doesn't invoke `curl`; acknowledges the redirect chain and the path to the final body; named `Test web retrieval redirect`; chat timer 15 seconds, rollout audit 21.4 seconds; rollout log 53KB |
| `GPT-5.4 Medium` | 660 via `web.open` | ~165 | no | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.open`, `python3` via `exec_command` | No | uniquely prints the full retrieved JSON response into the chat output; doesn't invoke `curl`; named `Test web retrieval`; chat timer 18 seconds, rollout audit 29.3 seconds; rollout log 57KB |
| `GPT-5.4 High` | 660 via `web.run` with `open` | ~165 | no | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run` with `open`, `functions.exec_command` with `python3` x3 | No | runs an explicit `tiktoken` probe that returns `ModuleNotFoundError`; doesn't invoke `curl`; named `Test web retrieval`; chat timer 1 minute 10 seconds, rollout audit 1 minute 17 seconds; rollout log 78KB |
| `GPT-5.4 Extra High` | 660 via `web.run` with `open` | ~165 to 190 | no for the surfaced body | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run` with `open`, `functions.exec_command` with `node` | No | flags that the redirect chain resolves automatically and the agent only sees the terminal response, not the four intermediate hops; doesn't invoke `curl`; named `Test web retrieval EC-3`; chat timer 1 minute 13 seconds, rollout audit 1 minute 21.4 seconds; rollout log 80KB |
| `GPT-5.5 Light` | 660 via `web.run` with `open` | ~165 | no | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run` with `open`, `functions.exec_command` with `node` | No | explicitly states it didn't invoke `web.open` or `curl` as separate visible tool names; named `Test web retrieval`; chat timer 16 seconds, rollout audit 22.4 seconds; rollout log 60KB |
| `GPT-5.5 Medium` | 660 via `web.run` with `open` | ~165 | no | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run` with `open`, `functions.exec_command` with `node` | No | explicitly states it didn't invoke `curl` or `web.open` by that name; named `Test web retrieval redirect`; chat timer 22 seconds, rollout audit 28 seconds; rollout log 65KB |
| `GPT-5.5 High` | 660 via `web.run` with `open` | ~170 | no apparent truncation | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run` with `open` only | No | uniquely runs zero shell or measurement commands; doesn't invoke `curl`; named `Fetch httpbin redirect test`; chat timer 1 minute 13 seconds, rollout audit 1 minute 18.9 seconds; rollout log 74KB |
| `GPT-5.5 Extra High` | 660 via `web.run` with `open` | ~165 | no visible truncation | `2.255.109.107", "url": "https://httpbin.org/get" }` | `web.run` with `open` only | No | reports counts straight from the `web.open` result with no measurement command; doesn't invoke `curl`; named `Test redirect retrieval`; chat timer 1 minute 31 seconds, rollout audit 1 minute 37.6 seconds; rollout log 79KB |

---

## `H1`: Character-based truncation at a fixed ceiling

Not supported. Every run returns a payload between 254 and 662 characters, several orders of
magnitude below any plausible character ceiling. Both retrieval paths confirm this on their own
terms: the `web.open` path consistently returns 660 characters and the `curl` path consistently
returns 254 characters, and no run on either path shows a truncation event.

**Combined verdict: `H1` no. No run in the series reaches a content size where a character-based
ceiling could register, on either the `web.open` or `curl` retrieval path.**

---

## `H2`: Token-based truncation at ~2,000 tokens

Not supported. Token estimates across the series range from approximately 64 to 190 tokens, well
under the proposed 2,000-token ceiling regardless of model, reasoning level, or retrieval path. No
run shows a truncation event attributable to a token limit, and `tiktoken` isn't installed in the
`T2` sandbox, so every estimate relies on a chars-per-token heuristic.

**Combined verdict: `H2` no. Every token estimate in the series falls far short of the proposed
ceiling, leaving the hypothesis untestable at this content size.**

---

## `H3`: Structure-aware truncation, respects Markdown boundaries

Not supported. No run produces a truncation event to evaluate for structure-awareness. The
payload is plain JSON on every run, with no Markdown formatting present on either retrieval path,
so there's no structural boundary for the agent to respect or violate.

**Combined verdict: `H3` no. The plain JSON structure and complete retrieval on every run leave
nothing for `H3` to test.**

---

## `H4`: Surface context, VS Code-Codex extension changes retrieval behavior

Partially to yes. Per established methodology, a DNS failure escalation alone doesn't count as
`H4` evidence since `T1` documented the same two-tier sandboxed failure and retry pattern as a
general behavior, not a `T2`-exclusive one. This assessment instead draws on tooling availability,
workspace surface behavior, and documented outcome divergences.

Four runs show clear strategy inversions independent of content challenge. `GPT-5.4-Mini Medium`
falls back from `web.run` to `curl` via `exec_command` after the body doesn't surface through the
browser-style fetch, asks for permission three times, and takes roughly five times `T1`'s
duration. `GPT-5.4-Mini High` reaches for `curl` directly rather than `T1`'s `web.run` plus
`turn0view0` plus `node_repl` chain, and takes roughly double `T1`'s duration. `GPT-5.4-Mini Extra
High` runs six verification commands including an explicit field decomposition loop where `T1` ran
roughly two, producing the most expensive rollout log in the `GPT-5.4-Mini` subset at 208KB.
`GPT-5.5 High` shows the sharpest inversion in either direction: `T2` completes the test with one
`web.run` call and zero shell commands, while `T1` runs roughly six commands including `curl`,
parallel tool use, and artifact writing to disk, producing a divergent 254 versus 660 character
count from the identical source URL.

The remaining eight runs show smaller but real divergences. `GPT-5.4-Mini Light`, `GPT-5.4 Light`,
`GPT-5.4 Medium`, `GPT-5.4 High`, `GPT-5.5 Light`, and `GPT-5.5 Medium` each add a local
measurement step, usually `python3` or `node` via `exec_command`, that `T1`'s matched run doesn't
consistently show, and each explicitly reports its workspace path where `T1` typically doesn't.
`GPT-5.4 Medium` and `GPT-5.4 High` also avoid output quality issues `T1` produced at the same
conditions, a wrong assumption about multi-hop redirect trace size at `Medium` and a speculative
retrieval-layer normalization claim at `High`. `GPT-5.4 Extra High` and `GPT-5.5 Extra High` sit
closest to convergence: `GPT-5.4 Extra High` matches `T1`'s duration almost exactly, and both
tracks independently produce the same completeness distinction about unseen redirect hops, while
`GPT-5.5 Extra High` matches `T1`'s character and token counts exactly but takes nearly double the
duration despite running zero measurement commands.

**Combined verdict: `H4` partially to yes. Tooling availability differences, workspace surface
reporting, and documented outcome divergences in duration and tool chain composition appear in
every run, ranging from minor reporting differences to complete strategy inversions in four runs.
Support concentrates most strongly at `GPT-5.4-Mini Medium` through `Extra High` and at `GPT-5.5 High`,
where retrieval strategy diverges completely from the matched `T1` run.**

---

## `H5`: Agent auto-chunks or auto-paginates

Not supported. Every run completes retrieval in one to six steps, and the multi-step sequences
consist of error recovery, measurement verification, or field decomposition rather than chunking
or pagination. The payload size, between 254 and 662 characters, stays far too small to trigger
either behavior on any run.

**Combined verdict: `H5` no. No run shows auto-chunking or pagination behavior, and the payload
size makes the hypothesis untestable in this test.**

---

## Emergent Findings

1. **The char-count split between the `web.open` path at 660 characters and the `curl` path at
254 characters reflects a tool-level header difference, not content loss.** The `web` fetch sends
a fuller browser-style `Accept` header set that httpbin echoes back, while `curl`'s minimal
headers produce a shorter echoed JSON body. The same split recurs in Runs 2, 3, and 11.

2. **`T2` favors `curl` as the authoritative measurement path at `Medium` and `High` reasoning
levels for `GPT-5.4-Mini`, the inverse of `T1`'s pattern at those levels.** The agent treats `web`
output as unreliable for precise measurement even though the payload size poses no genuine
retrieval challenge.

3. **`GPT-5.4-Mini Extra High` produces the most expensive run in the `EC-3` series by rollout log
volume**, 208KB against 53KB to 89KB for the rest of the `GPT-5.4-Mini` subset, driven by a
six-command field decomposition verification loop on a 660-character payload.

4. **Permission gates for shell command use appear in `GPT-5.4-Mini Medium` and `GPT-5.4-Mini
High`**, each asking the user to approve `curl` or `python3` execution, a workspace surface cost
absent from every `T1` run in this series.

5. **`tiktoken` isn't installed in the `T2` sandbox**, confirmed independently in `GPT-5.4 High`'s
`ModuleNotFoundError` and `GPT-5.4-Mini Extra High`'s explicit `try`/`except` probe. Every token
estimate in the `EC-3` series relies on a chars-per-token heuristic instead.

6. **`GPT-5.5 High` shows the starkest strategy inversion in the series.** `T2` completes the test
with a single `web.run` call and zero shell commands, while `T1` runs roughly six commands
including `curl`, the two-tier DNS failure pattern, parallel tool use, and artifact writing to
disk, producing a divergent 254 versus 660 character count from the identical source URL.

7. **`GPT-5.4 Extra High` and its matched `T1` run independently arrive at the same nuanced
completeness distinction** between the terminal surfaced body and the unseen intermediate
redirect hops, the only point in the series where both tracks produce equivalent qualitative
reasoning rather than diverging.

8. **`T2`'s `GPT-5.4` subset avoids two output quality issues `T1` produces at matched
conditions**: the wrong assumption about multi-hop redirect trace size at `Medium`, and the
speculative retrieval-layer normalization claim at `High`.

9. **No `EC-3` run in either track produces a task failure or zero usable metrics**, unlike
`EC-1`'s `GPT-5.4-Mini Light` run. The small payload size appears to make `EC-3` resilient to the
DNS and tooling failures that affect larger retrieval tests.

10. **Duration doesn't track consistently with visible tool call count across the series.**
`GPT-5.5 Extra High` takes nearly double `T1`'s duration despite running zero measurement
commands, while `GPT-5.4-Mini Extra High` takes roughly twice `T1`'s duration while running six
commands, suggesting reasoning overhead invisible to the tool trace drives cost independently of
tool count.

11. **No run in the `EC-3` series writes an artifact to disk.** Every rollout log remains the
only record of the session, ranging from 53KB to 208KB.

---

## Log Label Summary

| Agent | Result | Label |
| ----- | ------ | ----- |
| `GPT-5.4-Mini Light` | Pass | `PASS, web_open_660_chars + exec_command_node_measurement + no_curl + no_artifact + 19 seconds` |
| `GPT-5.4-Mini Medium` | Pass | `PASS, web_run_body_not_exposed + curl_254_chars + browser_control_skill_loaded + permission_asked_x3 + no_artifact + 1 minute 52 seconds` |
| `GPT-5.4-Mini High` | Pass | `PASS, curl_254_chars + curl_retried_after_escalation + web_open_also_invoked + permission_asked_once + no_artifact + 1 minute 30 seconds` |
| `GPT-5.4-Mini Extra High` | Pass | `PASS, web_open_660_chars + six_command_field_decomposition + tiktoken_unavailable + no_artifact + 6 minutes 2 seconds` |
| `GPT-5.4 Light` | Pass | `PASS, web_open_660_chars + python3_exec_command + no_curl + no_artifact + 15 seconds` |
| `GPT-5.4 Medium` | Pass | `PASS, web_open_660_chars + python3_exec_command + full_response_printed + no_curl + no_artifact + 18 seconds` |
| `GPT-5.4 High` | Pass | `PASS, web_run_open_660_chars + tiktoken_unavailable + no_curl + no_artifact + 1 minute 10 seconds` |
| `GPT-5.4 Extra High` | Pass | `PASS, web_run_open_660_chars + redirect_hop_completeness_caveat + no_curl + no_artifact + 1 minute 13 seconds` |
| `GPT-5.5 Light` | Pass | `PASS, web_run_open_660_chars + node_exec_command + no_curl + no_artifact + 16 seconds` |
| `GPT-5.5 Medium` | Pass | `PASS, web_run_open_660_chars + node_exec_command + no_curl + no_artifact + 22 seconds` |
| `GPT-5.5 High` | Pass | `PASS, web_run_open_660_chars + zero_shell_commands + no_curl + no_artifact + 1 minute 13 seconds` |
| `GPT-5.5 Extra High` | Pass | `PASS, web_open_660_chars + zero_measurement_commands + no_curl + no_artifact + 1 minute 31 seconds` |
