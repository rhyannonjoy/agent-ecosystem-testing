---
layout: default
title: "Friction Note"
nav_order: 5
permalink: /docs/anysphere-cursor/friction-note
parent: Anysphere Cursor
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Cursor IDE vs VS Code

Cursor is a standalone IDE forked from VS Code's codebase, not a VS Code extension.
`@Web` is exclusive to Cursor and can't be accessed in VS Code or through extensions.
While there are many "Cursor-like" extensions available, this specific web fetch
functionality isn't available in VS Code.

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
Question: "What model is your default?"

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
Gemini API docs. Pro plan at $20/month succeeds but truncates at ~6KB (~1.5K tokens).

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

When adding `@Web [URL]`, Cursor fetches the content and attaches it to
the message context. The underlying mechanism is `web_search`, but from a user perspective,
invocation happens through `@Web`.

Results are logged with `method: @Web` to reflect the **_user-facing syntax_**, but the backend 
mechanism is `web_search`.

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
