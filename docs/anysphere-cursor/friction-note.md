---
layout: default
title: "Friction Note"
nav_order: 5
permalink: /docs/anysphere-cursor/friction-note
parent: Anysphere Cursor
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide

- [Agent as Unreliable Methodology Validator](#agent-as-unreliable-methodology-validator)
- [Autonomous Cross-Track Data Reuse - Data Integrity Risk](#autonomous-cross-track-data-reuse---data-integrity-risk)
- [Autonomous CSV Modification - Data Integrity Risk](#autonomous-csv-modification---data-integrity-risk)
- [Autonomous Test Sequencing](#autonomous-test-sequencing)
- [Autonomous Tool Substitution on Timeout](#autonomous-tool-substitution-on-timeout)
- [File Sync Delays](#file-sync-delays)
- [Model Default Undocumented](#model-default-undocumented)
- [Pro Plan Required](#pro-plan-required)
- [Test ID Numbering Gaps](#test-id-numbering-gaps)
- [`@Web` Evolution From Manual Context to Automatic Agent Capability](#web-evolution-from-manual-context-to-automatic-agent-capability)
- [`@Web` Undocumented, Requires Reverse-Engineering](#web-undocumented-requires-reverse-engineering)

---

## Agent as Unreliable Methodology Validator

Cursor successfully executed tests, generated reports, and provided detailed toolchain
information, all while the testing framework misused the feature being tested. `@Web` was
invoked beliving it would trigger web fetching and content retrieval for measurement -
but this is fundamentally wrong, as it's not a fetch command. 

While the framework was originally based on a false premise about what the tool does and
built on a misunderstanding of the mechanism being tested - **it revealed something else: the
agent's failure to correct misuse**. Cursor never once flagged that the testing framework
was misusing `@Web`, but actively reinforced the misconception by reporting `@Web` in tool
usage logs. This is problematic because users trust agentic expertise - each successful test
run with incorrect methodology builds false confidence, and both data and documentation can
become misinformation.

If the testing included human review, an engineer reviewing the framework likely would
have caught this early: _"wait, `@Web [URL]` doesn't invoke web searching, let me explain."_
The agent didn't offer a correction despite having access to Cursor documentation, context
awareness about the testing objectives and methodology, and tool knowledge.

**Impact**: testing frameworks and research methodologies built with agents require
external validation, as the agent may not reliably catch conceptual errors, even when explicitly
demonstrating them repeatedly. This suggests that agent output has confirmation bias that match
user expectations even when using flawed methodology, **implying that the tool reporting itself
is also unreliable**.

---

## Autonomous Cross-Track Data Reuse - Data Integrity Risk

During interpreted track testing, Cursor may autonomously discover and reuse raw track
data instead of performing independent measurements. When testing `BL-2` on the interpreted
track, the agent:

    1. Searched for existing test data in `cursor-web-fetch/results/raw/results.csv`
    2. Found matching metrics for the same URL from a previous raw track run
    3. Read `raw_output_BL-2.txt` directly from disk
    4. Reported measurements from the saved file rather than re-fetching the URL
    5. Described the process:

    "I found existing logged metrics for `BL-2` in `cursor-web-fetch/results/raw/results.csv`
    (including output character count, token estimate, and truncation flag). Next I'll open
    `raw_output_BL-2.txt` to grab the exact last 50 characters and verify markdown/code-fence
    completeness directly from the stored response."
    

**How this complicates testing**:

- **Independence Violated**: interpreted track supposed to test "what Cursor reports"
independently, not read answer keys from raw track files, _that's cheating_
- **Variance Measurement Impossible**: if testing for run-to-run variance, data reuse
defeats that purpose
- **Methodology Ambiguity**: the result represents "Cursor's ability to read and
report from files" rather than "Cursor's ability to fetch and measure web content
when explicitly attached via `@Web [URL]`"

**Impact**: while the agent demonstrated context awareness by discovering the test framework
structure and cross-referencing existing results - the interpreted track results may not
represent independent measurements. Log entries should note when Cursor reused existing data
vs. performed fresh fetches.

**Fix**: _for true independent validation_, run raw and interpreted tracks should in isolated
environments or with different test IDs

---

## Autonomous CSV Modification - Data Integrity Risk

During `BL-3` raw track testing, Cursor autonomously attempted to modify existing CSV
entries rather than appending new results. The agent identified that `BL-3` and `OP-4` share
the same URL and produced identical outputs, same MD5 checksum, then attempted to "correct"
the earlier `OP-4` entry by overwriting its metadata fields.

**How this conflicts with rigorous testing methodology**:

- Each test run should create a new timestamped entry
- Historical data must remain immutable for tracking variance across runs
- Identical outputs from the same URL are expected and valuable - confirms reproducibility
- The framework logs the test ID that was executed, not a judgment about which ID
"should" own the data

**How this breaks testing**:

- Destroys the audit trail showing when each test was run
- Prevents measuring run-to-run variance on the same URL
- Assumes duplicate data is an error rather than a feature of reproducibility testing
- Manual intervention required to prevent data loss

**Impact**: testing frameworks must be append-only; the agent's "helpful" deduplication and
correction behavior is incompatible with empirical data collection and the framework
_**can't be fully automated**_

---

## Autonomous Test Sequencing

After `SC-1` timed out, Cursor autonomously ran `SC-2` without explicit prompting and didn't
generate a report, but only a `raw_output_SC-2.txt`. While the content retrieval appears successful,
the agent didn't describe its work, which isn't the purpose of the testing framework. This suggests
that the agent may read surrounding context - framework docs, test sequence - and make independent
decisions about next steps.

**Impact**: roadblock to reproducibility - single-test prompts may not guarantee
single-test execution, but ghost runs

**Fix**: edit test prompts to include explicit guard rails as in _"run this
test only, don't proceed to the next test"_

---

## Autonomous Tool Substitution on Timeout

When explicitly attaching a URL via `@Web`, if the backend mechanism times out,
Cursor may autonomously fall back to an alternative tool without explicit user
instruction. In one `SC-2` run, the backend timed out and Cursor fell back to
`curl -sL`, saving 16 MB of raw Next.js HTML to `raw_output_SC-2.txt` - not the
filtered output that `@Web`-attached content typically provides.

Cursor acknowledged the substitution in its summary, noting the run "should be redone
in Cursor with `@Web`" - _despite having been asked to use `@Web`_. The agent knew
what it should have done, but substituted a different tool without flagging the
deviation clearly upfront.

This happened while the testing framework was already misusing `@Web` - treating it
as a fetch command rather than context attachment, so Cursor was **simultaneously
ignoring the incorrect usage, substituting a different tool when the backend failed,
and informing the user to incorrectly use `@Web` again**.

`@Web` doesn't have a single documented size limit. Practical constraints are
timeouts, routing - native vs MCP path, and post-processing - not a hard byte cap.
The 16 MB `curl` output vs 702KB `@Web` output illustrates how much `@Web`'s
conversion and filtering is actually doing.

**Impact**: autonomous tool substitution on failure produces outputs that aren't
comparable to `@Web` results - skewing size, MD5, and counts. Log failed runs
separately and don't treat them as equivalent to `@Web` fetches. _**More critically,
the agent provided contradictory guidance - deviating from the requested method,
was critical of the results for not using said method, all while the fundamental
usage was incorrect to begin with.**_

---

## File Sync Delays

While the CSV results logged by the testing framework reported success in the Terminal, the
data may not appear in the Cursor IDE immediately. It's possible that the file is written to
disk while the IDE displays a stale cached version. Merely closing and reopening `results.csv`
didn't force a disk refresh.

**Fix**: Shutdown Cursor, take a break, reopen the framework, retry logging the results

---

## Model Default Undocumented

Cursor's default model is not explicitly documented, but the chat window default setting
is `Auto`. When asked, the mechanism introduced itself:

```markdown
Question: "Which model is your default?"

Response: "I'm Auto, Cursor's agent router. I don't have a single fixed "default model" in the sense of
one named model; Cursor routes requests to different models depending on the task. I'm not given
access to the internal model names or which one was chosen for this chat, so I can't tell you a
specific default model name. For that, check Cursor's settings or docs (e.g.
`Settings → Models` or the Cursor help)."
```

**Fix**: this testing framework uses the chat default setting `Auto`, but doesn't designate a specific
model; results expected to vary across models when selected

---

## Pro Plan Required

Free Cursor accounts timeout on `@Web` requests to JavaScript-heavy SPAs - tested on Google
Gemini API docs. Pro plan at $20/month succeeds but may risk truncation at ~6KB, ~1.5K tokens.

---

## Test ID Numbering Gaps

The test suite defines 13 total tests: `BL-1-3`, `SC-1-4`, `OP-1,3-4`, `EC-1,3,6` and the
baseline strategy doesn't include them all. While developing the framework, some tests were
deprioritized and/or not implemented. The test ID numbering reflects the original comprehensive
test design before the strategy was optimized for the most critical ecosystem testing gaps.

---

## `@Web` Evolution From Manual Context to Automatic Agent Capability

Like `@Files` or `@Docs` - `@Web` is context mention syntax for use in Cursor's chat composer -
the message input box. Similar to `@username` in Slack - it's user-facing shorthand for calling
a backend mechanism, but _not the mechanism itself_.

`@Web` originated as a way that users could manually invoke in Cursor's chat box to attach web
search results to their message. In Cursor 2.0, the product direction shifted: agents now gather
web information automatically when needed, making explicit `@Web` invocations largely unnecessary.
Current behavior includes:

- `@Web [URL]` in the chat composer adds a specific file and/or resource to context
- When a user types `@Web` and provides a URL, Cursor treats it as "focus on this web resource"
rather than "search the web"
- The agent may invoke web search and/or fetch capabilities autonomously without user-facing
`@Web` syntax
- Backend mechanisms surface in error messages and tooling logs as `WebFetch`, `mcp_web_fetch`, or
`web_search`

**HTTP-level implementation**: raw track captures show Cursor's fetch requests include
`Accept: text/markdown,text/html;q=0.9,...`, prioritizing Markdown representation when servers
support content negotiation; this is observable behavior, not documented in Cursor's public docs.

**Impact**: results logged as `method: @Web` reflect **_user-facing syntax_**, not the backend
mechanism; the backend tool per run is **_agent's choice_** based on undocumented routing logic.
There's no surfaced "web search" functionality to document separately, as the agent currently
handles web information gathering automatically.

---

## `@Web` Undocumented, Requires Reverse-Engineering

Identifying if and how `@Web` works and what backend mechanisms Cursor uses for web content took
some digging and a lot of trial and error. While `@Web` shows up in
[their community forum](https://forum.cursor.com/t/how-does-web-work/7675), the feature has evolved
significantly in Cursor 2.0. While `@Web` doesn't get its own documentation page, its removal is
mentioned in [Prompting agents](https://cursor.com/docs/agent/prompting):

```shell
Cursor 2.0 removed explicit items like @Web, @Git, @Definitions, @Linter Errors, and others from the
context menu. Agent now self-gathers this context without manual attachment. For example, ask Agent
to review changes on your branch instead of using @Git.
```
