# Windsurf - build a Taggbox social wall

Use this when Windsurf works inside your project folder and can create files
itself. Setup is done once; after that a one-line request is enough because
the context file carries the rules on every turn.

## 1. Install Windsurf

Download from https://windsurf.com and install.

## 2. Create the project folder and drop in the two files

macOS / Linux:

```bash
mkdir my-social-wall && cd my-social-wall
curl -sSLo llms.txt https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/llms.txt
mkdir -p .windsurf/rules
curl -sSLo .windsurf/rules/taggbox.md https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/prompts/TAGGBOX_CONTEXT.md
```

Windows (PowerShell):

```powershell
mkdir my-social-wall; cd my-social-wall
curl.exe -sSLo llms.txt https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/llms.txt
New-Item -ItemType Directory -Force .windsurf/rules | Out-Null
curl.exe -sSLo .windsurf/rules/taggbox.md https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/prompts/TAGGBOX_CONTEXT.md
```

This gives you `llms.txt` (the API spec) and `.windsurf/rules/taggbox.md` (the project rules
Windsurf reads automatically - contents in
[../TAGGBOX_CONTEXT.md](../TAGGBOX_CONTEXT.md)).

## 3. Launch Windsurf in that folder

Open the folder with File > Open Folder (or `windsurf .` if you enabled
the shell command). Open **Cascade** with **Cmd+L** (macOS) / **Ctrl+L**
(Windows) and make sure it is in **Write** mode, not Chat.

Rules in `.windsurf/rules/` are applied to every Cascade request. Approve
the file writes and the `npm install` step when Cascade proposes them.

## 4. Paste ONE of these prompts

### PHP

```
Build the Taggbox social wall in this folder. The project rules are in
.windsurf/rules/taggbox.md and the API spec is in llms.txt here - follow both exactly,
including the spec's "Integration rules for generated code".

Tech:
- PHP 8+, one self-contained index.php. No Composer; use the curl_* functions.
- File cache: taggbox-cache.json written next to index.php.
- Must run with the built-in server: php -S localhost:8080

Render per post: author.name, network.name, media[0].cdn_url (omit when
media is empty), content.text as escaped text, and source.permalink as a
"View original" link when present. Cache for 5 minutes with stale fallback.

Do not ask me questions - use the defaults above and in .windsurf/rules/taggbox.md. Create
the files, run any install command, then tell me the exact commands to set
TAGGBOX_ACCESS_TOKEN and TAGGBOX_API_BASE and start the page locally.
```

### Node.js

```
Build the Taggbox social wall in this folder. The project rules are in
.windsurf/rules/taggbox.md and the API spec is in llms.txt here - follow both exactly,
including the spec's "Integration rules for generated code".

Tech:
- Node.js 18+ with Express: exactly two files, server.js and package.json.
  Use the built-in fetch; express is the only dependency.
- In-memory cache (a module-level variable is fine).
- Must run with: npm install, then node server.js, on port 3000.

Render per post: author.name, network.name, media[0].cdn_url (omit when
media is empty), content.text as escaped text, and source.permalink as a
"View original" link when present. Cache for 5 minutes with stale fallback.

Do not ask me questions - use the defaults above and in .windsurf/rules/taggbox.md. Create
the files, run any install command, then tell me the exact commands to set
TAGGBOX_ACCESS_TOKEN and TAGGBOX_API_BASE and start the page locally.
```

Approve the file creations it proposes. When it finishes it prints the run
commands; they match the ones below.

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

## 5. Next changes are one line each

With the context file in place you can keep going with short requests, e.g.
"make it a 3-column masonry grid", "add a network filter bar built from
GET /v3/networks", "add a Load more button using paging.next_cursor", "swap
the cache for Redis with a file fallback". Ready-made versions of these are in
[../../guides/prompts.md](../../guides/prompts.md).

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
