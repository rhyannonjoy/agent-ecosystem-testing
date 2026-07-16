---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Skill Opt-In"
permalink: /docs/open-ai-codex-flash/test-findings-skill-opt-in
parent: OpenAI Codex - Flash
---

# Key Findings for Codex's Web Search Behavior<br>`GPT`-interpreted `/SKILL opt-in`

---

> _Companion conditions [`skill-off` baseline](../open-ai-codex/codex-test-findings-extension.md), `skill-on`, `skill-on + memory suppressed`
> excluded from this doc. Findings limited to whether agents discovered, followed `docs-consumption/SKILL` independently, not whether explicit
> activation or `/memories` removal changes retrieval, reporting outcomes. Experiment design in [Flash Runbook](runbook.md)._

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
| **`/SKILL`<br>Discovery** | _Passive, not guaranteed_: ~87% - 27/31 logs cite `/SKILL` injection from `<skills_instructions>` block;<br>only one agent reported its path; ~55% - 17/31 used `COMPLETE` protocol prefix |
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
| **Reasoning Levels** | `Light`/`Low`, `Medium`, `High`, `Extra High`, `Ultra` |
| **Total Runs** | 31 |
| **`/SKILL` Loaded** | ~87% of session logs cite `/docs-consumption/SKILL` injected into the agent's context |
| **`/SKILL` Path Emitted** | One agent wrote the full `/SKILL` path in its own output rather than mentioning it in passing |
| **Protocol Prefix Used** | ~55% of agents used `/SKILL` summarization prefix to signal completeness |
| **`/SKILL` Language Used** | 100% - every run contained at least one `/SKILL`-related phrase, but read as a shortcut<br>rather than protocol-driven analysis |
| **Truncation: `Yes`** | One agent reported incomplete content with the familiar `T2` [`L54` `web`-window cutpoint](../open-ai-codex/codex-test-findings-extension.md#platform-limit-summary) |
| **Truncation: `Mixed`** | Six agents reported both a `web` limit and a full `curl` result |
| **Truncation: `Implicit`** | No agent reasoned around a limit without naming it |
| **Truncation: `No`** | 77% of runs had no truncation signal, largely because agents bypassed `web` for `curl` |
| **Completeness Accurate** | 100% of agents correctly classified the fetch state against the evidence they had |
| **Errors Examined** | ~87% of agents accurately described their most common error, but ignored others |
| **Execution vs. Completeness** | 100% of agents distinguished _"the tool ran"_ from _"the full content arrived"_ |
| **Avoided Reframing** | ~84% of agents avoided calling a partial or error-state fetch _"complete"_ or _"successful"_ |
| **Fix Recommended** | 0 - even when agents accurately described a sandbox error or `web` limits,<br>none suggested some form of remediation |
| **`/memories` Signals** | ~77% of session logs cite the system `## Memory` instruction or the competing<br>`/memories/skills/single-url-retrieval-measurement/SKILL` |
| **`/memories` + `/SKILL`** | ~77% of runs had both `/docs-consumption/SKILL` and `/memories.../SKILL` injected,<br>making it hard to isolate either effect |

## Key Findings

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`/SKILL` discovery is location, version-dependent** | `GPT-5.4 Mini` runs | Early `Mini` runs didn't load `/SKILL` due to `~.agents/skills` location requirement; `/memories` didn't due to version limitations; both appeared in later runs | **`/SKILL` discovery depends on specific runtime conditions, not on general file presence, LLM, or reasoning level** |
| 2 | **`/SKILL` loaded, but followed superficially** | All tests | 87% loaded, 61% mentioned `/docs-consumption` by name, 55% used requested protocol prefix, 100% used somewhat `/SKILL`-like language | **Loading `/SKILL` doesn't guarantee comprehensive protocol compliance; half the runs using protocol prefix didn't follow failure-examination requirements** |
| 3 | **`COMPLETE` protocol prefix becomes a stylistic shortcut** | All tests | All agents used `/SKILL`-like language; many opened reports with `COMPLETE`, included common error phrasing or tool selection reasoning without tying them to platform limits | **Agents adopt the easiest surface markers of the protocol without adopting the requested, epistemic discipline** |
| 4 | **`/SKILL` `opt-in` doesn't shift retrieval strategy** | All tests | Most bypassed `web` for `curl`; no new pagination, escalation, or verification patterns tied to `/SKILL` discovery | **`/SKILL` requests for deeper retrieval analysis don't impact retrieval tool selection** |
| 5 | **`/SKILL` `opt-in` weakens truncation signals** | All tests | Only 22% of agents reported some form of truncation event, which is a 47% drop from the [historical `T2` results](../open-ai-codex/codex-test-findings-extension.md#results-snapshot) | **Agents remove `L54` `web` cutpoint by favoring `curl`; `/SKILL` presence doesn't independently enhance truncation reporting** |
| 6 | **Agents classify completeness accurately, but don't recommend fixes** | All tests | `completeness_accurate=100%`, `exec_vs_complete=100%`, `avoided_reframing=84%`, but `fix_recommended=0%` | **Agents ignored `/SKILL`'s fix requirement; classification, report integrity scores reflect baseline behavior, not explicit evidence of `/SKILL` influence** |
| 7 | **`/SKILL` `opt-in` produces expected false positive profile** | All tests | Shallow compliance scores, parroting common error phrasing, no fix recommendations, weak truncation reporting, strong `/memories` confound | **Passive `/SKILL` presence produces trivial compliance; this is a useful baseline, not evidence of `/SKILL` impact on retrieval behavior or report quality** |
| 8 | **`/memories` is the dominant influence** | All tests | 77% included both `/memories` and `docs-consumption` `/SKILL` signals; `/memories.../SKILL` referenced in 79% of `tool_output`, 92% of `final_answer` | **System-injected `/memories` largely overrides `docs-consumption/SKILL`, making individual evaluation a challenge** |

## `/memories` vs `/docs-consumption`

Scripts [`memory_audit`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_audit.py) and
[`memory_analyzer`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/memory_analyzer.py)
determine whether the `docs-consumption/SKILL` loaded in the `<skills_instructions>` block, the system `## Memory` instruction was present, and
if the agent read or cited the competing `/memories.../single-url-retrieval-measurement/SKILL`.

### `/memories` and `/docs-consumption` Co-occurrence

| **Condition** | **Count** | **% of Runs** |
| --- | --- | --- |
| `/docs-consumption` Signals | 27 | 87% |
| `/memories` Signals | 24 | 77% |
| Both `/docs-consumption` and `/memories` Signals | 24 | 77% |
| `/memories...single-url-retrieval-measurement` referenced | 24 | 77% |
| Only `/docs-consumption` Signals | 3 | 10% |
| Only `/memories` Signals | 0 | 0% |
| Neither due to `/docs-consumption` present, but not in `~.agents/skills` or version limited | 4 | 13% |

### `/docs-consumption` Signals

| **Signal** | **Count** | **% of Runs** |
| --- | --- | --- |
| Session log audits cite `skills: N loaded docs-consumption: yes`* | 27 | 87% |
| Agent mentions `/docs-consumption` in exposed reasoning or reporting | 19 | 61% |
| Agent mentions full `/docs-consumption` path | 1 | 3% |
| Agents use `/SKILL` protocol prefix `COMPLETE` | 17 | 55% |
| Agents use `/SKILL`-like language | 31 | 100% |

>_*`GPT-5.4 Mini` logs cite 9 skills, `GPT-5.5`+ load 10_

### `/memories` Session Log Signals

| **Signal** | **Count** | **% of `/memories`-positive** |
| --- | --- | --- |
| `system_prompt` includes `## Memory` block | 24 | 100% |
| `system_memory_instruction` header present | 24 | 100% |
| `final_answer` includes `/memories`-related text | 22 | 92% |
| `tool_output` includes `/memories`-related text | 19 | 79% |
| `commentary` includes `/memories`-related text and/or citations | 5 | 21% |

## Data Visualizations

The visualizations below are grounded in the merged `results.csv` and `memory-analysis/T2_memory_audit.csv` datasets.
They are designed to make the opt-in condition's false-positive profile concrete: most runs show surface-level skill
language without deep protocol compliance, and the strong `/memories` confound makes any independent `/SKILL` effect hard
to isolate.

{% raw %}
<div id="cdx-skill-optin-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.cdx-skill-wrap { overflow-x: auto; }
table.cdx-skill { border-collapse: collapse; }
table.cdx-skill th { font-size: 10px; font-weight: 500; padding: 3px 4px; text-align: center; white-space: nowrap; color: inherit; }
table.cdx-skill th.cdx-skill-rh { text-align: left; }
table.cdx-skill td { padding: 2px 2px; text-align: center; }
table.cdx-skill td.cdx-skill-rl { font-size: 11px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; vertical-align: middle; }
table.cdx-skill td.cdx-skill-rl.cdx-skill-model { font-size: 10px; opacity: 0.65; padding-left: 8px; }
.cdx-skill-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; }
.cdx-skill-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.78);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.cdx-skill-overlay-inner {
  border-radius: 10px; padding: 22px 26px;
  max-width: 99vw; max-height: 93vh;
  overflow: auto; position: relative;
}
.cdx-skill-close {
  position: absolute; top: 10px; right: 12px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.cdx-skill-close:hover { opacity: 1; }
.cdx-skill-fig { margin-top: 2rem; }
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

  var runs = [{"model": "GPT-5.4-Mini", "level": "Light/Low", "truncated": "mixed", "discovered": "no", "protocol": "", "memory": false, "single_url_skill": false, "skill_loaded": false, "skill_lang": true, "timestamp": "2026-07-11 13:36:35"}, {"model": "GPT-5.4-Mini", "level": "Light/Low", "truncated": "yes", "discovered": "yes", "protocol": "", "memory": false, "single_url_skill": false, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-11 15:46:12"}, {"model": "GPT-5.4-Mini", "level": "Light/Low", "truncated": "no", "discovered": "yes", "protocol": "", "memory": false, "single_url_skill": false, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-11 16:00:36"}, {"model": "GPT-5.4-Mini", "level": "Medium", "truncated": "mixed", "discovered": "no", "protocol": "", "memory": false, "single_url_skill": false, "skill_loaded": false, "skill_lang": true, "timestamp": "2026-07-11 14:33:25"}, {"model": "GPT-5.4-Mini", "level": "Medium", "truncated": "mixed", "discovered": "yes", "protocol": "", "memory": false, "single_url_skill": false, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-11 16:52:56"}, {"model": "GPT-5.4-Mini", "level": "High", "truncated": "mixed", "discovered": "no", "protocol": "", "memory": false, "single_url_skill": false, "skill_loaded": false, "skill_lang": true, "timestamp": "2026-07-11 14:56:30"}, {"model": "GPT-5.4-Mini", "level": "High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-11 17:08:40"}, {"model": "GPT-5.4-Mini", "level": "Extra High", "truncated": "mixed", "discovered": "no", "protocol": "", "memory": false, "single_url_skill": false, "skill_loaded": false, "skill_lang": true, "timestamp": "2026-07-11 15:13:15"}, {"model": "GPT-5.4-Mini", "level": "Extra High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-11 17:26:02"}, {"model": "GPT-5.4", "level": "Light/Low", "truncated": "mixed", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-12 15:57:12"}, {"model": "GPT-5.4", "level": "Medium", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-12 16:11:14"}, {"model": "GPT-5.4", "level": "High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-12 16:37:21"}, {"model": "GPT-5.4", "level": "Extra High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-12 17:20:14"}, {"model": "GPT-5.5", "level": "Light/Low", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 16:56:59"}, {"model": "GPT-5.5", "level": "Medium", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 17:18:23"}, {"model": "GPT-5.5", "level": "High", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 17:33:15"}, {"model": "GPT-5.5", "level": "Extra High", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 17:49:30"}, {"model": "GPT-5.6-Luna", "level": "Light/Low", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 20:49:23"}, {"model": "GPT-5.6-Luna", "level": "Medium", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 20:35:50"}, {"model": "GPT-5.6-Luna", "level": "High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 20:23:59"}, {"model": "GPT-5.6-Luna", "level": "Extra High", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 20:02:30"}, {"model": "GPT-5.6-Sol", "level": "Light/Low", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 21:56:19"}, {"model": "GPT-5.6-Sol", "level": "Medium", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 22:14:29"}, {"model": "GPT-5.6-Sol", "level": "High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 23:01:09"}, {"model": "GPT-5.6-Sol", "level": "Extra High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 23:13:46"}, {"model": "GPT-5.6-Sol", "level": "Ultra", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-13 23:29:49"}, {"model": "GPT-5.6-Terra", "level": "Light/Low", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-14 13:09:49"}, {"model": "GPT-5.6-Terra", "level": "Medium", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-14 13:22:07"}, {"model": "GPT-5.6-Terra", "level": "High", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-14 13:32:03"}, {"model": "GPT-5.6-Terra", "level": "Extra High", "truncated": "no", "discovered": "yes", "protocol": "", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-14 13:41:46"}, {"model": "GPT-5.6-Terra", "level": "Ultra", "truncated": "no", "discovered": "yes", "protocol": "COMPLETE", "memory": true, "single_url_skill": true, "skill_loaded": true, "skill_lang": true, "timestamp": "2026-07-14 13:50:47"}];
  var perModel = [{"model": "GPT-5.4-Mini", "n": 9, "loaded": 5, "protocol": 0, "lang": 9, "surl": 2}, {"model": "GPT-5.4", "n": 4, "loaded": 4, "protocol": 0, "lang": 4, "surl": 4}, {"model": "GPT-5.5", "n": 4, "loaded": 4, "protocol": 4, "lang": 4, "surl": 4}, {"model": "GPT-5.6-Luna", "n": 4, "loaded": 4, "protocol": 3, "lang": 4, "surl": 4}, {"model": "GPT-5.6-Sol", "n": 5, "loaded": 5, "protocol": 1, "lang": 5, "surl": 5}, {"model": "GPT-5.6-Terra", "n": 5, "loaded": 5, "protocol": 2, "lang": 5, "surl": 5}];
  var cooc = {"both": 24, "only_skill": 3, "only_mem": 0, "neither": 4};
  var dims = [{"label": "Completeness accurate", "yes": 31, "total": 31}, {"label": "Error examined", "yes": 27, "total": 31}, {"label": "Exec vs. complete", "yes": 31, "total": 31}, {"label": "Avoided reframing", "yes": 26, "total": 31}, {"label": "Fix recommended", "yes": 0, "total": 31}];

  var MODEL_ORDER = ['GPT-5.4-Mini','GPT-5.4','GPT-5.5','GPT-5.6-Luna','GPT-5.6-Sol','GPT-5.6-Terra'];
  var LEVEL_ORDER = ['Light/Low','Medium','High','Extra High','Ultra'];

  function disclosureColor(dark, tier) {
    var map = {
      'yes': { bg: dark ? '#A32D2D' : '#F06292', fg: '#fff', label: 'Y' },
      'mixed': { bg: dark ? '#185FA5' : '#378ADD', fg: '#fff', label: 'M' },
      'implicit': { bg: dark ? '#cba452' : '#FFB74D', fg: dark ? '#412402' : '#412402', label: 'I' },
      'no': { bg: dark ? '#0F6E56' : '#1D9E75', fg: '#fff', label: 'N' }
    };
    return map[tier] || { bg: dark ? '#363634' : '#d0cec7', fg: 'inherit', label: '' };
  }

  var SURFACE_NOTE = {
    'yes': 'Truncation reported with web limits named',
    'mixed': 'Mixed truncation signal, both paths used, web limits named',
    'implicit': 'Implicit truncation through tooling pivot and exposed reasoning',
    'no': 'No truncation signal, curl-complete and/or payload too small to test'
  };

  function buildRows() {
    var rows = [];
    MODEL_ORDER.forEach(function(model) {
      var modelRuns = runs.filter(function(r) { return r.model === model; });
      LEVEL_ORDER.forEach(function(level) {
        var levelRuns = modelRuns.filter(function(r) { return r.level === level; });
        if (levelRuns.length) {
          rows.push({ type: 'header', model: model, level: level });
          levelRuns.forEach(function(run, idx) {
            rows.push({ type: 'data', run: run, idx: idx + 1 });
          });
        }
      });
    });
    return rows;
  }

  function HeatmapTable(props) {
    var dark = props.isDark;
    var large = props.large;
    var tc = props.textColor || 'inherit';
    var cellW  = large ? 52  : 28;
    var cellH  = large ? 28  : 22;
    var labelW = large ? 130 : 100;
    var fs     = large ? 11  : 10;

    var rows = buildRows();
    var cols = [];
    var maxCols = 0;
    rows.forEach(function(row) {
      if (row.type === 'data') maxCols = Math.max(maxCols, row.idx);
    });
    for (var i = 1; i <= maxCols; i++) cols.push(i);

    return e('div', {className: 'cdx-skill-wrap'},
      e('table', {className: 'cdx-skill'},
        e('thead', null,
          e('tr', null,
            e('th', {className: 'cdx-skill-rh', style: {minWidth: labelW, color: tc}}, 'Model / Reasoning / Run'),
            cols.map(function(c) {
              return e('th', {key: c, style: {color: tc, fontSize: 9, opacity: 0.55}}, '#' + c);
            })
          )
        ),
        e('tbody', null,
          rows.map(function(row, i) {
            if (row.type === 'header') {
              return e('tr', {key: 'h-' + i, style: {borderTop: '1.5px solid rgba(128,128,128,0.22)'}},
                e('td', {colSpan: cols.length + 1,
                  style: {fontSize: 10, fontWeight: 700, letterSpacing: '0.07em',
                    opacity: 0.55, paddingTop: 5, paddingBottom: 1,
                    textTransform: 'uppercase', textAlign: 'center', color: tc}},
                  row.model + ' · ' + row.level
                )
              );
            }
            var run = row.run;
            var c = disclosureColor(dark, run.truncated);
            var tip = run.model + ' ' + run.level + ' run #' + row.idx + '\n' + run.timestamp + '\n' +
              'Truncation: ' + run.truncated + ' — ' + SURFACE_NOTE[run.truncated] + '\n' +
              'Agent discovered skill: ' + run.discovered + '\n' +
              'Protocol prefix: ' + (run.protocol || 'none') + '\n' +
              'Memory signal: ' + (run.memory ? 'yes' : 'no') + '\n' +
              'Single-url memory skill: ' + (run.single_url_skill ? 'yes' : 'no') + '\n' +
              'Skill loaded / language: ' + (run.skill_loaded ? 'yes' : 'no') + ' / ' + (run.skill_lang ? 'yes' : 'no');
            return e('tr', {key: 'r-' + i},
              e('td', {className: 'cdx-skill-rl cdx-skill-model', style: {color: tc, maxWidth: labelW, width: labelW}},
                'Run ' + row.idx
              ),
              e('td', {key: 'cell', colSpan: cols.length,
                style: {textAlign: 'left', paddingLeft: 4}},
                e('div', {title: tip, style: {
                  borderRadius: 3, fontSize: fs, fontWeight: 700,
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  width: cellW, height: cellH,
                  background: c.bg, color: c.fg, cursor: 'help'
                }}, c.label)
              )
            );
          })
        )
      )
    );
  }

  function DisclosureLegend(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var items = [
      {tier: 'yes', desc: 'Yes — truncation reported with web limits named'},
      {tier: 'mixed', desc: 'Mixed — both paths used, web limits named'},
      {tier: 'implicit', desc: 'Implicit — tooling pivot without naming limit'},
      {tier: 'no', desc: 'No — no truncation signal, curl-complete'}
    ];
    return e('table', {style: {borderCollapse: 'collapse', fontSize: 11, marginTop: 0}},
      e('tbody', null, items.map(function(item) {
        var c = disclosureColor(dark, item.tier);
        return e('tr', {key: item.tier},
          e('td', {style: {paddingRight: 8, paddingBottom: 4, verticalAlign: 'middle'}},
            e('span', {style: {
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              width: 24, height: 16, borderRadius: 3,
              background: c.bg, color: c.fg, fontSize: 10, fontWeight: 600
            }}, c.label)
          ),
          e('td', {style: {paddingBottom: 4, color: tc, opacity: 0.8}}, item.desc)
        );
      }))
    );
  }

  function FailureDimensionChart(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var barH = 22;
    var maxW = 320;
    return e('div', null,
      dims.map(function(d) {
        var pct = Math.round(100 * d.yes / d.total);
        var isZero = pct === 0;
        var barW = Math.max(2, Math.round(maxW * d.yes / d.total));
        var barColor = isZero ? (dark ? '#A32D2D' : '#F06292') : (dark ? '#185FA5' : '#378ADD');
        return e('div', {key: d.label, style: {marginBottom: 10}},
          e('div', {style: {fontSize: 11, marginBottom: 3, color: tc}}, d.label),
          e('div', {style: {display: 'flex', alignItems: 'center', gap: 8}},
            e('div', {style: {
              height: barH, width: barW, borderRadius: 3,
              background: barColor, transition: 'width 0.3s ease',
              boxShadow: isZero ? '0 0 0 2px ' + (dark ? '#ff8a80' : '#c62828') : 'none'
            }},
              isZero ? e('span', {style: {color: '#fff', fontSize: 10, paddingLeft: 6, lineHeight: barH + 'px'}}, '0%') : null
            ),
            !isZero ? e('span', {style: {color: tc, fontSize: 11, fontWeight: 600}}, pct + '%') : null
          )
        );
      })
    );
  }

  function CooccurrenceChart(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var total = cooc.both + cooc.only_skill + cooc.only_mem + cooc.neither;
    var cats = [
      {label: 'Both memory + workspace skill', count: cooc.both, color: dark ? '#A32D2D' : '#F06292'},
      {label: 'Workspace skill only', count: cooc.only_skill, color: dark ? '#185FA5' : '#378ADD'},
      {label: 'Memory only', count: cooc.only_mem, color: dark ? '#0F6E56' : '#1D9E75'},
      {label: 'Neither', count: cooc.neither, color: dark ? '#6b6b69' : '#bdbdb7'}
    ];
    var maxCount = Math.max.apply(null, cats.map(function(c) { return c.count; }));
    var maxW = 260;
    return e('div', null,
      cats.map(function(cat) {
        var barW = Math.max(2, Math.round(maxW * cat.count / maxCount));
        var pct = Math.round(100 * cat.count / total);
        return e('div', {key: cat.label, style: {marginBottom: 10}},
          e('div', {style: {fontSize: 11, marginBottom: 3, color: tc}}, cat.label),
          e('div', {style: {display: 'flex', alignItems: 'center', gap: 8}},
            e('div', {style: {height: 22, width: barW, borderRadius: 3, background: cat.color}}),
            e('span', {style: {color: tc, fontSize: 11, fontWeight: 600}}, cat.count + ' (' + pct + '%)')
          )
        );
      })
    );
  }

  function PerModelChart(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var maxW = 200;
    var barH = 14;
    var signals = [
      {key: 'loaded', label: 'docs-consumption loaded', color: dark ? '#0F6E56' : '#1D9E75'},
      {key: 'protocol', label: 'protocol prefix used', color: dark ? '#185FA5' : '#378ADD'},
      {key: 'lang', label: 'skill language used', color: dark ? '#5b3a9e' : '#9575cd'},
      {key: 'surl', label: 'single-url memory skill', color: dark ? '#A32D2D' : '#F06292'}
    ];
    return e('div', null,
      perModel.map(function(m) {
        return e('div', {key: m.model, style: {marginBottom: 16}},
          e('div', {style: {fontSize: 12, fontWeight: 600, marginBottom: 4, color: tc}}, m.model + ' (n=' + m.n + ')'),
          signals.map(function(sig) {
            var count = m[sig.key];
            var barW = Math.max(2, Math.round(maxW * count / m.n));
            return e('div', {key: sig.key, style: {display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3}},
              e('div', {style: {width: 110, fontSize: 10, color: tc, opacity: 0.85, textAlign: 'right'}}, sig.label),
              e('div', {style: {height: barH, width: barW, borderRadius: 2, background: sig.color, display: 'flex', alignItems: 'center', paddingLeft: count > 0 ? 4 : 0}},
                count > 0 ? e('span', {style: {color: '#fff', fontSize: 9, fontWeight: 600}}, count) : null
              ),
              count === 0 ? e('span', {style: {color: tc, fontSize: 9, opacity: 0.6}}, '0') : null
            );
          })
        );
      })
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
        e('h4', null, 'Disclosure Taxonomy Heatmap'),
        e('div', {onClick: function(){ setOpen(true); }, style: {cursor: 'pointer'}},
          e(HeatmapTable, {isDark: dark, large: false}),
          e('p', {className: 'cdx-skill-hint'}, '↗ click to expand')
        ),
        e('div', {style: {display: 'flex', gap: 28, alignItems: 'flex-start', flexWrap: 'wrap', marginTop: 10, justifyContent: 'center'}},
          e('div', {style: {flexShrink: 0}}, e(DisclosureLegend, {isDark: dark})),
          e('div', {style: {flex: 1, maxWidth: 420}},
            e('p', {className: 'cdx-skill-caption'},
              'Rows are individual model / reasoning-level combinations; columns are repeated EC-6 runs in chronological order. Colors encode self-reported truncation disclosure, not retrieval path. Hover a cell for timestamp, skill-discovery status, protocol prefix, and memory-vs-skill signal.'
            )
          )
        )
      ),
      e('div', {style: {display: 'flex', gap: 24, flexWrap: 'wrap', marginTop: '2rem'}},
        e('div', {className: 'cdx-skill-fig', style: {flex: 1, minWidth: 280}},
          e('h4', null, 'Failure-Examination Dimensions'),
          e(FailureDimensionChart, {isDark: dark}),
          e('p', {className: 'cdx-skill-caption'},
            'Percentage of runs answering "yes" on each report-integrity dimension. The 0% fix-recommendation bar is highlighted to show that agents classified state accurately but never proposed remediation.'
          )
        ),
        e('div', {className: 'cdx-skill-fig', style: {flex: 1, minWidth: 280}},
          e('h4', null, 'Memory vs. Workspace Skill Co-occurrence'),
          e(CooccurrenceChart, {isDark: dark}),
          e('p', {className: 'cdx-skill-caption'},
            'Four exclusive categories across 31 EC-6 runs. Memory-instruction signals appear in 24/31 runs (77%), almost always alongside the workspace skill, making it hard to isolate the workspace skill effect.'
          )
        )
      ),
      e('div', {className: 'cdx-skill-fig'},
        e('h4', null, 'Per-Model Skill-Signal Breakdown'),
        e(PerModelChart, {isDark: dark}),
        e('p', {className: 'cdx-skill-caption'},
          'Workspace skill "loaded" and "skill language" are near-universal, but the formal protocol prefix and the competing single-url memory skill diverge by model. High load does not translate into protocol-aligned output.'
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
            e('div', {style: {flexShrink: 0}}, e(DisclosureLegend, {isDark: dark, textColor: lbText})),
            e('div', {style: {flex: 1, maxWidth: 420}},
              e('p', {className: 'cdx-skill-caption', style: {color: lbText}},
                'Expanded view. Rows are model / reasoning-level groups; each cell is one EC-6 run. Tooltip includes run timestamp, agent-discovered flag, protocol prefix, memory signal, and skill-loaded / skill-language flags.'
              )
            )
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

