"""
Heptabase MCP Client.

Direct connection to Heptabase via Python MCP SDK.
Token resolution: ~/.zk-agent/tokens/ → OAuth flow.
"""

import json

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

from oauth import get_stored_token, build_oauth_provider, _find_free_port, _start_callback_server, _callback_result

HEPTABASE_MCP_URL = "https://api.heptabase.com/mcp"


async def _get_session():
    """Create an MCP client session to Heptabase.

    Uses stored token if available, falls back to OAuth flow.
    """
    token = get_stored_token()
    if token:
        # Fast path: use stored Bearer token
        return streamablehttp_client(
            HEPTABASE_MCP_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

    # No token — trigger OAuth flow
    print("No Heptabase token found. Starting authorization...", flush=True)
    port = _find_free_port()
    server = _start_callback_server(port)
    _callback_result.clear()
    try:
        provider = build_oauth_provider(port)
        return streamablehttp_client(HEPTABASE_MCP_URL, auth=provider)
    finally:
        server.shutdown()


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
    """Search Heptabase for notes related to query text."""
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


async def get_journal_today(date: str) -> str:
    """Read today's journal content. Date format: YYYY-MM-DD."""
    async with await _get_session() as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_journal_range", {"startDate": date, "endDate": date}
            )
            return result.content[0].text
