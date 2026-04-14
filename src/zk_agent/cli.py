"""
ZK Agent CLI — entry point for the `zk-agent` command.

Orchestrates: classify → metadata → route → save/output
"""

import asyncio
import sys

from zk_agent.config import apply_config
from zk_agent.env import load_env
apply_config()
load_env()

from zk_agent.classifier import classify_note
from zk_agent.metadata_generator import generate_metadata, NoteMetadata
from zk_agent.storage import get_storage


def _format_card(text: str, metadata: NoteMetadata) -> str:
    """Format note as Markdown card.

    Format:
    - First line is h1 (# Title) — used as card title by Heptabase,
      and as filename by Obsidian
    - Blocks separated by blank lines
    - Source rendered as clickable Markdown link
    - Used for literature/permanent notes only (fleeting → daily note)
    """
    all_tags = [metadata["note_type"]] + list(metadata["tags"])
    tags_str = ", ".join(f"#{t}" for t in all_tags)
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
    store = get_storage()

    classification = classify_note(text)
    metadata = generate_metadata(text, classification, source=source)

    if classification["note_type"] == "fleeting":
        if store:
            ok = await store.save_fleeting(metadata["title"], text, metadata["tags"])
        else:
            ok = False
        return {
            "classification": dict(classification),
            "metadata": dict(metadata),
            "related": [],
            "saved": None,
            "fleeting_saved": ok,
        }

    related = await store.search_related(text) if store else []
    metadata["related_notes"] = [r["title"] for r in related]

    card_md = _format_card(text, metadata)

    if store:
        save_result = await store.save_card(metadata["title"], card_md)
    else:
        save_result = None

    return {
        "classification": dict(classification),
        "metadata": dict(metadata),
        "related": related,
        "saved": save_result,
        "fleeting_saved": False,
        "content_md": card_md,
    }


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "init":
        from zk_agent.init_wizard import run_init
        run_init()
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "setup":
        from zk_agent.setup import run_setup
        asyncio.run(run_setup())
        return

    if len(sys.argv) < 2:
        print("Usage:")
        print("  zk-agent init                    — Interactive setup wizard")
        print("  zk-agent setup                   — Re-authorize Heptabase OAuth")
        print('  zk-agent "insight text"           — Save an insight')
        print('  zk-agent "text" --source <url>    — Save with source attribution')
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
    has_storage = result.get("saved") is not None or result.get("fleeting_saved")

    if note_type == "fleeting":
        print(f"\n📝 Fleeting note{' → saved' if has_storage else ''}")
    else:
        print(f"\n{'✅ Saved' if has_storage else '📋 Classified'} as {note_type} note")
    print(f"   Title: {result['metadata']['title']}")
    print(f"   Tags: {', '.join(f'#{t}' for t in result['metadata']['tags'])}")
    print(f"   Confidence: {result['classification']['confidence']:.0%}")
    print(f"   Reasoning: {result['classification']['reasoning']}")
    if result["related"]:
        print(f"   Related: {', '.join(r['title'] for r in result['related'])}")

    if not has_storage and result.get("content_md"):
        print(f"\n--- Markdown output ---\n")
        print(result["content_md"])


if __name__ == "__main__":
    main()
