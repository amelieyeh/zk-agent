"""Tests for the insight detector."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from detector import detect_insights


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


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
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
