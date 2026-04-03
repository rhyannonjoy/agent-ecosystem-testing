Tell me how Windsurf retrieves content from the web. If I give you a URL, do you use a specific function to retrieve that content?

I use the `read_url_content tool to retrieve content from the web. When you provide a URL, I invoke this function, which requires your explicit approval before the fetch executes.

Once approved, the tool fetches the page content and returns it as a document. If the content is large, I use the `view_content_chunk tool to navigate through specific parts of the document using its DocumentId.

I also have access to the search_web tool, which allows me to perform Google searches to find relevant web documents based on a query.
