"""
run_cli.py — Command-line interface for PixelForge.

Usage:
    python run_cli.py targets/pricing_card.png

Streams each node's completion in real time via graph.stream(stream_mode="updates").
Writes all artifacts to runs/<timestamp>/:
  - target.png
  - iteration_N.html
  - iteration_N.png
  - best.html
  - filmstrip.png
  - run.json
Prints a final summary table.
"""

import sys
import os

# Ensure backend/ is on the path so all modules resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import base64
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

from graph.builder import build_graph
from utils.images import encode_image_b64, decode_b64_to_image, b64_to_bytes, build_filmstrip
from config import MAX_ITERATIONS, SCORE_THRESHOLD


def run(target_path: str):
    target_path = Path(target_path)
    if not target_path.exists():
        print(f"ERROR: Target file not found: {target_path}")
        sys.exit(1)

    # --- Set up output directory ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_stem = target_path.stem
    run_dir = Path(__file__).parent.parent / "runs" / f"{timestamp}_{target_stem}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Copy target into run dir
    shutil.copy(target_path, run_dir / "target.png")
    print(f"\n{'='*60}")
    print(f"  PixelForge -- {target_path.name}")
    print(f"  Output: {run_dir}")
    print(f"  Max iterations: {MAX_ITERATIONS}, threshold: {SCORE_THRESHOLD}")
    print(f"{'='*60}\n")

    # --- Build graph and initial state ---
    graph = build_graph()
    target_b64 = encode_image_b64(str(target_path))

    initial_state = {
        "target_b64": target_b64,
        "palette": [],
        "current_html": "",
        "render_b64": "",
        "critique": None,
        "iteration": 1,
        "best_html": "",
        "best_score": 0,
        "best_iteration": 0,
        "history": [],
    }

    config = {"configurable": {"thread_id": f"run_{timestamp}"}}

    # --- Stream the graph, capturing state at each node ---
    start_time = time.time()
    node_times = {}
    iter_renders = {}   # iteration_number -> render_b64 (captured from render_html node)
    iter_htmls = {}     # iteration_number -> html (captured from generate_html node)
    current_iteration = 1

    print("Streaming graph execution...\n")
    node_start = time.time()

    for chunk in graph.stream(initial_state, config=config, stream_mode="updates"):
        node_name = list(chunk.keys())[0]
        node_data = chunk[node_name]
        elapsed = time.time() - node_start

        print(f"  [done] [{node_name}] completed in {elapsed:.1f}s")
        node_times[node_name] = node_times.get(node_name, []) + [elapsed]

        # Capture HTML as it's generated (before we know the iteration score)
        if node_name == "generate_html" and "current_html" in node_data:
            iter_htmls[current_iteration] = node_data["current_html"]

        # Capture render screenshot as it arrives
        if node_name == "render_html" and "render_b64" in node_data:
            iter_renders[current_iteration] = node_data["render_b64"]

        # After keep_best we know the score for this iteration
        if node_name == "keep_best":
            history = node_data.get("history", [])
            if history:
                last = history[-1]
                it_num = last.get("iteration", 1)
                score = last.get("score", 0)
                print(f"  -> Iteration {it_num} scored {score}/100")

                # Save iteration HTML
                it_html = iter_htmls.get(it_num, "")
                if it_html:
                    (run_dir / f"iteration_{it_num}.html").write_text(it_html, encoding="utf-8")

                # Save iteration render PNG
                it_render = iter_renders.get(it_num, "")
                if it_render:
                    (run_dir / f"iteration_{it_num}.png").write_bytes(b64_to_bytes(it_render))

            # Increment local counter (keep_best already incremented state.iteration)
            current_iteration += 1

        node_start = time.time()

    # --- Get final state ---
    final = graph.get_state(config)
    state_values = final.values

    # --- Save best.html ---
    best_html = state_values.get("best_html", "")
    best_score = state_values.get("best_score", 0)
    best_iteration = state_values.get("best_iteration", 0)
    history = state_values.get("history", [])

    if best_html:
        (run_dir / "best.html").write_text(best_html, encoding="utf-8")

    # --- Build filmstrip ---
    filmstrip_iters = []
    for entry in history:
        it_num = entry.get("iteration", 1)
        score = entry.get("score", 0)
        render_b64 = iter_renders.get(it_num, "")
        filmstrip_iters.append({
            "iteration": it_num,
            "score": score,
            "render_b64": render_b64,
        })

    if filmstrip_iters:
        filmstrip = build_filmstrip(target_b64, filmstrip_iters)
        filmstrip.save(str(run_dir / "filmstrip.png"))
        print(f"\n  Filmstrip saved: {run_dir / 'filmstrip.png'}")

    # --- Save run.json ---
    total_time = time.time() - start_time
    # Strip render_b64 from history to keep run.json readable
    history_clean = [
        {k: v for k, v in e.items() if k != "render_b64"}
        for e in history
    ]
    run_data = {
        "target": str(target_path),
        "best_score": best_score,
        "best_iteration": best_iteration,
        "total_iterations": len(history),
        "total_seconds": round(total_time, 2),
        "history": history_clean,
        "node_times": node_times,
    }
    (run_dir / "run.json").write_text(json.dumps(run_data, indent=2), encoding="utf-8")

    # --- Print summary table ---
    print(f"\n{'='*60}")
    print(f"  Run complete in {total_time:.1f}s")
    print(f"  Best: iteration {best_iteration}, score {best_score}/100")
    print(f"  Output: {run_dir}")
    print(f"\n  {'Iteration':<12} {'Score':>6}   Summary")
    print(f"  {'-'*55}")
    for entry in history:
        it = entry.get("iteration", "?")
        sc = entry.get("score", 0)
        sm = entry.get("summary", "")[:40]
        best_marker = " <- BEST" if it == best_iteration else ""
        print(f"  {str(it):<12} {sc:>6}   {sm}{best_marker}")
    print(f"{'='*60}\n")

    return run_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PixelForge CLI -- screenshot to HTML")
    parser.add_argument("target", help="Path to target screenshot PNG")
    args = parser.parse_args()
    run(args.target)
