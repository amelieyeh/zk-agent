"""Tests for the ZK classifier using sample fixtures."""

import json
import os
from pathlib import Path

import pytest

from zk_agent.classifier import classify_note

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "sample_insights.json"


def load_fixtures():
    with open(FIXTURES_PATH) as f:
        return json.load(f)


@pytest.fixture
def fixtures():
    return load_fixtures()


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("LLM_API_KEY"),
    reason="No LLM API key set",
)
class TestClassifier:
    def test_returns_valid_structure(self, fixtures):
        result = classify_note(fixtures[0]["text"])
        assert "note_type" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert result["note_type"] in ("fleeting", "literature", "permanent")
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.parametrize("idx", range(5))
    def test_fixture_classification(self, fixtures, idx):
        fixture = fixtures[idx]
        result = classify_note(fixture["text"])
        assert result["note_type"] == fixture["expected_type"], (
            f"Expected {fixture['expected_type']}, got {result['note_type']}. "
            f"Reasoning: {result['reasoning']}"
        )
