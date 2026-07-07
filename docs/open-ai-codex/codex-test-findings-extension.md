---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Extension"
permalink: /docs/open-ai-codex/codex-test-findings-extension
parent: OpenAI Codex
---

# Key Findings for Codex's Web Search Behavior, GPT-interpreted - Extension

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/scripts/framework.py)

1. Run `python scripts/framework.py --test {test_id} --track vscode-codex-interpreted`
2. Review terminal output
3. Copy the provided prompt asking agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
4. Open a new session in VS Code Codex, paste the prompt into the chat window
5. Approve `curl` escalation and shell permission requests; skip requests for runs of local scripts
6. Capture the agent's full response; observe the gap between self-report and actual retrieval behavior<br>as the interpreted finding
7. Log structured metadata as described in [`framework-reference.md`](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/framework-reference#workflow)
8. Ensure results saved to [`/results/vscode-codex-interpreted/results.csv`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/vscode-codex-interpreted/results.csv)

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard<br>Character<br>Limit** | _None detected via `curl`_: fetches returned payloads from `EC-3`'s 254 chars to `BL-3`'s 4,848,853 chars;<br>`web` path reflects a line-indexed window, not a byte ceiling |
| **Hard<br>Token<br>Limit** | _None detected via `curl`_: counts ranged from 38 to 1,212,213; `SC-2`'s `134804 tokens truncated` marker against an `Original token count: 144884` largest display cap, terminal-rendering cap independent of HTTP retrieval, consistent with [`T1`'s `EC-6` finding](codex-test-findings-desktop.md#platform-limit-summary), different threshold |
| **Output<br>Consistency** | _LLM-and-level-stratified_: same URL + reasoning level regularly produce distinct retrieval strategies, output;<br>`BL-1`'s `GPT-5.5 Medium`,`Extra High` `web`-only at ~85K chars while `Light (Low)`, `High` escalate to 509,025 chars with same LLM |
| **Content<br>Selection<br>Behavior** | _Two-tier retrieval_: `web` returns a rendered, line-indexed extraction; full content requires `curl` escalation with network permissions; `OP-4`'s `GPT-5.4-Mini Extra High` exposed `wordlim:200` parameter, supporting [`T1`'s `SC-1` inference of agent-adjustable soft-default](codex-test-findings-desktop.md#platform-limit-summary) rather than fixed extraction size |
| **Truncation<br>Pattern** | _At least three independent layers_: `web` line-indexed window, LLM-page-dependent; terminal display cap,<br>`SC-2`'s `134804 tokens truncated` marker; `curl` response body, never truncated on successful escalations;<br>`BL-3` shows window cutpoint on structural boundary against terminal display cutpoint arbitrary |
| **`web`<br>Line-Indexed<br>Window** | _Page-architecture-dependent, sharper than `T1`_: `EC-6`:`L54` across runs with most LLM + reasoning levels, `SC-2`:`L139-140`, `SC-3`:`L353` comparably tight; LLM splits elsewhere - `OP-1`:`L304`/`L556`, `OP-2`:`L317-318`/`L590-591`, `OP-4`:`L237`/`L616`; `BL-1`:`L420` mostly holds with `L119` outlier; `SC-1`:`L344`; `SC-4`:`L657` |
| **`curl`<br>Escalation** | _Dominant, not universal_: `curl` use 99/119 runs; success often led to saving full HTTP response; `BL-2`, `BL-3`, `OP-4`, `OP-2`, `SC-1` heavy `curl` use; `EC-3` rare due to small size; `BL-3`, `SC-2` retrieve full bodies only JS-rendered scaffolding, not prose; attempts with `Browser`, headless Chrome, `Playwright` failed |
| **Session<br>Contamination** | _Structurally reduced, not eliminated_: `/private/tmp` clears between `T2` sessions, no run wrote to a project-persistent directory; `SC-4`'s `GPT-5.4-Mini Extra High` displayed workspace substitution; filename collision risk from independently fetched runs sharing path often, most heavily `EC-6`, `OP-4` |
| **Post-Session Auto-Editing** | _Data integrity risk, reversed from `T1`_: confirmed across most runs; all `BL-1`, `BL-2`, `EC-1` 12/13 runs,  half of `OP-4`, `SC-4`, `OP-4`; `T1` double report resolves during cleanup, `T2` single report doubles; screenshot capture at runtime remains primary record |
| **JS-Rendered<br>Pages** | _Structural retrieval failure_: `SC-2`, Next.js hydrated shell ~578,000 chars with prose absent regardless of path or reasoning level; `BL-3` different tutorial page than `T1`, same pattern at ~4.5 to 4.85 million chars |
| **`Cache Miss`<br>Failure** | _No longer systematic for the URL that defined it_: only 1/13 `EC-6` runs emitted `Cache Miss` versus 17/20 in `T1`; most return windowed `L54` extraction instead of failure; `BL-3` `Cache Miss` 6/8 `web` attempts |
| **Self-reported Completeness** | _Failure abstraction, mirrors `T1`_: agents sanitize issues into success language rather than debugging or correcting misuse, users lose learning opportunities, analysis in [Retrieved-Report Mismatches](friction-note-interpreted-extension.md#retrieved-report-mismatches); explicit examples `BL-3` `GPT-5.5 Extra High`, `GPT-5.4-Mini Low` runs |

## Results Details

| | |
| --- | --- |
| **Track** | `T2` GPT-interpreted, VS Code with Codex Extension |
| **Agents Observed** | `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5`* |
| **Reasoning Levels** | `Light`/`Low`, `Medium`, `High`, `Extra High` |
| **Total Runs** | 119 |
| **Distinct URLs** | 13 |
| **Input Size Range** | `EC-3` 254 chars to `BL-3` ~4.85M chars |
| **Truncation Events** | 82 / 119 - 69% of runs report truncation in some form<br>- `yes` includes `web` use, reported explicitly: 22<br>- `mixed`, `curl` + `web` use, limits named: 44<br>- `implicit`, pivot to `curl` citing `web` limit in reasoning: 16<br>- `no`, `curl`-only and/or without truncation signal: 37 |
| **Average Output Size** | 429,563 chars |
| **Output Size Range** | 149 - 4,849,033 chars |
| **Average Token Use** | 102,606 tokens |
| **Token Count Range** | 38 - 1,212,213 tokens |
| **Workspace Substitution** | 1 / 119 runs explicitly reasoned; filename collision risk 16+ runs |
| **`curl` Escalation** | Dominant retrieval path; present 57%, in 68 / 119 runs |
| **`web` Bypass** | `GPT-5.5` skipped `web` at least one reasoning level in `BL-3`, `EC-1`, `EC-6`, `OP-4`, `SC-1`;<br>`GPT-5.4-Mini`, `GPT-5.4` bypass occasionally, less consistently |

_*Three-LLM roster reflects OpenAI's retirement of `GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4` between tracks; `GPT-5.4` reappeared for `EC` tests, analysis in [LLM Retirement](friction-note-interpreted-extension.md#llm-retirement)._

## Truncation + Inaccessibility

As in [`T1`](codex-test-findings-desktop.md#content-access-x-intelligence), agentic task completion isn't a meaningful signal
for page readability on `T2`. Retrieval strategy still governs content accessibility more than reasoning level does: `web`
returns a line-indexed rendered extraction, and it's up to the agent to paginate through the prose or escalate past it,
which most agents eventually did, but not consistently.

`T2` diverges from `T1` in how tightly the `web` ceiling holds across LLMs. `EC-6`'s identical `L54` cutpoint across 10/13
runs, and `SC-2`, `SC-3`'s comparably tight `L139-140` and `L353` clusters, show `web` setting ceilings by page structure or a
fixed extraction default as much as LLM identity, suggesting a sharpening, not overturning, of `T1`'s LLM-dependent window
finding, most explicit from `OP-1` and `OP-2`, which both still exhibit per-LLM splits across `T2`.

The same three-tier grouping from `T1` split results regarding content accessibility. `EC-3`, `BL-2`, `EC-6`, `SC-4`, and `SC-1`
remain readable static payloads where either retrieval path returns usable prose. `BL-1`, `OP-2`, `OP-1`, `SC-3`, and `OP-4`
are large static HTML where `web` truncates, but `curl` consistently returns coherent responses. The JS-rendered or SPAs of
`EC-1`, `BL-3`, and `SC-2` `curl` responses include scaffolding rather than prose regardless of tool sophistication or reasoning
level. `BL-3`'s specific URL changed between tracks after the original's retirement, but the replacement lands in the identical
accessibility tier, confirming that the JS-rendered failure mode isn't tied to one specific page.

The heat map below encodes truncation tier, not retrieval path. Rows are reasoning level, with LLM version as a sub-grouping.
`GPT-5.4` only has data for `EC` tests and renders as empty cells elsewhere. Content accessibility difficulty determines
column order, mirroring [`T1`'s heat map](codex-test-findings-desktop.md#content-access-x-intelligence).

{% raw %}
<div id="cdx-hm3-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.cdx3-wrap { overflow-x: auto; }
table.cdx3 { border-collapse: collapse; width: 100%; }
table.cdx3 th { font-size: 10px; font-weight: 500; padding: 3px 4px; text-align: center; white-space: nowrap; color: inherit; }
table.cdx3 th.cdx3-rh { text-align: left; }
table.cdx3 th .cdx3-sub { font-weight: 400; font-size: 10px; opacity: 0.55; display: block; }
table.cdx3 td { padding: 2px 2px; text-align: center; }
table.cdx3 td.cdx3-rl { font-size: 11px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; vertical-align: middle; }
table.cdx3 td.cdx3-rl.cdx3-llm { font-size: 10px; opacity: 0.65; padding-left: 8px; }
.cdx3-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.cdx3-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.78);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.cdx3-overlay-inner {
  border-radius: 10px; padding: 22px 26px;
  max-width: 99vw; max-height: 93vh;
  overflow: auto; position: relative;
}
.cdx3-close {
  position: absolute; top: 10px; right: 12px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.cdx3-close:hover { opacity: 1; }
.cdx3-section-label {
  font-size: 10px; font-weight: 600; letter-spacing: 0.06em;
  opacity: 0.45; padding: 6px 0 2px 0; text-align: left;
}
.cdx3-divider td { border-top: 1px solid rgba(128,128,128,0.18); height: 4px; }
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

  // Columns ordered by content accessibility difficulty, same order as T1's heat map:
  // clean static → large static → JS-rendered/SPA
  var cols = [
    {id:'EC-3',  l1:'EC-3',  l2:'254-660 B', tier:'readable', note:'JSON redirect chain with small payload, truncation untestable'},
    {id:'BL-2',  l1:'BL-2',  l2:'5.8 KB',    tier:'readable', note:'Raw Markdown stable 5,805 chars across all runs, no truncation'},
    {id:'EC-6',  l1:'EC-6',  l2:'92 KB',     tier:'readable', note:'Raw GitHub Markdown L54 web cutpoint in 10/13 runs'},
    {id:'SC-4',  l1:'SC-4',  l2:'65 KB',     tier:'readable', note:'Markdown guide L657 of 752 ceiling on GPT-5.5 runs'},
    {id:'SC-1',  l1:'SC-1',  l2:'125 KB',    tier:'readable', note:'Gemini API docs widest per-LLM retrieval strategy spread'},
    {id:'BL-1',  l1:'BL-1',  l2:'509 KB',    tier:'large',    note:'MongoDB docs L420 ceiling holds with L119 outlier'},
    {id:'OP-2',  l1:'OP-2',  l2:'242 KB',    tier:'large',    note:'MDN reference ceiling splits by LLM, L317 vs L590'},
    {id:'OP-1',  l1:'OP-1',  l2:'740 KB',    tier:'large',    note:'Wikipedia with URL fragment, fragment dropped with L304/L556 LLM split'},
    {id:'SC-3',  l1:'SC-3',  l2:'786 KB',    tier:'large',    note:'Table-heavy Wikipedia L353 ceiling near-universal'},
    {id:'OP-4',  l1:'OP-4',  l2:'514 KB',    tier:'large',    note:'CommonMark Spec with clusters L237 vs L616'},
    {id:'EC-1',  l1:'EC-1',  l2:'120 KB',    tier:'spa',      note:'Gemini API SPA with one task failure, one headless-Chrome recovery run'},
    {id:'BL-3',  l1:'BL-3',  l2:'4.5-4.85 MB', tier:'spa',    note:'MongoDB tutorial replacement URL, Cache Miss in all web use'},
    {id:'SC-2',  l1:'SC-2',  l2:'578 KB',    tier:'spa',      note:'Anthropic API docs — Next.js shell, prose absent; 134,804-token display truncation marker'},
  ];

  var LEVELS = ['L','M','H','XH'];
  var MODELS = ['5.4m','5.4','5.5'];

  var MODEL_LABELS = {
    '5.4m': 'GPT-5.4-Mini',
    '5.4':  'GPT-5.4',
    '5.5':  'GPT-5.5',
  };
  var LEVEL_LABELS = { L:'Light', M:'Medium', H:'High', XH:'Extra High' };

  // Truncation tier per run, sourced from results/vscode-codex-interpreted/results.csv `truncated` column.
  // One correction applied: SC-2's 5th row has LLM_observed mislabeled as GPT-5.4-Mini/Extra High in the
  // CSV; its notes, tools, and output figures match GPT-5.5 Low exactly, so it's keyed here as 5.5:L.
  // Where a cell had two rows (a failed attempt plus a completed retry, or an accidental duplicate run),
  // the completed/first run is used here; see the Emergent Findings and Log Label Summary in the matching
  // test ID doc for the other run.
  var runs = {
    'EC-3': {
      '5.4m:L':'no','5.4m:M':'no','5.4m:H':'no','5.4m:XH':'no',
      '5.4:L':'no','5.4:M':'no','5.4:H':'no','5.4:XH':'mixed',
      '5.5:L':'no','5.5:M':'no','5.5:H':'no','5.5:XH':'no',
    },
    'BL-2': {
      '5.4m:L':'no','5.4m:M':'no','5.4m:H':'no','5.4m:XH':'no',
      '5.5:L':'no','5.5:M':'no','5.5:H':'no','5.5:XH':'no',
    },
    'EC-6': {
      '5.4m:L':'no','5.4m:M':'mixed','5.4m:H':'mixed','5.4m:XH':'yes',
      '5.4:L':'mixed','5.4:M':'mixed','5.4:H':'yes','5.4:XH':'yes',
      '5.5:L':'mixed','5.5:M':'mixed','5.5:H':'mixed','5.5:XH':'mixed',
    },
    'SC-4': {
      '5.4m:L':'no','5.4m:M':'implicit','5.4m:H':'mixed','5.4m:XH':'mixed',
      '5.5:L':'yes','5.5:M':'mixed','5.5:H':'mixed','5.5:XH':'mixed',
    },
    'SC-1': {
      '5.4m:L':'no','5.4m:M':'implicit','5.4m:H':'mixed','5.4m:XH':'implicit',
      '5.5:L':'implicit','5.5:M':'mixed','5.5:H':'implicit','5.5:XH':'implicit',
    },
    'BL-1': {
      '5.4m:L':'mixed','5.4m:M':'mixed','5.4m:H':'mixed','5.4m:XH':'mixed',
      '5.5:L':'mixed','5.5:M':'yes','5.5:H':'mixed','5.5:XH':'yes',
    },
    'OP-2': {
      '5.4m:L':'implicit','5.4m:M':'yes','5.4m:H':'yes','5.4m:XH':'implicit',
      '5.5:L':'yes','5.5:M':'mixed','5.5:H':'mixed','5.5:XH':'mixed',
    },
    'OP-1': {
      '5.4m:L':'implicit','5.4m:M':'yes','5.4m:H':'implicit','5.4m:XH':'mixed',
      '5.5:L':'yes','5.5:M':'mixed','5.5:H':'no','5.5:XH':'yes',
    },
    'SC-3': {
      '5.4m:L':'yes','5.4m:M':'yes','5.4m:H':'mixed','5.4m:XH':'mixed',
      '5.5:L':'yes','5.5:M':'mixed','5.5:H':'implicit','5.5:XH':'yes',
    },
    'OP-4': {
      '5.4m:L':'no','5.4m:M':'mixed','5.4m:H':'yes','5.4m:XH':'mixed',
      '5.5:L':'mixed','5.5:M':'mixed','5.5:H':'mixed','5.5:XH':'no',
    },
    'EC-1': {
      '5.4m:L':'no','5.4m:M':'implicit','5.4m:H':'mixed','5.4m:XH':'no',
      '5.4:L':'implicit','5.4:M':'mixed','5.4:H':'mixed','5.4:XH':'yes',
      '5.5:L':'no','5.5:M':'no','5.5:H':'no','5.5:XH':'implicit',
    },
    'BL-3': {
      '5.4m:L':'no','5.4m:M':'no','5.4m:H':'implicit','5.4m:XH':'no',
      '5.5:L':'mixed','5.5:M':'no','5.5:H':'no','5.5:XH':'no',
    },
    'SC-2': {
      '5.4m:L':'yes','5.4m:M':'no','5.4m:H':'mixed','5.4m:XH':'mixed',
      '5.5:L':'mixed','5.5:M':'yes','5.5:H':'mixed','5.5:XH':'yes',
    },
  };

  var SURFACE_NOTE = {
    'no':       'No truncation signal, curl-complete or payload too small to test',
    'implicit': 'Implicit truncation through reasoning or tooling pivot',
    'mixed':    'Mixed truncation signal, both paths used, web limits reported',
    'yes':      'Truncation reported with web use',
  };

  function getColors(dark, tier) {
    // no       → green  — no truncation signal, best outcome
    // implicit → amber  — escalated without naming the limit, self-report gap
    // mixed    → blue   — both paths used, most transparent self-report
    // yes      → pink   — web.open hit and reported, least complete outcome
    var map = {
      'no':       { bg: dark ? '#0F6E56' : '#1D9E75', fg: '#fff',                       label: 'N' },
      'implicit': { bg: dark ? '#cba452' : '#FFB74D', fg: dark ? '#412402' : '#412402', label: 'I' },
      'mixed':    { bg: dark ? '#185FA5' : '#378ADD', fg: '#fff',                       label: 'M' },
      'yes':      { bg: dark ? '#A32D2D' : '#F06292', fg: '#fff',                       label: 'Y' },
    };
    return map[tier] || { bg: dark ? '#363634' : '#d0cec7', fg: 'inherit', label: '' };
  }

  function getTierHeaderBg(dark, tier) {
    if (tier === 'readable') return dark ? 'rgba(0,120,80,0.12)' : 'rgba(0,160,100,0.07)';
    if (tier === 'large')    return dark ? 'rgba(30,80,160,0.12)' : 'rgba(40,100,200,0.07)';
    if (tier === 'spa')      return dark ? 'rgba(140,0,0,0.15)'   : 'rgba(200,30,30,0.07)';
    return 'transparent';
  }

  function getTierLabel(tier) {
    if (tier === 'readable') return 'Readable Static';
    if (tier === 'large')    return 'Large Static HTML';
    if (tier === 'spa')      return 'JS-rendered / SPA';
    return '';
  }

  function LegendTable(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var cs = {fontFamily:'monospace', fontSize:10,
      background:'rgba(128,128,128,0.15)', borderRadius:2, padding:'1px 3px'};
    var C = function(t) { return e('code', {style:cs}, t); };
    var items = [
      { tier: 'no',       desc: ['No: truncation not reported, ', C('curl'), '-complete and/or payload too small to test'] },
      { tier: 'implicit', desc: ['Implicit: truncation through tooling pivot and exposed reasoning'] },
      { tier: 'mixed',    desc: ['Mixed: truncation report split with both paths used, ', C('web'), 'limits named'] },
      { tier: 'yes',      desc: ['Yes: truncation reported with ', C('web'), 'limits named'] },
    ];
    return e('table', {style:{borderCollapse:'collapse', fontSize:11, marginTop:0}},
      e('tbody', null, items.map(function(item) {
        var c = getColors(dark, item.tier);
        return e('tr', {key:item.tier},
          e('td', {style:{paddingRight:8, paddingBottom:4, verticalAlign:'middle'}},
            e('span', {style:{
              display:'inline-flex', alignItems:'center', justifyContent:'center',
              width:32, height:16, borderRadius:3,
              background:c.bg, color:c.fg, fontSize:10, fontWeight:600
            }}, c.label)
          ),
          e('td', {style:{paddingBottom:4, color:tc, opacity:0.8}}, item.desc)
        );
      }))
    );
  }

  function NoteBlock(props) {
    var tc = props.textColor || 'inherit';
    var cs = {fontFamily:'monospace', fontSize:10,
      background:'rgba(128,128,128,0.15)', borderRadius:2, padding:'1px 3px'};
    var C = function(t) { return e('code', {style:cs}, t); };
    return e('p', {style:{fontSize:11, marginTop:8, lineHeight:1.6, opacity:0.65, color:tc}},
      e('i', null,
        'Columns grouped left-to-right by content accessibility: static pages where tools return readable content; large static HTML where ', C('web'), ' truncates but ', C('curl'), 'is readable; JS-rendered/SPAs ', C('curl'), ' returns a text-less shell. ',
        C('GPT-5.4'), ' only ran ', C('EC'), ' tests, renders as empty cells elsewhere. ',
        C('SC-3'), ' has 9 runs; failed capacity-error attempt folded into completed retry\'s cell. Hover over cells for details.'
      )
    );
  }

  function HeatmapTable(props) {
    var dark = props.isDark;
    var large = props.large;
    var tc = props.textColor || 'inherit';
    var cellW  = large ? 52  : 38;
    var cellH  = large ? 30  : 24;
    var labelW = large ? 110 : 86;
    var fs     = large ? 11  : 10;

    var rows = [];
    LEVELS.forEach(function(level) {
      rows.push({ type: 'level-header', level: level });
      MODELS.forEach(function(llm) {
        rows.push({ type: 'data', llm: llm, level: level, key: llm + ':' + level });
      });
    });

    return e('div', {className:'cdx3-wrap'},
      e('table', {className:'cdx3'},
        e('thead', null,
          e('tr', null,
            e('th', {className:'cdx3-rh', style:{minWidth:labelW, color:tc}},
              'LLM / Reasoning'
            ),
            cols.map(function(col) {
              return e('th', {key:col.id, title:col.note,
                style:{color:tc, background:getTierHeaderBg(dark, col.tier)}},
                col.l1,
                e('span', {className:'cdx3-sub'}, col.l2)
              );
            })
          ),
          e('tr', null,
            e('th', {className:'cdx3-rh', style:{color:tc, fontSize:9, opacity:0.4,
              fontWeight:400, paddingBottom:4}},''),
            (function() {
              var groups = [];
              cols.forEach(function(col) {
                if (!groups.length || groups[groups.length-1].tier !== col.tier) {
                  groups.push({tier:col.tier, count:1});
                } else {
                  groups[groups.length-1].count++;
                }
              });
              return groups.map(function(g, i) {
                return e('th', {key:'tier-'+g.tier+i, colSpan:g.count,
                  style:{fontSize:9, opacity:0.55, fontWeight:600,
                    textAlign:'center', color:tc,
                    background:getTierHeaderBg(dark, g.tier),
                    borderTop:'1px solid rgba(128,128,128,0.15)',
                    letterSpacing:'0.04em'}},
                  getTierLabel(g.tier)
                );
              });
            })()
          )
        ),
        e('tbody', null,
          rows.map(function(row) {
            if (row.type === 'level-header') {
              return e('tr', {key:'lh-'+row.level,
                style:{borderTop:'1.5px solid rgba(128,128,128,0.22)'}},
                e('td', {colSpan: cols.length + 1,
                  style:{fontSize:10, fontWeight:700, letterSpacing:'0.07em',
                    opacity:0.55, paddingTop:5, paddingBottom:1,
                    textTransform:'uppercase', textAlign:'center', color:tc}},
                  LEVEL_LABELS[row.level]
                )
              );
            }

            var rowKey = row.key;
            return e('tr', {key:rowKey},
              e('td', {className:'cdx3-rl cdx3-llm', style:{color:tc, maxWidth:labelW, width:labelW}},
                MODEL_LABELS[row.llm]
              ),
              cols.map(function(col) {
                var tier = (runs[col.id] || {})[rowKey];
                if (!tier) {
                  return e('td', {key:col.id},
                    e('div', {style:{
                      width:cellW, height:cellH, margin:'1px auto',
                      borderRadius:3,
                      background: dark ? '#2a2a28' : '#e0e0de'
                    }})
                  );
                }
                var c = getColors(dark, tier);
                var tip = col.l1 + ' · ' + MODEL_LABELS[row.llm] + ' ' +
                  LEVEL_LABELS[row.level] + '\n' + SURFACE_NOTE[tier];
                return e('td', {key:col.id,
                  style:{background:getTierHeaderBg(dark, col.tier)}},
                  e('div', {title:tip, style:{
                    borderRadius:3, fontSize:fs, fontWeight:700,
                    display:'flex', alignItems:'center', justifyContent:'center',
                    width:cellW, height:cellH, margin:'1px auto',
                    background:c.bg, color:c.fg, cursor:'help'
                  }}, c.label)
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

    return e('div', {style:{marginTop:'1.5rem', fontFamily:'inherit'}},
      e('div', {onClick:function(){ setOpen(true); }, style:{cursor:'pointer'}},
        e(HeatmapTable, {isDark:dark, large:false}),
        e('p', {className:'cdx3-hint'}, '\u2197 click to expand')
      ),
      e('div', {style:{display:'flex', gap:28, alignItems:'flex-start',
        flexWrap:'wrap', marginTop:10, justifyContent:'center'}},
        e('div', {style:{flexShrink:0}}, e(LegendTable, {isDark:dark})),
        e('div', {style:{flex:1, maxWidth:460}}, e(NoteBlock, {isDark:dark}))
      ),
      isOpen && e('div', {
        className:'cdx3-overlay',
        onClick:function(ev){ if (ev.target===ev.currentTarget) setOpen(false); }
      },
        e('div', {className:'cdx3-overlay-inner',
          style:{background:lbBg, color:lbText, width:'99vw'}},
          e('button', {className:'cdx3-close', style:{color:lbText},
            onClick:function(){ setOpen(false); }, 'aria-label':'Close'}, '\u00d7'),
          e(HeatmapTable, {isDark:dark, large:true, textColor:lbText}),
          e('div', {style:{display:'flex', gap:28, alignItems:'flex-start',
            flexWrap:'wrap', marginTop:10, justifyContent:'center'}},
            e('div', {style:{flexShrink:0}}, e(LegendTable, {isDark:dark, textColor:lbText})),
            e('div', {style:{flex:1, maxWidth:460}}, e(NoteBlock, {isDark:dark, textColor:lbText}))
          )
        )
      )
    );
  }

  var root = ReactDOM.createRoot(document.getElementById('cdx-hm3-root'));
  root.render(e(App));
})();
</script>
{% endraw %}

---

## Truncation Analysis

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`web` returns line-indexed, rendered text, extraction window, not full page** | All<br>tests | Returns a line-numbered, HTML-to-text-extracted viewport; `OP-4`'s toolchain includes `wordlim: 200`; most reports include `Total lines: N` | **Output chars on `web` path reflect viewport depth, not retrieval ceiling; `curl` remains only path to raw HTTP body** |
| 2 | **No fixed character or token ceiling detected with `curl`** | `BL-1`<br>`BL-3`<br>`OP-1` `OP-2`<br>`OP-4` `SC-3` `EC-6` | `BL-3`: `GPT-5.5 Low`, `Medium`, `High` retrieved ~4.85M chars; `OP-4`: 6/8 runs retrieved 514,092 chars, several in under a minute | **Char/token access is escalation-test-ID-gated, not architecturally defined** |
| 3 | **Truncation layers conflict within test cycles** | `BL-3` `EC-6` `SC-2` | `BL-3` cutpoint at structural boundary against terminal display cutoff at arbitrary position; `EC-6` confirms `web` line ceiling independent from HTTP body; `SC-2`'s terminal display shows token-count marker independent of both | **Self-reported truncation tool-dependent, disambiguating layers requires per-run, per-page-architecture analysis** |
| 4 | **`curl` escalation success size and LLM-version-dependent** | All<br>tests | 68/119 runs, 57% success rate; ranges `EC-3`'s 2/12 to `BL-2`'s 8/8 depending on agent's choice and/or whether payload size requires escalation | **Unlike `T1`'s cleaner per-version threshold, same `T2` LLM bypasses `web` entirely on one test, fails to escalate on another** |
| 5 | **Higher reasoning levels continue to show inconsistent and/or diminishing or returns** | `BL-3` `EC-6`<br>`SC-1` `SC-3` | `EC-6`'s `GPT-5.4-Mini Extra High` spent 11m37s across three failed tool paths to retrieve nothing, while `Light` completed same test in 29 seconds; `SC-3`'s<br>`GPT-5.5 Extra High` ran most streamlined path in its cycle | **`Extra High` doesn't reliably improve retrieval outcomes; in several test cycles actively underperforms against `Light`/`Low`** |
| 6 | **Single write destination risks constant collision** | `BL-1`<br>`BL-2` `EC-1` `EC-6` `OP-4` | `T1` agents mostly wrote-reported to `Documents/GitHub/Codex`, most `T2` agents wrote to `/private/tmp` without reporting it; `BL-1`'s `GPT-5.4-Mini High` only agent to write to project; `SC-4`'s `GPT-5.4-Mini Extra High` read prior logs instead of fetching; filename collision recurs across 16+ cycles, most heavily in `EC-6`, `OP-4` | **`/private/tmp` clearing between sessions reduces cross-cycle collision, stale artifacts can't persist to be misread later, but reducing paths to temp storage without any infrastructure contributes to constant collision, requires observability to untangle** |
| 7 | **JS-rendered pages remain structural retrieval failure** | `BL-3` `SC-2` | `BL-3`: a replacement URL, different from `T1`'s retired original, produces similar JS-rendered tutorial-body-absent pattern; `SC-2`: Next.js hydrated shell, ~578,000 chars, prose absent | **Neither `web` nor `curl` returns prose for CSP-gated or client-hydrated pages regardless of surface, pattern holds across URL replacement** |
| 8 | **`Cache Miss` no longer systematic for URL that defined it** | `BL-3` `EC-6` | `BL-3` includes `Cache Miss` all results; 1/13 `EC-6` includes `Cache Miss` string vs `T1`'s 17/20; others return windowed `L54` extraction instead | **Failure signature maybe URL-specific rather than stable property of raw and/or large payloads; same URL anchored `T1`'s `Cache Miss` finding fails silently into `T2` text slice** |
| 9 | **`web` line ceiling page-architecture-driven** | `EC-6` `SC-2` `SC-3` | `EC-6`'s `L54` identical cutpoint 10/13 runs; `SC-2`'s `L139-140` and `SC-3`'s `L353` show comparably tight cross-LLM clustering | **Where `T1` found LLM-version-correlated windows, `T2`'s tightest cycles show opposite, same ceiling regardless of LLM. `OP-1`, `OP-2`, `OP-4` show LLM-family splits; mechanisms coexist depending on URL** |
| 10 | **`T2` agents reported `wordlim:200` less** | `OP-4` | `GPT-5.4-Mini Extra High`'s reported `web` reference `wordlim:200` alongside extraction window `turn0view0`, while `T1` agents cited it at least 10+ | **In spite of `web` usage, no strong support for `T1`'s `SC-1` inference as agent-adjustable parameter, less visibility likely due to version upgrades, stronger security** |

## Retrieval Paths

The second heat map encodes retrieval path, built from `tools_named` cross-checked against `output_chars` and, where needed, the source screenshot: a tool listed as attempted only counts if the reported output actually traces back to it, since `tools_named` is itself an agent self-report and sometimes under-reports what was used. `python3 urllib` and headless Chrome get their own categories, `web+python` and `browser`, rather than folding into `curl`, since which tool an agent reaches for is a real behavioral signal, not a cosmetic difference.

{% raw %}
<div id="cdx-hm4-root"></div>

<style>
.cdx4-wrap { overflow-x: auto; }
table.cdx4 { border-collapse: collapse; width: 100%; }
table.cdx4 th { font-size: 10px; font-weight: 500; padding: 3px 4px; text-align: center; white-space: nowrap; color: inherit; }
table.cdx4 th.cdx4-rh { text-align: left; }
table.cdx4 th .cdx4-sub { font-weight: 400; font-size: 10px; opacity: 0.55; display: block; }
table.cdx4 td { padding: 2px 2px; text-align: center; }
table.cdx4 td.cdx4-rl { font-size: 11px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; vertical-align: middle; }
table.cdx4 td.cdx4-rl.cdx4-model { font-size: 10px; opacity: 0.65; padding-left: 8px; }
.cdx4-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.cdx4-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.78);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.cdx4-overlay-inner {
  border-radius: 10px; padding: 22px 26px;
  max-width: 99vw; max-height: 93vh;
  overflow: auto; position: relative;
}
.cdx4-close {
  position: absolute; top: 10px; right: 12px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.cdx4-close:hover { opacity: 1; }
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

  var cols = [
    {id:'EC-3',  l1:'EC-3',  l2:'254-660 B', tier:'readable', note:'Redirect JSON — both paths return usable content, distinction is which path is reported'},
    {id:'BL-2',  l1:'BL-2',  l2:'5.8 KB',    tier:'readable', note:'Raw Markdown — curl dominant, 7 of 8 runs escalate for a payload this small'},
    {id:'EC-6',  l1:'EC-6',  l2:'92 KB',     tier:'readable', note:'Raw GitHub Markdown — two GPT-5.4 High/Extra High runs never touch curl at all'},
    {id:'SC-4',  l1:'SC-4',  l2:'65 KB',     tier:'readable', note:'Markdown Guide — one run used python3 urllib in place of curl, its own category here'},
    {id:'SC-1',  l1:'SC-1',  l2:'125 KB',    tier:'readable', note:'Gemini API docs — widest per-model strategy spread, all four GPT-5.4-Mini levels differ'},
    {id:'BL-1',  l1:'BL-1',  l2:'509 KB',    tier:'large',    note:'MongoDB docs — curl succeeds in 6 of 8 runs'},
    {id:'OP-2',  l1:'OP-2',  l2:'242 KB',    tier:'large',    note:'MDN Array — curl succeeds in only 4 of 8, several curl attempts fail without escalation'},
    {id:'OP-1',  l1:'OP-1',  l2:'740 KB',    tier:'large',    note:'Wikipedia + #fragment — curl succeeds in 3 of 8; one run converts full HTML via xmllint/pandoc/lynx'},
    {id:'SC-3',  l1:'SC-3',  l2:'786 KB',    tier:'large',    note:'Wikipedia population table — curl succeeds in 4 of 8 canonical cells'},
    {id:'OP-4',  l1:'OP-4',  l2:'514 KB',    tier:'large',    note:'CommonMark spec — GPT-5.5 Medium and Extra High bypass web entirely'},
    {id:'EC-1',  l1:'EC-1',  l2:'120 KB',    tier:'spa',      note:'Gemini API SPA — one total failure, one headless-Chrome recovery via Playwright, its own category here'},
    {id:'BL-3',  l1:'BL-3',  l2:'4.5-4.85 MB', tier:'spa',    note:'MongoDB Vector Search tutorial, T2 replacement URL — one total failure, one python3-urllib recovery'},
    {id:'SC-2',  l1:'SC-2',  l2:'578 KB',    tier:'spa',      note:'Anthropic API docs — curl succeeds in 5 of 8; one run resolved from the source screenshot after tools_named omitted both a failed node fetch and the successful curl step'},
  ];

  var LEVELS = ['L','M','H','XH'];
  var MODELS = ['5.4m','5.4','5.5'];

  var MODEL_LABELS = { '5.4m': 'GPT-5.4-Mini', '5.4': 'GPT-5.4', '5.5': 'GPT-5.5' };
  var LEVEL_LABELS = { L:'Light', M:'Medium', H:'High', XH:'Extra High' };

  // Retrieval path per run, classified by tracing output_chars back to the tool that actually produced it,
  // not by which tools appear in tools_named, since that field is itself agent self-reported and sometimes
  // under-reports a tool that was actually used. python3 urllib (SC-4's GPT-5.4-Mini Light, BL-3's
  // GPT-5.4-Mini Extra High) and headless Chrome via Playwright (EC-1's GPT-5.4-Mini High) get their own
  // categories rather than folding into curl/web+curl; the mechanism is a genuinely different signal about
  // what the agent reached for, not a cosmetic difference in tool name. SC-2's GPT-5.4-Mini High looked
  // unresolvable from tools_named alone ("web.open, turn0view0" only), but the source screenshot shows the
  // full sequence directly: web.open, then a failed node fetch (DNS ENOTFOUND), then a successful curl
  // fetch matching the full 578,233-char body every other successful SC-2 run reports. Classified
  // web+curl on that direct evidence rather than the incomplete CSV field.
  // Same duplicate-cell handling as the truncation-tier grid.
  var runs = {
    'EC-3': {
      '5.4m:L':'web','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web',
      '5.4:L':'web','5.4:M':'web','5.4:H':'web','5.4:XH':'web',
      '5.5:L':'web','5.5:M':'web','5.5:H':'web','5.5:XH':'web',
    },
    'BL-2': {
      '5.4m:L':'web+curl','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.5:L':'web+curl','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'curl',
    },
    'EC-6': {
      '5.4m:L':'curl','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web',
      '5.4:L':'web+curl','5.4:M':'web+curl','5.4:H':'web','5.4:XH':'web',
      '5.5:L':'web+curl','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'SC-4': {
      '5.4m:L':'web+python','5.4m:M':'web','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.5:L':'web','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'SC-1': {
      '5.4m:L':'web+curl','5.4m:M':'web','5.4m:H':'web','5.4m:XH':'web',
      '5.5:L':'web','5.5:M':'curl','5.5:H':'web+curl','5.5:XH':'web',
    },
    'BL-1': {
      '5.4m:L':'web+curl','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.5:L':'web+curl','5.5:M':'web','5.5:H':'web+curl','5.5:XH':'web',
    },
    'OP-2': {
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web','5.4m:XH':'web+curl',
      '5.5:L':'web','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'OP-1': {
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web','5.4m:XH':'web+curl',
      '5.5:L':'web','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web',
    },
    'SC-3': {
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.5:L':'web','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web',
    },
    'OP-4': {
      '5.4m:L':'web','5.4m:M':'web+curl','5.4m:H':'web','5.4m:XH':'web+curl',
      '5.5:L':'web+curl','5.5:M':'curl','5.5:H':'web+curl','5.5:XH':'curl',
    },
    'EC-1': {
      '5.4m:L':'none','5.4m:M':'web','5.4m:H':'browser','5.4m:XH':'web+curl',
      '5.4:L':'web+curl','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'web',
      '5.5:L':'web+curl','5.5:M':'curl','5.5:H':'curl','5.5:XH':'web',
    },
    'BL-3': {
      '5.4m:L':'none','5.4m:M':'web+curl','5.4m:H':'web','5.4m:XH':'web+python',
      '5.5:L':'web+curl','5.5:M':'curl','5.5:H':'curl','5.5:XH':'web+curl',
    },
    'SC-2': {
      '5.4m:L':'web','5.4m:M':'curl','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.5:L':'web+curl','5.5:M':'web','5.5:H':'web+curl','5.5:XH':'web',
    },
  };

  var SURFACE_NOTE = {
    'web':        'web.open only, output traces to the rendered extraction',
    'web+curl':   'output traces to a full-body fetch via curl, web.open also attempted',
    'curl':       'output traces to a full-body fetch via curl, web.open not attempted',
    'web+python': 'output traces to a full-body fetch via python3 urllib, web.open also attempted',
    'browser':    'output traces to headless-Chrome browser automation via Playwright, after curl and other paths failed',
    'none':       'no usable content retrieved on any path',
  };

  function getColors(dark, path) {
    var map = {
      'web':        { bg: dark ? '#0F6E56' : '#1D9E75', fg: '#fff',                       label: 'W'   },
      'web+curl':   { bg: dark ? '#185FA5' : '#378ADD', fg: '#fff',                       label: 'W+C' },
      'curl':       { bg: dark ? '#cba452' : '#FFB74D', fg: dark ? '#412402' : '#412402', label: 'C'   },
      'web+python': { bg: dark ? '#0e7a8c' : '#26b8cf', fg: '#fff',                       label: 'W+P' },
      'browser':    { bg: dark ? '#5b3a9e' : '#9575cd', fg: '#fff',                       label: 'B'   },
      'none':       { bg: dark ? '#D4537E' : '#FF8A65', fg: '#fff',                       label: '✗'   },
    };
    return map[path] || { bg: dark ? '#363634' : '#d0cec7', fg: 'inherit', label: '' };
  }

  function getTierHeaderBg(dark, tier) {
    if (tier === 'readable') return dark ? 'rgba(0,120,80,0.12)' : 'rgba(0,160,100,0.07)';
    if (tier === 'large')    return dark ? 'rgba(30,80,160,0.12)' : 'rgba(40,100,200,0.07)';
    if (tier === 'spa')      return dark ? 'rgba(140,0,0,0.15)'   : 'rgba(200,30,30,0.07)';
    return 'transparent';
  }

  function getTierLabel(tier) {
    if (tier === 'readable') return 'Readable Static';
    if (tier === 'large')    return 'Large Static HTML';
    if (tier === 'spa')      return 'JS-rendered / SPA';
    return '';
  }

  function LegendTable(props) {
    var dark = props.isDark;
    var tc = props.textColor || 'inherit';
    var cs = {fontFamily:'monospace', fontSize:10,
      background:'rgba(128,128,128,0.15)', borderRadius:2, padding:'1px 3px'};
    var C = function(t) { return e('code', {style:cs}, t); };
    var items = [
      { path: 'web',        desc: [C('web.open'), ' only, output traces to the rendered extraction'] },
      { path: 'web+curl',   desc: ['Output traces to a full-body fetch via ', C('curl'), ', ', C('web.open'), ' also attempted'] },
      { path: 'curl',       desc: ['Output traces to a full-body fetch via ', C('curl'), ', ', C('web.open'), ' not attempted'] },
      { path: 'web+python', desc: ['Output traces to a full-body fetch via ', C('python3 urllib'), ' instead of ', C('curl')] },
      { path: 'browser',    desc: ['Output traces to headless-Chrome browser automation, after ', C('curl'), ' failed'] },
      { path: 'none',       desc: ['No usable content retrieved on any path'] },
    ];
    return e('table', {style:{borderCollapse:'collapse', fontSize:11, marginTop:0}},
      e('tbody', null, items.map(function(item) {
        var c = getColors(dark, item.path);
        return e('tr', {key:item.path},
          e('td', {style:{paddingRight:8, paddingBottom:4, verticalAlign:'middle'}},
            e('span', {style:{
              display:'inline-flex', alignItems:'center', justifyContent:'center',
              width:32, height:16, borderRadius:3,
              background:c.bg, color:c.fg, fontSize:10, fontWeight:600
            }}, c.label)
          ),
          e('td', {style:{paddingBottom:4, color:tc, opacity:0.8}}, item.desc)
        );
      }))
    );
  }

  function NoteBlock(props) {
    var tc = props.textColor || 'inherit';
    var cs = {fontFamily:'monospace', fontSize:10,
      background:'rgba(128,128,128,0.15)', borderRadius:2, padding:'1px 3px'};
    var C = function(t) { return e('code', {style:cs}, t); };
    return e('p', {style:{fontSize:11, marginTop:8, lineHeight:1.6, opacity:0.65, color:tc}},
      e('i', null,
        C('W'), ' = ', C('web.open'), ' only; ', C('W+C'), ' = both attempted, output from a full curl fetch; ',
        C('C'), ' = full curl fetch, ', C('web.open'), ' not attempted; ', C('W+P'), ' = full fetch via ', C('python3 urllib'), ' instead of ', C('curl'), '; ',
        C('B'), ' = headless-Chrome browser automation; ', C('\u2717'), ' = no usable content on any path. ',
        C('GPT-5.4'), ' only ran ', C('EC-1'), ', ', C('EC-3'), ', and ', C('EC-6'), ', empty cells elsewhere. ',
        'No run in this corpus produced a clean "', C('web'), ' attempted and failed, nothing else tried" case; every near-zero output either had real uncounted ', C('web.open'), ' content or was a total multi-tool failure. Hover cells for the specific mechanism.'
      )
    );
  }

  function HeatmapTable(props) {
    var dark = props.isDark;
    var large = props.large;
    var tc = props.textColor || 'inherit';
    var cellW  = large ? 52  : 38;
    var cellH  = large ? 30  : 24;
    var labelW = large ? 110 : 86;
    var fs     = large ? 11  : 10;

    var rows = [];
    LEVELS.forEach(function(level) {
      rows.push({ type: 'level-header', level: level });
      MODELS.forEach(function(model) {
        rows.push({ type: 'data', model: model, level: level, key: model + ':' + level });
      });
    });

    return e('div', {className:'cdx4-wrap'},
      e('table', {className:'cdx4'},
        e('thead', null,
          e('tr', null,
            e('th', {className:'cdx4-rh', style:{minWidth:labelW, color:tc}}, 'LLM / Reasoning'),
            cols.map(function(col) {
              return e('th', {key:col.id, title:col.note,
                style:{color:tc, background:getTierHeaderBg(dark, col.tier)}},
                col.l1, e('span', {className:'cdx4-sub'}, col.l2)
              );
            })
          ),
          e('tr', null,
            e('th', {className:'cdx4-rh', style:{color:tc, fontSize:9, opacity:0.4,
              fontWeight:400, paddingBottom:4}},''),
            (function() {
              var groups = [];
              cols.forEach(function(col) {
                if (!groups.length || groups[groups.length-1].tier !== col.tier) {
                  groups.push({tier:col.tier, count:1});
                } else {
                  groups[groups.length-1].count++;
                }
              });
              return groups.map(function(g, i) {
                return e('th', {key:'tier-'+g.tier+i, colSpan:g.count,
                  style:{fontSize:9, opacity:0.55, fontWeight:600,
                    textAlign:'center', color:tc,
                    background:getTierHeaderBg(dark, g.tier),
                    borderTop:'1px solid rgba(128,128,128,0.15)',
                    letterSpacing:'0.04em'}},
                  getTierLabel(g.tier)
                );
              });
            })()
          )
        ),
        e('tbody', null,
          rows.map(function(row) {
            if (row.type === 'level-header') {
              return e('tr', {key:'lh-'+row.level,
                style:{borderTop:'1.5px solid rgba(128,128,128,0.22)'}},
                e('td', {colSpan: cols.length + 1,
                  style:{fontSize:10, fontWeight:700, letterSpacing:'0.07em',
                    opacity:0.55, paddingTop:5, paddingBottom:1,
                    textTransform:'uppercase', textAlign:'center', color:tc}},
                  LEVEL_LABELS[row.level]
                )
              );
            }
            var rowKey = row.key;
            return e('tr', {key:rowKey},
              e('td', {className:'cdx4-rl cdx4-model', style:{color:tc, maxWidth:labelW, width:labelW}},
                MODEL_LABELS[row.model]
              ),
              cols.map(function(col) {
                var path = (runs[col.id] || {})[rowKey];
                if (!path) {
                  return e('td', {key:col.id},
                    e('div', {style:{
                      width:cellW, height:cellH, margin:'1px auto',
                      borderRadius:3,
                      background: dark ? '#2a2a28' : '#e0e0de'
                    }})
                  );
                }
                var c = getColors(dark, path);
                var tip = col.l1 + ' · ' + MODEL_LABELS[row.model] + ' ' +
                  LEVEL_LABELS[row.level] + '\n' + SURFACE_NOTE[path];
                return e('td', {key:col.id,
                  style:{background:getTierHeaderBg(dark, col.tier)}},
                  e('div', {title:tip, style:{
                    borderRadius:3, fontSize:fs, fontWeight:700,
                    display:'flex', alignItems:'center', justifyContent:'center',
                    width:cellW, height:cellH, margin:'1px auto',
                    background:c.bg, color:c.fg, cursor:'help'
                  }}, c.label)
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

    return e('div', {style:{marginTop:'1.5rem', fontFamily:'inherit'}},
      e('div', {onClick:function(){ setOpen(true); }, style:{cursor:'pointer'}},
        e(HeatmapTable, {isDark:dark, large:false}),
        e('p', {className:'cdx4-hint'}, '\u2197 click to expand')
      ),
      e('div', {style:{display:'flex', gap:28, alignItems:'flex-start',
        flexWrap:'wrap', marginTop:10, justifyContent:'center'}},
        e('div', {style:{flexShrink:0}}, e(LegendTable, {isDark:dark})),
        e('div', {style:{flex:1, maxWidth:460}}, e(NoteBlock, {isDark:dark}))
      ),
      isOpen && e('div', {
        className:'cdx4-overlay',
        onClick:function(ev){ if (ev.target===ev.currentTarget) setOpen(false); }
      },
        e('div', {className:'cdx4-overlay-inner',
          style:{background:lbBg, color:lbText, width:'99vw'}},
          e('button', {className:'cdx4-close', style:{color:lbText},
            onClick:function(){ setOpen(false); }, 'aria-label':'Close'}, '\u00d7'),
          e(HeatmapTable, {isDark:dark, large:true, textColor:lbText}),
          e('div', {style:{display:'flex', gap:28, alignItems:'flex-start',
            flexWrap:'wrap', marginTop:10, justifyContent:'center'}},
            e('div', {style:{flexShrink:0}}, e(LegendTable, {isDark:dark, textColor:lbText})),
            e('div', {style:{flex:1, maxWidth:460}}, e(NoteBlock, {isDark:dark, textColor:lbText}))
          )
        )
      )
    );
  }

  var root = ReactDOM.createRoot(document.getElementById('cdx-hm4-root'));
  root.render(e(App));
})();
</script>
{% endraw %}

---

## Retrieval Outcomes

Output chars on the `web` surface aren't a retrieval ceiling metric, but reflect how far the agent traversed through a
line-indexed renderer before stopping or escalating. Artifact write-saves were less consistent than in `T1`; several runs wrote
files without referencing them in the final report, a pattern documented across `SC-1` through `SC-4`. Rows below organized by
page architecture:<br> _raw files → static HTML → reference/wiki → JS-rendered/SPA_

{: .table-perception}
| **Test** | **Expected** | **Received** | **Content Accessibility** | **Agent Characterization** |
| --- | --- | --- | --- | --- |
| **[`EC-3`](https://httpbin.org/redirect/5)<br>Redirect JSON** | ~2 KB | `web`: 660 chars<br>`curl`: 254 chars | 100% | _Complete on both paths_: `GPT-5.4-Mini` favors `curl` as the authoritative measurement path at `Medium` and `High`, the inverse of its own `T1` pattern at those levels |
| **[`BL-2`](https://www.mongodb.com/docs/manual/reference/change-events/create.md)<br>Raw Markdown** | ~20 KB | 5,805 chars, all 8 runs | 100% | _Complete and internally consistent_: the 219-char gap against `T1`'s 6,024 chars most likely reflects a source update between collection windows, not surface behavior |
| **[`EC-6`](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md)<br>Raw GitHub Markdown** | ~60 KB | `curl`: 91,869 chars, 9/13 runs<br>`web`: `L54` cutoff, 10/13 runs | ~100% body where `curl` succeeds; line-capped elsewhere | _No HTTP-layer truncation on any successful `curl` run_: the `L54` `web` cutoff is the single most consistent finding across the whole `T2` corpus, identical regardless of LLM or reasoning level; one run failed to retrieve any content at all |
| **[`SC-4`](https://www.markdownguide.org/basic-syntax/)<br>Markdown Guide** | ~30 KB | `curl`: 64,527 chars, most runs<br>`web`: `L657` of 752 | `curl` 100%, `web` ~87% | _Complete via `curl`_: `L657` ceiling consistent across `GPT-5.5` runs; `GPT-5.4-Mini Extra High` sourced metrics from a prior rollout log rather than fetching, a fallback mode not seen in `T1` |
| **[`SC-1`](https://ai.google.dev/gemini-api/docs/url-context)<br>Gemini<br>API Docs** | ~40 KB | `curl`: 125,248-125,252 chars, 3/8 runs<br>`web`: 16,390-34,000 chars | `curl` 100%, `web` 13-27% | _Complete via `curl` where attempted_: `GPT-5.4-Mini` shows four different retrieval strategies across its four reasoning levels, the widest intra-LLM spread in the `T2` corpus |
| **[`OP-2`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)<br>MDN Reference** | ~120 KB | `curl`: 241,720 chars, 4/8 runs | `curl` 100%, `web` 13-25% | _Complete via `curl`_: line ceiling splits by LLM, `~L317-318` for `GPT-5.4-Mini High`/`Extra High` versus `~L590-591` for `Medium` and all `GPT-5.5` runs, extending `T1`'s `OP-1` finding that the ceiling can be LLM-dependent |
| **[`BL-1`](https://www.mongodb.com/docs/manual/reference/change-events/create/)<br>MongoDB Reference** | ~85 KB | `curl`: 509,025 chars, 6/8 runs | `curl` 100%, `web` ~15-17% | _Complete via `curl`_: the `L420` ceiling isn't as tightly held as `EC-6`'s `L54` - one run, `GPT-5.4-Mini Extra High`, cut at `L119` instead, so this test ID's ceiling is real but less deterministic than the corpus's strongest cases |
| **[`OP-4`](https://spec.commonmark.org/0.31.2/)<br>CommonMark Spec** | ~500 KB | `curl`: 514,092 chars, 6/8 runs | `curl` 100%, `web` 2-3% | _Complete via `curl`_: two clean line-ceiling clusters, `L237` for `GPT-5.4-Mini Medium`/`Extra High` and `L616` for `GPT-5.5 Low`/`High`; two independent filename-collision pairs recurred in this test ID alone |
| **[`OP-1`](https://en.wikipedia.org/wiki/Machine_learning#History)<br>Wikipedia<br>with URL Fragment** | ~40 KB | `curl`: 740,370 chars, 3/8 runs | `curl` 100%, `web` ~0.5-4% | _Complete via `curl`_: `#History` silently dropped on every run, consistent with `T1`; the corpus's clearest LLM-family split, `L304` for `GPT-5.4-Mini` versus `L556` for `GPT-5.5`, held across all 4 reasoning levels each |
| **[`SC-3`](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population)<br>Wikipedia<br>Table-Heavy** | ~100 KB | `curl`: 786,213 chars, 5/9 runs | `curl` 100%, `web` 1-3% | _Complete via `curl`_: `L353` ceiling holds across every LLM and level where observable, one of the tightest single-value clusters in the corpus alongside `EC-6`'s `L54`; one run failed outright on a LLM capacity error |
| **[`EC-1`](https://ai.google.dev/gemini-api/docs)<br>Gemini<br>API Docs** | ~100 KB | `curl`: 119,785-120,001 chars, 8/13 runs | `curl` 100%, `web` 7-18% | _Complete via `curl`_: one run, `GPT-5.4-Mini Light`, is a full task failure with zero usable metrics; one run reached content via headless Chrome rather than `curl`, the corpus's only instance of that recovery path |
| **[`SC-2`](https://docs.anthropic.com/en/api/messages)<br>Anthropic API Docs** | ~80 KB | `curl`: 578,233-578,275 chars, 5/8 runs | Not accessible | _Complete HTML shell, prose absent regardless of path_: JS-hydrated reference content never appears in any run's output; `L139-140` ceiling on `web` near-universal; a token-denominated terminal display truncation, `134,804 tokens truncated`, appeared for the first time in the `T2` corpus |
| **[`BL-3`](https://www.mongodb.com/docs/vector-search/tutorials/quick-start/?deployment-type=atlas&interface=atlas-ui&embedding=auto)<br>MongoDB Vector Search Tutorial** | ~4,531 KB | `curl`: 4,640,208-4,848,853 chars, 5/8 runs | Not accessible | _Complete HTML shell, prose absent_: every `web` attempt returned a literal `Cache Miss`, unlike `EC-6`'s mostly windowed failure mode; one run silently substituted the canonical URL without query parameters, weakening its contribution to every hypothesis; no `T1` baseline exists for this replacement URL |
