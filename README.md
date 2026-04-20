# ZK Agent

AI agent that classifies conversation insights into Zettelkasten note types and saves them to your note-taking app.

## What's New in v2: Scope

v1 treats every insight the same — it classifies without knowing what you're working on. But conversations often happen within a specific project context (a language you're learning, a research topic, a creative project). **Scope** lets you point ZK Agent at a Heptabase whiteboard so it understands your project before classifying. Same pipeline, better judgment.

```bash
# Without scope — general classification
zk-agent "subjunctif seems to only be used in formal contexts"

# With scope — reads your "French A1" whiteboard first, then classifies
zk-agent --scope learning-french "subjunctif seems to only be used in formal contexts"
```

## Features

- **ZK Classification**: LLM classifies notes as Fleeting, Literature, or Permanent
- **Scope Context**: Point at a Heptabase whiteboard for project-aware classification
- **Smart Routing**: Fleeting → daily note, Literature/Permanent → cards (auto-tagged `#fleeting`, `#literature`, `#permanent`)
- **Multi-destination**: Heptabase, Obsidian
- **Any LLM Provider**: OpenAI, Anthropic, Google Gemini, OpenRouter, Ollama, or any OpenAI-compatible endpoint
- **Auto Metadata**: Generates title and tags in the same language as the input
- **Smart Linking**: Searches existing notes for related content
- **Conversation Scanner**: Auto-detect insights worth saving from any conversation
- **Multi-language**: Works with Chinese, English, or mixed-language input

## Quick Start

### Install

```bash
pipx install git+https://github.com/amelieyeh/zk-agent.git
```

Or with pip: `pip install git+https://github.com/amelieyeh/zk-agent.git`

### Setup

Run the interactive setup wizard:

```bash
zk-agent init
```

It guides you through:
1. **AI provider** — Anthropic, OpenAI, Google Gemini, OpenRouter, Ollama, or any OpenAI-compatible endpoint
2. **Note storage** — Heptabase (OAuth), Obsidian (local vault), or output-only

Config is saved to `~/.zk-agent/config.json`.

> For developers: `.env` in the project root is also supported, but `~/.zk-agent/config.json` takes priority.

### Usage

```bash
# Save an insight (auto-classifies and routes)
zk-agent "Your insight text here"

# With source attribution (renders as clickable link)
zk-agent "Insight from article" --source "https://example.com/article"

# With project scope (reads whiteboard context before classifying)
zk-agent --scope learning-french "subjunctif seems formal only"
```

Works with any MCP-capable AI tool (e.g. Claude Code) for a more integrated experience.

### Examples

**Permanent note → card:**
```
$ zk-agent "Good API design is like good translation — it lets users accomplish goals without understanding the underlying complexity."

✅ Saved as permanent note
   Title: Good API Design as Translation
   Tags: #api-design, #user-experience, #abstraction
   Confidence: 85%
   Reasoning: Original synthesis connecting API design to translation as a unifying metaphor
```

**Fleeting note → daily note:**
```
$ zk-agent "Maybe use webhooks for real-time notifications? Need to research."

📝 Fleeting note → saved
   Title: Research webhooks for real-time notifications
   Tags: #webhook, #real-time, #research
   Confidence: 95%
   Reasoning: Unprocessed idea with open question, needs further exploration
```

**Scoped note (with project context):**
```
$ zk-agent --scope learning-french "subjunctif seems to only be used in formal contexts"

   Scope: learning-french (whiteboard loaded)
📝 Fleeting note → saved
   Title: Subjunctif limited to formal register
   Tags: #french, #grammar, #subjunctif
   Confidence: 90%
   Reasoning: Personal observation about usage pattern, not from a textbook
```

## Scope (v2)

Scope gives ZK Agent project context by reading a Heptabase whiteboard before classification.

### Why Scope?

Without scope, the classifier sees only the raw text. It doesn't know whether "Marina's motivation needs work" refers to a character in your novel or a colleague's performance review. With scope, ZK Agent reads your project whiteboard first — it knows who Marina is, what the story structure looks like, and classifies accordingly.

### Setup

Create a scope config file at `~/.zk-agent/scopes/<name>.json`:

```json
{
  "name": "learning-french",
  "whiteboard": "French A1",
  "whiteboard_id": "43d09d11-...",
  "context_cards": ["Grammar Rules", "Vocabulary", "Resources"],
  "tags_prefix": "french"
}
```

| Field | Description |
|-------|-------------|
| `name` | Scope identifier (matches filename) |
| `whiteboard` | Heptabase whiteboard name (used for search fallback) |
| `whiteboard_id` | Heptabase whiteboard ID (recommended — reliable, skips search) |
| `context_cards` | Card titles to read for context (empty = read all, max 10) |
| `tags_prefix` | Auto-prepended to tags on every note saved with this scope |

> Tip: You can find the whiteboard ID in the Heptabase URL when viewing the whiteboard.

### How It Works

```
zk-agent --scope learning-french "subjunctif seems formal only"

1. Load scope config → ~/.zk-agent/scopes/learning-french.json
2. Search whiteboard → find "French A1"
3. Read whiteboard structure → cards, sections, connections
4. Read context cards → Grammar Rules, Vocabulary, Resources
5. Inject context into classifier prompt → LLM knows your project
6. Classify → fleeting (personal observation, not from textbook)
7. Save with tags → #french, #grammar, #subjunctif
```

Without `--scope`, the pipeline is identical to v1. Scope is purely additive.

## Classification Criteria

| Type | Criteria | Examples |
|------|----------|---------|
| **Fleeting** | Raw, undeveloped thought. Questions, todos, "what if" ideas. | "Maybe use webhooks for notifications? Need to research." |
| **Literature** | References or paraphrases an external source — article, product, talk, documentation. | "Shopify built Sidekick, an AI that ties together product management and marketing." |
| **Permanent** | Your own synthesized conclusion. Connects multiple ideas, draws analogies, proposes frameworks. | "Good API design is like translation — hiding complexity so users focus on goals." |

## Architecture

```
Input text
  → [Scope?] → read Heptabase whiteboard → build project context
  → Classifier (LLM + context) → fleeting / literature / permanent
  → Metadata Generator (LLM) → title + tags (+ scope prefix)
  → Storage backend:
      Fleeting → daily note
      Literature/Permanent → search related → save as card

Storage backends:
  heptabase  → MCP (save_to_note_card + append_to_journal)
  obsidian   → local .md files (ZK-Agent/ + Daily Notes/)
```

Auto-detect mode:
```
Conversation text
  → [Scope?] → load project context
  → Detector (LLM + context) → 0-5 insight candidates
  → User approves/rejects each
  → Approved insights → save pipeline
```

## Project Structure

```
src/zk_agent/
  cli.py                 — CLI entry point (zk-agent command)
  classifier.py          — ZK note type classification (few-shot, with retry)
  note_types.py          — Shared type definitions and boundary rules
  metadata_generator.py  — Title + tags generation
  detector.py            — Conversation insight scanner
  scope.py               — Scope config loader (~/.zk-agent/scopes/)
  context.py             — Whiteboard context builder (reads Heptabase whiteboards)
  llm.py                 — Unified LLM client (any OpenAI-compatible provider)
  storage.py             — Storage interface + backend selector
  storage_heptabase.py   — Heptabase backend (MCP)
  storage_obsidian.py    — Obsidian backend (local Markdown)
  heptabase_client.py    — Heptabase MCP connection + OAuth + whiteboard reading
  oauth.py               — Self-contained OAuth 2.1 for Heptabase
  config.py              — User config (~/.zk-agent/config.json)
  init_wizard.py         — Interactive setup wizard
  setup.py               — Heptabase OAuth re-authorization
  env.py                 — .env file loader (developer override)
tests/                   — 26 tests (classifier + detector + parse/validation)
```

## Status

**v1 — Core pipeline**: ✅ Classify → metadata → route → save

**v1 — Auto-detect**: ✅ Conversation scanner + `/zk-scan`

**v1 — Multi-destination**: ✅ Heptabase + Obsidian

**v2 — Scope**: ✅ Project-aware classification via Heptabase whiteboards

## License

MIT
