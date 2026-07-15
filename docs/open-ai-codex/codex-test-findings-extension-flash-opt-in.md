---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Extension Flash"
permalink: /docs/open-ai-codex/codex-test-findings-extension-flash-opt-in
parent: OpenAI Codex
---

# Key Findings for Codex's Web Search Behavior, GPT-interpreted - Extension Flash

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Run `python scripts/framework.py --test EC-6 --track vscode-codex-interpreted`
2. Review terminal output
3. Copy the provided prompt asking agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
4. Open a new session in VS Code Codex, paste the prompt into the chat window
5. Approve `curl` escalation and shell permission requests; skip requests for runs of existing workspace scripts
6. Capture the agent's full response; observe the gap between self-report and actual retrieval behavior<br>as the interpreted finding
7. Log structured metadata as described in [`framework-reference.md`](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/framework-reference#workflow)
8. Ensure results saved to [`/results/vscode-codex-interpreted/results.csv`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/vscode-codex-interpreted/results.csv)

---
