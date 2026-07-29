"""
graph/nodes/palette.py — Extract a colour palette from the target image.

WHY CODE INSTEAD OF A MODEL?
Vision models read hex codes off images unreliably — they hallucinate colours
that are "close" rather than exact. Pillow's quantize() is deterministic and
extracts the true dominant colours in milliseconds with zero API cost.
This is a deliberate design choice: use code where code is unambiguously better.
"""

import sys
import os

# Allow imports from backend/ root when running nodes standalone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from PIL import Image
import io
import base64

from graph.state import GraphState


def extract_palette(state: GraphState) -> dict:
    """
    Pure Python palette extraction. No LLM call.
    Returns a partial state update with the 'palette' field.
    """
    raw = base64.b64decode(state["target_b64"])
    img = Image.open(io.BytesIO(raw)).convert("RGB")

    # Quantize reduces the image to N distinct colours using a median-cut algorithm.
    # 6 colours captures the dominant palette without overwhelming the generator.
    quantized = img.quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    rgb_img = quantized.convert("RGB")

    # Pull the 6 most frequent colours from the quantized palette
    palette_colours = []
    palette_data = rgb_img.getpalette()  # flat list: [R, G, B, R, G, B, ...]
    if palette_data:
        for i in range(6):
            r, g, b = palette_data[i * 3], palette_data[i * 3 + 1], palette_data[i * 3 + 2]
            hex_colour = f"#{r:02x}{g:02x}{b:02x}"
            palette_colours.append(hex_colour)
    else:
        # Fallback: sample pixel colours from a grid
        w, h = rgb_img.size
        for row in range(2):
            for col in range(3):
                px = rgb_img.getpixel((int(w * (col + 0.5) / 3), int(h * (row + 0.5) / 2)))
                palette_colours.append(f"#{px[0]:02x}{px[1]:02x}{px[2]:02x}")

    print(f"  [palette] Extracted: {palette_colours}")
    return {"palette": palette_colours}
