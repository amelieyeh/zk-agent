# ZK Agent — Implementation Plan

## Overview

AI agent that classifies conversation insights into Zettelkasten note types and saves them to your note-taking app.

**Runtime:** Python 3.11+ with OpenAI-compatible SDK + MCP SDK
**Classification:** Any LLM via OpenAI-compatible API
**Storage:** Heptabase (MCP), Obsidian (local Markdown), or output-only
**Publish target:** PyPI

## Architecture

```
User input (conversation snippet / insight)
    ↓
ZK Classification Engine (LLM API — any OpenAI-compatible provider)
    ├── Fleeting Note → daily note (under dedicated section)
    ├── Literature Note → card
    └── Permanent Note → card
    ↓
Metadata Generator (LLM API)
    ├── Title (auto-generated, same language as input)
    └── Tags (3-5, lowercase)
    ↓
Storage Backend (user-configured)
    ├── heptabase  → MCP (save_to_note_card + append_to_journal)
    ├── obsidian   → local .md files (ZK-Agent/ + Daily Notes/)
    └── (none)     → output Markdown only
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
- **Fleeting → daily note, not card** — reduces card volume, fleeting notes live in daily note under dedicated section
- **No Heptabase tag API** — MCP doesn't expose tag management, note type indicated in card metadata text

## Phases

### Phase 1 — MVP (✅ complete)

Manual trigger mode: user provides text, agent classifies + saves.

| # | Task | Status | Notes |
|---|------|--------|-------|
| T1 | Heptabase MCP setup + self-contained OAuth | ✅ | `zk-agent setup` triggers browser OAuth |
| T2 | `classifier.py` — ZK classification via LLM | ✅ | 100% accuracy on 5 fixtures |
| T3 | `metadata_generator.py` — title + tags generation | ✅ | Same-language titles via LLM |
| T4 | Semantic search for related notes | ✅ | Integrated in storage backends |
| T5 | `zk_agent.py` — full pipeline | ✅ | Fleeting → daily note, lit/perm → card |
| T6 | Note formatting | ✅ | Markdown card format in `_format_card()` |
| T7 | Fleeting note routing | ✅ | Appends under `## 🧠 ZK Fleeting Notes` section |
| T8 | Tests | ✅ | 8/8 pass (classifier 5/5 + detector 2/2) |
| T9 | Packaging | Pending | `SKILL.md` + `pyproject.toml` ready |
| T10 | Publish to PyPI | Pending | |

### Phase 2 — Auto-detect (✅ core complete)

Scan conversations for insights worth saving, present candidates for approval.

| # | Task | Status | Notes |
|---|------|--------|-------|
| D1 | `detector.py` — scan conversation for ZK-worthy insights | ✅ | LLM-powered, returns 0-5 candidates |
| D2 | `/zk` Claude Code command — manual save | ✅ | Works in any session |
| D3 | `/zk-scan` Claude Code command — batch scan + select | ✅ | Scan conversation, approve/reject each |
| D4 | End-of-day scan integration | ✅ | Can be hooked into any CLI workflow |
| D5 | Multi-provider LLM support | ✅ | `llm.py` — OpenAI, Anthropic, OpenRouter, Ollama |

### Phase 3 — Multi-destination (✅ core complete)

Pluggable storage backends via `NoteStorage` protocol.

| # | Task | Status | Notes |
|---|------|--------|-------|
| S1 | `storage.py` — storage interface + backend selector | ✅ | `STORAGE` env var |
| S2 | `storage_heptabase.py` — Heptabase backend | ✅ | Default, MCP-based |
| S3 | `storage_obsidian.py` — Obsidian backend | ✅ | Local .md files |

## Key Technical Decisions

### Classifier: LLM API (not rules)

ZK note types have fuzzy boundaries that need semantic understanding. Any OpenAI-compatible LLM works. The prompt lives in `classifier.py` and can be tuned without changing architecture. Provider configured via `.env`.

### MCP: Direct Python SDK connection

The Python MCP SDK connects directly to Heptabase using self-managed OAuth tokens. No external agent framework required.

### Note routing: fleeting → daily note, literature/permanent → card

One conversation can easily produce 4+ insights. Creating a card for each floods the note app. Fleeting notes (raw thoughts, questions, todos) go to the daily note under a dedicated section. Only literature and permanent notes — which represent developed ideas — become cards.

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
| Heptabase OAuth token expiry | Medium | Token has 48h TTL, no refresh token. Re-auth on expiry. |
| MCP SDK OAuth resource validation bug | Low | Fixed in SDK >=1.27.0, pinned in requirements |
| Classification accuracy (zh/en mixed) | Low | 100% on current fixtures |

## Example Interactions

### Manual save (permanent → card)

```
$ python scripts/zk_agent.py "Good API design is like good translation — it lets users accomplish goals without understanding the underlying complexity."

✅ Saved as permanent note → card
   Title: Good API Design as Translation
   Tags: #api-design, #user-experience, #abstraction
   Confidence: 85%
```

### Manual save (fleeting → daily note)

```
$ python scripts/zk_agent.py "Maybe use webhooks for real-time notifications? Need to research."

📝 Fleeting note → daily note
   Title: Research webhooks for real-time notifications
   Tags: #webhook, #real-time, #research
   Confidence: 95%
```

### Auto-detect scan

```
$ python scripts/detector.py  # or via /zk-scan in Claude Code

Scanning conversation... found 2 candidates:

📝 1/2: permanent
"Systematic insight capture from AI conversations is a universal pain point — not limited to any specific tool's users."
Save? (y/n)
> y
✅ Saved → card

📝 2/2: fleeting
"Maybe use webhooks for real-time notifications?"
Save? (y/n)
> y
📝 Saved → daily note

Summary: 2 saved (1 card, 1 daily note)
```
