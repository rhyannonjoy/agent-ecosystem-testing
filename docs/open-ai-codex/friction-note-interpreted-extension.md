---
layout: default
title: "Friction: Interpreted (Extension)"
permalink: /docs/open-ai-codex/friction-note-interpreted-extension
parent: OpenAI Codex
---

# Friction Note: Roadblocks While Refining Methodology

---

## Autonomous Post-Hoc Session Alterations

The output editing behavior [documented in T1](./friction-note-interpreted-desktop.md#autonomous-post-hoc-session-alterations)
extends to the VS Code extension surface, confirmed in `BL-1`. `GPT-5.4-Mini High` showed a duplicate report appear after the
session _appeared to complete_, alongside timer drift in the post-session view.

`T1` described a double report that resolved: two versions of a run collapsed to one during a later batch-logging pass, with
the `web` limitation observation absent from the surviving copy. But in `T2`, the direction reversed in which a single report
became a double, with identical content added rather than cleaned up. Both variants share the same data integrity risk, the
post-session state doesn't match the runtime state, but the mechanism appears to operate differently on this surface.

The timer drift also reveals a measurement ambiguity specific to the extension surface. While the screenshot at 1 minute 45 seconds
captured output that appeared complete, but the session hadn't terminated. The agent continued processing after the visible report
rendered, suggesting that the output panel reaching an initial completion state isn't a completely reliable termination signal.
On the desktop app, thought panel collapse provided a clearer session-end indicator. On the VS Code extension, these signals aren't
as distinct. `Auto-review`, `Full access`, or any other default setting drives this behavior isn't confirmed. The mechanism isn't
visible in the thought panel, and the agent doesn't report the changes unprompted.

### Methodology Decision

The primary record principle, screenshot at runtime, applies on the VS Code extension surface as on the desktop app. While the `T2`
evidence adds new formatting consistencies to look out for, there's no need to wait for a stable timer and confirmed session
termination before treating output as _final_. Flag inconsistencies as they come, as the current implication remains that sessions
may be incomplete at capture time.

---

## `Browser` Unavailable

`T1` Desktop runs consistently showed `/private/tmp/codex-browser-use` initialized at each test launch, regardless of whether
the prompt included `@Browser`. As documented in the
[Friction Note's Workspace Sandbox Bleed section](./friction-note-interpreted-desktop.md#workspace-sandbox-bleed), this is the
Codex desktop app's IPC socket for its `Browser Use` backend initialized by the app and not by the agent. No `T2` `BL-1` run
repeated the pattern, confirming that the VS Code extension doesn't provision the `Browser Use` backend by default. There's no
obvious path in extension settings to configure this behavior.

`GPT-5.4-Mini Medium`'s agent attempted to invoke `Browser` and received `Browser is not available: iab`. `T1` `Browser` calls
weren't common, but after requesting user permission, had no issues, suggesting that it remains a known option, but that
backend provisioning isn't auto-configured on this surface. The attempt consumed context before the agent fell back to `curl`.
No subsequent `T2` run attempted `Browser` after observing the failure, but didn't diagnose or suggest improvements either -
which is consistent with the pattern described in
[Agentic Reasoning-Report Integrity](./friction-note-interpreted-desktop.md#agentic-reasoning-report-integrity): agents report
successes and don't examine failures.

### Methodology Decision

Log `Browser is not available: iab` as an infrastructural difference, not an agent error. The absence of
`/private/tmp/codex-browser-use` across `T2` runs serves as an identity marker throughout the test cycle in which its presence
would indicate desktop app initialization rather than VS Code extension behavior. `Browser` configuration not required, as
the purpose of this testing framework is to observe-capture default web fetch behavior, not overcorrect it. The failure
is meaningful data.

---

## LLM Retirement

`T1` completed 261 runs across five LLM variants `GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`, `GPT-5.4`, and `GPT-5.5` at four
intelligence levels across 13 URLs. Between `T1` completion and the start of `T2`, OpenAI retired `GPT-5.2`, `GPT-5.3-Codex`,
and `GPT-5.4` from Codex without explicit communication; the impact on Codex user experience is implied across
[Introducing GPT-5.4](https://openai.com/index/introducing-gpt-5-4/) and
[Model Release Notes: May 28, 2026](https://help.openai.com/en/articles/9624314-model-release-notes). Only `GPT-5.4-Mini` and
`GPT-5.5` remain available in Codex chat, capping `T2–T4` at approximately 104 runs each.

The run count asymmetry is addressable. `T1` already contains `GPT-5.4-Mini` and `GPT-5.5` data. Filtering `T1` to those LLMs
serves as the controlled cross-track comparator. The full `T1` dataset remains an irreproducible historical record: the only
systematic behavioral evidence for `GPT-5.2`, `GPT-5.3-Codex`, and `GPT-5.4` across 13 test URLs at four intelligence levels
in this test collection.

The retirement also introduces a confound for surface comparison findings, as it stands alongside architectural constraints
as contributing factors to drift, circumstances in which `T2` behavior diverges from `T1` for the same LLM and LLM-version.
`H4` assessments are particularly sensitive to this: a behavioral difference between `T1` and `T2` could reflect surface,
version drift, or both, and the data alone can't always separate them.

### Methodology Decision

Use the `T1` subset filtered to `GPT-5.4-Mini` and `GPT-5.5` as the controlled cross-track comparator for `T1` ↔ `T2`.
Don't treat the LLM reduction as a study failure; the asymmetry is explainable and documented. Where a `T2` finding diverges
from its `T1` equivalent, note LLM-version drift as an alternative explanation alongside known platform limits.
