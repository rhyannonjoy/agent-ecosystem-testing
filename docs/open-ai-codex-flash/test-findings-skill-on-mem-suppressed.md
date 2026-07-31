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
| **`/SKILL`<br>Discovery** | _Universal_: 100% of session rollout logs cite `docs-consumption/SKILL` loaded, 100% of agents start session mentioning `docs-consumption` specifically, then reading-reasoning with it |
| **`/SKILL`<br>Retrieval<br>Influence** | _Weak to none_: shifted towards `web` with `L54` cutpoint without explicit `/SKILL`-driven examination; `/SKILL`-phrasing didn't predict tool choice, agents often used similar language to support<br>different strategies  |
| **`/SKILL`<br>Reporting<br>Influence** | _Surface-level_: 100% of runs produced `skill-surface-only` false positives; every rollout emitted a completeness prefix, but new _under-confidence_ variant appeared in which agents labeled standard<br>`curl` fetches `UNVERIFIABLE` or `PARTIAL` |
| **`/memories`<br>Confound** | _Suppressed_: isolation achieved; no run included `/memories` signals in the form of rollout emissions - `system_memory_instruction`, `MEMORY.md`, `single-url-retrieval-measurement/SKILL`, `memory_mentioned` or<br>chat-rendered citations |
| **Recommendations** | _Absent_: No run generated meaningful remediation for common failures or tips for efficiency; only 19% of agents used a `Recommendation`-like label to point to `curl`-use - as though it weren't already common practice; the remaining agents ignored the requirement completely |

## Results Snapshot

| **Metric** | **Results** |
| --- | --- |
| **Track** | `T2` `GPT`-interpreted, VS Code with Codex Extension, `T3` sub-track |
| **Test** | [`EC-6` Raw GitHub Markdown](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md) |
| **`/SKILL` Condition** | `on + /memories suppressed`: `docs-consumption/SKILL` present and prompt-instructed,<br>`/memories` not enabled |
| **LLMs Observed** | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5`, `GPT-5.6 Luna`, `GPT-5.6 Sol`, `GPT-5.6 Terra` |
| **Reasoning Levels** | `Light`, `Medium`, `High`, `Extra High`, `Ultra` |
| **Total Runs** | 26 |
| **`/SKILL` Loaded** | 100% of session logs cite `docs-consumption/SKILL` injected into the agent's context |
| **`/SKILL` Path Emitted** | 12% of agents wrote the full `/SKILL` path rather than mentioning it in passing |
| **`/SKILL` Protocol<br>Prefix Used** | 100% emitted a completeness label -<br>`COMPLETE`: 16<br>`PARTIAL`: 8<br>`UNVERIFIABLE`: 2 |
| **`/SKILL` Language Used** | 77% of runs contained at least one `/SKILL`-related phrase, but read as a<br>shortcut rather than protocol-driven analysis |
| **Truncation: `Yes`** | 31% of agents reported the `web` `L54` cutpoint after `JSON-LD metadata,` |
| **Truncation: `Mixed`** | 15% of agents reported both a limited `web` window-view and a full `curl` payload |
| **Truncation: `Implicit`** | One agent reasoned around a `web` limit without naming it explicitly |
| **Truncation: `No`** | 50% of runs had no truncation signal, largely because these agents bypassed `web` for `curl` |
| **Completeness Accurate** | 85% of agents correctly classified the fetch state - down from [`opt-in`'s 100%](test-findings-skill-opt-in.md#results-snapshot) |
| **Errors Examined** | 69% of agents accurately described their most common error, but ignored others |
| **Execution vs. Completeness** | 85% of agents distinguished _"the tool ran"_ from _"the full content arrived"_ -<br>down from `opt-in`'s 100% |
| **Avoided Reframing** | 42% of agents avoided calling a partial or error-state fetch _"complete"_ or<br>_"successful"_ - down from `opt-in`'s 84% |
| **Fix Recommended** | No substantial recommendations; 5 agents used a `Recommendation` label that<br>restated baseline behavior, the remaining 21 offered none |
| **`/memories` Signals** | No session rollout or agentic self-report included `## Memory` instruction, `MEMORY.md`<br>citations, or competing `/memories/skills/single-url-retrieval-measurement/SKILL` use |
| **Retrieval Method** | 50% of agents relied completely on `curl`, while 27% relied completely on `web`,<br>and 23% used both |

## Key Findings

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`/memories` suppression successfully isolates `/SKILL` influence** | All tests | No sessions emitted `/memories` signals observed in [`/SKILL opt-in`](test-findings-skill-opt-in.md#memories-dominance) - references and/or explicit citations pointing to `system_memory_instruction`, `MEMORY.md`, `single-url-retrieval-measurement/SKILL` | **[As documented](https://learn.chatgpt.com/docs/customization/memories?surface=app), `/memories`-domainance isn't default Codex behavior, but requires configuration, explicit activation** |
| 2 | **`/SKILL`-influence improves without competing `/memories`** | All tests | 100% of agents named vs 61% of `opt-in`, 100% of agents used a protocol prefix vs 58% of `opt-in`; only `/SKILL`-like language dropped to 77% | **`opt-in`'s `/memories` successfully suppressed `/SKILL`, deactivating `/memories` allows for more reliable `/SKILL` loading and authority** |
| 3 | **`/SKILL` compliance depth doesn't improve** | All tests | 100% of agents generated `skill-surface-only` false positives with zero meaningful efficiency recommendations, seemingly recycling language from `opt-in` | **Deactivating `/memories` doesn't raise `/SKILL` compliance ceiling; agentic performance reflects baseline `EC-6` behavior** |
| 4 | **Retrieval shifts to `web` with the `L54` cutpoint** | `Mini` `Luna` `Sol` `Terra` | 50% of agents self-reported truncation signals vs 22% of `opt-in`; `web`-only or `web`+`curl` runs appeared in 13/26; ~25,453-character count with `L54` clip reappeared in 8 runs | **`/memories` were the `curl`-bypass driver, influenced by _"stop trusting the clipped rendered view"_; suppressing `/memories` allows for baseline retrieval path variety** |
| 5 | **Reporting discipline degrades with _under-confidence_ variant** | `Terra`<br>`High`<br>`5.4`<br>`High` `Luna xHigh` | Completeness accuracy fell to 85% vs 100% of `opt-in`, avoided reframing to 42% vs 84% of `opt-in`; Three runs labeled fully verifed `curl` fetches `UNVERIFIABLE` or `PARTIAL` - inverse of baseline _failure-as-success_ pattern | **Without `/memories` over-documenting common errors, agents swing from over-confident parroting to under-confident mislabeling; `/SKILL` prefix stylistic, detached from evidence** |
| 6 | **`/SKILL` phrasing doesn't predict tool choice** | `Sol`<br>`High` `Sol xHigh` | `Sol High` used `curl` while `Sol Extra High` used `web` with near-identical _"the skill requires distinguishing a successful request from a complete response"_ to justify opposing retrieval tools | **`/SKILL`-derived language functions as a post-hoc narrative wrapper applied after the tool choice, not a verified driver of retrieval strategy** |
| 7 | **Common agent flaws persist without `/memories`** | `Luna` `Sol` | `Luna High` not reporting `zsh` read-only variable bug, artifact naming collisions, and `Sol`'s invented `/SKILL` attributions all recurred with `/memories` suppressed | **Collision-prone scripting and over-extended citation are default agent behavior; suppression rules out `/memories` as the source** |
| 8 | **Suppression exposes the false-positive floor** | All tests | Without `/memories`, the `skill-surface-only` false-positive profile remains unchanged from `opt-in`; influence-tracking rose while substantive compliance flattened | **Compliance reduced to `/SKILL`-framing, but false-positive floor is baseline agentic performance, independent of `/memories`** |

## False Positive Floor

Together [`memory_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_audit.py) and
[`memory_analyzer`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_analyzer.py)
confirm that `.codex/memories` was absent while
[`rollout_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/rollout_audit.py) flags
`/docs-consumption/SKILL` loading, general session shape, and agent errors from each test's rollout log. Because rollouts include
what _can render each session_ and don't transcribe what _does render each session_, the visualizations below include a hybrid of
rollout metadata and agent self-reports from the chat.

With `opt-in` conditions including `/docs-consumption/SKILL` presence - but not explicitly mentioned in the prompt - and available
`/memories`, most agents never declared a preference, and the results exhibited a type of co-occurence. With the `/SKILL` explicitly mentioned
in the prompt and `/memories` deactivated, results exhibited `/SKILL` isolation:

{% raw %}
<svg class="cdx-skill-stack" viewBox="0 0 870 130" style="max-width: 870px; margin: 1rem auto; display: block;">
  <style>
    .cdx-skill-stack .bar { height: 36; }
    .cdx-skill-stack .neither { fill: #d0cec7; }
    .cdx-skill-stack .docs { fill: #1D9E75; }
    .cdx-skill-stack .both { fill: #378ADD; }
    .cdx-skill-stack text { fill: currentColor; font-family: inherit; }
    .cdx-skill-stack .rowlabel { font-size: 12px; opacity: 0.85; }
    .cdx-skill-stack .code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 10px; font-weight: 400; }
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
  <text class="rowlabel code" x="10" y="28">opt-in</text>
  <rect class="bar neither" x="86" y="14" width="100.1" height="36"/>
  <rect class="bar docs" x="186.1" y="14" width="77" height="36"/>
  <rect class="bar both" x="263.1" y="14" width="592.9" height="36"/>
  <text class="inside-dark" x="136.1" y="37" text-anchor="middle">13%</text>
  <text class="inside-light" x="224.6" y="37" text-anchor="middle">10%</text>
  <text class="inside-light" x="559.6" y="37" text-anchor="middle">77% both</text>

  <!-- T3 suppressed row: 100% docs-only -->
  <text class="rowlabel" x="10" y="76"><tspan class="code" x="10" dy="0">on + /mem</tspan><tspan class="code" x="10" dy="14">suppressed</tspan></text>
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

`/SKILL` isolation didn't produce deeper compliance. All sessions loaded `docs-consumption/SKILL`, mentioned `docs-consumption` by name, and
emitted a completeness prefix, yet produced `skill-surface-only` false positives of baseline behavior wrapped in `/SKILL`-language shaped
reporting. The following profile classification seeks to illustrate `/SKILL` compliance scoring:

| **Profile** | **Pattern** | **Example** |
| --- | --- | --- |
| `baseline` | `/SKILL` not present, behavior matches<br>pre-`/SKILL` results | No protocol language, intermittently<br>describes failures |
| `skill-surface`<br>`only` | `/SKILL` loaded with cosmetic adoption,<br>no meaningful analysis | Uses `COMPLETE` prefix, but intermittently<br>describes failures |
| `skill-influenced` | `/SKILL` present, partially adopted,<br>description elevated to analysis | Distinguishes tool-execution from content delivery,<br>but reframes errors as successes |
| `memory-dominant` | `/memories` override `/SKILL` protocol | Follows stale `/memories` clippings instead of<br>live `/SKILL` instructions |
| `unclear` | Insufficient evidence for classification | Inconsistent across fields or partially truncated |

While `/SKILL` isolation allowed for a return to baseline retrieval variety, expanding from `/memories`' choice `curl` to include
`web`, or a combination of both, the `/SKILL` failed to improve report depth, defining a false positive floor:

| **Behavior** | **Observation** |
| --- | --- |
| **Longer Synthesis, Same Partial View** | Produces more details without protocol analysis |
| **Protocol Misattribution** | Reports with protocol prefix, but the label doesn't match tool result;<br>uses identical `/SKILL`-phrases to justify opposing retrieval strategies |
| **_Recommendationless_ Recommendation** | Uses _"Recommendation"_ label without diagnosis, or suggests<br>an already common strategy, _"use `curl`"_ |
| **Failure Under-reporting, Reframing** | Describes errors in without examination while reporting _"the fetch worked"_<br>or _"the content is complete"_ |
| **Tool Rerouting, No Disclosure** | Pivots mid-path or abandons capabilities without explanation |

### `/SKILL` Compliance

organizes runs by LLM-reasoning combination and
tracks `/SKILL` protocol compliance as binary signals: `/SKILL` presence (green) and `/SKILL` requirement (light green, striped cells indicate
presence but shallow compliance reading as false positives). The `fix recs` column stays empty across every run - the `/SKILL`'s recommendation
requirement went unmet even with the confound removed.

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

  var ALL_COLS = PRESENCE_COLS.concat(REQ_COLS);
  var SPACER_AFTER = [PRESENCE_COLS.length, PRESENCE_COLS.length + REQ_COLS.length];

  var STRIPE_COLS = {skill_lang: true, accuracy: true, error_exam: true, exec_vs_comp: true, no_reframe: true};

  var GROUP_COLORS = {
    req: {dark: '#0F6E56', light: '#1D9E75'},
    reqSub: {dark: '#3BAE7C', light: '#5DC99A'}
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
        if (col.id === 'prefix' && val) {
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
      }
    ];
    return e('div', {style: {fontSize: 11, marginTop: 8, display: 'flex', flexDirection: 'column', gap: 16}},
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
          e('div', {style: {display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'center', gap: 28}},
            e('div', null,
              e(HeatmapTable, {isDark: dark, large: false}),
              e('p', {className: 'cdx-skill-hint'}, '↗ click to expand')
            ),
            e('div', {style: {flex: '0 0 auto', marginTop: 4}},
              e(Legend, {isDark: dark})
            )
          )
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
          e('div', {style: {display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'center', gap: 28}},
            e('div', null,
              e(HeatmapTable, {isDark: dark, large: true, textColor: lbText})
            ),
            e('div', {style: {flex: '0 0 auto', marginTop: 4}},
              e(Legend, {isDark: dark, textColor: lbText})
            )
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

### Retrieval Outcomes

Each cell carries one signal as its fill (`method`: `web`, `curl`, or `both`) and folds the other two
into the cell border and overlay: the border encodes `truncation` tier (`yes` = red, `mixed` = amber, `implicit` = dashed yellow, `no` = faint),
and a diagonal stripe marks `mislabel` cells where the completeness label diverges from the evidence. `web` returns in `Terra` and `Luna` re-hit
the `L54` cutpoint, the `yes`-truncation cells ring red, and the under-confidence `under` cells stripe clean `curl` fetches mislabeled
`UNVERIFIABLE` or `PARTIAL`.

{% raw %}
<div id="cdx-t3b-root"></div>

<style>
.cdx-t3b-wrap { overflow-x: auto; display: flex; justify-content: center; }
table.cdx-t3b { border-collapse: collapse; width: auto; }
table.cdx-t3b th { font-size: 10px; font-weight: 500; padding: 3px 6px; text-align: center; white-space: nowrap; color: inherit; }
table.cdx-t3b th.cdx-t3b-rh { text-align: left; padding-left: 0; padding-right: 6px; }
table.cdx-t3b th .cdx-t3b-sub { font-weight: 400; font-size: 9px; opacity: 0.55; display: block; }
table.cdx-t3b td { padding: 2px 2px; text-align: center; vertical-align: middle; }
table.cdx-t3b td.cdx-t3b-rl { font-size: 11px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 8px; color: inherit; vertical-align: middle; }
table.cdx-t3b td.cdx-t3b-llm { font-size: 10px; opacity: 0.7; padding-left: 10px; }
.cdx-t3b-cell { border-radius: 3px; display: flex; align-items: center; justify-content: center; width: 44px; height: 24px; margin: 1px auto; cursor: help; font-size: 10px; font-weight: 600; position: relative; box-sizing: border-box; border: 2px solid rgba(128,128,128,0.22); }
.cdx-t3b-stripe::after { content: ''; position: absolute; inset: 0; border-radius: 3px; background: repeating-linear-gradient(135deg, rgba(255,255,255,0.45), rgba(255,255,255,0.45) 3px, transparent 3px, transparent 6px); pointer-events: none; }
html[data-theme="dark"] .cdx-t3b-stripe::after { background: repeating-linear-gradient(135deg, rgba(0,0,0,0.35), rgba(0,0,0,0.35) 3px, transparent 3px, transparent 6px); }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .cdx-t3b-stripe::after { background: repeating-linear-gradient(135deg, rgba(0,0,0,0.35), rgba(0,0,0,0.35) 3px, transparent 3px, transparent 6px); }
}
.cdx-t3b-banner { font-size: 10px; font-weight: 600; letter-spacing: 0.04em; opacity: 0.6; text-align: center; }
.cdx-t3b-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; }
.cdx-t3b-overlay { position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,0.78); display: flex; align-items: center; justify-content: center; padding: 20px; }
.cdx-t3b-overlay-inner { border-radius: 10px; padding: 22px 26px; max-width: 99vw; max-height: 93vh; overflow: auto; position: relative; }
.cdx-t3b-close { position: absolute; top: 10px; right: 12px; background: none; border: none; font-size: 20px; cursor: pointer; opacity: 0.5; line-height: 1; }
.cdx-t3b-close:hover { opacity: 1; }
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

  // Single page type: EC-6 (Raw GitHub Markdown, ~92 KB). One matrix: rows are
  // LLM version, columns are reasoning level. Each cell encodes three signals —
  // fill = method, border = truncation tier, stripe = mislabel — and carries that
  // run's log-label surface note in its tooltip.

  var LEVELS = [
    {k: 'L',  label: 'Light'},
    {k: 'M',  label: 'Medium'},
    {k: 'H',  label: 'High'},
    {k: 'XH', label: 'Extra High'},
    {k: 'U',  label: 'Ultra'}
  ];

  var MODELS = [
    {k: '5.4m',  label: 'GPT-5.4-Mini', short: '5.4m'},
    {k: '5.4',   label: 'GPT-5.4',      short: '5.4'},
    {k: '5.5',   label: 'GPT-5.5',      short: '5.5'},
    {k: 'luna',  label: 'GPT-5.6 Luna', short: 'Luna'},
    {k: 'sol',   label: 'GPT-5.6 Sol',  short: 'Sol'},
    {k: 'terra', label: 'GPT-5.6 Terra', short: 'Terra'}
  ];

  // T3 semantic coloring: curl = complete (green), web = truncated path (blue),
  // both = purple; truncation yes = red, no = grey; mislabel accurate = green,
  // under = blue (success mislabeled unresolved), over = orange.
  var COLORS = {
    method: {
      web:  {bgLight:'#378ADD', bgDark:'#185FA5', fg:'#fff',     label:'w',     full:'web'},
      curl: {bgLight:'#1D9E75', bgDark:'#0F6E56', fg:'#fff',     label:'c',     full:'curl'},
      both: {bgLight:'#7A5BC9', bgDark:'#5A4A9C', fg:'#fff',     label:'w + c', full:'both'}
    },
    truncated: {
      yes:      {bgLight:'#C94B4B', bgDark:'#A03A3A', fg:'#fff',     label:'yes'},
      mixed:    {bgLight:'#D98A3D', bgDark:'#B5703A', fg:'#1a1a18',  label:'mix'},
      implicit: {bgLight:'#C9A23D', bgDark:'#A8863A', fg:'#1a1a18',  label:'impl'},
      no:       {bgLight:'#9A9A92', bgDark:'#6E6E66', fg:'#1a1a18',  label:'no'}
    },
    mislabel: {
      accurate: {bgLight:'#5DC99A', bgDark:'#3BAE7C', fg:'#1a1a18',  label:'acc'},
      under:    {bgLight:'#378ADD', bgDark:'#185FA5', fg:'#fff',     label:'under'},
      over:     {bgLight:'#D98A3D', bgDark:'#B5703A', fg:'#1a1a18',  label:'over'}
    }
  };

  var CATEGORY_DESC = {
    method: {
      web: 'text extraction, often L54-clipped',
      curl: 'response, often Content-Length-verified',
      both: 'web and curl both used'
    },
    truncated: {
      yes: 'web L54 cutpoint reported explicitly',
      mixed: 'both web limit and full curl result reported',
      implicit: 'truncation implied but not explicitly named',
      no: 'no truncation signal, curl-complete'
    },
    mislabel: {
      accurate: 'completeness label matches evidence',
      under: 'curl-complete labeled UNVERIFIABLE or PARTIAL',
      over: 'COMPLETE despite truncation signal'
    }
  };

  // Per-run outcome + log-label surface note, keyed model:level.
  var RUNS = {
    '5.4m:L':  {method:'web',  truncated:'yes',      mislabel:'accurate', note:'curl_dns_blocked + web_open_partial_only + skill_instructed_docs_consumption + 37s (FAIL)'},
    '5.4m:M':  {method:'both', truncated:'implicit', mislabel:'over',     note:'curl_91877_bytes + web_view_truncation_undisclosed + skill_instructed_docs_consumption + 1m18s'},
    '5.4m:H':  {method:'both', truncated:'mixed',    mislabel:'accurate', note:'curl_91869_chars + web_open_clip_l54_disclosed + skill_instructed_docs_consumption + 1m45s'},
    '5.4m:XH': {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars + sandbox_empty_response_then_escalated + tiktoken_unavailable_undisclosed + skill_instructed_docs_consumption + 6m26s'},
    '5.4:L':   {method:'both', truncated:'mixed',    mislabel:'accurate', note:'curl_91869_chars + web_open_windowed_l33_visible_of_l55 + skill_instructed_docs_consumption + 1m1s'},
    '5.4:M':   {method:'both', truncated:'mixed',    mislabel:'accurate', note:'curl_91877_chars + web_open_clip_l54_undisclosed_in_report + skill_instructed_docs_consumption + 1m7s'},
    '5.4:H':   {method:'both', truncated:'mixed',    mislabel:'under',    note:'curl_91877_chars_eof_clean + web_open_clip_l54_disclosed + self_labeled_partial_mismatch + skill_instructed_docs_consumption + 2m20s'},
    '5.4:XH':  {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + sandbox_dns_failure_disclosed + web_not_invoked + skill_instructed_docs_consumption + 2m17s'},
    '5.5:L':   {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + dns_failure_disclosed_3x + no_web + skill_instructed_docs_consumption + 46s'},
    '5.5:M':   {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + headers_request_id_reuse_flagged + no_web + skill_instructed_docs_consumption + 1m0.7s'},
    '5.5:H':   {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_byte_char_gap_reasoned + no_web + skill_instructed_docs_consumption + 1m23s'},
    '5.5:XH':  {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + hyphenated_artifact_naming_variant + no_web + skill_instructed_docs_consumption + 1m29s'},
    'luna:L':  {method:'web',  truncated:'yes',      mislabel:'accurate', note:'web_24884_chars_partial_L54 + curl_dns_failure_not_escalated + shell_dominant_flag + skill_instructed_docs_consumption + 29s'},
    'luna:M':  {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + artifact_naming_collision + tool_visibility_undercount + skill_instructed_docs_consumption + 47s'},
    'luna:H':  {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + zsh_readonly_var_undisclosed + skill_instructed_docs_consumption + 2m8s'},
    'luna:XH': {method:'both', truncated:'yes',      mislabel:'under',    note:'web_24885_chars_partial_L54 + curl_91869_chars_verified + early_exit_partial_label + skill_instructed_docs_consumption + 3m13s'},
    'sol:L':   {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + ruby_local_inspection + scope_overgeneralized_skill_citation + skill_instructed_docs_consumption + 57s'},
    'sol:M':   {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + xcache_hit_zero_hits_contradiction + skill_instructed_docs_consumption + 1m7s'},
    'sol:H':   {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + invented_skill_attribution + skill_instructed_docs_consumption + 1m16s'},
    'sol:XH':  {method:'web',  truncated:'yes',      mislabel:'accurate', note:'web_25453_chars_partial_L54 + js_textencoder_error_disclosed + skill_instructed_docs_consumption + 1m29s'},
    'sol:U':   {method:'curl', truncated:'no',       mislabel:'accurate', note:'curl_91869_chars_content_length_match + artifact_naming_collision + undisclosed_ui_truncation_flag + skill_instructed_docs_consumption + 2m44s'},
    'terra:L': {method:'web',  truncated:'yes',      mislabel:'accurate', note:'web_25453_chars_partial_L54 + est_not_confirmed_char_count + skill_instructed_docs_consumption + 48s'},
    'terra:M': {method:'web',  truncated:'yes',      mislabel:'accurate', note:'web_25453_chars_partial_L54 + tool_vs_self_report_tension + skill_instructed_docs_consumption + 32s'},
    'terra:H': {method:'curl', truncated:'no',       mislabel:'under',    note:'curl_91869_chars_content_length_match + success_mislabeled_unverifiable + local_verification + skill_instructed_docs_consumption + 55s'},
    'terra:XH':{method:'web',  truncated:'yes',      mislabel:'accurate', note:'web_25453_chars_partial_L54 + secondary_truncation_underreported + skill_instructed_docs_consumption + 2m1s'},
    'terra:U': {method:'web',  truncated:'yes',      mislabel:'accurate', note:'web_25453_chars_partial_L54 + dual_web_call_reasoned_refetch + wordlim_200 + skill_instructed_docs_consumption + 3m17s'}
  };

  function modelLabel(k) {
    for (var i = 0; i < MODELS.length; i++) if (MODELS[i].k === k) return MODELS[i].label;
    return k;
  }

  // Truncation tier → border color + style (light/dark).
  var TRUNC_BORDER = {
    yes:      {cLight:'#C94B4B', cDark:'#A03A3A', style:'solid'},
    mixed:    {cLight:'#D98A3D', cDark:'#B5703A', style:'solid'},
    implicit: {cLight:'#C9A23D', cDark:'#A8863A', style:'dashed'},
    no:       {cLight:'rgba(128,128,128,0.22)', cDark:'rgba(128,128,128,0.22)', style:'solid'}
  };

  function methodSwatch(dark, key, w, h) {
    var spec = COLORS.method[key];
    var bg = dark ? spec.bgDark : spec.bgLight;
    return e('span', {style: {
      display: 'inline-block', boxSizing: 'border-box', flexShrink: 0, width: w, height: h, borderRadius: 3,
      background: bg, border: '2px solid rgba(128,128,128,0.22)'
    }});
  }

  function truncSwatch(dark, key, w, h) {
    var b = TRUNC_BORDER[key];
    var bc = dark ? b.cDark : b.cLight;
    return e('span', {style: {
      display: 'inline-block', boxSizing: 'border-box', flexShrink: 0, width: w, height: h, borderRadius: 3,
      background: 'transparent',
      border: '2px ' + b.style + ' ' + bc
    }});
  }

  function LegendGroup(props) {
    var tc = props.textColor || 'inherit';
    var group = props.group;
    var cs = {fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace', fontSize: 10};
    var C = function(t) { return e('code', {style: cs}, t); };
    return e('div', {style: {width: 'fit-content', minWidth: 230}},
      e('div', {style: {display: 'flex', flexDirection: 'column', gap: 2, color: tc, opacity: 0.8, lineHeight: 1.3, fontSize: 11}},
        group.rows.map(function(r) {
          return e('div', {key: r.key, style: {display: 'flex', alignItems: 'center', gap: 7}},
            r.swatch,
            e('span', null, r.parts ? r.parts.map(function(p, i) {
              return p.code ? C(p.t) : e('span', {key: i}, p.t);
            }) : r.desc)
          );
        })
      )
    );
  }

  function Legend(props) {
    var dark = props.isDark;
    var groups = [
      {
        key: 'method',
        rows: [
          {key: 'web', swatch: methodSwatch(dark, 'web', 28, 16), parts: [
            {t: 'web', code: true}, {t: ' rendered extraction, often '}, {t: 'L33/54', code: true}, {t: '-clipped'}
          ]},
          {key: 'curl', swatch: methodSwatch(dark, 'curl', 28, 16), parts: [
            {t: 'curl', code: true}, {t: ' full response, often '}, {t: 'Content-Length', code: true}, {t: '-verified'}
          ]},
          {key: 'both', swatch: methodSwatch(dark, 'both', 28, 16), parts: [
            {t: 'both', code: false}, {t: ' '}, {t: 'web', code: true}, {t: ' + '}, {t: 'curl', code: true}, {t: ' use'}
          ]}
        ]
      },
      {
        key: 'truncated',
        rows: [
          {key: 'yes', swatch: truncSwatch(dark, 'yes', 28, 16), parts: [
            {t: ''}, {t: 'web', code: true}, {t: ' '}, {t: ' truncation reported explicitly'}
          ]},
          {key: 'mixed', swatch: truncSwatch(dark, 'mixed', 28, 16), parts: [
            {t: 'both '}, {t: 'web', code: true}, {t: ' truncation, full '}, {t: 'curl', code: true}, {t: ' response reported'}
          ]},
          {key: 'implicit', swatch: truncSwatch(dark, 'implicit', 28, 16), desc: 'truncation implied, not explicitly reported'},
          {key: 'no', swatch: truncSwatch(dark, 'no', 28, 16), parts: [
            {t: 'no truncation signal, '}, {t: 'curl', code: true}, {t: '-complete'}
          ]}
        ]
      },
      {
        key: 'mislabel',
        rows: [
          {key: 'stripe', swatch:
            e('span', {className: 'cdx-t3b-stripe', style: {display: 'inline-block', boxSizing: 'border-box', flexShrink: 0, width: 28, height: 16, borderRadius: 3, background: dark ? '#2a2a28' : '#e0e0de', border: '2px solid rgba(128,128,128,0.22)', position: 'relative'}}),
            desc: 'completeness label does not match evidence'},
          {key: 'plain', swatch:
            e('span', {style: {display: 'inline-block', boxSizing: 'border-box', flexShrink: 0, width: 28, height: 16, borderRadius: 3, background: 'transparent', border: '2px solid rgba(128,128,128,0.22)'}}),
            desc: 'completeness label matches evidence'}
        ]
      }
    ];
    return e('div', {style: {display: 'flex', flexDirection: 'column', gap: 12, marginTop: 4}},
      groups.map(function(g) {
        return e(LegendGroup, {key: g.key, isDark: dark, textColor: props.textColor, group: g});
      })
    );
  }

  function NoteBlock(props) {
    var tc = props.textColor || 'inherit';
    var cs = {fontFamily: 'monospace', fontSize: 10, background: 'rgba(128,128,128,0.15)', borderRadius: 2, padding: '1px 3px'};
    var C = function(t) { return e('code', {style: cs}, t); };
    return e('p', {style: {fontSize: 11, marginTop: 8, lineHeight: 1.6, opacity: 0.65, color: tc, maxWidth: 720}},
      e('i', null,
        'Single page type ', C('EC-6'), ' (Raw GitHub Markdown, ~92 KB). Rows are LLM version, columns are reasoning level; ',
        C('Ultra'), ' ran on ', C('Sol'), ' and ', C('Terra'), ' only. Each cell folds three signals: fill = ',
        C('method'), ' (retrieval path), border = ', C('truncation'), ' tier (red = ', C('web'), ' ', C('L54'),
        ' cutpoint, amber = mixed, dashed yellow = implicit), and a diagonal stripe marks a ', C('mislabel'),
        ' where the completeness label diverges from the evidence. Cell tooltips carry each run\'s log-label surface note: ',
        C('web'), ' returns in ', C('Terra'), ' and ', C('Luna'), ' re-hit the ', C('L54'), ' cutpoint (red borders), and the striped ',
        C('under'), ' cells mark clean ', C('curl'), ' fetches mislabeled ', C('UNVERIFIABLE'), ' or ', C('PARTIAL'), '.'
      )
    );
  }

  function HeatmapTable(props) {
    var dark = props.isDark;
    var large = props.large;
    var tc = props.textColor || 'inherit';
    var labelW = large ? 170 : 130;
    var cellW  = large ? 72  : 58;
    var cellH  = large ? 40  : 32;
    var fs     = large ? 14  : 12;

    return e('div', {className: 'cdx-t3b-wrap'},
      e('table', {className: 'cdx-t3b'},
        e('thead', null,
          e('tr', null,
            e('th', {className: 'cdx-t3b-rh', style: {minWidth: labelW, color: tc, fontSize: 10, fontWeight: 600, verticalAlign: 'bottom'}},
              'LLM / Reasoning'),
            LEVELS.map(function(lv) {
              return e('th', {key: 'lv-' + lv.k, title: lv.label,
                style: {color: tc, fontSize: 9, fontWeight: 700, letterSpacing: '0.06em',
                  opacity: 0.6, textTransform: 'uppercase', textAlign: 'center',
                  borderLeft: '1.5px solid rgba(128,128,128,0.22)'}},
                lv.label);
            })
          )
        ),
        e('tbody', null,
          MODELS.map(function(m) {
            return e('tr', {key: 'row-' + m.k},
              e('td', {className: 'cdx-t3b-rl', style: {color: tc, maxWidth: labelW, width: labelW, fontWeight: 400, fontSize: 11}},
                modelLabel(m.k)),
              LEVELS.map(function(lv) {
                var key = m.k + ':' + lv.k;
                var run = RUNS[key];
                if (!run) {
                  return e('td', {key: key, style: {borderLeft: '1px solid rgba(128,128,128,0.10)'}},
                    e('div', {style: {width: cellW, height: cellH, margin: '1px auto', borderRadius: 3,
                      background: dark ? '#2a2a28' : '#e0e0de'}})
                  );
                }
                var ms = COLORS.method[run.method];
                var tb = TRUNC_BORDER[run.truncated];
                var bc = dark ? tb.cDark : tb.cLight;
                var striped = run.mislabel !== 'accurate';
                var className = 'cdx-t3b-cell';
                if (striped) className += ' cdx-t3b-stripe';
                var tip = 'EC-6 · ' + modelLabel(m.k) + ' ' + lv.label +
                  '\nmethod: ' + ms.full + ' (' + CATEGORY_DESC.method[run.method] + ')' +
                  '\ntruncation: ' + run.truncated + ' (' + CATEGORY_DESC.truncated[run.truncated] + ')' +
                  '\nmislabel: ' + run.mislabel + ' (' + CATEGORY_DESC.mislabel[run.mislabel] + ')' +
                  '\n' + run.note;
                return e('td', {key: key, style: {borderLeft: '1px solid rgba(128,128,128,0.10)'}},
                  e('div', {title: tip, className: className,
                    style: {width: cellW, height: cellH, fontSize: fs,
                      background: dark ? ms.bgDark : ms.bgLight, color: ms.fg,
                      border: '2px ' + tb.style + ' ' + bc}},
                    ms.label)
                );
              })
            );
          })
        )
      )
    );
  }

  function App() {
    var openState = React.useState(false);
    var isOpen = openState[0];
    var setOpen = openState[1];
    var dark = detectDark();
    var lbBg = dark ? '#1c1c1a' : '#ffffff';
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
      e('div', {onClick: function(){ setOpen(true); }, style: {cursor: 'pointer'}},
        e('div', {style: {display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'center', gap: 28}},
          e('div', null,
            e(HeatmapTable, {isDark: dark, large: false}),
            e('p', {className: 'cdx-t3b-hint'}, '↗ click to expand')
          ),
          e('div', {style: {flex: '0 0 auto', marginTop: 4}},
            e(Legend, {isDark: dark})
          )
        )
      ),
      e(NoteBlock, {isDark: dark}),
      isOpen && e('div', {
        className: 'cdx-t3b-overlay',
        onClick: function(ev){ if (ev.target === ev.currentTarget) setOpen(false); }
      },
        e('div', {className: 'cdx-t3b-overlay-inner', style: {background: lbBg, color: lbText, width: '99vw'}},
          e('button', {className: 'cdx-t3b-close', style: {color: lbText},
            onClick: function(){ setOpen(false); }, 'aria-label': 'Close'}, '×'),
          e('div', {style: {display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'center', gap: 28}},
            e('div', null,
              e(HeatmapTable, {isDark: dark, large: true, textColor: lbText})
            ),
            e('div', {style: {flex: '0 0 auto', marginTop: 4}},
              e(Legend, {isDark: dark, textColor: lbText})
            )
          ),
          e(NoteBlock, {isDark: dark, textColor: lbText})
        )
      )
    );
  }

  var root = ReactDOM.createRoot(document.getElementById('cdx-t3b-root'));
  root.render(e(App));
})();
</script>
{% endraw %}
