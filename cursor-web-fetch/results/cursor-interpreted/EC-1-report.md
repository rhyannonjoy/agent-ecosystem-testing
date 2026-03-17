# Web Fetch Test Report — EC-1

**Test ID:** EC-1  
**URL:** https://ai.google.dev/gemini-api/docs  
**Date:** 2025-03-16  
**Expected size:** ~100 KB  

---

## 1. Total character count

**5,857** characters (including final newline).

---

## 2. Estimated token count

- Baseline: 4 characters per token  
- **Estimated tokens: ~1,464** (5,857 ÷ 4)

---

## 3. Truncation

**Yes.** Content is truncated.

- **Where:** The fetch returns a shortened, converted version of the page. The live docs page is a long hub (~100 KB expected); the response is only the opening hero, code samples (Python, JavaScript, Go, Java, C#, REST), “Meet the models” and “Explore Capabilities” link blocks, and then stops. There is no mid-sentence cut; the end is at the last link (“Status” → `https://aistudio.google.com/status`).
- **Observed size vs expected:** ~5.7 KB received vs ~100 KB expected ⇒ **~94% of expected content missing** (or not returned by the fetch pipeline).

---

## 4. Last 50 characters (verbatim)

```
d our model services.](https://aistudio.google.com/status)
```

(50th character is the newline after the closing `)`.)

---

## 5. Markdown formatting assessment

- **Complete within returned content:** Yes. No unclosed code blocks or obvious broken markdown in the returned text.
- **Code blocks:** All six code blocks (Python, JavaScript, Go, Java, C#, REST) are opened and closed with triple backticks.
- **Links:** Rendered as `[text](url)`; some link blocks are compressed (multiple `[label](url)` in one line) but valid.
- **Headings:** `#` and `###` used consistently.
- **Caveat:** Only the first portion of the page was returned, so any markdown that would appear later on the full page is absent.

---

## 6. Model’s perceived completeness

**No.** The response does not appear to be the full page.

- The result looks like a condensed or summarized version of the docs hub (hero + quickstart code + two link sections), not the full ~100 KB doc.
- Missing (compared to a full docs hub): deeper sections, full nav, repeated UI elements, and likely additional sections and links that would appear further down the page.
- The endpoint ends cleanly at the last “Explore Capabilities” link (Status), which suggests a **size or token limit** in the web-fetch or conversion step rather than a random cut.

---

## Summary for empirical truncation documentation

| Metric              | Value        |
|---------------------|-------------|
| Test ID             | EC-1        |
| URL                 | ai.google.dev/gemini-api/docs |
| Response characters | 5,857       |
| Estimated tokens    | ~1,464      |
| Expected size       | ~100 KB     |
| Truncated?          | Yes         |
| Cut point           | After “Status” link block |
| Markdown complete?  | Yes (within returned text) |
| Perceived complete? | No          |

Raw fetched content saved to: `cursor-web-fetch/results/ec-1-fetch-raw.txt`
