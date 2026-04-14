"""Load .env file into os.environ (developer override)."""

import os
from pathlib import Path


def load_env():
    """Search for .env in current directory or project root."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent / ".env",  # src/../.env = project root
    ]
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
            return
