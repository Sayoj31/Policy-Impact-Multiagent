"""
config.py
---------
Central configuration for the Policy Impact Analysis multi-agent system.

Loads settings from environment variables (via a local .env file if present)
and exposes a single OpenAI-compatible client used by every agent.

Why a single shared client?
    Each agent module imports `client` and `MODEL_NAME` from here instead of
    constructing its own client. That keeps API keys / model choice in one
    place and makes it trivial to swap providers later.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from a .env file in the project root (if one exists).
load_dotenv()

# --- LLM settings -----------------------------------------------------
# Works with any OpenAI-compatible endpoint. To point this at a different
# provider (Azure OpenAI, a local vLLM server, OpenRouter, etc.) just set
# OPENAI_BASE_URL in your .env file - no code changes needed.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # optional
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Copy .env.example to .env and fill in "
        "your key before running the system."
    )

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# --- Misc settings ------------------------------------------------------
MAX_TOOL_ITERATIONS = int(os.getenv("MAX_TOOL_ITERATIONS", "4"))
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"


def log(agent_name: str, message: str) -> None:
    """Small helper so every agent prints its progress the same way."""
    if VERBOSE:
        print(f"[{agent_name}] {message}")
