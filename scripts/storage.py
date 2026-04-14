"""
Storage — unified interface for saving notes to any destination.

Configuration via .env:
  STORAGE=heptabase          (default)
  STORAGE=obsidian

Each backend implements: save_card(), save_fleeting(), search_related()
"""

import os
from typing import Protocol


class NoteStorage(Protocol):
    """Interface that all storage backends must implement."""

    async def save_card(self, title: str, content_md: str) -> str:
        """Save a literature/permanent note as a card.

        Args:
            title: Note title
            content_md: Full Markdown content (h1 title included for backends that need it)

        Returns:
            Result message string.
        """
        ...

    async def save_fleeting(self, title: str, text: str, tags: list[str]) -> bool:
        """Save a fleeting note (journal/daily note, not a standalone card).

        Args:
            title: Short title
            text: The original insight text
            tags: List of tag strings (no # prefix)

        Returns:
            True if saved successfully.
        """
        ...

    async def search_related(self, query: str, max_results: int = 3) -> list[dict]:
        """Search for related existing notes.

        Returns:
            List of dicts with at least a 'title' key.
        """
        ...


def get_storage() -> NoteStorage:
    """Get the configured storage backend from STORAGE env var."""
    backend = os.environ.get("STORAGE", "heptabase").lower()

    if backend == "heptabase":
        from storage_heptabase import HeptabaseStorage
        return HeptabaseStorage()

    if backend == "obsidian":
        from storage_obsidian import ObsidianStorage
        return ObsidianStorage()

    raise ValueError(
        f"Unknown storage backend: {backend}. "
        f"Supported: heptabase, obsidian"
    )
