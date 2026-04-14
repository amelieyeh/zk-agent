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
from journal import log_to_journal
from heptabase_client import save_note_card


def _format_card(text: str, metadata: NoteMetadata) -> str:
    """Format note as Markdown card for Heptabase.

    First line is # title (becomes card title in Heptabase).
    """
    tags_str = ", ".join(f"#{t}" for t in metadata["tags"])
    related_str = "\n".join(
        f"- {r}" for r in metadata["related_notes"]
    ) or "None yet"

    source_line = f"Source: {metadata['source']}" if metadata["source"] else ""
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

    # Step 3: Search for related notes (async — Heptabase MCP)
    related = await find_related_notes(text)
    metadata["related_notes"] = [r["title"] for r in related]

    # Step 4: Format and save to Heptabase (async — Heptabase MCP)
    card_md = _format_card(text, metadata)
    save_result = await save_note_card(card_md)

    # Step 5: Log to daily journal (async — Heptabase MCP)
    journal_ok = await log_to_journal(metadata)

    return {
        "classification": dict(classification),
        "metadata": dict(metadata),
        "related": related,
        "saved": save_result,
        "journal": journal_ok,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python zk_agent.py <text> [--source <source>]")
        sys.exit(1)

    args = sys.argv[1:]
    source = None
    if "--source" in args:
        idx = args.index("--source")
        source = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    text = " ".join(args)
    result = asyncio.run(save_note(text, source=source))

    print(f"\n✅ Saved as {result['classification']['note_type']} note")
    print(f"   Title: {result['metadata']['title']}")
    print(f"   Tags: {', '.join(f'#{t}' for t in result['metadata']['tags'])}")
    print(f"   Confidence: {result['classification']['confidence']:.0%}")
    print(f"   Reasoning: {result['classification']['reasoning']}")
    if result["related"]:
        print(f"   Related: {', '.join(r['title'] for r in result['related'])}")
    print(f"   Journal: {'✓' if result['journal'] else '✗'}")


if __name__ == "__main__":
    main()
