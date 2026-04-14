---
name: zk-agent
description: Auto-classify conversation insights into Zettelkasten notes and save to Heptabase
version: 0.1.0
author: amelieyeh
tags: [zettelkasten, heptabase, knowledge-management, note-taking]
tools: [save_to_note_card, semantic_search_objects, append_to_journal]
---

# ZK Agent

Classifies conversation insights as Zettelkasten note types (Fleeting / Literature / Permanent) using Claude Haiku, then saves them to Heptabase with auto-generated metadata and related note links.

## Usage

```
python scripts/zk_agent.py <text>                    — Classify and save an insight
python scripts/zk_agent.py <text> --source <url>     — Save with source attribution
```

## Requirements

- Heptabase account with MCP access (OAuth token via Hermes)
- Anthropic API key (set in `.env`)
