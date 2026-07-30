"""
graph/nodes/keep_best.py — Track the best-scoring HTML and advance the iteration.

WHY THIS NODE EXISTS:
In a self-correcting loop, scores can oscillate. Attempt 4 might score 72 after
attempt 3 scored 78 (the model "over-corrected"). Without this guard, the user
would receive the last HTML, not the best one.

This node has no LLM call. It does three things:
1. Update best_html/best_score/best_iteration if this iteration beat the record.
2. Append a log entry to history for run.json.
3. Increment the iteration counter so generate_html knows to do a revision.

The conditional edge in builder.py reads best_score and iteration from state
after this node runs to decide whether to loop or stop.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import time
from graph.state import GraphState


def keep_best(state: GraphState) -> dict:
    """
    Update best tracking, log this iteration, increment counter.
    Returns partial state update.
    """
    critique = state.get("critique") or {}
    score = critique.get("score", 0)
    iteration = state.get("iteration", 1)
    current_html = state.get("current_html", "")

    best_score = state.get("best_score", 0)
    best_html = state.get("best_html", "")
    best_iteration = state.get("best_iteration", 0)

    # Update best if this attempt is strictly better
    new_best_score = best_score
    new_best_html = best_html
    new_best_iteration = best_iteration

    if score > best_score:
        new_best_score = score
        new_best_html = current_html
        new_best_iteration = iteration
        print(f"  [keep_best] New best: {score}/100 (was {best_score}/100) at iteration {iteration}")
    else:
        print(f"  [keep_best] No improvement: {score}/100 <= {best_score}/100, keeping iteration {best_iteration}")

    # Append history entry for run.json
    history = list(state.get("history", []))
    # We store render_b64 in history so the API can emit it per iteration via SSE.
    # The run_cli.py strips it before writing run.json (to keep the file readable).
    history.append({
        "iteration": iteration,
        "score": score,
        "summary": critique.get("summary", ""),
        "discrepancies": critique.get("discrepancies", []),
        "render_b64": state.get("render_b64", ""),
        "timestamp": time.time(),
    })

    new_iteration = iteration + 1

    return {
        "best_score": new_best_score,
        "best_html": new_best_html,
        "best_iteration": new_best_iteration,
        "history": history,
        "iteration": new_iteration,
    }
