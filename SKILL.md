---
name: zk-agent
description: Auto-classify conversation insights into Zettelkasten notes and save to Heptabase
version: 0.1.0
author: amelieyeh
tags: [zettelkasten, heptabase, knowledge-management, note-taking]
tools: [save_to_note_card, semantic_search_objects, append_to_journal]
---

# ZK Agent

Classifies conversation insights as Zettelkasten note types (Fleeting / Literature / Permanent), then saves them to your note-taking app with auto-generated metadata and related note links.

## Usage

```
python scripts/zk_agent.py setup                     — Authorize Heptabase (one-time)
python scripts/zk_agent.py <text>                     — Classify and save an insight
python scripts/zk_agent.py <text> --source <url>      — Save with source attribution
```

## Requirements

- Heptabase account with MCP access
- LLM API key (Anthropic, OpenAI, or any OpenAI-compatible provider — set in `.env`)
