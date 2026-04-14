"""
LLM Client — unified interface for any OpenAI-compatible provider.

Supports: OpenAI, Anthropic (via OpenRouter), Google (via OpenRouter),
Ollama, or any OpenAI-compatible endpoint.

Configuration via .env:
  LLM_API_KEY=sk-xxx              (required)
  LLM_BASE_URL=https://...        (optional, defaults to OpenAI)
  LLM_MODEL=gpt-4o-mini           (optional, defaults to gpt-4o-mini)

  # Shortcut: set ANTHROPIC_API_KEY instead to use Anthropic directly
"""

import os

from openai import OpenAI


def _get_client() -> tuple[OpenAI, str]:
    """Build OpenAI-compatible client from env vars.

    Returns (client, model_name).
    """
    # Shortcut: ANTHROPIC_API_KEY → use Anthropic via their OpenAI-compatible endpoint
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    llm_key = os.environ.get("LLM_API_KEY")

    if llm_key:
        base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
        model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
        return OpenAI(api_key=llm_key, base_url=base_url), model

    if anthropic_key:
        return OpenAI(
            api_key=anthropic_key,
            base_url="https://api.anthropic.com/v1/",
        ), os.environ.get("LLM_MODEL", "claude-haiku-4-5-20251001")

    raise RuntimeError(
        "No LLM API key found. Set LLM_API_KEY (any OpenAI-compatible provider) "
        "or ANTHROPIC_API_KEY in your .env file."
    )


def chat(prompt: str, max_tokens: int = 500) -> str:
    """Send a single prompt and return the response text."""
    client, model = _get_client()

    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()
