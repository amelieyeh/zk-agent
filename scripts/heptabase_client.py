"""
Heptabase MCP Client.

Direct connection to Heptabase via Python MCP SDK + OAuth token.
Tokens managed by Hermes at ~/.hermes/mcp-tokens/heptabase.json.
"""

import json
from pathlib import Path

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

HEPTABASE_MCP_URL = "https://api.heptabase.com/mcp"
TOKEN_PATH = Path.home() / ".hermes" / "mcp-tokens" / "heptabase.json"


def _load_token() -> str:
    with open(TOKEN_PATH) as f:
        data = json.load(f)
    return data["access_token"]


async def _get_session():
    """Create an MCP client session to Heptabase."""
    token = _load_token()
    headers = {"Authorization": f"Bearer {token}"}
    return streamablehttp_client(HEPTABASE_MCP_URL, headers=headers)


async def save_note_card(content_md: str) -> str:
    """Save a markdown note card to Heptabase.

    The first line must be an h1 heading (# Title) which becomes the card title.
    Returns the result text from MCP.
    """
    async with await _get_session() as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "save_to_note_card", {"content": content_md}
            )
            return result.content[0].text


async def search_related(query: str, max_results: int = 3) -> list[dict]:
    """Search Heptabase for notes related to query text.

    Returns list of result objects from semantic_search_objects.
    """
    async with await _get_session() as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "semantic_search_objects",
                {"queries": [query], "resultObjectTypes": ["card"]},
            )
            text = result.content[0].text
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return [{"raw": text}]


async def append_journal(content: str) -> str:
    """Append content to today's Heptabase journal."""
    async with await _get_session() as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "append_to_journal", {"content": content}
            )
            return result.content[0].text
