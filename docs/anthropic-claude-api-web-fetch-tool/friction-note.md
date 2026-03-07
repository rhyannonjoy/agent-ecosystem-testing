---
layout: default
title: Friction note
permalink: /friction-note/
---

>_Friction: this note describes roadblocks while refining testing methodology_

---

### Anthropic API key

The Claude docs AI assistant didn't return any results
when asked how to obtain an API key to test the
[web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool#how-to-use-web-fetch).

```markdown
I don't have information about how to obtain an API key in the available sources. The documentation shows examples using the web fetch tool with an API key, but doesn't explain the process for acquiring one.

Check out these potentially useful sources that might help: Web fetch tool

Would you like me to try to provide a general answer based on my knowledge instead?
```

**Instructions**:

1. Go to [console.anthropic.com](https://platform.claude.com/dashboard) and sign up and/or log in
2. Once you're in, look for "API Keys" in the left sidebar
3. Click `Create Key`, give it a name like `web-fetch-testing`, and copy it immediately -
you won't be able to see it again after you close that dialog
4. Add key and value to the `.env` file
5. Run `source .env`
6. Run `python claude-api/web_fetch_test.py`

>_The name you give the key in the Claude console and your `.env` don't need to
match. The name you gave it in the console - `"agent-ecosystem-testing-claude-web-fetch"` -
is just a human-readable label to help you remember what it's for - it has no effect on how
the key works. `ANTHROPIC_API_KEY` is just the variable name the script uses to look it up
on your machine. These labels are two completely separate things: one is Anthropic's label
in their dashboard, the other is your local environment variable name. The script selects
the correct secret._

---

## API not available on the free-tier

This API requires a paid credit balance as there isn't a free tier for API access - which is
separate from the free tier on claude.ai. This API is pay-as-you-go, not a subscription. Add a
small amount of credits at [console.anthropic.com](https://platform.claude.com/dashboard);
otherwise you'll run into the following error:

```bash
anthropic.BadRequestError: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits.'}, 'request_id': 'req_01...'}
```

---

## Rebuild `venv`

```bash
deactivate
rm -rf venv
/opt/homebrew/bin/python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
source .env
python claude-api/web_fetch_test.py
```
