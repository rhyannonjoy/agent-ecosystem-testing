---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Skill On + Memory Suppressed"
permalink: /docs/open-ai-codex-flash/test-findings-skill-on-mem-suppressed
parent: OpenAI Codex - Flash
---

# Key Findings for Codex's Web Search Behavior<br>`GPT`-interpreted `/SKILL`-on + `/memories`-suppressed

---

> _Companion conditions include [`/SKILL-off` baseline](../open-ai-codex/codex-test-findings-extension.md) and [`/SKILL-on` opt-in](test-findings-skill-opt-in.md).
> This doc's limited to whether suppressing `/memories` isolates the `docs-consumption/SKILL` effect, and what that isolation exposes about retrieval-reporting.
> Experiment design in [Flash Runbook](runbook.md)._

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Confirm that `.agents/skills/docs-consumption/SKILL.md` exists in the workspace without `/memories` enabled
2. Run `python scripts/framework.py --test EC-6 --track vscode-codex-interpreted`
3. Review terminal output
4. Copy the provided prompt asking the agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
5. Open a new session in [VS Code Codex](https://learn.chatgpt.com/docs/codex/ide), paste the prompt into the chat window
6. Approve `curl` escalation, shell permission requests; skip requests for runs of existing workspace scripts
7. Capture the agent's full response; observe whether agent follows `/SKILL` protocol
8. Log structured metadata with `python scripts/log.py --results-dir results/docs-consumption-skill-flash`
9. Run `rollout_audit.py`, `memory_audit.py` to confirm `/memories` suppression, determine `/SKILL` influence

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard<br>Character<br>Limit** | _None detected with `curl`_: `curl` often `Content-Length`-verified: 91,877 bytes and 91,869 characters;<br>`web`: ~25,453 characters with `L54` cutpoint defined in [`/SKILL-off`](../open-ai-codex/codex-test-findings-extension.md), absent from [`/SKILL-on` opt-in](test-findings-skill-opt-in.md) |
| **Hard<br>Token<br>Limit** | _None detected with `curl`_: both common strategies consistently past `H2` 2,000 ceiling; <br>`curl`: ~23,000 tokens; `web`: ~6,364 tokens |
| **`/SKILL`<br>Discovery** | _Universal_: `100%` of session rollout logs cite `docs-consumption/SKILL` loaded, `100%` of agents start session mentioning `docs-consumption` specifically, then reading-reasoning with it |
| **`/SKILL`<br>Retrieval<br>Influence** | _Weak to none_: shifted towards `web` with `L54` cutpoint without explicit `/SKILL`-driven examination; `/SKILL`-phrasing didn't predict tool choice, agents often used similar language to support<br>different strategies  |
| **`/SKILL`<br>Reporting<br>Influence** | _Surface-level_: 100% of runs produced `skill-surface-only` false positives; every rollout emitted a completeness prefix, but new _under-confidence_ variant appeared in which agents labeled standard<br>`curl` fetches `UNVERIFIABLE` or `PARTIAL` |
| **`/memories`<br>Confound** | _Suppressed_: isolation achieved; no run included `/memories` signals in the form of rollout emissions - `system_memory_instruction`, `MEMORY.md`, `single-url-retrieval-measurement/SKILL`, `memory_mentioned` or<br>chat-rendered citations |
| **Recommendations** | _Absent_: No run generated meaningful remediation for common failures or tips for efficiency; only 19% of agents used a `Recommendation`-like label to point to `curl`-use - as though it weren't already common practice; the remaining agents ignored the requirement completely |

## Results Snapshot

| **Metric** | **Results** |
| --- | --- |
| **Track** | `T2` `GPT`-interpreted, VS Code with Codex Extension, `T3` sub-track |
| **Test** | [`EC-6` Raw GitHub Markdown](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md) |
| **`/SKILL` Condition** | `on` - `docs-consumption/SKILL` present and prompt-instructed; `/memories` suppressed |
| **LLMs Observed** | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5`, `GPT-5.6 Luna`, `GPT-5.6 Sol`, `GPT-5.6 Terra` |
| **Reasoning Levels** | `Light`, `Medium`, `High`, `Extra High`, `Ultra` |
| **Total Runs** | 26 |
| **`/SKILL` Loaded** | `100%` of session logs cite `docs-consumption/SKILL` injected into the agent's context |
| **`/SKILL` Path Emitted** | `12%` - `3/26` agents referenced the full `/SKILL` path in their own output |
| **Protocol Prefix Used** | `100%` emitted a completeness label, `100%` rollout-detected; `62%` `COMPLETE`, `31%` `PARTIAL`, `8%` `UNVERIFIABLE` |
| **`/SKILL` Language Used** | `77%` of runs contained at least one `/SKILL`-related phrase, read as a shortcut<br>rather than protocol-driven analysis |
| **Truncation: `Yes`** | `31%` - `8/26` agents reported the `web` `L54` cutpoint after `JSON-LD metadata,` |
| **Truncation: `Mixed`** | `15%` - `4/26` reported both a `web` limit and a full `curl` result |
| **Truncation: `Implicit`** | `4%` - `1/26` reasoned around a limit without naming it explicitly |
| **Truncation: `No`** | `50%` of runs had no truncation signal, largely `curl`-only runs that bypassed `web` |
| **Completeness Accurate** | `85%` - `22/26` correctly classified the fetch state, down from the [opt-in `100%`](test-findings-skill-opt-in.md#results-snapshot) |
| **Errors Examined** | `69%` - `18/26` accurately described their most common error, but ignored others |
| **Execution vs. Completeness** | `85%` - `22/26` distinguished _"the tool ran"_ from _"the full content arrived"_, down from opt-in `100%` |
| **Avoided Reframing** | `42%` - `11/26` avoided calling a partial or error-state fetch _"complete"_ or _"successful"_, down from opt-in `84%` |
| **Fix Recommended** | `0%` genuine; only `5/26` carried a label-only recommendation that restated baseline behavior, the remaining `21/26` offered none |
| **`/memories` Signals** | `0%` - `0/26` session logs carried any `## Memory` instruction, `MEMORY.md` citation, or competing `single-url-retrieval-measurement/SKILL` |
| **Retrieval Method** | `50%` - `13/26` `curl`-only; `27%` - `7/26` `web`-only; `23%` - `6/26` both |

## Key Findings

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`/memories` suppression isolates `/SKILL` cleanly** | All tests | `0/26` runs carried any memory signal across `system_memory_instruction`, `MEMORY.md`, `single-url-retrieval-measurement/SKILL`, and `memory_mentioned` | **This is the first condition where the `docs-consumption/SKILL` effect can be read without the [opt-in `/memories` confound](test-findings-skill-opt-in.md#memories-dominance)** |
| 2 | **`/SKILL` surface uptake _improves_ without `/memories` competing** | All tests | `100%` loaded (vs opt-in `87%`), `100%` named (vs `61%`), `100%` prefix rollout-detected (vs `58%`); only `/SKILL`-like _language_ dropped (`77%` vs `100%`) | **The opt-in `/memories` confound was suppressing surface uptake of `/SKILL`, not driving it; removing it lets `/SKILL` load and surface more reliably** |
| 3 | **Substantive compliance does _not_ improve** | All tests | `100%` - `26/26` read as `skill-surface-only` false positives; `0` genuine fix recommendations, identical to opt-in | **Removing `/memories` does not raise the compliance ceiling; shallow compliance is baseline agent behavior with the skill, not a `/memories` artifact** |
| 4 | **Retrieval shifts back to `web`; the `L54` cutpoint returns** | `Terra`, `Luna`, `Sol`, `Mini` runs | `50%` of runs showed a truncation signal (vs opt-in `22%`); `web`-only or `web`+`curl` runs appeared in `13/26`; the `~25,453`-character `L54` clip reappeared in `8` runs | **`/memories` was the `curl`-bypass driver (its _"stop trusting the clipped rendered view"_ lesson); suppressing it lets agents revert to `web` and re-hit the `L54` ceiling** |
| 5 | **Reporting discipline degrades; a new _under-confidence_ variant appears** | `Terra High`, `GPT-5.4 High`, `Luna Extra High` | Completeness accuracy fell to `85%` (vs `100%`), avoided-reframing to `42%` (vs `84%`); `3` runs labeled clean full `curl` fetches `UNVERIFIABLE` / `PARTIAL`, the inverse of opt-in's failure-as-success pattern | **Without `/memories` over-documenting common errors, agents swing from over-confident parroting to under-confident mislabeling; the `/SKILL` prefix becomes a stylistic label detached from the evidence** |
| 6 | **`/SKILL` phrasing doesn't predict tool choice** | `Sol High` vs `Sol Extra High` | `Sol High` (`curl`) and `Sol Extra High` (`web`) used near-identical _"the skill requires distinguishing a successful request from a complete response"_ phrasing to justify opposite retrieval choices | **`/SKILL`-derived language functions as a post-hoc narrative wrapper applied after the tool choice, not a genuine driver of retrieval strategy** |
| 7 | **Default-agent habits persist without memory** | `Luna`, `Sol` runs | The `Luna High` `zsh` read-only-variable bug, `/private/tmp` artifact naming collisions, and invented `/SKILL` attribution (`Sol`) all recurred with `/memories` fully suppressed | **Collision-prone scripting and over-extended citation are default agent behavior, not stale memory echoes; suppression rules out `/memories` as the source** |
| 8 | **Suppression exposes the false-positive floor** | All tests | With `/memories` removed, the `skill-surface-only` false-positive profile (`26/26`) is unchanged from opt-in; surface uptake rose while substantive compliance held flat | **This is the true control for the opt-in condition: the false-positive floor is the baseline agent + `/SKILL` compliance level, independent of `/memories`** |

## Memory Suppression

Together [`memory_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_audit.py) and
[`memory_analyzer`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_analyzer.py)
confirm that `.codex/memories` was absent across the sub-track while
[`rollout_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_audit.py) flags
`/docs-consumption/SKILL` injection, general session shape, and agent errors from each test's rollout log. Because rollouts include
what _can render each session_ and don't transcribe what _does render each session_, the visualizations below include a hybrid of
rollout metadata and agent self-reports from the chat.

The suppression holds cleanly: `0/26` runs carried the `## Memory` block in the `system_prompt`, and `0/26` referenced `MEMORY.md`,
the `raw_memories` file, `memory_summary.md`, or the competing `/memories/skills/single-url-retrieval-measurement/SKILL`. This is the
first condition in the flash experiment where `docs-consumption/SKILL` can be evaluated without `/memories` overprinting the session.
The contrast against the [opt-in sub-track](test-findings-skill-opt-in.md#memories-dominance) is stark: where opt-in sessions were
`77%` _both_ `/docs-consumption` + `/memories`, every suppressed session is `docs-consumption` alone.

{% raw %}
<svg class="cdx-skill-stack" viewBox="0 0 870 130" style="max-width: 870px; margin: 1rem auto; display: block;">
  <style>
    .cdx-skill-stack .bar { height: 36; }
    .cdx-skill-stack .neither { fill: #d0cec7; }
    .cdx-skill-stack .docs { fill: #1D9E75; }
    .cdx-skill-stack .both { fill: #378ADD; }
    .cdx-skill-stack text { fill: currentColor; font-family: inherit; }
    .cdx-skill-stack .rowlabel { font-size: 12px; opacity: 0.85; }
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

  <!-- opt-in row: 13% neither / 10% docs / 77% both -->
  <text class="rowlabel" x="10" y="28">opt-in (31)</text>
  <rect class="bar neither" x="86" y="14" width="100.1" height="36"/>
  <rect class="bar docs" x="186.1" y="14" width="77" height="36"/>
  <rect class="bar both" x="263.1" y="14" width="592.9" height="36"/>
  <text class="inside-dark" x="136.1" y="37" text-anchor="middle">13%</text>
  <text class="inside-light" x="224.6" y="37" text-anchor="middle">10%</text>
  <text class="inside-light" x="559.6" y="37" text-anchor="middle">77% both</text>

  <!-- T3 suppressed row: 100% docs-only -->
  <text class="rowlabel" x="10" y="80">T3 supp (26)</text>
  <rect class="bar docs" x="86" y="66" width="770" height="36"/>
  <text class="inside-light" x="471" y="89" text-anchor="middle">100% only /docs-consumption</text>

  <!-- Legend -->
  <rect x="86" y="112" width="8" height="8" class="neither"/>
  <text class="legend" x="98" y="119" text-anchor="start">neither</text>

  <rect x="180" y="112" width="8" height="8" class="docs"/>
  <text class="legend" x="192" y="119" text-anchor="start">only /docs-consumption</text>

  <rect x="380" y="112" width="8" height="8" class="both"/>
  <text class="legend" x="392" y="119" text-anchor="start">both /docs-consumption + /memories</text>
</svg>
{% endraw %}

Isolation, however, did not produce deeper compliance. `100%` of runs loaded `docs-consumption/SKILL`, `100%` mentioned it by name, and
`100%` emitted a completeness prefix — surface uptake that _exceeds_ the opt-in sub-track — yet `26/26` still read as `skill-surface-only`
false positives and `0` runs produced a genuine fix. The shallow compliance ceiling is independent of `/memories`. What suppression _did_
change was retrieval and reporting: with `/memories`'s _"stop trusting the clipped rendered view"_ lesson gone, agents reverted to the `web`
tool and re-hit the `L54` cutpoint (`50%` truncation signal vs opt-in `22%`), and a new _under-confidence_ variant appeared where clean full
fetches were labeled `UNVERIFIABLE` or `PARTIAL`. `/SKILL`-derived phrasing continued to function as a narrative wrapper rather than a strategy
driver — `Sol High` and `Sol Extra High` used near-identical justification language to choose `curl` and `web` respectively.

This heat map organizes runs by LLM-reasoning combination. Column colors group the signal type: `/SKILL` presence (green), `/SKILL` requirement
(light green, striped cells indicate presence but shallow compliance reading as false positives), retrieval (blue/purple for method, red/orange
for truncation), and mislabel direction. The retrieval and mislabel columns carry T3's distinctive story: `web` returns in `Terra` and `Luna`,
the `L54` `yes`-truncation cells light up red, and the under-confidence `under` cells mark clean fetches mislabeled as unresolved. The
`fix recs` column stays empty across every run — the `/SKILL`'s recommendation requirement went unmet even with the confound removed.

{% raw %}
<div id="cdx-skill-t3-root"></div>

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
.cdx-skill-cell.cdx-skill-cat { display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 600; color: #fff; border-color: transparent; }
.cdx-skill-cell.cdx-skill-cat.cdx-skill-cat-dark { color: #1a1a18; }
@media (prefers-color-scheme: dark) {
  .cdx-skill-cell.cdx-skill-stripe::after { background: repeating-linear-gradient(135deg, rgba(0,0,0,0.35), rgba(0,0,0,0.35) 3px, transparent 3px, transparent 6px); }
  .cdx-skill-cell.cdx-skill-cat.cdx-skill-cat-dark { color: #e8e6df; }
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

  var runs = [{"llm":"GPT-5.4 Mini","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"web","truncated":"yes","mislabel":"accurate","session":"019f8700"},{"llm":"GPT-5.4 Mini","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":0,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"both","truncated":"implicit","mislabel":"over","session":"019f8709"},{"llm":"GPT-5.4 Mini","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"both","truncated":"mixed","mislabel":"accurate","session":"019f8716"},{"llm":"GPT-5.4 Mini","level":"Extra High","skill_loaded":1,"skill_lang":0,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f871f"},{"llm":"GPT-5.4","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"both","truncated":"mixed","mislabel":"accurate","session":"019f87b1"},{"llm":"GPT-5.4","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"both","truncated":"mixed","mislabel":"accurate","session":"019f87b9"},{"llm":"GPT-5.4","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":0,"error_exam":0,"exec_vs_comp":0,"no_reframe":0,"fix_rec":0,"method":"both","truncated":"mixed","mislabel":"under","session":"019f87c2"},{"llm":"GPT-5.4","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f87cd"},{"llm":"GPT-5.5","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f87e9"},{"llm":"GPT-5.5","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f87f3"},{"llm":"GPT-5.5","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f87fb"},{"llm":"GPT-5.5","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f8803"},{"llm":"GPT-5.6 Luna","level":"Light","skill_loaded":1,"skill_lang":0,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"web","truncated":"yes","mislabel":"accurate","session":"019f8816"},{"llm":"GPT-5.6 Luna","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f8823"},{"llm":"GPT-5.6 Luna","level":"High","skill_loaded":1,"skill_lang":0,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":0,"exec_vs_comp":0,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f882b"},{"llm":"GPT-5.6 Luna","level":"Extra High","skill_loaded":1,"skill_lang":0,"skill_path":1,"prefix":1,"accuracy":0,"error_exam":1,"exec_vs_comp":0,"no_reframe":0,"fix_rec":0,"method":"both","truncated":"yes","mislabel":"under","session":"019f8833"},{"llm":"GPT-5.6 Sol","level":"Light","skill_loaded":1,"skill_lang":0,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f8b5c"},{"llm":"GPT-5.6 Sol","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f8b64"},{"llm":"GPT-5.6 Sol","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f8b6e"},{"llm":"GPT-5.6 Sol","level":"Extra High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"web","truncated":"yes","mislabel":"accurate","session":"019f8b74"},{"llm":"GPT-5.6 Sol","level":"Ultra","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"accurate","session":"019f8b7d"},{"llm":"GPT-5.6 Terra","level":"Light","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"web","truncated":"yes","mislabel":"accurate","session":"019f8be2"},{"llm":"GPT-5.6 Terra","level":"Medium","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"web","truncated":"yes","mislabel":"accurate","session":"019f8be9"},{"llm":"GPT-5.6 Terra","level":"High","skill_loaded":1,"skill_lang":1,"skill_path":0,"prefix":1,"accuracy":0,"error_exam":1,"exec_vs_comp":0,"no_reframe":0,"fix_rec":0,"method":"curl","truncated":"no","mislabel":"under","session":"019f8bef"},{"llm":"GPT-5.6 Terra","level":"Extra High","skill_loaded":1,"skill_lang":0,"skill_path":1,"prefix":1,"accuracy":1,"error_exam":0,"exec_vs_comp":1,"no_reframe":0,"fix_rec":0,"method":"web","truncated":"yes","mislabel":"accurate","session":"019f8bf5"},{"llm":"GPT-5.6 Terra","level":"Ultra","skill_loaded":1,"skill_lang":1,"skill_path":1,"prefix":1,"accuracy":1,"error_exam":1,"exec_vs_comp":1,"no_reframe":1,"fix_rec":0,"method":"web","truncated":"yes","mislabel":"accurate","session":"019f8bfc"}];

  var PRESENCE_COLS = [
    {id: 'skill_loaded', label: '/SKILL\nloaded', full: '/SKILL loaded', group: 'req'},
    {id: 'skill_lang', label: '/SKILL\nlang', full: '/SKILL language', group: 'req'},
    {id: 'skill_path', label: '/SKILL\npath', full: '/SKILL path', group: 'req'}
  ];

  var REQ_COLS = [
    {id: 'prefix', label: 'prefix', full: 'protocol prefix', group: 'reqSub'},
    {id: 'accuracy', label: 'accuracy', full: 'completeness accuracy', group: 'reqSub'},
    {id: 'error_exam', label: 'error\nexam', full: 'error examined', group: 'reqSub'},
    {id: 'exec_vs_comp', label: 'exec\ncomp', full: 'execution vs completeness', group: 'reqSub'},
    {id: 'no_reframe', label: 'no\nreframing', full: 'no reframing', group: 'reqSub'},
    {id: 'fix_rec', label: 'fix\nrecs', full: 'fix recommendation', group: 'reqSub'}
  ];

  var RETR_COLS = [
    {id: 'method', label: 'method', full: 'retrieval method', group: 'ret', type: 'cat'},
    {id: 'truncated', label: 'trunc', full: 'truncation signal', group: 'ret', type: 'cat'}
  ];

  var ML_COLS = [
    {id: 'mislabel', label: 'mislabel', full: 'mislabel direction', group: 'ml', type: 'cat'}
  ];

  var ALL_COLS = PRESENCE_COLS.concat(REQ_COLS, RETR_COLS, ML_COLS);
  var SPACER_AFTER = [PRESENCE_COLS.length, PRESENCE_COLS.length + REQ_COLS.length, PRESENCE_COLS.length + REQ_COLS.length + RETR_COLS.length];

  var STRIPE_COLS = {skill_lang: true, accuracy: true, error_exam: true, exec_vs_comp: true, no_reframe: true};

  var GROUP_COLORS = {
    req: {dark: '#0F6E56', light: '#1D9E75'},
    reqSub: {dark: '#3BAE7C', light: '#5DC99A'}
  };

  var CAT_COLORS = {
    method: {
      web:   {dark: '#185FA5', light: '#378ADD', label: 'web'},
      curl:  {dark: '#0F6E56', light: '#1D9E75', label: 'curl'},
      both:  {dark: '#5A4A9C', light: '#7A5BC9', label: 'both'}
    },
    truncated: {
      yes:      {dark: '#A03A3A', light: '#C94B4B', label: 'yes'},
      mixed:    {dark: '#B5703A', light: '#D98A3D', label: 'mix'},
      implicit: {dark: '#A8863A', light: '#C9A23D', label: 'impl'},
      no:       {dark: '#6E6E66', light: '#9A9A92', label: 'no'}
    },
    mislabel: {
      accurate: {dark: '#3BAE7C', light: '#5DC99A', label: 'acc'},
      under:    {dark: '#185FA5', light: '#378ADD', label: 'under'},
      over:     {dark: '#B5703A', light: '#D98A3D', label: 'over'}
    }
  };

  function spacerClass(i) {
    return SPACER_AFTER.indexOf(i) >= 0 ? 'cdx-skill-spacer' : '';
  }

  function Cell(props) {
    var dark = props.dark;
    var col = props.col;
    var val = props.val;
    var tip = props.tip;
    var mode = dark ? 'dark' : 'light';

    if (col.type === 'cat') {
      var spec = CAT_COLORS[col.id][val];
      if (!spec) {
        return e('div', {title: tip, className: 'cdx-skill-cell', style: {background: 'transparent', borderColor: 'transparent'}});
      }
      var isLightText = (val === 'no' || val === 'impl' || val === 'mix' || val === 'acc' || val === 'over');
      var catClass = 'cdx-skill-cell cdx-skill-cat' + (isLightText ? ' cdx-skill-cat-dark' : '');
      return e('div', {
        title: tip,
        className: catClass,
        style: {background: spec[mode]}
      }, spec.label);
    }

    var baseColor = GROUP_COLORS[col.group][mode];
    var className = 'cdx-skill-cell';
    if (val && STRIPE_COLS[col.id]) className += ' cdx-skill-stripe';
    return e('div', {
      title: tip,
      className: className,
      style: val ? {background: baseColor, borderColor: baseColor} : {background: 'transparent', borderColor: 'transparent'}
    });
  }

  function HeaderRow(props) {
    var tc = props.tc;
    var labelW = props.labelW;
    return e('thead', null,
      e('tr', null,
        e('th', {className: 'cdx-skill-rh', style: {minWidth: labelW, color: tc}}, 'LLM / Reasoning'),
        ALL_COLS.map(function(col, i) {
          var lines = col.label.split(/\n/);
          return e('th', {key: col.id, className: spacerClass(i), title: col.full, style: {color: tc, lineHeight: 1.1}},
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
    var rowTip = run.llm + ' ' + level + '\nsession: ' + run.session;
    return e('tr', {key: run.session, title: rowTip},
      e('td', {className: 'cdx-skill-rl cdx-skill-llm', style: {color: tc, maxWidth: labelW, width: labelW}},
        run.llm + ' ' + level
      ),
      ALL_COLS.map(function(col, i) {
        var val = run[col.id];
        var isShallow = val && STRIPE_COLS[col.id];
        var label;
        if (col.type === 'cat') {
          label = val;
        } else if (col.id === 'prefix' && val) {
          label = 'prefix';
        } else if (isShallow) {
          label = 'false positive';
        } else {
          label = val ? 'yes' : 'no';
        }
        var tip = col.full + ': ' + label;
        if (col.id === 'error_exam' && val) {
          tip = 'DNS/sandbox error examined: ' + label;
        }
        return e('td', {key: col.id, className: spacerClass(i)},
          e(Cell, {dark: dark, col: col, val: val, tip: tip, textColor: tc})
        );
      })
    );
  }

  function Legend(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var mode = dark ? 'dark' : 'light';
    var sections = [
      {
        key: 'req',
        label: '<code>/docs-consumption/SKILL</code> presence',
        color: GROUP_COLORS.req[mode],
        cols: [
          {name: '/SKILL loaded', desc: 'in <code>&lt;skills_instructions&gt;</code>'},
          {name: '/SKILL lang', desc: 'use <code>/SKILL</code>-like phrases'},
          {name: '/SKILL path', desc: 'reference full path'}
        ]
      },
      {
        key: 'reqSub',
        label: '<code>/docs-consumption/SKILL</code> requirement',
        color: GROUP_COLORS.reqSub[mode],
        cols: [
          {name: 'prefix', desc: '<code>COMPLETE/PARTIAL/UNVERIFIABLE</code>'},
          {name: 'accuracy', desc: 'classify fetch state correctly'},
          {name: 'error exam', desc: 'examine embedded failures'},
          {name: 'exec comp', desc: 'flag tool ran from full content'},
          {name: 'no reframe', desc: 'no reframing error as success'},
          {name: 'fix recs', desc: 'suggest remediation'}
        ]
      },
      {
        key: 'ret',
        label: 'retrieval',
        color: CAT_COLORS.method.curl[mode],
        cols: [
          {name: 'method', desc: '<span style="color:#378ADD">web</span> / <span style="color:#1D9E75">curl</span> / <span style="color:#7A5BC9">both</span>'},
          {name: 'trunc', desc: '<span style="color:#C94B4B">yes</span> / <span style="color:#D98A3D">mix</span> / <span style="color:#C9A23D">impl</span> / <span style="color:#9A9A92">no</span>'}
        ]
      },
      {
        key: 'ml',
        label: 'mislabel direction',
        color: CAT_COLORS.mislabel.under[mode],
        cols: [
          {name: 'accurate', desc: 'label matches evidence'},
          {name: 'under', desc: 'clean full fetch labeled <code>UNVERIFIABLE</code>/<code>PARTIAL</code>'},
          {name: 'over', desc: '<code>COMPLETE</code> despite truncation signal'}
        ]
      }
    ];
    return e('div', {style: {fontSize: 11, marginTop: 8, display: 'flex', gap: 28, justifyContent: 'center', flexWrap: 'wrap'}},
      sections.map(function(s) {
        return e('div', {key: s.key, style: {width: 230}},
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
        e(HeaderRow, {tc: tc, labelW: labelW}),
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

  var root = ReactDOM.createRoot(document.getElementById('cdx-skill-t3-root'));
  root.render(e(App));
})();
</script>
{% endraw %}
