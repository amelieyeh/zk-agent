"""
ZK Agent — Main entry point.

Orchestrates the full flow:
  input → classify → metadata → link → format → save to Heptabase → journal
"""

import asyncio
import sys
from pathlib import Path

from env import load_env
load_env()

from classifier import classify_note
from metadata_generator import generate_metadata, NoteMetadata
from linker import find_related_notes
from journal import log_fleeting_to_journal
from heptabase_client import save_note_card


def _format_card(text: str, metadata: NoteMetadata) -> str:
    """Format note as Markdown card for Heptabase.

    Heptabase save_to_note_card expects Markdown where:
    - First line must be h1 (# Title) → becomes card title
    - Blocks separated by blank lines
    - Source rendered as clickable Markdown link
    - Used for literature/permanent notes only (fleeting → journal)
    """
    tags_str = ", ".join(f"#{t}" for t in metadata["tags"])
    related_str = "\n".join(
        f"- {r}" for r in metadata["related_notes"]
    ) or "None yet"

    source_line = f"Source: [{metadata['source']}]({metadata['source']})" if metadata["source"] else ""
    meta_block = "\n".join(
        line for line in [
            f"Type: {metadata['note_type']} | Confidence: {metadata['confidence']:.0%}",
            f"Tags: {tags_str}",
            source_line,
            f"Created: {metadata['created_at'][:10]}",
        ] if line
    )

    return f"""# {metadata['title']}

{text}

---

{meta_block}

## Related Notes

{related_str}"""


async def save_note(text: str, source: str | None = None) -> dict:
    """Full ZK save pipeline."""
    # Step 1: Classify note type (sync — Claude API call)
    classification = classify_note(text)

    # Step 2: Generate metadata (sync — Claude API call)
    metadata = generate_metadata(text, classification, source=source)

    # Step 3: Route by note type
    if classification["note_type"] == "fleeting":
        # Fleeting → journal only, no card
        journal_ok = await log_fleeting_to_journal(
            text, metadata["title"], metadata["tags"]
        )
        return {
            "classification": dict(classification),
            "metadata": dict(metadata),
            "related": [],
            "saved": None,
            "journal": journal_ok,
        }

    # Literature/Permanent → card + related notes, no journal
    related = await find_related_notes(text)
    metadata["related_notes"] = [r["title"] for r in related]

    card_md = _format_card(text, metadata)
    save_result = await save_note_card(card_md)

    return {
        "classification": dict(classification),
        "metadata": dict(metadata),
        "related": related,
        "saved": save_result,
        "journal": False,
    }


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "setup":
        from setup import run_setup
        asyncio.run(run_setup())
        return

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python zk_agent.py setup                  — Authorize Heptabase")
        print("  python zk_agent.py <text> [--source <url>] — Save an insight")
        sys.exit(1)

    args = sys.argv[1:]
    source = None
    if "--source" in args:
        idx = args.index("--source")
        source = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    text = " ".join(args)
    result = asyncio.run(save_note(text, source=source))

    note_type = result['classification']['note_type']
    if note_type == "fleeting":
        print(f"\n📝 Fleeting note → journal")
    else:
        print(f"\n✅ Saved as {note_type} note → card")
    print(f"   Title: {result['metadata']['title']}")
    print(f"   Tags: {', '.join(f'#{t}' for t in result['metadata']['tags'])}")
    print(f"   Confidence: {result['classification']['confidence']:.0%}")
    print(f"   Reasoning: {result['classification']['reasoning']}")
    if result["related"]:
        print(f"   Related: {', '.join(r['title'] for r in result['related'])}")


if __name__ == "__main__":
    main()
