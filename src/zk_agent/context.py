"""
Context — build project context from a Heptabase whiteboard.

Reads whiteboard structure + key cards, assembles a text summary
that can be injected into classifier/detector prompts.
"""

from zk_agent.scope import ScopeConfig

# Module-level cache: avoid re-reading the same whiteboard in one session
_context_cache: dict[str, str] = {}

# Max cards to read full content for (avoid huge context)
_MAX_CARDS_TO_READ = 10


async def build_context(scope: ScopeConfig) -> str | None:
    """Build a text context from a scope's Heptabase whiteboard.

    Returns a formatted string suitable for prompt injection,
    or None if the whiteboard can't be found.
    """
    cache_key = scope["name"]
    if cache_key in _context_cache:
        return _context_cache[cache_key]

    from zk_agent.heptabase_client import (
        search_whiteboards,
        get_whiteboard_with_objects,
        get_object,
    )

    # Step 1: Find the whiteboard (prefer ID, fall back to search)
    board_id = scope.get("whiteboard_id")
    if not board_id:
        boards = await search_whiteboards(scope["whiteboard"])
        if not boards:
            return None
        # Prefer exact name match
        board_id = boards[0]["id"]
        for b in boards:
            if b["name"].lower() == scope["whiteboard"].lower():
                board_id = b["id"]
                break

    # Step 2: Read whiteboard structure
    structure = await get_whiteboard_with_objects(board_id)
    if not structure:
        return None

    objects = structure.get("objects", [])

    # Step 3: Decide which cards to read
    wanted = {name.lower() for name in scope["context_cards"]}
    cards_to_read = []

    for obj in objects:
        title = obj.get("title", "").strip()
        if not title or not obj.get("id"):
            continue

        if wanted:
            # Only read specified cards
            if title.lower() in wanted:
                cards_to_read.append(obj)
        else:
            # No filter — read up to max
            cards_to_read.append(obj)

    cards_to_read = cards_to_read[:_MAX_CARDS_TO_READ]

    # Step 4: Read card contents
    card_contents: list[str] = []
    for obj in cards_to_read:
        content = await get_object(obj["id"])
        if content:
            # Truncate very long cards
            if len(content) > 2000:
                content = content[:2000] + "\n...(truncated)"
            card_contents.append(f"### {obj['title']}\n\n{content}")

    # Step 5: Assemble context
    all_titles = [obj.get("title", "(untitled)") for obj in objects]

    if card_contents:
        context = (
            f"Project: {scope['name']}\n"
            f"Whiteboard: {scope['whiteboard']} ({len(objects)} cards)\n"
            f"All cards: {', '.join(all_titles)}\n\n"
            + "\n\n".join(card_contents)
        )
    else:
        context = (
            f"Project: {scope['name']}\n"
            f"Whiteboard: {scope['whiteboard']}\n"
            f"Contains {len(objects)} cards: {', '.join(all_titles[:20])}"
        )

    _context_cache[cache_key] = context
    return context
