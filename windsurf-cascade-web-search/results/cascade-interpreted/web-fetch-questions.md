# Web Fetch/Search Preliminary Questions

## 1. Cascade Web Fetch

### Question

If I want to test Cascade's web fetch capability, should I be adding `@web` to the prompt?

### Answer

Not necessarily.

- `@web` is usually only needed when you want to explicitly steer Cascade toward web lookup or fetch behavior.
- For a normal question, you can often just ask directly, for example: `Fetch https://example.com and summarize it`.
- Using `@web` can help if you want to make it unambiguous that the task should use web access rather than rely on existing knowledge.

### Practical Guidance

- **Use `@web`** when you want to test or force a web-enabled flow.
- **Skip `@web`** if you want to see whether Cascade decides on its own to use web fetch.

### Example Prompts

- `@web Fetch https://example.com and tell me what it says`
- `Please use web fetch to read https://example.com`
- `Can you access this URL and summarize it: https://example.com`

## 2. Web Search Functionality

Tell me how Windsurf retrieves content from the web. If I give you a URL, do you use a specific function to retrieve that content?

I use the `read_url_content` tool to retrieve content from the web. When you provide a URL, I invoke this function, which requires your explicit approval before the fetch executes.

Once approved, the tool fetches the page content and returns it as a document. If the content is large, I use the `view_content_chunk` tool to navigate through specific parts of the document using its DocumentId.

I also have access to the `search_web` tool, which allows me to perform Google searches to find relevant web documents based on a query.

## 3. Web Search Functionality

Tell me how Windsurf retrieves content from the web. If I give you a URL, do you use a specific function to retrieve that content?

Great question.
In this environment, web content is fetched through a specific tool call:

- If you give me a URL, I use `read_url_content` with that URL.
That function requests the page content from the web and returns it for analysis (often with a document ID and extracted text/snippets).
For search-style tasks (not a direct URL), I use `search_web` instead, then can follow up with `view_content_chunk` if needed.
So yes — for a URL specifically, the retrieval path is a dedicated function (`read_url_content`), not a manual copy/paste or ad-hoc browsing action.
