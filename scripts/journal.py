"""
Journal Logger.

Appends fleeting notes to Heptabase journal under a dedicated section.
Literature/permanent notes are saved as cards, not logged to journal.
"""

from heptabase_client import append_journal


JOURNAL_SECTION = "## 🧠 ZK Fleeting Notes"


async def log_fleeting_to_journal(text: str, title: str, tags: list[str]) -> bool:
    """Append a fleeting note to today's Heptabase journal.

    Format in journal:
      ## 🧠 ZK Fleeting Notes
      - Title — preview text... (#tag1, #tag2)

    Section header keeps ZK captures separate from hand-written journal content.
    """
    tags_str = ", ".join(f"#{t}" for t in tags)
    entry = f"{JOURNAL_SECTION}\n\n- {title} — {text[:100]}{'...' if len(text) > 100 else ''} ({tags_str})"

    try:
        await append_journal(entry)
        return True
    except Exception:
        return False
