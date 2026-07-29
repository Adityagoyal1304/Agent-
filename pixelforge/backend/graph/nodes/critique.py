"""
graph/nodes/critique.py — Vision model compares target vs rendered attempt.

Key design choices:
- with_structured_output(Critique): forces the model to return a typed Pydantic
  object. No regex, no JSON parsing, no free-text ambiguity.
- Both images sent in the same message, clearly labelled TARGET and ATTEMPT.
- TARGET always sent first so the model anchors on it as the ground truth.
- The Critique object is converted to dict before storing in state (TypedDict
  cannot hold Pydantic objects across serialisation boundaries).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from prompts import CRITIC_SYSTEM_PROMPT
from schemas import Critique
from graph.state import GraphState


def critique_render(state: GraphState) -> dict:
    """
    Compare target vs render using structured vision output.
    Returns partial state with 'critique' updated.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(Critique)

    target_b64 = state["target_b64"]
    render_b64 = state.get("render_b64", "")
    iteration = state.get("iteration", 1)

    # Build multimodal message: TARGET first, ATTEMPT second.
    # The label text makes it unambiguous which is which.
    content = [
        {
            "type": "text",
            "text": "IMAGE 1 — TARGET (the design to reproduce):",
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{target_b64}"},
        },
        {
            "type": "text",
            "text": f"IMAGE 2 — ATTEMPT {iteration} (the current HTML render):",
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{render_b64}"},
        },
        {
            "type": "text",
            "text": (
                "Score the ATTEMPT against the TARGET on visual fidelity (0-100). "
                "List at most 6 discrepancies, most severe first. "
                "Every fix must be a concrete Tailwind/CSS instruction."
            ),
        },
    ]

    messages = [
        SystemMessage(content=CRITIC_SYSTEM_PROMPT),
        HumanMessage(content=content),
    ]

    print(f"  [critique] Calling vision model for iteration {iteration}...")
    critique_obj: Critique = structured_llm.invoke(messages)

    if critique_obj is None:
        print("  [critique] Warning: vision model returned None, using safe fallback Critique.")
        critique_obj = Critique(
            score=50,
            summary="Refining layout and colors towards target.",
            discrepancies=[]
        )

    # Serialise to dict for storage in TypedDict state
    critique_dict = critique_obj.model_dump()
    print(f"  [critique] Score: {critique_dict['score']}/100 -- {critique_dict['summary']}")

    return {"critique": critique_dict}
