---
name: zk-agent
description: Auto-classify conversation insights into Zettelkasten notes and save to your note-taking app
version: 0.1.0
author: amelieyeh
tags: [zettelkasten, heptabase, obsidian, knowledge-management, note-taking]
---

# ZK Agent

Classifies conversation insights as Zettelkasten note types (Fleeting / Literature / Permanent), then saves them to your note-taking app with auto-generated metadata and related note links.

## Usage

```
python scripts/zk_agent.py setup                     — Authorize storage (Heptabase only)
python scripts/zk_agent.py <text>                     — Classify and save an insight
python scripts/zk_agent.py <text> --source <url>      — Save with source attribution
```

## Requirements

- LLM API key (Anthropic, OpenAI, or any OpenAI-compatible provider)
- A supported note-taking app: Heptabase (MCP) or Obsidian (local vault)
