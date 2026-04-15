"""
ZK Note Classifier.

Classifies text into Zettelkasten note types:
  - fleeting: raw thought, quick observation, not yet developed
  - literature: insight from external source, paraphrased in own words
  - permanent: own synthesized conclusion, connects multiple ideas
"""

import json
from typing import TypedDict, Literal

from zk_agent.llm import chat

NoteType = Literal["fleeting", "literature", "permanent"]


class Classification(TypedDict):
    note_type: NoteType
    confidence: float
    reasoning: str


SYSTEM_PROMPT = """\
You are a Zettelkasten classification expert. You receive a single insight and \
classify it into exactly one of three note types. You respond with JSON only."""

CLASSIFY_PROMPT = """\
Classify this insight into exactly one Zettelkasten note type.

## Definitions

- **fleeting**: A raw thought, quick observation, or unprocessed idea. Not yet \
developed. Often contains "maybe", "what if", questions, or todos.
- **literature**: An insight derived from an external source (article, talk, \
book, product, documentation, someone else's idea). The key test: could you \
cite where this came from? If yes, it's literature.
- **permanent**: Your own synthesized conclusion that connects multiple ideas \
or domains. This is an original thought that stands on its own — it draws \
parallels, makes analogies, proposes frameworks, or reveals a pattern.

## Boundary rules

- References an external source AND adds original synthesis → **permanent** \
(the synthesis is the value, not the reference)
- States facts from a source without adding interpretation → **literature**
- A question that embeds a hypothesis ("maybe X works because Y") → **fleeting**
- An observation that could become a framework but isn't developed → **fleeting**
- When genuinely ambiguous, prefer **fleeting** (lower commitment, can be promoted later)

## Examples

Insight: "Shopify built Sidekick, an AI assistant that ties together product \
management, payments, and analytics into one interface."
{{"type": "literature", "confidence": 0.95, "reasoning": "Describes an external \
product's feature without adding interpretation"}}

Insight: "Maybe I should try using a graph database for the knowledge base? \
Need to research Neo4j vs ArangoDB."
{{"type": "fleeting", "confidence": 0.92, "reasoning": "Unprocessed idea with \
open questions, needs further exploration"}}

Insight: "The best AI agents are translators — they take complex APIs and \
translate them into flows humans can follow. CSS is also translation: turning \
design intent into visual reality. My core skill is this same translation."
{{"type": "permanent", "confidence": 0.93, "reasoning": "Original synthesis \
connecting three domains (AI, CSS, personal skill) through a unifying metaphor"}}

Insight: "LangChain 的 LCEL 語法讓 chain 組合變得很直覺，但 debug 很痛苦，\
因為中間 state 不好追蹤。"
{{"type": "literature", "confidence": 0.88, "reasoning": "Observation about an \
external tool's trade-off, could be cited back to LangChain experience"}}

Insight: "或許可以在每次對話結束時自動掃描 insight？但不確定 false positive \
會不會太多。"
{{"type": "fleeting", "confidence": 0.90, "reasoning": "Half-formed idea with \
explicit uncertainty, needs validation"}}

Insight: "當多個獨立產品缺乏整合時，編排層就是新的機會——誰能串連資料流和使用者旅程，\
誰就掌握了平台價值。"
{{"type": "permanent", "confidence": 0.94, "reasoning": "Synthesized framework \
about platform strategy, connects integration gap to value capture"}}

## Task

Respond with JSON only, no markdown fences:
{{"type": "fleeting|literature|permanent", "confidence": 0.0-1.0, "reasoning": "one sentence why"}}

Insight: {text}"""

_VALID_TYPES = {"fleeting", "literature", "permanent"}


def _parse_llm_json(raw: str) -> dict:
    """Parse JSON from LLM response, handling common formatting issues."""
    # Strip markdown code fences
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    # Strip trailing non-JSON text (LLM sometimes appends explanation)
    brace_end = text.rfind("}")
    if brace_end != -1:
        text = text[: brace_end + 1]

    return json.loads(text)


def _validate_classification(parsed: dict) -> Classification:
    """Validate and normalize parsed classification."""
    note_type = parsed.get("type", "fleeting")
    if note_type not in _VALID_TYPES:
        note_type = "fleeting"

    confidence = parsed.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)):
        confidence = 0.5
    confidence = max(0.0, min(1.0, float(confidence)))

    reasoning = parsed.get("reasoning", "")
    if not isinstance(reasoning, str):
        reasoning = str(reasoning)

    return Classification(
        note_type=note_type,
        confidence=confidence,
        reasoning=reasoning,
    )


def classify_note(text: str) -> Classification:
    """Classify text into a Zettelkasten note type."""
    try:
        raw = chat(
            CLASSIFY_PROMPT.format(text=text),
            max_tokens=200,
            system=SYSTEM_PROMPT,
        )
        parsed = _parse_llm_json(raw)
        return _validate_classification(parsed)
    except (json.JSONDecodeError, KeyError):
        # Retry once on parse failure
        try:
            raw = chat(
                CLASSIFY_PROMPT.format(text=text),
                max_tokens=200,
                system=SYSTEM_PROMPT,
            )
            parsed = _parse_llm_json(raw)
            return _validate_classification(parsed)
        except Exception:
            return Classification(
                note_type="fleeting",
                confidence=0.0,
                reasoning="Classification failed — defaulting to fleeting",
            )
