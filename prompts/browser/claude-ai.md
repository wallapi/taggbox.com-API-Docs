# claude.ai - build a Taggbox social wall

Use this when you are chatting with claude.ai in the browser. It cannot touch
your computer, so the prompts below make it hand you complete files plus a
setup checklist, and forbid it from asking questions before the code.

## 1. Get the spec file

Download [llms.txt](https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/llms.txt) to your computer
(right-click the link, "Save link as...", keep the name `llms.txt`), or in a
terminal:

```bash
curl -sSLo llms.txt https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/llms.txt
```

## 2. Start the chat and attach the spec

1. Open https://claude.ai and start a **new chat**.
2. Click the **+** button in the message box, choose **Upload a file**, and
   pick `llms.txt` (or drag it into the chat).
3. Paste the prompt from step 3 and send.

Claude usually puts each file in an **Artifact** panel on the right with a
**Download** button - use it and rename if needed so the filename matches the
`### FILE:` header exactly. Claude tends to start coding without asking; if it
does ask, reply "build it with the defaults in the prompt".

## 3. Paste ONE of these prompts

Pick your language. Paste the whole block as your first message, with
llms.txt attached (or its full contents pasted underneath).

### PHP

```
Build me a social wall: one web page that shows the live posts from my
Taggbox wall, using the Taggbox Developer API v3. The full spec is in the
attached llms.txt (also at https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/llms.txt).
Follow it exactly, including its "Integration rules for generated code".

Deliverable mode - you cannot access my computer:
- Do NOT ask me anything before writing code. Everything you need is in the
  spec and below. No plan and no summary first - start with the files.
- Output every file COMPLETE and ready to save. Start each with a header
  line naming its exact path, e.g. `### FILE: index.php`.
- After the files, give me a SETUP CHECKLIST for someone who has never used
  a terminal: where to save each file, how to set the two environment
  variables on macOS/Linux (export) and on Windows PowerShell ($env:), the
  exact command to run, the URL to open, and a curl test with the expected
  output.
- If I report an error, reply with the corrected COMPLETE file, not a diff.

Tech:
- PHP 8+, one self-contained index.php. No Composer; use the curl_* functions.
- File cache: taggbox-cache.json written next to index.php.
- Must run with the built-in server: php -S localhost:8080

Fixed requirements:
- Read the credential from the TAGGBOX_ACCESS_TOKEN environment variable
  (an account access token or a wt1_ wall token both work) and the base URL
  from TAGGBOX_API_BASE, defaulting to https://staging-apis.taggbox.com/api.
  Never hard-code either; the token must never reach the browser.
- Fetch GET {base}/v3/posts?limit=24 server-side with the header
  Authorization: Bearer <token>. The payload is inside the envelope:
  body.posts and body.paging.
- Check the HTTP status AND the envelope's `status` flag; on 422 log
  body.fields so I can see which parameter was wrong.
- Keep the API's default sort (pinned first, then newest) - do not override it.
- Cache the response for 5 minutes. If the API call fails, serve the last
  good cached copy so the wall never renders blank; with no cache at all,
  show an empty state with a friendly message.
- For each post render: author.name, network.name, media[0].cdn_url as an
  <img> (or a <video> when media[0].type is "video"; omit the element when
  media is empty), content.text as escaped TEXT (never as HTML), and
  source.permalink as a "View original" link when present.
- Escape all output (XSS). Semantic markup and minimal CSS I can extend.
```

### Node.js

```
Build me a social wall: one web page that shows the live posts from my
Taggbox wall, using the Taggbox Developer API v3. The full spec is in the
attached llms.txt (also at https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/llms.txt).
Follow it exactly, including its "Integration rules for generated code".

Deliverable mode - you cannot access my computer:
- Do NOT ask me anything before writing code. Everything you need is in the
  spec and below. No plan and no summary first - start with the files.
- Output every file COMPLETE and ready to save. Start each with a header
  line naming its exact path, e.g. `### FILE: server.js`.
- After the files, give me a SETUP CHECKLIST for someone who has never used
  a terminal: where to save each file, how to set the two environment
  variables on macOS/Linux (export) and on Windows PowerShell ($env:), the
  exact command to run, the URL to open, and a curl test with the expected
  output.
- If I report an error, reply with the corrected COMPLETE file, not a diff.

Tech:
- Node.js 18+ with Express: exactly two files, server.js and package.json.
  Use the built-in fetch; express is the only dependency.
- In-memory cache (a module-level variable is fine).
- Must run with: npm install, then node server.js, on port 3000.

Fixed requirements:
- Read the credential from the TAGGBOX_ACCESS_TOKEN environment variable
  (an account access token or a wt1_ wall token both work) and the base URL
  from TAGGBOX_API_BASE, defaulting to https://staging-apis.taggbox.com/api.
  Never hard-code either; the token must never reach the browser.
- Fetch GET {base}/v3/posts?limit=24 server-side with the header
  Authorization: Bearer <token>. The payload is inside the envelope:
  body.posts and body.paging.
- Check the HTTP status AND the envelope's `status` flag; on 422 log
  body.fields so I can see which parameter was wrong.
- Keep the API's default sort (pinned first, then newest) - do not override it.
- Cache the response for 5 minutes. If the API call fails, serve the last
  good cached copy so the wall never renders blank; with no cache at all,
  show an empty state with a friendly message.
- For each post render: author.name, network.name, media[0].cdn_url as an
  <img> (or a <video> when media[0].type is "video"; omit the element when
  media is empty), content.text as escaped TEXT (never as HTML), and
  source.permalink as a "View original" link when present.
- Escape all output (XSS). Semantic markup and minimal CSS I can extend.
```

## 4. Save the files it gives you

For every `### FILE:` block: click the copy button on the code block, open a
plain-text editor (macOS: TextEdit with Format > Make Plain Text; Windows:
Notepad; or VS Code), paste, and save with the exact filename shown into a
new folder called `my-social-wall`. Do not let the editor add `.txt`.

### Run it (PHP)

Check the runtime once:

```bash
php -v    # must print PHP 8.x
```

Install PHP if the check fails: macOS `brew install php`, Windows https://windows.php.net/download, Ubuntu `sudo apt install php-cli php-curl`.

macOS / Linux (Terminal):

```bash
cd my-social-wall
export TAGGBOX_ACCESS_TOKEN="wt1_your_token_here"
export TAGGBOX_API_BASE="https://staging-apis.taggbox.com/api"
php -S localhost:8080
```

Windows (PowerShell):

```powershell
cd my-social-wall
$env:TAGGBOX_ACCESS_TOKEN="wt1_your_token_here"
$env:TAGGBOX_API_BASE="https://staging-apis.taggbox.com/api"
php -S localhost:8080
```

Open http://localhost:8080 in your browser. Stop the server with Ctrl+C.

Verify the API side independently of the page:

```bash
curl -s -H "Authorization: Bearer $TAGGBOX_ACCESS_TOKEN" "$TAGGBOX_API_BASE/v3/posts?limit=1"
```

You should see `"status":true` and one post inside `body.posts`. A 401 means
the token is wrong or the API is disabled for the account; the message says
which.

### Run it (Node.js)

Check the runtime once:

```bash
node -v   # must print v18 or higher
```

Install Node.js from https://nodejs.org (LTS) if the check fails.

macOS / Linux (Terminal):

```bash
cd my-social-wall
npm install
export TAGGBOX_ACCESS_TOKEN="wt1_your_token_here"
export TAGGBOX_API_BASE="https://staging-apis.taggbox.com/api"
node server.js
```

Windows (PowerShell):

```powershell
cd my-social-wall
npm install
$env:TAGGBOX_ACCESS_TOKEN="wt1_your_token_here"
$env:TAGGBOX_API_BASE="https://staging-apis.taggbox.com/api"
node server.js
```

Open http://localhost:3000 in your browser. Stop the server with Ctrl+C.

Verify the API side independently of the page:

```bash
curl -s -H "Authorization: Bearer $TAGGBOX_ACCESS_TOKEN" "$TAGGBOX_API_BASE/v3/posts?limit=1"
```

You should see `"status":true` and one post inside `body.posts`. A 401 means
the token is wrong or the API is disabled for the account; the message says
which.

## If it goes wrong

- **The AI asked questions instead of writing code** - your prompt (or a
  follow-up) contained "ask me first" or similar. Reply: "Do not ask, build
  it now with the defaults in the prompt."
- **`Taggbox API error: 401`** - token missing or wrong in the environment
  variable, or the API is switched off for the account.
- **`422 Validation Failed`** - a query parameter is wrong; the response's
  `body.fields` names it. Paste it back to the AI.
- **Blank wall, no error** - the account has no approved posts, or the wall
  token points at a wall with none. Test with the curl command above.
- **Fields look wrong** (`undefined`, empty author) - the AI guessed field
  names; make sure llms.txt was attached or is in the folder, and paste the
  Post object section from it.

Spec: [llms.txt](https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/llms.txt) · more prompts (filters, load-more, Redis, design):
[../../guides/prompts.md](../../guides/prompts.md)
