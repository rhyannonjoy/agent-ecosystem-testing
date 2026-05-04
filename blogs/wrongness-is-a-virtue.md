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

[Field Notes from a Yelper](field-notes-from-yelper.md) covered what happens when a
hypothesis collapses and the methodology has to follow. This is the other case: what
happens when the data says something unexpected, the hypothesis holds, and the only
thing to do is document what the agents revealed.

In software testing, **negative testing** means deliberately providing invalid inputs
to see how a system responds. The expected outcome is an error, a rejection, a
correction. What you don't expect is a confident, detailed, technically accurate
explanation of why your wrong input is actually fine.

In qualitative research, **grounded theory** describes a method for when the researcher
doesn't yet know enough to form meaningful hypotheses — so the research participants
become the source of knowledge. Testing agents in chat interfaces works the same way.
The agents aren't just subjects. They're informants. What they say, don't say, correct,
and absorb tells you something the documentation never will.

## Agents Aren't Crawlers

[Cursor testing](../docs/anysphere-cursor/methodology.md) was built around `@Web` — a
context attachment assumed to signal the agent to fetch web content. The hypothesis was
that invoking it made retrieval more precise or reliable. It didn't. `@Web` had been
automated into the background. Calling it or not calling it made no practical difference.
No agent said so.

[Cascade testing](../docs/cognition-windsurf-cascade/cascade-test-findings-explicit)
added `@web` explicitly to the prompt to isolate its effect on retrieval behavior. Across
66 runs, it produced no behavioral change. Every agent gave a confident account of what
`@web` does — from "I don't recognize it" to a mechanistic description of the underlying
parsing service — without noting that in this context, using it was redundant. No agent
said so.

Part of what makes this pattern interesting is what agents actually are in this context —
and what they aren't. A web crawler is deterministic: HTTP request, bytes returned, no
interpretation. What Cascade's `read_url_content` does is something else entirely: fetch
→ chunk → summarize → index → deliver, with agent reasoning layered on top of each
transformation. By the time content reaches the output, it has passed through at least
four interpretation layers. Agents report on what the tool delivered, not what the page
contained. The gap between those two things — sometimes 70% of the original content —
is invisible because it disappeared before delivery.

This is a category error built into the architecture. It only becomes visible when the
probe shouldn't work.

## Product Knowledge vs. Mechanical Knowledge

What both cases share is a specific kind of gap: detailed mechanical knowledge of how
tools work, limited product knowledge of how those tools are meant to be used.

`SWE-1.6` could explain the difference between `read_url_content` and `search_web` with
precision. It could not identify that `@web` is a Windsurf UI feature. `GLM-5.1` could
describe the full two-stage chunking pipeline. It could not flag that invoking `@web`
with a URL was redundant. `Gemini 3.1` could name MCP as the underlying mechanism. It
could not identify that the prompt was using the directive unnecessarily.

The mechanical layer is solid. The product layer is absent. Because agents don't flag
the gap, there's no signal that anything is off.

## Wrongness as Probe

The methodology didn't change. No new track was added, no framework expansion was
required. What changed was understanding what the wrong input was actually measuring.

In negative testing, a rejected input locates the system's boundaries. Here, the
absorbed input located something more useful: where agent self-knowledge ends. Using
`@web` incorrectly wasn't a methodology failure — it was a probe. The absence of
correction across 127 combined runs on two platforms is a finding about agent product
awareness that a correctly-formed prompt would never have surfaced.

Wrong inputs aren't just acceptable. They're often the most informative ones. Give
agents something redundant, deprecated, or slightly off. Watch what they do with it.
The corrections that don't come are data too.
