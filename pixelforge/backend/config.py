"""
config.py — Central configuration for PixelForge.
All tuneable constants live here so we change them in one place.
"""

import os
from dotenv import load_dotenv

# Load .env from the same directory as this file.
# The user has already placed GEMINI_API_KEY in backend/.env — we read it here.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# --- Run limits ---
MAX_ITERATIONS = 5        # Hard cap: never loop more than this many times
SCORE_THRESHOLD = 85      # Stop early if visual fidelity reaches this score

# --- Playwright viewport ---
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 800

# --- LLM config (read from environment, never hardcoded) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY not found. Copy .env.example to .env and fill in your key."
    )
