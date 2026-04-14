"""
Journal Logger.

Appends daily capture summary to Heptabase journal
via append_to_journal MCP tool.
"""

from heptabase_client import append_journal


async def log_to_journal(metadata: dict) -> bool:
    """Append a note capture record to today's Heptabase journal."""
    tags_str = ", ".join(f"#{t}" for t in metadata.get("tags", []))
    entry = f"- [{metadata['note_type']}] {metadata['title']} ({tags_str})"

    try:
        await append_journal(entry)
        return True
    except Exception:
        return False
