# ZK Agent

AI agent that classifies conversation insights into Zettelkasten note types and saves them to your note-taking app.

## Features

- **ZK Classification**: LLM classifies notes as Fleeting, Literature, or Permanent
- **Smart Routing**: Fleeting → daily note, Literature/Permanent → cards
- **Multi-destination**: Heptabase, Obsidian
- **Any LLM Provider**: OpenAI, Anthropic, OpenRouter, Ollama, or any OpenAI-compatible endpoint
- **Auto Metadata**: Generates title and tags in the same language as the input
- **Smart Linking**: Searches existing notes for related content
- **Conversation Scanner**: Auto-detect insights worth saving from any conversation
- **Multi-language**: Works with Chinese, English, or mixed-language input

## Quick Start

### Install

```bash
pipx install zk-agent
```

Or with pip: `pip install zk-agent`

### Setup

Run the interactive setup wizard:

```bash
zk-agent init
```

It guides you through:
1. **AI provider** — Anthropic, OpenAI, OpenRouter, Ollama, or any OpenAI-compatible endpoint
2. **Note storage** — Heptabase (OAuth), Obsidian (local vault), or output-only

Config is saved to `~/.zk-agent/config.json`.

> For developers: `.env` in the project root is also supported and takes priority over config.

### Usage

```bash
# Save an insight (auto-classifies and routes)
zk-agent "Your insight text here"

# With source attribution (renders as clickable link)
zk-agent "Insight from article" --source "https://example.com/article"
```

Works with any MCP-capable AI tool (e.g. Claude Code) for a more integrated experience.

### Examples

**Permanent note → card:**
```
$ zk-agent "Good API design is like good translation — it lets users accomplish goals without understanding the underlying complexity."

✅ Saved as permanent note → card
   Title: Good API Design as Translation
   Tags: #api-design, #user-experience, #abstraction
   Confidence: 85%
```

**Fleeting note → daily note:**
```
$ zk-agent "Maybe use webhooks for real-time notifications? Need to research."

📝 Fleeting note → daily note
   Title: Research webhooks for real-time notifications
   Tags: #webhook, #real-time, #research
   Confidence: 95%
```

## Architecture

```
Input text
  → Classifier (LLM) → fleeting / literature / permanent
  → Metadata Generator (LLM) → title + tags
  → Storage backend:
      Fleeting → daily note
      Literature/Permanent → search related → save as card

Storage backends:
  heptabase  → MCP (save_to_note_card + append_to_journal)
  obsidian   → local .md files (ZK-Agent/ + Daily Notes/)
```

Auto-detect mode:
```
Conversation text
  → Detector (LLM) → 0-5 insight candidates
  → User approves/rejects each
  → Approved insights → save pipeline
```

## Project Structure

```
scripts/
  zk_agent.py            — Main pipeline (classify → route → save)
  classifier.py          — ZK note type classification
  metadata_generator.py  — Title + tags generation
  detector.py            — Conversation insight scanner
  llm.py                 — Unified LLM client (any OpenAI-compatible provider)
  storage.py             — Storage interface + backend selector
  storage_heptabase.py   — Heptabase backend (MCP)
  storage_obsidian.py    — Obsidian backend (local Markdown)
  heptabase_client.py    — Heptabase MCP connection + OAuth
  oauth.py               — Self-contained OAuth 2.1 for Heptabase
  config.py              — User config (~/.zk-agent/config.json)
  init_wizard.py         — Interactive setup wizard
  setup.py               — Heptabase OAuth re-authorization
  env.py                 — .env file loader (developer override)
tests/                   — 8 tests (classifier 5/5 + detector 2/2)
```

## Status

**Phase 1 — MVP**: ✅ Complete

**Phase 2 — Auto-detect**: ✅ Complete (detector + `/zk-scan` command)

**Phase 3 — Multi-destination**: ✅ Heptabase + Obsidian

## License

MIT
