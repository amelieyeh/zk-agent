"""
Insight Detector.

Scans conversation text and identifies segments worth saving
as Zettelkasten notes. Returns candidates with suggested note type.
"""

import json
import os
from typing import TypedDict

import anthropic


class InsightCandidate(TypedDict):
    text: str
    suggested_type: str
    reason: str


DETECT_PROMPT = """You are a Zettelkasten expert scanning a conversation for valuable insights worth preserving.

Identify 0-5 distinct insights from this conversation that are worth saving as notes. Look for:
- Original conclusions or syntheses (permanent notes)
- References to external products, articles, or ideas (literature notes)
- Interesting questions or half-formed ideas worth developing (fleeting notes)

Skip: greetings, small talk, task coordination, debugging output, code snippets, routine decisions.

Respond with JSON only, no markdown fences:
[{{"text": "the insight in the speaker's own words (quote or close paraphrase)", "suggested_type": "fleeting|literature|permanent", "reason": "why this is worth saving"}}]

Return an empty array [] if nothing is worth saving.

Conversation:
{conversation}"""


def detect_insights(conversation: str) -> list[InsightCandidate]:
    """Scan conversation text for ZK-worthy insights."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": DETECT_PROMPT.format(conversation=conversation)}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    candidates = json.loads(raw)
    return [InsightCandidate(**c) for c in candidates]
