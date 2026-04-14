# ZK Agent — Implementation Plan

## Overview

AI agent that automatically identifies valuable insights from conversations and saves them as Zettelkasten notes to Heptabase.

**Runtime:** Python 3.11+ with OpenAI-compatible SDK + MCP SDK
**Classification:** Any LLM via OpenAI-compatible API (default: Claude Haiku)
**Storage:** Heptabase official MCP (`https://api.heptabase.com/mcp`), more destinations planned
**Publish target:** PyPI + agentskills.io

## Architecture

```
User input (conversation snippet / insight)
    ↓
ZK Classification Engine (LLM API — any OpenAI-compatible provider)
    ├── Fleeting Note → journal only (under dedicated section)
    ├── Literature Note → Heptabase card
    └── Permanent Note → Heptabase card
    ↓
Metadata Generator (LLM API)
    ├── Title (auto-generated, same language as input)
    └── Tags (3-5, lowercase)
    ↓
Linker (Heptabase semantic_search_objects) [literature/permanent only]
    └── Find related existing notes, suggest connections
    ↓
Heptabase MCP (direct connection via Python MCP SDK + OAuth token)
    ├── save_to_note_card — create card (Markdown, h1 = title, source as clickable link)
    ├── semantic_search_objects — find related notes
    └── append_to_journal — fleeting notes under "## 🧠 ZK Fleeting Notes" section
```

Auto-detect flow (Phase 2):
```
Conversation text
    ↓
Insight Detector (LLM API)
    → 0-5 candidates with suggested type + reason
    → User selects which to save
    → Each approved insight runs through the save pipeline
```

Key decisions:
- **Self-contained OAuth** — built-in OAuth flow, no external dependencies. Tokens at `~/.zk-agent/tokens/`
- **Any LLM provider** — unified `llm.py` interface via OpenAI-compatible SDK (OpenAI, Anthropic, OpenRouter, Ollama)
- **Fleeting → journal, not card** — reduces card volume, fleeting notes live in daily journal under dedicated section
- **No Heptabase tag API** — MCP doesn't expose tag management, note type indicated in card metadata text

## Phases

### Phase 1 — MVP (✅ complete)

Manual trigger mode: user provides text, agent classifies + saves.

| # | Task | Status | Notes |
|---|------|--------|-------|
| T1 | Heptabase MCP setup + self-contained OAuth | ✅ | `zk-agent setup` triggers browser OAuth |
| T2 | `classifier.py` — ZK classification via LLM | ✅ | 100% accuracy on 5 fixtures |
| T3 | `metadata_generator.py` — title + tags generation | ✅ | Same-language titles via LLM |
| T4 | `linker.py` — semantic search for related notes | ✅ | Uses Heptabase `semantic_search_objects` |
| T5 | `zk_agent.py` — full pipeline | ✅ | Fleeting → journal, lit/perm → card |
| T6 | Note templates | ✅ | Markdown format, h1 title, source as clickable link |
| T7 | `journal.py` — fleeting notes to journal | ✅ | Appends under `## 🧠 ZK Fleeting Notes` section |
| T8 | Tests | ✅ | 8/8 pass (classifier 5/5 + detector 2/2) |
| T9 | Packaging | Pending | `SKILL.md` + `pyproject.toml` ready |
| T10 | Publish to agentskills.io | Pending | |

### Phase 2 — Auto-detect (✅ core complete)

Scan conversations for insights worth saving, present candidates for approval.

| # | Task | Status | Notes |
|---|------|--------|-------|
| D1 | `detector.py` — scan conversation for ZK-worthy insights | ✅ | LLM-powered, returns 0-5 candidates |
| D2 | `/zk` Claude Code command — manual save | ✅ | Works in any session |
| D3 | `/zk-scan` Claude Code command — batch scan + select | ✅ | Scan conversation, approve/reject each |
| D4 | `/wrap-up` integration — auto-scan at end of day | ✅ | Step 5 in wrap-up flow |
| D5 | Multi-provider LLM support | ✅ | `llm.py` — OpenAI, Anthropic, OpenRouter, Ollama |

### Phase 3 — Multi-destination (planned)

Support Obsidian, Notion, local markdown in addition to Heptabase.

Priority from research:
1. **Obsidian** — local `.md` files, no API needed, highest ZK user overlap
2. **Notion** — mature REST API + official MCP, largest user base (30M)
3. **Logseq** — local Markdown, high ZK community overlap

## Key Technical Decisions

### Classifier: LLM API (not rules)

ZK note types have fuzzy boundaries that need semantic understanding. Any OpenAI-compatible LLM works. The prompt lives in `classifier.py` and can be tuned without changing architecture. Provider configured via `.env`.

### MCP: Direct Python SDK connection

The Python MCP SDK connects directly to Heptabase using self-managed OAuth tokens. No external agent framework required.

### Note routing: fleeting → journal, literature/permanent → card

One conversation can easily produce 4+ insights. Creating a card for each floods Heptabase. Fleeting notes (raw thoughts, questions, todos) go to the daily journal under a dedicated section. Only literature and permanent notes — which represent developed ideas — become cards.

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

## Example Interactions

### Manual save (permanent → card)

```
$ python scripts/zk_agent.py "好的 API 設計像好的翻譯——讓使用者不需要理解底層複雜性，就能完成目標。"

✅ Saved as permanent note → card
   Title: 好的 API 設計像翻譯——隱藏複雜性
   Tags: #api design, #user experience, #abstraction, #software engineering, #interface design
   Confidence: 85%
```

### Manual save (fleeting → journal)

```
$ python scripts/zk_agent.py "也許可以用 webhook 做即時通知？要研究一下"

📝 Fleeting note → journal
   Title: 研究 webhook 實現即時通知機制
   Tags: #webhook, #real-time notification, #instant alert, #technical research
   Confidence: 95%
```

### Auto-detect scan (`/zk-scan`)

```
/zk-scan

Scanning conversation... found 4 candidates:

📝 1/4: permanent
「AI 對話中的 insight 需要系統性捕捉——這個痛點不限於特定工具用戶」
存嗎？ (y/n/edit)
> y
✅ Saved → card

📝 2/4: fleeting
「也許可以用 webhook 做即時通知？」
存嗎？ (y/n/edit)
> y
📝 Saved → journal

Summary: 2 saved (1 card, 1 journal), 2 skipped
```
