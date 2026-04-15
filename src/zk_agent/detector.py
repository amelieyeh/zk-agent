"""
Insight Detector.

Scans conversation text and identifies segments worth saving
as Zettelkasten notes. Returns candidates with suggested note type.
"""

import json
from typing import TypedDict

from zk_agent.llm import chat
from zk_agent.note_types import DEFINITIONS, BOUNDARY_RULES


class InsightCandidate(TypedDict):
    text: str
    suggested_type: str
    reason: str


SYSTEM_PROMPT = """\
You are a Zettelkasten expert scanning conversations for valuable insights. \
You respond with JSON only."""

DETECT_PROMPT = """\
Scan this conversation for distinct insights worth saving as Zettelkasten notes.

## Note type definitions

{definitions}

## Boundary rules

{boundary_rules}

## What to extract

- Original conclusions or syntheses (→ permanent)
- References to external products, articles, or ideas (→ literature)
- Interesting questions or half-formed ideas worth developing (→ fleeting)

## What to skip

Greetings, small talk, task coordination, debugging output, code snippets, routine decisions.

## Output

Return 0-5 insights as JSON only, no markdown fences:
[{{"text": "the insight in the speaker's own words (quote or close paraphrase)", "suggested_type": "fleeting|literature|permanent", "reason": "why this is worth saving"}}]

Return an empty array [] if nothing is worth saving.

Conversation:
{conversation}"""


def _parse_llm_json_array(raw: str) -> list[dict]:
    """Parse JSON array from LLM response, handling common formatting issues."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    # Strip trailing text after JSON array
    bracket_end = text.rfind("]")
    if bracket_end != -1:
        text = text[: bracket_end + 1]

    return json.loads(text)


def detect_insights(conversation: str) -> list[InsightCandidate]:
    """Scan conversation text for ZK-worthy insights."""
    raw = chat(
        DETECT_PROMPT.format(
            conversation=conversation,
            definitions=DEFINITIONS,
            boundary_rules=BOUNDARY_RULES,
        ),
        max_tokens=1000,
        system=SYSTEM_PROMPT,
    )

    try:
        candidates = _parse_llm_json_array(raw)
    except (json.JSONDecodeError, KeyError):
        return []

    return [InsightCandidate(**c) for c in candidates]
