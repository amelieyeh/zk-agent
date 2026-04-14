"""
Journal Logger.

Appends fleeting notes to Heptabase journal under a dedicated section.
Literature/permanent notes are saved as cards, not logged to journal.
"""

from datetime import datetime, timezone

from heptabase_client import append_journal, get_journal_today

JOURNAL_SECTION = "## 🧠 ZK Fleeting Notes"


async def log_fleeting_to_journal(text: str, title: str, tags: list[str]) -> bool:
    """Append a fleeting note to today's Heptabase journal.

    Format in journal:
      ## 🧠 ZK Fleeting Notes
      - Title — preview text... (#tag1, #tag2)

    Section header is only added once per day. Subsequent notes
    append as bullet points under the existing header.
    """
    tags_str = ", ".join(f"#{t}" for t in tags)
    bullet = f"- {title} — {text[:100]}{'...' if len(text) > 100 else ''} ({tags_str})"

    # Check if today's journal already has our section header
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        journal_content = await get_journal_today(today)
        has_header = JOURNAL_SECTION in journal_content
    except Exception:
        has_header = False

    if has_header:
        entry = f"\n{bullet}"
    else:
        entry = f"{JOURNAL_SECTION}\n\n{bullet}"

    try:
        await append_journal(entry)
        return True
    except Exception:
        return False
