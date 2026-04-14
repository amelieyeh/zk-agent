# ZK Agent — Implementation Plan

## Overview

AI agent that automatically identifies valuable insights from conversations and saves them as Zettelkasten notes to Heptabase.

**Runtime:** Python 3.11+ with Anthropic SDK + MCP SDK
**Classification:** Claude Haiku via Anthropic API
**Storage:** Heptabase official MCP (`https://api.heptabase.com/mcp`)
**Publish target:** agentskills.io

## Architecture

```
User input (conversation snippet / insight)
    ↓
ZK Classification Engine (Claude Haiku API)
    ├── Fleeting Note — raw thought, not yet developed
    ├── Literature Note — insight from external source, paraphrased
    └── Permanent Note — own synthesized conclusion, connects ideas
    ↓
Metadata Generator (Claude Haiku API)
    ├── Title (auto-generated, same language as input)
    └── Tags (3-5, lowercase)
    ↓
Linker (Heptabase semantic_search_objects)
    └── Find related existing notes, suggest connections
    ↓
Heptabase MCP (direct connection via Python MCP SDK + OAuth token)
    ├── save_to_note_card — create the note (Markdown, h1 = title)
    ├── semantic_search_objects — find related notes
    └── append_to_journal — daily capture log
```

Key decisions:
- **Bypass Hermes chat** — connect to Heptabase MCP directly via Python MCP SDK
- **Hermes used only for OAuth** — tokens persist at `~/.hermes/mcp-tokens/heptabase.json`
- **Anthropic SDK for classification** — Claude Haiku, fast and cheap

## Phases

### Phase 1 — MVP (✅ complete)

Manual trigger mode: user provides text, agent classifies + saves.

| # | Task | Status | Notes |
|---|------|--------|-------|
| T1 | Hermes + Heptabase MCP setup | ✅ | OAuth via Hermes, direct MCP SDK connection |
| T2 | `classifier.py` — ZK classification via Claude Haiku | ✅ | 100% accuracy on 5 fixtures |
| T3 | `metadata_generator.py` — title + tags generation | ✅ | Claude Haiku, same-language titles |
| T4 | `linker.py` — semantic search for related notes | ✅ | Uses Heptabase `semantic_search_objects` |
| T5 | `zk_agent.py` — full pipeline | ✅ | classify → metadata → link → save → journal |
| T6 | Note templates | ✅ | Markdown format, h1 title for Heptabase |
| T7 | `journal.py` — daily journal logging | ✅ | Appends capture record to Heptabase journal |
| T8 | Tests | ✅ | 6/6 pass, classifier 100% on all fixtures |
| T9 | Packaging | Pending | `SKILL.md` + `pyproject.toml` ready |
| T10 | Publish to agentskills.io | Pending | |

### Phase 2 — Auto-detect (future)

Agent monitors conversation in real-time, proactively suggests saving.

### Phase 3 — Multi-destination (future)

Support Obsidian, Notion, local markdown in addition to Heptabase.

## Key Technical Decisions

### Classifier: Claude Haiku API (not rules)

ZK note types have fuzzy boundaries that need semantic understanding. Haiku is fast and cheap. The prompt lives in `classifier.py` and can be tuned without changing architecture.

### MCP: Direct Python SDK connection

Hermes chat has an OpenRouter encoding bug, so we bypass it entirely. The Python MCP SDK connects directly to Heptabase using OAuth tokens that Hermes manages. This is simpler and more reliable.

### Types: Python TypedDict

```python
from typing import TypedDict, Literal

class NoteMetadata(TypedDict):
    title: str
    tags: list[str]
    note_type: Literal["fleeting", "literature", "permanent"]
    confidence: float
    source: str | None
    created_at: str
    related_notes: list[str]
```

## Risk Register

| Risk | Severity | Status |
|------|----------|--------|
| Heptabase OAuth token expiry | Medium | Token refresh not yet implemented |
| MCP SDK OAuth resource validation bug | Low | Patched locally, lost on SDK upgrade |
| Classification accuracy (zh/en mixed) | Low | 100% on current fixtures |

## Example Interaction

```
python scripts/zk_agent.py "CSS 的本質是翻譯——把設計變成真的。
MCP tool design 也是翻譯——把 API 變成用戶能用的流程。我的核心能力是翻譯。"

→ Type: Permanent Note (92% confidence)
→ Title: 翻譯是核心能力：設計、API 到用戶體驗
→ Tags: #translation, #design, #api, #core_competency, #user_experience
→ Related: (semantic search results from Heptabase)
→ Saved to Heptabase ✓
→ Journal updated ✓
```
