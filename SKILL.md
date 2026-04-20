---
name: zk-agent
description: Auto-classify conversation insights into Zettelkasten notes with optional project scope context
version: 0.2.0
author: amelieyeh
tags: [zettelkasten, heptabase, obsidian, knowledge-management, note-taking, scope]
---

# ZK Agent

Classifies conversation insights as Zettelkasten note types (Fleeting / Literature / Permanent), then saves them to your note-taking app with auto-generated metadata and related note links. Optionally reads a Heptabase whiteboard for project-aware classification.

## Usage

```
zk-agent init                      — Interactive setup wizard
zk-agent <text>                     — Classify and save an insight
zk-agent <text> --source <url>      — Save with source attribution
zk-agent <text> --scope <name>      — Save with project context (reads whiteboard)
zk-agent setup                     — Re-authorize Heptabase OAuth
```

## Requirements

- LLM API key (Anthropic, OpenAI, or any OpenAI-compatible provider)
- A supported note-taking app: Heptabase (MCP) or Obsidian (local vault)
- (Optional) Scope config in `~/.zk-agent/scopes/<name>.json` for project context
