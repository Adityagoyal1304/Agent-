"""
graph/builder.py — Assemble the LangGraph with a conditional cycle.

Graph topology:
  START → extract_palette → generate_html → render_html → critique_render
        → keep_best → (conditional) → END or generate_html

The back-edge from keep_best → generate_html is the CYCLE that makes this a
graph, not a chain. A LangChain chain is a DAG (no back-edges). This cycle
cannot be expressed as a chain.

WHY CONDITIONAL EDGE (not fixed loop count)?
If the model hits 85/100 on iteration 2, we stop. Unconditional looping would
waste 3 more API calls to make zero visual improvement.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from config import MAX_ITERATIONS, SCORE_THRESHOLD
from graph.state import GraphState
from graph.nodes.palette import extract_palette
from graph.nodes.generate import generate_html
from graph.nodes.render import render_html
from graph.nodes.critique import critique_render
from graph.nodes.keep_best import keep_best


def _should_continue(state: GraphState) -> str:
    """
    Conditional edge function. Called after keep_best.
    Returns "end" or "generate_html" (the node name to route to).
    """
    best_score = state.get("best_score", 0)
    # iteration was already incremented by keep_best, so it now equals (completed + 1)
    # We compare against MAX_ITERATIONS: if next iteration number > MAX_ITERATIONS, stop
    iteration = state.get("iteration", 1)

    if best_score >= SCORE_THRESHOLD:
        print(f"  [router] Score {best_score} >= {SCORE_THRESHOLD} threshold -- DONE")
        return "end"
    if iteration > MAX_ITERATIONS:
        print(f"  [router] Reached max iterations ({MAX_ITERATIONS}) -- DONE")
        return "end"

    print(f"  [router] Score {best_score} < {SCORE_THRESHOLD}, iteration {iteration}/{MAX_ITERATIONS} -- looping")
    return "generate_html"


def build_graph():
    """
    Build and compile the PixelForge LangGraph.
    Returns a compiled graph with InMemorySaver checkpointing.
    """
    builder = StateGraph(GraphState)

    # Register all nodes
    builder.add_node("extract_palette", extract_palette)
    builder.add_node("generate_html", generate_html)
    builder.add_node("render_html", render_html)
    builder.add_node("critique_render", critique_render)
    builder.add_node("keep_best", keep_best)

    # Linear path
    builder.add_edge(START, "extract_palette")
    builder.add_edge("extract_palette", "generate_html")
    builder.add_edge("generate_html", "render_html")
    builder.add_edge("render_html", "critique_render")
    builder.add_edge("critique_render", "keep_best")

    # Conditional back-edge (the cycle) — routes to END or back to generate_html
    builder.add_conditional_edges(
        "keep_best",
        _should_continue,
        {
            "end": END,
            "generate_html": "generate_html",
        },
    )

    # InMemorySaver enables checkpointing and streaming per thread
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    return graph
