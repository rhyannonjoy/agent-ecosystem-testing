---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Desktop"
permalink: /docs/open-ai-codex/codex-test-findings-desktop
parent: OpenAI Codex
---

# Key Findings for Codex's Web Search Behavior, `GPT`-interpreted - Desktop

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search//scripts/framework.py)

1. Run `python scripts/framework.py --test {test ID} --track codex-interpreted`
2. Review terminal output
3. Copy the provided prompt asking agent to report on fetch results:
   character count, token estimate,<br>truncation status, content completeness,
   Markdown formatting integrity, and tool visibility
4. Open a new session in the Codex desktop app, paste the prompt into the chat window
5. Approve `curl` escalation and shell permission requests; skip requests for runs of local scripts
6. Capture the agent's full response; observe the gap between self-report and actual retrieval behavior<br>as the interpreted finding
7. Log structured metadata as described in [`framework-reference.md`](https://rhyannonjoy.github.io/agent-ecosystem-testing/docs/open-ai-codex/framework-reference#workflow)
8. Ensure results saved to [`/results/codex-interpreted/results.csv`](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/results/codex-interpreted/results.csv)

---

## Platform Limit Summary

| **Limit** | **Observed** |
| --- | --- |
| **Hard<br>Character<br>Limit** | _None detected via `curl` path_: successful `curl` fetches returned payloads from 660 chars to 3.1 MB with no ceiling hit; output chars on the `web` path reflect a `wordlim: 200` window, not a byte ceiling |
| **Hard<br>Token<br>Limit** | _None detected via `curl` path_: token counts ranged from ~24 to ~835,000; display truncation confirmed at ~12,970 tokens in `EC-6` tool output rendering, independent of HTTP retrieval |
| **Output<br>Consistency** | _LLM-version-stratified_: same URL and intelligence level produced distinct output sizes and tool strategies across `GPT-5.2` through `GPT-5.5`; intelligence level weaker predictor than LLM version |
| **Content<br>Selection<br>Behavior** | _Two-tier retrieval_: `web` returns rendered text extraction often with `wordlim: 200`; full content requires `curl` escalation with elevated network permissions; `SC-1`:`GPT-5.3-Codex Extra High` only agent to report `response_length` suggesting `wordlim: 200` soft-cap, agent-adjustable parameter |
| **Truncation<br>Pattern** | _Three independent truncation layers_: `web` line-indexed window, LLM/URL dependent - `L237–L657`, `EC-6`'s terminal display cap ~12,970 tokens, and underlying `curl` response `Loading...` placeholders |
| **`web`<br>Line-Indexed<br>Window** | _LLM-version-URL-dependent_: agent's choice, varied across sessions, rarely started at `L0` - <br>`BL-1`:`L140`, `BL-3`:`L453`, `EC-1`:`L479`, `OP-1`:`L305/L477/L552`, `OP-4`:`L237`, `SC-1`:`L362/L478`, <br>`SC-3`:`L266/L309/L353`, `SC-4`:`L316/L657` |
| **`curl`<br>Escalation** | _LLM-version-dependent_: `GPT-5.2` requires `Medium`+ intelligence; `GPT-5.3-Codex` typically `Medium`+, `GPT-5.4` escalates at `Low`, `GPT-5.5` bypasses `web` pipeline at all levels without exposing reasoning |
| **Session<br>Contamination** | _Fresh fetch compound_: prior sessions' artifacts persist across runs in `Documents/Codex` while `/private/tmp` clears between sessions; filename reuse observed in 42 / 261 runs, while explicit artifact reuse reported less often, write-save location pattern nondeterministic |
| **Post-Session Auto-Editing** | _Data integrity risk_: continues processing sessions after chats in and out of archives - output editing, thought panel collapse with reasoning and/or command execution removed, timer drift and/or removal - `GPT-5.2` timers removed completely; `Auto-review`, `Full Access` disabling has no impact on this behavior |
| **JS-Rendered<br>Pages** | _Structural retrieval failure_: `SC-2` - Next.js/Netlify and `BL-3` - Next.js/Gatsby tutorial body absent from static extraction regardless of  or intelligence level; `curl` returns app shell only |
| **`Cache Miss`<br>Failure** | _Systematic_: agents reported `web`:`Cache Miss` on `EC-6` mutable, raw GitHub URL across all runs that attempted it; additional test ruled out a blanket host block |
| **Self-reported Completeness** | _`curl`-anchored_: agents conflate `curl` body completeness with overall retrieval completeness even if artifacts display otherwise; `web` truncation consistently underreported in summary assessments |

## Results Details

| | |
| --- | --- |
| **Track** | `T1` GPT-interpreted, Codex Desktop App |
| **Agents Observed** | `GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5` |
| **Intelligence Levels** | `Low`, `Medium`, `High`, `Extra High` |
| **Total Runs** | 261 |
| **Distinct URLs** | 13 |
| **Input Size Range** | `EC-3`: ~660 chars to `BL-3`: ~3.1 MB |
| **Truncation Events** | 195 / 261 ~75% of agents report truncation in some form<br>- `web`-only path with limits reported explicitly: 42 <br>- `web`&rarr;`curl` path with `web` limits reported explicitly: 114<br>- `web`&rarr;`curl` path with `web` limits implied in reasoning: 39<br>- `curl`-only path and/or no truncation signal: 66 |
| **Average Output Size** | 351,961 chars |
| **Output Size Range** | 95 - 3,103,342 chars |
| **Average Token Use** | 88,489 tokens |
| **Token Count Range** | 24 - 835,000 tokens |
| **Workspace Substitution** | 2 / 261 runs confirmed, contamination risk flagged in ~40 additional runs |
| **`curl` Escalation** | Dominant retrieval path, present 69% of track ~180 / 261 runs |
| **`web` Bypass** | `GPT-5.5` at all intelligence levels skipped `web` completely on at least one URL |

## Content Access x Intelligence

Agentic task completion isn't a useful signal for page readability. For Codex, retrieval strategy largely influences content accessbility; its `web` tool
returns a rendered text extraction window, but it's up to the agent to use it and most agent's didn't, at least not completely. Agents across this track most often
started with `web`, recognized its limits, and pivoted to `curl` to complete the task, but `curl` returns a raw HTTP body whose readability entirely depends on that
page's architecture. For JS-rendered pages, `curl` delivers app shells with prose absent. Agents rarely distinguished between having fetched a URL and
having read it.

The heat map below encodes retrieval strategy, not task outcome. Rows are reasoning/intelligence levels, with LLM version as a sub-grouping. Columns are URLs ordered
by content accessibility difficulty, left to right: static payloads → large static HTML → JS-rendered and/or SPAs where `curl` returns mostly scaffolding.

{% raw %}
<div id="cdx-hm2-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.cdx2-wrap { overflow-x: auto; }
table.cdx2 { border-collapse: collapse; width: 100%; }
table.cdx2 th { font-size: 10px; font-weight: 500; padding: 3px 4px; text-align: center; white-space: nowrap; color: inherit; }
table.cdx2 th.cdx2-rh { text-align: left; }
table.cdx2 th .cdx2-sub { font-weight: 400; font-size: 10px; opacity: 0.55; display: block; }
table.cdx2 td { padding: 2px 2px; text-align: center; }
table.cdx2 td.cdx2-rl { font-size: 11px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; vertical-align: middle; }
table.cdx2 td.cdx2-rl.cdx2-model { font-size: 10px; opacity: 0.65; padding-left: 8px; }
.cdx2-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.cdx2-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.78);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.cdx2-overlay-inner {
  border-radius: 10px; padding: 22px 26px;
  max-width: 99vw; max-height: 93vh;
  overflow: auto; position: relative;
}
.cdx2-close {
  position: absolute; top: 10px; right: 12px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.cdx2-close:hover { opacity: 1; }
.cdx2-section-label {
  font-size: 10px; font-weight: 600; letter-spacing: 0.06em;
  opacity: 0.45; padding: 6px 0 2px 0; text-align: left;
}
.cdx2-divider td { border-top: 1px solid rgba(128,128,128,0.18); height: 4px; }
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

  // Columns ordered by content accessibility difficulty:
  // clean static → large static → JS-rendered/SPA (curl returns unreadable shell)
  // Each entry: id, short label, difficulty tier, note shown on hover
  var cols = [
    // ── Readable via web.open ─────────────────────────────────────────
    {id:'EC-3',  l1:'EC-3',  l2:'660 B',   tier:'readable', note:'Redirect JSON — tiny, inline, no truncation possible'},
    {id:'BL-2',  l1:'BL-2',  l2:'6 KB',    tier:'readable', note:'Raw Markdown — small, clean, well below any ceiling'},
    {id:'EC-6',  l1:'EC-6',  l2:'92 KB',   tier:'readable', note:'Raw GitHub Markdown — web.open cache miss; curl readable'},
    {id:'SC-4',  l1:'SC-4',  l2:'65 KB',   tier:'readable', note:'Markdown Guide — static HTML, fully readable via curl'},
    {id:'SC-1',  l1:'SC-1',  l2:'121 KB',  tier:'readable', note:'Gemini API docs — static HTML, readable via curl'},
    // ── Large static — readable via curl but web.open truncates ───────
    {id:'BL-1',  l1:'BL-1',  l2:'505 KB',  tier:'large',    note:'MongoDB docs — large static; curl readable; web.open line-windowed'},
    {id:'OP-2',  l1:'OP-2',  l2:'240 KB',  tier:'large',    note:'MDN Array — large static HTML; curl readable'},
    {id:'OP-1',  l1:'OP-1',  l2:'696 KB',  tier:'large',    note:'Wikipedia + #fragment — large; fragment silently dropped'},
    {id:'SC-3',  l1:'SC-3',  l2:'786 KB',  tier:'large',    note:'Wikipedia population table — large; curl readable raw HTML'},
    {id:'OP-4',  l1:'OP-4',  l2:'514 KB',  tier:'large',    note:'CommonMark spec — large; curl readable; web.open line-windowed'},
    // ── JS-rendered — curl returns unreadable shell ───────────────────
    {id:'EC-1',  l1:'EC-1',  l2:'133 KB',  tier:'spa',      note:'Gemini API SPA — web.open ~10% of raw; curl readable static shell'},
    {id:'BL-3',  l1:'BL-3',  l2:'3.1 MB',  tier:'spa',      note:'MongoDB Atlas tutorial — Next.js/Gatsby; tutorial body JS-rendered, absent from any fetch'},
    {id:'SC-2',  l1:'SC-2',  l2:'512 KB',  tier:'spa',      note:'Anthropic API docs — Next.js CSP-nonce SPA; curl returns app shell only; API reference text inaccessible'},
  ];

  // Surface encoding per run.
  // web        — agent used web.open only (got text extraction, readable but possibly truncated)
  // web+curl   — used both; reported on web.open limits explicitly (mixed)
  // curl       — escalated to curl; bypassed or skipped web.open (implicit or curl-primary)
  // web-fail   — attempted web.open, got nothing useful (cache miss, 0 bytes, DNS block)
  // none       — no usable content retrieved (runaway loop, hard fail)
  // n/a        — not run

  // Rows: grouped by intelligence level, sub-keyed by model version
  // Key format: "MODEL:LEVEL" e.g. "5.2:L"
  var LEVELS = ['L','M','H','XH'];
  var MODELS = ['5.2','5.3','5.4m','5.4','5.5'];

  var MODEL_LABELS = {
    '5.2':  'GPT-5.2',
    '5.3':  'GPT-5.3-Codex',
    '5.4m': 'GPT-5.4-Mini',
    '5.4':  'GPT-5.4',
    '5.5':  'GPT-5.5',
  };
  var LEVEL_LABELS = { L:'Low', M:'Medium', H:'High', XH:'Extra High' };

  // Surface data: runs[testId][modelKey] = {surface, note}
  // modelKey = model + ':' + level
  var runs = {
    'EC-3': {
      '5.2:L':'web','5.2:M':'curl','5.2:H':'web','5.2:XH':'web',
      '5.3:L':'web','5.3:M':'web','5.3:H':'web','5.3:XH':'web',
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web','5.4m:XH':'web',
      '5.4:L':'web','5.4:M':'web','5.4:H':'web','5.4:XH':'web',
      '5.5:L':'web','5.5:M':'web','5.5:H':'curl','5.5:XH':'web',
    },
    'BL-2': {
      '5.2:L':'web-fail','5.2:M':'web+curl','5.2:H':'web+curl','5.2:XH':'web+curl',
      '5.3:L':'web-fail','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.4:L':'web+curl','5.4:M':'web-fail','5.4:H':'web+curl','5.4:XH':'web+curl',
      '5.5:L':'curl','5.5:M':'curl','5.5:H':'curl','5.5:XH':'web+curl',
    },
    'EC-6': {
      '5.2:L':'curl','5.2:M':'curl','5.2:H':'curl','5.2:XH':'curl',
      '5.3:L':'curl','5.3:M':'web+curl','5.3:H':'curl','5.3:XH':'curl',
      '5.4m:L':'curl','5.4m:M':'curl','5.4m:H':'curl','5.4m:XH':'curl',
      '5.4:L':'curl','5.4:M':'curl','5.4:H':'curl','5.4:XH':'curl',
      '5.5:L':'curl','5.5:M':'curl','5.5:H':'curl','5.5:XH':'curl',
    },
    'SC-4': {
      '5.2:L':'web','5.2:M':'web+curl','5.2:H':'web+curl','5.2:XH':'web+curl',
      '5.3:L':'curl','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.4:L':'web+curl','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'web+curl',
      '5.5:L':'curl','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'SC-1': {
      '5.2:L':'web+curl','5.2:M':'web+curl','5.2:H':'web','5.2:XH':'web+curl',
      '5.3:L':'web+curl','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web','5.4m:XH':'web',
      '5.4:L':'web','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'web+curl',
      '5.5:L':'web+curl','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'BL-1': {
      '5.2:L':'web','5.2:M':'web','5.2:H':'curl','5.2:XH':'curl',
      '5.3:L':'web','5.3:M':'web','5.3:H':'web','5.3:XH':'web',
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web','5.4m:XH':'web',
      '5.4:L':'curl','5.4:M':'curl','5.4:H':'curl','5.4:XH':'curl',
      '5.5:L':'curl','5.5:M':'curl','5.5:H':'curl','5.5:XH':'curl',
    },
    'OP-2': {
      '5.2:L':'web+curl','5.2:M':'web+curl','5.2:H':'web+curl','5.2:XH':'web+curl',
      '5.3:L':'web+curl','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web',
      '5.4:L':'web+curl','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'web+curl',
      '5.5:L':'curl','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'OP-1': {
      '5.2:L':'curl','5.2:M':'web','5.2:H':'web+curl','5.2:XH':'curl',
      '5.3:L':'web','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web+curl','5.4m:XH':'web',
      '5.4:L':'web','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'curl',
      '5.5:L':'curl','5.5:M':'web+curl','5.5:H':'curl','5.5:XH':'web+curl',
    },
    'SC-3': {
      '5.2:L':'web','5.2:M':'web+curl','5.2:H':'web+curl','5.2:XH':'web+curl',
      '5.3:L':'web','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.4:L':'web','5.4:M':'web','5.4:H':'web','5.4:XH':'web+curl',
      '5.5:L':'web+curl','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'OP-4': {
      '5.2:L':'web','5.2:M':'web','5.2:H':'web','5.2:XH':'web+curl',
      '5.3:L':'web','5.3:M':'curl','5.3:H':'curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web+curl',
      '5.4:L':'web+curl','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'web+curl',
      '5.5:L':'curl','5.5:M':'curl','5.5:H':'curl','5.5:XH':'web+curl',
    },
    'EC-1': {
      '5.2:L':'web+curl','5.2:M':'web','5.2:H':'web+curl','5.2:XH':'none',
      '5.3:L':'web-fail','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'web+curl','5.4m:H':'web+curl','5.4m:XH':'web',
      '5.4:L':'web+curl','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'web',
      '5.5:L':'curl','5.5:M':'curl','5.5:H':'web+curl','5.5:XH':'curl',
    },
    'BL-3': {
      '5.2:L':'web+curl','5.2:M':'web+curl','5.2:H':'web+curl','5.2:XH':'web+curl',
      '5.3:L':'web','5.3:M':'web','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'web','5.4m:M':'curl','5.4m:H':'curl','5.4m:XH':'curl',
      '5.4:L':'web','5.4:M':'web+curl','5.4:H':'web+curl','5.4:XH':'web+curl',
      '5.5:L':'curl','5.5:M':'web+curl','5.5:H':'web+curl','5.5:XH':'web+curl',
    },
    'SC-2': {
      '5.2:L':'web','5.2:M':'web','5.2:H':'web+curl','5.2:XH':'none',
      '5.3:L':'web-fail','5.3:M':'web+curl','5.3:H':'web+curl','5.3:XH':'web+curl',
      '5.4m:L':'curl','5.4m:M':'web','5.4m:H':'web','5.4m:XH':'curl',
      '5.4:L':'web','5.4:M':'web+curl','5.4:H':'web','5.4:XH':'web+curl',
      '5.5:L':'web+curl','5.5:M':'curl','5.5:H':'web+curl','5.5:XH':'web',
    },
  };

  var SURFACE_NOTE = {
    'web':      'web-only text extraction, readable but truncated',
    'web+curl': 'web + curl used with web limits reported',
    'curl':     'curl-only raw HTTP body, readability architecture-dependent',
    'web-fail': 'web attempted, no usable content returned: cache miss / DNS / 0 bytes',
    'none':     'no usable content retrieved',
  };

  function getColors(dark, surface) {
    // web      → green   — text extraction, readable (Cascade 100% = best outcome)
    // web+curl → blue    — both surfaces, most informative (Cascade 50-99%)
    // curl     → amber   — raw body only, readability uncertain (Cascade 10-49%)
    // web-fail → pink    — attempted, nothing returned (Cascade <10%)
    // none     → red/orange — complete failure (Cascade refused)
    var map = {
      'web':      { bg: dark ? '#0F6E56' : '#1D9E75', fg: '#fff',                        label: 'W'   },
      'web+curl': { bg: dark ? '#185FA5' : '#378ADD', fg: '#fff',                        label: 'W+C' },
      'curl':     { bg: dark ? '#cba452' : '#FFB74D', fg: dark ? '#412402' : '#412402',  label: 'C'   },
      'web-fail': { bg: dark ? '#A32D2D' : '#F06292', fg: '#fff',                        label: 'W✗'  },
      'none':     { bg: dark ? '#D4537E' : '#FF8A65', fg: '#fff',                        label: '✗'   },
    };
    return map[surface] || { bg: dark ? '#363634' : '#d0cec7', fg: 'inherit', label: '' };
  }
  // Column tier background tint for readability grouping
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
      { surface: 'web',      desc: [C('web'), '-only text extraction: readable, but truncated'] },
      { surface: 'web+curl', desc: [C('web'), ' + ', C('curl'), ' path with ', C('web'), ' limits reported'] },
      { surface: 'curl',     desc: [C('curl'), '-only raw HTTP body: readability architecture-dependent'] },
      { surface: 'web-fail', desc: [C('web'), ' attempted, no usable content: cache miss / DNS / 0 bytes'] },
      { surface: 'none',     desc: ['no usable content retrieved'] },
    ];
    return e('table', {style:{borderCollapse:'collapse', fontSize:11, marginTop:0}},
      e('tbody', null, items.map(function(item) {
        var c = getColors(dark, item.surface);
        return e('tr', {key:item.surface},
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
        'Columns grouped left-to-right by content accessibility: static pages where any path returns readable content; large static HTML where ', C('web'), ' truncates but ', C('curl'), ' is readable; JS-rendered or SPAs where ', C('curl'), ' returns text-less shell. ',
        C('W'), ' = ', C('web'), ' only; ', C('W+C'), ' = both surfaces; ', C('C'), ' = ', C('curl'), ' only; ', C('W✗'), ' = ', C('web'), ' attempted, but no content; ', C('✗'), ' = complete failure. ',
        C('SC-3'), ' has 21 runs; extra ', C('GPT-5.5 High'), ' run included in ', C('High'), ' row. Hover over cells for retrieval path details.'
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

    // Build rows: for each level, emit a level-header row then one row per model
    var rows = [];
    LEVELS.forEach(function(level) {
      // level header row
      rows.push({ type: 'level-header', level: level });
      MODELS.forEach(function(model) {
        rows.push({ type: 'data', model: model, level: level, key: model + ':' + level });
      });
    });

    return e('div', {className:'cdx2-wrap'},
      e('table', {className:'cdx2'},
        // ── thead ──────────────────────────────────────────────────────
        e('thead', null,
          e('tr', null,
            e('th', {className:'cdx2-rh', style:{minWidth:labelW, color:tc}},
              'LLM / Intelligence'
            ),
            cols.map(function(col) {
              return e('th', {key:col.id, title:col.note,
                style:{color:tc, background:getTierHeaderBg(dark, col.tier)}},
                col.l1,
                e('span', {className:'cdx2-sub'}, col.l2)
              );
            })
          ),
          // tier label row — one spanning cell per tier group, centered
          e('tr', null,
            e('th', {className:'cdx2-rh', style:{color:tc, fontSize:9, opacity:0.4,
              fontWeight:400, paddingBottom:4}},''),
            (function() {
              // Build groups: [{tier, startId, count}]
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
        // ── tbody ──────────────────────────────────────────────────────
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
              e('td', {className:'cdx2-rl cdx2-model', style:{color:tc, maxWidth:labelW, width:labelW}},
                MODEL_LABELS[row.model]
              ),
              cols.map(function(col) {
                var surface = (runs[col.id] || {})[rowKey];
                if (!surface) {
                  return e('td', {key:col.id},
                    e('div', {style:{
                      width:cellW, height:cellH, margin:'1px auto',
                      borderRadius:3,
                      background: dark ? '#2a2a28' : '#e0e0de'
                    }})
                  );
                }
                var c = getColors(dark, surface);
                var tip = col.l1 + ' · ' + MODEL_LABELS[row.model] + ' ' +
                  LEVEL_LABELS[row.level] + '\n' + SURFACE_NOTE[surface];
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
        e('p', {className:'cdx2-hint'}, '\u2197 click to expand')
      ),
      e('div', {style:{display:'flex', gap:28, alignItems:'flex-start',
        flexWrap:'wrap', marginTop:10, justifyContent:'center'}},
        e('div', {style:{flexShrink:0}}, e(LegendTable, {isDark:dark})),
        e('div', {style:{flex:1, maxWidth:460}}, e(NoteBlock, {isDark:dark}))
      ),
      isOpen && e('div', {
        className:'cdx2-overlay',
        onClick:function(ev){ if (ev.target===ev.currentTarget) setOpen(false); }
      },
        e('div', {className:'cdx2-overlay-inner',
          style:{background:lbBg, color:lbText, width:'99vw'}},
          e('button', {className:'cdx2-close', style:{color:lbText},
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

  var root = ReactDOM.createRoot(document.getElementById('cdx-hm2-root'));
  root.render(e(App));
})();
</script>
{% endraw %}

While `curl` is an appropriate choice to calculate metrics for some URLs, a prompt with context-specific questions - summarize a section, locate a specific value in
the documentation - may have produced a different signal. This track instead uncovers a proxy: agents that used `web` long enough to traverse page text completely
performed something closer to reading prose, as in, accessed semantic context, but agents that pivoted to `curl` may have retrieved code they never processed
as text.

The column grouping makes the practitioner-relevant question legible: agents working with pages in the left two groups had readable content to process regardless of
toolchain. Agents working with pages in the right group - `EC-1`'s SPA extraction at ~10% of raw, `BL-3`'s JS-rendered tutorial body absent from every fetch,
`SC-2`'s CSP-nonce-gated app shell - retrieved bytes but perhaps didn't meaningfully read regardless of intelligence level or method. Depending on LLM-version,
intelligence level, and page architecture, the `curl`-only cells sometimes represent the highest task effort with the lowest content accessibility.

---

## Truncation Analysis

{: .table-findings}
| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`web` returns line-indexed rendered text extraction window, not full page** | All tests | Returns a line-numbered, HTML-to-text-extracted viewport; `wordlim: 200` in output across `BL-1`, `OP-1`, `SC-3`, `SC-4`; `Total lines: N` reported for most URLs | **Output chars on `web` path reflect viewport depth, not retrieval ceiling; `curl` only path to raw HTTP body** |
| 2 | **No fixed character or token ceiling detected on `curl` path** | `BL-1`<br>`BL-3`<br>`OP-1` `OP-4` `SC-3` | `BL-3`:`GPT-5.2 Medium` largest valid fetch ~3.1M chars; `OP-4`:`GPT-5.5 Low` ~514,092 chars in 27 seconds with 8% context | **Char/token constraint LLM-version-gated access, not architecturally defined** |
| 3 | **Three independent truncation layers disambiguated** | `BL-1` `EC-6` `OP-4` | `BL-1`: `GPT-5.4 Low` first isolated all three: `web` window, terminal display cap, underlying HTTP body; `EC-6` confirmed ~12,970-token display cap independent of file size; `OP-4`:`GPT-5.4 Extra High` named all three layers | **Self-reported truncation tool-dependent; agents frequently report _"no truncation"_ for `curl` while `web` truncation noted in passing or implied** |
| 4 | **`curl` escalation capability LLM-version-gated, not intelligence-level-gated for newer versions** | `BL-1`<br>`BL-3`<br>`OP-4` `SC-3` | `GPT-5.2` requires `High`+ for `curl`;<br>`GPT-5.4` escalates at `Low`; `GPT-5.5` skips `web` entirely at all levels; within `GPT-5.4-Mini`, DNS sandbox failures suppressed escalation | **`curl`-first behavior LLM-version property; capability threshold collapsed from `High` to `Low` between `GPT-5.2` and `GPT-5.4`** |
| 5 | **Higher intelligence levels don't produce better retrieval outcomes, `Extra High` shows cost/yield regression** | `BL-1` `EC-1` `OP-4` `SC-2` | `GPT-5.4-Mini Extra High` spent 85 seconds on a 3-part fetch strategy matching `Medium`'s single-fetch result; `EC-1`:`GPT-5.2 Extra High` looped ~48 minutes on 113 `web` calls without escalating;<br>`OP-4`:`GPT-5.5 Low` retrieved 514 KB in 27 seconds vs `GPT-5.2 High` looping ~14 minutes at 45% context | **Intelligence level governs tool sophistication, not task success; `Extra High` consistently produces diminishing returns against `web`-focused prompt** |
| 6 | **Session contamination persistent confound** | `BL-1`<br>`BL-2`<br>`BL-3` `EC-1` `EC-6` `SC-2` `SC-4` | `Documents/Codex` persists across sessions; artifact filenames reused across runs confirmed in 20+ cases;<br>`BL-2`:`GPT-5.5 High` likely read prior session artifact rather than fetching;<br>`BL-1`:`GPT-5.4 Extra High` completed task in 42 seconds vs `Low`'s ~2 minutes due to reuse | **Intelligence level not independent variable within shared sessions** |
| 7 | **JS-rendered pages produce a structural retrieval failure, not a truncation event** | `BL-3` `SC-2` | `SC-2`: Next.js / Netlify - `web` returns a consistent 142-line pre-hydration shell; nonce-based CSP, `no-store` cache policy prevent JS execution on any path; `BL-3` tutorial body absent from static extraction at a reproducible structural position `L385-L389` | **Neither `web` nor `curl` returns content for CSP-gated JS-rendered pages - fundamental retrieval barrier not addressable by escalation** |
| 8 | **`Cache Miss` is systematic for large, mutable payloads** | `EC-6` | 17 of 20 `web`-runs on raw GitHub URL received `Cache Miss (no content retrieved)`; smaller `raw.githubusercontent.com` sized doc confirmed host isn't fully blocked; no run investigated or diagnosed failure before pivoting to `curl` | **Failure is URL-size-class-specific to raw GitHub payloads; agents report what succeeded, not what failed** |
| 9 | **`web` window LLM-version-correlated on same URL** | `OP-2` `OP-4` `SC-3` | `OP-2`:`L317` dominant cutpoint for<br>`GPT-5.2-5.4`; `L590` for `GPT-5.5`;<br>`OP-4`:`L237` for `GPT-5.2-5.4`; `L616` for `GPT-5.5 Extra High`; `SC-3`:`L266` dominant for `GPT-5.2`/`5.4-Mini`; `L353` for<br>`GPT-5.3-Codex`/`5.5` | **Viewport window scales across LLM generations; same URL returns a larger first-fetch window in newer LLM versions** |
| 10 | **`wordlim: 200` soft default, not hard cap** | `BL-1` `OP-1` `OP-4` `SC-3` `SC-4` | `SC-1`:`GPT-5.3-Codex Extra High` named `response_length` short vs long parameter distinction - short mode stopping ~`L362`, long mode ~`L478`; `BL-3`:`GPT-5.4 Extra High` re-issued `web` in _"long response mode,"_ localized truncation boundary to `L385-L389`; `SC-3`: `GPT-5.4 Extra High` observed both `L266`, `L353` in a session by varying response length settings;<br>`SC-4` shows two-stage `L316`→`L657` pattern consistent with narrow-then-wider window sequence | **`wordlim: 200` pattern agent-dependent, not fixed infrastructure ceiling, not consistently named** |
| 11 | **`multi_tool_use.parallel` exclusive to `GPT-5.4 Extra High`-`GPT-5.5`** | Most tests | Not observed in `GPT-5.2` or `GPT-5.3-Codex` at any intelligence level; first appeared in `GPT-5.4 Extra High`; consistent across all `GPT-5.5` levels | **Parallel tool invocation is LLM-version capability, not an intelligence-level default** |

## Retrieval Outcomes

Output chars on the `web` surface aren't a retrieval ceiling metric, but reflect how far the agent traversed through a line-indexed renderer.
Agents wrote-saved a variety of artifacts unprompted in which `curl` body size was partially observable. Raw tracks intend document precise
artifact measurements. Rows below organized by page architecture:<br> _raw files → static HTML → reference/wiki → JS-rendered/SPA_

{: .table-perception}
| **Test** | **Expected** | **Received** | **Content Accessibility** | **Agent Characterization** |
| --- | --- | --- | --- | --- |
| **[`EC-3`](https://httpbin.org/redirect/5)<br>Redirect JSON** | ~2 KB | `web`: 660 chars<br>`curl`: 254 bytes | 100% | _Complete_: `web` pipeline likely pads response with wrapper text; `curl` returns raw body; neither represents truncation |
| **[`BL-2`](https://www.mongodb.com/docs/manual/reference/change-events/create.md)<br>Mixed HTML Markdown** | ~20 KB | `200`: 6,024<br>char count<br>`400`: 95<br>char count | `200`: 100% | _Complete, but misidentified_: mixed format caused persistent false truncation reports across all LLMs; actual size consistently confirmed - 6,024 chars |
| **[`EC-6`](https://raw.githubusercontent.com/agent-ecosystem/agent-docs-spec/main/SPEC.md)<br>Raw GitHub Markdown** | ~60 KB | `web`:<br>`Cache Miss`<br>`curl`: 91,869 char count | ~100% body;<br>display cap | _No retrieval truncation_: `web` `Cache Miss` error systematic while `curl`'s complete; display truncation at ~12,970 tokens is a terminal rendering cap, not a fetch limit |
| **[`SC-4`](https://www.markdownguide.org/basic-syntax/)<br>Markdown Guide** | ~30 KB | `web`: `L316/L657`<br>`curl`: 64,527 char count | `curl`: 100%<br>`web`: 50% | _Complete via `curl`_: `web` delivers a pageable line-indexed window; `L316/L657` cutpoints land mid-document at non-structural boundaries |
| **[`SC-1`](https://ai.google.dev/gemini-api/docs/url-context)<br>Gemini<br>API Docs** | ~40 KB | `web`:<br>18–33K<br> char range<br>`curl`: ~121.4K<br>char count | `curl`: 100%<br>`web`: 15-27% | _Complete via `curl`_: `web` `L362` short-mode ceiling confirmed; second fetch recovered through `L478`; truncation lands on page-content notice, not a structural boundary |
| **[`OP-2`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)<br>MDN<br>Docs** | ~120 KB | `web`: `L317/590` `curl`: 240, 370 char count | `curl`: 100%<br>`web`: 13-25% | _Complete via `curl`_: `web` line window LLM-version-correlated; both cutpoints land mid-sentence at non-structural positions |
| **[`BL-1`](https://www.mongodb.com/docs/manual/reference/change-events/create/)<br>MongoDB Docs** | ~85 KB | `web`:<br>1.6–61K~<br>19K–85K<br>`curl`: 505,339 char count | `curl`: 100%<br>`web`:<br>~0.3–17% | _LLM-intelligence-tool-dependent_: `GPT-5.2`-`5.3-Codex` lower range, `5.4-Mini` upper range;`web` truncated at extraction's line boundary, suggesting tool ceiling as content beyond `L140/L477` not retrieved, cutpoint `L477` consistent across `5.2 Medium`, `5.3-Codex High`-`Extra High`; `5.4-5` use of `curl` returned full response body, diambiguated truncation layers |
| **[`OP-4`](https://spec.commonmark.org/0.31.2/)<br>CommonMark Spec** | ~500 KB | `web`: `L237-616`<br>`curl`: 514,092 char count | `curl`: 100%<br>`web`: 2-3% | _Complete via `curl`_: `GPT-5.2-4` stopped ~`L237` while `5.5 Extra High` stopped ~`L616`; `GPT-5.2 High` looped 14m24s at 45% context; three truncation layers identified in a single run |
| **[`OP-1`](https://en.wikipedia.org/wiki/Machine_learning#History)<br>Wikipedia<br>with URL Fragment** | ~40 KB | `web`: `L305/552` `curl`: 693,475 char count | `curl`: 100%<br>`web`: ~0.5-4% | _Complete via `curl`_: `#History` silently dropped by both tools; full article retrieved without targeted section; `web` consistent cutpoint `L552`, content accessibility calculated by token estimates |
| **[`SC-3`](https://en.wikipedia.org/wiki/List_of_countries_by_population)<br>Wikipedia<br>Table-Heavy** | ~100 KB | `web`: `L266/309/353`<br>`curl`: 785,605 char count | `curl`: 100%<br>`web`: 1-3% | _Complete via `curl`_: `web` window varies across LLM versions; `wordlim: 200` confirmed as soft default; three distinct cutoff points across 21 runs rules out an architecturally fixed ceiling |
| **[`EC-1`](https://ai.google.dev/gemini-api/docs)<br>Gemini<br>API Docs** | ~100 KB | `web`: 13K–13.4K char range<br>`curl`: 132,894 char count | `curl`: 100%<br>`web`: 10% | _Extraction ratio gap_: `web` consistently delivers 10% of HTML; `GPT-5.2 Extra High` called `web` 113 times for 48m10s, never pivoting to `curl` |
| **[`SC-2`](https://docs.anthropic.com/en/api/messages)<br>Anthropic API Docs** | ~80 KB | `web`: `L142` `curl`:<br>~511K–519K char range | Not accessible | _Incomplete HTML shell, prose absent_: reference prose is JS-hydrated, CSP nonce-gating prevents JS execution on any fetch path; `curl` delivers navigation scaffolding and/or data bundles, not documentation; artifacts include `Loading...` placeholders |
| **[`BL-3`](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/)<br>MongoDB Docs** | ~250 KB | `web`: `L453` `curl`: ~3.1 MB char estimate | Not accessible | _Complete HTML shell, prose absent_: tutorial walkthrough is client-side rendered and not represented in static payload regardless of fetch strategy; documentation body not examined in `web` `L385–L389` extraction |
