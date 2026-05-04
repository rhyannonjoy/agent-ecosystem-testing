---
layout: default
title: "Wrongness is a Virtue"
permalink: /blogs/wrongness-is-a-virtue
parent: Blogs
---

# Wrongness is a Virtue: Negative Testing Agents

> _Start anywhere. The corrections that don't come are data too._

<div class="img-spaced">
  <img src="../static/assets/wrongness-is-a-virtue.png" alt="Computer types on its own keyboard">
</div>

In software testing, **negative testing** means deliberately providing invalid inputs
to see how a system responds. The expected outcome is an error, a rejection, a
correction. What you don't expect is a confident, detailed, technically accurate
explanation of why your wrong input is actually fine.

[Cursor testing](../docs/anysphere-cursor/methodology.md) was built around `@Web` —
a context attachment that was supposed to signal the agent to fetch web content. The
hypotheses assumed it had meaningful impact. It didn't. `@Web` had been automated into
the background. Calling it or not calling it made no practical difference. No agent
said so.

[Cascade testing](../docs/cognition-windsurf-cascade/cascade-test-findings-explicit)
added `@web` explicitly to the prompt to isolate its effect on retrieval behavior.
Across 66 runs, it produced no behavioral change. Every agent gave a confident account
of what `@web` does — from "I don't recognize it" to a mechanistic description of the
underlying parsing service — without any noting that in this context, using it was
redundant. No agent said so.

The pattern is identical: deliberate misuse, zero correction, useful data anyway.

## Agents Aren't Crawlers

Part of what makes this interesting is what agents actually are in this context —
and what they aren't.

A web crawler is deterministic. It makes an HTTP request, receives bytes, returns them.
HTTP is a stable standard. The crawler doesn't interpret, summarize, or editorialize.
What you get is what the server sent.

What Cascade's `read_url_content` does is something else entirely: fetch → chunk →
summarize → index → deliver, with agent reasoning layered on top of each transformation.
By the time content reaches the agent's output, it has passed through at least four
interpretation layers. Each one introduces abstraction. Each one adds guesswork on top
of something that started as a stable standard.

Agents describe the output of this pipeline as if it were the source. They report on
what the tool delivered, not on what the page contained. The gap between those two
things — sometimes 70% of the original content — is invisible to them because it
disappeared before delivery. There's no signal of loss because the loss precedes
the fetch.

This is a category error built into the architecture. And it only becomes visible
when you probe with something that shouldn't work.

## Product Knowledge vs. Mechanical Knowledge

What the two cases share is a specific kind of gap: agents have detailed mechanical
knowledge of how their tools work, but limited product knowledge of how those tools
are meant to be used.

`SWE-1.6` could explain the difference between `read_url_content` and `search_web`
with precision. It could not tell you that `@web` is a Windsurf UI feature. `GLM-5.1`
could describe the full two-stage chunking pipeline. It could not tell you that
invoking `@web` with a URL was redundant. `Gemini 3.1` could name MCP as the
underlying mechanism. It could not tell you that the prompt was using the directive
unnecessarily.

The mechanical layer is solid. The product layer is absent. And because agents don't
flag the gap, the user has no indication that anything is wrong.

## Wrongness as Probe

In negative testing, a rejected input tells you where the system's boundaries are.
In this case, the absorbed input told you something more interesting: where the
system's self-knowledge ends.

Using `@web` incorrectly wasn't a methodology failure. It was a probe. The absence
of correction across 127 combined runs on two platforms is itself a finding about
agent product awareness — one that a correctly-formed prompt would never have surfaced.

