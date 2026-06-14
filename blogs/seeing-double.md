---
layout: default
title: "Seeing Double"
permalink: /blogs/seeing-double
parent: Blogs
---

# Seeing Double

![Two identical computers smile with stars framing them](../static/assets/seeing-double.png)

AET research concerns remain capturing default behavior to assess documentation truncation
risk across the web. Each platform testing cycle offers opportunities to adapt to
changes and unique architectural constraints.
[The Codex framework](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/methodology)
is the fourth in a series of chat-based agent testing which builds on previous frameworks and adds a
deployment context comparison. Codex testing first felt expansive,
[LLM x Intelligence Matrix](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-desktop#llm--intelligence-matrix)
now restrive, [LLM Retirement](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-extension#llm-retirement),

How did we get to the logs?
Opportunity to capture more data, influenced process change in which run and log tests in batches
Previously I wasn't even looking at session output after they had ran, but that changed with the volume up
Among the version updates, I noticed that data had changed and started to poke around more. Noticed
session terminal execution details gone, cleaned up, timer drift.
[Autonomous Post-Hoc Session Alterations](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-desktop#autonomous-post-hoc-session-alterations)
but on the second track, there was doubling
[Autonomous Post-Hoc Session Double Rendering](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/friction-note-interpreted-extension#autonomous-post-hoc-session-double-rendering) and I dug in more.

## What the logs actually contain

Each rollout file interleaves two parallel streams describing one session. The `event_msg` records are the UI event
feed, what the panel renders live. The `response_item` records are the model-facing conversation transcript, the
message objects that get replayed as context. When the agent emits its final answer, Codex writes it once to each
stream, and the `task_complete` event carries the full text a third time as `last_agent_message`. One generation,
three stored copies.

## The audit

A small Python script parses each file and counts everything: turns, emissions, tool calls, completion events, and
any record appended after `task_complete`. Across all eight sessions, spanning two models, four reasoning levels,
zero to twelve tool calls, and 25 to 233 seconds of runtime:

1. Every session contains exactly one final answer emission.
2. All three stored copies are byte-identical in every session.
3. Zero records exist after `task_complete` in any session. The file's wall clock span equals the turn duration
   exactly, so the log closes at completion and nothing touches it afterward.

The doubling reproduced in the panel for all eight runs. The invariant held in the transcript for all eight runs.
Whatever duplicates the report lives downstream of the log writer, in the client's render path. The likeliest
mechanism given the file structure: the panel hydrates the final message from two of its three stored copies,
probably the live event stream plus `task_complete.last_agent_message`, without deduplicating by ID.

The timer drift resolves the same way. The completion event carries `duration_ms` as the authoritative turn length,
and it ran 4 to 10 seconds longer than the live counter in every session. Two instruments, one reconciliation, no
mystery. The simplest failing case is a 38 second session with zero tool calls and 18,002 total tokens, so nothing
about session complexity is required to trigger any of it.

## What the audit caught that the panel couldn't

One run's report cut off mid-sentence, ending inside item 7 of an eight-item report with an unclosed backtick. The
transcript shows the same truncation in all three copies. So that one was real: the generation itself stopped, the
durable record agrees with the screenshot, and no later process repaired it. Distinguishing a rendering artifact
from a genuine generation failure is exactly what the runtime screenshot alone couldn't do, and the JSONL settles
it per run.

The wrappers around tool outputs settled a second standing question. Every `function_call_output` carries an
`Original token count` field, and when output is clipped before entering the model's context, the arithmetic is
exact: one run's `curl` output arrived at 144,804 tokens and kept exactly 10,000; another arrived at 118,359 and
kept exactly 2,000. What renders in the panel as a display truncation marker is actually a configured context
injection budget, which is why an agent can correctly measure a 145,000 token payload while its session consumes a
fraction of that. The retrieval layer and the context layer are decoupled by design, and the logs carry the budget
math even though the clipped content is gone.

## Practitioner takeaways

1. The duplicate reports and timer drift on the Codex VS Code extension are presentation-layer behavior. Your
   session data is intact, and the rollout file is the arbiter.
2. Don't trust the panel as a record of what the agent did. Trust it as a record of what rendered, and reconcile
   against `~/.codex/sessions` when the two might differ.
3. Tool output entering model context is budgeted in exact token amounts that the logs disclose per call. If your
   agent's behavior depends on seeing large tool outputs, it isn't seeing them, and the wrapper tells you precisely
   how much it saw.
4. Reasoning blocks in the rollout are encrypted, but their lengths and the cumulative `total_token_usage`
   checkpoints survive as effort proxies, useful on a surface that exposes little else.

The audit and decoder scripts are small, dependency-free Python and run against any rollout file. The bug itself
belongs to OpenAI's extension render path; everything needed to reproduce and localize it is in the logs their own
client writes.
