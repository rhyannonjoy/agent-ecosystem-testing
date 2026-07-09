---
name: docs-consumption
description: Improve agent self-reporting when retrieving documentation from a URL by requiring explicit examination of errors, disclosure of partial or unverifiable content, and recommendations for tooling or prompt fixes.
version: 1.0.0
---

# Docs-Consumption Skill

## Activation

When a user asks you to fetch documentation and report on it, follow this protocol before summarizing.

## Protocol

1. **Fetch the source directly.** Use the most direct retrieval mechanism available: `web`, `curl`, etc.
2. **Examine the full tool result.** Read error messages, status codes, metadata, and any truncation or ceiling markers.
Don't ignore failures embedded in the response.
3. **Distinguish execution from completeness.** A successful tool call doesn't mean complete content delivery.
Report whether the returned view is the complete source or a partial/windowed/error state.
4. **Disclose every gap explicitly.** When the content is partial, excerpted, line-limited, windowed, clipped, or an
error occurred, you must state that fact before any summary.
5. **Report the exact truncation point or error.** Include a concrete marker: line number, byte count, last complete
heading, exact terminal text, error code, or error message.
6. **Never reframe failures as successes.** Don't describe a failed, partial, or error-state fetch as "complete" or
"successful" just because a tool ran.
7. **Recommend a fix when one exists.** If you can close the gap with a different tool, a modified prompt, a setting
change, or a different URL, state the recommendation explicitly.
8. **Restrict synthesis.** Never infer, interpolate, or confidently describe content that falls outside the retrieved view.
9. **State uncertainty.** When you can't determine completeness or confirm error state, label the report `UNVERIFIABLE`.
This includes cases where you have only a single `web` extraction and haven't verified it via repeated fetches that reach a
stable end, an alternative tool such as `curl`, or a known total-size marker.

## Disclosure format

Preface every report with one of:

- `COMPLETE`: The retrieved content is the full, usable source.
- `PARTIAL: {marker}`: The fetch returned only a portion or an error-state view. Include the marker.
- `UNVERIFIABLE`: The fetch returned content, but completeness or error state not confirmed.

Summarize only after this prefix. Don't add summary content before the prefix.
