"""
Journal Logger.

Appends fleeting notes to Heptabase journal under a dedicated section.
Literature/permanent notes are saved as cards, not logged to journal.
"""

from heptabase_client import append_journal


JOURNAL_SECTION = "## 🧠 ZK Fleeting Notes"


async def log_fleeting_to_journal(text: str, title: str, tags: list[str]) -> bool:
    """Append a fleeting note to today's Heptabase journal.

    Adds a section header on first call, then bullet points for each note.
    """
    tags_str = ", ".join(f"#{t}" for t in tags)
    entry = f"{JOURNAL_SECTION}\n\n- {title} — {text[:100]}{'...' if len(text) > 100 else ''} ({tags_str})"

    try:
        await append_journal(entry)
        return True
    except Exception:
        return False
