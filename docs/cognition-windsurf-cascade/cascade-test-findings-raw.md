---
layout: default
title: "Key Findings for Cascade's Web Search Behavior, Raw"
permalink: /docs/cognition-windsurf-cascade/cascade-test-findings-raw
parent: Cognition Windsurf Cascade
---

## Key Findings for Cascade's Web Search Behavior, Raw

---

## [Raw Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/windsurf-cascade-web-search/web_search_testing_framework.py)

1. Run `python web_search_testing_framework.py --test {test ID} --track raw`
2. Review the terminal output
3. Copy the provided prompt instructing the agent to retrieve the URL and return
   content exactly as received, saving output to `results/raw/raw_output_{test_ID}.txt`
4. Open a new Cascade session in Windsurf and paste the prompt into the chat window
5. Approve web fetch calls and terminal commands; cancel if any run loops hang
6. Run the verification script against the saved file; capture path compliance,
   file size, checksum, and truncation indicators
7. Log structured metadata as described in `framework-reference.md`
8. Ensure log results are saved to `/results/cascade-raw/results.csv`

> _Raw output file presence, path compliance, and content fidelity are tracked. Claiming a save without writing a file, referencing another
> agent's file, or generating structurally accurate but semantically unmeaningful content all describe distinct failure modes;
> analysis in [Friction: Raw](friction-note-raw.md)._

---

## Platform Limit Summary

| **Limit** | **Observed** |
|---|---|
| **Hard Character Limit** | _None detected_: output sizes ranged from 275-56,256,891 chars; ceilings agent-imposed or write-stage failures, not explicitly platform-imposed byte limits |
| **Hard Token Limit** | _None detected_: token counts ranged from 52-12,782,469; `BL-3`'s `SWE-1.6` appears to hit a write ceiling |
| **Output Consistency** | _Agent- and strategy-dependent_: pipeline-accepting runs cluster within a narrow size band per URL; `curl`-bypass runs produce larger files for same URLs that pass path and size verification, but containing no semantic meaning |
| **Content Selection Behavior** | _Two-stage chunked retrieval_: mirrors interpreted, explicit tracks; all agents used `read_url_content` → `view_content_chunk`; `SC-2`'s `SWE-1.6` called `search_web` once as a fallback in repsonse to redirect, found URL but didn't return content |
| **Truncation Pattern** | _Write-stage asymmetry_: `view_content_chunk` retrieval reliable across agents, chunk counts; dominant failure modes were write-related: heredoc errors, token ceiling, false completions, file reuse |
| **Redirect Chains** | _Size-influenced, behavior dependent_: `EC-3` 5-hop redirect chain followed cleanly by all agents; `SC-2` single cross-domain redirect caused `read_url_content` halt, named destination in error message |
| **Auto-pagination** | _Consistent up to ~60 chunks; abandoned at 1,026_: agents auto-paginated chunk counts ≤ 60; no agent paginated beyond position 0 at `SC-2`'s 1,026-chunk corpus, confirming size threshold |
| **False Completion Claims** | _Distinct failure mode_: `BL-1`, `OP-1` - `SWE-1.6`; `BL-3`, `SC-3` - `GPT-5.3-Codex`; `EC-6` - `Gemini 3.1`; agents reported saved files with metrics that were never written |
| **Cross-Agent File Reuse** | _Confirmed via `EC-6` MD5 checksum_: `BL-2`, `BL-3`, `OP-1`, `EC-6` - once a plausible file exists in the workspace, agents may satisfy persistence requirement by reference rather than by writing |
| **`curl` as Fidelity Escape Hatch** | _Consistent pattern_: agents that correctly diagnose Cascade pipeline returns Markdown-ish, not raw HTML switch to `curl`; output files architecturally correct, but contain HTML shells without prose |

## Results Details

| | |
|---|---|
| **Agent Selector** | Hybrid Arena — 5 slots per run; some tests ran two arena rounds |
| **Agents Observed** | `Claude Opus 4.7`, `Claude Sonnet 4.6 Thinking`, `GLM-5.1`, `Gemini 3.1 Pro`, `GPT-5.3-Codex`, `GPT-5.4`, `GPT-5.5`, `Kimi K2.6`, `Minimax M2.5`, `SWE-1.6`, `SWE-1.6 Fast`, `xAI Grok-3` |
| **Total Runs** | 66 |
| **Distinct URLs** | 10 |
| **Input Size Range** | ~2 KB – 256 KB (estimated rendered); actual pipeline output: 275B – 56MB depending on retrieval method |
| **Truncation Events** | 5 / 66 |
| **Average Output Size** | 1,129,230 chars |
| **Output Size Range** | 275 – 56,256,891 chars |
| **Average Token Count** | 266,105 tokens |
| **Token Count Range** | 52 – 12,782,469 tokens |
| **Approval-gated Fetch** | 56 / 66 runs prompted for approval |
| **Auto-pagination** | 48 run(s) auto, 0 run(s) prompted |
| **Complete Retrieval Failure** | `SC-2` redirect halt; `OP-4` all 5 agents retrieved chunks but none produced clean output |
| **URL Fragment Handling** | `OP-1` — 1 of 10 agents (Grok-3) intentionally targeted `#History`; 1 hit it incidentally; 8 defaulted to full-document retrieval |

---

## Agent Pagination Depth

As observed in the interpreted and explicit tracks, agents consistently use `read_url_content` to fetch URLs, but whether they proceed to exhaust `view_content_chunk` varies substantially by agent, chunk count, and — on the raw track — whether a write task is present. Chunks fetched remains the primary behavioral variable in this dataset.
 
{% raw %}
<div id="raw-hm-root"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
 
<style>
.raw-hm-wrap { overflow-x: auto; }
table.raw-hm { border-collapse: collapse; width: 100%; }
table.raw-hm th { font-size: 11px; font-weight: 500; padding: 4px 5px; text-align: center; white-space: nowrap; color: inherit; }
table.raw-hm th.raw-row-head { text-align: left; }
table.raw-hm th .raw-chunk-count { font-weight: 400; font-size: 11px; opacity: 0.6; }
table.raw-hm td { padding: 2px 3px; text-align: center; }
table.raw-hm td.raw-row-label { font-size: 12px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; }
.raw-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.raw-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.75);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.raw-overlay-inner {
  border-radius: 10px;
  padding: 24px 28px;
  max-width: 98vw;
  max-height: 92vh;
  overflow: auto;
  position: relative;
}
.raw-close {
  position: absolute; top: 12px; right: 14px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.raw-close:hover { opacity: 1; }
.raw-note { font-size: 12px; margin-top: 10px; line-height: 1.6; opacity: 0.7; }
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
    {id:'BL-2', total:3,    l1:'BL-2', l2:'3'    },
    {id:'EC-1', total:10,   l1:'EC-1', l2:'10'   },
    {id:'SC-1', total:14,   l1:'SC-1', l2:'14'   },
    {id:'SC-4', total:33,   l1:'SC-4', l2:'33'   },
    {id:'EC-6', total:41,   l1:'EC-6', l2:'41'   },
    {id:'BL-3', total:53,   l1:'BL-3', l2:'53'   },
    {id:'OP-4', total:53,   l1:'OP-4', l2:'53'   },
    {id:'BL-1', total:54,   l1:'BL-1', l2:'54'   },
    {id:'SC-3', total:60,   l1:'SC-3', l2:'60'   },
    {id:'OP-1', total:92,   l1:'OP-1', l2:'92'   },
    {id:'SC-2', total:1026, l1:'SC-2', l2:'1,026'},
  ];
  // fetched values from CSV notes + per-test summaries
  var runs = [
    // BL-2 (3 chunks)
    {test:'BL-2', agent:'GLM',     fetched:3,   total:3   },
    {test:'BL-2', agent:'Gemini',  fetched:3,   total:3   },
    {test:'BL-2', agent:'SWE',     fetched:3,   total:3   },
    {test:'BL-2', agent:'Grok',    fetched:2,   total:3   },
    {test:'BL-2', agent:'Kimi',    fetched:3,   total:3   },
    // EC-1 (10 chunks)
    {test:'EC-1', agent:'SWE',     fetched:10,  total:10  },
    {test:'EC-1', agent:'Opus',    fetched:10,  total:10  },
    {test:'EC-1', agent:'Codex',   fetched:0,   total:10  },
    {test:'EC-1', agent:'Gemini',  fetched:10,  total:10  },
    {test:'EC-1', agent:'GLM',     fetched:10,  total:10  },
    // SC-1 (14 chunks)
    {test:'SC-1', agent:'Sonnet',  fetched:14,  total:14  },
    {test:'SC-1', agent:'Kimi',    fetched:14,  total:14  },
    {test:'SC-1', agent:'GPT55',   fetched:14,  total:14  },
    {test:'SC-1', agent:'Minimax', fetched:14,  total:14  },
    {test:'SC-1', agent:'Grok',    fetched:9,   total:14  },
    // SC-4 (33 chunks)
    {test:'SC-4', agent:'Kimi',    fetched:33,  total:33  },
    {test:'SC-4', agent:'Sonnet',  fetched:33,  total:33  },
    {test:'SC-4', agent:'Grok',    fetched:33,  total:33  },
    {test:'SC-4', agent:'Minimax', fetched:33,  total:33  },
    {test:'SC-4', agent:'GPT55',   fetched:33,  total:33  },
    // EC-6 (41 chunks)
    {test:'EC-6', agent:'Opus',    fetched:41,  total:41  },
    {test:'EC-6', agent:'GLM',     fetched:41,  total:41  },
    {test:'EC-6', agent:'Minimax', fetched:41,  total:41  },
    {test:'EC-6', agent:'Gemini',  fetched:12,  total:41  },
    {test:'EC-6', agent:'Codex',   fetched:41,  total:41  },
    // BL-3 (53 chunks)
    {test:'BL-3', agent:'Opus',    fetched:53,  total:53  },
    {test:'BL-3', agent:'SWE',     fetched:53,  total:53  },
    {test:'BL-3', agent:'Codex',   fetched:1,   total:53  },
    {test:'BL-3', agent:'GLM',     fetched:53,  total:53  },
    {test:'BL-3', agent:'Gemini',  fetched:53,  total:53  },
    // OP-4 (53 chunks)
    {test:'OP-4', agent:'Sonnet',  fetched:53,  total:53  },
    {test:'OP-4', agent:'Kimi',    fetched:53,  total:53  },
    {test:'OP-4', agent:'GPT54',   fetched:12,  total:53  },
    {test:'OP-4', agent:'Minimax', fetched:38,  total:53  },
    {test:'OP-4', agent:'Grok',    fetched:53,  total:53  },
    // BL-1 (54 chunks)
    {test:'BL-1', agent:'GLM',     fetched:54,  total:54  },
    {test:'BL-1', agent:'Gemini',  fetched:54,  total:54  },
    {test:'BL-1', agent:'GPT54',   fetched:18,  total:54  },
    {test:'BL-1', agent:'SWE',     fetched:54,  total:54  },
    {test:'BL-1', agent:'Opus',    fetched:54,  total:54  },
    // SC-3 (60 chunks)
    {test:'SC-3', agent:'SWE',     fetched:60,  total:60  },
    {test:'SC-3', agent:'Opus',    fetched:60,  total:60  },
    {test:'SC-3', agent:'Codex',   fetched:0,   total:60  },
    {test:'SC-3', agent:'GLM',     fetched:60,  total:60  },
    {test:'SC-3', agent:'Gemini',  fetched:60,  total:60  },
    // OP-1 (92 chunks) — 10 runs across 2 rounds
    {test:'OP-1', agent:'GLM',     fetched:92,  total:92  },
    {test:'OP-1', agent:'Gemini',  fetched:0,   total:92  },
    {test:'OP-1', agent:'SWE',     fetched:92,  total:92  },
    {test:'OP-1', agent:'Codex',   fetched:10,  total:92  },
    {test:'OP-1', agent:'Opus',    fetched:92,  total:92  },
    {test:'OP-1', agent:'Sonnet',  fetched:92,  total:92  },
    {test:'OP-1', agent:'Kimi',    fetched:0,   total:92  },
    {test:'OP-1', agent:'GPT54',   fetched:78,  total:92  },
    {test:'OP-1', agent:'Minimax', fetched:5,   total:92  },
    {test:'OP-1', agent:'Grok',    fetched:1,   total:92  },
    // SC-2 (1026 chunks)
    {test:'SC-2', agent:'GLM',     fetched:20,  total:1026},
    {test:'SC-2', agent:'Gemini',  fetched:0,   total:1026},
    {test:'SC-2', agent:'Kimi',    fetched:1,   total:1026},
    {test:'SC-2', agent:'Sonnet',  fetched:1,   total:1026},
    {test:'SC-2', agent:'SWE',     fetched:0,   total:1026},
  ];
  var agentOrder = ['Opus','Sonnet','Gemini','GLM','Codex','GPT54','GPT55','Kimi','Minimax','Grok','SWE'];
  var agentLabels = {
    Opus:    'Claude Opus 4.7',
    Sonnet:  'Claude Sonnet 4.6',
    Gemini:  'Gemini 3.1',
    GLM:     'GLM-5.1',
    Codex:   'GPT-5.3-Codex',
    GPT54:   'GPT-5.4',
    GPT55:   'GPT-5.5',
    Kimi:    'Kimi K2.6',
    Minimax: 'Minimax M2.5',
    Grok:    'xAI Grok-3',
    SWE:     'SWE-1.6',
  };
  function getCellColors(isDark, fetched, total) {
    if (fetched === 0) return {bg:isDark?'#3C3489':'#BA68C8', fg:'#fff', label:'0'};
    var p = Math.round((fetched / total) * 100);
    if (p === 100) return {bg:isDark?'#0F6E56':'#1D9E75', fg:'#fff', label:'100%'};
    if (p >= 50)   return {bg:isDark?'#185FA5':'#378ADD', fg:'#fff', label:p+'%'};
    if (p >= 10)   return {bg:isDark?'#cba452':'#FFB74D', fg:isDark?'#412402':'#412402', label:p+'%'};
    return               {bg:isDark?'#A32D2D':'#F06292', fg:'#fff', label:'<1%'};
  }
  function getLegendItems(isDark, notObsBg) {
    return [
      {bg:isDark?'#0F6E56':'#1D9E75', label:'100% chunk summaries viewed'},
      {bg:isDark?'#185FA5':'#378ADD', label:'50–99% — most chunk summaries viewed'},
      {bg:isDark?'#cba452':'#FFB74D', label:'10–49% — sparse chunk summary sampling'},
      {bg:isDark?'#A32D2D':'#F06292', label:'<10% — minimal and/or endpoint summary sampling'},
      {bg:isDark?'#3C3489':'#BA68C8', label:'0 — declined pagination'},
      {bg:notObsBg,                   label:'untested'},
    ];
  }
  function Code(props) {
    return e('code', {style:{
      background: props.isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.07)',
      color: props.textColor || 'inherit',
      borderRadius: 3, padding: '1px 4px', fontSize: '11px', fontFamily: 'monospace'
    }}, props.children);
  }
  function HeatmapTable(props) {
    var dark = props.isDark;
    var cellW = props.large ? 58 : 44;
    var cellH = props.large ? 36 : 28;
    var agentColW = props.large ? 160 : 120;
    var fs = props.large ? 12 : 11;
    var tc = props.textColor || 'inherit';
    var notObsBg = dark ? '#363634' : '#d0cec7';
    return e('div', {className:'raw-hm-wrap'},
      e('table', {className:'raw-hm'},
        e('thead', null,
          e('tr', null,
            e('th', {className:'raw-row-head', style:{minWidth:agentColW, color:tc}}, 'Agent'),
            testOrder.map(function(t) {
              return e('th', {key:t.id, style:{color:tc}},
                t.l1, e('br'), e('span', {className:'raw-chunk-count'}, t.l2)
              );
            })
          )
        ),
        e('tbody', null,
          agentOrder.map(function(agent) {
            var ar = runs.filter(function(r) { return r.agent === agent; });
            if (!ar.length) return null;
            return e('tr', {key:agent},
              e('td', {className:'raw-row-label', style:{color:tc, verticalAlign:'middle'}}, agentLabels[agent]),
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
                var c = getCellColors(dark, run.fetched, run.total);
                return e('td', {key:t.id},
                  e('div', {
                    title: run.fetched+'/'+run.total,
                    style:{
                      borderRadius:4, fontSize:fs, fontWeight:500,
                      display:'flex', alignItems:'center', justifyContent:'center',
                      width:cellW, height:cellH, margin:'1px auto',
                      background:c.bg, color:c.fg
                    }
                  }, c.label)
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
    return e('p', {className:'raw-note', style:{color:tc, marginTop:0, paddingTop:0}},
      e('i', null,
        'Columns: total chunks, ascending. ',
        e(C, null, 'EC-3'), ' excluded as inline JSON response below chunking threshold, but successful retrieval. ',
        e(C, null, 'SC-2'), ' redirect delivered full docs set, not target page; ',
        e(C, null, 'SWE'), ' retry declined pagination. ',
        e(C, null, 'OP-1'), ' ran 2 arena rounds. ',
        e(C, null, '0'), ': agent observed but made no ', e(C, null, 'view_content_chunk'), ' calls. Hover over cells for fetched/total counts.'
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
        e('p', {className:'raw-hint'}, '\u2197 click to expand')
      ),
      e('div', {style:{display:'flex', gap:32, alignItems:'center', flexWrap:'wrap', marginTop:8, width:'100%', justifyContent:'center'}},
        e('div', {style:{flexShrink:0}},
          e(Legend, {isDark:isDark})
        ),
        e('div', {style:{flex:1, maxWidth:420}},
          e(Note, {isDark:isDark})
        )
      ),
      isOpen && e('div', {
        className:'raw-overlay',
        onClick:function(ev){ if (ev.target === ev.currentTarget) setOpen(false); }
      },
        e('div', {
          className:'raw-overlay-inner',
          style:{background:lbBg, color:lbText, width:'98vw'}
        },
          e('button', {
            className:'raw-close',
            style:{color:lbText},
            onClick:function(){ setOpen(false); },
            'aria-label':'Close'
          }, '\u00d7'),
          e(HeatmapTable, {large:true, isDark:isDark, textColor:lbText}),
          e('div', {style:{display:'flex', gap:32, alignItems:'center', flexWrap:'nowrap', marginTop:8, width:'100%', justifyContent:'center'}},
            e('div', {style:{flexShrink:0}},
              e(Legend, {isDark:isDark, textColor:lbText})
            ),
            e('div', {style:{flex:1, maxWidth:420}},
              e(Note, {isDark:isDark, textColor:lbText})
            )
          )
        )
      )
    );
  }
  var root = ReactDOM.createRoot(document.getElementById('raw-hm-root'));
  root.render(e(App));
})();
</script>
{% endraw %}
 
Unlike the interpreted track — where full retrieval at small chunk counts was near-universal — the raw track shows much spottier coverage even at low counts. Full pagination appears more consistently on write-task tests (EC-6, BL-1, SC-3, BL-3) where agents have a concrete reason to fetch every chunk, while tests with ambiguous scope or instruction friction (OP-1, SC-2, OP-4) produce the widest variance. The SC-2 column confirms abandonment is universal at 1,026 chunks regardless of agent family.
 
---

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
|---|---|---|---|---|
| 1 | **No fixed character or token ceiling detected at retrieval stage** | All tests | Output sizes ranged from 275B (`EC-3`) to 56MB (`SC-2 Kimi`); no run hit a tool-imposed byte ceiling during `view_content_chunk` retrieval | **Where ceilings appeared, they were self-imposed (deliberate elision), write-stage failures (output token limit), or environment degradation (VS Code). The retrieval pipeline has no confirmed upper bound.** |
| 2 | **Output token ceiling confirmed as a write-stage failure mechanism** | `BL-3` | `SWE-1.6` hit the model's output token limit explicitly mid-write, visible in the thought panel in real time; the first direct observation of this ceiling across any Cascade track | **The ceiling is real but write-stage, not retrieval-stage. Prior tracks inferred it; BL-3 observed it directly.** |
| 3 | **Read-write asymmetry is the dominant structural finding** | `SC-3`, `SC-4`, `BL-3`, `OP-4` | All or most agents successfully retrieved all chunks in every test; write success was substantially lower across the same tests | **Retrieval via `view_content_chunk` is reliable; the obstacle is reassembling and persisting ~200KB+ of distributed chunk output through shell heredocs or Python scripts at scale.** |
| 4 | **Auto-pagination is confirmed but does not predict output success** | All tests | 48 of 66 runs auto-paginated without explicit prompting; 3 of 4 auto-paginating runs in BL-1 still failed to produce a valid output file | **H5 yes across the dataset. The behavior is robust; it does not guarantee file persistence or content fidelity.** |
| 5 | **Auto-pagination has a behavioral threshold around 1,026 chunks** | `SC-2` vs `BL-2`/`EC-3` | Agents fully paginated at ≤60 chunks in every test; no agent paginated beyond position 0 at SC-2's 1,026-chunk corpus | **A behavioral threshold exists between small and large document sets. Its exact boundary is unconfirmed but falls between 60 and 1,026 chunks.** |
| 6 | **`curl` as a fidelity escape hatch produces semantically empty output** | `BL-1`, `BL-3`, `SC-2`, `SC-3`, `EC-1`, `EC-6` | Agents that correctly diagnose the pipeline as returning processed Markdown switch to `curl`; resulting files contain raw HTML or JS skeletons — architecturally correct but without semantic page content | **Pipeline abandonment is the dominant response to fidelity instinct. Agents that accept the pipeline output succeed; agents that treat it as a shortfall to correct produce files that pass verification while missing target content.** |
| 7 | **Cross-agent file reuse is confirmed at checksum level** | `EC-6`, `BL-2`, `BL-3`, `OP-1` | `Gemini 3.1` and `GLM-5.1` produced EC-6 output files with an identical MD5 checksum; GLM ran earlier and wrote first; Gemini's thought panel narrated retrieval while making no corresponding tool calls | **Path compliance and content fidelity are independent variables. File presence at the correct path does not confirm independent retrieval. Per-agent checksum comparison within the same arena run is required to detect reuse.** |
| 8 | **False completion claims are a distinct failure mode from task drift** | `BL-1`, `BL-3`, `SC-3`, `OP-1`, `EC-6` | `SWE-1.6`, `GPT-5.3-Codex`, and `Gemini 3.1` each reported saved files — with metrics, checksums, and file paths — for content that was never written | **Confident incorrect assertions with no visible uncertainty signal are structurally different from spirals and early stops. All three failure modes produce the same outcome: no valid output file.** |
| 9 | **Redirect halt behavior is confirmed as server-side, not tool-layer rewriting** | `SC-2` | Three agents successfully called `read_url_content` a second time against the redirect destination surfaced in the error payload and received valid chunked responses; this is inconsistent with silent pre-network URL substitution | **`read_url_content` makes the network call, receives a redirect, and halts rather than following automatically. The destination is actionable via a follow-up call. Confirmed as redirect halt, not URL rewriting.** |
| 10 | **Chunking pipeline does not engage below a size threshold** | `EC-3` | 5-hop redirect chain returned 366B JSON inline via `read_url_content` alone; `view_content_chunk` not called in any run | **Chunked delivery has at least two modes; small payloads return inline without triggering the two-fetch pipeline. Lower bound confirmed: 366 bytes. Upper bound unconfirmed but between 366B and ~30KB.** |
| 11 | **URL fragment targeting is behavioral, not architectural** | `OP-1` | 8 of 10 agents retrieved all 92 chunks rather than targeting `#History` at chunk position 17; the chunk index exposes the section header; Grok-3 is the only agent to have used it for navigation | **Fragment-targeting is achievable via the chunk index, absent by default. The write-fidelity instruction may actively suppress targeting: agents attending to output completeness default to full-document collection.** |
| 12 | **Prompt size estimates act as a confound for fidelity-sensitive agents** | `BL-1`, `OP-4` | The ~85KB size expectation in BL-1's prompt is architecturally unreachable: Cascade returns ~8–32KB of filtered Markdown; `curl` returns ~508KB of raw HTML. Agents with strong output-fidelity monitoring spiraled or truncated trying to reach the target | **Size expectations in prompts should be omitted or post-hoc only. No available tool produces the estimated size, making the estimate an irresolvable constraint rather than a verification guide.** |
| 13 | **"Exactly as received" is underspecified and resolved silently** | `SC-3`, `SC-4`, `BL-1`, `OP-4` | Agents interpreted the instruction as Cascade's chunk output with metadata wrappers, raw HTTP response via `curl`, or semantic Markdown — without flagging the ambiguity or asking for clarification in most runs | **Instruction underspecification is resolved silently across agent families. Only `Claude Opus 4.7` surfaced the tradeoff to the user before committing to a write strategy, across two separate tests.** |
| 14 | **`search_web` was not invoked as a primary retrieval mechanism in any run** | All tests | Zero `search_web` calls across 66 raw track runs; `SWE-1.6`'s SC-2 call on the explicit track was a fallback after retrieval failure, not enrichment | **H4 untested across the entire raw track. URL provision alone does not activate `search_web`.** |

---

## Perception Gap

| **Test** | **Expected** | **Received (pipeline)** | **Delivery Ratio** | **Agent Characterization** |
|---|---|---|---|---|
| **`EC-6` Raw Markdown** | ~94 KB | ~95.5–96.4KB (4 agents, independent writes) | ~100% | _"Complete — chunk assembly variation within ±858 chars; elision markers are source false positives"_ |
| **`SC-4` Markdown Guide** | ~30 KB | 30.44KB (`Sonnet`), 32.33KB (`Minimax`) | ~100% | _"Complete — breadcrumb heading injection at chunk boundaries inflates Minimax output; 6 elision markers present but may be tool-layer assembly artifacts"_ |
| **`SC-1` Gemini API Docs** | ~14 chunks | 38–44KB chunk cluster; 10.25KB via direct fetch | ~97% (chunk); ~60% (direct) | _"Chunk cluster structurally identical across agents; direct fetch cleaner but loses code blocks and navigation structure"_ |
| **`BL-1` MongoDB Docs** | ~85 KB | 8KB (`Opus` elided); 32KB (`GLM` verbatim) | ~9–38% | _"Pipeline output is 8–32KB of filtered Markdown; raw HTML is 508KB; no tool produces the estimated size"_ |
| **`BL-3` Tutorial** | ~256 KB | 7.4KB (`Opus`, chunks 0–6 only); 463–474KB (`GLM`/`Gemini`, raw HTML) | ~3% pipeline; ~180% via curl | _"Pipeline abandoned for `curl`; `curl` output is Gatsby/React skeleton with no tutorial body content"_ |
| **`SC-2` Anthropic Docs** | ~1,026 chunks | 56MB (`Kimi`, full `llms-full.txt` corpus) | N/A — redirect target is the full documentation corpus | _"Scale outlier; VS Code tokenization, highlighting, and scroll disabled on open; file exists, environment degraded"_ |
| **`EC-3` Redirect JSON** | ~366 B | 366B (all 5 runs, identical content) | ~100% | _"Complete — 5-hop redirect chain followed cleanly; unique `X-Amzn-Trace-Id` per run confirms independent live requests"_ |

> _Implication: on the raw track, output size is determined by whether agents accept the pipeline or bypass it via `curl`, not by a retrieval ceiling. Pipeline-accepting runs cluster tightly by source URL regardless of agent. `curl`-bypass runs produce structurally valid files — large, correct path, clean endings — that contain no semantic page content. Neither outcome is distinguishable from a successful retrieval through path-and-size verification alone._

---

## Agent Behavior Patterns

Across 66 raw track runs, agent behavior sorted into four observable strategies. Strategy selection, not tool capability, was the primary predictor of output quality:

**Pipeline acceptance** — agents that accepted Cascade's Markdown output and wrote it verbatim produced the most consistent successful files. `SWE-1.6 Fast` (EC-1, EC-3), `Minimax M2.5` (SC-1, SC-4, EC-6), and `Claude Sonnet 4.6 Thinking` (EC-3, SC-4) represent this pattern. These runs clustered within a narrow size band per URL and passed content verification.

**Deliberate elision** — `Claude Opus 4.7` consistently read all chunks, assessed the output against practical write constraints, saved a partial file, and disclosed the decision. The behavior was documented in BL-1, BL-3, and SC-3 and is the only consistent instance across the dataset of an agent explicitly communicating a tradeoff between semantic fidelity and verbatim completeness before the user asked.

**`curl` bypass** — agents that correctly diagnosed the pipeline as returning processed Markdown switched to `curl` to retrieve "raw" content. The strategy consistently produced structurally valid files — large, correct path, clean endings — containing raw HTML or JS framework skeletons with no semantic page content. Observed across `Gemini 3.1`, `GLM-5.1`, `GPT-5.3-Codex`, and `SWE-1.6` across multiple tests.

**Silent failure** — false completion claims, cross-agent file reuse, and environment-degrading scale outliers. These runs produced metrics, checksums, and file paths for content that was either absent, identical to another agent's prior output, or unworkable as a project artifact. `Gemini 3.1` (EC-6 reuse), `GPT-5.3-Codex` (SC-3 false completion), and `Kimi K2.6` (SC-2 scale outlier) are the clearest instances.
