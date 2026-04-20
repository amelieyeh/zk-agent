# ZK Agent — Architecture & Design

## Overview

AI agent that classifies conversation insights into Zettelkasten note types and saves them to your note-taking app.

**Runtime:** Python 3.11+ with OpenAI-compatible SDK + MCP SDK
**Classification:** Any LLM via OpenAI-compatible API
**Storage:** Heptabase (MCP), Obsidian (local Markdown), or output-only
**Install:** `pipx install git+https://github.com/amelieyeh/zk-agent.git`

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

Auto-detect flow:
```
Conversation text
    ↓
Insight Detector (LLM API)
    → 0-5 candidates with suggested type + reason
    → User selects which to save
    → Each approved insight runs through the save pipeline
```

## Key Design Decisions

### Classifier: few-shot LLM prompt (not rules)

ZK note types have fuzzy boundaries that need semantic understanding. Any OpenAI-compatible LLM works. The prompt in `classifier.py` uses few-shot examples (EN + ZH) with explicit boundary rules, and shares type definitions with the detector via `note_types.py` to ensure consistent classification across stages. Provider configured via `zk-agent init`, `~/.zk-agent/config.json`, or `.env`.

### MCP: Direct Python SDK connection

The Python MCP SDK connects directly to Heptabase using self-managed OAuth tokens. No external agent framework required.

### Note routing: fleeting → daily note, literature/permanent → card

One conversation can easily produce 4+ insights. Creating a card for each floods the note app. Fleeting notes (raw thoughts, questions, todos) go to the daily note under a dedicated section. Only literature and permanent notes — which represent developed ideas — become cards.

### Shared type definitions

Detector and classifier both reference `note_types.py` for type definitions and boundary rules. This eliminates classification drift between the "find insights" and "classify insight" stages — when two LLM prompts need to agree on categorization, they must share the same criteria text.

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

## Implementation Status

### Phase 1 — MVP (complete)

Manual trigger mode: user provides text, agent classifies + saves.

| # | Task | Status | Notes |
|---|------|--------|-------|
| T1 | Heptabase MCP setup + self-contained OAuth | Done | `zk-agent setup` triggers browser OAuth |
| T2 | `classifier.py` — ZK classification via LLM | Done | 100% accuracy on 12 fixtures (EN + ZH, few-shot prompt) |
| T3 | `metadata_generator.py` — title + tags generation | Done | Same-language titles via LLM |
| T4 | Semantic search for related notes | Done | Integrated in storage backends |
| T5 | Full pipeline | Done | Fleeting → daily note, lit/perm → card |
| T6 | Note formatting | Done | Markdown card format in `_format_card()` |
| T7 | Fleeting note routing | Done | Appends under `## 🧠 ZK Fleeting Notes` section |
| T8 | Tests | Done | 26 pass (12 classifier fixtures + 7 detector + 6 parse/validation + 1 structure) |
| T9 | Packaging | Done | `pyproject.toml` + `pip install` + CLI entry point |

### Phase 2 — Auto-detect (complete)

Scan conversations for insights worth saving, present candidates for approval.

| # | Task | Status | Notes |
|---|------|--------|-------|
| D1 | `detector.py` — scan conversation for ZK-worthy insights | Done | LLM-powered, returns 0-5 candidates |
| D2 | Multi-provider LLM support | Done | OpenAI, Anthropic, Google Gemini, OpenRouter, Ollama |

> **AI tool integration:** The detector is designed to be called from any AI assistant or script. For example, Claude Code users can integrate it as a custom command to scan conversations and selectively save insights.

### Phase 3 — Multi-destination (complete)

Pluggable storage backends via `NoteStorage` protocol.

| # | Task | Status | Notes |
|---|------|--------|-------|
| S1 | `storage.py` — storage interface + backend selector | Done | `STORAGE` env var |
| S2 | `storage_heptabase.py` — Heptabase backend | Done | Default, MCP-based |
| S3 | `storage_obsidian.py` — Obsidian backend | Done | Local .md files |

## Known Limitations

| Item | Details |
|------|---------|
| Heptabase OAuth token expiry | Token has 48h TTL, no refresh token. Re-auth via `zk-agent setup` on expiry. |
| No Heptabase tag API | MCP doesn't expose tag management. Note type indicated as `#hashtag` in card content (plain text, not native tags). |

## Example Interactions

### Manual save (permanent → card)

```
$ zk-agent "Good API design is like good translation — it lets users accomplish goals without understanding the underlying complexity."

✅ Saved as permanent note
   Title: Good API Design as Translation
   Tags: #api-design, #user-experience, #abstraction
   Confidence: 85%
   Reasoning: Original synthesis connecting API design to translation as a unifying metaphor
```

### Manual save (fleeting → daily note)

```
$ zk-agent "Maybe use webhooks for real-time notifications? Need to research."

📝 Fleeting note → saved
   Title: Research webhooks for real-time notifications
   Tags: #webhook, #real-time, #research
   Confidence: 95%
   Reasoning: Unprocessed idea with open question, needs further exploration
```
