---
layout: default
title: "Key Findings for Cascade's Web Search Behavior, Explicit"
permalink: /docs/cognition-windsurf-cascade/cascade-test-findings-explicit
parent: Cognition Windsurf Cascade
---

## Key Findings for Cascade's Web Search Behavior, Explicit `@web`

The explicit track confirms that `@web` doesn't meaningfully change the retrieval behavior the interpreted track
identified. Core findings hold: chunked architecture, no fixed ceiling, index-size suppression threshold,
CSS extraction failure, and self-reporting fidelity gaps. Extensions:

- `@web` is redundant with a URL
- Wider agent pool: `Gemini 3.1`, `GLM-5.1`, `GPT-5.4`, `o3`
- `SC-2` chunk sampling data
- More precise fidelity failure characterization
- [Colly](https://github.com/gocolly/colly) in toolchain
- Tool wrapper preamble inflates character counts

---

## [Cascade-explicit Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/windsurf-cascade-web-search/web_search_testing_framework.py)

1. Run `python web_search_testing_framework.py --test {test ID} --track explicit`
2. Review the terminal output
3. Copy the provided prompt asking the agent to report on fetch results:
   character count, token estimate, truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
4. Open a new Cascade session in Windsurf and paste the prompt into the chat window
5. Approve web fetch calls, but skip requests for runs of local scripts
6. Capture the agent's full response and observations as the explicit finding;
   the gap between the agent's self-report and actual fetch behavior is a finding
7. Log structured metadata as described in `framework-reference.md`
8. Ensure log results are saved to `/results/cascade-explicit/results.csv`

> _`@web` mapped to `read_url_content` in all runs; `search_web` called once; analysis in [Friction: Explicit](friction-note-explicit.md#web-semantics-prompt-tool-misalignment)._

---

## Platform Limit Summary

| **Limit** | **Observed** |
|---|---|
| **Hard Character Limit** | _None detected_: `read_url_content` returns a chunked index, not raw content with a byte ceiling; output chars reflect agent chunk selection depth from a pipeline that has no full-page retrieval path |
| **Hard Token Limit** | _None detected_: estimates ranged from ~91-85,000 tokens;<br>no run hit a fixed ceiling |
| **Output Consistency** | _Agent-dependent, self-reported_: same URL and prompt produces ~365–350,000 chars depending on agent and chunk selection; figures without verification script cross-reference; some values are retrieved content, others are full-doc extrapolations |
| **Content Selection Behavior** | _Two-stage chunked retrieval_: `read_url_content` returns a positional index with summaries; content requires sequential `view_content_chunk`<br>calls per position |
| **Truncation Pattern** | _Two independent truncation layers_: agent chunk selection, most large page content never fetched; per-chunk display ceiling variable by chunk, remainder hidden with a byte-count notice |
| **Redirect Chains** | _Consistent_: tested 5-level redirect chain; returned inline<br>without triggering chunked pipeline |
| **Self-reported Completeness** | _Inconsistent_: agents with identical content report contradictory truncation assessments; disagreement tracks chunk selection depth,<br>not actual content loss |
| **Chunk Summary Population** | _URL-dependent_: well-structured pages return populated summaries providing navigational signal; CSS-heavy or SPAs may return empty summaries collapsing skimming into blind sampling |
| **SPA extraction** | _Lossy by design_: Go Colly static scraper delivers ~20–35% of expected rendered page size as extracted text; `EC-1` runs ~20,000–35,500 chars from ~100 KB source; HTML stripped, JavaScript not executed before delivery; gap invisible to agents evaluating completeness<br>within the tool's output frame |
| **`@web` directive** | _Redundant for URL fetch_: `@web` maps to `read_url_content` across all agents, all runs; `search_web` called once for `SC-2`'s `GLM-5.1` run as verification attempt; didn't return usable content |
| **Agent Self-Reporting Fidelity** | _Unreliable_: thought panels display collapsed passes and/or batch reads, re-reads not disclosed in output; fidelity failures documented across<br>`BL-3`, `OP-4`, `SC-1`, `SC-2`, `SC-4` |

## Results Details

| | |
|---|---|
| **Agent Selector** | Hybrid Arena — 5 slots per run;<br>10 `BL-1` runs for prompt variant testing;<br>1 single-agent retry - `EC-1` run 6 |
| **Agents Observed** | `Claude Opus 4.7`, `Claude Sonnet 4.6`,<br>`Gemini 3.1`, `GLM-5.1`, `GPT-5.3-Codex`,<br>`GPT-5.4`, `Kimi K2.5`, `o3`, `SWE-1.6` |
| **Total Runs** | 66 |
| **Distinct URLs** | 11 |
| **Input Size Range** | ~2 KB – 256 KB |
| **Truncation Events** | 35 / 66 |
| **Average Output Size** | 43,441 chars |
| **Average Token Count** | 13,320 tokens |
| **Approval-gated Fetch** | 58 / 66 runs prompted for approval |
| **Auto-pagination** | 35 runs auto-paginated;<br> 1 run paginated when prompted |
| **Complete Retrieval Failure** | `EC-1` run 5 `Claude Sonnet 4.6`: infrastructure error;<br>no tool call completed, no output; rerun succeeded |
| **Content Targeting<br>Failure** | `SC-2` all followed redirect to `llms-full.txt`,<br>delivering all Anthropic docs instead of Messages API page, analysis in [Friction: Explicit](friction-note-explicit.md#sc-2-url-redirect-behavior) |
| **URL Fragment<br>Handling** | `OP-1` `#History` fragment not consistently honored;<br>3 of 5 agents reached targeted section |

## Agentic Pagination Depth

As observed in the interpreted track, agents consistently use `read_url_content` to fetch URLs, but depending on
the state of the chunk index, they reason whether individual calls to `view_content_chunk` is worth it. While it
determines output size and truncation self-report, chunks fetched remains the primary behavioral variable in this
dataset.

<div id="exp-hm-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.exp-hm-wrap { overflow-x: auto; }
table.exp-hm { border-collapse: collapse; width: 100%; }
table.exp-hm th { font-size: 11px; font-weight: 500; padding: 4px 5px; text-align: center; white-space: nowrap; color: inherit; }
table.exp-hm th.exp-row-head { text-align: left; }
table.exp-hm th .exp-chunk-count { font-weight: 400; font-size: 11px; opacity: 0.6; }
table.exp-hm td { padding: 2px 3px; text-align: center; }
table.exp-hm td.exp-row-label { font-size: 12px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; }
.exp-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.exp-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.75);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.exp-overlay-inner {
  border-radius: 10px;
  padding: 24px 28px;
  max-width: 98vw;
  max-height: 92vh;
  overflow: auto;
  position: relative;
}
.exp-close {
  position: absolute; top: 12px; right: 14px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.exp-close:hover { opacity: 1; }
.exp-note { font-size: 12px; margin-top: 10px; line-height: 1.6; opacity: 0.7; }
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
    {id:'BL-2', total:3,    l1:'BL-2',  l2:'3'    },
    {id:'EC-1', total:10,   l1:'EC-1',  l2:'10'   },
    {id:'SC-1', total:14,   l1:'SC-1',  l2:'14'   },
    {id:'SC-4', total:33,   l1:'SC-4',  l2:'33'   },
    {id:'EC-6', total:38,   l1:'EC-6',  l2:'38'   },
    {id:'BL-3', total:53,   l1:'BL-3',  l2:'53'   },
    {id:'OP-4', total:53,   l1:'OP-4',  l2:'53'   },
    {id:'BL-1', total:54,   l1:'BL-1',  l2:'54'   },
    {id:'SC-3', total:60,   l1:'SC-3',  l2:'60'   },
    {id:'OP-1', total:91,   l1:'OP-1',  l2:'91'   },
    {id:'SC-2', total:1009, l1:'SC-2',  l2:'1,009'},
  ];

  var runs = [
    {test:'BL-2', agent:'Codex',   fetched:3,    total:3   },
    {test:'BL-2', agent:'Opus',    fetched:3,    total:3   },
    {test:'BL-2', agent:'SWE',     fetched:3,    total:3   },
    {test:'BL-2', agent:'Kimi',    fetched:3,    total:3   },
    {test:'BL-2', agent:'GLM',     fetched:3,    total:3   },
    {test:'EC-1', agent:'GLM',     fetched:10,   total:10  },
    {test:'EC-1', agent:'Gemini',  fetched:3,    total:10  },
    {test:'EC-1', agent:'GPT54',   fetched:10,   total:10  },
    {test:'EC-1', agent:'SWE',     fetched:10,   total:10  },
    {test:'EC-1', agent:'Sonnet',  fetched:10,   total:10  },
    {test:'SC-1', agent:'Codex',   fetched:14,   total:14  },
    {test:'SC-1', agent:'SWE',     fetched:14,   total:14  },
    {test:'SC-1', agent:'GLM',     fetched:14,   total:14  },
    {test:'SC-1', agent:'Opus',    fetched:9,    total:14  },
    {test:'SC-1', agent:'Kimi',    fetched:10,   total:14  },
    {test:'SC-4', agent:'SWE',     fetched:33,   total:33  },
    {test:'SC-4', agent:'o3',      fetched:33,   total:33  },
    {test:'SC-4', agent:'GLM',     fetched:8,    total:33  },
    {test:'SC-4', agent:'Gemini',  fetched:1,    total:33  },
    {test:'SC-4', agent:'GPT54',   fetched:0,    total:33  },
    {test:'EC-6', agent:'SWE',     fetched:38,   total:38  },
    {test:'EC-6', agent:'GLM',     fetched:14,   total:38  },
    {test:'EC-6', agent:'Gemini',  fetched:5,    total:38  },
    {test:'EC-6', agent:'Opus',    fetched:0,    total:38  },
    {test:'EC-6', agent:'GPT54',   fetched:0,    total:38  },
    {test:'BL-3', agent:'Kimi',    fetched:11,   total:53  },
    {test:'BL-3', agent:'GLM',     fetched:13,   total:53  },
    {test:'BL-3', agent:'Sonnet',  fetched:6,    total:53  },
    {test:'BL-3', agent:'Codex',   fetched:0,    total:53  },
    {test:'BL-3', agent:'SWE',     fetched:1,    total:53  },
    {test:'OP-4', agent:'SWE',     fetched:53,   total:53  },
    {test:'OP-4', agent:'GLM',     fetched:14,   total:53  },
    {test:'OP-4', agent:'Kimi',    fetched:10,   total:53  },
    {test:'OP-4', agent:'Codex',   fetched:1,    total:53  },
    {test:'OP-4', agent:'Opus',    fetched:0,    total:53  },
    {test:'BL-1', agent:'SWE',     fetched:23,   total:54  },
    {test:'BL-1', agent:'Opus',    fetched:8,    total:54  },
    {test:'BL-1', agent:'Kimi',    fetched:3,    total:54  },
    {test:'BL-1', agent:'Codex',   fetched:2,    total:54  },
    {test:'BL-1', agent:'Sonnet',  fetched:2,    total:54  },
    {test:'SC-3', agent:'GLM',     fetched:5,    total:60  },
    {test:'SC-3', agent:'Kimi',    fetched:6,    total:60  },
    {test:'SC-3', agent:'SWE',     fetched:6,    total:60  },
    {test:'SC-3', agent:'Sonnet',  fetched:2,    total:60  },
    {test:'SC-3', agent:'Codex',   fetched:1,    total:60  },
    {test:'OP-1', agent:'Opus',    fetched:4,    total:91  },
    {test:'OP-1', agent:'GLM',     fetched:3,    total:91  },
    {test:'OP-1', agent:'Kimi',    fetched:3,    total:91  },
    {test:'OP-1', agent:'Codex',   fetched:1,    total:91  },
    {test:'OP-1', agent:'SWE',     fetched:1,    total:91  },
    {test:'SC-2', agent:'Kimi',    fetched:5,    total:1009},
    {test:'SC-2', agent:'SWE',     fetched:4,    total:1009},
    {test:'SC-2', agent:'Opus',    fetched:2,    total:1009},
    {test:'SC-2', agent:'GLM',     fetched:2,    total:1009},
    {test:'SC-2', agent:'Codex',   fetched:1,    total:1009},
  ];

  var agentOrder = ['Sonnet','Opus','Gemini','GLM','Codex','GPT54','Kimi','o3','SWE'];
  var agentLabels = {
    Sonnet: 'Claude Sonnet 4.6',
    Opus:   'Claude Opus 4.6-7',
    Gemini: 'Gemini 3.1',
    GLM:    'GLM-5.1',
    Codex:  'GPT-5.3-Codex',
    GPT54:  'GPT-5.4',
    Kimi:   'Kimi K2.5',
    o3:     'o3',
    SWE:    'SWE-1.6',
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
      {bg:isDark?'#185FA5':'#378ADD', label:'50–99% - most chunk summaries viewed'},
      {bg:isDark?'#cba452':'#FFB74D', label:'10–49% - sparse chunk summary sampling'},
      {bg:isDark?'#A32D2D':'#F06292', label:'<10% - endpoint chunk summary sampling'},
      {bg:isDark?'#3C3489':'#BA68C8', label:'0: declined pagination'},
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
    var agentColW = props.large ? 160 : 110;
    var fs = props.large ? 12 : 11;
    var tc = props.textColor || 'inherit';
    var notObsBg = dark ? '#363634' : '#d0cec7';

    return e('div', {className:'exp-hm-wrap'},
      e('table', {className:'exp-hm'},
        e('thead', null,
          e('tr', null,
            e('th', {className:'exp-row-head', style:{minWidth:agentColW, color:tc}}, 'Agent'),
            testOrder.map(function(t) {
              return e('th', {key:t.id, style:{color:tc}},
                t.l1, e('br'), e('span', {className:'exp-chunk-count'}, t.l2)
              );
            })
          )
        ),
        e('tbody', null,
          agentOrder.map(function(agent) {
            var ar = runs.filter(function(r) { return r.agent === agent; });
            return e('tr', {key:agent},
              e('td', {className:'exp-row-label', style:{color:tc, verticalAlign:'middle'}}, agentLabels[agent]),
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
    return e('p', {className:'exp-note', style:{color:tc, marginTop:0, paddingTop:0}},
      e('i', null,
        'Columns: total chunks, ascending. Excluded: ',
        e(C, null, 'EC-3'), ' — untriggered chunked pipeline. ',
        '0: agent observed, but no ', e(C, null, 'view_content_chunk'), ' call made. ',
        e(C, null, 'SC-2'), ' included; URL redirect delivered entire docs set, not targeted page. ',
        'Hover over cells for fetched/total counts.'
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
        e('p', {className:'exp-hint'}, '\u2197 click to expand')
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
        className:'exp-overlay',
        onClick:function(ev){ if (ev.target === ev.currentTarget) setOpen(false); }
      },
        e('div', {
          className:'exp-overlay-inner',
          style:{background:lbBg, color:lbText, width:'98vw'}
        },
          e('button', {
            className:'exp-close',
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

  var root = ReactDOM.createRoot(document.getElementById('exp-hm-root'));
  root.render(e(App));
})();
</script>

The tractability threshold is visible across tests: agents tend toward full retrieval on
chunk counts ≤14 and toward sparse sampling on larger ones ≥50, with 33–38 chunks as the transition
zone where model families diverge. `SWE` shows the most consistent full-retrieval behavior while
`GLM`, `GPT` and `Kimi` use sparse sampling more than any other technique.

`BL-3` and `OP-4` use the same source URL across different test sessions, making them the only direct
same-source comparison in the dataset. Retrieval depth isn't consistent across sessions: `SWE` retrieved
all chunks in `OP-4` but only 1 chunk in `BL-3`; `GPT-5.3-Codex` retrieved 1 chunk in `OP-4` and stopped
at the index in `BL-3`. `GLM` and `Kimi` were more stable across sessions, but no agent produced identical
retrieval depth in both runs. Retrieval depth may reflect a mix of verified and unverified session conditions
such as context window state, tool response latency, arena slot position, Windsurf version, and chunk summary
content - as much as individual agent capability.

---

## `@web`: Routing Hint, not Retrieval Modifier 

Across all runs, no agent said the obvious thing: `@web` is redundant with a URL. Agents exhibited a wide range
of architectural understanding from non-recognition to mechanical familiarity of the underlying parsing service,
without mentioning that in this context, calling it would produce no behavioral difference. This absence is the
`H4` finding; analysis in [Friction: Explicit](friction-note-explicit.md#web-semantics-prompt-tool-misalignment).

<style>
.web-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin: 1.5rem 0;
}
@media (max-width: 600px) {
  .web-grid {
    grid-template-columns: 1fr;
  }
}
.web-card {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 12px 14px;
  display: block;
  width: 100%;
  box-sizing: border-box;
   text-align: center;
}
.web-card p {
  margin: 0 0 8px;
}
.web-card-agent {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--muted);
  margin: 0 0 6px;
  letter-spacing: 0.03em;
}
.web-card-quote {
  font-size: 0.8rem;
  color: var(--text);
  line-height: 1.6;
  margin: 0 0 10px;
  font-style: italic;
}
.web-card-tag {
  display: inline-block;
  font-size: 0.7rem;
  padding: 2px 7px;
  border-radius: 2px;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--muted);
  letter-spacing: 0.02em;
}
.web-grid-note {
  font-size: 0.8rem;
  color: var(--muted);
  border-left: 2px solid var(--border);
  padding-left: 1rem;
  margin: 1rem 0 0;
  line-height: 1.7;
}
</style>

<div class="web-grid">
  <div class="web-card">
    <p class="web-card-agent">SWE-1.6</p>
    <span class="web-card-tag">No Product Knowledge</span>
    <p class="web-card-quote">"I don't have a tool called <code>@web</code>. Was there a different tool you intended for me to use?"</p>
  </div>
  <div class="web-card">
    <p class="web-card-agent">GPT-5.3-Codex</p>
    <span class="web-card-tag">Tool Mapping Only</span>
    <p class="web-card-quote">"<code>@web</code> maps conceptually to web retrieval tooling — <code>read_url_content</code> under the hood."</p>
  </div>
  <div class="web-card">
    <p class="web-card-agent">Kimi K2.5</p>
    <span class="web-card-tag">Tool Mapping Only</span>
    <p class="web-card-quote">"<code>@web</code> is a user-facing alias that routes to <code>read_url_content</code> as the fetch mechanism."</p>
  </div>
  <div class="web-card">
    <p class="web-card-agent">Claude Sonnet 4.6</p>
    <span class="web-card-tag">UI Awareness</span>
    <p class="web-card-quote">"Not a distinct tool or named symbol — a user-facing shorthand in the Windsurf chat UI."</p>
  </div>
  <div class="web-card">
    <p class="web-card-agent">Claude Opus 4.6-7</p>
    <span class="web-card-tag">Conditional Routing</span>
    <p class="web-card-quote">"<code>@web</code> resolves to <code>read_url_content</code> for a direct URL fetch; would resolve to <code>search_web</code> for a query-based task."</p>
  </div>
   <div class="web-card">
    <p class="web-card-agent">GPT-5.4</p>
    <span class="web-card-tag">Conditional Routing</span>
    <p class="web-card-quote">"Direct URL → <code>read_url_content</code>; search query → <code>search_web</code>. No literal tool named <code>@web</code>."</p>
  </div>
  <div class="web-card">
    <p class="web-card-agent">GLM-5.1</p>
    <span class="web-card-tag">Pipeline Depth</span>
    <p class="web-card-quote">"A directive that triggers the chunking pipeline, not a separate tool, a user-facing shorthand."</p>
  </div>
  <div class="web-card">
    <p class="web-card-agent">o3</p>
    <span class="web-card-tag">Pipeline Depth</span>
    <p class="web-card-quote">"<code>@web</code> maps to <code>read_url_content</code> followed by <code>view_content_chunk</code> to stream the page content."</p>
  </div>
  <div class="web-card">
    <p class="web-card-agent">Gemini 3.1</p>
    <span class="web-card-tag">Implementation Detail</span>
    <p class="web-card-quote">"A macro proxying to <code>read_url_content</code> — runs the page through a parsing service that breaks the document into an AST-like structure chunked by headings."</p>
  </div>
</div>

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
|---|---|---|---|---|
| 1 | **`read_url_content` returns chunk index** | All tests | Requires `view_content_chunk` × N;<br>no single-call full-page<br>retrieval path | **Output chars reflect chunks fetched, not retrieval ceiling; variance behavioral, not architectural** |
| 2 | **No fixed character or token ceiling detected** | `BL-1`<br>`EC-6`<br>`SC-4` | `BL-1` `Opus` estimated ~120,000–200,000 chars across 54 chunks;<br>`EC-6` `SWE` measured 61,921 chars with no cutoff; `SC-4` `o3` summed 34,200 chars across 33 chunks | **If ceiling exists, no test hit it; constraint is chunks fetched, not a tool-imposed byte limit** |
| 3 | **Per-chunk display truncation<br>is a second independent layer** | `BL-1`<br>`SC-4`<br>`OP-4` | `view_content_chunk` hides middle portion of large chunks with explicit byte-count notice;<br>`SC-4` `SWE` found 3,766 bytes hidden across 4 positions; `OP-4` `SWE` found truncation warnings on all 53 chunks ranging 367–24,204 bytes | **Full chunk retrieval doesn't guarantee full content delivery; internal truncation invisible** |
| 4 | **Truncation self-report tracks chunks fetched, not content loss** | `SC-4`<br>`BL-3`<br>`SC-3` | Agents sampling 3 chunks reported no truncation; agents retrieving all 33 found byte-level notices at 4 positions; `SWE` and `o3` full-retrieval contradiction on identical source | **Self-reported truncation accurate for chunks seen, not accurate for doc; agents conflate retrieval completeness with content fidelity** |
| 5 | **Chunk summary population determines retrieval strategy quality** | `SC-1`<br>`SC-3`<br>`BL-3`<br>`OP-4` | `SC-1` populated summaries enabled chrome exclusion before fetching; `BL-3` and `OP-4` empty summaries (`"/"`) collapsed skimming to blind sampling; `SC-3` populated summaries present, but unused above ~50 chunks | **Index-guided targeting requires populated summaries; populated summaries provide signal but don't guarantee targeted retrieval** |
| 6 | **SPA sources produce an extraction ratio gap, not a truncation event** | `EC-1` | Go Colly static scraper delivers ~20–35% of raw HTML as extracted text; ~70 KB gap on a ~100 KB page, suggesting gap is architectural | **Agents evaluate completeness within tool output frame, characterize gap as pipeline transformation, not content loss** |
| 7 | **Routing bypasses chunked pipeline for small payloads** | `EC-3` | `read_url_content` returned<br>5 redirect-chain terminal JSON response inline ~353–367 chars body; `view_content_chunk`<br>not called in any run | **Chunked architecture has at least two modes; small payloads return inline without triggering the two-fetch process** |
| 8 | **`@web` redundant with URLs** | All tests | Most agents used toolchain identical to interpreted track: `read_url_content` → `view_content_chunk` | **`@web` produced no behavior change; `H4` confirmed redundant** |
| 9 | **`@web` conditional routing described consistently** | `SC-1`<br>`SC-2`<br>`SC-4`<br>`EC-6`| `@web` + URL → `read_url_content`; `@web` + query → `search_web`; `GLM-5.1` invoked `search_web` once during<br>`SC-2` as an independent verification, but returned<br>near-empty results | **`@web` is a routing hint; `search_web` verification call distinct from `@web`-driven routing, didn't produce usable output** |
| 10 | **Agent self-reporting fidelity is a systematic confound** | `SC-2`<br>`OP-4`<br>`BL-3`<br>`SC-1`<br>`SC-4` | Under-reporting; partial reporting; parallel execution opacity | **Don't treat agent self-report as complete record, add thought panel cross-reference; analysis in [Friction: Explicit](friction-note-explicit.md#agent-self-reporting-fidelity)** |
| 11 | **Index size suppresses auto-pagination above ~50 chunks** | `SC-3`<br>`OP-1`<br>`BL-3`<br>`OP-4` | Maximum chunks retrieved:<br>`SC-3`: 6/60, `OP-1`: 5/91,<br>`BL-3`: 19/53,<br>`OP-4`, `SWE` only: 53/53 | **Tractability threshold is agent-dependent, index-size-sensitive; 33–38 chunks is transition zone where agents diverge** |
| 12 | **CSS-heavy sources produce content extraction failure, not truncation** | `BL-1`<br>`BL-3`<br>`OP-4` | MongoDB LeafyGreen CSS dominated chunk content across all runs on three distinct MongoDB URLs; tutorial body content absent across all 53 chunks in all `BL-3` runs; _"Structurally complete, semantically incomplete"_  | **Page navigation and chrome recovered; article content inaccessible regardless of retrieval depth** |
| 13 | **Tool wrapper preamble inflates character counts** | `EC-3` | `Claude Opus 4.7` identified and quoted the preamble string `"Here is the content of the article at [URL]"` prepended by `read_url_content`; explains cross-run variance on identical content | **Variance between runs on identical content reflects tool wrapper inclusion rules, not retrieval differences** |
| 14 | **Colly identified as fetch backend** | `EC-3` | `GLM-5.1` and `Claude Opus 4.7` independently identified<br>`User-Agent: colly — https://github.com/gocolly/colly` from `httpbin`'s echoed request headers | **Windsurf uses scraping library; possibly explains CSS and/or SPA extraction gap** |
| 15 | **Per-chunk byte ceiling may reflect server-side rate limiting, not a tool gate** | `SC-2` | `SWE`, `GLM` hit 17,993-byte truncation at chunk 1008, mid-identifier inside `BetaManagedAgentsModelRateLimitedError`; likely HTTP response complete, but agent abstracted | **Unresolvable from agent self-report, raw track required** |

## Perception Gap

| **Test** | **Expected** | **Received** | **Delivery Ratio** | **Agent Characterization** |
|---|---|---|---|---|
| **`EC-6`<br>Raw Markdown** | ~61 KB | 61,921 chars<br>`SWE` full retrieval | ~97% | _"No truncation, structurally complete; tool transforms content before delivery"_ |
| **`SC-4`<br>Markdown Guide** | ~30 KB | ~15,500–34,200 chars; full retrieval runs | ~52–114%* | _"Complete but contradicted; `SWE` found truncation at 4 positions; `o3` found none<br>on identical content"_ |
| **`EC-1`<br>SPA** | ~100 KB | ~20,100–35,500 chars extracted | ~20–36% | _"Extraction ratio, not truncation — HTML stripped and JavaScript not executed before delivery"_ |
| **`SC-3`<br>Wikipedia** | ~100 KB | ~4,900 chars index to ~150,000 chars extrapolated | varies by method | _"No truncation, index complete vs yes, 57/60 chunks never fetched"_ |
| **`BL-3`<br>CSS Tutorial** | ~256 KB | ~2,598–350,000 chars across runs | indeterminate | _"Structurally complete, semantically incomplete; tutorial body absent across all chunks"_ |
| **`EC-3`<br>Redirect JSON** | ~2 KB | ~353–367<br>chars body | ~15–18% of expected | _"Complete; JSON payload is the full response; size gap reflects redirect chain delivering terminal response only"_ |

> _* `SC-4` figures above 100% reflect counting method differences, not over-retrieval.
> `SWE` and `o3` both retrieved all 33 chunks and reported estimates differing by
> ~18,700 chars; the largest same-source, same-depth variance in the dataset._
>
> _Implication: output chars aren't an appropriate truncation ceiling metric for Cascade; they
> reflect chunk count, content transformation, and tool wrapper inclusion rules. None is
> observable from agent self-report alone._