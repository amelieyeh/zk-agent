"""
ZK Note Classifier.

Uses Claude Haiku to classify text into Zettelkasten note types:
  - fleeting: raw thought, quick observation, not yet developed
  - literature: insight from external source, paraphrased in own words
  - permanent: own synthesized conclusion, connects multiple ideas
"""

import json
import os
from typing import TypedDict, Literal

import anthropic

NoteType = Literal["fleeting", "literature", "permanent"]


class Classification(TypedDict):
    note_type: NoteType
    confidence: float
    reasoning: str


CLASSIFY_PROMPT = """You are a Zettelkasten expert. Classify the following insight into exactly one type:

- **fleeting**: A raw thought, quick observation, or unprocessed idea. Not yet developed. Often contains "maybe", "what if", questions, or todos.
- **literature**: An insight derived from an external source (article, talk, conversation with someone, book, product, documentation). The key is it references or paraphrases someone else's idea or factual information.
- **permanent**: Your own synthesized conclusion that connects multiple ideas. This is an original thought that stands on its own. Often draws parallels, makes analogies, or proposes frameworks.

Respond with JSON only, no markdown fences:
{{"type": "fleeting|literature|permanent", "confidence": 0.0-1.0, "reasoning": "one sentence why"}}

Insight:
{text}"""


def classify_note(text: str) -> Classification:
    """Classify text into a Zettelkasten note type using Claude Haiku."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": CLASSIFY_PROMPT.format(text=text)}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    parsed = json.loads(raw)

    return Classification(
        note_type=parsed["type"],
        confidence=parsed["confidence"],
        reasoning=parsed["reasoning"],
    )
