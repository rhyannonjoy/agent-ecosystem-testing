# Memory vs. Workspace Docs-Consumption Skill Audit

Total sessions: **26**

_Memory_ = any `.codex/memories` content, including the competing `single-url-retrieval-measurement` skill.
_Workspace skill_ = the repository's `.agents/skills/docs-consumption/SKILL.md`. The agent loads it through the developer `<skills_instructions>` block, names it, mentions its path, or uses a `COMPLETE/PARTIAL/UNVERIFIABLE` prefix.
_Memory skill delivery_ = Codex doesn't list the `single-url-retrieval-measurement` skill in the `<skills_instructions>` block. Instead, it delivers that skill through the separate system `## Memory` instruction, which tells the agent it has access to a memory folder and should use it by default.

## Overall Co-occurrence

- Memory signals: 0% 0/26
- Workspace skill signals: 100% 26/26
- Both memory and workspace skill: 0% 0/26
- Memory only: 0% 0/26
- Workspace skill only, no `.codex/memories` detected: 100% 26/26
- Neither: 0% 0/26

## Memory Sources

This table shows where memory-related content appeared in memory-positive runs. `system_memory_instruction` marks the separate `## Memory` system prompt. `system_prompt` marks the same block where a concrete path like `.codex/memories` matched. `report notes` are derived from the observer-written `results.csv` notes field, not from the rollout logs.

| Source | Count | % of memory-positive: 0 |
| --- | --- | --- |

## Workspace Docs-Consumption Skill Signal Breakdown

| Signal | Count | % of all runs |
| --- | --- | --- |
| `docs-consumption` loaded | 26 | 100% |
| name mentioned by agent | 26 | 100% |
| path mentioned by agent | 3 | 12% |
| protocol prefix used | 26 | 100% |
| skill language used | 26 | 100% |

## Per-Model Comparison

| Model | Runs | Memory+ | Workspace Skill+ | Both | Memory-only | Workspace-only | Neither |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `GPT-5.4` | 4 | 0 | 4 | 0 | 0 | 4 | 0 |
| `GPT-5.4 Mini` | 4 | 0 | 4 | 0 | 0 | 4 | 0 |
| `GPT-5.5` | 4 | 0 | 4 | 0 | 0 | 4 | 0 |
| `GPT-5.6 Luna` | 4 | 0 | 4 | 0 | 0 | 4 | 0 |
| `GPT-5.6 Sol` | 5 | 0 | 5 | 0 | 0 | 5 | 0 |
| `GPT-5.6 Terra` | 5 | 0 | 5 | 0 | 0 | 5 | 0 |

## Competing Skills: System Skills Block vs. System Memory Instruction

Codex loads the workspace `docs-consumption` skill through the developer `<skills_instructions>` block. It doesn't list the `single-url-retrieval-measurement` skill there. Instead, it delivers that skill through the separate system `## Memory` instruction, which tells the agent it has access to a memory folder and should use it by default. The 'referenced' row counts runs where that instruction was present **and** the agent read or cited the memory skill or folder.

| Condition | Count | % of all runs |
| --- | --- | --- |
| `docs-consumption` loaded: system skills block | 26 | 100% |
| system `## Memory` instruction present | 0 | 0% |
| `single-url-retrieval-measurement` referenced: system-instructed, agent-read | 0 | 0% |
| Both present | 0 | 0% |
| `docs-consumption` only | 26 | 100% |
| memory-instructed only | 0 | 0% |

## Edge Cases


### Memory-only sessions

- None

### Workspace-skill-only sessions: no `.codex/memories` detected

- `rollout-2026-07-21T16-26-37-019f8700-b360-7642-a30b-7b0c43be4719.jsonl` `GPT-5.4 Mini`, low
- `rollout-2026-07-21T16-36-41-019f8709-e760-7643-a8a8-962ed960bdd6.jsonl` `GPT-5.4 Mini`, medium
- `rollout-2026-07-21T16-50-03-019f8716-2798-7370-9edc-72c9793786ac.jsonl` `GPT-5.4 Mini`, high
- `rollout-2026-07-21T17-00-00-019f871f-4162-79d0-914f-9000fe582126.jsonl` `GPT-5.4 Mini`, extra-high
- `rollout-2026-07-21T19-39-37-019f87b1-6426-78b0-a445-5b9b3dbb3e2e.jsonl` `GPT-5.4`, low
- `rollout-2026-07-21T19-48-45-019f87b9-c1cc-7551-8b93-acf562e40673.jsonl` `GPT-5.4`, medium
- `rollout-2026-07-21T19-58-23-019f87c2-9397-74a2-812d-e33d49d5171b.jsonl` `GPT-5.4`, high
- `rollout-2026-07-21T20-10-30-019f87cd-ab8a-7853-b4cc-5de74fb5a1a6.jsonl` `GPT-5.4`, extra-high
- `rollout-2026-07-21T20-41-16-019f87e9-d6ee-7202-a313-12ecfe3345af.jsonl` `GPT-5.5`, low
- `rollout-2026-07-21T20-52-05-019f87f3-bc51-7fd3-a63f-edd7584ad87f.jsonl` `GPT-5.5`, medium
- `rollout-2026-07-21T21-00-07-019f87fb-16ce-7980-bea5-de2ec4707c4a.jsonl` `GPT-5.5`, high
- `rollout-2026-07-21T21-09-21-019f8803-8aed-7392-8d3a-d2fdf638a01b.jsonl` `GPT-5.5`, extra-high
- `rollout-2026-07-21T21-30-35-019f8816-fc1c-7d81-8090-efc5350774fa.jsonl` `GPT-5.6 Luna`, low
- `rollout-2026-07-21T21-44-18-019f8823-8a4c-7ae0-ad72-603a58e46414.jsonl` `GPT-5.6 Luna`, medium
- `rollout-2026-07-21T21-53-21-019f882b-d332-71b2-9140-571d8ecfc3d6.jsonl` `GPT-5.6 Luna`, high
- `rollout-2026-07-21T22-01-17-019f8833-173e-7740-b8da-a1949f3fd145.jsonl` `GPT-5.6 Luna`, extra-high
- `rollout-2026-07-22T12-45-13-019f8b5c-5a37-7321-9880-e35901265357.jsonl` `GPT-5.6 Sol`, low
- `rollout-2026-07-22T12-54-32-019f8b64-e109-7942-bbad-52b1adb3b586.jsonl` `GPT-5.6 Sol`, medium
- `rollout-2026-07-22T13-04-44-019f8b6e-3775-7093-b372-9344f25240fc.jsonl` `GPT-5.6 Sol`, high
- `rollout-2026-07-22T13-11-48-019f8b74-b243-74a3-a820-1602eb624487.jsonl` `GPT-5.6 Sol`, extra-high
- `rollout-2026-07-22T13-21-35-019f8b7d-a591-7781-8941-d8a01893d200.jsonl` `GPT-5.6 Sol`, ultra
- `rollout-2026-07-22T15-11-57-019f8be2-afb8-7fd1-bb31-26934f70261f.jsonl` `GPT-5.6 Terra`, low
- `rollout-2026-07-22T15-19-54-019f8be9-f93a-7022-a9a9-443733c3d0d8.jsonl` `GPT-5.6 Terra`, medium
- `rollout-2026-07-22T15-25-55-019f8bef-7948-7d30-bbb2-b06629ed94a4.jsonl` `GPT-5.6 Terra`, high
- `rollout-2026-07-22T15-32-49-019f8bf5-cd5c-7dd0-b84f-6d12b4fdacdb.jsonl` `GPT-5.6 Terra`, extra-high
- `rollout-2026-07-22T15-40-38-019f8bfc-f4be-77d1-a800-4537f72f1fb5.jsonl` `GPT-5.6 Terra`, ultra
