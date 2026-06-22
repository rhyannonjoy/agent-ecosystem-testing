---
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

AET borrows from a handful of ideas across conventional research methodology and software testing.
[Natural experiments](https://en.wikipedia.org/wiki/Natural_experiment) describe studies in which
researchers observe conditions determined by factors outside their control, and the variation becomes
data instead of noise to clean up.
[Testing software in production](https://bugbug.io/blog/software-testing/production-testing/)
is similar where staged and QA
environments are artificially stable in ways that hide real failure modes, and only the live environment
with live dependencies, deprecation, removal, and restructuring tell the truth.
[Usability testing](https://en.wikipedia.org/wiki/Usability_testing) supplies the third piece, documenting
attempts to use something for its intended purpose and noting where it holds up or doesn't. Chat-based
testing in this collection, like that used in [the Codex methodology](../docs/open-ai-codex/methodology.md),
involves a hybrid approach in which the framework supplies agents a task in a way an ordinary user would.
Assessment includes capturing variance through agent self-reports, app logs, and programmatic verification
the same way an engineer investigating a bug would, but the results remain for users. Findings get
documented, not fixed.

Codex testing initially assumed the platform would hold long enough to compare two tracks against each
other, but observing agent web fetch behavior on the Codex VS Code extension broke that assumption
quickly in a couple of ways. LLM lineup shrunk mid-track, a test URL went from unstable to deleted.
Both changes arrived the same way, an external decision, no warning, and required adjustment
to proceed.

## LLM Retirement

>_And then there were two._

Track 1 included this collection's most ambitious data set with 261 sessions across five LLM variants,
`GPT-5.2`, `GPT-5.3-Codex`, `GPT-5.4-Mini`, `GPT-5.4`, and `GPT-5.5`, at four reasoning levels across 13 URLs.
Between Track 1's completion and Track 2's start, OpenAI retired three of those five models, `GPT-5.2`,
`GPT-5.3-Codex`, and `GPT-5.4`. No retirement notice showed up where AET was watching for one, no obvious
changelog links in the chat, only the broader implications stated across
[Introducing GPT-5.4](https://openai.com/index/introducing-gpt-5-4/) and
[Model Release Notes: May 28, 2026](https://help.openai.com/en/articles/9624314-model-release-notes).
Two LLMs remained, cutting runs and results by 40%.

AET's purpose isn't about tracking individual LLM performance, but about documenting agent web fetch behavior
across platforms in service of everyday practitioners, and
_["an agent is more than its brain."](https://dacharycarey.com/2026/03/02/an-agent-is-more-than-its-brain/)_
Track 1 stands as an irreproducible historical record and includes the only systematic evidence this
collection has for the three retired LLMs. A filtered subset of Track 1 became the controlled comparator for
any track-to-track comparison. The retirement also folds itself into the surface impact hypothesis as an
additional possible explanation alongside version drift, and the data alone can't always separate them.

## URL Retirement

>_`404` between tracks._

The original `BL-3` test URL, a MongoDB tutorial, remained stable across five AET test cycles, but started to
[show instability across Codex's Track 1](../docs/open-ai-codex/friction-note-interpreted-desktop.md#url-instability-mid-testing)
before becoming completely
[unavailable for Track 2](../docs/open-ai-codex/friction-note-interpreted-extension.md#url-retirement).
MongoDB hasn't issued a clear user path beyond the `404`, suggesting a documentation
restructuring without an obvious paper trail. While using the same targets across cycles offers a semblance of
consistency to facilitate comparison, it's not imperative that each target include semantically similar content
more than architecturally similar documentation. With that said, testing approach adaptation became an
opportunity to stress test Codex agents with something similar, but all together more complex.
[`BL-3` replacement target](https://www.mongodb.com/docs/vector-search/tutorials/quick-start/?deployment-type=atlas&interface=atlas-ui&embedding=auto)
includes components no other cycle has tested, a slew of query parameters and a raw HTML payload of ~4.4 MB
against the original's ~250 KB.

While the page weight gap is too large to attribute a track-to-track behavioral difference directly to surface,
the `BL-3` desktop vs extension hypothesis remains untested. The test is still worth running and the data is
still worth collecting. The page's size make it a useful ceiling probe as the character, token, structure-aware,
and pagination hypotheses all stay valid. The Track 1 `BL-3` record stands alone without any retrofitting, but
the replacement target URL remains part of Tracks 3 and 4 unless MongoDB throws more curveballs.

## Build for Change

Software is all change and testing. LLM lineups shift without changelogs. Documentation
restructures without redirects. The live environment doesn't hold still and doesn't explain itself.
For developers building agentic systems and documentation teams making their work agent-friendly:

- **Pin versions, monitor.** Assume the platform can pull any LLM at any time without notice.
- **Test continuously.** The live environment changes independently of the test target system.
  A behavioral baseline that held last month may not hold today.
- **Changes don't invalidate testing, they justify it.** A retired LLM, a restructured URL,
  a removed fallback path, deprecated tools, each one is evidence of exactly the kind of drift that
  testing exists to detect.
