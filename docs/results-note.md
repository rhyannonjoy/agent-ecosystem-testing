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
