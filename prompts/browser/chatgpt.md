# ChatGPT - build a Taggbox social widget

Use this when you are chatting with ChatGPT in the browser. It cannot touch
your computer, so the prompts below make it hand you complete files plus a
setup checklist, and forbid it from asking questions before the code.

## 1. Get the spec file

Download [llms.txt](../../llms.txt) to your computer
(right-click the link, "Save link as...", keep the name `llms.txt`), or in a
terminal:

```bash
BASE=https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/build   # change "main" to test another branch
curl -sSLo llms.txt "$BASE/llms.txt"
```

## 2. Start the chat and attach the spec

1. Open https://chatgpt.com and start a **new chat**.
2. Click the **+** (paperclip) button next to the message box, choose
   **Upload from computer**, and pick `llms.txt`.
3. Click **+** again and choose **Canvas**. ChatGPT only draws an HTML page
   inside a canvas; in a normal chat it shows the file as code, so without
   this you get no preview.
4. Paste the prompt from step 3 and send.

ChatGPT can sometimes fetch URLs itself, but attaching the file is more
reliable than hoping it browses. If your plan has no file upload, paste the
whole llms.txt at the bottom of the prompt instead. Use the **Copy code**
button on each code block - never retype a file.

## 3. Paste this prompt

Six lines. Paste the block as your first message with
llms.txt attached (or its contents pasted underneath). The detailed rules live
in llms.txt; the AI reads them there.

```
BASE = https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/build - every BASE/... link, here and in the files you fetch, starts from it.
Build me a social widget: one web page that shows the live posts from my Taggbox gallery.
Brief: BASE/guides/widget-build-brief.md - fetch it RAW and the two specs it links (the API spec and the design spec); if you cannot fetch URLs, follow the attached llms.txt.
Give me BOTH languages: a single self-contained index.php (PHP 8, nothing to install) AND the Node.js set (server.js, package.json, cache file) - plus a preview.html - the same page as a static file with the sample posts baked into the HTML, calling nothing, so I can double-click it and see the design before I have a token - and one README.md covering them. Token comes from the ACCESS_TOKEN env var - write the code first, then ask me for it at the end.
Give me the complete code first, then tell me how to run it as if I've never used a terminal.
You can't access my computer, so output every file complete and ready to save, starting each with "### FILE: <name>", then a setup checklist.
Put preview.html in its own canvas so I can click Preview and see the design here; give the other files as normal code blocks.
```

## See the design in the chat

When `preview.html` comes as an HTML box showing code, click **▶ (Play)** at
its top right to see the page - ChatGPT decides by itself whether the box
opens on the code or the preview, so this click is sometimes needed. If it came as a plain code block instead, reply:
"Open preview.html in a canvas." Images can show blurred or missing inside
the canvas; for the real look, save the file (step 4) and double-click it.

Do not ask ChatGPT to copy the gallery or a `guides/previews/` file back
to you: it cannot read a linked file's exact source (its browsing tool
changes it, and its Python sandbox has no internet). With only the link,
steps.md has it write a small page that shows the real gallery or preview
from GitHub Pages
(https://wallapi.github.io/taggbox.com-API-Docs/guides/theme-gallery.html);
when the preview asks "Allow network access?" for
wallapi.github.io, click **Allow** - that is ChatGPT's own
check before a preview loads another site. If no Allow prompt comes and
it says "Could not load it here", the preview blocked the request; open
the link it gives in your browser, or attach previews-lite.txt - it
needs no network. To copy the
lite files into the canvas instead, attach them - see
[Step by step (Prompt 1 in ChatGPT)](#step-by-step-prompt-1-in-chatgpt).

## Step by step (Prompt 1 in ChatGPT)

The guided build from Prompt 1 in [guides/prompts.md](../../guides/prompts.md):
pick a theme, see it in a canvas, change the look, then get the finished
code as a zip. ChatGPT does not reliably open raw GitHub files, so attach
them instead.

1. Download [steps.md](../../prompts/library/build/steps.md) and
   [previews-lite.txt](../../guides/previews-lite.txt)
   (right-click each, "Save link as...", keep the names), or in a terminal:

   ```bash
   BASE=https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/build   # change "main" to test another branch
   curl -sSLo steps.md "$BASE/prompts/library/build/steps.md"
   curl -sSLo previews-lite.txt "$BASE/guides/previews-lite.txt"
   ```

2. Open https://chatgpt.com, start a **new chat**, click **+** >
   **Upload from computer** and pick both files.
3. Click **+** again and choose **Canvas**.
4. Paste this prompt and send:

```
BASE = https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/build - every BASE/... link in the attached file starts from it.
Build me a social widget from my Taggbox gallery, step by step.
The attached steps.md lists every step and when to stop and wait for my answer - follow it exactly. You are ChatGPT: wherever it says "If you are ChatGPT or Gemini", do that. previews-lite.txt is attached too. Open no link - only write links for me to click.
Start with step 1 now.
If steps.md is not attached, say so in one line - do not build from memory.
```

In step 2, click **Preview** at the top right of the canvas. Images can look
soft there - the canvas may block outside images, and then a small built-in
copy shows instead. For the sharp version, save preview.html and
double-click it.

## 4. Save the files it gives you

For every `### FILE:` block: click the copy button on the code block, open a
plain-text editor (macOS: TextEdit with Format > Make Plain Text; Windows:
Notepad; or VS Code), paste, and save with the exact filename shown into a
new folder called `my-social-widget`. Do not let the editor add `.txt`.

### Run it (PHP)

Check the runtime once:

```bash
php -v    # must print PHP 8.x
```

Install PHP if the check fails: macOS `brew install php`, Windows https://windows.php.net/download, Ubuntu `sudo apt install php-cli php-curl`.

macOS / Linux (Terminal):

```bash
cd my-social-widget
export ACCESS_TOKEN="wt1_your_token_here"
export API_BASE_URL="https://api.taggbox.com/api"
php -S localhost:8080
```

Windows (PowerShell):

```powershell
cd my-social-widget
$env:ACCESS_TOKEN="wt1_your_token_here"
$env:API_BASE_URL="https://api.taggbox.com/api"
php -S localhost:8080
```

Open http://localhost:8080 in your browser. Stop the server with Ctrl+C.

Verify the API side independently of the page:

```bash
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$API_BASE_URL/v3/posts?limit=1"
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
cd my-social-widget
npm install
export ACCESS_TOKEN="wt1_your_token_here"
export API_BASE_URL="https://api.taggbox.com/api"
node server.js
```

Windows (PowerShell):

```powershell
cd my-social-widget
npm install
$env:ACCESS_TOKEN="wt1_your_token_here"
$env:API_BASE_URL="https://api.taggbox.com/api"
node server.js
```

Open http://localhost:3000 in your browser. Stop the server with Ctrl+C.

Verify the API side independently of the page:

```bash
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$API_BASE_URL/v3/posts?limit=1"
```

You should see `"status":true` and one post inside `body.posts`. A 401 means
the token is wrong or the API is disabled for the account; the message says
which.

## If it goes wrong

- **The AI asked questions instead of writing code** - your prompt (or a
  follow-up) asked before writing anything. Reply: "Build it now with the
  defaults in the prompt, and ask me for the credentials at the end."
- **No preview in the chat, only code** - Canvas was not on. Reply: "Open
  preview.html in a canvas", then click **Preview**. Or save `preview.html`
  and double-click it.
- **Step by step: no preview in step 2, only a line of text** -
  previews-lite.txt was not attached. Attach it and reply "Show the preview
  now".
- **"Could not load it here"** - ChatGPT's preview blocked the request to GitHub Pages and no
  Allow prompt came. Attach previews-lite.txt and reply "Show the preview
  again from previews-lite.txt" - it has every preview built in, no
  network needed. Or open the link it gave in your browser.
- **The preview stops halfway or looks broken** - reply "Give preview.html
  again from previews-lite.txt, whole and unchanged". Or download the
  theme's file from [guides/previews-lite/](../../guides/previews-lite) and
  double-click it.
- **`Taggbox API error: 401`** - token missing or wrong in the environment
  variable, or the API is switched off for the account.
- **`422 Validation Failed`** - a query parameter is wrong; the response's
  `body.fields` names it. Paste it back to the AI.
- **Blank widget, no error** - the account has no approved posts, or the wall
  token points at a widget with none. Test with the curl command above.
- **Fields look wrong** (`undefined`, empty author) - the AI guessed field
  names; make sure llms.txt was attached or is in the folder, and paste the
  Post object section from it.

Spec: [llms.txt](../../llms.txt) · more prompts (filters, load-more, Redis, design):
[../../guides/prompts.md](../../guides/prompts.md)
