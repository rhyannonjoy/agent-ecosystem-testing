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
extends to the VS Code extension surface, confirmed in `BL-1`.<br>`GPT-5.4-Mini High` showed a duplicate report appear after the
session _appeared to complete_, alongside timer drift.

`T1` described a double report that resolved: two versions of a run collapsed to one during a later batch-logging pass, with
the `web` limitation observation absent from the surviving copy. But in `T2`, the direction reversed in which a single report
became a double, with identical content added rather than cleaned up. Both variants share the same data integrity risk, the
post-session state doesn't match the runtime state, but the mechanism may continue to operate differently while testing the VS Code
extension.

The timer drift also reveals a measurement ambiguity specific to the extension surface. While the screenshot at `1min45s`
captured output that appeared complete, the session hadn't terminated. The agent continued processing after the visible report
rendered, suggesting that the output panel reaching an initial completion state isn't a completely reliable termination signal.
On the desktop app, thought panel collapse offered an explicit session-end indicator. On the VS Code extension, these signals aren't
as distinct. Whether `Auto-review`, `Full access`, or any other default setting drives this behavior isn't confirmed. The mechanism
isn't visible in the thought panel, and the agent doesn't report the changes unprompted.

`BL-2` extended this from an isolated event to a consistent surface behavior. All runs produced a duplicate report after an initial
complete render, with identical content added rather than resolved. The pattern appeared at every intelligence level, with no exceptions,
suggesting this post-hoc over-delivery isn't LLM-specific or intelligence-level-specific.

### Methodology Decision

The primary record principle, screenshot at runtime, also applies while testing using the VS Code extension. While the `T2` evidence
adds new formatting inconsistencies to look out for, there's no need to wait for a stable timer and confirmed session termination
before treating output as _final_. Flag inconsistencies as they come, as the current implication remains that sessions may be incomplete
at capture time.

---

## `Browser` Unavailable

`T1` Desktop runs consistently showed `/private/tmp/codex-browser-use` initialized at each test launch, regardless of whether
the prompt included `@Browser`. As documented in [Session Contamination](./friction-note-interpreted-desktop.md#session-contamination),
this is the Codex desktop app's IPC socket for its `Browser Use` backend initialized by the app, not by the agent. No `T2` `BL-1` runs
repeated the pattern, confirming that the VS Code extension doesn't provision the `Browser Use` backend by default. There's no
obvious path in extension settings to configure this behavior.

`GPT-5.4-Mini Medium`'s agent attempted to invoke `Browser` and received `Browser is not available: iab`. `T1` `Browser` calls
weren't common, but after requesting user permission, had no issues, suggesting that it remains a known option, but that
backend provisioning isn't auto-configured for the extension. The attempt consumed context before the agent fell back to `curl`.
No subsequent `T2` run attempted `Browser` after observing the failure, but didn't diagnose or suggest improvements either -
which is consistent with the pattern described in [`web` Cache Miss](./friction-note-interpreted-desktop.md#web-cache-miss): agents tend
to report successes and not examine failures.

### Methodology Decision

Log `Browser is not available: iab` as an infrastructural difference, not an agent error. The absence of
`/codex-browser-use` across `T2` runs serves as an identity marker throughout the test cycle in which its presence
would indicate desktop app initialization rather than VS Code extension behavior. `Browser` configuration not required, as
the purpose of this testing framework is to observe-capture default behavior, not overcorrect it. The failure
is meaningful data.

---

## LLM Retirement

`T1` completed 261 runs across five LLM variants `GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`, `GPT-5.4`, and `GPT-5.5` at four
intelligence levels across 13 URLs. Between `T1` completion and the start of `T2`, OpenAI retired `GPT-5.2`, `GPT-5.3-Codex`,
and `GPT-5.4` from Codex without explicit communication. OpenAI implies the impact on Codex user experience across
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

---

## Mixed-Format Source Misidentification, Tool Selection Driver

`T2` `BL-2` replicated `T1`'s pattern at reduced cost. The same triggers were present: embedded HTML table markup, the
`ce-create## Summary` concatenation artifact, and an unexplained ~20 KB size expectation across most runs. The `file` utility
added a layer not observed in `T1`: every run that saved and inspected the `.md` file received
`HTML document text, ASCII text, with very long lines (527)`, which some agents cited alongside the format anomaly. The
`Browser Use` escalation path isn't available on the VS Code extension by default, so the misidentification resolved to a generic,
unexamined `web` error and `curl` pivot rather than a 63K-token tool failure. Whether the same escalation would have
occurred with `Browser` configuration isn't resolvable from `T2` data alone, but the surface constraint bounded the cost.

>_Read more about this `T1` pattern in [Friction: Interpreted - Desktop](friction-note-interpreted-desktop.md#mixed-format-source-misidentification-tool-selection-driver)_
