"""
Note Linker.

Searches existing Heptabase notes via semantic_search_objects
and suggests connections for the new note.
"""

from heptabase_client import search_related


async def find_related_notes(text: str, max_results: int = 3) -> list[dict]:
    """Search Heptabase for notes related to the given text."""
    results = await search_related(text, max_results)

    related = []
    for item in results:
        if isinstance(item, dict) and "title" in item:
            related.append({"title": item["title"]})
        elif isinstance(item, dict) and "raw" in item:
            related.append({"title": item["raw"][:80]})
    return related
