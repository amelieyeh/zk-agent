"""Tests for the ZK classifier using sample fixtures."""

import json
import os
from pathlib import Path

import pytest

from zk_agent.classifier import classify_note, _parse_llm_json, _validate_classification

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "sample_insights.json"


def load_fixtures():
    with open(FIXTURES_PATH) as f:
        return json.load(f)


@pytest.fixture
def fixtures():
    return load_fixtures()


class TestParseAndValidation:
    """Unit tests for JSON parsing and validation — no LLM needed."""

    def test_parse_clean_json(self):
        result = _parse_llm_json('{"type": "fleeting", "confidence": 0.8, "reasoning": "test"}')
        assert result["type"] == "fleeting"

    def test_parse_with_markdown_fences(self):
        raw = '```json\n{"type": "permanent", "confidence": 0.9, "reasoning": "test"}\n```'
        result = _parse_llm_json(raw)
        assert result["type"] == "permanent"

    def test_parse_with_trailing_text(self):
        raw = '{"type": "literature", "confidence": 0.85, "reasoning": "test"}\n\nThis is a literature note.'
        result = _parse_llm_json(raw)
        assert result["type"] == "literature"

    def test_validate_clamps_confidence(self):
        result = _validate_classification({"type": "permanent", "confidence": 1.5, "reasoning": "x"})
        assert result["confidence"] == 1.0

        result = _validate_classification({"type": "permanent", "confidence": -0.5, "reasoning": "x"})
        assert result["confidence"] == 0.0

    def test_validate_invalid_type_defaults_to_fleeting(self):
        result = _validate_classification({"type": "invalid", "confidence": 0.9, "reasoning": "x"})
        assert result["note_type"] == "fleeting"

    def test_validate_missing_fields(self):
        result = _validate_classification({})
        assert result["note_type"] == "fleeting"
        assert result["confidence"] == 0.5
        assert result["reasoning"] == ""


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

    @pytest.mark.parametrize("idx", range(len(load_fixtures())))
    def test_fixture_classification(self, fixtures, idx):
        fixture = fixtures[idx]
        result = classify_note(fixture["text"])
        assert result["note_type"] == fixture["expected_type"], (
            f"Expected {fixture['expected_type']}, got {result['note_type']}. "
            f"Reasoning: {result['reasoning']}"
        )
