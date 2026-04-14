# ZK Agent

AI agent that classifies conversation insights into Zettelkasten note types and saves them to Heptabase.

## Features

- **ZK Classification**: Claude Haiku classifies notes as Fleeting, Literature, or Permanent
- **Smart Routing**: Fleeting → journal, Literature/Permanent → cards (reduces noise)
- **Auto Metadata**: Generates title and tags in the same language as the input
- **Smart Linking**: Searches existing Heptabase notes for related content
- **Conversation Scanner**: Auto-detect insights worth saving from any conversation
- **Claude Code Integration**: `/zk` and `/zk-scan` commands for seamless workflow
- **Multi-language**: Works with Chinese, English, or mixed-language input

## Quick Start

### Prerequisites

- Python 3.11+
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) (for OAuth token management)
- Heptabase account with MCP access
- Anthropic API key

### Setup

1. Install Hermes and run `hermes setup` to configure a model provider
2. Add Heptabase MCP to `~/.hermes/config.yaml`:
   ```yaml
   mcp_servers:
     heptabase:
       url: "https://api.heptabase.com/mcp"
       auth: oauth
   ```
3. Run `hermes chat` once to complete Heptabase OAuth (then exit)
4. Create `.env` in the project root:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

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
  → Classifier (Claude Haiku) → fleeting / literature / permanent
  → Metadata Generator (Claude Haiku) → title + tags
  → Router:
      Fleeting → append to Heptabase journal (## 🧠 ZK Fleeting Notes)
      Literature/Permanent → Linker (semantic search) → save as Heptabase card
```

Auto-detect mode:
```
Conversation text
  → Detector (Claude Haiku) → 0-5 insight candidates
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
