"""
Obsidian storage backend.

Saves notes as local Markdown files in an Obsidian vault.
Fleeting notes append to a daily note file.
No API required — just writes to the filesystem.

Configuration via .env:
  OBSIDIAN_VAULT=/path/to/your/vault
  OBSIDIAN_NOTES_DIR=ZK-Agent           (subfolder for cards, default: ZK-Agent)
  OBSIDIAN_DAILY_DIR=Daily Notes        (subfolder for daily notes, default: Daily Notes)
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path


def _vault_path() -> Path:
    vault = os.environ.get("OBSIDIAN_VAULT")
    if not vault:
        raise RuntimeError(
            "OBSIDIAN_VAULT not set in .env. "
            "Set it to your Obsidian vault path, e.g. OBSIDIAN_VAULT=~/Documents/MyVault"
        )
    return Path(vault).expanduser()


def _sanitize_filename(title: str) -> str:
    """Remove characters not allowed in filenames."""
    return re.sub(r'[<>:"/\\|?*]', "", title).strip()


JOURNAL_SECTION = "## 🧠 ZK Fleeting Notes"


class ObsidianStorage:
    """Obsidian vault storage backend — writes local Markdown files."""

    async def save_card(self, title: str, content_md: str) -> str:
        vault = _vault_path()
        notes_dir = vault / os.environ.get("OBSIDIAN_NOTES_DIR", "ZK-Agent")
        notes_dir.mkdir(parents=True, exist_ok=True)

        filename = _sanitize_filename(title) + ".md"
        filepath = notes_dir / filename

        filepath.write_text(content_md, encoding="utf-8")
        return f"Saved to {filepath}"

    async def save_fleeting(self, title: str, text: str, tags: list[str]) -> bool:
        vault = _vault_path()
        daily_dir = vault / os.environ.get("OBSIDIAN_DAILY_DIR", "Daily Notes")
        daily_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filepath = daily_dir / f"{today}.md"

        tags_str = ", ".join(f"#{t}" for t in tags)
        bullet = f"- {title} — {text[:100]}{'...' if len(text) > 100 else ''} ({tags_str})"

        if filepath.exists():
            existing = filepath.read_text(encoding="utf-8")
            if JOURNAL_SECTION in existing:
                filepath.write_text(existing + f"\n{bullet}\n", encoding="utf-8")
            else:
                filepath.write_text(existing + f"\n\n{JOURNAL_SECTION}\n\n{bullet}\n", encoding="utf-8")
        else:
            filepath.write_text(f"# {today}\n\n{JOURNAL_SECTION}\n\n{bullet}\n", encoding="utf-8")

        return True

    async def search_related(self, query: str, max_results: int = 3) -> list[dict]:
        """Simple filename-based search in vault.

        Obsidian doesn't have a semantic search API.
        This does a basic keyword match on filenames in the notes dir.
        """
        vault = _vault_path()
        notes_dir = vault / os.environ.get("OBSIDIAN_NOTES_DIR", "ZK-Agent")
        if not notes_dir.exists():
            return []

        keywords = query.lower().split()
        matches = []
        for md_file in notes_dir.glob("*.md"):
            name = md_file.stem.lower()
            if any(k in name for k in keywords):
                matches.append({"title": md_file.stem})
                if len(matches) >= max_results:
                    break
        return matches
