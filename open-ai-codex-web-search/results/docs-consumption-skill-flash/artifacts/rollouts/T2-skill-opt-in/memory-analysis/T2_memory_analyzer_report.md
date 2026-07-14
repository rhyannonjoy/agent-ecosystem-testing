# Memory vs. Workspace Docs-Consumption Skill Audit

Total sessions: **31**

- _Memory_ = any `.codex/memories` content, including the competing `single-url-retrieval-measurement` skill.
- _Workspace skill_ = the repository's `.agents/skills/docs-consumption/SKILL.md` loaded via the developer
`<skills_instructions>` block, named by the agent, path mentioned, or COMPLETE/PARTIAL/UNVERIFIABLE prefix used.
- _Memory skill delivery_ = the `single-url-retrieval-measurement` skill isn't listed in the `<skills_instructions>` block,
but reached through the separate system `## Memory` instruction, which tells the agent it has access to a memory folder and
should use it by default.

## Overall Co-occurrence

- Memory signals: 24/31 (77%)
- Workspace skill signals: 27/31 (87%)
- Both memory and workspace skill: 24/31 (77%)
- Memory only: 0/31 (0%)
- Workspace skill only, no `.codex/memories` detected: 3/31 (10%)
- Neither: 4/31 (13%)

## Memory Sources

Where memory-related content appeared across all memory-positive runs. `system_memory_instruction` is the separate `## Memory`
system prompt; `system_prompt` is the same block where a concrete path like `.codex/memories` matched.

| Source | Count | % of memory-positive (24)
| --- | --- | ---
| system_prompt (## Memory block) | 24 | 100%
| system_memory_instruction header | 24 | 100%
| final_answer | 22 | 92%
| tool_output | 19 | 79%
| commentary | 5 | 21%

## Workspace Docs-Consumption Skill Signal Breakdown

| Signal | Count | % of all runs
| --- | --- | ---
| docs-consumption loaded | 27 | 87%
| name mentioned by agent | 19 | 61%
| path mentioned by agent | 1 | 3%
| protocol prefix used | 10 | 32%
| skill language used | 31 | 100%

## Per-Model Comparison

| Model | Runs | Memory+ | Workspace Skill+ | Both | Memory-only | Workspace-only | Neither |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.4 | 4 | 4 | 4 | 4 | 0 | 0 | 0 |
| GPT-5.4 Mini | 9 | 2 | 5 | 2 | 0 | 3 | 4 |
| GPT-5.5 | 4 | 4 | 4 | 4 | 0 | 0 | 0 |
| GPT-5.6 Luna | 4 | 4 | 4 | 4 | 0 | 0 | 0 |
| GPT-5.6 Sol | 5 | 5 | 5 | 5 | 0 | 0 | 0 |
| GPT-5.6 Terra | 5 | 5 | 5 | 5 | 0 | 0 | 0 |

## Competing Skills: System Skills Block vs. System Memory Instruction

Codex loads workspace `docs-consumption` skill through the developer `<skills_instructions>` block. The `single-url-retrieval-measurement`
skill isn't loaded there, but reached through the separate system `## Memory` instruction, which directs the agent to use its memory folder
by default. The 'referenced' row counts runs where that instruction was present **and** the agent read or cited the memory skill or folder.

| Condition | Count | % of all runs
| --- | --- | ---
| docs-consumption loaded (system skills block) | 27 | 87%
| system `## Memory` instruction present | 24 | 77%
| single-url-retrieval-measurement referenced (system-instructed + agent-read) | 24 | 77%
| Both present | 24 | 77%
| docs-consumption only | 3 | 10%
| memory-instructed only | 0 | 0%

## GPT-5.4 Mini Early vs. Late Split

The first four `Mini` rollouts (morning of 2026-07-09) show no memory signals. The later five show the workspace skill loading consistently,
but memory references only appear in the last two (18:51 and 19:06).

| Period | Runs | Memory+ | Workspace Skill+ | Both | Memory-only | Workspace-only | Neither |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Early | 4 | 0 | 0 | 0 | 0 | 0 | 4 |
| Late | 5 | 2 | 5 | 2 | 0 | 3 | 0 |

## Edge Cases

### Memory-only sessions

- None

### Workspace-skill-only sessions, no `.codex/memories` detected

- `rollout-2026-07-09T17-14-45-019f4960-7325-7d81-9df0-37f3f43cd1de.jsonl` - GPT-5.4 Mini (low)
- `rollout-2026-07-09T17-54-01-019f4984-6752-7af3-9bf5-92441ed39872.jsonl` - GPT-5.4 Mini (low)
- `rollout-2026-07-09T18-37-53-019f49ac-8e18-71f0-aec7-06b6d3a747af.jsonl` - GPT-5.4 Mini (medium)

### Sessions where docs-consumption loaded but no COMPLETE/PARTIAL/UNVERIFIABLE prefix (17)

- `rollout-2026-07-09T17-14-45-019f4960-7325-7d81-9df0-37f3f43cd1de.jsonl` - GPT-5.4 Mini (low)
- `rollout-2026-07-09T17-54-01-019f4984-6752-7af3-9bf5-92441ed39872.jsonl` - GPT-5.4 Mini (low)
- `rollout-2026-07-09T18-37-53-019f49ac-8e18-71f0-aec7-06b6d3a747af.jsonl` - GPT-5.4 Mini (medium)
- `rollout-2026-07-09T18-51-23-019f49b8-e95d-7903-8899-af9c3dfc30d1.jsonl` - GPT-5.4 Mini (high)
- `rollout-2026-07-09T19-06-18-019f49c6-93e4-7971-abfc-51a64ecbd6f3.jsonl` - GPT-5.4 Mini (extra-high)
- `rollout-2026-07-12T12-03-02-019f57b6-24b8-7ec1-ba6a-7ce00378962b.jsonl` - GPT-5.4 (low)
- `rollout-2026-07-12T12-31-35-019f57d0-467c-7341-a164-4e58be0859fa.jsonl` - GPT-5.4 (medium)
- `rollout-2026-07-12T12-54-49-019f57e5-8d61-74c3-bb37-e3fdd541f8e7.jsonl` - GPT-5.4 (high)
- `rollout-2026-07-12T13-07-40-019f57f1-4ef1-77b2-ada3-afdbc27e6d6c.jsonl` - GPT-5.4 (extra-high)
- `rollout-2026-07-12T20-51-09-019f5999-a649-7ac3-954a-ac59bbcbac71.jsonl` - GPT-5.6 Luna (high)
- `rollout-2026-07-13T12-59-53-019f5d10-8e63-75d2-91f1-7ba50c59e992.jsonl` - GPT-5.6 Sol (medium)
- `rollout-2026-07-13T13-10-07-019f5d19-eae4-72b3-a28a-141cc406f121.jsonl` - GPT-5.6 Sol (high)
- `rollout-2026-07-13T13-24-53-019f5d27-70f9-7471-9d0e-123a82a9895e.jsonl` - GPT-5.6 Sol (extra-high)
- `rollout-2026-07-13T15-28-31-019f5d98-9fdc-7713-aae5-f6d391a51d74.jsonl` - GPT-5.6 Sol (ultra)
- `rollout-2026-07-13T14-20-55-019f5d5a-be38-7a71-b370-f254f406ad41.jsonl` - GPT-5.6 Terra (low)
- `rollout-2026-07-13T14-35-17-019f5d67-e4c9-76e2-a8ae-0d10d9f64e77.jsonl` - GPT-5.6 Terra (medium)
- `rollout-2026-07-13T14-56-00-019f5d7a-db04-7b60-aafe-c1f9f071b5e8.jsonl` - GPT-5.6 Terra (extra-high)

