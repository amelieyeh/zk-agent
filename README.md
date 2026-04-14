# ZK Agent

AI agent that classifies conversation insights into Zettelkasten note types and saves them to Heptabase.

## Features

- **ZK Classification**: LLM classifies notes as Fleeting, Literature, or Permanent
- **Smart Routing**: Fleeting → journal, Literature/Permanent → cards (reduces noise)
- **Auto Metadata**: Generates title and tags in the same language as the input
- **Smart Linking**: Searches existing Heptabase notes for related content
- **Conversation Scanner**: Auto-detect insights worth saving from any conversation
- **Claude Code Integration**: `/zk` and `/zk-scan` commands for seamless workflow
- **Multi-language**: Works with Chinese, English, or mixed-language input

## Quick Start

### Prerequisites

- Python 3.11+
- Heptabase account with MCP access
- API key from any supported LLM provider

### Setup

1. Create `.env` in the project root with your LLM provider:
   ```bash
   # Option A: Anthropic (default, cheapest for this use case)
   ANTHROPIC_API_KEY=sk-ant-your-key-here

   # Option B: OpenAI
   LLM_API_KEY=sk-your-key-here
   LLM_MODEL=gpt-4o-mini

   # Option C: Any OpenAI-compatible endpoint (OpenRouter, Ollama, etc.)
   LLM_API_KEY=your-key
   LLM_BASE_URL=https://openrouter.ai/api/v1
   LLM_MODEL=anthropic/claude-haiku-4-5-20251001
   ```
2. Authorize Heptabase (opens browser for OAuth):
   ```bash
   python scripts/zk_agent.py setup
   ```
   Tokens are stored at `~/.zk-agent/tokens/heptabase.json`.

   > If you already have [Hermes Agent](https://github.com/NousResearch/hermes-agent) with Heptabase configured, ZK Agent can auto-detect your existing tokens.

### Usage

```bash
# Save an insight (auto-classifies and routes)
python scripts/zk_agent.py "Your insight text here"

# With source attribution (renders as clickable link in Heptabase)
python scripts/zk_agent.py "Insight from article" --source "https://example.com/article"
```

If using Claude Code, the `/zk` and `/zk-scan` commands provide a more integrated experience.

### Examples

**Permanent note → card:**
```
$ python scripts/zk_agent.py "好的 API 設計像好的翻譯——讓使用者不需要理解底層複雜性，就能完成目標。"

✅ Saved as permanent note → card
   Title: 好的 API 設計像翻譯——隱藏複雜性
   Tags: #api design, #user experience, #abstraction
   Confidence: 85%
```

**Fleeting note → journal:**
```
$ python scripts/zk_agent.py "也許可以用 webhook 做即時通知？要研究一下"

📝 Fleeting note → journal
   Title: 研究 webhook 實現即時通知機制
   Tags: #webhook, #real-time notification
   Confidence: 95%
```

## Architecture

```
Input text
  → Classifier (LLM) → fleeting / literature / permanent
  → Metadata Generator (LLM) → title + tags
  → Router:
      Fleeting → append to Heptabase journal (## 🧠 ZK Fleeting Notes)
      Literature/Permanent → Linker (semantic search) → save as Heptabase card
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
  zk_agent.py           — Main pipeline (classify → route → save)
  classifier.py         — ZK note type classification
  metadata_generator.py — Title + tags generation
  heptabase_client.py   — Direct MCP SDK client for Heptabase
  linker.py             — Semantic search for related notes
  journal.py            — Fleeting notes to journal
  detector.py           — Conversation insight scanner
  env.py                — .env file loader
tests/                  — 8 tests (classifier 5/5 + detector 2/2)
```

## Status

**Phase 1 — MVP**: ✅ Complete

**Phase 2 — Auto-detect**: ✅ Core complete (detector + `/zk-scan` command)

**Phase 3 — Multi-destination**: Planned (Obsidian, Notion, local markdown)

## License

MIT
