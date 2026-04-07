---
layout: default
title: "Friction Note"
permalink: /docs/cognition-windsurf-cascade/friction-note
parent: Cognition Windsurf Cascade
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

## Topic Guide

---

- [Arena Mode: Unit of Observation](#arena-mode-unit-of-observation)

---

## Arena Mode: Unit of Observation

Cascade includes [arena mode](https://docs.windsurf.com/windsurf/cascade/arena), which
runs the same prompt across multiple models simultaneously for side-by-side comparison.
Each slot executes the prompt in a separate session with its own worktree, providing a type of
test isolation. While arena mode is designed for parallel execution, the user may control
whether slots run in parallel or sequentially. Because Cascade requests permission to use
`read_url_content` before completing the prompt tasks in each slot, the user can approve
all slots at once or one at a time. During `BL-1` interpreted track runs, slots were approved
and completed one at a time by user choice, not by Cascade automation.

**Worktree isolation offers to close the workspace-artifact-accumulation confounder.** If each
slot runs in its own worktree, later slots can't read artifacts written by earlier slots
regardless of approval order. The session ordering confounder documented in
[Copilot's unsolicited cross-run analysis](../microsoft-github-copilot/friction-note.md#agentic-over-delivery-unsolicited-cross-run-analysis---raw-track) —
where later runs incorporated prior run artifacts autonomously — doesn't apply here by design. Each
slot is a structurally independent replicate of the same condition. Whether Cascade's worktree isolation
holds in practice under sequential approval is worth confirming from the `BL-1` output, but the documented
architecture supports treating slots as independent.

**`read_url_content` requires explicit user approval before each fetch executes.** When
asked directly, Cascade confirmed: it invokes `read_url_content` when a URL is provided,
and the function requires explicit approval before the fetch executes. Each slot issued its
own fetch independently, confirmed by a distinct permission prompt per slot. Output variance
across slots reflects the full pipeline — retrieval through post-processing — not
post-retrieval processing differences from a shared fetch result.

**Methodology Decision**: log all four slots as distinct rows under the same test ID.
`Auto Execution` is disabled throughout testing to maximize observable detail; slots are
approved sequentially by user choice. Worktree isolation means slot position isn't
expected to be an ordering variable, but continue to check if output shows any cross-slot
artifact bleed before treating all four slots as fully independent replicates.

>_Open Question: does Cascade's per-slot worktree isolation hold under sequential
>approval in practice, or does some shared session state persist across slots? The `BL-1` interpreted track
>output is the first opportunity to check for cross-slot behavioral similarity that would suggest shared context._
