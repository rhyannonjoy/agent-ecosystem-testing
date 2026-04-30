---
layout: default
title: "Key Findings for Cascade's Web Search Behavior, Raw"
permalink: /docs/cognition-windsurf-cascade/cascade-test-findings-raw
parent: Cognition Windsurf Cascade
---

## Key Findings for Cascade's Web Search Behavior, Raw

---

## Topic Guide

- [Raw Test Workflow](#raw-test-workflow)
- [Platform Limit Summary](#platform-limit-summary)
- [Results Details](#results-details)
- [Agentic Pagination Depth](#agentic-pagination-depth)
- [Agentic Write Performance](#agentic-write-performance)
- [Truncation Analysis](#truncation-analysis)
- [Perception Gap](#perception-gap)

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
| **Hard Character Limit** | _None detected_: output sizes ranged from 275 to 56,256,891 chars;<br>ceilings agent-imposed and/or write-stage failures, not explicitly<br> platform-imposed byte limits |
| **Hard<br>Token<br>Limit** | _None detected_: token counts ranged from 52 to 12,782,469;<br>`BL-3`'s `SWE` error message `model's generation exceeded the maximum output token limit` first to suggest a write ceiling |
| **Write Strategy** | _Capability doesn't predict output quality, but agent reasoning_: <br>- pipeline acceptance runs cluster within narrow size band per URL <br>- deliberate elision - `Opus` only agent to ask questions mid-session<br>- `curl` bypass - files pass verification without prose<br>- silent failure - false completions, reuse, environment-degrading output |
| **Content Selection Behavior** | _Two-stage chunked retrieval_: mirrors interpreted, explicit tracks - most agents used `read_url_content` → `view_content_chunk`; `SC-2`'s `SWE` called `search_web` once as a fallback in repsonse to redirect, found URL but didn't return any content |
| **Truncation Pattern** | _Write-stage asymmetry_: `view_content_chunk` retrieval reliable across agents, chunk counts; most failure modes write-related: Python heredoc errors, token ceiling and/or under-reporting, false completions, file reuse |
| **Redirect Chains** | _Size-influenced, behavior-dependent_: all agents follow `EC-3` 5-hop redirect chain; `SC-2` single cross-domain redirect caused `read_url_content` halt, error message referenced destination |
| **Auto-pagination** | _Spotty, agent-dependent_: full retrieval common, but not guaranteed, even at low chunk counts; wide variance by model family; no agent paginated meaningfully at `SC-2`'s 1,026-chunk corpus; see [Agentic Pagination Depth](#agentic-pagination-depth) |
| **`curl` Bypass** | _Consistent failure_: agents that correctly diagnose Cascade pipeline returns Markdown-ish, not raw HTML, often switch to `curl`; output files architecturally correct, but contain shells without prose |
| **False Completion Claims** | _Distinct failure mode_: `SWE` runs of `BL-1`, `OP-1`; `GPT-5.3-Codex` runs of<br>`BL-3`, `SC-3`; `Gemini` run of `EC-6`; agents reported metrics of saved files that were never written |
| **Cross-Agent File Reuse** | _Confirmed via MD5 checksum_: `BL-2`, `BL-3`, `OP-1`, `EC-6` - once a plausible file exists in the workspace, agents may satisfy persistence requirement by reference rather than by writing |
| **Path Compliance** | _Agent-dependent_: prompt instructs saving to `raw/` which doesn't exist;<br>`BL-2`'s `GLM` created it, later agents referenced `cascade-raw/` and/or failed to save; cross-agent file visibility suggests worktree state is shared across Hybrid Arena slots, not isolated |
| **URL Fragment Targeting** | _Behavioral, not architectural_: chunk index exposes headers, fragment targets; `OP-1`'s `Grok-3` only agent to use it for navigation; 8 of 10 defaulted to full-doc retrieval; _"EXACTLY as received"_ prompt may suppress targeting, making full retrieval seem like the safer interpretation |

## Results Details

| | |
|---|---|
| **Agent Selector** | Hybrid Arena — 5 slots per run;<br>`OP-1` includes two arena rounds |
| **Agents Observed** | `Claude Opus 4.7`, `Claude Sonnet 4.6`, `Gemini 3.1`,<br>`GLM-5.1`, `GPT-5.3-Codex`, `GPT-5.4`, `GPT-5.5`,<br>`Kimi K2.6`, `Minimax M2.5`, `SWE-1.6`, `xAI Grok-3` |
| **Total Runs** | 66 |
| **Distinct URLs** | 11 |
| **Input Size Range** | estimation, rendered: ~2 KB – 256 KB<br> pipeline output, depending on retrieval method: 275B – 56 MB|
| **Truncation Events** | explicitly reported 5 / 66 <br>chunked-architecture often acknowledged as lossy by design |
| **Average Output Size** | 1,129,230 chars |
| **Output Size Range** | 275 – 56,256,891 chars |
| **Average Token Count** | 266,105 tokens |
| **Token Count Range** | 52 – 12,782,469 tokens |
| **Approval-gated Fetch** | 56 / 66 runs prompted for approval |
| **Auto-pagination** | 48 runs |
| **Failures** | - `BL-1` `Gemini` task drift, token overflow<br>- `EC-6` `Gemini` retrieval theater<br>- `OP-1` most agents don't isolate target section<br>- `OP-4` retrieval success, but no clean output<br>- `SC-2` redirect halt |
| **URL Fragment Handling** | - `OP-1`'s `Grok` only agent to intentionally target `#History`<br>- `Minimax` analyzed `#History` incidentally via sampling<br>- 8 defaulted to full-doc retrieval |

## Agentic Pagination Depth

As observed in the interpreted and explicit tracks, agents consistently use `read_url_content` to fetch URLs, but whether
they proceed to exhaust `view_content_chunk` varies substantially by agent, chunk count, and exclusively on the raw track -
how they strategize the write task. Chunks-analyzed remains a primary behavioral variable in this dataset.

Full pagination appears more consistently throughout the raw track, suggesting the write task influences reason to retrieve
each chunk. Document size and structure still have an impact, as `OP-1`, `OP-4`, and `SC-2` produce the widest variance.
`SC-2` confirms abandonment is universal at 1,026 chunks regardless of agent family.
 
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
  var agentOrder = ['Opus','Sonnet','Gemini','GLM','Codex','GPT54','GPT55','Kimi','Minimax','SWE','Grok'];
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

## Agentic Write Performance
 
While the [pagination depth map](#agentic-pagination-depth) shows claimed retrieval, what agents reported reading, the
write outcome map shows verified output: what ended up on disk, and in what form. The two maps together reveal the gap.
`EC-6`'s `Gemini` run reads as 29% pagination coverage, but doesn't map to a file; a content diff checker and MD5 checksum
match confirmed it was all retrieval theater.

Tests where pagination depth is high, but write outcomes are spotty - `BL-3`, `OP-1`,<br>`OP-4`, `SC-3`, are where the read-write
asymmetry is most visible. `EC-3` is the only test with a clean success sweep, likely because the URL content didn't require
chunking at all. While `EC-6` and `SC-4` appeared to produce accurate output, many runs included false completions and file reuse.

{% raw %}
<div id="raw-wo-root"></div>
<style>
.raw-wo-wrap { overflow-x: auto; }
table.raw-wo { border-collapse: collapse; width: 100%; }
table.raw-wo th { font-size: 11px; font-weight: 500; padding: 4px 5px; text-align: center; white-space: nowrap; color: inherit; }
table.raw-wo th.raw-wo-row-head { text-align: left; }
table.raw-wo th .raw-wo-chunk-count { font-weight: 400; font-size: 11px; opacity: 0.6; }
table.raw-wo td { padding: 2px 3px; text-align: center; }
table.raw-wo td.raw-wo-row-label { font-size: 12px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; }
.raw-wo-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.raw-wo-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.75);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.raw-wo-overlay-inner {
  border-radius: 10px;
  padding: 24px 28px;
  max-width: 98vw;
  max-height: 92vh;
  overflow: auto;
  position: relative;
}
.raw-wo-close {
  position: absolute; top: 12px; right: 14px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.raw-wo-close:hover { opacity: 1; }
.raw-wo-note { font-size: 12px; margin-top: 10px; line-height: 1.6; opacity: 0.7; }
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
  // S = success, P = partial success, C = curl bypass, F = failure, no file
  var testOrder = [
    {id:'EC-3', l1:'EC-3', l2:'null' },
    {id:'BL-2', l1:'BL-2', l2:'3'    },
    {id:'EC-1', l1:'EC-1', l2:'10'   },
    {id:'SC-1', l1:'SC-1', l2:'14'   },
    {id:'SC-4', l1:'SC-4', l2:'33'   },
    {id:'EC-6', l1:'EC-6', l2:'41'   },
    {id:'BL-3', l1:'BL-3', l2:'53'   },
    {id:'OP-4', l1:'OP-4', l2:'53'   },
    {id:'BL-1', l1:'BL-1', l2:'54'   },
    {id:'SC-3', l1:'SC-3', l2:'60'   },
    {id:'OP-1', l1:'OP-1', l2:'92'   },
    {id:'SC-2', l1:'SC-2', l2:'1,026'},
  ];
  var runs = [
    // EC-3 no chunking pipeline
    {test:'EC-3', agent:'SWE',     outcome:'S'},
    {test:'EC-3', agent:'Sonnet',  outcome:'S'},
    {test:'EC-3', agent:'Kimi',    outcome:'S'},
    {test:'EC-3', agent:'GPT55',   outcome:'S'},
    {test:'EC-3', agent:'Grok',    outcome:'S'},
    // BL-2
    {test:'BL-2', agent:'GLM',     outcome:'S'},
    {test:'BL-2', agent:'Gemini',  outcome:'F'},
    {test:'BL-2', agent:'SWE',     outcome:'F'},
    {test:'BL-2', agent:'Grok',    outcome:'P'},
    {test:'BL-2', agent:'Kimi',    outcome:'F'},
    // EC-1
    {test:'EC-1', agent:'SWE',     outcome:'S'},
    {test:'EC-1', agent:'Opus',    outcome:'S'},
    {test:'EC-1', agent:'Codex',   outcome:'C'},
    {test:'EC-1', agent:'Gemini',  outcome:'C'},
    {test:'EC-1', agent:'GLM',     outcome:'P'},
    // SC-1
    {test:'SC-1', agent:'Sonnet',  outcome:'S'},
    {test:'SC-1', agent:'Kimi',    outcome:'F'},
    {test:'SC-1', agent:'GPT55',   outcome:'F'},
    {test:'SC-1', agent:'Minimax', outcome:'S'},
    {test:'SC-1', agent:'Grok',    outcome:'S'},
    // SC-4
    {test:'SC-4', agent:'Kimi',    outcome:'F'},
    {test:'SC-4', agent:'Sonnet',  outcome:'S'},
    {test:'SC-4', agent:'Grok',    outcome:'F'},
    {test:'SC-4', agent:'Minimax', outcome:'S'},
    {test:'SC-4', agent:'GPT55',   outcome:'F'},
    // EC-6
    {test:'EC-6', agent:'Opus',    outcome:'S'},
    {test:'EC-6', agent:'GLM',     outcome:'F'},
    {test:'EC-6', agent:'Minimax', outcome:'S'},
    {test:'EC-6', agent:'Gemini',  outcome:'F'},
    {test:'EC-6', agent:'Codex',   outcome:'F'},
    // BL-3
    {test:'BL-3', agent:'Opus',    outcome:'P'},
    {test:'BL-3', agent:'SWE',     outcome:'F'},
    {test:'BL-3', agent:'Codex',   outcome:'F'},
    {test:'BL-3', agent:'GLM',     outcome:'C'},
    {test:'BL-3', agent:'Gemini',  outcome:'C'},
    // OP-4
    {test:'OP-4', agent:'Sonnet',  outcome:'P'},
    {test:'OP-4', agent:'Kimi',    outcome:'F'},
    {test:'OP-4', agent:'GPT54',   outcome:'C'},
    {test:'OP-4', agent:'Minimax', outcome:'C'},
    {test:'OP-4', agent:'Grok',    outcome:'P'},
    // BL-1
    {test:'BL-1', agent:'GLM',     outcome:'S'},
    {test:'BL-1', agent:'Gemini',  outcome:'F'},
    {test:'BL-1', agent:'GPT54',   outcome:'F'},
    {test:'BL-1', agent:'SWE',     outcome:'F'},
    {test:'BL-1', agent:'Opus',    outcome:'P'},
    // SC-3
    {test:'SC-3', agent:'SWE',     outcome:'P'},
    {test:'SC-3', agent:'Opus',    outcome:'F'},
    {test:'SC-3', agent:'Codex',   outcome:'F'},
    {test:'SC-3', agent:'GLM',     outcome:'C'},
    {test:'SC-3', agent:'Gemini',  outcome:'C'},
    // OP-1 (10 runs)
    {test:'OP-1', agent:'GLM',     outcome:'P'},
    {test:'OP-1', agent:'Gemini',  outcome:'F'},
    {test:'OP-1', agent:'SWE',     outcome:'F'},
    {test:'OP-1', agent:'Codex',   outcome:'F'},
    {test:'OP-1', agent:'Opus',    outcome:'F'},
    {test:'OP-1', agent:'Sonnet',  outcome:'F'},
    {test:'OP-1', agent:'Kimi',    outcome:'F'},
    {test:'OP-1', agent:'GPT54',   outcome:'P'},
    {test:'OP-1', agent:'Minimax', outcome:'P'},
    {test:'OP-1', agent:'Grok',    outcome:'S'},
    // SC-2
    {test:'SC-2', agent:'GLM',     outcome:'P'},
    {test:'SC-2', agent:'Gemini',  outcome:'F'},
    {test:'SC-2', agent:'Kimi',    outcome:'C'},
    {test:'SC-2', agent:'Sonnet',  outcome:'P'},
    {test:'SC-2', agent:'SWE',     outcome:'F'},
    {test:'SC-2', agent:'SWE2',    outcome:'C'},
  ];
  var agentOrder = ['Opus','Sonnet','Gemini','GLM','Codex','GPT54','GPT55','Kimi','Minimax','SWE', 'SWE2', 'Grok'];
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
    SWE2:    'SWE-1.6*',
  };
  var outcomeLabels = {
  S: 'Success',
  P: 'Partial Success',
  C: 'curl bypass',
  F: 'Failure',
 };
  function getCellStyle(isDark, outcome) {
    switch(outcome) {
      case 'S': return {bg:isDark?'#0F6E56':'#1D9E75', fg:'#fff',                         label:'S'};
      case 'P': return {bg:isDark?'#185FA5':'#378ADD', fg:'#fff',                         label:'P'};
      case 'C': return {bg:isDark?'#cba452':'#FFB74D', fg:isDark?'#412402':'#412402',     label:'C'};
      case 'F': return {bg:isDark?'#A32D2D':'#F06292', fg:'#fff',                         label:'F'};
      default:  return {bg:isDark?'#363634':'#d0cec7', fg:'inherit',                      label:''  };
    }
  }
  function getLegendItems(isDark, notObsBg) {
    return [
      {bg:isDark?'#0F6E56':'#1D9E75', label:'S — success: pipeline accepted, Cascade output'},
      {bg:isDark?'#185FA5':'#378ADD', label:'P — partial success: content loss'},
      {bg:isDark?'#cba452':'#FFB74D', label:'C — curl bypass: file present, no semantic content'},
      {bg:isDark?'#A32D2D':'#F06292', label:'F — failure: false completion, reuse, or terminal error'},
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
  function WOTable(props) {
    var dark = props.isDark;
    var cellW = props.large ? 48 : 36;
    var cellH = props.large ? 36 : 28;
    var agentColW = props.large ? 160 : 120;
    var fs = props.large ? 12 : 11;
    var tc = props.textColor || 'inherit';
    var notObsBg = dark ? '#363634' : '#d0cec7';
    return e('div', {className:'raw-wo-wrap'},
      e('table', {className:'raw-wo'},
        e('thead', null,
          e('tr', null,
            e('th', {className:'raw-wo-row-head', style:{minWidth:agentColW, color:tc}}, 'Agent'),
            testOrder.map(function(t) {
              return e('th', {key:t.id, style:{color:tc}},
                t.l1, e('br'), e('span', {className:'raw-wo-chunk-count'}, t.l2)
              );
            })
          )
        ),
        e('tbody', null,
          agentOrder.map(function(agent) {
            var ar = runs.filter(function(r) { return r.agent === agent; });
            if (!ar.length) return null;
            return e('tr', {key:agent},
              e('td', {className:'raw-wo-row-label', style:{color:tc, verticalAlign:'middle'}}, agentLabels[agent]),
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
                var c = getCellStyle(dark, run.outcome);
                return e('td', {key:t.id},
                  e('div', {
                    title: outcomeLabels[run.outcome] || run.outcome,
                    style:{
                      borderRadius:4, fontSize:fs, fontWeight:600,
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
    return e('p', {className:'raw-wo-note', style:{color:tc, marginTop:0, paddingTop:0}},
    e('i', null,
        'Columns: total chunks, ascending. ',
        e(C, null, 'EC-6'), ', ', e(C, null, 'BL-3'), ' - strongest file reuse evidence. ',
        e(C, null, 'OP-1'), ' ran 2 arena rounds. ',
        e(C, null, 'EC-3'), ' included as all agents produced output despite JSON response below chunking threshold. ',
        e(C, null, 'SWE-1.6*'), ' single retry produced different outcome than arena run.'

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
        e(WOTable, {large:false, isDark:isDark}),
        e('p', {className:'raw-wo-hint'}, '\u2197 click to expand')
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
        className:'raw-wo-overlay',
        onClick:function(ev){ if (ev.target === ev.currentTarget) setOpen(false); }
      },
        e('div', {
          className:'raw-wo-overlay-inner',
          style:{background:lbBg, color:lbText, width:'98vw'}
        },
          e('button', {
            className:'raw-wo-close',
            style:{color:lbText},
            onClick:function(){ setOpen(false); },
            'aria-label':'Close'
          }, '\u00d7'),
          e(WOTable, {large:true, isDark:isDark, textColor:lbText}),
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
  var root = ReactDOM.createRoot(document.getElementById('raw-wo-root'));
  root.render(e(App));
})();
</script>
{% endraw %}

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
|---|---|---|---|---|
| 1 | **No fixed character or token ceiling detected at retrieval stage** | All tests | Output sizes ranged from<br>275 B to 56 MB; no run hit a tool-imposed retriveal byte ceiling | **Ceilings self-imposed and/or write-stage failures: deliberate elision or environment degradation; retrieval pipeline has no confirmed upper bound** |
| 2 | **Output token ceiling as a write-stage failure mechanism** | `BL-3` | `SWE` exceeded the model's output token limit explicitly mid-write, visible in the thought panel in real time; first direct observation of this ceiling across any Cascade track | **Ceiling real but write-related, not retrieval-related. Prior tracks inferred it; `BL-3` observed it directly** |
| 3 | **Read-write asymmetry as dominant structural finding** | `SC-3` `SC-4` `BL-3` `OP-4` | Most agents successfully retrieved all chunks in every test; write success was substantially lower across the same tests | **Retrieval via `view_content_chunk` reliable; obstacle is reassembling, persisting at scale** |
| 4 | **Auto-pagination confirmed,<br>but doesn't predict output success** | All tests | 48 of 66 runs auto-paginated; 3 of 4 `BL-1` auto-paginating runs still failed to produce a valid output file | **`H5`-yes across the dataset; behavior robust; doesn't guarantee file persistence or<br>content fidelity** |
| 5 | **Auto-pagination threshold<br>~1K chunks** | `SC-2` `BL-2` `EC-3` | Most agents fully-paginated at ≤ 50 chunks; no agent auto-paginated `SC-2`'s 1,026-chunk corpus | **Threshold exists, exact boundary is unconfirmed, but likely in 100 - 1K chunks range** |
| 6 | **`curl` bypass produces semantically empty output** | `BL-1` `BL-3` `SC-2` `SC-3` `EC-1` `EC-6` | Agents that correctly diagnose the pipeline as returning processed Markdown switch to `curl`; resulting files contain raw HTML or JS skeletons, architecturally correct, textually less meaningful | **Pipeline abandonment is dominant response to fidelity instinct, produce files that pass verification while missing target content** |
| 7 | **Cross-agent file reuse confirmed at checksum level** | `BL-2` `BL-3` `EC-6` `OP-1` | `Gemini`, `GLM` produced output files with identical MD5 checksum; `GLM` ran earlier, wrote first; `Gemini`'s thought panel narrated retrieval while making no corresponding tool calls | **Path compliance independent variable; file presence at correct path doesn't confirm independent retrieval** |
| 8 | **False completion claims as a distinct failure mode** | `BL-1` `BL-3` `EC-6` `SC-3` `OP-1` | `Gemini`, `GPT-5.3-Codex`, `SWE` reported metrics, file paths for content that was never written | **Confident assertions without uncertainty signal structurally different from spirals, early stops, but all three failure modes produce same outcome: no valid output file** |
| 9 | **Redirect halt behavior is confirmed as server-side, not tool-layer rewriting** | `SC-2` | Three agents successfully called `read_url_content` a second time against the redirect destination surfaced in the error payload, received valid chunked responses, not silent pre-network URL substitution | **`read_url_content` makes network call, receives redirect, halts rather than automatically follows; destination<br>is actionable via<br>follow-up call** |
| 10 | **Chunking pipeline size threshold** | `EC-3` | 5-hop redirect chain returned ~366 B JSON inline via `read_url_content` alone; `view_content_chunk` not<br>called in any run | **Small payloads return inline without triggering the<br>two-fetch pipeline** |
| 11 | **URL fragment targeting is behavioral, not architectural** | `OP-1` | 8 of 10 agents retrieved all 92 chunks rather than targeting `#History` at chunk position 17; chunk index exposes the section header; `Grok` only agent to have used it for navigation | **Fragment-targeting achievable, but absent by default; agents attending to output completeness may prioritize full-doc collection** |
| 12 | **Prompt size estimates act as a confound for fidelity-sensitive agents** | `BL-1`, `OP-4` | `BL-1` ~85 KB prompt estimation architecturally unreachable; Cascade returns ~8–32 KB of filtered Markdown; `curl` returns<br>~508 KB of raw HTML; some agents spiraled or truncated trying to reach the target | **Prompt estimation became irresolvable constraint rather than a verification guide** |
| 13 | **_"EXACTLY as received"_ underspecified, resolved silently** | `BL-1` `OP-4` `SC-3` `SC-4` | Most agents interpreted output format as chunk index, metadata wrappers, raw HTTP response via `curl`, or semantic Markdown without flagging ambiguity or asking for clarification | **Instruction underspecification is reasoned-around across model families; only `Opus` identified the tradeoff in chat while strategizing a write plan** |
| 14 | **`search_web` not invoked as a retrieval mechanism** | Most tests | Across 66 runs only `SC-2`'s `SWE` called `search_web` after retrieval failure, which only returned a URL, not content | **`H4` untested across raw track; URL provision alone doesn't trigger `search_web`** |

## Perception Gap

| **Test** | **Expected** | **Received** | **Delivery Ratio** | **Agent Characterization** |
|---|---|---|---|---|
| **`EC-6`<br>Raw Markdown** | ~60 KB | ~96 KB<br>3 agents, independent writes | ~100% | _"Complete — chunk assembly variation within ±858 chars; elision markers are source false positives"_ |
| **`SC-4` Markdown Guide** | ~30 KB | `Sonnet`<br>30.44 KB<br>`Minimax` 32.33 KB | ~100% | _"Complete — breadcrumb heading injection at chunk boundaries inflates Minimax output; 6 elision markers present, but may be tool-layer assembly artifacts"_ |
| **`EC-3` Redirect JSON** | ~2 KB | 366 B<br>identical output | ~100% | _"Complete — 5-hop redirect chain followed cleanly; unique `X-Amzn-Trace-Id` per run confirms independent live requests"_ |
| **`SC-1` Gemini API Docs** | ~40 KB | 38–44 KB chunk cluster<br> 10.25 KB via direct fetch | chunk ~97%<br>direct ~60% | _"Chunk cluster structurally identical across agents; direct fetch cleaner, but loses code blocks, navigation structure"_ |
| **`SC-3` Wikipedia** | ~100 KB | `SWE`<br>69.5 KB pipeline<br>`GLM`/`Gemini`<br>275–774 KB via `curl` | pipeline ~68%; curl ~270–760% | _"Pipeline converts HTML tables to plain text lists, stripping column-row structure entirely; 255 table rows confirmed in raw HTML, 0 preserved in any Cascade-native output"_ |
| **`EC-1` Gemini API SPA** | ~100 KB | `SWE`, `Opus` ~33–35 KB pipeline; `GPT`/`Gemini` ~118 KB<br>via `curl` | pipeline ~32–34%; curl ~115% | _"JavaScript SPA handled by Cascade pre-processing layer; `SWE`, `Opus` extracted semantic content, code blocks, model descriptions; `curl` returned raw HTML skeleton regardless of agent"_ |
| **`BL-1` MongoDB Docs** | ~85 KB | `Opus`<br>~8 KB<br>`GLM`<br>~32 KB | ~9–38% | _"Pipeline output is 8–32 KB of filtered Markdown; raw HTML is<br>508 KB; no tool produces<br>estimated size"_ |
| **`BL-3` Tutorial** | ~250 KB | `Opus`<br>~7.4 KB<br> `GLM`<br>~468 KB | ~3% pipeline<br> ~180% via `curl` | _"Pipeline abandoned for `curl`; `curl` output Gatsby/React skeleton, no tutorial body content"_ |
| **`SC-2` Anthropic Docs** | ~80 KB | `Kimi`<br>53.65 MB | Full docs corpus | _"Scale outlier; VS Code tokenization, highlighting, scroll disabled on open; file exists, environment degraded"_ |

> _Implication: the [write outcome map](#agentic-write-performance) is the only verified signal in this dataset. Output size, path compliance, and agent self-report are somewhat insufficient to distinguish genuine retrieval from `curl` bypass, deliberate elision, or retrieval theater without cross-agent checksum comparison and thought panel inspection._
