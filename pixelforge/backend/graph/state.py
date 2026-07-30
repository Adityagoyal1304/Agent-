"""
graph/state.py — The shared state object that flows through the LangGraph.

Using TypedDict (not a class) is the LangGraph convention. Every node receives
the full state and returns a PARTIAL dict of only the fields it changed.
LangGraph merges partial updates — nodes don't need to copy unchanged fields.

WHY SHARED STATE?
A plain LangChain chain passes output from one step directly to the next.
That works for linear pipelines. Here we have a back-edge (keep_best → generate),
so generate_html on iteration 3 needs to see: the critique from iteration 2,
the HTML from iteration 2, and the original target from iteration 0.
A flat call stack can't hold all three. Shared state can.
"""

from typing import TypedDict


class GraphState(TypedDict):
    # --- Input ---
    target_b64: str          # Base64 PNG of the user's target screenshot

    # --- Extracted by palette node ---
    palette: list[str]       # 6 hex strings, e.g. ["#1a2b3c", "#ffffff", ...]

    # --- Active iteration ---
    current_html: str        # HTML produced by the most recent generate step
    render_b64: str          # Base64 PNG screenshot of current_html

    # --- Critique from most recent render ---
    critique: dict | None    # Serialised Critique (score, discrepancies, summary)

    # --- Loop counter ---
    iteration: int           # 1-indexed; incremented by keep_best

    # --- Best-so-far tracking ---
    best_html: str           # HTML of the highest-scoring attempt so far
    best_score: int          # Score of best_html
    best_iteration: int      # Which iteration produced best_html

    # --- Run log ---
    history: list[dict]      # One entry per completed iteration, for run.json
