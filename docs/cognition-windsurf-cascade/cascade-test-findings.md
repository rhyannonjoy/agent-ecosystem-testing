---
layout: default
title: "Key Findings for Cascade's Web Search Behavior, Cascade-interpreted"
permalink: /docs/cognition-windsurf-cascade/cascade-test-findings
parent: Cognition Windsurf Cascade
---

# Key Findings for Cascade's Web Search Behavior, Cascade-interpreted

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/windsurf-cascade-web-search/web_search_testing_framework.py)

1. Run `python web_search_testing_framework.py --test {test ID} --track interpreted`
2. Review terminal output
3. Copy the provided prompt asking agent to report on fetch results:
   character count, token estimate, truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
4. Open a new Cascade session in Windsurf, paste the prompt into the chat window
5. Approve web fetch calls, but skip requests for runs of local scripts
6. Capture the agent's full response, observations as the interpreted finding;
   the gap between the agent's self-report and actual fetch behavior is a finding
7. Log structured metadata as described in `framework-reference.md`
8. Ensure log results saved to `/results/cascade-interpreted/results.csv`

> _`cascade-implicit` results document web fetch requests, but no explicit calls to Cascade's tools - a pipeline with a two-stage chunked
> architecture wihtout a single-call full-page retrieval path; restricted to `read_url_content` → `view_content_chunk`; see
> [Friction: Interpreted](friction-note-interpreted.md#read_url_content--fetch-architecture-and-parsing-limits) for analysis._

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard Character Limit** | _None detected_: `read_url_content` returns a chunked index, not raw content with a byte ceiling; output chars reflect agent chunk selection depth from a pipeline that has no full-page retrieval path |
| **Hard Token Limit** | _None detected_: estimates ranged from ~82 to ~65,000 tokens;<br>no run hit a fixed ceiling |
| **Output Consistency** | _Agent-dependent_: same URL and prompt produces 0–106,000 chars<br>depending on agent and chunk selection |
| **Content Selection Behavior** | _Two-stage chunked retrieval_: `read_url_content` returns a positional<br>index with summaries; content requires sequential `view_content_chunk`<br>calls per position |
| **Truncation Pattern** | _Two independent truncation layers_: agent chunk selection, most large page content never fetched; per-chunk display ceiling ~2K chars visible per chunk, remainder hidden with a byte-count notice |
| **Redirect Chains** | _Consistent_: tested 5-level redirect chain; returned inline without triggering chunked pipeline |
| **Self-reported Completeness** | _Inconsistent_: agents with identical content report contradictory truncation assessments; disagreement tracks chunk selection depth,<br>not actual content loss |
| **Chunk Summary Population** | _URL-dependent_: well-structured pages return populated summaries providing navigational signal; CSS-heavy or SPAs may return empty summaries collapsing skimming into blind sampling |
| **SPA extraction** | _Lossy by design_: Go Colly static scraper delivers ~25–30% of raw HTML as extracted text; scripts, styles, and metadata discarded before delivery |
| **Prompt Injection Sensitivity** | _Agent-dependent_: `Claude Sonnet 4.6` triggered safety heuristics twice, refusing tool visibility reporting in one and full<br>prompt execution in another |

## Results Details

| | |
| --- | --- |
| **Agent Selector** | Hybrid Arena - 5 slots per run;<br>one single-agent retry - `EC-6` run 6 |
| **Agents Observed** | `Claude Sonnet 4.6`, `Claude Opus 4.6`, `GPT-5.3-Codex`,<br>`GPT-5.4`, `Kimi K2.5`, `SWE-1.5`, `SWE-1.6` |
| **Total Runs** | 61 |
| **Distinct URLs** | 11 |
| **Input Size Range** | ~2 KB - 256 KB |
| **Truncation Events** | 27 / 61 |
| **Average Output Size** | 37,600 chars |
| **Average Token Count** | 13,745 tokens |
| **Approval-gated Fetch** | 49 / 61 runs prompted for approval |
| **Auto-pagination** | 33 runs auto-paginated;<br>2 runs paginated when prompted |
| **Complete Retrieval Failure** | `SC-2` URL rewriting bug |
| **URL Fragment Handling** | `OP-1` `#History` fragment model-dependent, mostly absent; 1 of 5 agents reached targeted section |

## Agentic Pagination Depth

Agents consistently use `read_url_content` to fetch URLs, but depending on the state of the chunk index, they reason whether individual
calls to `view_content_chunk` is worth it. While it determines output size and truncation self-report, chunks fetched is the primary
behavioral variable in this dataset.

{% raw %}
<div id="cas-hm-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.cas-hm-wrap { overflow-x: auto; }
table.cas-hm { border-collapse: collapse; width: 100%; }
table.cas-hm th { font-size: 11px; font-weight: 500; padding: 4px 5px; text-align: center; white-space: nowrap; color: inherit; }
table.cas-hm th.cas-row-head { text-align: left; }
table.cas-hm th .cas-chunk-count { font-weight: 400; font-size: 11px; opacity: 0.6; }
table.cas-hm td { padding: 2px 3px; text-align: center; }
table.cas-hm td.cas-row-label { font-size: 12px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; }
.cas-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.cas-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.75);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.cas-overlay-inner {
  border-radius: 10px;
  padding: 24px 28px;
  max-width: 98vw;
  max-height: 92vh;
  overflow: auto;
  position: relative;
}
.cas-close {
  position: absolute; top: 12px; right: 14px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.cas-close:hover { opacity: 1; }
.cas-legend { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; font-size: 11px; align-items: center; opacity: 0.8; }
.cas-legend-swatch { width: 12px; height: 12px; border-radius: 2px; display: inline-block; flex-shrink: 0; border: 0.5px solid rgba(128,128,128,0.3); }
.cas-note { font-size: 12px; margin-top: 10px; line-height: 1.6; opacity: 0.7; }
</style>

<script>
(function() {
  var e = React.createElement;

  function detectDark() {
    var theme = document.documentElement.getAttribute('data-theme');
    if (theme === 'dark') return true;
    if (theme === 'light') return false;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  var testOrder = [
    {id:'BL-2', total:3,  l1:'BL-2', l2:'3'  },
    {id:'EC-1', total:10, l1:'EC-1', l2:'10' },
    {id:'SC-1', total:14, l1:'SC-1', l2:'14' },
    {id:'SC-4', total:33, l1:'SC-4', l2:'33' },
    {id:'EC-6', total:38, l1:'EC-6', l2:'38' },
    {id:'BL-3', total:53, l1:'BL-3', l2:'53' },
    {id:'OP-4', total:53, l1:'OP-4', l2:'53' },
    {id:'BL-1', total:54, l1:'BL-1', l2:'54' },
    {id:'SC-3', total:59, l1:'SC-3', l2:'59' },
    {id:'OP-1', total:91, l1:'OP-1', l2:'91' },
    {id:'SC-2', total:0, l1:'SC-2', l2:'null'},
  ];

  var runs = [
    {test:'BL-1',agent:'Sonnet', fetched:2,  total:54},
    {test:'BL-1',agent:'Codex',  fetched:2,  total:54},
    {test:'BL-1',agent:'Opus',   fetched:54, total:54},
    {test:'BL-1',agent:'Kimi',   fetched:6,  total:54},
    {test:'BL-1',agent:'SWE',    fetched:6,  total:54},
    {test:'BL-2',agent:'Codex',  fetched:3,  total:3 },
    {test:'BL-2',agent:'Sonnet', fetched:3,  total:3 },
    {test:'BL-2',agent:'Opus',   fetched:3,  total:3 },
    {test:'BL-2',agent:'SWE',    fetched:3,  total:3 },
    {test:'BL-2',agent:'GPT54',  fetched:3,  total:3 },
    {test:'BL-3',agent:'Codex',  fetched:2,  total:53},
    {test:'BL-3',agent:'Sonnet', fetched:0,  total:53, declined:true},
    {test:'BL-3',agent:'Opus',   fetched:53, total:53},
    {test:'BL-3',agent:'SWE',    fetched:53, total:53},
    {test:'BL-3',agent:'Kimi',   fetched:11, total:53},
    {test:'SC-1',agent:'Codex',  fetched:14, total:14},
    {test:'SC-1',agent:'Kimi',   fetched:14, total:14},
    {test:'SC-1',agent:'SWE',    fetched:14, total:14},
    {test:'SC-1',agent:'Opus',   fetched:14, total:14},
    {test:'SC-1',agent:'Sonnet', fetched:10, total:14},
    {test:'SC-2', agent:'Codex',  fetched:0, total:0, declined:true},
    {test:'SC-2', agent:'Sonnet', fetched:0, total:0, declined:true},
    {test:'SC-2', agent:'GPT54',  fetched:0, total:0, declined:true},
    {test:'SC-2', agent:'Opus',   fetched:0, total:0, declined:true},
    {test:'SC-2', agent:'SWE',    fetched:0, total:0, declined:true},
    {test:'SC-3',agent:'Codex',  fetched:2,  total:59},
    {test:'SC-3',agent:'Sonnet', fetched:2,  total:59},
    {test:'SC-3',agent:'Opus',   fetched:3,  total:59},
    {test:'SC-3',agent:'SWE',    fetched:3,  total:59},
    {test:'SC-3',agent:'Kimi',   fetched:2,  total:59},
    {test:'SC-4',agent:'Codex',  fetched:3,  total:33},
    {test:'SC-4',agent:'Sonnet', fetched:33, total:33},
    {test:'SC-4',agent:'Opus',   fetched:33, total:33},
    {test:'SC-4',agent:'SWE',    fetched:33, total:33},
    {test:'SC-4',agent:'Kimi',   fetched:3,  total:33},
    {test:'OP-4',agent:'Codex',  fetched:2,  total:53},
    {test:'OP-4',agent:'Sonnet', fetched:2,  total:53},
    {test:'OP-4',agent:'GPT54',  fetched:1,  total:53},
    {test:'OP-4',agent:'Opus',   fetched:6,  total:53},
    {test:'OP-4',agent:'Kimi',   fetched:11, total:53},
    {test:'OP-1',agent:'Codex',  fetched:2,  total:91},
    {test:'OP-1',agent:'SWE',    fetched:5,  total:91},
    {test:'OP-1',agent:'Opus',   fetched:3,  total:91},
    {test:'OP-1',agent:'GPT54',  fetched:0,  total:91, declined:true},
    {test:'OP-1',agent:'Sonnet', fetched:0,  total:91, declined:true},
    {test:'EC-1',agent:'Codex',  fetched:10, total:10},
    {test:'EC-1',agent:'Opus',   fetched:10, total:10},
    {test:'EC-1',agent:'Sonnet', fetched:10, total:10},
    {test:'EC-1',agent:'Kimi',   fetched:10, total:10},
    {test:'EC-1',agent:'SWE',    fetched:10, total:10},
    {test:'EC-6',agent:'Codex',  fetched:3,  total:38},
    {test:'EC-6',agent:'Sonnet', fetched:0,  total:38, refused:true},
    {test:'EC-6',agent:'Opus',   fetched:38, total:38},
    {test:'EC-6',agent:'SWE',    fetched:38, total:38},
    {test:'EC-6',agent:'Kimi',   fetched:8,  total:38},
    {test:'EC-6',agent:'Sonnet2',fetched:38, total:38, note:'single retry'},
  ];

  var agentOrder = ['Opus','Sonnet','Sonnet2','Codex','GPT54','Kimi','SWE'];
  var agentLabels = {
    Opus:'Claude Opus 4.6', Sonnet:'Claude Sonnet 4.6', Sonnet2:'Claude Sonnet 4.6*',
    Codex:'GPT-5.3-Codex', GPT54:'GPT-5.4', Kimi:'Kimi K2.5', SWE:'SWE-1.5-6',
  };

  function getCellColors(isDark, fetched, total, declined, refused) {
    if (refused)  return {bg:isDark?'#D4537E':'#FF8A65', fg:'#fff', label:'R'};
    if (declined) return {bg:isDark?'#3C3489':'#BA68C8', fg:'#fff', label: '0'};
    var p = Math.round((fetched / total) * 100);
    if (p === 100) return {bg:isDark?'#0F6E56':'#1D9E75', fg:'#fff', label:'100%'};
    if (p >= 50)   return {bg:isDark?'#185FA5':'#378ADD', fg:'#fff', label:p+'%'};
    if (p >= 10)   return {bg:isDark?'#cba452':'#FFB74D', fg:isDark?'#412402':'#412402', label:p+'%'};
    return               {bg:isDark?'#A32D2D':'#F06292', fg:'#fff', label:p+'%'};
  }

  function getLegendItems(isDark, notObsBg) {
    return [
      {bg:isDark?'#0F6E56':'#1D9E75', label:'100% chunk summaries viewed'},
      {bg:isDark?'#185FA5':'#378ADD', label:'50-99% - most chunk summaries viewed'},
      {bg:isDark?'#cba452':'#FFB74D', label:'10-49% - sparse chunk summary sampling'},
      {bg:isDark?'#A32D2D':'#F06292', label:'<10% - endpoint chunk summary sampling'},
      {bg:isDark?'#3C3489':'#BA68C8', label:'0: declined pagination'},
      {bg:isDark?'#D4537E':'#FF8A65', label:'R \u2014 prompt refused'},
      {bg:notObsBg,                       label:'untested'},
    ];
  }

  function Code(props) {
    return e('code', {style:{
      background: props.isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.07)',
      color: props.textColor || 'inherit',
      borderRadius: 3,
      padding: '1px 4px',
      fontSize: '11px',
      fontFamily: 'monospace'
    }}, props.children);
  }

  function HeatmapTable(props) {
    var dark = props.isDark;
    var cellW = props.large ? 64 : 46;
    var cellH = props.large ? 38 : 30;
    var agentColW = props.large ? 140 : 100;
    var fs = props.large ? 12 : 11;
    var tc = props.textColor || 'inherit';
    var notObsBg = dark ? '#363634' : '#d0cec7';

    return e('div', {className:'cas-hm-wrap'},
      e('table', {className:'cas-hm'},
        e('thead', null,
          e('tr', null,
            e('th', {className:'cas-row-head', style:{minWidth:agentColW, color:tc}}, 'Agent'),
            testOrder.map(function(t) {
              return e('th', {key:t.id, style:{color:tc}},
                t.l1, e('br'), e('span', {className:'cas-chunk-count'}, t.l2)
              );
            })
          )
        ),
        e('tbody', null,
          agentOrder.map(function(agent) {
            var ar = runs.filter(function(r) { return r.agent === agent; });
            if (!ar.length) return null;
            return e('tr', {key:agent},
              e('td', {className:'cas-row-label', style:{color:tc, verticalAlign:'middle'}}, agentLabels[agent]),
              testOrder.map(function(t) {
                var run = ar.find(function(r) { return r.test === t.id; });
                if (!run) {
                  return e('td', {key:t.id},
                    e('div', {style:{
                      borderRadius:4, fontSize:fs, fontWeight:500,
                      display:'flex', alignItems:'center', justifyContent:'center',
                      width:cellW, height:cellH, margin:'1px auto',
                      background:notObsBg
                    }})
                  );
                }
                var c = getCellColors(dark, run.fetched, run.total, run.declined, run.refused);
                var tip = run.fetched+'/'+run.total+(run.note?' ('+run.note+')':'');
                return e('td', {key:t.id},
                  e('div', {title:tip, style:{
                    borderRadius:4, fontSize:fs, fontWeight:500,
                    display:'flex', alignItems:'center', justifyContent:'center',
                    width:cellW, height:cellH, margin:'1px auto',
                    background:c.bg, color:c.fg
                  }}, c.label)
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
  var notObsBg = dark ? '#363634' : '#d0cec7';
  var tc = props.textColor || 'inherit';
  var items = getLegendItems(dark, notObsBg);
  return e('table', {style:{borderCollapse:'collapse', marginTop:0, fontSize:11, width:'auto'}},
    e('tbody', null,
      items.map(function(item, i) {
        return e('tr', {key:i},
          e('td', {style:{paddingRight:8, paddingBottom:4, verticalAlign:'middle'}},
            e('span', {style:{
              width:12, height:12, borderRadius:2, display:'inline-block',
              background:item.bg, border:'0.5px solid rgba(128,128,128,0.3)'
            }})
          ),
          e('td', {style:{paddingBottom:4, color:tc, opacity:0.8, whiteSpace:'nowrap'}}, item.label)
        );
      })
    )
  );
}

  function Note(props) {
  var tc = props.textColor || 'inherit';
  var dark = props.isDark;
  var C = function(p) { return e(Code, {textColor:tc, isDark:dark}, p.children); };
  return e('p', {className:'cas-note', style:{color:tc, marginTop:0, paddingTop:0}},
    e('i', null,
      'Columns: total chunks, ascending. ',
      e(C, null, 'EC-3'), ' excluded as inline JSON response below chunking threshold, but successful retrieval. ',
      e(C, null, 'SC-2'), ' URL rewriting failure, no content retrieval. ',
      e(C, null, '0'),': agent observed, but made no ', e(C, null, 'view_content_chunk'), ' calls. ',
      e(C, null, 'Sonnet 4.6*'), ': single retry after prompt refusal. Hover over cells for fetched/total counts.'
    )
  );
}

  function App() {
    var state = React.useState(false);
    var isOpen = state[0];
    var setOpen = state[1];

    var isDark = detectDark();
    var lbBg   = isDark ? '#1e1e1c' : '#ffffff';
    var lbText = isDark ? '#e8e6df' : '#1a1a18';

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
        e(HeatmapTable, {large:false, isDark:isDark}),
        e('p', {className:'cas-hint'}, '\u2197 click to expand')
      ),
      e('div', {style:{display:'flex', gap:32, alignItems:'center', flexWrap:'wrap', marginTop:8, width:'100%', justifyContent:'center'}},
        e('div', {style:{flexShrink:0}},
          e(Legend, {isDark:isDark})
        ),
        e('div', {style:{flex:1, maxWidth:380}},
          e(Note, {isDark:isDark})
        )
      ),
      isOpen && e('div', {
        className:'cas-overlay',
        onClick:function(ev){ if (ev.target === ev.currentTarget) setOpen(false); }
      },
        e('div', {
          className:'cas-overlay-inner',
          style:{background:lbBg, color:lbText, width: '98vw'}
        },
          e('button', {
            className:'cas-close',
            style:{color:lbText},
            onClick:function(){ setOpen(false); },
            'aria-label':'Close'
          }, '\u00d7'),
          e(HeatmapTable, {large:true, isDark:isDark, textColor:lbText}),
          e('div', {style:{display:'flex', gap:32, alignItems:'center', flexWrap:'nowrap', marginTop:8, width:'100%', justifyContent:'center'}},
            e('div', {style:{flexShrink:0}},
              e(Legend, {isDark:isDark, textColor:lbText})
            ),
            e('div', {style:{flex:1, maxWidth:380}},
              e(Note, {isDark:isDark, textColor:lbText})
            )
          ),
        )
      )
    );
  }

  var root = ReactDOM.createRoot(document.getElementById('cas-hm-root'));
  root.render(e(App));
})();
</script>
{% endraw %}

The tractability threshold is visible left-to-right: agents tend toward full retrieval on chunk counts ≤14 and toward sparse sampling on
larger ones ≥50, with 33–38 chunks as the transition zone where model families diverge. `Opus 4.6` and `SWE-1.6` show the most consistent
full-retrieval behavior while `GPT-5.3-Codex` and `Kimi K2.5` default to sparse sampling regardless of chunk count.

---

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`read_url_content` returns<br>chunk index** | All tests | Requires `view_content_chunk` × N; no single-call full-page retrieval path | **Output chars reflect chunks fetched, not retrieval ceiling; variance is behavioral, not architectural** |
| 2 | **No fixed character or token ceiling detected** | `BL-1`<br>`BL-3`<br>`EC-6` | `BL-1` `Opus` full retrieval estimated ~55,000–65,000 tokens; `EC-6` `SWE` measured 58,947 chars with no cutoff; `BL-3` `Opus` retrieved ~106,000 visible chars from 53 chunks | **If ceiling exists,<br> no test hit it; constraint is chunks fetched, not a tool-imposed byte limit** |
| 3 | **Per-chunk display truncation<br>is a second independent layer** | `BL-1`<br>`SC-4`<br>`EC-6` | `view_content_chunk` hides middle portion of large chunks with explicit byte-count notice; `SC-4` showed 3,736 bytes<br>hidden across 4 positions;<br>`BL-1` `Opus` found 132 KB<br>hidden across 51 of 54 chunks | **Full chunk retrieval doesn't guarantee full content delivery; internal truncation invisible** |
| 4 | **Truncation self-report tracks chunks fetched, not content loss** | `SC-4`<br>`SC-3`<br>`BL-3` | `SC-4` - agents sampling 3 chunks reported no truncation; agents retrieving all 33 reported byte-level notices at 4 positions; same pattern repeated across tests | **Self-reported truncation accurate for chunks seen, not accurate for doc; agents conflate retrieval completeness with content fidelity** |
| 5 | **Chunk summary population determines retrieval strategy quality** | `SC-1`<br>`SC-3`<br>`BL-3`<br>`OP-4` | `SC-1` populated summaries enabled selective exclusion; `BL-3` and `OP-4` empty summaries collapsed skimming to blind sampling; `SC-3` populated summaries present, but unused above ~50 chunks | **_"Human skim"_ behavior requires populated summaries to function; empty summaries are URL-dependent, not universal failure; populated summaries provide signal but don't guarantee targeted retrieval** |
| 6 | **SPA sources produce an extraction ratio gap, not a truncation event** | `EC-1` | Go Colly static scraper delivers ~25–30% of raw HTML; gap is architectural and consistent, not stochastic; `H1` untestable on SPAs | **3 untestable conditions confirmed: `BL-1` chunks fetched, `EC-1` extraction ratio, `EC-3`<br>payload size** |
| 7 | **Routing bypasses chunked pipeline for small payloads** | `EC-3` | `read_url_content` returned 5-redirect-chain terminal response inline ~306–424 chars; `view_content_chunk`<br>not called in any runs | **Chunked architecture has at least two modes; small payloads return inline without triggering the two-fetch process** |
| 8 | **`search_web` called once across 61 runs** | All tests | `SWE-1.6` invoked `search_web` once in `SC-2` after two failures; zero calls elsewhere, including runs where agents expressed explicit uncertainty | **URL provision alone doesn't activate `search_web`; single call was a fallback, not retrieval enrichment; `H4` mostly untested** |
| 9 | **Prompt injection sensitivity produced two refusals** | `OP-4`<br>`EC-6` | `OP-4` `Sonnet` declined tool reporting; `EC-6` `Sonnet` refused full prompt execution, flagging tool names, URL, and framing as injection signals; single retry success | **Safety heuristic sensitivity is prompt-dependent and not consistently reproducible** |
| 10 | **URL rewriting is a tool-layer bug, not agent behavior** | `SC-2` | `read_url_content` silently rewrites `docs.anthropic.com/en/api/messages` to `llms-full.txt`, redirecting to a dead endpoint; all runs failed | **`SC-2` hypotheses untestable until<br>rewriting resolved** |
| 11 | **URL fragment targeting is behavioral, not architectural** | `OP-1` | 4 of 5 runs treated the fragment URL as a generic retrieval target; `SWE-1.5` only agent to confirm `#History` chunk position; chunk index supported targeting, agents largely didn't use it | **Fragment targeting is achievable via chunk index, but absent by default; miss rate is behavioral, not tool limitation** |
| 12 | **Selective semantic processing applies to content, not shell** | `EC-1`<br>`BL-3`<br>`OP-4` | Tool strips HTML, converts prose to Markdown, summarizes chunk index entries, but passes nav chrome, responsive breakpoint duplicates, and pre/post-render DOM states through verbatim without de-duplication | **Selective content transformation; page structure extracted raw with CSS noise, nav duplication, SPA extraction artifacts across multiple tests** |

## Perception Gap

> _Output chars aren't an appropriate truncation ceiling metric; they reflect how much the tools discard before delivery through
> chunk count, content transformation. Neither is observable from the interpreted track alone._

| **Test** | **Expected** | **Received** | **Delivery Ratio** | **Agent Characterization** |
| --- | --- | --- | --- | --- |
| **`EC-6`<br>Raw<br>Markdown** | ~61 KB | 58,947 chars<br>`SWE` full<br>retrieval | ~97% | _"No truncation, structurally complete - tool transforms content before delivery, exact char count unverifiable"_ |
| **`SC-4` Markdown Guide** | ~30 KB | ~24,100–29,000 chars; full retrieval runs | ~78–94% | _"Substantially complete but not byte-for-byte faithful - code examples flattened, tables stripped"_ |
| **`EC-1`<br>SPA** | ~100 KB | ~22,500–53,000 chars extracted | ~22–53% | _"Extraction ratio, not truncation - tool delivers ~25–30% of raw HTML by design"_ |
| **`SC-3` Wikipedia** | ~102 KB | `Kimi` ~6,777 chars received to `Sonnet` ~150,000 chars extrapolated | varies<br>by<br>method | _"No truncation, index complete, vs yes truncation, content withheld"_ |
| **`BL-3` Tutorial** | ~256 KB | `Opus` ~106,000 chars visible<br>53 chunks | ~41% visible; ~56% layer 2 loss | _"Double-truncated - chunked then per-chunk display-capped; tutorial content inaccessible"_ |
| **`EC-3` Redirect<br>JSON** | ~2 KB | 306–424 chars | ~15–21% of expected | _"Complete - JSON payload is the full response; size gap reflects per-request header variance"_ |
