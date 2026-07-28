---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Skill On + Memory Suppressed"
permalink: /docs/open-ai-codex-flash/test-findings-skill-on-mem-suppressed
parent: OpenAI Codex - Flash
---

# Key Findings for Codex's Web Search Behavior<br>`GPT`-interpreted `/SKILL` On + `/memories` Suppressed

---

> _Companion conditions [`skill-off` baseline](../open-ai-codex/codex-test-findings-extension.md), [`skill-opt-in`](test-findings-skill-opt-in.md), `skill-on + memory available`
> excluded from this doc. Findings limited to whether agents followed `docs-consumption/SKILL` after explicit activation or `/memories` deactivation changes retrieval-reporting outcomes. Experiment design in [Flash Runbook](runbook.md)._

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Confirm that `.agents/skills/docs-consumption/SKILL.md` exists in the workspace and mentioned in the prompt
2. Run `python scripts/framework.py --test EC-6 --track vscode-codex-interpreted`
3. Review terminal output
4. Copy the provided prompt asking the agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
5. Open a new session in [VS Code Codex](https://learn.chatgpt.com/docs/codex/ide), paste the prompt into the chat window
6. Approve `curl` escalation, shell permission requests; skip requests for runs of existing workspace scripts
7. Capture the agent's full response; observe whether the agent reads and acts on `docs-consumption/SKILL.md`
8. Log structured metadata with `python scripts/log.py --results-dir results/docs-consumption-skill-flash`
9. Run `rollout_audit.py`, `memory_audit.py` to separate `/SKILL` reference from `/memories` influence

---
