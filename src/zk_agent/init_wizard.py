"""
Interactive setup wizard for ZK Agent.

Guides the user through LLM provider and note storage configuration.
Saves to ~/.zk-agent/config.json.
"""

import asyncio
import sys

from zk_agent.config import load_config, save_config


def _prompt_choice(question: str, options: list[str], allow_skip: bool = False) -> int | None:
    """Present numbered options, return 0-based index or None if skipped."""
    print(f"\n  {question}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    if allow_skip:
        print(f"  0. Skip")

    while True:
        try:
            raw = input("> ").strip()
            if not raw:
                continue
            choice = int(raw)
            if allow_skip and choice == 0:
                return None
            if 1 <= choice <= len(options):
                return choice - 1
        except (ValueError, EOFError):
            pass
        print(f"  Enter a number 1-{len(options)}")


def _prompt_input(label: str, required: bool = True, secret: bool = False) -> str:
    """Prompt for text input."""
    while True:
        value = input(f"  {label}: ").strip()
        if value or not required:
            return value
        print(f"  This field is required.")


def _verify_llm(config: dict) -> bool:
    """Quick test that the LLM config works."""
    import os
    # Temporarily apply config
    if "anthropic_api_key" in config:
        os.environ["ANTHROPIC_API_KEY"] = config["anthropic_api_key"]
    if "llm_api_key" in config:
        os.environ["LLM_API_KEY"] = config["llm_api_key"]
    if "llm_base_url" in config:
        os.environ["LLM_BASE_URL"] = config["llm_base_url"]
    if "llm_model" in config:
        os.environ["LLM_MODEL"] = config["llm_model"]

    try:
        from llm import chat
        result = chat("Respond with exactly: OK", max_tokens=10)
        return "OK" in result.upper()
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        return False


def _setup_llm() -> dict:
    """Step 1: Configure LLM provider."""
    print("\nStep 1/2: AI Provider")

    providers = [
        "Anthropic (Claude)",
        "OpenAI (GPT)",
        "OpenRouter (any model)",
        "Ollama (local)",
        "Other (OpenAI-compatible)",
    ]
    choice = _prompt_choice("Which AI provider do you use?", providers)

    config = {}

    if choice == 0:  # Anthropic
        key = _prompt_input("Anthropic API key (sk-ant-...)")
        config["anthropic_api_key"] = key

    elif choice == 1:  # OpenAI
        key = _prompt_input("OpenAI API key (sk-...)")
        config["llm_api_key"] = key
        config["llm_model"] = "gpt-4o-mini"

    elif choice == 2:  # OpenRouter
        key = _prompt_input("OpenRouter API key")
        config["llm_api_key"] = key
        config["llm_base_url"] = "https://openrouter.ai/api/v1"
        model = _prompt_input("Model (e.g. anthropic/claude-haiku-4-5-20251001)")
        config["llm_model"] = model

    elif choice == 3:  # Ollama
        config["llm_api_key"] = "ollama"
        config["llm_base_url"] = "http://localhost:11434/v1"
        model = _prompt_input("Model name (e.g. llama3, mistral)")
        config["llm_model"] = model

    elif choice == 4:  # Other
        key = _prompt_input("API key")
        config["llm_api_key"] = key
        base_url = _prompt_input("Base URL (e.g. https://api.example.com/v1)")
        config["llm_base_url"] = base_url
        model = _prompt_input("Model name")
        config["llm_model"] = model

    print("  Verifying...", end=" ", flush=True)
    if _verify_llm(config):
        print("✓")
    else:
        print("\n  Warning: could not verify API key. Saving anyway.")

    return config


def _setup_storage(config: dict) -> dict:
    """Step 2: Configure note storage."""
    print("\nStep 2/2: Note Storage")

    options = [
        "Heptabase (cloud, requires OAuth)",
        "Obsidian (local vault)",
        "None (output Markdown only)",
    ]
    choice = _prompt_choice("Where do you save notes?", options)

    if choice == 0:  # Heptabase
        config["storage"] = "heptabase"
        print("\n  Authorizing Heptabase...")
        try:
            from zk_agent.setup import run_setup
            asyncio.run(run_setup())
        except Exception as e:
            print(f"  ✗ OAuth failed: {e}")
            print("  You can retry later with: zk-agent setup")

    elif choice == 1:  # Obsidian
        config["storage"] = "obsidian"
        vault = _prompt_input("Obsidian vault path (e.g. ~/Documents/MyVault)")
        config["obsidian_vault"] = vault
        print(f"  ✓ Cards → {{vault}}/ZK-Agent/, fleeting → {{vault}}/Daily Notes/")

    elif choice == 2:  # None
        pass  # No storage key = output only

    return config


def run_init():
    """Run the full interactive setup wizard."""
    print("=" * 50)
    print("  ZK Agent — Setup Wizard")
    print("=" * 50)

    existing = load_config()
    if existing:
        print(f"\n  Existing config found at ~/.zk-agent/config.json")
        answer = input("  Reconfigure? (y/n): ").strip().lower()
        if answer != "y":
            print("  Setup cancelled.")
            return

    config = {}

    # Step 1: LLM
    llm_config = _setup_llm()
    config.update(llm_config)

    # Step 2: Storage
    config = _setup_storage(config)

    # Save
    save_config(config)
    print(f"\n{'=' * 50}")
    print(f"  ✅ Setup complete!")
    print(f"  Config saved to ~/.zk-agent/config.json")
    print(f"\n  Try it:")
    print(f'    zk-agent "Your first insight"')
    print(f"{'=' * 50}")
