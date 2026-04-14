"""
ZK Agent Setup — OAuth flow for Heptabase MCP.

Triggers browser-based OAuth authorization and stores tokens
at ~/.zk-agent/tokens/heptabase.json.
"""

import asyncio

from oauth import get_token_status, build_oauth_provider, _find_free_port, _start_callback_server, _callback_result
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession


async def run_setup():
    """Run the Heptabase OAuth setup flow."""
    status = get_token_status()

    if status["valid"]:
        print(f"Existing token found (source: {status['source']})")
        answer = input("Re-authorize? (y/n): ").strip().lower()
        if answer != "y":
            print("Setup cancelled.")
            return

    print("Starting Heptabase OAuth setup...\n")

    # Start callback server
    port = _find_free_port()
    server = _start_callback_server(port)
    _callback_result.clear()

    try:
        # Build OAuth provider — triggers browser flow on first MCP request
        provider = build_oauth_provider(port)

        # Make a test connection to trigger the OAuth flow
        async with streamablehttp_client(
            "https://api.heptabase.com/mcp",
            auth=provider,
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print(f"\n✅ Authorized! {len(tools.tools)} Heptabase tools available.")
                print(f"   Tokens saved to ~/.zk-agent/tokens/heptabase.json")

    except TimeoutError:
        print("\n❌ OAuth timed out. Please try again.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
    finally:
        server.shutdown()
