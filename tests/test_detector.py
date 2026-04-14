"""Tests for the insight detector."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from detector import detect_insights


SAMPLE_CONVERSATION = """
User: 我最近在研究 agent 框架，發現 Hermes 和 Claude Code 的設計哲學很不同。
Hermes 是 tool-first，先給你工具再讓你組合。Claude Code 是 conversation-first，
對話本身就是介面。

Agent: 這兩種 approach 各有優缺點...

User: 對，而且我覺得最好的 agent 其實是翻譯者——把複雜的 API 翻譯成人能理解的流程。
不是取代人，是幫人跨越理解的鴻溝。

Agent: 這個觀點很有趣...

User: 另外 Shopify 的 Sidekick 做得不錯，它用一個 AI 入口串起了商品管理、金流和行銷。
"""

EMPTY_CONVERSATION = """
User: 幫我改一下那個 bug
Agent: 好的，我看一下程式碼
User: 改好了嗎
Agent: 改好了，已經 commit
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
