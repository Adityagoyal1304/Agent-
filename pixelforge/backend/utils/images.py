"""
utils/images.py — Image encode/decode helpers and the filmstrip builder.

The filmstrip is the portfolio artifact: a single horizontal image showing the
target alongside every rendered attempt, with score labels. Clean, no-dependency
output that captures the entire run at a glance.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import base64
import io
from PIL import Image, ImageDraw, ImageFont

from config import VIEWPORT_WIDTH, VIEWPORT_HEIGHT


def encode_image_b64(path: str) -> str:
    """Read a PNG file and return its base64 string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def decode_b64_to_image(b64: str) -> Image.Image:
    """Decode a base64 string to a PIL Image."""
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def b64_to_bytes(b64: str) -> bytes:
    """Decode base64 to raw bytes."""
    return base64.b64decode(b64)


# Filmstrip constants
STRIP_THUMB_W = 320        # Width of each thumbnail in the filmstrip
STRIP_THUMB_H = 200        # Height of each thumbnail
STRIP_LABEL_H = 28         # Height of the label bar below each thumbnail
STRIP_PADDING = 12         # Padding between thumbnails
STRIP_BG = (20, 20, 30)    # Dark background
STRIP_LABEL_BG = (35, 35, 50)
STRIP_TEXT = (230, 230, 240)
STRIP_PASS_COLOR = (34, 197, 94)    # Green — score ≥ 85
STRIP_WARN_COLOR = (251, 191, 36)   # Amber — score 60-84
STRIP_FAIL_COLOR = (239, 68, 68)    # Red   — score < 60


def _score_color(score: int):
    if score >= 85:
        return STRIP_PASS_COLOR
    if score >= 60:
        return STRIP_WARN_COLOR
    return STRIP_FAIL_COLOR


def build_filmstrip(
    target_b64: str,
    iterations: list[dict],  # [{"iteration": 1, "render_b64": "...", "score": 72}, ...]
) -> Image.Image:
    """
    Build a horizontal filmstrip: target + one panel per iteration.
    Each panel shows the thumbnail + score label.
    Returns a PIL Image.
    """
    n_panels = 1 + len(iterations)   # target + attempts
    cell_w = STRIP_THUMB_W + STRIP_PADDING
    total_w = STRIP_PADDING + n_panels * cell_w
    total_h = STRIP_PADDING + STRIP_THUMB_H + STRIP_LABEL_H + STRIP_PADDING

    canvas = Image.new("RGB", (total_w, total_h), color=STRIP_BG)
    draw = ImageDraw.Draw(canvas)

    # Try to load a font; fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 13)
        font_small = ImageFont.truetype("arial.ttf", 11)
    except IOError:
        font = ImageFont.load_default()
        font_small = font

    def paste_panel(img_b64_or_img, label: str, score: int | None, col: int):
        x = STRIP_PADDING + col * cell_w
        y = STRIP_PADDING

        # Resize thumbnail
        if isinstance(img_b64_or_img, str):
            img = decode_b64_to_image(img_b64_or_img)
        else:
            img = img_b64_or_img
        thumb = img.resize((STRIP_THUMB_W, STRIP_THUMB_H), Image.LANCZOS)
        canvas.paste(thumb, (x, y))

        # Label bar
        label_y = y + STRIP_THUMB_H
        draw.rectangle([x, label_y, x + STRIP_THUMB_W, label_y + STRIP_LABEL_H], fill=STRIP_LABEL_BG)

        text_color = _score_color(score) if score is not None else STRIP_TEXT
        draw.text((x + 6, label_y + 6), label, font=font, fill=text_color)

    # Paste target (column 0)
    paste_panel(target_b64, "TARGET", None, 0)

    # Paste each attempt
    for idx, it in enumerate(iterations):
        score = it.get("score", 0)
        iteration_num = it.get("iteration", idx + 1)
        render_b64 = it.get("render_b64", "")
        label = f"#{iteration_num}  {score}/100"
        paste_panel(render_b64, label, score, idx + 1)

    return canvas
