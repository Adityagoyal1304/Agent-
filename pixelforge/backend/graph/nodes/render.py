"""
graph/nodes/render.py — Render HTML to PNG via Playwright headless Chromium.

Key design choices:
- Write HTML to a temp file and use file:// URL (avoids encoding issues with data: URLs).
- wait_for_load_state("networkidle") + 400ms sleep: Tailwind CDN must download
  and apply before we screenshot. Without the sleep, we'd capture unstyled HTML.
- full_page=False: we want the viewport screenshot, not the full scroll height,
  because the target was captured at a fixed viewport.
- Graceful error handling: on Playwright failure, return a blank white PNG and
  log the error. This prevents one bad render from crashing a 5-iteration run.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import base64
import io
import asyncio
import tempfile
import time

from PIL import Image

from config import VIEWPORT_WIDTH, VIEWPORT_HEIGHT
from graph.state import GraphState


def _blank_image_b64() -> str:
    """Return a base64-encoded white 1280x800 PNG for use on render failure."""
    img = Image.new("RGB", (VIEWPORT_WIDTH, VIEWPORT_HEIGHT), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def render_html(state: GraphState) -> dict:
    """
    Write current_html to a temp file, load it in Playwright, screenshot it.
    Returns partial state with 'render_b64' updated.
    """
    html = state.get("current_html", "")
    iteration = state.get("iteration", 1)
    history = list(state.get("history", []))

    if not html:
        print("  [render] No HTML to render, returning blank image.")
        return {"render_b64": _blank_image_b64()}

    # Write HTML to a temp file so Playwright can load it as file://
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.write(html)
    tmp.close()
    tmp_path = tmp.name

    try:
        screenshot_b64 = _run_playwright(tmp_path)
        print(f"  [render] Screenshot captured ({len(screenshot_b64)} chars b64)")
        return {"render_b64": screenshot_b64}
    except Exception as e:
        err_msg = f"Iteration {iteration} render failed: {e}"
        print(f"  [render] ERROR: {err_msg}")
        history.append({"iteration": iteration, "render_error": str(e)})
        return {"render_b64": _blank_image_b64(), "history": history}
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _run_playwright(html_path: str) -> str:
    """Synchronous Playwright call (thread-safe on Windows Python 3.12)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})

        file_url = f"file:///{html_path.replace(os.sep, '/')}"
        page.goto(file_url, wait_until="networkidle", timeout=30000)

        time.sleep(0.4)

        png_bytes = page.screenshot(full_page=False)
        browser.close()

    return base64.b64encode(png_bytes).decode()
