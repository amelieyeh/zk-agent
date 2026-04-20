"""
Scope — optional project context for scoped classification.

A scope points ZK Agent at a Heptabase whiteboard so it understands
your project before classifying. Same pipeline, better judgment.

Config files live in ~/.zk-agent/scopes/<name>.json
"""

import json
from pathlib import Path
from typing import TypedDict

from zk_agent.config import CONFIG_DIR

SCOPES_DIR = CONFIG_DIR / "scopes"


class ScopeConfig(TypedDict):
    name: str
    whiteboard: str
    whiteboard_id: str
    context_cards: list[str]
    tags_prefix: str


def load_scope(name: str) -> ScopeConfig | None:
    """Load a scope config by name.

    Returns None if the scope file doesn't exist.
    """
    path = SCOPES_DIR / f"{name}.json"
    if not path.exists():
        return None

    data = json.loads(path.read_text())

    return ScopeConfig(
        name=data.get("name", name),
        whiteboard=data.get("whiteboard", ""),
        whiteboard_id=data.get("whiteboard_id", ""),
        context_cards=data.get("context_cards", []),
        tags_prefix=data.get("tags_prefix", name),
    )


def list_scopes() -> list[str]:
    """List available scope names."""
    if not SCOPES_DIR.exists():
        return []
    return [p.stem for p in SCOPES_DIR.glob("*.json")]
