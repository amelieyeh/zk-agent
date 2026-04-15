"""
Metadata Generator.

Generates structured metadata for a Zettelkasten note:
  title, tags, source, created_at, related_notes
"""

import json
from datetime import datetime, timezone
from typing import TypedDict, Literal

from zk_agent.llm import chat


class NoteMetadata(TypedDict):
    title: str
    tags: list[str]
    note_type: Literal["fleeting", "literature", "permanent"]
    confidence: float
    source: str | None
    created_at: str
    related_notes: list[str]


SYSTEM_PROMPT = """\
You are a metadata generator for Zettelkasten notes. You produce concise titles \
and useful tags. You respond with JSON only."""

METADATA_PROMPT = """\
Generate metadata for this Zettelkasten note.

Classification: {note_type} (confidence: {confidence})
Insight: {text}

Respond with JSON only, no markdown fences:
{{"title": "concise title (under 60 chars, same language as insight)", "tags": ["tag1", "tag2", "tag3"]}}

Rules:
- Title should capture the core idea, not just describe the topic
- 3-5 tags, lowercase, no # prefix
- Tags should be useful for future retrieval
- Use the same language as the insight for the title"""


def generate_metadata(
    text: str,
    classification: dict,
    source: str | None = None,
) -> NoteMetadata:
    """Generate structured metadata for a note."""
    raw = chat(
        METADATA_PROMPT.format(
            note_type=classification["note_type"],
            confidence=classification["confidence"],
            text=text,
        ),
        max_tokens=200,
        system=SYSTEM_PROMPT,
    )

    try:
        parsed = _parse_llm_json(raw)
    except (json.JSONDecodeError, KeyError):
        parsed = {"title": text[:57] + "..." if len(text) > 60 else text, "tags": []}

    title = parsed.get("title", text[:60])
    if not isinstance(title, str):
        title = str(title)

    tags = parsed.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    tags = [str(t).lower() for t in tags if isinstance(t, (str, int, float))]

    return NoteMetadata(
        title=title,
        tags=tags,
        note_type=classification["note_type"],
        confidence=classification["confidence"],
        source=source,
        created_at=datetime.now(timezone.utc).isoformat(),
        related_notes=[],
    )


def _parse_llm_json(raw: str) -> dict:
    """Parse JSON from LLM response, handling common formatting issues."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    brace_end = text.rfind("}")
    if brace_end != -1:
        text = text[: brace_end + 1]

    return json.loads(text)
