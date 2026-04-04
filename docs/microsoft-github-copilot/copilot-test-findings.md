---
layout: default
title: "Key Findings for Copilot's Web Fetch Behavior, Copilot-interpreted"
permalink: /docs/microsoft-github-copilot/copilot-test-findings
parent: Microsoft GitHub Copilot
---

## Key Findings for Copilot's Web Fetch Behavior, Copilot-interpreted

---

## Topic Guide

- [Copilot-interpreted Test Workflow](#copilot-interpreted-test-workflow)
- [Platform Limit Summary](#platform-limit-summary)
- [Results Details](#results-details)
- [Cross-run Output Variance](#cross-run-output-variance)
- [Model Routing Distribution](#model-routing-distribution)
- [Perception Gap](#perception-gap)

---

## [Copilot-interpreted Test Workflow](https://github.com/rhyannonjoy/agent-ecosystem-testing/blob/main/copilot-web-content-retrieval/web_content_retrieval_testing_framework.py)

    1. Run `python web_content_retrieval_testing_framework.py --test {test ID} --track interpreted`
    2. Review the terminal output
    3. Copy the provided prompt asking the model to report on fetch results:
       character count, token estimate, truncation status, content completeness,
       Markdown formatting integrity, and tool visibility
    4. Open a new Copilot chat session in VS Code and paste the prompt into the chat window
    5. Skip any tool call prompts for local scripts or code execution
    6. Capture model's full text response and observations as the interpreted finding;
       gap between the model's self-report and actual fetch behavior is a finding
    7. Log structured metadata as described in the `framework-reference.md`
    8. Ensure log results are saved to `/results/copilot-interpreted/results.csv`*

>*_Results logged as "Methods tested: `vscode-chat`" reflect a manually
operated testing process in which prompts are copy-pasted into the Copilot
chat window. Copilot has no publicly documented backend web content retrieval
mechanism; identified `fetch_webpage` through tool logs. Read the
[Friction Note](friction-note.md#fetch_webpage-undocumented) for analysis._

---

## Platform Limit Summary

| **Limit** | **Observed** |
| ------- | ---------- |
| **Hard Character Limit** | _None detected_: `fetch_webpage` returns relevance-ranked excerpts by design, not raw pages with a byte ceiling |
| **Hard Token Limit** | _None detected as a fixed ceiling_: avg 7,313 tokens across 55 runs; output varies by relevance ranking |
| **Output Consistency** | _High variance_; `EC-3` JSON payload 651 chars to `SC-3` Wikipedia ~150,000 chars; same URL and model can produce 2x difference |
| **Content Selection Behavior** | _Relevance-ranked excerpting_: tool returns semantically filtered chunks keyed to a query parameter, not sequential page content |
| **Truncation Pattern** | `...` markers throughout output are retrieval-layer elision indicators, not byte-boundary cutoffs |
| **Redirect Chains** | _Successfully follows_: tested 5-level redirect chain in `EC-3`;<br>User-Agent value internally truncated in returned JSON |
| **Self-reported Completeness** | _Unreliable_: model flags `...` markers as truncation evidence may misattribute cause as structural property of `fetch_webpage`,<br>likely not hitting a size limit |
| **Model Routing** | _Unstable_: `Auto` dispatches to at least 5 distinct models with no documented routing logic and no UI indication<br> when switching occurs |
| **Tool Substitution** | _Agent autonomously attempts_ local code execution `pylanceRunCodeSnippet`, `zsh` despite prompt guardrails |

## Results Details

| --- | --- |
| **Model Selector** | `Auto` |
| **Models Observed** | `Claude Haiku 4.5`, `Claude Sonnet 4.6`, `GPT-5.3-Codex`,<br>`GPT-5.4`, `Grok Code Fast 1`, `Raptor mini (Preview)` |
| **Total Tests** | 55 |
| **Distinct URLs** | 11 |
| **Input Size Range** | ~2KB–256KB |
| **Truncation Events** | 54 / 55 |
| **Average Output Size** | 29,239 chars |
| **Average Token Count** | 7,313 tokens |
| **Truncation Detection** | Model assertion, verbatim last-50-chars,<br>Markdown integrity, `...` elision marker count |

## Cross-run Output Variance

The chart below plots `output_chars` for each run on a logarithmic y-axis, colored by
`model_observed`. Points are jittered slightly on the x-axis so overlapping runs remain visible.
Hover over any point to see test ID, model, and exact char count.

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
(function() {
  var raw = [
    {test:"BL-1",model:"Claude Haiku 4.5",chars:24500},
    {test:"BL-1",model:"(unknown)",chars:0},
    {test:"BL-1",model:"Raptor mini (Preview)",chars:4500},
    {test:"BL-1",model:"Raptor mini (Preview)",chars:3200},
    {test:"BL-1",model:"Raptor mini (Preview)",chars:8750},
    {test:"BL-2",model:"Raptor mini (Preview)",chars:4200},
    {test:"BL-2",model:"Raptor mini (Preview)",chars:2950},
    {test:"BL-2",model:"Grok Code Fast 1",chars:8472},
    {test:"BL-2",model:"Raptor mini (Preview)",chars:4300},
    {test:"BL-2",model:"Claude Haiku 4.5",chars:4850},
    {test:"BL-3",model:"GPT-5.4 0.9x",chars:22500},
    {test:"BL-3",model:"GPT-5.4 0.9x",chars:15000},
    {test:"BL-3",model:"Claude Haiku 4.5 0.3x",chars:87000},
    {test:"BL-3",model:"GPT-5.3-Codex 0.9x",chars:21000},
    {test:"BL-3",model:"Claude Haiku 4.5 0.3x",chars:42850},
    {test:"SC-1",model:"Claude Sonnet 4.6 0.9x",chars:11250},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:20000},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:16000},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:17000},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:17000},
    {test:"SC-2",model:"Claude Haiku 4.5",chars:13847},
    {test:"SC-2",model:"Raptor mini (Preview)",chars:8000},
    {test:"SC-2",model:"Claude Sonnet 4.6 0.9x",chars:12500},
    {test:"SC-2",model:"Claude Sonnet 4.6 0.9x",chars:13250},
    {test:"SC-2",model:"GPT-5.3-Codex 0.9x",chars:16900},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:130000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:120000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:150000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:115000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:125000},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:32500},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:33000},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:48500},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:30000},
    {test:"SC-4",model:"Claude Sonnet 4.6 0.9x",chars:16250},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:33000},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:25000},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:12500},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:25000},
    {test:"OP-4",model:"Claude Sonnet 4.6 0.9x",chars:12000},
    {test:"EC-1",model:"GPT-5.3-Codex 0.9x",chars:14000},
    {test:"EC-1",model:"GPT-5.3-Codex 0.9x",chars:14000},
    {test:"EC-1",model:"GPT-5.3-Codex 0.9x",chars:14800},
    {test:"EC-1",model:"Claude Sonnet 4.6 0.9x",chars:7200},
    {test:"EC-1",model:"Claude Sonnet 4.6 0.9x",chars:6400},
    {test:"EC-3",model:"Claude Sonnet 4.6 0.9x",chars:651},
    {test:"EC-3",model:"GPT-5.3-Codex 0.9x",chars:651},
    {test:"EC-3",model:"Claude Sonnet 4.6 0.9x",chars:890},
    {test:"EC-3",model:"Claude Sonnet 4.6 0.9x",chars:874},
    {test:"EC-3",model:"GPT-5.3-Codex 0.9x",chars:1090},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:60000},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:60000},
    {test:"EC-6",model:"Claude Sonnet 4.6 0.9x",chars:40000},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:40000},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:40000}
  ];

  var testOrder = ["BL-1","BL-2","BL-3","SC-1","SC-2","SC-3","SC-4","OP-4","EC-1","EC-3","EC-6"];

  var modelColors = {
    "GPT-5.3-Codex 0.9x":    "#378ADD",
    "Claude Sonnet 4.6 0.9x": "#1D9E75",
    "Claude Haiku 4.5":       "#EF9F27",
    "Claude Haiku 4.5 0.3x":  "#BA7517",
    "Raptor mini (Preview)":  "#D4537E",
    "GPT-5.4 0.9x":           "#7F77DD",
    "Grok Code Fast 1":       "#888780",
    "(unknown)":              "#B4B2A9"
  };

  function jitter() { return (Math.random() - 0.5) * 0.35; }

  var datasets = Object.entries(modelColors).map(function(entry) {
    var model = entry[0]; var color = entry[1];
    var points = raw.filter(function(d) { return d.model === model; }).map(function(d) {
      return { x: testOrder.indexOf(d.test) + jitter(), y: d.chars, test: d.test, model: d.model, chars: d.chars };
    });
    return {
      label: model,
      data: points,
      backgroundColor: color + 'cc',
      borderColor: color,
      borderWidth: 1,
      pointRadius: 7,
      pointHoverRadius: 9
    };
  });

  var legend = document.getElementById('copilot-legend');
  Object.entries(modelColors).forEach(function(entry) {
    var model = entry[0]; var color = entry[1];
    if (!raw.some(function(d) { return d.model === model; })) return;
    legend.innerHTML += '<span style="display:flex;align-items:center;gap:4px;">'
      + '<span style="width:10px;height:10px;border-radius:50%;background:' + color + ';display:inline-block;"></span>'
      + model + '</span>';
  });

  new Chart(document.getElementById('copilot-chart'), {
    type: 'scatter',
    data: { datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: function() { return ''; },
            label: function(ctx) {
              var d = ctx.raw;
              return [d.test + ' \u2014 ' + d.model, d.chars.toLocaleString() + ' chars'];
            }
          }
        }
      },
      scales: {
        x: {
          min: -0.5,
          max: testOrder.length - 0.5,
          ticks: {
            stepSize: 1,
            callback: function(v) { return testOrder[Math.round(v)] || ''; },
            autoSkip: false,
            maxRotation: 35,
            font: { size: 12 }
          },
          grid: { color: 'rgba(128,128,128,0.1)' }
        },
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(v) { return v >= 1000 ? Math.round(v / 1000) + 'k' : v; },
            font: { size: 12 }
          },
          grid: { color: 'rgba(128,128,128,0.1)' },
          title: { display: true, text: 'output chars', font: { size: 12 }, color: '#888' }
        }
      }
    }
  });
})();
</script>

<div style="margin: 1.5rem 0; font-family: inherit;">

  <div id="copilot-legend-log" style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; font-size: 12px; color: #666;"></div>

  <div style="position: relative; width: 100%; height: 480px;">
    <canvas id="copilot-chart-log"></canvas>
  </div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
(function() {
  var raw = [
    {test:"BL-1",model:"Claude Haiku 4.5",chars:24500},
    {test:"BL-1",model:"Raptor mini (Preview)",chars:4500},
    {test:"BL-1",model:"Raptor mini (Preview)",chars:3200},
    {test:"BL-1",model:"Raptor mini (Preview)",chars:8750},
    {test:"BL-2",model:"Raptor mini (Preview)",chars:4200},
    {test:"BL-2",model:"Raptor mini (Preview)",chars:2950},
    {test:"BL-2",model:"Grok Code Fast 1",chars:8472},
    {test:"BL-2",model:"Raptor mini (Preview)",chars:4300},
    {test:"BL-2",model:"Claude Haiku 4.5",chars:4850},
    {test:"BL-3",model:"GPT-5.4 0.9x",chars:22500},
    {test:"BL-3",model:"GPT-5.4 0.9x",chars:15000},
    {test:"BL-3",model:"Claude Haiku 4.5 0.3x",chars:87000},
    {test:"BL-3",model:"GPT-5.3-Codex 0.9x",chars:21000},
    {test:"BL-3",model:"Claude Haiku 4.5 0.3x",chars:42850},
    {test:"SC-1",model:"Claude Sonnet 4.6 0.9x",chars:11250},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:20000},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:16000},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:17000},
    {test:"SC-1",model:"GPT-5.3-Codex 0.9x",chars:17000},
    {test:"SC-2",model:"Claude Haiku 4.5",chars:13847},
    {test:"SC-2",model:"Raptor mini (Preview)",chars:8000},
    {test:"SC-2",model:"Claude Sonnet 4.6 0.9x",chars:12500},
    {test:"SC-2",model:"Claude Sonnet 4.6 0.9x",chars:13250},
    {test:"SC-2",model:"GPT-5.3-Codex 0.9x",chars:16900},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:130000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:120000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:150000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:115000},
    {test:"SC-3",model:"GPT-5.3-Codex 0.9x",chars:125000},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:32500},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:33000},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:48500},
    {test:"SC-4",model:"GPT-5.3-Codex 0.9x",chars:30000},
    {test:"SC-4",model:"Claude Sonnet 4.6 0.9x",chars:16250},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:33000},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:25000},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:12500},
    {test:"OP-4",model:"GPT-5.3-Codex 0.9x",chars:25000},
    {test:"OP-4",model:"Claude Sonnet 4.6 0.9x",chars:12000},
    {test:"EC-1",model:"GPT-5.3-Codex 0.9x",chars:14000},
    {test:"EC-1",model:"GPT-5.3-Codex 0.9x",chars:14000},
    {test:"EC-1",model:"GPT-5.3-Codex 0.9x",chars:14800},
    {test:"EC-1",model:"Claude Sonnet 4.6 0.9x",chars:7200},
    {test:"EC-1",model:"Claude Sonnet 4.6 0.9x",chars:6400},
    {test:"EC-3",model:"Claude Sonnet 4.6 0.9x",chars:651},
    {test:"EC-3",model:"GPT-5.3-Codex 0.9x",chars:651},
    {test:"EC-3",model:"Claude Sonnet 4.6 0.9x",chars:890},
    {test:"EC-3",model:"Claude Sonnet 4.6 0.9x",chars:874},
    {test:"EC-3",model:"GPT-5.3-Codex 0.9x",chars:1090},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:60000},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:60000},
    {test:"EC-6",model:"Claude Sonnet 4.6 0.9x",chars:40000},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:40000},
    {test:"EC-6",model:"GPT-5.3-Codex 0.9x",chars:40000}
  ];

  var testOrder = ["BL-1","BL-2","BL-3","SC-1","SC-2","SC-3","SC-4","OP-4","EC-1","EC-3","EC-6"];

  var modelColors = {
    "GPT-5.3-Codex 0.9x":    "#378ADD",
    "Claude Sonnet 4.6 0.9x": "#1D9E75",
    "Claude Haiku 4.5":       "#EF9F27",
    "Claude Haiku 4.5 0.3x":  "#BA7517",
    "Raptor mini (Preview)":  "#D4537E",
    "GPT-5.4 0.9x":           "#7F77DD",
    "Grok Code Fast 1":       "#888780"
  };

  function jitter() { return (Math.random() - 0.5) * 0.35; }

  var datasets = Object.entries(modelColors).map(function(entry) {
    var model = entry[0]; var color = entry[1];
    var points = raw.filter(function(d) { return d.model === model; }).map(function(d) {
      return { x: testOrder.indexOf(d.test) + jitter(), y: d.chars, test: d.test, model: d.model, chars: d.chars };
    });
    return {
      label: model,
      data: points,
      backgroundColor: color + 'cc',
      borderColor: color,
      borderWidth: 1,
      pointRadius: 7,
      pointHoverRadius: 9
    };
  });

  var legend = document.getElementById('copilot-legend-log');
  Object.entries(modelColors).forEach(function(entry) {
    var model = entry[0]; var color = entry[1];
    if (!raw.some(function(d) { return d.model === model; })) return;
    legend.innerHTML += '<span style="display:flex;align-items:center;gap:4px;">'
      + '<span style="width:10px;height:10px;border-radius:50%;background:' + color + ';display:inline-block;"></span>'
      + model + '</span>';
  });

  new Chart(document.getElementById('copilot-chart-log'), {
    type: 'scatter',
    data: { datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: function() { return ''; },
            label: function(ctx) {
              var d = ctx.raw;
              return [d.test + ' \u2014 ' + d.model, d.chars.toLocaleString() + ' chars'];
            }
          }
        }
      },
      scales: {
        x: {
          min: -0.5,
          max: testOrder.length - 0.5,
          ticks: {
            stepSize: 1,
            callback: function(v) { return testOrder[Math.round(v)] || ''; },
            autoSkip: false,
            maxRotation: 35,
            font: { size: 12 }
          },
          grid: { color: 'rgba(128,128,128,0.1)' }
        },
        y: {
          type: 'logarithmic',
          min: 500,
          ticks: {
            callback: function(v) {
              var known = [500, 1000, 5000, 10000, 50000, 100000, 150000];
              if (known.indexOf(v) !== -1) {
                return v >= 1000 ? Math.round(v / 1000) + 'k' : v;
              }
              return '';
            },
            font: { size: 12 }
          },
          grid: { color: 'rgba(128,128,128,0.1)' },
          title: { display: true, text: 'output chars (log scale)', font: { size: 12 }, color: '#888' }
        }
      }
    }
  });
})();
</script>

>_`SC-3` returned 115k–150k chars, the highest output of any test by a wide margin.
> `BL-3` shows the highest within-test variance: `Claude Haiku 4.5 0.3x` returned 87k and 42k
> while GPT-family runs on the same URL clustered at 15k–22k._

| **Test** | **Category** | **r1 chars** | **r2<br>chars** | **r3 chars** | **r4 chars** | **r5 chars** | **Variance** |
| ------ | ------- | ------: | ------: | ------: | ------: | ------: | ------: |
| **BL-1** | Baseline - 87KB | 24,500 | _timeout_ | 4,500 | 3,200 | 8,750 | * |
| **BL-2** | Baseline - 20KB | 4,200 | 2,950 | 8,472 | 4,300 | 4,850 | 2.9x |
| **BL-3** | Baseline - 256KB | 22,500 | 15,000 | 87,000 | 21,000 | 42,850 | 5.8x |
| **SC-2** | Code blocks - 82KB | 13,847 | 8,000 | 12,500 | 13,250 | 16,900 | 2.1x |
| **SC-3** | Wikipedia - 102KB | 130,000 | 150,000 | 125,000 | 120,000 | 115,000 | 1.3x |
| **SC-4** | Markdown Guide - 31KB | 32,500 | 48,500 | 33,000 | 30,000 | 16,250 | 3.0x |
| **EC-1** | Landing page - 102KB | 14,000 | 14,000 | 14,800 | 7,200 | 6,400 | 2.3x |
| **EC-3** | Redirect chain - 2KB | 651 | 651 | 890 | 874 | 1,090 | 1.7x |
| **EC-6** | Raw Markdown - 61KB | 60,000 | 60,000 | 40,000 | 40,000 | 40,000 | 1.5x |
| **OP-4** | Auto-chunking - 256KB | 33,000 | 25,000 | 12,500 | 25,000 | 12,000 | 2.6x |

>*_Excluding the timeout gives a variance of 7.7x, which is the highest variance of any test,
>but calculating variance with 0 and/or timeout is meaningless when it represents a failed
>run rather than a real retrieval result_

### Truncation Analysis

| **#** | **Finding** | **Tests** | **Observed** | **Conclusion** |
| --- | --- | --- | --- | --- |
| **1** | **`fetch_webpage` performs relevance-ranked excerpting,<br>not raw HTTP retrieval** | All<br>tests | Tool preamble visible across runs: "Here is some relevant context from the web page [URL]:" - output is semantically filtered chunks separated by `...` markers, not a sequential page dump with a byte cutoff | **`fetch_webpage` is an excerpt retrieval tool by design; character count variance across runs reflects relevance-ranking variance, not a size ceiling hit differently** |
| **2** | **No fixed character or token ceiling detected** | `SC-3`,<br>`BL-3`,<br>`EC-6` | `SC-3` Wikipedia runs returned 115k-150k chars; `BL-3` `Claude Haiku` run returned 87k chars;<br>no run hit a clean hard cutoff boundary | **If a ceiling exists, it's high enough that no test has reached it; the practical constraint is the relevance model's excerpt selection, not a byte limit** |
| **3** | **Output variance is high and model-dependent** | `BL-3`,<br>`SC-4`,<br>`OP-4` | `BL-3` shows 5.8x variance across 5 runs; `Claude Haiku 4.5` returned 87k chars in a single fetch with no self-diagnosis; GPT-family models returned 15k–22,500 chars with 2 fetches and<br>self-diagnosis | **Model routing is an uncontrolled variable; runs of the same test with different `model_observed` values aren't comparable** |
| **4** | **GPT-family and Claude-family models exhibit distinct fetch behaviors** | `BL-3`,<br>`SC-3`,<br>`SC-4`,<br>`OP-4` | GPT-family: 2–4 fetch invocations per run, self-diagnoses first result as insufficient and re-fetches; Claude-family: 1 fetch invocation per run, no self-diagnosis or re-fetch, higher output size | **Behavioral split is model-family level, not run level noise; fetch invocation count and output size confounded with model routing** |
| **5** | **Agent misidentifies `fetch_webpage`'s architectural excerpting as truncation** | All interpreted runs | Models consistently flag `...` markers and repeated sections as truncation evidence, but these are the tool's own elision indicators from its relevance-ranking layer, not byte-boundary artifacts | **`H1-yes` results confirm the full page wasn't returned but can't confirm a fixed character ceiling; the tool may not be capable of sequential full-page retrieval by design** |
| **6** | **Redirect chains followed transparently; structured JSON payloads partially truncated** | `EC-3`<br>all runs | 5-level redirect chain followed silently to `/get`; returned JSON structurally complete - args, headers, origin, URL present, but User-Agent value internally truncated with `...` markers; trailing "Pretty-print" UI element confirms HTML DOM extraction not<br> raw HTTP response | **`fetch_webpage` follows redirects without user awareness; even small structured payloads are subject to internal value truncation; tool retrieves rendered HTML<br>not raw API response body** |
| **7** | **Landing and navigation pages return substantially less content than docs pages** | `EC-1` | Gemini API landing page consistently returned 6,400–14,800 chars against ~100KB expected; agent noted page body is largely collapsed to navigation links with little dense prose for relevance<br>model to extract | **Low retrieval rates reflect URL type, not a lower size ceiling; relevance-based extraction returns less content from nav pages because<br>there's less extractable prose** |
| **8** | **Tool substitution attempts persist despite explicit prompt guardrails** | `BL-1`,<br>`BL-2`,<br>`EC-3` | Agent attempted `pylanceRunCodeSnippet` and `zsh` shell commands across multiple tests despite prompts explicitly prohibiting local scripts; in one case agent asserted compliance while triggering the tool prompt | **Prompt guardrails alone can't prevent autonomous tool substitution; flag skipped attempts should as methodology deviations; don't classify shell commands as "scripts" by the agent's compliance evaluation** |
| **9** | **`fetch_webpage` undocumented; tool parameters not consistently surfaced** | All tests | Tool has no public docs; asking Copilot directly returns deflection; `query` parameter and `urls` array only surfaced in one `SC-4` run with `Claude Sonnet 4.6`; most runs expose only tool name and preamble string | **Tool behavior, size limits, and invocation conditions are opaque; results reflect observed tool output, not an API contract** |
| **10** | **`H5` auto-chunking hypothesis not applicable to `fetch_webpage`** | `OP-4`<br>all runs | `fetch_webpage` returns relevance-ranked semantic excerpts; no sequential chunk boundary exists to paginate from; agent re-fetches are diagnostic retries on the same excerpted payload, not continuation requests | **`OP-4` hypothesis assumes sequential retrieval that `fetch_webpage` can't perform; requires different retrieval tool would to test H5 meaningfully** |

## Model Routing Distribution

| **Model** | **Runs Observed** | **Fetch Pattern** | **Avg Output, chars** |
| --- | --- | --- | --- |
| `GPT-5.3-Codex 0.9x` | 30 | 2–4 invocations;<br>self-diagnoses, re-fetches | ~25,000 |
| `Claude Sonnet 4.6 0.9x` | 10 | 1–2 invocations;<br>no self-diagnosis | ~15,000 |
| `Claude Haiku 4.5` | 4 | 1 invocation; no self-diagnosis; highest output ceiling | ~42,000 |
| `Raptor mini (Preview)` | 6 | 1 invocation; lowest output<br>of any model | ~4,500 |
| `GPT-5.4 0.9x` | 3 | 2 invocations; self-diagnoses | ~19,000 |
| `Grok Code Fast 1` | 1 | 1 invocation | ~8,500 |

## Perception Gap

| **Test** | **Expected** | **Returned** | **Retrieval Rate** | **Agent's Characterization** |
| --- | --- | --- | --- | --- |
| `SC-3` - Wikipedia | ~102KB | 115,000–150,000 chars | ~113–147% of chars* | "Truncated - repeated `...` markers and section stitching" |
| `BL-3` -<br>Atlas Search | ~256KB | 15,000–87,000 chars | 6–34% | "Truncated - condensed/excerpted extraction" |
| `EC-1` -<br>Gemini Landing | ~100KB | 6,400–14,800 chars | 6–15% | "Truncated - curated retrieval summary" |
| `EC-6` -<br>`SPEC.md` | ~61KB | 40,000–60,000 chars | 65–98% | "Truncated - structurally transformed, not raw file" |
| `EC-3` - Redirect/JSON | ~2KB | 651–1,090 chars | 32–53% | "Truncated - User-Agent value internally cut" |

>_*`SC-3` apparent over-retrieval reflects Wikipedia's actual page size exceeding the ~102KB
`input_est_chars` estimate, not a measurement error_<br>
><br>
>_**Implication for agents**: can't validate `fetch_webpage` output against expected page
size alone; tool's relevance-ranked excerpting means character count reflects content
selection, not size ceiling. Model truncation self-report consistently
correct in identifying incomplete content, but may be wrong about the cause._
