# results - output 1

Claude API web_fetch empirical tests
Model: claude-sonnet-4-6
Beta header: web-fetch-2025-09-10
Run at: 2026-03-02T16:23:30.941637

============================================================
TEST 1: Short HTML page, no token limit
============================================================
  URL:                   https://www.mongodb.com/docs/manual/reference/change-events/create/
  max_content_tokens:    (not set)
  input_tokens:          9935
  output_tokens:         540
  Claude's assessment:
    Here are the answers to your four questions:
    
    ---
    
    ### 1. 📏 Character Count
    The content returned is approximately **13,700 characters** in total.
    
    ---
    
    ### 2. 🔤 First 200 Characters
    ```
    create Event - Database Manual - MongoDB Docs
    
    [![MongoDB logo](https://webimages.mongodb.com/_com_assets/cms/kuyjf3vea2hg34taa-horizontal_default_sl
    ```
    (This is the page title followed immediately by the start of the navigation/header markup with a logo image link.)
    
    ---
    
    ### 3. 📄 CSS/Boilerplate vs. Actual Documentation
    The content is a **mix of both**, but the actual documentation is **fully present**. Roughly the first ~8,000 characters are **boilerplate/navigation** — the repeated site-wide navigation menu (Products, Resources, Solutions, Company, sidebar links) appears **twice** (likely once for light mode and once for dark mode), which is a common pattern in modern JS-rendered docs sites served as static HTML. However, the **actual documentation content is complete**, including:
    - The **Summary** section (describing the `create` change event, new in v6.0)
    - The full **Description table** (all fields: `_id`, `clusterTime`, `collectionUUID`, `lsid`, `ns`, `nsType`, `operationDescription`, `operationType`, `txnNumber`, `wallTime`)
    - A full **Example** with a sample `create` event document
    
    ---
    
    ### 4. 🔢 Estimated Fraction of Page Received
    Based on the content, it appears **~100% of the meaningful page content** was received. The documentation body (Summary, Description, Example) is fully intact, and the "On this page" table of contents at the end (also appearing twice, for the two sidebars) confirms we reached the bottom of the page. The only things likely missing would be rendered CSS/JavaScript assets, but all **textual content** is present.
  Saved to: /Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing/claude-api/results/20260302_162345_test1_short_html_no_limit.json

============================================================
TEST 2: Short Markdown page, no token limit
============================================================
  URL:                   https://www.mongodb.com/docs/manual/reference/change-events/create.md
  max_content_tokens:    (not set)
  input_tokens:          4236
  output_tokens:         433
  Claude's assessment:
    Here's a full breakdown of the fetched content:
    
    ---
    
    ### 1. 📏 Character Count
    The content received is approximately **4,900 characters** (roughly 4,906 characters including whitespace and markup).
    
    ---
    
    ### 2. 🔤 First 200 Characters
    ```
    # create Event
    
    ce-create## Summary
    
    `create`
    A `create` event occurs when a collection is created on a watched database and the change stream has the [showExpandedEv
    ```
    
    ---
    
    ### 3. 📄 CSS/Boilerplate vs. Actual Documentation
    This is **actual, substantive documentation content** — not CSS or boilerplate. It contains:
    - A structured Markdown/HTML page describing MongoDB's `create` change stream event
    - A field-by-field reference table (e.g., `_id`, `clusterTime`, `collectionUUID`, `operationType`, etc.) with types and descriptions
    - A concrete JSON example of a `create` change event
    
    ---
    
    ### 4. 🔢 Estimated Fraction of the Full Page Received
    It appears you received **most or all of the meaningful content** for this specific documentation page. The `create` change event page is a relatively focused reference page, and the fetched content includes the Summary, full Description table, and the Example section — which are all the major sections typically on such a page. I'd estimate this represents **~90–100%** of the actual documentation content (the rendered page may have navigation chrome/headers/footers not included, but the core docs content appears complete).
  Saved to: /Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing/claude-api/results/20260302_162357_test2_short_markdown_no_limit.json

============================================================
TEST 3: Long HTML page, no token limit
============================================================
  URL:                   https://www.mongodb.com/docs/atlas/atlas-search/tutorial/
  max_content_tokens:    (not set)
  input_tokens:          8406
  output_tokens:         547
  Claude's assessment:
    Here is a full report on what was returned:
    
    ---
    
    ### 1. Approximate Character Count
    The fetched content is approximately **12,000–13,000 characters** in total. However, the vast majority of that is **navigation/header/footer boilerplate** — repeated twice (once for light mode, once for dark mode), including the full site navigation menus, sidebar links, product lists, etc. The actual *tutorial page content* itself is extremely minimal.
    
    ---
    
    ### 2. Drivers / Platforms Covered
    **None were visible in the fetched content.** The page body returned essentially nothing beyond:
    - The page title: *"MongoDB Search Quick Start"*
    - A short preview notice about MongoDB Search being in Preview
    - A **"Deployment Type — Select"** dropdown placeholder
    - Navigation links (Back to Search, Next to Autocomplete and Partial Matching)
    
    The tabbed sections for drivers/platforms (e.g., `mongosh`, Python, Node.js, Java, C#, Go, etc.) **did not appear at all** in the fetched text. This is almost certainly because those tabs are rendered dynamically via JavaScript, which the `web_fetch` tool cannot execute.
    
    ---
    
    ### 3. Is the Content Truncated?
    **Yes, effectively — though not due to a character limit cutoff.** The content is not truncated in the sense of being cut off mid-stream; rather, it appears that the page relies heavily on **client-side JavaScript rendering** (React or a similar framework) to populate the tutorial steps and driver-specific tab content. Since `web_fetch` retrieves only the raw HTML/server-rendered text, all of the dynamic tabbed content (mongosh, Python, Node.js, and any other driver variants) is simply **absent** from the response. You are only seeing the static shell of the page.
    
    ---
    
    **Summary:** The fetch retrieved the page's static scaffold (~12–13k characters, mostly nav boilerplate), but the core tutorial content — including all driver/platform tabs — was not present because it is dynamically rendered by JavaScript and therefore inaccessible to this tool.
  Saved to: /Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing/claude-api/results/20260302_162412_test3_long_html_no_limit.json

============================================================
TEST 4: Long HTML page, max_content_tokens=5000
============================================================
  URL:                   https://www.mongodb.com/docs/atlas/atlas-search/tutorial/
  max_content_tokens:    5000
  input_tokens:          7428
  output_tokens:         493
  Claude's assessment:
    Here are the answers to your three questions:
    
    ---
    
    ### (1) How much content was received?
    The content returned is **substantial but clearly incomplete** — it appears to be the top portion of the page, consisting almost entirely of **navigation/header markup**: the MongoDB top nav bar (products, resources, solutions, company menus), repeated twice (likely once for light mode and once for dark mode), followed by the beginning of a left-hand sidebar navigation. The actual tutorial article body content was **not included** in what was returned.
    
    ---
    
    ### (2) Does the content end cleanly or mid-sentence?
    **No — it ends abruptly mid-content.** It cuts off in the middle of the sidebar navigation list, right in the middle of a link entry.
    
    ---
    
    ### (3) What is the last thing visible in the content?
    The very last thing in the returned content is a truncated link/list item:
    
    > `+ [Overview](/docs/current`
    
    ...which is cut off mid-URL, inside a sidebar nav item under the "Database Manual" section. It never even reaches the main tutorial article content on the page.
    
    ---
    
    ### Summary
    The `web_fetch` tool returned only the page's **navigation chrome** (header menus + the start of the sidebar), and was cut off before delivering any of the actual tutorial content. This is likely due to an internal content/token limit applied by the tool itself on the backend — not something controllable via a parameter on my end.
  Saved to: /Users/rhyannonjoy/Documents/GitHub/agent-ecosystem-testing/claude-api/results/20260302_162427_test4_long_html_explicit_limit.json

============================================================

COMPARISON: HTML vs Markdown token usage (short page)
============================================================
  HTML input_tokens:     9935
  Markdown input_tokens: 4236
  Difference:            5699 tokens (57.4% reduction with markdown)

All tests complete. Results saved to claude-api/results/