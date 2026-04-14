# ZK Agent

AI agent that classifies conversation insights into Zettelkasten note types and saves them to your note-taking app.

## Features

- **ZK Classification**: LLM classifies notes as Fleeting, Literature, or Permanent
- **Smart Routing**: Fleeting → daily note, Literature/Permanent → cards
- **Multi-destination**: Heptabase, Obsidian (more coming)
- **Any LLM Provider**: OpenAI, Anthropic, OpenRouter, Ollama, or any OpenAI-compatible endpoint
- **Auto Metadata**: Generates title and tags in the same language as the input
- **Smart Linking**: Searches existing notes for related content
- **Conversation Scanner**: Auto-detect insights worth saving from any conversation
- **Multi-language**: Works with Chinese, English, or mixed-language input

## Quick Start

### Prerequisites

- Python 3.11+
- API key from any supported LLM provider
- A note-taking app: Heptabase (MCP) or Obsidian (local vault)

### Setup

1. Create `.env` in the project root:
   ```bash
   # --- LLM Provider (pick one) ---

   # Option A: Anthropic (default)
   ANTHROPIC_API_KEY=sk-ant-your-key-here

   # Option B: OpenAI
   LLM_API_KEY=sk-your-key-here
   LLM_MODEL=gpt-4o-mini

   # Option C: Any OpenAI-compatible endpoint (OpenRouter, Ollama, etc.)
   LLM_API_KEY=your-key
   LLM_BASE_URL=https://openrouter.ai/api/v1
   LLM_MODEL=anthropic/claude-haiku-4-5-20251001

   # --- Storage (pick one) ---

   # Heptabase (default) — run 'python scripts/zk_agent.py setup' to authorize
   STORAGE=heptabase

   # Obsidian — set vault path, no setup needed
   STORAGE=obsidian
   OBSIDIAN_VAULT=~/Documents/MyVault
   ```

2. If using Heptabase, authorize via OAuth (opens browser):
   ```bash
   python scripts/zk_agent.py setup
   ```

### Usage

```bash
# Save an insight (auto-classifies and routes)
python scripts/zk_agent.py "Your insight text here"

# With source attribution (renders as clickable link)
python scripts/zk_agent.py "Insight from article" --source "https://example.com/article"
```

If using Claude Code, the `/zk` and `/zk-scan` commands provide a more integrated experience.

### Examples

**Permanent note → card:**
```
$ python scripts/zk_agent.py "Good API design is like good translation — it lets users accomplish goals without understanding the underlying complexity."

✅ Saved as permanent note → card
   Title: Good API Design as Translation
   Tags: #api-design, #user-experience, #abstraction
   Confidence: 85%
```

**Fleeting note → daily note:**
```
$ python scripts/zk_agent.py "Maybe use webhooks for real-time notifications? Need to research."

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
  setup.py               — 'zk-agent setup' CLI
  env.py                 — .env file loader
tests/                   — 8 tests (classifier 5/5 + detector 2/2)
```

## Status

**Phase 1 — MVP**: ✅ Complete

**Phase 2 — Auto-detect**: ✅ Complete (detector + `/zk-scan` command)

**Phase 3 — Multi-destination**: ✅ Heptabase + Obsidian (Notion planned)

## License

MIT
