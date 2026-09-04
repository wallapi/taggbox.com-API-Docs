# Prompts by tool - build a Taggbox social wall

One document per AI tool. Each contains the setup for that tool, a **PHP**
prompt, a **Node.js** prompt, the exact run commands for both, and a
troubleshooting list. Open the file for the tool you use and follow it top to
bottom.

## Which document?

**Browser chat** (the AI cannot touch your computer; it hands you complete
files and you save them yourself):

| Tool      | Document                                | PHP                                | Node.js                                |
| --------- | --------------------------------------- | ---------------------------------- | -------------------------------------- |
| ChatGPT   | [browser/chatgpt.md](browser/chatgpt.md)     | [prompt](browser/chatgpt.md#php)   | [prompt](browser/chatgpt.md#nodejs)    |
| Gemini    | [browser/gemini.md](browser/gemini.md)       | [prompt](browser/gemini.md#php)    | [prompt](browser/gemini.md#nodejs)     |
| claude.ai | [browser/claude-ai.md](browser/claude-ai.md) | [prompt](browser/claude-ai.md#php) | [prompt](browser/claude-ai.md#nodejs)  |

**Coding agent in an editor or terminal** (the AI creates the files in your
project folder itself; a context file carries the rules):

| Tool                     | Document                                                          | Context file it reads              |
| ------------------------ | ----------------------------------------------------------------- | ---------------------------------- |
| Claude Code              | [editor/claude-code.md](editor/claude-code.md)                    | `CLAUDE.md`                        |
| Cursor                   | [editor/cursor.md](editor/cursor.md)                              | `.cursor/rules/taggbox.mdc`        |
| OpenAI Codex CLI         | [editor/codex.md](editor/codex.md)                                | `AGENTS.md`                        |
| GitHub Copilot (VS Code) | [editor/copilot.md](editor/copilot.md)                            | `.github/copilot-instructions.md`  |
| Gemini CLI / Antigravity | [editor/gemini-cli-antigravity.md](editor/gemini-cli-antigravity.md) | `GEMINI.md`                     |
| Windsurf                 | [editor/windsurf.md](editor/windsurf.md)                          | `.windsurf/rules/taggbox.md`       |

Every editor document has a PHP and a Node.js prompt under headings `### PHP`
and `### Node.js`. The context file contents are in
[TAGGBOX_CONTEXT.md](TAGGBOX_CONTEXT.md); the setup commands in each document
download it to the right path for that tool.

## Why the prompts are written this way

- **They say "do not ask me anything before writing code."** Some models
  (Gemini in particular) take "ask me for my token before you start"
  literally: they stop, ask, and print a plan; the code only comes after
  you answer. The base URL is in the spec and the token comes from an
  environment variable, so there is nothing to ask.
- **Browser prompts demand complete files with `### FILE:` headers** and a
  setup checklist, because you will be saving the files by hand.
- **Editor prompts are short** because the context file and the local
  `llms.txt` already carry the rules; the prompt only adds the language and
  the render list.
- **Both always attach [llms.txt](../llms.txt).** Field names like
  `content.text` and `media[0].cdn_url` are not guessable.

Follow-up prompts (filters, load more, auto-refresh, Redis, design) work in
every tool and are in [../guides/prompts.md](../guides/prompts.md).
