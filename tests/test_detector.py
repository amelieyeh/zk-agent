"""Tests for the insight detector."""

import os

import pytest

from zk_agent.detector import detect_insights, _parse_llm_json_array
from zk_agent.classifier import classify_note


SAMPLE_CONVERSATION = """
User: I've been comparing agent frameworks and found that tool-first vs
conversation-first is a fundamental design difference. Some frameworks give
you tools first and let you compose them. Others make the conversation itself
the interface.

Agent: Both approaches have trade-offs...

User: Right, and I think the best agents are actually translators — they take
complex APIs and translate them into flows humans can understand. Not replacing
people, but bridging the comprehension gap.

Agent: That's an interesting perspective...

User: Also, Shopify's Sidekick is a good example — it ties together product
management, payments, and marketing through a single AI entry point.
"""

EMPTY_CONVERSATION = """
User: Can you fix that bug?
Agent: Sure, let me look at the code
User: Is it done?
Agent: Done, committed.
"""


class TestParseJsonArray:
    """Unit tests for JSON array parsing — no LLM needed."""

    def test_parse_clean_array(self):
        result = _parse_llm_json_array('[{"text": "x", "suggested_type": "fleeting", "reason": "y"}]')
        assert len(result) == 1

    def test_parse_empty_array(self):
        result = _parse_llm_json_array("[]")
        assert result == []

    def test_parse_with_markdown_fences(self):
        raw = '```json\n[{"text": "x", "suggested_type": "permanent", "reason": "y"}]\n```'
        result = _parse_llm_json_array(raw)
        assert len(result) == 1

    def test_parse_with_trailing_text(self):
        raw = '[{"text": "x", "suggested_type": "literature", "reason": "y"}]\n\nThese are the insights.'
        result = _parse_llm_json_array(raw)
        assert len(result) == 1


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("LLM_API_KEY"),
    reason="No LLM API key set",
)
class TestDetector:
    def test_finds_insights_in_rich_conversation(self):
        results = detect_insights(SAMPLE_CONVERSATION)
        assert len(results) >= 1
        for r in results:
            assert "text" in r
            assert "suggested_type" in r
            assert r["suggested_type"] in ("fleeting", "literature", "permanent")

    def test_empty_for_routine_conversation(self):
        results = detect_insights(EMPTY_CONVERSATION)
        assert len(results) == 0

    def test_detector_classifier_consistency(self):
        """Detector suggested_type should match classifier result."""
        results = detect_insights(SAMPLE_CONVERSATION)
        assert len(results) >= 1
        mismatches = []
        for r in results:
            classification = classify_note(r["text"])
            if classification["note_type"] != r["suggested_type"]:
                mismatches.append(
                    f"Detector: {r['suggested_type']}, "
                    f"Classifier: {classification['note_type']}, "
                    f"Text: {r['text'][:60]}..."
                )
        assert not mismatches, (
            f"{len(mismatches)} type mismatches between detector and classifier:\n"
            + "\n".join(mismatches)
        )
