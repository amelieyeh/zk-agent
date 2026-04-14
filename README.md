# ZK Agent

AI agent that classifies conversation insights into Zettelkasten note types and saves them to Heptabase.

## Features

- **ZK Classification**: Claude Haiku classifies notes as Fleeting, Literature, or Permanent
- **Auto Metadata**: Generates title and tags in the same language as the input
- **Smart Linking**: Searches existing Heptabase notes for related content
- **Heptabase Integration**: Saves cards + journal entries via MCP
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
# Save an insight
python scripts/zk_agent.py "Your insight text here"

# With source attribution
python scripts/zk_agent.py "Insight from article" --source "https://example.com/article"
```

### Example

```
$ python scripts/zk_agent.py "The essence of CSS is translation — turning design into reality. MCP tool design is also translation — turning APIs into user flows."

✅ Saved as permanent note
   Title: Translation as Core Skill: Design and API to UX
   Tags: #translation, #design, #api, #core_competency, #user_experience
   Confidence: 92%
   Journal: ✓
```

## Architecture

```
Input text
  → Classifier (Claude Haiku) → fleeting / literature / permanent
  → Metadata Generator (Claude Haiku) → title + tags
  → Linker (Heptabase MCP) → related notes
  → Save (Heptabase MCP) → note card + journal entry
```

## Project Structure

```
scripts/
  zk_agent.py          — Main pipeline entry point
  classifier.py        — ZK note type classification
  metadata_generator.py — Title + tags generation
  heptabase_client.py  — Direct MCP SDK client for Heptabase
  linker.py            — Semantic search for related notes
  journal.py           — Daily journal logging
  env.py               — .env file loader
templates/             — Note format templates
tests/                 — Classifier accuracy tests (5 fixtures, 100% pass)
```

## Status

**Phase 1 — MVP**: ✅ Complete (classify + save + journal working end-to-end)

**Phase 2 — Auto-detect**: Planned (agent proactively suggests saving insights)

**Phase 3 — Multi-destination**: Planned (Obsidian, Notion, local markdown)

## License

MIT
