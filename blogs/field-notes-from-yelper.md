---
layout: default
title: "Field Notes from a Yelper: Testing Agents Without a Lab"
permalink: /blogs/field-notes-from-a-yelper
parent: Blogs
---

# Field Notes from a Yelper: Guerrilla Testing Agents

> _Start anywhere, be wrong. Catching a false premise is when the real testing begins._

![Computer types on its own keyboard](../static/assets/field-notes-from-yelper.png)

What happens when the data pulls the rug out from under the hypotheses? Adapt. Then adapt again.
And again. Eventually, the methodology itself becomes the finding.

AET, the [Agent Ecosystem Testing](https://github.com/rhyannonjoy/agent-ecosystem-testing) project,
began as a programmatic extension of
[Dachary Carey's Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/)
in support of the [Agent-Friendly Documentation Spec](https://agentdocsspec.com/). AET
started with a basic question: _what actually happens between "agent fetches a URL" and
"user sees output?"_

It's like Yelping for agents: use a product, note what's there. The value isn't entirely in
controlled conditions or peer-reviewed reproducibility. It's in the honest record: here's what was
expected and here's what the data said instead.

## Premise Collapse

The methodology was initially a two-track approach: **interpreted** captures model self-reports 
while **raw** produces citable metrics. Some testing frameworks inspected API responses directly, while
others use intentionally unautomated, chat-based measurements through interaction and no direct code
instrumentation. Testing closed-consumer applications expose all sorts of complications that make it
difficult to extract meaningful data, and output variance is just the tip of the iceberg.

While reproducibility is a design goal, it's not guaranteed. Running the same test twice and getting
meaningfully different results is expected - retrieval depth, content transformation, and self-reported
behavior may all vary across sessions. This isn't necessarily a testing flaw, but it's a finding
worth documenting.

[Cursor testing](../docs/anysphere-cursor/methodology.md) posed a particular challenge. The hypotheses
were built on the assumption that attaching `@Web` to a context window had some meaningful impact on
whether the agent successfully retrieved content from the web - possibly making the prompting more precise
and effective. This turned out to be completely false. The feature had been automated into the background.
While `@Web` was an acceptable invocation, it no longer had any functional impact. Calling it or not calling
it made no practical difference. The agent was fetching from the web either way. On one hand, maybe the signs
were there. `@Web` has no dedicated documentation outside of some old community forums, but on the other hand,
no model called out this unnecessary invocation.

This meant necessary reframing of the Cursor findings - framework reference, tool chain data, all of it
had to be re-evaluated and re-contextualized. It wasn't a failure, but a correction. The
data wasn't wrong, only the premise. The revised [Cursor Friction Note](../docs/anysphere-cursor/friction-note.md)
is better for it.

## No Docs, No Anchor

[Gemini API URL context](https://ai.google.dev/gemini-api/docs/url-context) testing caught documentation gaps.
Some hard limits were reinforced, while other assertions proved less accurate. The expectation was that Gemini
wouldn't be able to describe a YouTube video, but it very confidently reported
[Rick Astley's "Never Gonna Give You Up."](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

[Copilot testing](../docs/microsoft-github-copilot/methodology.md) posed a different challenge. It wasn't a
false premise, but the absence of a premise. There's no documented web fetch behavior to anchor hypotheses against -
forcing the framework to expand into something more exploratory and less hypothesis-driven. The framework instead
instrumented-around this absence: more logging, inference, and separation between what the model reports and what
the data actually demonstrates. Two retrieval mechanisms surfaced during testing: an agent-routed `fetch_webpage`
that returns relevance-ranked excerpts, and a `curl` path that retrieves byte-perfect full content. Very different
behaviors. Neither documented. When the platform doesn't document how it works, the testing framework has to do more
of the talking.

## Natural Methodology Evolution

The methodology didn't start with a roadmap, but accumulated one. While the
[Claude API web fetch testing](../docs/anthropic-claude-api-web-fetch-tool/methodology.md)
established a baseline and two-track structure, Cursor introduced the problem of opaque, undocumented functionality
and false premise correction. Copilot forced the framework to expand when tool visibility was absent. Unlike Cursor
and Copilot, [testing Windsurf's Cascade](../docs/cognitition-windsurf-cascade/methodology.md) requires another
framework expansion in the form of a new track in which `@web` is called directly. This brings the testing
framework track number to three:

  1. Cascade-interpreted: model self-reports
  2. Raw: programmatically verified metrics
  3. Explicit: `@web` directive called directly, behavior isolated

The platform testing order was also not plannned and organically grew out of each testing session's findings -
revealing what users can and can't observe, what instrumentation is required to surface it, and each testing platform
is a response to the last one.

## Start Guerrilla Testing Agents

> _Start anywhere and iterate honestly. The data will do the rest._

Output variation is a given, platforms may remain opaque, and documentation can be sparse. The goal isn't a tidy
conclusion, but getting comfortable moving through uncertainty and taking notes along the way. No lab coat
required. Some tips:

1. Test something specific: _"how does this agent fetch URLs?"_ is specific while _"is this agent good?"_ is well, less good
2. Wrong hypothesis beats no hypothesis: false premises can be corrected, no premise may require expensive framework expansion
3. Keep model self-reporting and raw output separate: they diverge more often than one might expect
4. Let constraints shape methodology: no docs, no problem - instrument around it
5. Over-document: log more than seems necessary, especially for chat-based interactions
