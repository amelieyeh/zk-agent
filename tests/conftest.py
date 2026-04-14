"""Load config + .env before tests run."""

from zk_agent.config import apply_config
from zk_agent.env import load_env
apply_config()
load_env()
