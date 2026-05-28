---
layout: default
title: "Key Findings for Codex's Web Search Behavior, GPT-interpreted - Desktop"
permalink: /docs/open-ai-codex/codex-test-findings-desktop
parent: OpenAI Codex
---

# Key Findings for Codex's Web Search Behavior, GPT-interpreted - Desktop

---

## [Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/open-ai-codex-web-search/framework.py)

1. Run `python framework.py --test {test ID} --track codex-interpreted`
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
| **Content<br>Selection<br>Behavior** | _Two-tier retrieval_: `web` returns a line-indexed rendered text extraction, `wordlim: 200`; full content requires `curl` escalation with elevated network permissions |
| **Truncation<br>Pattern** | _Three independent truncation layers_: `web` line-indexed window, LLM/URL dependent - `L237–L657`, `EC-6`'s terminal display cap ~12,970 tokens, and underlying `curl` response |
| **`web`<br>Line-Indexed<br>Window** | _LLM-version-URL-dependent_: agent's choice, varied across sessions - `BL-1`:`L140`, `BL-3`:`L453`, `EC-1`:`L479`, `OP-4`:`L237`, `SC-3`:`L266/L309/L353`, `OP-1`:`L305/L477/L552`, `SC-4`:`L316/L657`, `SC-1`:`L362/L478` |
| **`curl` Escalation** | _Model-version-gated_: `GPT-5.2` requires `Medium`+ intelligence; `GPT-5.3-Codex` typically `Medium`+; `GPT-5.4` escalates at `Low`; `GPT-5.5` bypasses `web.open` entirely at all levels |
| **Session Contamination** | _Significant confound_: workspace artifacts from prior sessions persist across runs in `Documents/Codex`; `/private/tmp` clears between sessions; filename reuse observed across 42 / 261 runs |
| **JS-Rendered Pages** | _Structural retrieval failure_: `SC-2` (Next.js/Netlify) and `BL-3` (Next.js/Gatsby) tutorial body absent from static extraction regardless of model or intelligence level; `curl` returns app shell only |
| **`raw.githubusercontent.com` Cache Miss** | _Systematic_: `web.open` hit `Cache Miss` on the raw GitHub URL in `EC-6` across all 17 runs that attempted it; smaller `raw.githubusercontent.com` files confirmed loadable, ruling out a blanket host block |
| **Self-reported Completeness** | _Curl-anchored_: agents conflate `curl` body completeness with overall retrieval completeness; `web.open` truncation consistently underreported in summary assessments |

## Results Details

| | |
| --- | --- |
| **Track** | `T1` GPT-interpreted, Codex IDE |
| **Agents Observed** | `GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`, `GPT-5.4`, `GPT-5.5` |
| **Intelligence Levels** | `Low`, `Medium`, `High`, `Extra High` |
| **Total Runs** | 261 |
| **Distinct URLs** | 11 |
| **Input Size Range** | ~660 chars (`EC-3`) – ~3.1 MB (`BL-3`) |
| **Truncation Events** | 42 / 261 |
| **Average Output Size** | 351,961 chars |
| **Output Size Range** | 95 – 3,103,342 chars |
| **Average Token Count** | 88,489 tokens |
| **Token Count Range** | 24 – 835,000 tokens |
| **Workspace Substitution** | 2 / 261 runs (confirmed); contamination risk flagged in ~40 additional runs |
| **`curl` Escalation** | Dominant full-document retrieval path; present in ~180 / 261 runs |
| **`GPT-5.5` `web.open` Bypass** | All four intelligence levels bypassed `web.open` on at least one URL |
| **Parallel Tool Use** | `multi_tool_use.parallel` exclusive to `GPT-5.4 Extra High` and all `GPT-5.5` runs |
| **Runaway Failure** | `EC-1` `GPT-5.2 Extra High`: 113 web searches, 48m10s, context auto-compacted |
| **`SC-2` URL** | Next.js CSP-nonce-gated SPA; `web.open` returns 142-line loading shell; no run retrieved API reference text |

## Retrieval Strategy by Model Version and Intelligence Level

Agents consistently used `web.open` as a first fetch attempt, but whether they escalated to `curl` — and at what intelligence level — is the primary behavioral variable in this dataset. The heatmap below shows retrieval outcome per run, organized by test ID (ascending by actual page size) and model family × intelligence level.

{% raw %}
<div id="cdx-hm-root"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>

<style>
.cdx-hm-wrap { overflow-x: auto; }
table.cdx-hm { border-collapse: collapse; width: 100%; }
table.cdx-hm th { font-size: 11px; font-weight: 500; padding: 4px 5px; text-align: center; white-space: nowrap; color: inherit; }
table.cdx-hm th.cdx-row-head { text-align: left; }
table.cdx-hm th .cdx-url-note { font-weight: 400; font-size: 10px; opacity: 0.55; }
table.cdx-hm td { padding: 2px 3px; text-align: center; }
table.cdx-hm td.cdx-row-label { font-size: 11px; text-align: left; padding-left: 0; white-space: nowrap; font-weight: 400; padding-right: 6px; color: inherit; }
.cdx-hint { font-size: 11px; opacity: 0.5; margin-top: 6px; cursor: pointer; color: inherit; }
.cdx-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.75);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.cdx-overlay-inner {
  border-radius: 10px;
  padding: 24px 28px;
  max-width: 98vw;
  max-height: 92vh;
  overflow: auto;
  position: relative;
}
.cdx-close {
  position: absolute; top: 12px; right: 14px;
  background: none; border: none; font-size: 20px;
  cursor: pointer; opacity: 0.5; line-height: 1;
}
.cdx-close:hover { opacity: 1; }
.cdx-legend { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; font-size: 11px; align-items: center; opacity: 0.8; }
.cdx-legend-swatch { width: 12px; height: 12px; border-radius: 2px; display: inline-block; flex-shrink: 0; border: 0.5px solid rgba(128,128,128,0.3); }
.cdx-note { font-size: 12px; margin-top: 10px; line-height: 1.6; opacity: 0.7; }
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

  // Tests ordered by actual page size ascending
  var testOrder = [
    {id:'EC-3',  l1:'EC-3',  l2:'0.7 KB' },
    {id:'BL-2',  l1:'BL-2',  l2:'6 KB'   },
    {id:'SC-4',  l1:'SC-4',  l2:'65 KB'  },
    {id:'EC-6',  l1:'EC-6',  l2:'92 KB'  },
    {id:'EC-1',  l1:'EC-1',  l2:'133 KB' },
    {id:'SC-1',  l1:'SC-1',  l2:'121 KB' },
    {id:'BL-1',  l1:'BL-1',  l2:'505 KB' },
    {id:'SC-2',  l1:'SC-2',  l2:'512 KB' },
    {id:'OP-1',  l1:'OP-1',  l2:'696 KB' },
    {id:'SC-3',  l1:'SC-3',  l2:'786 KB' },
    {id:'BL-3',  l1:'BL-3',  l2:'3.1 MB' },
    {id:'OP-2',  l1:'OP-2',  l2:'240 KB' },
    {id:'OP-4',  l1:'OP-4',  l2:'514 KB' },
  ];

  // OUTCOME CODES:
  // pass      = full doc retrieved (curl or valid path)
  // partial   = partial retrieval / web.open only / truncated
  // fail      = retrieval failure (0 bytes, 400, loop, etc.)
  // invalid   = HTTP 404 or known bad measurement
  // N/A       = not run

  var runs = [
    // EC-3 (660 chars - all pass, tiny payload)
    {test:'EC-3', agent:'5.2-L',    outcome:'pass'},
    {test:'EC-3', agent:'5.2-M',    outcome:'pass'},
    {test:'EC-3', agent:'5.2-H',    outcome:'pass'},
    {test:'EC-3', agent:'5.2-XH',   outcome:'pass'},
    {test:'EC-3', agent:'5.3-L',    outcome:'pass'},
    {test:'EC-3', agent:'5.3-M',    outcome:'pass'},
    {test:'EC-3', agent:'5.3-H',    outcome:'pass'},
    {test:'EC-3', agent:'5.3-XH',   outcome:'pass'},
    {test:'EC-3', agent:'5.4m-L',   outcome:'pass'},
    {test:'EC-3', agent:'5.4m-M',   outcome:'pass'},
    {test:'EC-3', agent:'5.4m-H',   outcome:'pass'},
    {test:'EC-3', agent:'5.4m-XH',  outcome:'pass'},
    {test:'EC-3', agent:'5.4-L',    outcome:'pass'},
    {test:'EC-3', agent:'5.4-M',    outcome:'pass'},
    {test:'EC-3', agent:'5.4-H',    outcome:'pass'},
    {test:'EC-3', agent:'5.4-XH',   outcome:'pass'},
    {test:'EC-3', agent:'5.5-L',    outcome:'pass'},
    {test:'EC-3', agent:'5.5-M',    outcome:'pass'},
    {test:'EC-3', agent:'5.5-H',    outcome:'pass'},
    {test:'EC-3', agent:'5.5-XH',   outcome:'pass'},
    // BL-2 (6 KB)
    {test:'BL-2', agent:'5.2-L',    outcome:'fail'},
    {test:'BL-2', agent:'5.2-M',    outcome:'pass'},
    {test:'BL-2', agent:'5.2-H',    outcome:'pass'},
    {test:'BL-2', agent:'5.2-XH',   outcome:'pass'},
    {test:'BL-2', agent:'5.3-L',    outcome:'fail'},
    {test:'BL-2', agent:'5.3-M',    outcome:'pass'},
    {test:'BL-2', agent:'5.3-H',    outcome:'pass'},
    {test:'BL-2', agent:'5.3-XH',   outcome:'pass'},
    {test:'BL-2', agent:'5.4m-L',   outcome:'partial', note:'rendered view, curl DNS fail'},
    {test:'BL-2', agent:'5.4m-M',   outcome:'pass'},
    {test:'BL-2', agent:'5.4m-H',   outcome:'pass'},
    {test:'BL-2', agent:'5.4m-XH',  outcome:'pass'},
    {test:'BL-2', agent:'5.4-L',    outcome:'partial', note:'false truncation report'},
    {test:'BL-2', agent:'5.4-M',    outcome:'fail'},
    {test:'BL-2', agent:'5.4-H',    outcome:'pass'},
    {test:'BL-2', agent:'5.4-XH',   outcome:'pass'},
    {test:'BL-2', agent:'5.5-L',    outcome:'pass'},
    {test:'BL-2', agent:'5.5-M',    outcome:'pass'},
    {test:'BL-2', agent:'5.5-H',    outcome:'pass'},
    {test:'BL-2', agent:'5.5-XH',   outcome:'pass'},
    // SC-4 (65 KB)
    {test:'SC-4', agent:'5.2-L',    outcome:'partial'},
    {test:'SC-4', agent:'5.2-M',    outcome:'pass'},
    {test:'SC-4', agent:'5.2-H',    outcome:'pass'},
    {test:'SC-4', agent:'5.2-XH',   outcome:'pass'},
    {test:'SC-4', agent:'5.3-L',    outcome:'pass', note:'bypassed web.open entirely'},
    {test:'SC-4', agent:'5.3-M',    outcome:'pass'},
    {test:'SC-4', agent:'5.3-H',    outcome:'pass'},
    {test:'SC-4', agent:'5.3-XH',   outcome:'pass'},
    {test:'SC-4', agent:'5.4m-L',   outcome:'partial', note:'curl 0 bytes, believed footer reached'},
    {test:'SC-4', agent:'5.4m-M',   outcome:'pass'},
    {test:'SC-4', agent:'5.4m-H',   outcome:'pass'},
    {test:'SC-4', agent:'5.4m-XH',  outcome:'pass'},
    {test:'SC-4', agent:'5.4-L',    outcome:'pass'},
    {test:'SC-4', agent:'5.4-M',    outcome:'pass'},
    {test:'SC-4', agent:'5.4-H',    outcome:'pass'},
    {test:'SC-4', agent:'5.4-XH',   outcome:'pass'},
    {test:'SC-4', agent:'5.5-L',    outcome:'pass', note:'bypassed web.open entirely'},
    {test:'SC-4', agent:'5.5-M',    outcome:'pass'},
    {test:'SC-4', agent:'5.5-H',    outcome:'pass'},
    {test:'SC-4', agent:'5.5-XH',   outcome:'pass'},
    // EC-6 (92 KB - raw GitHub, cache miss on web.open)
    {test:'EC-6', agent:'5.2-L',    outcome:'pass', note:'display trunc ~20470 tok'},
    {test:'EC-6', agent:'5.2-M',    outcome:'pass'},
    {test:'EC-6', agent:'5.2-H',    outcome:'pass'},
    {test:'EC-6', agent:'5.2-XH',   outcome:'pass'},
    {test:'EC-6', agent:'5.3-L',    outcome:'pass', note:'bypassed web.open'},
    {test:'EC-6', agent:'5.3-M',    outcome:'pass'},
    {test:'EC-6', agent:'5.3-H',    outcome:'pass'},
    {test:'EC-6', agent:'5.3-XH',   outcome:'pass'},
    {test:'EC-6', agent:'5.4m-L',   outcome:'pass'},
    {test:'EC-6', agent:'5.4m-M',   outcome:'pass'},
    {test:'EC-6', agent:'5.4m-H',   outcome:'pass'},
    {test:'EC-6', agent:'5.4m-XH',  outcome:'pass'},
    {test:'EC-6', agent:'5.4-L',    outcome:'pass'},
    {test:'EC-6', agent:'5.4-M',    outcome:'pass', note:'display trunc ~12970 tok'},
    {test:'EC-6', agent:'5.4-H',    outcome:'pass', note:'display trunc ~12970 tok'},
    {test:'EC-6', agent:'5.4-XH',   outcome:'pass', note:'display trunc ~12970 tok'},
    {test:'EC-6', agent:'5.5-L',    outcome:'pass', note:'bypassed web.open'},
    {test:'EC-6', agent:'5.5-M',    outcome:'pass', note:'display trunc confirmed'},
    {test:'EC-6', agent:'5.5-H',    outcome:'pass', note:'display trunc confirmed'},
    {test:'EC-6', agent:'5.5-XH',   outcome:'pass', note:'bypassed web.open'},
    // EC-1 (133 KB SPA)
    {test:'EC-1', agent:'5.2-L',    outcome:'pass'},
    {test:'EC-1', agent:'5.2-M',    outcome:'partial', note:'web.open only, ~13K chars'},
    {test:'EC-1', agent:'5.2-H',    outcome:'pass'},
    {test:'EC-1', agent:'5.2-XH',   outcome:'fail', note:'113 searches, runaway 48m'},
    {test:'EC-1', agent:'5.3-L',    outcome:'partial', note:'curl 0 bytes'},
    {test:'EC-1', agent:'5.3-M',    outcome:'pass'},
    {test:'EC-1', agent:'5.3-H',    outcome:'pass'},
    {test:'EC-1', agent:'5.3-XH',   outcome:'pass'},
    {test:'EC-1', agent:'5.4m-L',   outcome:'partial', note:'web.open extraction not isolated'},
    {test:'EC-1', agent:'5.4m-M',   outcome:'pass', note:'Browser/Playwright path'},
    {test:'EC-1', agent:'5.4m-H',   outcome:'pass', note:'Browser/Playwright path'},
    {test:'EC-1', agent:'5.4m-XH',  outcome:'partial', note:'web.open only, no curl'},
    {test:'EC-1', agent:'5.4-L',    outcome:'pass'},
    {test:'EC-1', agent:'5.4-M',    outcome:'pass'},
    {test:'EC-1', agent:'5.4-H',    outcome:'pass'},
    {test:'EC-1', agent:'5.4-XH',   outcome:'partial', note:'web.open only, ~13K chars isolated'},
    {test:'EC-1', agent:'5.5-L',    outcome:'pass', note:'bypassed web.open'},
    {test:'EC-1', agent:'5.5-M',    outcome:'pass', note:'bypassed web.open'},
    {test:'EC-1', agent:'5.5-H',    outcome:'pass'},
    {test:'EC-1', agent:'5.5-XH',   outcome:'pass', note:'bypassed web.open'},
    // SC-1 (121 KB)
    {test:'SC-1', agent:'5.2-L',    outcome:'pass'},
    {test:'SC-1', agent:'5.2-M',    outcome:'pass'},
    {test:'SC-1', agent:'5.2-H',    outcome:'partial', note:'curl DNS blocked, web.open only'},
    {test:'SC-1', agent:'5.2-XH',   outcome:'pass'},
    {test:'SC-1', agent:'5.3-L',    outcome:'pass'},
    {test:'SC-1', agent:'5.3-M',    outcome:'pass'},
    {test:'SC-1', agent:'5.3-H',    outcome:'pass'},
    {test:'SC-1', agent:'5.3-XH',   outcome:'pass'},
    {test:'SC-1', agent:'5.4m-L',   outcome:'partial', note:'curl DNS blocked, two-fetch web.open'},
    {test:'SC-1', agent:'5.4m-M',   outcome:'partial', note:'curl DNS blocked'},
    {test:'SC-1', agent:'5.4m-H',   outcome:'partial', note:'curl DNS blocked, browser fallback'},
    {test:'SC-1', agent:'5.4m-XH',  outcome:'partial', note:'curl DNS blocked, browser playwright'},
    {test:'SC-1', agent:'5.4-L',    outcome:'partial', note:'curl not invoked'},
    {test:'SC-1', agent:'5.4-M',    outcome:'pass'},
    {test:'SC-1', agent:'5.4-H',    outcome:'pass'},
    {test:'SC-1', agent:'5.4-XH',   outcome:'pass'},
    {test:'SC-1', agent:'5.5-L',    outcome:'pass'},
    {test:'SC-1', agent:'5.5-M',    outcome:'pass'},
    {test:'SC-1', agent:'5.5-H',    outcome:'pass'},
    {test:'SC-1', agent:'5.5-XH',   outcome:'pass'},
    // BL-1 (505 KB - model-stratified curl escalation)
    {test:'BL-1', agent:'5.2-L',    outcome:'partial', note:'wordlim:200 cap ~1600 chars'},
    {test:'BL-1', agent:'5.2-M',    outcome:'partial', note:'L477 cut, gap-aware, no pagination'},
    {test:'BL-1', agent:'5.2-H',    outcome:'pass', note:'curl escalation, 505K'},
    {test:'BL-1', agent:'5.2-XH',   outcome:'pass', note:'curl, 18 web searches'},
    {test:'BL-1', agent:'5.3-L',    outcome:'partial', note:'L140 cut, open→find template'},
    {test:'BL-1', agent:'5.3-M',    outcome:'partial', note:'L140 cut identical to Low'},
    {test:'BL-1', agent:'5.3-H',    outcome:'partial', note:'L477 cut, meta-ceiling reasoning'},
    {test:'BL-1', agent:'5.3-XH',   outcome:'partial', note:'L477 cut, Node REPL'},
    {test:'BL-1', agent:'5.4m-L',   outcome:'partial', note:'web.open line window ~19K'},
    {test:'BL-1', agent:'5.4m-M',   outcome:'partial', note:'web.open ~85K, identical tail'},
    {test:'BL-1', agent:'5.4m-H',   outcome:'partial', note:'web.open ~85K, fewer tool calls'},
    {test:'BL-1', agent:'5.4m-XH',  outcome:'partial', note:'3-part fetch strategy, 85s runtime'},
    {test:'BL-1', agent:'5.4-L',    outcome:'pass', note:'curl default, 3 trunc layers'},
    {test:'BL-1', agent:'5.4-M',    outcome:'pass', note:'curl default, stable profile'},
    {test:'BL-1', agent:'5.4-H',    outcome:'pass', note:'curl, DNS sandbox retry'},
    {test:'BL-1', agent:'5.4-XH',   outcome:'pass', note:'curl, session contamination flag'},
    {test:'BL-1', agent:'5.5-L',    outcome:'pass', note:'curl primary, no web.open'},
    {test:'BL-1', agent:'5.5-M',    outcome:'pass', note:'curl primary, session contam flag'},
    {test:'BL-1', agent:'5.5-H',    outcome:'pass', note:'curl primary, session contam flag'},
    {test:'BL-1', agent:'5.5-XH',   outcome:'pass', note:'curl, parallel tools, session contam'},
    // SC-2 (512 KB Next.js SPA - structural retrieval failure)
    {test:'SC-2', agent:'5.2-L',    outcome:'partial', note:'JS render wall, loading shell'},
    {test:'SC-2', agent:'5.2-M',    outcome:'partial', note:'wordlim:200, redirect detected'},
    {test:'SC-2', agent:'5.2-H',    outcome:'pass', note:'curl, Next.js shell ~512K'},
    {test:'SC-2', agent:'5.2-XH',   outcome:'fail', note:'curl DNS fail, 1hr+ loop'},
    {test:'SC-2', agent:'5.3-L',    outcome:'partial', note:'curl 0 bytes, web.open shell'},
    {test:'SC-2', agent:'5.3-M',    outcome:'pass', note:'curl escalated, 512K shell'},
    {test:'SC-2', agent:'5.3-H',    outcome:'pass'},
    {test:'SC-2', agent:'5.3-XH',   outcome:'pass', note:'headers saved, CSP nonce confirmed'},
    {test:'SC-2', agent:'5.4m-L',   outcome:'pass', note:'most efficient, 57s, 8% ctx'},
    {test:'SC-2', agent:'5.4m-M',   outcome:'partial', note:'curl DNS fail, 142-line L141'},
    {test:'SC-2', agent:'5.4m-H',   outcome:'partial', note:'browser, innerText 15K'},
    {test:'SC-2', agent:'5.4m-XH',  outcome:'pass'},
    {test:'SC-2', agent:'5.4-L',    outcome:'partial', note:'web.open only, truncation named'},
    {test:'SC-2', agent:'5.4-M',    outcome:'pass', note:'display vs retrieval trunc distd'},
    {test:'SC-2', agent:'5.4-H',    outcome:'partial', note:'web.open only, 142-line confirmed'},
    {test:'SC-2', agent:'5.4-XH',   outcome:'pass', note:'Loading block mapped L28-L84'},
    {test:'SC-2', agent:'5.5-L',    outcome:'pass', note:'browser screenshot confirms loading'},
    {test:'SC-2', agent:'5.5-M',    outcome:'pass', note:'bypassed web.open, curl only'},
    {test:'SC-2', agent:'5.5-H',    outcome:'pass', note:'perl UTF-8, 0 fences confirmed'},
    {test:'SC-2', agent:'5.5-XH',   outcome:'partial', note:'web.open only, Loading L23'},
    // OP-1 (696 KB Wikipedia + fragment)
    {test:'OP-1', agent:'5.2-L',    outcome:'pass', note:'fragment-aware, curl direct'},
    {test:'OP-1', agent:'5.2-M',    outcome:'partial', note:'web.open L303, wordlim:200, 9m'},
    {test:'OP-1', agent:'5.2-H',    outcome:'pass'},
    {test:'OP-1', agent:'5.2-XH',   outcome:'pass', note:'37 searches, History regex isolated'},
    {test:'OP-1', agent:'5.3-L',    outcome:'partial', note:'lineno pagination, missing middle'},
    {test:'OP-1', agent:'5.3-M',    outcome:'pass'},
    {test:'OP-1', agent:'5.3-H',    outcome:'pass', note:'L305/L551 cutpoints named'},
    {test:'OP-1', agent:'5.3-XH',   outcome:'pass'},
    {test:'OP-1', agent:'5.4m-L',   outcome:'partial', note:'web.open L305, curl 0 bytes'},
    {test:'OP-1', agent:'5.4m-M',   outcome:'partial', note:'wordlim:200, 3-turn pagination'},
    {test:'OP-1', agent:'5.4m-H',   outcome:'pass'},
    {test:'OP-1', agent:'5.4m-XH',  outcome:'partial', note:'L552/L553 handoff, no curl'},
    {test:'OP-1', agent:'5.4-L',    outcome:'partial', note:'web.open L305, no curl'},
    {test:'OP-1', agent:'5.4-M',    outcome:'pass'},
    {test:'OP-1', agent:'5.4-H',    outcome:'pass'},
    {test:'OP-1', agent:'5.4-XH',   outcome:'pass'},
    {test:'OP-1', agent:'5.5-L',    outcome:'pass', note:'curl only, bypassed web.open'},
    {test:'OP-1', agent:'5.5-M',    outcome:'partial', note:'web.open L552, curl complete'},
    {test:'OP-1', agent:'5.5-H',    outcome:'pass', note:'curl only, bypassed web.open'},
    {test:'OP-1', agent:'5.5-XH',   outcome:'pass'},
    // SC-3 (786 KB Wikipedia)
    {test:'SC-3', agent:'5.2-L',    outcome:'partial', note:'web.run snippets, no curl'},
    {test:'SC-3', agent:'5.2-M',    outcome:'pass'},
    {test:'SC-3', agent:'5.2-H',    outcome:'pass'},
    {test:'SC-3', agent:'5.2-XH',   outcome:'pass', note:'20 searches, triple artifact'},
    {test:'SC-3', agent:'5.3-L',    outcome:'partial', note:'two-fetch start+end, no curl'},
    {test:'SC-3', agent:'5.3-M',    outcome:'pass'},
    {test:'SC-3', agent:'5.3-H',    outcome:'pass'},
    {test:'SC-3', agent:'5.3-XH',   outcome:'pass'},
    {test:'SC-3', agent:'5.4m-L',   outcome:'fail', note:'curl 0 bytes, believed 18K complete'},
    {test:'SC-3', agent:'5.4m-M',   outcome:'partial', note:'L266 correctly identified, no curl'},
    {test:'SC-3', agent:'5.4m-H',   outcome:'pass'},
    {test:'SC-3', agent:'5.4m-XH',  outcome:'pass', note:'text proxy 67K measured separately'},
    {test:'SC-3', agent:'5.4-L',    outcome:'partial', note:'L266, lineno pagination, no curl'},
    {test:'SC-3', agent:'5.4-M',    outcome:'partial', note:'3-point traversal, no curl'},
    {test:'SC-3', agent:'5.4-H',    outcome:'partial', note:'L353, follow-up L1225, no curl'},
    {test:'SC-3', agent:'5.4-XH',   outcome:'pass', note:'L266+L353 both in single session'},
    {test:'SC-3', agent:'5.5-L',    outcome:'pass'},
    {test:'SC-3', agent:'5.5-M',    outcome:'pass'},
    {test:'SC-3', agent:'5.5-H',    outcome:'pass'},
    {test:'SC-3', agent:'5.5-H2',   outcome:'pass'},
    {test:'SC-3', agent:'5.5-XH',   outcome:'pass', note:'custom user-agent, L309 third cutoff'},
    // BL-3 (3.1 MB Next.js tutorial)
    {test:'BL-3', agent:'5.2-L',    outcome:'partial', note:'curl ~299KB anomaly'},
    {test:'BL-3', agent:'5.2-M',    outcome:'pass', note:'curl 3MB'},
    {test:'BL-3', agent:'5.2-H',    outcome:'pass'},
    {test:'BL-3', agent:'5.2-XH',   outcome:'pass'},
    {test:'BL-3', agent:'5.3-L',    outcome:'partial', note:'web.open only, 453-line cap'},
    {test:'BL-3', agent:'5.3-M',    outcome:'partial', note:'web.open only, 453-line cap'},
    {test:'BL-3', agent:'5.3-H',    outcome:'pass'},
    {test:'BL-3', agent:'5.3-XH',   outcome:'pass'},
    {test:'BL-3', agent:'5.4m-L',   outcome:'partial', note:'web.open only, 453-line cap'},
    {test:'BL-3', agent:'5.4m-M',   outcome:'invalid', note:'HTTP 404 fetched'},
    {test:'BL-3', agent:'5.4m-H',   outcome:'invalid', note:'HTTP 404 fetched'},
    {test:'BL-3', agent:'5.4m-XH',  outcome:'invalid', note:'HTTP 404 fetched'},
    {test:'BL-3', agent:'5.4-L',    outcome:'partial', note:'web.open only, 453-line cap'},
    {test:'BL-3', agent:'5.4-M',    outcome:'pass'},
    {test:'BL-3', agent:'5.4-H',    outcome:'pass'},
    {test:'BL-3', agent:'5.4-XH',   outcome:'pass', note:'L385-L389 boundary localized'},
    {test:'BL-3', agent:'5.5-L',    outcome:'pass', note:'curl-first, web.open bypassed'},
    {test:'BL-3', agent:'5.5-M',    outcome:'pass'},
    {test:'BL-3', agent:'5.5-H',    outcome:'pass'},
    {test:'BL-3', agent:'5.5-XH',   outcome:'pass'},
    // OP-2 (240 KB MDN Array)
    {test:'OP-2', agent:'5.2-L',    outcome:'pass'},
    {test:'OP-2', agent:'5.2-M',    outcome:'pass'},
    {test:'OP-2', agent:'5.2-H',    outcome:'pass'},
    {test:'OP-2', agent:'5.2-XH',   outcome:'pass'},
    {test:'OP-2', agent:'5.3-L',    outcome:'pass'},
    {test:'OP-2', agent:'5.3-M',    outcome:'pass'},
    {test:'OP-2', agent:'5.3-H',    outcome:'pass'},
    {test:'OP-2', agent:'5.3-XH',   outcome:'pass'},
    {test:'OP-2', agent:'5.4m-L',   outcome:'partial', note:'curl 0 bytes silent fail'},
    {test:'OP-2', agent:'5.4m-M',   outcome:'pass'},
    {test:'OP-2', agent:'5.4m-H',   outcome:'pass'},
    {test:'OP-2', agent:'5.4m-XH',  outcome:'partial', note:'browser only, DOM 143K vs raw 240K'},
    {test:'OP-2', agent:'5.4-L',    outcome:'pass'},
    {test:'OP-2', agent:'5.4-M',    outcome:'pass'},
    {test:'OP-2', agent:'5.4-H',    outcome:'pass'},
    {test:'OP-2', agent:'5.4-XH',   outcome:'pass'},
    {test:'OP-2', agent:'5.5-L',    outcome:'pass', note:'curl only, bypassed web.open'},
    {test:'OP-2', agent:'5.5-M',    outcome:'pass'},
    {test:'OP-2', agent:'5.5-H',    outcome:'pass'},
    {test:'OP-2', agent:'5.5-XH',   outcome:'pass'},
    // OP-4 (514 KB CommonMark)
    {test:'OP-4', agent:'5.2-L',    outcome:'partial', note:'web.open only, L237 ceiling'},
    {test:'OP-4', agent:'5.2-M',    outcome:'partial', note:'lineno tail probe, no curl'},
    {test:'OP-4', agent:'5.2-H',    outcome:'partial', note:'looped 14m24s, L237 ceiling'},
    {test:'OP-4', agent:'5.2-XH',   outcome:'pass'},
    {test:'OP-4', agent:'5.3-L',    outcome:'partial', note:'web.open only, L237'},
    {test:'OP-4', agent:'5.3-M',    outcome:'pass', note:'bypassed web.open'},
    {test:'OP-4', agent:'5.3-H',    outcome:'pass', note:'run 6 - most granular permissions'},
    {test:'OP-4', agent:'5.3-XH',   outcome:'pass'},
    {test:'OP-4', agent:'5.4m-L',   outcome:'partial', note:'curl DNS fail, tail reached L7422'},
    {test:'OP-4', agent:'5.4m-M',   outcome:'pass'},
    {test:'OP-4', agent:'5.4m-H',   outcome:'pass'},
    {test:'OP-4', agent:'5.4m-XH',  outcome:'pass'},
    {test:'OP-4', agent:'5.4-L',    outcome:'pass', note:'first Low-tier curl success in OP-4'},
    {test:'OP-4', agent:'5.4-M',    outcome:'pass'},
    {test:'OP-4', agent:'5.4-H',    outcome:'pass', note:'pagination described correctly'},
    {test:'OP-4', agent:'5.4-XH',   outcome:'pass', note:'3 trunc layers identified'},
    {test:'OP-4', agent:'5.5-L',    outcome:'pass', note:'curl only, 27s, 8% ctx'},
    {test:'OP-4', agent:'5.5-M',    outcome:'pass', note:'curl only'},
    {test:'OP-4', agent:'5.5-H',    outcome:'pass', note:'curl only'},
    {test:'OP-4', agent:'5.5-XH',   outcome:'pass'},
  ];

  // Agent rows: model version × intelligence level
  var agentOrder = [
    '5.2-L','5.2-M','5.2-H','5.2-XH',
    '5.3-L','5.3-M','5.3-H','5.3-XH',
    '5.4m-L','5.4m-M','5.4m-H','5.4m-XH',
    '5.4-L','5.4-M','5.4-H','5.4-XH',
    '5.5-L','5.5-M','5.5-H','5.5-XH',
    '5.5-H2'
  ];

  var agentLabels = {
    '5.2-L':   'GPT-5.2 Low',
    '5.2-M':   'GPT-5.2 Medium',
    '5.2-H':   'GPT-5.2 High',
    '5.2-XH':  'GPT-5.2 Extra High',
    '5.3-L':   'GPT-5.3-Codex Low',
    '5.3-M':   'GPT-5.3-Codex Medium',
    '5.3-H':   'GPT-5.3-Codex High',
    '5.3-XH':  'GPT-5.3-Codex Extra High',
    '5.4m-L':  'GPT-5.4-Mini Low',
    '5.4m-M':  'GPT-5.4-Mini Medium',
    '5.4m-H':  'GPT-5.4-Mini High',
    '5.4m-XH': 'GPT-5.4-Mini Extra High',
    '5.4-L':   'GPT-5.4 Low',
    '5.4-M':   'GPT-5.4 Medium',
    '5.4-H':   'GPT-5.4 High',
    '5.4-XH':  'GPT-5.4 Extra High',
    '5.5-L':   'GPT-5.5 Low',
    '5.5-M':   'GPT-5.5 Medium',
    '5.5-H':   'GPT-5.5 High',
    '5.5-XH':  'GPT-5.5 Extra High',
    '5.5-H2':  'GPT-5.5 High*',
  };

  function getCellColors(isDark, outcome) {
    if (outcome === 'pass')    return {bg: isDark ? '#0F6E56' : '#1D9E75', fg: '#fff',                           label: '✓'};
    if (outcome === 'partial') return {bg: isDark ? '#cba452' : '#FFB74D', fg: isDark ? '#412402' : '#412402',   label: '~'};
    if (outcome === 'fail')    return {bg: isDark ? '#A32D2D' : '#F06292', fg: '#fff',                           label: '✗'};
    if (outcome === 'invalid') return {bg: isDark ? '#3C3489' : '#BA68C8', fg: '#fff',                           label: '!'};
    return {bg: isDark ? '#363634' : '#d0cec7', fg: 'inherit', label: ''};
  }

  function getLegendItems(isDark, notObsBg) {
    return [
      {bg: isDark ? '#0F6E56' : '#1D9E75', label: '✓ — full document retrieved (curl or valid path)'},
      {bg: isDark ? '#cba452' : '#FFB74D', label: '~ — partial: web.open only, truncated, or curl failed'},
      {bg: isDark ? '#A32D2D' : '#F06292', label: '✗ — retrieval failure (0 bytes, loop, DNS block)'},
      {bg: isDark ? '#3C3489' : '#BA68C8', label: '! — invalid measurement (HTTP 404, contaminated)'},
      {bg: notObsBg,                        label: 'untested'},
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
    var cellW = props.large ? 52 : 38;
    var cellH = props.large ? 34 : 26;
    var agentColW = props.large ? 190 : 140;
    var fs = props.large ? 13 : 11;
    var tc = props.textColor || 'inherit';
    var notObsBg = dark ? '#363634' : '#d0cec7';

    return e('div', {className:'cdx-hm-wrap'},
      e('table', {className:'cdx-hm'},
        e('thead', null,
          e('tr', null,
            e('th', {className:'cdx-row-head', style:{minWidth:agentColW, color:tc}}, 'Agent'),
            testOrder.map(function(t) {
              return e('th', {key:t.id, style:{color:tc}},
                t.l1, e('br'), e('span', {className:'cdx-url-note'}, t.l2)
              );
            })
          )
        ),
        e('tbody', null,
          agentOrder.map(function(agent) {
            var ar = runs.filter(function(r) { return r.agent === agent; });
            return e('tr', {key:agent},
              e('td', {className:'cdx-row-label', style:{color:tc, verticalAlign:'middle'}}, agentLabels[agent]),
              testOrder.map(function(t) {
                var run = ar.find(function(r) { return r.test === t.id; });
                if (!run) {
                  return e('td', {key:t.id},
                    e('div', {style:{
                      borderRadius:4, fontSize:fs, fontWeight:600,
                      display:'flex', alignItems:'center', justifyContent:'center',
                      width:cellW, height:cellH, margin:'1px auto',
                      background:notObsBg
                    }})
                  );
                }
                var c = getCellColors(dark, run.outcome);
                var tip = run.outcome + (run.note ? ': ' + run.note : '');
                return e('td', {key:t.id},
                  e('div', {title:tip, style:{
                    borderRadius:4, fontSize:fs, fontWeight:600,
                    display:'flex', alignItems:'center', justifyContent:'center',
                    width:cellW, height:cellH, margin:'1px auto',
                    background:c.bg, color:c.fg,
                    cursor: run.note ? 'help' : 'default'
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
    return e('p', {className:'cdx-note', style:{color:tc, marginTop:0, paddingTop:0}},
      e('i', null,
        'Columns: page size ascending. ',
        e(C, null, 'SC-3'), ' has 21 runs (one extra ', e(C, null, 'GPT-5.5 High'), ' retry). ',
        e(C, null, 'GPT-5.5 High*'), ': second run in SC-3 cycle. ',
        e(C, null, '!'), ': invalid measurement (HTTP 404, contamination). ',
        'Hover cells for run notes.'
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
        e('p', {className:'cdx-hint'}, '\u2197 click to expand')
      ),
      e('div', {style:{display:'flex', gap:32, alignItems:'center', flexWrap:'wrap', marginTop:8, width:'100%', justifyContent:'center'}},
        e('div', {style:{flexShrink:0}}, e(Legend, {isDark:isDark})),
        e('div', {style:{flex:1, maxWidth:420}}, e(Note, {isDark:isDark}))
      ),
      isOpen && e('div', {
        className:'cdx-overlay',
        onClick:function(ev){ if (ev.target === ev.currentTarget) setOpen(false); }
      },
        e('div', {
          className:'cdx-overlay-inner',
          style:{background:lbBg, color:lbText, width:'98vw'}
        },
          e('button', {
            className:'cdx-close',
            style:{color:lbText},
            onClick:function(){ setOpen(false); },
            'aria-label':'Close'
          }, '\u00d7'),
          e(HeatmapTable, {large:true, isDark:isDark, textColor:lbText}),
          e('div', {style:{display:'flex', gap:32, alignItems:'center', flexWrap:'nowrap', marginTop:8, width:'100%', justifyContent:'center'}},
            e('div', {style:{flexShrink:0}}, e(Legend, {isDark:isDark, textColor:lbText})),
            e('div', {style:{flex:1, maxWidth:420}}, e(Note, {isDark:isDark, textColor:lbText}))
          )
        )
      )
    );
  }

  var root = ReactDOM.createRoot(document.getElementById('cdx-hm-root'));
  root.render(e(App));
})();
</script>
{% endraw %}

The model-version threshold is visible top-to-bottom: `GPT-5.2` requires `High` or `Extra High` intelligence to escalate to `curl` on most URLs; `GPT-5.3-Codex` escalates at `Medium`; `GPT-5.4` at `Low`; and `GPT-5.5` bypasses `web.open` entirely at all intelligence levels. Partial-retrieval runs cluster in `GPT-5.2` and `GPT-5.3-Codex` at `Low` and `Medium` intelligence levels, with `GPT-5.4-Mini` as an exception — `curl` DNS failures suppressed escalation there regardless of intelligence level.

---

## Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| 1 | **`web.open` is a line-indexed rendered text extraction, not a raw HTTP response** | All tests | Returns a line-numbered, HTML-to-text-extracted viewport; `wordlim: 200` visible in tool output across `BL-1`, `OP-1`, `SC-3`, `SC-4`; `Total lines: N` reported for each URL | **Output chars on the `web.open` path reflect viewport depth, not retrieval ceiling; `curl` is the only path to the raw HTTP body** |
| 2 | **No fixed character or token ceiling detected on the `curl` path** | `BL-1`, `BL-3`, `OP-1`, `OP-4`, `SC-3` | Largest valid fetch: ~3.1M chars (`BL-3` `GPT-5.2 Medium`); `OP-4` `GPT-5.5 Low` returned 514,092 chars in 27 seconds with 8% context; no run hit a ceiling on the `curl` path | **`curl` path has no observed byte or token ceiling across 261 runs; constraint is model-version-gated access, not infrastructure** |
| 3 | **Three independent truncation layers disambiguated** | `BL-1`, `EC-6`, `OP-4` | `GPT-5.4 Low` (`BL-1`) first isolated all three: `web.open` viewer window, terminal display cap, and the underlying HTTP body; `EC-6` confirmed a ~12,970-token display cap independent of file size; `OP-4` `GPT-5.4 Extra High` explicitly named all three layers | **Self-reported truncation is surface-specific; agents frequently report "no truncation" on the `curl` body while `web.open` truncation goes unmentioned in the summary** |
| 4 | **`curl` escalation capability is model-version-gated, not intelligence-level-gated for newer families** | `BL-1`, `BL-3`, `OP-4`, `SC-3` | `GPT-5.2` requires `High`+ for `curl`; `GPT-5.4` escalates at `Low`; `GPT-5.5` skips `web.open` entirely at all levels; within `GPT-5.4-Mini`, DNS sandbox failures suppressed escalation regardless of level | **`curl`-first behavior is a model-version property, not an intelligence-level property; the capability threshold collapsed from `High` to `Low` between `GPT-5.2` and `GPT-5.4`** |
| 5 | **Higher intelligence levels don't reliably produce better retrieval, and `Extra High` shows cost/yield regression** | `BL-1`, `EC-1`, `OP-4`, `SC-2` | `GPT-5.4-Mini Extra High` spent 85s on a 3-part fetch strategy matching `Medium`'s single-fetch result; `GPT-5.2 Extra High` (`EC-1`) looped for 48m10s on 113 web searches without escalating; `GPT-5.5 Low` retrieved 514 KB (`OP-4`) in 27s vs `GPT-5.2 High` looping 14m24s at 45% context on the same task | **Intelligence level governs instrumentation sophistication, not retrieval outcome; `Extra High` consistently produces diminishing returns against `web.open`-bounded tasks** |
| 6 | **Session contamination is a persistent confound** | `BL-1`, `BL-2`, `BL-3`, `EC-1`, `EC-6`, `SC-2`, `SC-4` | `Documents/Codex` persists across sessions; artifact filenames reused across runs confirmed in 20+ cases; `GPT-5.5 High` (`BL-2`) likely read a prior session artifact rather than executing a fresh fetch; `GPT-5.4 Extra High` (`BL-1`) completed in 42s vs 1m46s for `Low` on identical task due to strategy reuse | **Intelligence level is not an independent variable within shared sessions; future runs should use isolated sessions per level** |
| 7 | **JS-rendered pages produce a structural retrieval failure, not a truncation event** | `SC-2`, `BL-3` | `SC-2` (Next.js / Netlify): `web.open` returns a consistent 142-line pre-hydration shell; nonce-based CSP and `no-store` cache policy prevent JS execution on any fetch path; `BL-3` tutorial body absent from static extraction at a reproducible structural position (L385-L389) across all 20 runs | **Neither `web.open` nor `curl` returns the actual content for CSP-gated JS-rendered pages; this is a fundamental retrieval barrier not addressable by escalation** |
| 8 | **`raw.githubusercontent.com` `Cache Miss` is systematic for large payloads** | `EC-6` | 17 of 20 runs that attempted `web.open` on the raw GitHub URL received `Cache Miss (no content retrieved)`; a smaller `raw.githubusercontent.com` control confirmed the host isn't fully blocked; no run investigated or diagnosed the failure before pivoting to `curl` | **The failure is URL-size-class-specific to raw GitHub payloads; agents report what succeeded, not what failed** |
| 9 | **`web.open` line window is LLM-version-correlated on the same URL** | `OP-2`, `OP-4`, `SC-3` | `OP-2`: L317 dominant cutpoint for `GPT-5.2`–`5.4`; L590 for `GPT-5.5`; `OP-4`: L237 for `GPT-5.2`–`5.4`; L616 for `GPT-5.5 Extra High`; `SC-3`: L266 dominant for `GPT-5.2`/`5.4-Mini`; L353 for `GPT-5.3-Codex`/`5.5` | **The viewport window scales across model generations; the same URL returns a larger first-fetch window in newer LLM versions** |
| 10 | **`wordlim: 200` is the operative `web.open` window parameter** | `BL-1`, `OP-1`, `OP-4`, `SC-3`, `SC-4` | First surfaced in `BL-1` `GPT-5.2 Low`; confirmed in `OP-1`, `SC-3`, and `SC-4` across multiple model families; controls the line window and explains consecutive L-offset cutpoints | **`wordlim: 200` is a line-count parameter, not a character or token ceiling; increasing intelligence level doesn't change it** |
| 11 | **`L477` is a probable shared infrastructure cutoff constant in `BL-1`** | `BL-1` | L477 appeared as the identical cutpoint across `GPT-5.2 Medium`, `GPT-5.3-Codex High`, and `GPT-5.3-Codex Extra High` without model coordination | **A hardcoded viewer-window constant rather than content-adaptive behavior; L477 cutpoint makes `GPT-5.3-Codex` ceiling behavior an infrastructure property** |
| 12 | **`multi_tool_use.parallel` is exclusive to `GPT-5.4 Extra High` and `GPT-5.5`** | `BL-1`, `BL-3`, `EC-1`, `EC-3`, `EC-6`, `OP-2`, `OP-4`, `SC-1`, `SC-3`, `SC-4` | Not observed in `GPT-5.2` or `GPT-5.3-Codex` at any intelligence level; first appeared in `GPT-5.4 Extra High`; consistent across all `GPT-5.5` levels | **Parallel tool invocation is a model-version capability, not an intelligence-level behavior** |

## Perception Gap

> _Output chars on the `web.open` surface aren't a retrieval ceiling metric; they reflect how far the agent scrolled through a line-indexed renderer. Neither that viewport depth nor the `curl` body size is directly observable from the interpreted track alone when session contamination is present._

| **Test** | **Expected** | **Received** | **Delivery Ratio** | **Agent Characterization** |
| --- | --- | --- | --- | --- |
| **`BL-1`<br>`curl`-capable** | ~505 KB | 505,339 chars<br>`GPT-5.4`/`5.5` all levels | ~100% | _"No truncation — curl returned full response body; web.open viewer window is a separate, capped surface"_ |
| **`BL-1`<br>`web.open` only** | ~505 KB | ~19K–85K chars<br>`GPT-5.4-Mini`; ~1,600–61K `GPT-5.2`/`5.3-Codex` | ~0.3–17% | _"Truncated at line boundary — tool ceiling confirmed; content beyond L140/L477 not retrieved"_ |
| **`EC-6`<br>Raw Markdown** | ~92 KB | 91,869 chars<br>`curl` all runs | ~100% body | _"No retrieval truncation — display truncation at ~12,970 tokens is a terminal rendering cap, not a fetch limit; saved file complete"_ |
| **`SC-2`<br>Next.js SPA** | ~80 KB doc content | 511K–519K chars<br>`curl` (app shell only) | N/A — structural | _"Full shell retrieved — actual API reference text is JS-hydrated and inaccessible on any retrieval path; curl delivers nav scaffolding and data bundles, not documentation"_ |
| **`BL-3`<br>Tutorial** | ~250 KB | ~3.1 MB `curl`<br>(tutorial body absent) | N/A — JS-rendered | _"Complete HTML shell — tutorial walkthrough is client-side rendered and not present in static payload; curl is complete for what the server returns"_ |
| **`EC-3`<br>Redirect JSON** | ~2 KB | 660 chars web pipeline<br>254 bytes `curl` | ~100% | _"Complete — web pipeline pads response with wrapper text; curl returns raw body; neither represents truncation"_ |

---

## Hypothesis Verdicts

| **Hypothesis** | **Combined Verdict** | **Notes** |
| --- | --- | --- |
| **`H1`: Character-based truncation at a fixed ceiling** | Partially supported — model-stratified on `web.open` path; not supported on `curl` path | `web.open` window is line-count-bound via `wordlim: 200`, not character-bound; `curl` path hit no ceiling across any test |
| **`H2`: Token-based truncation ~2,000 tokens** | Not supported | No run approached a 2,000-token ceiling on either path; `web.open` token counts are lower but reflect the line window, not a token gate; EC-6 display cap at ~12,970 tokens is a terminal rendering layer |
| **`H3`: Structure-aware truncation, respects Markdown boundaries** | Not supported as a mechanism | `web.open` cutpoints consistently land mid-article, mid-table, or mid-sentence; `wordlim: 200` is the operative parameter; EC-6 display truncation confirmed mid-word |
| **`H4`: Surface context changes retrieval ceiling** | Untested — all runs Codex IDE | Two-tier network access architecture confirmed as a consistent surface property; cross-surface VS Code-Codex comparison not yet performed |
| **`H5`: Agent auto-chunks above the truncation ceiling** | Partially supported — reactive escalation only | Proactive pagination not observed; dominant pattern is `web.open` → gap recognition → `curl` escalation; `GPT-5.5` bypasses `web.open` entirely rather than paginating it |
