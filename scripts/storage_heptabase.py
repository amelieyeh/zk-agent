"""
Heptabase storage backend.

Saves notes via Heptabase MCP (save_to_note_card, append_to_journal,
semantic_search_objects). Requires OAuth setup via 'zk-agent setup'.
"""

from datetime import datetime, timezone

from heptabase_client import (
    save_note_card,
    search_related as _search_related,
    append_journal,
    get_journal_today,
)

JOURNAL_SECTION = "## 🧠 ZK Fleeting Notes"


class HeptabaseStorage:
    """Heptabase MCP storage backend."""

    async def save_card(self, title: str, content_md: str) -> str:
        return await save_note_card(content_md)

    async def save_fleeting(self, title: str, text: str, tags: list[str]) -> bool:
        tags_str = ", ".join(f"#{t}" for t in tags)
        bullet = f"- {title} — {text[:100]}{'...' if len(text) > 100 else ''} ({tags_str})"

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        try:
            journal_content = await get_journal_today(today)
            has_header = JOURNAL_SECTION in journal_content
        except Exception:
            has_header = False

        entry = f"\n{bullet}" if has_header else f"{JOURNAL_SECTION}\n\n{bullet}"

        try:
            await append_journal(entry)
            return True
        except Exception:
            return False

    async def search_related(self, query: str, max_results: int = 3) -> list[dict]:
        results = await _search_related(query, max_results)
        related = []
        for item in results:
            if isinstance(item, dict) and "title" in item:
                related.append({"title": item["title"]})
            elif isinstance(item, dict) and "raw" in item:
                related.append({"title": item["raw"][:80]})
        return related
