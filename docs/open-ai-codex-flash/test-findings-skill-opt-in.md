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

The visualization below condenses the opt-in condition into one model-level heatmap. Rows are models; columns show how often each signal appeared across all runs for that model. Because the denominator is the same for every cell in a row, the colors are comparable across columns. The story is the drop-off from left to right: workspace skill and memory signal almost always appear together, but protocol use and especially fix recommendations drop sharply.

{% raw %}
<div id="cdx-skill-optin-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.cdx-skill-wrap { overflow-x: auto; }
table.cdx-skill { border-collapse: collapse; width: auto; }
table.cdx-skill th { font-size: 10px; font-weight: 500; padding: 3px 2px; text-align: center; white-space: nowrap; color: inherit; }
table.cdx-skill th.cdx-skill-rh { text-align: left; }
table.cdx-skill th .cdx-skill-sub { font-weight: 400; font-size: 10px; opacity: 0.55; display: block; }
table.cdx-skill td { padding: 2px 0; text-align: center; }
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

  var rows = [{"model": "GPT-5.4-Mini", "n": 9, "skill_loaded_pct": 56, "memory_present_pct": 44, "both_pct": 22, "protocol_pct": 0, "fix_pct": 0, "tool": "curl", "failure": "DNS/sandbox"}, {"model": "GPT-5.4", "n": 4, "skill_loaded_pct": 100, "memory_present_pct": 100, "both_pct": 100, "protocol_pct": 0, "fix_pct": 0, "tool": "curl", "failure": "none notable"}, {"model": "GPT-5.5", "n": 4, "skill_loaded_pct": 100, "memory_present_pct": 100, "both_pct": 100, "protocol_pct": 100, "fix_pct": 0, "tool": "curl", "failure": "none notable"}, {"model": "GPT-5.6-Luna", "n": 4, "skill_loaded_pct": 100, "memory_present_pct": 100, "both_pct": 100, "protocol_pct": 75, "fix_pct": 0, "tool": "curl", "failure": "none notable"}, {"model": "GPT-5.6-Sol", "n": 5, "skill_loaded_pct": 100, "memory_present_pct": 100, "both_pct": 100, "protocol_pct": 20, "fix_pct": 0, "tool": "curl", "failure": "none notable"}, {"model": "GPT-5.6-Terra", "n": 5, "skill_loaded_pct": 100, "memory_present_pct": 100, "both_pct": 100, "protocol_pct": 40, "fix_pct": 0, "tool": "curl", "failure": "none notable"}];

  var COLS = [{"id": "skill_loaded_pct", "label": "Skill loaded", "sub": "docs-consumption"}, {"id": "memory_present_pct", "label": "Memory signal", "sub": "## Memory"}, {"id": "both_pct", "label": "Both", "sub": "skill + memory"}, {"id": "protocol_pct", "label": "Protocol prefix", "sub": "COMPLETE"}, {"id": "fix_pct", "label": "Fix recommended", "sub": "none produced"}];

  var MODEL_ORDER = ['GPT-5.4-Mini','GPT-5.4','GPT-5.5','GPT-5.6-Luna','GPT-5.6-Sol','GPT-5.6-Terra'];

  function getColor(dark, pct) {
    if (pct === 0) return { bg: dark ? '#2a2a28' : '#e0e0de', fg: dark ? '#a0a0a0' : '#666666' };
    if (pct <= 33) return { bg: dark ? '#0F6E56' : '#1D9E75', fg: '#fff' };
    if (pct <= 66) return { bg: dark ? '#185FA5' : '#378ADD', fg: '#fff' };
    return { bg: dark ? '#A32D2D' : '#F06292', fg: '#fff' };
  }

  function HeatmapTable(props) {
    var dark = props.isDark;
    var large = props.large;
    var tc = props.textColor || 'inherit';
    var cellW  = large ? 60  : 46;
    var cellH  = large ? 32  : 26;
    var labelW = large ? 170 : 130;
    var fs     = large ? 12  : 11;

    return e('div', {className: 'cdx-skill-wrap'},
      e('table', {className: 'cdx-skill'},
        e('thead', null,
          e('tr', null,
            e('th', {className: 'cdx-skill-rh', style: {minWidth: labelW, color: tc}}, 'Model (n runs)'),
            COLS.map(function(col) {
              return e('th', {key: col.id, style: {color: tc}},
                col.label,
                e('span', {className: 'cdx-skill-sub'}, col.sub)
              );
            })
          )
        ),
        e('tbody', null,
          MODEL_ORDER.map(function(model) {
            var row = rows.find(function(r) { return r.model === model; });
            return e('tr', {key: row.model},
              e('td', {className: 'cdx-skill-rl', style: {color: tc, maxWidth: labelW, width: labelW}},
                row.model + ' (n=' + row.n + ')'
              ),
              COLS.map(function(col) {
                var pct = row[col.id];
                var c = getColor(dark, pct);
                var tip = row.model + ' (n=' + row.n + ')\n' +
                  col.label + ': ' + pct + '% of runs\n' +
                  'Dominant retrieval: ' + row.tool + '\n' +
                  'Failure mode: ' + row.failure;
                return e('td', {key: col.id},
                  e('div', {title: tip, style: {
                    borderRadius: 3, fontSize: fs, fontWeight: 700,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    width: cellW, height: cellH, margin: '1px auto',
                    background: c.bg, color: c.fg, cursor: 'help'
                  }}, pct + '%')
                );
              })
            );
          })
        )
      )
    );
  }

  function Legend(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var items = [
      { pct: 0, label: '0% — signal absent' },
      { pct: 33, label: '1–33% — rare' },
      { pct: 66, label: '34–66% — mixed' },
      { pct: 100, label: '67–100% — dominant' }
    ];
    return e('table', {style: {borderCollapse: 'collapse', fontSize: 11, marginTop: 0}},
      e('tbody', null, items.map(function(item) {
        var c = getColor(dark, item.pct);
        return e('tr', {key: item.pct},
          e('td', {style: {paddingRight: 8, paddingBottom: 4, verticalAlign: 'middle'}},
            e('span', {style: {
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              width: 36, height: 16, borderRadius: 3,
              background: c.bg, color: c.fg, fontSize: 10, fontWeight: 600
            }}, item.pct + '%')
          ),
          e('td', {style: {paddingBottom: 4, color: tc, opacity: 0.8}}, item.label)
        );
      }))
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
        e('h4', null, 'Skill/Memory Influence vs. Protocol Compliance by Model'),
        e('div', {onClick: function(){ setOpen(true); }, style: {cursor: 'pointer'}},
          e(HeatmapTable, {isDark: dark, large: false}),
          e('p', {className: 'cdx-skill-hint'}, '↗ click to expand')
        ),
        e('div', {style: {display: 'flex', gap: 28, alignItems: 'flex-start', flexWrap: 'wrap', marginTop: 10, justifyContent: 'center'}},
          e('div', {style: {flexShrink: 0}}, e(Legend, {isDark: dark})),
          e('div', {style: {flex: 1, maxWidth: 460}},
            e('p', {className: 'cdx-skill-caption'},
              'Each row is a model; the denominator is the total runs for that model. Columns show the percentage of runs where the signal appeared. Because the denominator is the same across every column in a row, the colors are directly comparable. The pattern is the drop-off from left to right: workspace skill and memory signal almost always co-occur, protocol prefix use is inconsistent, and no model produced a fix recommendation.'
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
          e(HeatmapTable, {isDark: dark, large: true, textColor: lbText}),
          e('div', {style: {display: 'flex', gap: 28, alignItems: 'flex-start', flexWrap: 'wrap', marginTop: 10, justifyContent: 'center'}},
            e('div', {style: {flexShrink: 0}}, e(Legend, {isDark: dark, textColor: lbText})),
            e('div', {style: {flex: 1, maxWidth: 460}},
              e('p', {className: 'cdx-skill-caption', style: {color: lbText}},
                'Expanded view. Each row is one model; every column shares the same n. The story is the cliff between signal presence (left) and meaningful protocol compliance (right): skill and memory almost always appear together, yet no run produced a fix recommendation.'
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
