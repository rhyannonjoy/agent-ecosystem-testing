---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Skill Opt-In"
permalink: /docs/open-ai-codex-flash/test-findings-skill-opt-in
parent: OpenAI Codex - Flash
---

# Key Findings for Codex's Web Search Behavior<br>`GPT`-interpreted `/SKILL opt-in`

---

> _Companion conditions include [`/SKILL-off` baseline](../open-ai-codex/codex-test-findings-extension.md) and [`/SKILL-on + /memories suppressed`](test-findings-skill-on-mem-suppressed.md).
> This doc's limited to whether agents discovered-followed `docs-consumption/SKILL` independently, not whether explicit
> activation or `/memories` removal changes retrieval-reporting outcomes. Experiment design in [Flash Runbook](runbook.md)._

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Confirm that `.agents/skills/docs-consumption/SKILL.md` exists in the workspace, but not mentioned in the prompt
2. Run `python scripts/framework.py --test EC-6 --track vscode-codex-interpreted`
3. Review terminal output
4. Copy the provided prompt asking the agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
5. Open a new session in [VS Code Codex](https://learn.chatgpt.com/docs/codex/ide), paste the prompt into the chat window
6. Approve `curl` escalation, shell permission requests; skip requests for runs of existing workspace scripts
7. Capture the agent's full response; observe whether the agent discovers or acts on `docs-consumption/SKILL.md`
8. Log structured metadata with `python scripts/log.py --results-dir results/docs-consumption-skill-flash`
9. Run `rollout_audit.py`, `memory_audit.py` to separate `/SKILL` reference from `/memories` influence

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard<br>Character<br>Limit** | _None detected with `curl`_: most agents retrieved the full response with `curl`;<br>no new retrieval ceiling attributable to `docs-consumption/SKILL`. |
| **Hard<br>Token<br>Limit** | _None detected with `curl`_: results mirror the [historical `T2` findings](../open-ai-codex/codex-test-findings-extension.md);<br>token counts stayed within the measured payload range |
| **`/SKILL`<br>Discovery** | _Passive, not guaranteed_: ~87% - 27/31 logs cite `/SKILL` injection from `<skills_instructions>` block;<br>only one agent reported its path; ~58% - 18/31 used `COMPLETE` protocol prefix |
| **`/SKILL`<br>Retrieval<br>Influence** | _Weak to none_: most bypassed `web` entirely for `curl` without meaningful truncation assessment, [historically agentic retrieval paths](../open-ai-codex/codex-test-findings-extension.md#retrieval-paths) included much more variety; `/SKILL` presence didn't produce evidence of any impact on tool selection |
| **`/SKILL`<br>Reporting<br>Influence** | _Surface-level_: agents frequently opened reports with `COMPLETE`, echoed _"DNS/sandbox error"_, but these read as shortcuts rather than protocol-driven analysis; most didn't follow deeper requirements to include explicit truncation markers, embedded-error examination, and recommendations for improvement |
| **`/memories`<br>Confound** | _Strong_: log `## Memory` instruction with its own competing `single-url-retrieval-measurement/SKILL` present/referenced ~77% - 24/31, making `docs-consumption/SKILL` effect isolation challenging |
| **Recommendations** | _Absent_: despite `/SKILL` requiring suggestions when a gap is addressable, no agent produced one |

## Results Snapshot

| **Metric** | **Results** |
| --- | --- |
| **Track** | `T2` `GPT`-interpreted, VS Code with Codex Extension |
| **Test** | [`EC-6` Raw GitHub Markdown](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md) |
| **`/SKILL` Condition** | `opt-in` - `docs-consumption/SKILL` present, but the prompt never mentioned it |
| **LLMs Observed** | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5`, `GPT-5.6 Luna`, `GPT-5.6 Sol`, `GPT-5.6 Terra` |
| **Reasoning Levels** | `Light`, `Medium`, `High`, `Extra High`, `Ultra` |
| **Total Runs** | 31 |
| **`/SKILL` Loaded** | ~87% of session logs cite `/docs-consumption/SKILL` injected into the agent's context |
| **`/SKILL` Path Emitted** | One agent wrote the full `/SKILL` path in its own output rather than mentioning it in passing |
| **Protocol Prefix Used** | ~58% of agents used `/SKILL` summarization prefix to signal completeness |
| **`/SKILL` Language Used** | 100% of runs contained at least one `/SKILL`-related phrase, but read as a shortcut<br>rather than protocol-driven analysis |
| **Truncation: `Yes`** | One agent reported incomplete content with the familiar `T2` [`L54` `web`-window cutpoint](../open-ai-codex/codex-test-findings-extension.md#platform-limit-summary) |
| **Truncation: `Mixed`** | Six agents reported both a `web` limit and a full `curl` result |
| **Truncation: `Implicit`** | No agent reasoned around a limit without naming it |
| **Truncation: `No`** | 77% of runs had no truncation signal, largely because agents bypassed `web` for `curl` |
| **Completeness Accurate** | 100% of agents correctly classified the fetch state against the evidence they had |
| **Errors Examined** | ~87% of agents accurately described their most common error, but ignored others |
| **Execution vs. Completeness** | 100% of agents distinguished _"the tool ran"_ from _"the full content arrived"_ |
| **Avoided Reframing** | ~84% of agents avoided calling a partial or error-state fetch _"complete"_ or _"successful"_ |
| **Fix Recommended** | 0% agents suggested some form of remediation; rare recs limited to log formatting |
| **`/memories` Signals** | ~77% of session logs cite the system `## Memory` instruction or its competing<br>`/memories/skills/single-url-retrieval-measurement/SKILL` |
| **`/memories` + `/SKILL`** | ~77% of runs had both `/docs-consumption/SKILL` and `/memories.../SKILL` injected,<br>making it hard to isolate either effect |

## Key Findings

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`/SKILL` discovery is location, version-dependent** | `GPT-5.4 Mini` runs | Early `Mini` runs didn't load `/SKILL` due to `~.agents/skills` location requirement; `/memories` didn't due to version limitations; both appeared in later runs | **`/SKILL` discovery depends on specific runtime conditions, not on general file presence, LLM, or reasoning level** |
| 2 | **`/SKILL` loaded, but followed superficially** | All tests | 87% loaded, 61% mentioned `/docs-consumption` by name, 58% used requested protocol prefix, 100% used somewhat `/SKILL`-like language | **Loading `/SKILL` doesn't guarantee comprehensive protocol compliance; half the runs using protocol prefix didn't follow failure-examination requirements** |
| 3 | **`COMPLETE` protocol prefix becomes a stylistic shortcut** | All tests | All agents used `/SKILL`-like language; many opened reports with `COMPLETE`, included common error phrasing or tool selection reasoning without tying them to platform limits | **Agents adopt the easiest surface markers of the protocol without adopting the requested, epistemic discipline** |
| 4 | **`/SKILL` `opt-in` doesn't shift retrieval strategy** | All tests | Most bypassed `web` for `curl`; no new pagination, escalation, or verification patterns tied to `/SKILL` discovery | **`/SKILL` requests for deeper retrieval analysis don't impact retrieval tool selection** |
| 5 | **`/SKILL` `opt-in` weakens truncation signals** | All tests | Only 22% of agents reported some form of truncation event, which is a 47% drop from the [historical `T2` results](../open-ai-codex/codex-test-findings-extension.md#results-snapshot); reflects strategy, not lack of truncation risk | **Agents remove `L54` `web` cutpoint by favoring `curl`; `/SKILL` presence doesn't independently enhance truncation reporting** |
| 6 | **Agents classify completeness accurately, but don't recommend fixes** | All tests | `completeness_accurate=100%`, `exec_vs_complete=100%`, `avoided_reframing=84%`, but `fix_recommended=0%`; agents weren't lying, just not comprehensive | **Agents ignored `/SKILL`'s fix requirement; classification, report integrity scores reflect baseline behavior, not explicit evidence of `/SKILL` influence** |
| 7 | **`/SKILL` `opt-in` produces expected _false positive_ profile** | All tests | Shallow compliance scores, parroting common error phrasing, no fix recommendations, weak truncation reporting, strong `/memories` confound | **Passive `/SKILL` presence produces trivial compliance; this is a useful baseline, not evidence of `/SKILL` impact on retrieval behavior or report quality** |
| 8 | **`/memories` is the dominant influence** | All tests | 77% included both `/memories` and `docs-consumption` `/SKILL` signals; `/memories.../SKILL` referenced in 79% of `tool_output`, 92% of `final_answer` | **System-injected `/memories` largely overrides `docs-consumption/SKILL`, making individual evaluation a challenge** |

## `/memories` Dominance

Together [`memory_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_audit.py) and
[`memory_analyzer`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_analyzer.py)
extract `.codex/memories` presence while
[`rollout_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_audit.py) flags
`/docs-consumption/SKILL` injection, general session shape, and agent errors from each test's rollout log. Because rollouts include
what _can render each session_ and don't transcribe what _does render each session_, the visualizations below include a hybrid of
rollout metadata and agent self-reports from the chat.

While all agents used `/docs-consumption/SKILL`-like phrases and 87% of session logs cite `skills: N loaded docs-consumption: yes`, only 61%
mentioned it in their output, and only 58% showed compliance by using a protocol prefix in their reports. When the `/memories`
feature became available mid-track, it made a big impact on retrieval paths and outcomes. All session logs included
the `## Memory` block in the `system_prompt`. 92% of `final_answer`, 79% of `tool_output`, and 21% of `commentary` fields were overrun with
`/memories`-related language while 58% of agent reports included line-numbered citations from `/memories` content, including but not limited to
`MEMORY.md`, rollout summaries, or its own competing `/single-url-retrieval-measurement/SKILL`.

Due to the design of this natural experiment in which runtime conditions shift among `/docs-consumption/SKILL` relocation, available LLM-reasoning
combinations and extension versions, while 87% of the track injected `/docs-consumption/SKILL` vs 77% `/memories`, agents never explicitly
favored one over the other in chat. If `/docs-consumption/SKILL` loaded correctly and `/memories` were available, agents' rendered reasoning-reporting
showed a mix. No result exhibited a `/memories`-only profile. On the surface, the most common agent report character was somewhat balanced co-occurence:

{% raw %}
<svg class="cdx-skill-stack" viewBox="0 0 790 80" style="max-width: 790px; margin: 1rem auto; display: block;">
  <style>
    .cdx-skill-stack .bar { height: 36; }
    .cdx-skill-stack .neither { fill: #d0cec7; }
    .cdx-skill-stack .docs { fill: #1D9E75; }
    .cdx-skill-stack .both { fill: #378ADD; }
    .cdx-skill-stack text { fill: currentColor; font-family: inherit; }
    .cdx-skill-stack .inside-dark { font-size: 13px; }
    .cdx-skill-stack .inside-light { font-size: 13px; fill: #fff; }
    .cdx-skill-stack .legend { font-size: 10px; opacity: 0.8; }

    html[data-theme="dark"] .cdx-skill-stack .neither { fill: #363634; }
    html[data-theme="dark"] .cdx-skill-stack .docs { fill: #0F6E56; }
    html[data-theme="dark"] .cdx-skill-stack .both { fill: #185FA5; }
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) .cdx-skill-stack .neither { fill: #363634; }
      :root:not([data-theme="light"]) .cdx-skill-stack .docs { fill: #0F6E56; }
      :root:not([data-theme="light"]) .cdx-skill-stack .both { fill: #185FA5; }
    }
  </style>

  <!-- Bar spans full width -->
  <rect class="bar neither" x="10" y="14" width="102.2" height="36"/>
  <rect class="bar docs" x="112.2" y="14" width="76.4" height="36"/>
  <rect class="bar both" x="188.6" y="14" width="631.4" height="36"/>

  <!-- Inside labels -->
  <text class="inside-dark" x="61.1" y="37" text-anchor="middle">13%</text>
  <text class="inside-light" x="150.4" y="37" text-anchor="middle">10%</text>
  <text class="inside-light" x="504.3" y="37" text-anchor="middle">77%</text>

  <!-- Legend horizontal below the bar -->
  <rect x="10" y="58" width="8" height="8" class="neither"/>
  <text class="legend" x="22" y="65" text-anchor="start">neither</text>

  <rect x="104" y="58" width="8" height="8" class="docs"/>
  <text class="legend" x="116" y="65" text-anchor="start">only /docs-consumption</text>

  <rect x="305" y="58" width="8" height="8" class="both"/>
  <text class="legend" x="317" y="65" text-anchor="start">both /docs-consumption + /memories</text>
</svg>
{% endraw %}

The rollout details tell another story. `/memories` load first and populate more session fields; its clippings of
agentic interpretation of past sessions, without user input, create a brittle cheat sheet of competing conventions, flattening the test task
into `single-URL-retrieval-measurement` instead of truncation assessment. Agents didn't lie about including `/docs-consumption/SKILL` requirements,
but they complied as little as possible - producing false positive results of historically, baseline behavior. While no `/memories` component
forbid  `web` use, its `single-URL-retrieval-measurement/SKILL` states _"start with the lightest retrieval surface that can
answer the question"_ and `memory_summary.md` concludes that _"the durable lesson was to stop trusting the clipped rendered view"_ influencing
agents to bypass `web`'s text extraction for `curl`'s raw reponse. Each run replayed the same strategy, like an agentic echo chamber of
stale misinterpretation, burying the prompt and `/docs-consumption/SKILL`.

This heat map organizes runs by LLM-reasoning combination. Column colors group the signal type. Striped cells indicate signal presence, but
shallow compliance reading as false positives. Columns `SKILL path` and `fix recs` are the most telling: only one agent wrote the full
`/docs-consumption/SKILL` path, and in spite of `/memories` over-documenting common errors, no agent suggested remediation. Results read
like a script rather than live reasoning, suiting deterministic measurement tasks well, but an old-fashioned cron job would outperform an agent here.

{% raw %}
<div id="cdx-skill-optin-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.cdx-skill-wrap { overflow-x: auto; display: flex; justify-content: center; }
table.cdx-skill { border-collapse: collapse; width: auto; }
table.cdx-skill th { font-size: 10px; font-weight: 500; padding: 3px 0; text-align: center; white-space: nowrap; color: inherit; }
table.cdx-skill th:not(.cdx-skill-rh) { padding-left: 3px; padding-right: 3px; }
table.cdx-skill th.cdx-skill-rh { text-align: left; padding-left: 0; padding-right: 1px; }
table.cdx-skill th.cdx-skill-spacer { border-left: 1.5px solid rgba(128,128,128,0.22); }
table.cdx-skill th .cdx-skill-sub { font-weight: 400; font-size: 9px; opacity: 0.55; display: block; }
table.cdx-skill td { padding: 1px 3px; text-align: center; vertical-align: middle; }
table.cdx-skill td.cdx-skill-spacer { border-left: 1.5px solid rgba(128,128,128,0.22); }
table.cdx-skill td.cdx-skill-rl { font-size: 10px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 1px; color: inherit; vertical-align: middle; }
table.cdx-skill td.cdx-skill-llm { font-weight: 400; }
.cdx-skill-cell { border-radius: 3px; display: block; width: 22px; height: 22px; margin: 1px auto; cursor: help; border: 1.5px solid rgba(128,128,128,0.22); box-sizing: border-box; position: relative; }
.cdx-skill-cell.cdx-skill-stripe::after { content: ''; position: absolute; inset: 0; border-radius: 3px; background: repeating-linear-gradient(135deg, rgba(255,255,255,0.45), rgba(255,255,255,0.45) 3px, transparent 3px, transparent 6px); pointer-events: none; }
@media (prefers-color-scheme: dark) {
  .cdx-skill-cell.cdx-skill-stripe::after { background: repeating-linear-gradient(135deg, rgba(0,0,0,0.35), rgba(0,0,0,0.35) 3px, transparent 3px, transparent 6px); }
}
.cdx-skill-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; }
.cdx-skill-overlay { position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,0.78); display: flex; align-items: center; justify-content: center; padding: 20px; }
.cdx-skill-overlay-inner { border-radius: 10px; padding: 22px 26px; max-width: 99vw; max-height: 93vh; overflow: auto; position: relative; }
.cdx-skill-close { position: absolute; top: 10px; right: 12px; background: none; border: none; font-size: 20px; cursor: pointer; opacity: 0.5; line-height: 1; }
.cdx-skill-close:hover { opacity: 1; }
.cdx-skill-fig { margin-top: 1.5rem; }
.cdx-skill-fig h4 { margin-bottom: 0.5rem; }
.cdx-skill-caption { font-size: 11px; opacity: 0.65; margin-top: 6px; line-height: 1.5; }
</style>

<script>
(function() {
  var e = React.createElement;

  function detectDark() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t === 'dark') return true;
    if (t === 'light') return false;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  var runs = [{"llm":"GPT-5.4 Mini","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":0,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":0,"complete":0,"complete_acc":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"yes","session":"019f4960"},{"llm":"GPT-5.4 Mini","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":0,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":0,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f4984"},{"llm":"GPT-5.4 Mini","level":"Light","skill_loaded":0,"skill_lang":1,"skill_path":0,"mem_system":0,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":0,"complete":0,"complete_acc":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"mixed","session":"019f485f"},{"llm":"GPT-5.4 Mini","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":0,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":0,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"mixed","session":"019f49ac"},{"llm":"GPT-5.4 Mini","level":"Medium","skill_loaded":0,"skill_lang":1,"skill_path":0,"mem_system":0,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":0,"complete":0,"complete_acc":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"mixed","session":"019f486a"},{"llm":"GPT-5.4 Mini","level":"High","skill_loaded":0,"skill_lang":1,"skill_path":0,"mem_system":0,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":0,"complete":0,"complete_acc":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"mixed","session":"019f4870"},{"llm":"GPT-5.4 Mini","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":1,"mem_summary":1,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f49b8"},{"llm":"GPT-5.4 Mini","level":"Extra High","skill_loaded":0,"skill_lang":1,"skill_path":0,"mem_system":0,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":0,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"mixed","session":"019f487a"},{"llm":"GPT-5.4 Mini","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":1,"mem_summary":1,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f49c6"},{"llm":"GPT-5.4","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":0,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"mixed","session":"019f57b6"},{"llm":"GPT-5.4","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f57d0"},{"llm":"GPT-5.4","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":1,"mem_system":1,"mem_tool":0,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f57e5"},{"llm":"GPT-5.4","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":1,"mem_summary":1,"complete":0,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f57f1"},{"llm":"GPT-5.5","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":1,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5944"},{"llm":"GPT-5.5","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":1,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5950"},{"llm":"GPT-5.5","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5959"},{"llm":"GPT-5.5","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5962"},{"llm":"GPT-5.6 Luna","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":0,"mem_final":0,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","session":"019f59ae"},{"llm":"GPT-5.6 Luna","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":0,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f59a5"},{"llm":"GPT-5.6 Luna","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5999"},{"llm":"GPT-5.6 Luna","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f597c"},{"llm":"GPT-5.6 Sol","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5cfb"},{"llm":"GPT-5.6 Sol","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d10"},{"llm":"GPT-5.6 Sol","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d19"},{"llm":"GPT-5.6 Sol","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d27"},{"llm":"GPT-5.6 Sol","level":"Ultra","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d98"},{"llm":"GPT-5.6 Terra","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d5a"},{"llm":"GPT-5.6 Terra","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d67"},{"llm":"GPT-5.6 Terra","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d71"},{"llm":"GPT-5.6 Terra","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d7a"},{"llm":"GPT-5.6 Terra","level":"Ultra","skill_loaded":1,"skill_lang":1,"skill_path":0,"mem_system":1,"mem_tool":1,"mem_final":1,"mem_comm":0,"mem_summary":1,"complete":1,"complete_acc":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","session":"019f5d83"}];


  var INFLUENCE_COLS = [
    {id: 'mem_system', label: '/mem\nsys', full: '/memories system', group: 'mem'},
    {id: 'mem_tool', label: '/mem\ntool_output', full: '/memories tool_output', group: 'mem'},
    {id: 'mem_final', label: '/mem\nfinal_answer', full: '/memories final_answer', group: 'mem'},
    {id: 'mem_comm', label: '/mem\ncomm', full: '/memories commentary', group: 'mem'},
    {id: 'mem_summary', label: '/mem\nsummary', full: '/memories summary', group: 'mem'},
    {id: 'skill_loaded', label: '/SKILL\nloaded', full: '/SKILL loaded', group: 'req'},
    {id: 'skill_lang', label: '/SKILL\nlang', full: '/SKILL language', group: 'req'},
    {id: 'skill_path', label: '/SKILL\npath', full: '/SKILL path', group: 'req'}
  ];

  var REQ_COLS = [
    {id: 'complete', label: 'prefix', full: 'protocol prefix', group: 'reqSub'},
    {id: 'complete_acc', label: 'accuracy', full: 'completeness accuracy', group: 'reqSub'},
    {id: 'error_exam', label: 'error\nexam', full: 'error examined', group: 'reqSub'},
    {id: 'exec_vs_comp', label: 'exec\ncomp', full: 'execution vs completeness', group: 'reqSub'},
    {id: 'no_reframe', label: 'no\nreframing', full: 'no reframing', group: 'reqSub'},
    {id: 'fix_rec', label: 'fix\nrecs', full: 'fix recommendation', group: 'reqSub'}
  ];

  var ALL_COLS = INFLUENCE_COLS.concat(REQ_COLS);
  var STRIPE_COLS = {skill_lang: true, complete_acc: true, error_exam: true, exec_vs_comp: true, no_reframe: true};
  var GROUP_COLORS = {
    mem: {dark: '#185FA5', light: '#378ADD'},
    req: {dark: '#0F6E56', light: '#1D9E75'},
    reqSub: {dark: '#3BAE7C', light: '#5DC99A'}
  };

  function cellColor(dark, group) {
    return GROUP_COLORS[group][dark ? 'dark' : 'light'];
  }

  function Cell(props) {
    var dark = props.dark;
    var val = props.val;
    var tip = props.tip;
    var group = props.group;
    var colId = props.colId;
    var baseColor = cellColor(dark, group);
    var filled = {background: baseColor, borderColor: baseColor};
    var empty = {background: 'transparent', borderColor: 'transparent'};
    var className = 'cdx-skill-cell';
    if (val && STRIPE_COLS[colId]) className += ' cdx-skill-stripe';
    return e('div', {
      title: tip,
      className: className,
      style: val ? filled : empty
    });
  }

  function HeaderRow(props) {
    var tc = props.tc;
    var dark = props.dark;
    var labelW = props.labelW;
    return e('thead', null,
      e('tr', null,
        e('th', {className: 'cdx-skill-rh', style: {minWidth: labelW, color: tc}}, 'LLM / Reasoning'),
        ALL_COLS.map(function(col, i) {
          var spacerClass = i === INFLUENCE_COLS.length ? 'cdx-skill-spacer' : '';
          var lines = col.label.split(/\n/);
          return e('th', {key: col.id, className: spacerClass, title: col.full, style: {color: tc, lineHeight: 1.1}},
            lines.map(function(line, idx) { return e('div', {key: idx}, line); })
          );
        })
      )
    );
  }

  function RunRow(props) {
    var run = props.run;
    var dark = props.dark;
    var tc = props.textColor || 'inherit';
    var labelW = props.labelW;
    var level = run.level;
    var surface = 'tool: ' + run.method + ' · truncation: ' + run.truncated;
    var rowTip = run.llm + ' ' + run.level + '\n' + surface;
    var ERROR_NOTES = {
      '019f5959': 'shell command error reported',
      '019f5962': 'shell command error not reported',
      '019f5d5a': 'tiktoken error not reported'
    };
    return e('tr', {key: run.session, title: rowTip},
      e('td', {className: 'cdx-skill-rl cdx-skill-llm', style: {color: tc, maxWidth: labelW, width: labelW}},
        run.llm + ' ' + level
      ),
      ALL_COLS.map(function(col, i) {
        var spacerClass = i === INFLUENCE_COLS.length ? 'cdx-skill-spacer' : '';
        var val = run[col.id];
        var isShallow = val && STRIPE_COLS[col.id];
        var label;
        if (col.id === 'complete' && val) {
          label = 'COMPLETE';
        } else if (isShallow) {
          label = 'false positive';
        } else {
          label = val ? 'yes' : 'no';
        }
        var tip = col.full + ': ' + label;
        if (col.id === 'error_exam' && val) {
          tip = 'DNS resolution/sandbox error examined: ' + label;
          if (ERROR_NOTES[run.session]) {
            tip += ', ' + ERROR_NOTES[run.session];
          }
        }
        return e('td', {key: col.id, className: spacerClass},
          e(Cell, {dark: dark, val: val, tip: tip, textColor: tc, group: col.group, colId: col.id})
        );
      })
    );
  }

  function Legend(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var sections = [
      {
        key: 'mem',
        label: '<code>/memories</code> presence',
        color: cellColor(dark, 'mem'),
        cols: [
          {name: '<code>/mem sys</code>', desc: 'inject <code>## Memory</code> block'},
          {name: '<code>/mem tool_output</code>', desc: 'carry <code>/mem</code>-derived info'},
          {name: '<code>/mem final_answer</code>', desc: 'include <code>/mem</code> citations'},
          {name: '<code>/mem comm</code>', desc: 'reasoning invokes <code>/mem</code>'},
          {name: '<code>/mem summary</code>', desc: 'close with <code>/mem</code> framing'}
        ]
      },
      {
        key: 'req',
        label: '<code>/docs-consumption/SKILL</code> presence',
        color: cellColor(dark, 'req'),
        cols: [
          {name: '/SKILL loaded', desc: 'in <code>&lt;skills_instructions&gt;</code>'},
          {name: '/SKILL lang', desc: 'use <code>/SKILL</code>-like phrases'},
          {name: '/SKILL path', desc: 'reference full path'}
        ]
      },
      {
        key: 'reqSub',
        label: '<code>/docs-consumption/SKILL</code> requirement',
        color: cellColor(dark, 'reqSub'),
        cols: [
          {name: 'prefix', desc: '<code>COMPLETE/PARTIAL/UNVERIFIABLE</code>'},
          {name: 'accuracy', desc: 'classify fetch state correctly'},
          {name: 'error exam', desc: 'examine embedded failures'},
          {name: 'exec comp', desc: 'flag tool ran from full content'},
          {name: 'no reframe', desc: 'no reframing error as success'},
          {name: 'fix recs', desc: 'suggest remediation'}
        ]
      }
    ];
    return e('div', {style: {fontSize: 11, marginTop: 8, display: 'flex', gap: 32, justifyContent: 'center'}},
      sections.map(function(s) {
        return e('div', {key: s.key, style: {width: 260}},
          e('div', {style: {display: 'inline-flex', alignItems: 'center', gap: 5, color: tc, marginBottom: 4}},
            e('span', {style: {width: 10, height: 10, borderRadius: 2, background: s.color}}),
            e('span', {dangerouslySetInnerHTML: {__html: s.label}})
          ),
          e('div', {style: {display: 'flex', flexDirection: 'column', gap: 2, color: tc, opacity: 0.8, lineHeight: 1.3}},
            s.cols.map(function(c, i) {
              return e('div', {key: i, style: {whiteSpace: 'nowrap'}, dangerouslySetInnerHTML: {__html:
                '<span style="font-weight: 500;">' + c.name + '</span>: ' + c.desc
              }});
            })
          )
        );
      })
    );
  }

  function HeatmapTable(props) {
    var dark = props.isDark;
    var large = props.large;
    var tc = props.textColor || 'inherit';
    var labelW = large ? 200 : 150;
    return e('div', {className: 'cdx-skill-wrap'},
      e('table', {className: 'cdx-skill'},
        e(HeaderRow, {tc: tc, dark: dark, labelW: labelW}),
        e('tbody', null, runs.map(function(run) {
          return e(RunRow, {key: run.session, run: run, dark: dark, textColor: tc, labelW: labelW});
        }))
      )
    );
  }

  function App() {
    var openState = React.useState(false);
    var isOpen = openState[0];
    var setOpen = openState[1];
    var dark = detectDark();
    var lbBg   = dark ? '#1c1c1a' : '#ffffff';
    var lbText = dark ? '#e8e6df' : '#1a1a18';

    React.useEffect(function() {
      function onKey(ev) { if (ev.key === 'Escape') setOpen(false); }
      if (isOpen) {
        document.addEventListener('keydown', onKey);
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
      return function() {
        document.removeEventListener('keydown', onKey);
        document.body.style.overflow = '';
      };
    }, [isOpen]);

    return e('div', {style: {marginTop: '1.5rem', fontFamily: 'inherit'}},
      e('div', {className: 'cdx-skill-fig'},
        e('div', {onClick: function(){ setOpen(true); }, style: {cursor: 'pointer'}},
          e(HeatmapTable, {isDark: dark, large: false}),
          e('p', {className: 'cdx-skill-hint'}, '↗ click to expand')
        ),
        e('div', {style: {display: 'flex', gap: 28, alignItems: 'flex-start', flexWrap: 'wrap', marginTop: 10, justifyContent: 'center'}},
          e(Legend, {isDark: dark})
        )
      ),
      isOpen && e('div', {
        className: 'cdx-skill-overlay',
        onClick: function(ev){ if (ev.target===ev.currentTarget) setOpen(false); }
      },
        e('div', {className: 'cdx-skill-overlay-inner',
          style: {background: lbBg, color: lbText, width: '99vw'}},
          e('button', {className: 'cdx-skill-close', style: {color: lbText},
            onClick: function(){ setOpen(false); }, 'aria-label': 'Close'}, '×'),
          e(HeatmapTable, {isDark: dark, large: true, textColor: lbText}),
          e('div', {style: {display: 'flex', gap: 28, alignItems: 'flex-start', flexWrap: 'wrap', marginTop: 10, justifyContent: 'center'}},
            e(Legend, {isDark: dark, textColor: lbText})
          )
        )
      )
    );
  }

  var root = ReactDOM.createRoot(document.getElementById('cdx-skill-optin-root'));
  root.render(e(App));
})();
</script>
{% endraw %}
