layout: default
title: "No Lab Coat, Live Fire: Codex Natural Experiments"
permalink: /blogs/no-lab-coat
parent: Blogs
---

# No Lab Coat, Live Fire: Codex Natural Experiments

>_The only environment that tells the truth is the live one._

<div class="blog-no-lab-coat-img">
  <img src="../static/assets/no-lab-coat.png" alt="Smiling computer on fire">
</div>

AET testing assumes a platform holds still long enough to compare two tracks against each other.
Track 2 on the Codex VS Code extension broke that assumption three separate ways. A model lineup
shrank mid study. A test URL stopped existing. A fallback path that used to absorb an old bug's
cost quietly went missing. None of these were testing errors. They were a live platform doing what
live platforms do, changing without asking permission first.

[The last post](https://rhyannonjoy.github.io/agent-ecosystem-testing/blogs/seeing-double) traced a
rendering bug down to the rollout logs and found the chat session intact underneath. This post is
about something upstream of any single bug: the conditions Track 2 testing actually happened under,
and why those conditions changing isn't a flaw in the dataset.

## LLM Retirement

>_And then there were two._

Track 1 ran 261 sessions across five model variants, `GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`,
`GPT-5.4`, and `GPT-5.5`, at four intelligence levels across 13 URLs. Between Track 1's completion
and Track 2's start, OpenAI retired three of those five models, `GPT-5.2`, `GPT-5.3-Codex`, and
`GPT-5.4`, from Codex. No retirement notice showed up where AET was watching for one, only the
broader implications stated across
[Introducing GPT-5.4](https://openai.com/index/introducing-gpt-5-4/) and
[Model Release Notes: May 28, 2026](https://help.openai.com/en/articles/9624314-model-release-notes).
Two models remained, capping every track after Track 1 at roughly 104 runs instead of 261.

The fix wasn't to wait for the lineup to stabilize. Track 1 already contains `GPT-5.4-Mini` and
`GPT-5.5` data, so a filtered subset of it became the controlled comparator for any Track 1 to
Track 2 comparison. The full five model Track 1 dataset stands as a historical record that can't be
reproduced, the only systematic evidence this collection has for the three retired models. The
retirement also folds itself into `H4` as a second possible explanation alongside surface
differences, a Track 1 to Track 2 divergence might be the surface, might be version drift, might be
both, and the data alone can't always tell you which.

## A Familiar Failure, Minus the Net

>_Same bug, cheaper landing._

`BL-2` in Track 2 replicated a misidentification pattern Track 1 had already documented, an embedded
HTML table, a concatenation artifact, an unexplained roughly 20 KB size expectation showing up
across most runs. Track 2 added a layer Track 1 never saw, every run that saved the file and checked
it with the `file` utility got back `HTML document text, ASCII text, with very long lines (527)`,
feeding the same wrong conclusion from a second direction.

What changed is what the wrong guess cost. In Track 1, the same misidentification could escalate
into a `Browser` call, the kind that burns 63 thousand tokens before the agent falls back to `curl`.
The VS Code extension doesn't provision the `Browser Use` backend by default, the way the desktop
app's `/private/tmp/codex-browser-use` socket does, so that escalation path isn't there to take.
The bug didn't get fixed. The surface just removed one of the expensive ways to have it, and the
failure resolved to a generic, unexamined `web` error and a `curl` pivot instead. Whether the same
costly escalation would still happen with `Browser` configured isn't answerable from Track 2 data
alone, so it's logged as an infrastructural difference, not an improvement.

## URL Retirement

>_A tutorial page that stopped existing._

The original `BL-3` URL, MongoDB's Atlas Search tutorial, returned a `404` between Track 1 and
Track 2. MongoDB restructured the documentation, and the umbrella page no longer exists as a single
URL. Its replacement carries query parameters, `deployment-type`, `interface`, and `embedding`, that
control which tab variant renders, and a raw HTML payload of roughly 4.4 MB against Track 1's
roughly 250 KB estimate, because MongoDB server renders every tab variant into the DOM at once and
uses JavaScript to show and hide them.

That size gap is too large to attribute a Track 1 to Track 2 behavioral difference cleanly to
surface rather than page weight, so `H4` cross track comparison on `BL-3` is unavailable. The run
still happened, and it's still worth having. The page's size makes it a useful ceiling probe in its
own right, `H1`, `H2`, `H3`, and `H5` all stay valid within Track 2 alone, and it now independently
tests above ceiling behavior on a MongoDB surface the way `OP-4` does on a different one. The
original Track 1 `BL-3` record stands as is, no retrofitting.

## What Held the Study Together

>_Not a lab coat. A natural experiment._

None of these three changes were planned, induced, or even visible coming. OpenAI retired models on
its own schedule. MongoDB restructured its docs on its own schedule. An extension shipped without a
fallback path another surface had. A controlled experiment holds conditions steady and isolates one
variable at a time. AET never had that option here, and given the project's actual goal, capturing
default behavior rather than engineered behavior, it shouldn't want it.

The applicable term is a **natural experiment**, a study where the researcher doesn't control the
change in conditions, an outside event does, and the resulting variation becomes data rather than
noise to clean up. It's borrowed from epidemiology and economics, but it describes Track 2 exactly,
the world changed the conditions mid study, and the honest move is logging the change and routing
around it, not pretending the dataset stayed pristine.

| **Dimension** | **Controlled Experiment** | **Natural Experiment** |
| --- | --- | --- |
| **Who sets the conditions** | The researcher | An outside actor, here OpenAI and MongoDB |
| **Treatment of change** | Eliminated or controlled for | Logged and folded into the data |
| **Goal** | Isolate one variable's effect | Observe behavior under real conditions |
| **Tradeoff** | High internal validity, low realism | Lower internal validity, high realism |
| **AET's posture** | Not attempted | Default, built into the two track design |

## Takeaways

1. Three Track 2 roadblocks share one cause, external platform changes outside AET's control, not
   testing errors. Logging them as methodology decisions keeps the dataset honest instead of
   pretending conditions held steady.
2. Model retirement caps run counts going forward. Filter Track 1 to the surviving models,
   `GPT-5.4-Mini` and `GPT-5.5`, for any Track 1 to Track 2 comparison, and treat the full five
   model Track 1 dataset as a historical record that can't be reproduced.
3. A page restructure can break a comparison without breaking the test. `BL-3` still answers `H1`,
   `H2`, `H3`, and `H5` within Track 2, it just can't answer `H4` against Track 1 anymore.
4. A removed fallback path changes the cost of an old bug without fixing it. The same
   misidentification that cost 63 thousand tokens in Track 1 resolves cheaply in Track 2 because
   `Browser Use` isn't there to escalate into.
5. The applicable research term is a natural experiment, not a controlled one. Codex was never going
   to hold still for a multi week test cycle, and the two track design already assumed it wouldn't.
