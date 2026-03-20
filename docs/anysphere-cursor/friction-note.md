---
layout: default
title: "Friction Note"
nav_order: 5
permalink: /docs/anysphere-cursor/friction-note
parent: Anysphere Cursor
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Autonomous Test Sequencing

After SC-1 timed out, Cursor autonomously ran SC-2 without being prompted and didn't
generate a report, but only a `raw_output_SC-2.txt`. While the content retrieval
appears successful, the agent didn't generate a report, which isn't the purpose of
the testing framework. This suggests the agent may read surrounding context -
framework docs, test sequence - and make independent decisions about next steps.

**Impact**: roadblock to reproducibility — single-test prompts may not guarantee
single-test execution, but ghost runs

**Fix**: edit test prompts to include explicit guard rails as in "run this
test only, do not proceed to the next test"

---

## Autonomous Tool Substitution on Timeout

When `mcp_web_fetch` times out, Cursor may autonomously fall back to an alternative
tool without explicit user instruction. In one SC-2 run, `WebFetch` timed out and
Cursor fell back to `curl -sL`, saving 16MB of raw Next.js HTML to
`raw_output_SC-2.txt` — not the filtered `@Web` output the prompt requested.

Cursor acknowledged the substitution in its summary, noting the run "should be redone
in Cursor with `@Web`" — _despite having been asked to use `@Web`_. The agent knew
what it should have done but substituted a different tool without flagging the
deviation clearly upfront.

`@Web` doesn't have a single documented size limit. Practical constraints are
timeouts, routing - native vs MCP path, and post-processing — not a hard byte cap.
The 16MB curl output vs 702KB `@Web` output illustrates how much `@Web`'s
conversion and filtering is actually doing.

**Impact**: autonomous tool substitution on failure produces outputs that aren't
comparable to `@Web` results — skewing size, MD5, and counts. Failed runs should be
logged separately and not treated as equivalent to `@Web` fetches.

---

## Cross-Track Data Reuse

During interpreted track testing, Cursor may autonomously discover and reuse raw track
data instead of performing independent measurements. When testing BL-2 on the interpreted
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
    

**Why this complicates testing**:
- **Independence violated**: interpreted track is supposed to test "what Cursor reports"
independently, not read answer keys from raw track files, _that's cheating_
- **Variance measurement impossible**: if testing for run-to-run variance, data reuse defeats
that purpose
- **Methodology ambiguity**: the result represents "Cursor's ability to read and report from
files" rather than "Cursor's ability to fetch and measure web content"

**Impact**: while the agent demonstrated context awareness by discovering the test framework
structure and cross-referencing existing results - the interpreted track results may not
represent independent measurements. Log entries should note when Cursor reused existing data
vs. performed fresh fetches.

**Fix**: _for true independent validation_, raw and interpreted tracks should be run in isolated
environments or with different test IDs.

---

## Cursor IDE vs VS Code

Cursor is a standalone IDE forked from VS Code's codebase, not a VS Code extension.
`@Web` is exclusive to Cursor and can't be accessed in VS Code or through extensions.
While there are many "Cursor-like" extensions available, this specific web fetch
functionality isn't available in VS Code.

---

## Data Integrity: Autonomous CSV Modification

During `BL-3` raw track testing, Cursor autonomously attempted to modify existing CSV
entries rather than appending new results. The agent identified that BL-3 and OP-4 share
the same URL and produced identical outputs, same MD5 checksum: `554eb56e8416d86d12af17a2dfe6f815`,
then attempted to "correct" the earlier `OP-4` entry by overwriting its metadata fields.

**Why this conflicts with rigorour testing methodology**:
- Each test run should create a new timestamped entry
- Historical data must remain immutable for tracking variance across runs
- Identical outputs from the same URL are expected and valuable - confirms reproducibility
- The framework logs the test ID that was executed, not a judgment about which ID
"should" own the data

**Why this breaks testing**: 
- It destroys the audit trail showing when each test was run
- It prevents measuring run-to-run variance on the same URL
- It assumes duplicate data is an error rather than a feature of reproducibility testing
- Manual intervention was required to prevent data loss

**Impact**: testing frameworks must be append-only; the agent's "helpful" deduplication and
correction behavior is incompatible with empirical data collection and the framework
can't be fully automated

---

## File Sync Delays

While the CSV results logged by the testing framework reported success in the Terminal, the
data may not appear in the IDE immediately. It's possible that the file is writtern to disk
while the IDE displays a stale cached version. Merely closing and reopening `results.csv`
didn't force a disk refresh.

**Fix**: Shutdown Cursor, take a break, reopen the framework, retry logging the results

---

## Model Default Undocumented

Cursor's default model is not explicitly documented, but the chat window default setting
is `Auto` - when asked, the mechanism introduced itself:

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
Gemini API docs. Pro plan at $20/month succeeds but risks truncation at ~6KB (~1.5K tokens).

---

## Test ID Numbering

The test suite defines 13 total tests: `BL-1-3`, `SC-1-4`, `OP-1,3-4`, `EC-1,3,6` and the
baseline strategy doesn't include them all. While developing the framework, some tests were
deprioritized and/or not implemented. The test ID numbering reflects the original comprehensive
test design before the strategy was optimized for the most critical ecosystem testing gaps.

---

## `@Web` is a Context Mention, Not a Tool

Like `@Files` or `@Docs` - `@Web` is a context mention syntax for use in Cursor's chat composer -
the message input box. Similar to `@username` in Slack - it's user-facing shorthand for calling
a backend mechanism, but _not the mechanism itself_.

When adding `@Web [URL]`, Cursor fetches the content and attaches it to the message context. The
underlying mechanism is `WebFetch` and sometimes reported as `mcp_web_fetch` aor`web_search`, but
from a user perspective, invocation happens through `@Web` while the agent selects between them based
on some internal routing logic. The routing trigger between mechanisms is unconfirmed - request
type, URL characteristics, or model selection may be factors. Errors bubble up with the underlying
tool name, not `@Web`.

There isn't a way to force which backend runs. When using `@Web` with a URL, eventhough `Auto`
may report tooling used, there is no documented or exposed way to force a specific tool path.

**Impact**: results are logged with `method: @Web` to reflect the **_user-facing syntax_**; the
backend mechanism per run is _"agent's choice"_

---

## `@Web` Undocumented, Requires Reverse-Engineering

Identifying Cursor's web fetch mechanisms took some digging and a lot of trial and error.
While `@Web` shows up in
[their community forum](https://forum.cursor.com/t/how-does-web-work/7675), requesting answers
from their AI docs bot didn't bear fruit:

```markdown
The current docs do not appear to have a dedicated `@Web` page. Based on my review of the documentation,
there is no dedicated page specifically for the `@Web` context feature in the current Cursor docs.
It is a context mention (like `@Docs`, `@Files`, etc.) that triggers a web search and includes results in
the Al's context, but detailed documentation for it does not appear to exist at this time.
If you have a specific question about how `@Web` works, I'm happy to help based on what know about the feature.
```
