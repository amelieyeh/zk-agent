"""Load .env before tests run."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from env import load_env
load_env()
