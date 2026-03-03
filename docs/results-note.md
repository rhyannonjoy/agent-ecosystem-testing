# `/results` note

`/results` is a directory that gets created automatically
when you run the script - it likely doesn't exist yet.
The script creates it with this line:

```python
results_dir = Path(__file__).parent / "results"
results_dir.mkdir(exist_ok=True)
```

Each time you run a test, it saves a `.json` file inside it, like:

```bash
claude-api/results/20260302_142301_test1_short_html_no_limit.json
```

JSON is just a data format; it's the raw output from each API call
so you have a record of exactly what came back.

**Should `/results` be committed?** These are likely more helpful
published for contributors to review, but reconsider as you test.

## First iteration limits

Claude is interpreting what it received, not a raw dump. That's why the
character counts vary slightly between runs - Claude is estimating, not
measuring precisely. The reliable, objective data in our results is actually
the token counts in the usage block, which come directly from the API response
metadata and don't pass through Claude's interpretation at all.

We're relying on Claude to tell us what it received, rather than inspecting the
raw fetch result directly. The script does try to capture the raw content length
from the web_fetch_tool_result block, but that part isn't working reliably -
`fetch_content_length_chars` is showing 0 in the results.

## Second iteration differences

Claude's role is minimal. The prompt is just `"Fetch this URL: {url}" with max_tokens=128` —
we only need Claude to trigger the fetch, not describe anything. This also makes
it much cheaper to run.

All analysis is Python. The `analyze_content()` function measures directly from
the raw string - exact character counts, CSS indicator detection in the first 2000
chars, where the first heading appears, whether the content ends cleanly or mid-word.
No estimation, no interpretation.

Output files - `_raw_results.json` and `_raw_summary.md` so they don't collide
with the files from `web_fetch_test.py`.

> _The raw content extraction depends on the `web_fetch_tool_result` block having a specific
structure. If the API response format differs from what the script expects, `raw_content_chars`
show `None`- which is itself a useful finding to document._
