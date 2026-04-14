"""
Config — manages user configuration at ~/.zk-agent/config.

Handles reading/writing config and loading values into os.environ
so the rest of the codebase works unchanged.
"""

import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".zk-agent"
CONFIG_PATH = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """Load config from ~/.zk-agent/config.json, or return empty dict."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def save_config(config: dict):
    """Save config to ~/.zk-agent/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(config, indent=2))
    os.chmod(tmp, 0o600)
    tmp.rename(CONFIG_PATH)


def apply_config():
    """Load config and set os.environ for LLM + storage.

    Priority: environment variables > config file > .env file.
    """
    config = load_config()

    env_mappings = {
        "llm_api_key": "LLM_API_KEY",
        "llm_base_url": "LLM_BASE_URL",
        "llm_model": "LLM_MODEL",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "storage": "STORAGE",
        "obsidian_vault": "OBSIDIAN_VAULT",
        "obsidian_notes_dir": "OBSIDIAN_NOTES_DIR",
        "obsidian_daily_dir": "OBSIDIAN_DAILY_DIR",
    }

    for config_key, env_key in env_mappings.items():
        if config_key in config and not os.environ.get(env_key):
            os.environ[env_key] = config[config_key]
