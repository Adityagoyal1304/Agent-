"""
graph/nodes/generate.py — Generate (or revise) HTML from the target screenshot.

Iteration 1: cold start — target image + palette only.
Iteration 2+: warm revision — also include the previous HTML and critique so the
model revises rather than regenerates. This is crucial: regenerating from scratch
on each iteration means losing progress. Revising preserves what works and fixes
only what is called out.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import re
from langchain_core.messages import HumanMessage, SystemMessage

from config import MODEL_NAME
from llm import get_llm
from prompts import GENERATOR_SYSTEM_PROMPT
from graph.state import GraphState


def _strip_fences(text: str) -> str:
    """Remove markdown code fences the model sometimes adds despite instructions."""
    # Strip ```html ... ``` or ``` ... ```
    text = re.sub(r"^```(?:html)?\s*\n?", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\n?```\s*$", "", text.strip())
    return text.strip()


def generate_html(state: GraphState) -> dict:
    """
    Generate or revise HTML. Returns partial state with 'current_html'.
    """
    llm = get_llm()
    iteration = state.get("iteration", 1)
    palette = state.get("palette", [])
    target_b64 = state["target_b64"]

    palette_str = ", ".join(palette)

    # --- Build the human message content (multimodal list) ---
    content = []

    if iteration == 1:
        # Cold start: show the target and palette
        content.append({
            "type": "text",
            "text": (
                f"Here is the UI screenshot to reproduce as HTML.\n\n"
                f"Colour palette extracted from this image: {palette_str}\n\n"
                f"Use ONLY these colours. Output raw HTML starting with <!DOCTYPE html>."
            ),
        })
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{target_b64}"},
        })
    else:
        # Revision: target + previous HTML + discrepancy list
        critique = state.get("critique") or {}
        discrepancies = critique.get("discrepancies", [])
        prev_html = state.get("current_html", "")
        prev_score = critique.get("score", 0)
        summary = critique.get("summary", "")

        disc_lines = "\n".join(
            f"  [{d.get('severity', 1)}/5] {d.get('region', '')}: {d.get('issue', '')} → FIX: {d.get('fix', '')}"
            for d in discrepancies
        )

        content.append({
            "type": "text",
            "text": (
                f"REVISION — Iteration {iteration}\n\n"
                f"The previous attempt scored {prev_score}/100. Summary: {summary}\n\n"
                f"TARGET IMAGE (what you must match):\n"
            ),
        })
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{target_b64}"},
        })
        content.append({
            "type": "text",
            "text": (
                f"\nColour palette: {palette_str}\n\n"
                f"DISCREPANCIES TO FIX (apply all of these, change nothing else):\n{disc_lines}\n\n"
                f"PREVIOUS HTML (keep everything that already matches, revise only the discrepancies above):\n"
                f"```html\n{prev_html}\n```\n\n"
                f"Output the revised raw HTML starting with <!DOCTYPE html>."
            ),
        })

    messages = [
        SystemMessage(content=GENERATOR_SYSTEM_PROMPT),
        HumanMessage(content=content),
    ]

    print(f"  [generate] Calling {MODEL_NAME} (iteration {iteration})...")
    response = llm.invoke(messages)
    html = _strip_fences(response.content)

    print(f"  [generate] Got {len(html)} chars of HTML")
    return {"current_html": html}
