"""
Metadata Generator.

Generates structured metadata for a Zettelkasten note:
  title, tags, source, created_at, related_notes
"""

import json
import os
from datetime import datetime, timezone
from typing import TypedDict, Literal

import anthropic


class NoteMetadata(TypedDict):
    title: str
    tags: list[str]
    note_type: Literal["fleeting", "literature", "permanent"]
    confidence: float
    source: str | None
    created_at: str
    related_notes: list[str]


METADATA_PROMPT = """Given this insight and its classification, generate metadata.

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
    """Generate structured metadata for a note using Claude Haiku."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": METADATA_PROMPT.format(
                    note_type=classification["note_type"],
                    confidence=classification["confidence"],
                    text=text,
                ),
            }
        ],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    parsed = json.loads(raw)

    return NoteMetadata(
        title=parsed["title"],
        tags=parsed["tags"],
        note_type=classification["note_type"],
        confidence=classification["confidence"],
        source=source,
        created_at=datetime.now(timezone.utc).isoformat(),
        related_notes=[],
    )
