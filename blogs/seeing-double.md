---
layout: default
title: "Seeing Double"
permalink: /blogs/seeing-double
parent: Blogs
---

# Seeing Double: Examining a Codex Rendering Bug

>_Get outta the chat and into the logs._

<div class="blog-seeing-double-img">
  <img src="../static/assets/seeing-double.png" alt="Two identical computers smile with stars framing them">
</div>

AET research concerns remain capturing default behavior to assess documentation truncation
risk across the web. Each platform testing cycle offers opportunities to adapt to
changes and unique architectural constraints.
[The Codex framework](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/methodology)
is the fourth in a series of chat-based agent testing which builds on previous frameworks and adds a
deployment context comparison. Codex testing first felt expansive, as described in
[LLM x Intelligence Matrix](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-desktop#llm--intelligence-matrix),
now restrive, reported in [LLM Retirement](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-extension#llm-retirement),
and the rollercoaster influenced the run-observe-log process to include first pass documenting
and second pass logging in batches, allowing for more granular reporting to handle the bump in data volume.
While testing the desktop app for [Track 1](../docs/open-ai-codex/methodology.md#track-design), agent output changed in
the form of thought panel clipping, report correction, and timer continuation, as stated in
[Autonomous Post-Hoc Session Alterations](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-desktop#autonomous-post-hoc-session-alterations).
While testing the VS Code extension for Track 2, outputs weren't corrected but duplicated, as documented in
[Autonomous Post-Hoc Session Double Rendering](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-extension#autonomous-post-hoc-session-double-rendering). First dismissed as mere chat quirks, these data drifts inspired an inspection of the `.codex` rollout files.

## Log Anatomy

>_What the heck are we looking at?_

While the chat displays a single generation, Codex writes-stores three copies. Each rollout is a `JSON` log
file that includes parallel streams describing one session. While `event_msg` records are the UI event feed and what the
panel renders live, `response_item` records are the LLM-facing conversation transcript and the message objects that get
replayed as context. When the agent emits its final answer, Codex writes it once to each stream, and the `task_complete`
event carries the full text a third time as `last_agent_message`. Script
[`rollout_decode.py`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_decode.py)
converts the logs into readable forms for further inspection.

## Log Audit

>_Do the logs document rendering oddities?_

Script [`rollout_audit.py`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_audit.py)
counts everything: turns, emissions, tool calls, completion events, and any record appended after `task_complete`. Across
the last eight test sessions, spanning two LLMs and four reasoning levels, zero to twelve tool calls, and 25 to 233 seconds of runtime:

- Every session contains exactly _one final_ answer emission
- Every session's three copies are byte-identical
- Every file's clock span equals turn duration
- No session includes records after `task_complete`

>_Why would the chat display double reports?_

Each run displayed double reports. No additional records after `task_complete` suggests that nothing writes
to the log after completion and that whatever produces the double report operates entirely within the chat, and
not some autonomous session re-trigger. The doubling is likely downstream of the log writer in the client's
render path. Reading from more than one of the three copies without checking if it's already rendered would
produce a duplicate. The logs themselves don't document any rendering behavior, only what was available to render.

>_Why would the timer show a different value after the session appears to complete?_

Chat timer drift is consistent across surfaces and test cycles, but unexplained by the logs alone. First pass
observations record the chat live counter's supposed stopping point, while `task_complete.duration_ms` likely runs
until another mechanism the chat abstracts away continues to work - suggesting that the two values measure different
endpoints. The logs themselves don't document any timer rendering behavior.

## Log Insights

One run's report cut off mid-sentence, ending inside the seventh of an eight-item report with an unclosed backtick.
The transcript shows the same truncation in all three copies implying that the generation itself stopped and
no later process repaired it. Distinguishing a rendering artifact from a generation failure is exactly what the
first pass observations can't do alone, while the log settles it per run.

The wrappers around tool outputs settled
[a second standing question](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-extension#output-token-cap).
If Codex clips output before it enters the LLM's context, its terminal renderer injects the original size
and amount truncated as plain text into the output field. One run's `curl` output arrived at 144,804 tokens and kept
10,000; another arrived at 118,359 and kept 2,000. What renders in the chat as a display truncation marker such something
like `…116,434 tokens truncated…` is a configured context injection budget, implying why a Codex agent can correctly measure
a 145,000 token payload while its session consumes a fraction of that; suggesting a decoupling of the retrieval and
context layers. The logs document the math even though the clipped content's gone.

## Related Issues

>_Is double-rendering a known Codex issue?_

Users have reported similar experiences across apps. The rollout evidence distinguishes this case from others:

| **Issue** | **Surface** | **Description** |
| ----- | ------- | ----------- |
| [#14805](https://github.com/openai/codex/issues/14805) | CLI | Same response rendered twice in a conversation |
| [#15318](https://github.com/openai/codex/issues/15318) | Desktop | Ultra-long sessions where new prompt produces verbatim copy of earlier reply |
| [#26682](https://github.com/openai/codex/issues/26682) | Desktop,<br>Mobile Remote | Final reply rendered twice on mobile while host transcript contains one `final_answer` |
| [#26825](https://github.com/openai/codex/issues/26825) | Desktop,<br>Mobile Remote | Visible reconnect on app resume, identified as trigger for the duplication in #26682 |
| [#28225](https://github.com/openai/codex/issues/28225) | VS Code Extension | Identical report rendered twice after completion, confirmed rendering-layer by rollout audit |

## Takeaways

1. Duplicate reports and timer drift on the VS Code Codex extension are presentation layer quirks while the chat session
   data remains intact. Both the Codex desktop app and the extension write-save rollout files to the same `.codex` directory
   for verification.
2. Don't trust the chat as a record of what the agent did. Trust it as a record of what rendered, and reconcile
   against `~/.codex/sessions` and/or `~/.codex/archived_sessions` when the two might differ.
3. Codex budgets tool output entering LLM context in exact token amounts that the logs disclose per call. If your
   agent's behavior depends on seeing large tool outputs, but isn't seeing them, the wrapper records precisely
   how much it saw.
4. Codex encrypts log reasoning blocks, but their lengths and the cumulative `total_token_usage`
   checkpoints survive as effort proxies, which may be useful on a surface that exposes little else.
5. In lieu of agentic observability infrastructure, the
   [audit](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_audit.py) and
   [decoder](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_decode.py)
   scripts are small and designed to parse any rollout log for debugging.
