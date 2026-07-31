"""
api.py — FastAPI backend for PixelForge web interface.

Endpoints:
  POST /api/runs          — Upload target image, start a run, return run_id
  GET  /api/runs/{id}/stream   — SSE stream of node completions
  GET  /api/runs/{id}/download — Download best.html

SSE (Server-Sent Events) gives us push without WebSockets. The client opens
an EventSource and receives one JSON event per completed graph node.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import uuid
import json
import asyncio
import time
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from graph.builder import build_graph
from utils.images import encode_image_b64, build_filmstrip

app = FastAPI(title="PixelForge API")

# Allow the Vite dev server (port 5173) and any localhost origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active runs: run_id -> {state, graph, config, dir}
# For a production system this would be Redis or a DB, but scope says keep it flat
RUNS: dict[str, dict] = {}

RUNS_DIR = Path(__file__).parent.parent / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/api/runs")
async def create_run(file: UploadFile = File(...)):
    """
    Upload a target image, save it, return a run_id.
    The actual graph run is started lazily when the client opens the SSE stream.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    run_id = str(uuid.uuid4())
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded target
    target_path = run_dir / "target.png"
    content = await file.read()
    target_path.write_bytes(content)

    # Store run metadata
    RUNS[run_id] = {
        "run_dir": run_dir,
        "target_path": target_path,
        "status": "pending",
        "best_html": "",
        "best_score": 0,
    }

    return {"run_id": run_id}


async def _stream_graph(run_id: str) -> AsyncGenerator[dict, None]:
    """
    Run the graph and yield SSE events as each node completes.
    Each event is a JSON dict with node-specific fields.
    """
    if run_id not in RUNS:
        yield {"data": json.dumps({"error": "Run not found", "done": True})}
        return

    run_meta = RUNS[run_id]
    target_path = run_meta["target_path"]
    run_dir = run_meta["run_dir"]

    # Encode target image
    target_b64 = encode_image_b64(str(target_path))

    graph = build_graph()
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
    config = {"configurable": {"thread_id": f"api_{run_id}"}}

    # Real-time streaming via asyncio.Queue so the browser receives each iteration card live
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def _sync_runner():
        try:
            for chunk in graph.stream(initial_state, config=config, stream_mode="updates"):
                loop.call_soon_threadsafe(queue.put_nowait, ("chunk", chunk))
            final = graph.get_state(config)
            loop.call_soon_threadsafe(queue.put_nowait, ("final", final))
        except Exception as e:
            loop.call_soon_threadsafe(queue.put_nowait, ("error", str(e)))

    # Start graph execution in background thread
    loop.run_in_executor(None, _sync_runner)

    # State tracking across live chunks
    current_palette = []
    latest_history = []
    best_html = ""
    best_score = 0
    best_iteration = 0
    render_b64 = ""

    while True:
        kind, payload = await queue.get()
        if kind == "error":
            yield {"data": json.dumps({"error": payload, "done": True})}
            return
        elif kind == "chunk":
            # Inspect node output
            for node_name, node_output in payload.items():
                if node_name == "extract_palette" and "palette" in node_output:
                    current_palette = node_output.get("palette", [])
                elif node_name == "keep_best":
                    history = node_output.get("history", [])
                    if history:
                        entry = history[-1]
                        it_num = entry.get("iteration", 1)
                        score = entry.get("score", 0)
                        discrepancies = entry.get("discrepancies", [])
                        summary = entry.get("summary", "")
                        it_render_b64 = entry.get("render_b64", "")
                        
                        best_score = max(best_score, score)
                        if score == best_score:
                            best_iteration = it_num
                            best_html = node_output.get("best_html", best_html)

                        event_data = {
                            "node": "keep_best",
                            "iteration": it_num,
                            "score": score,
                            "discrepancies": discrepancies,
                            "summary": summary,
                            "html": best_html if it_num == best_iteration else "",
                            "render_b64": it_render_b64,
                            "palette": current_palette if it_num == 1 else [],
                            "done": False,
                            "best_score": best_score,
                            "best_iteration": best_iteration,
                        }
                        yield {"data": json.dumps(event_data)}
        elif kind == "final":
            state_values = payload.values
            best_html = state_values.get("best_html", best_html)
            best_score = state_values.get("best_score", best_score)
            best_iteration = state_values.get("best_iteration", best_iteration)
            history = state_values.get("history", latest_history)
            render_b64 = state_values.get("render_b64", render_b64)
            current_palette = state_values.get("palette", current_palette)

            if best_html:
                (run_dir / "best.html").write_text(best_html, encoding="utf-8")
            break
    final_event = {
        "node": "done",
        "iteration": len(history),
        "score": best_score,
        "best_score": best_score,
        "best_iteration": best_iteration,
        "html": best_html,
        "render_b64": render_b64,
        "palette": current_palette,
        "discrepancies": [],
        "summary": f"Run complete. Best score: {best_score}/100 at iteration {best_iteration}",
        "done": True,
    }
    yield {"data": json.dumps(final_event)}

    # Store final state in RUNS for download endpoint
    RUNS[run_id]["best_html"] = best_html
    RUNS[run_id]["best_score"] = best_score
    RUNS[run_id]["status"] = "done"


@app.get("/api/runs/{run_id}/stream")
async def stream_run(run_id: str):
    """SSE endpoint — streams graph node completions to the client."""
    return EventSourceResponse(_stream_graph(run_id))


@app.get("/api/runs/{run_id}/download")
async def download_best(run_id: str):
    """Download the best HTML file produced by a run."""
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run not found")

    run_dir = RUNS[run_id]["run_dir"]
    best_path = run_dir / "best.html"

    if not best_path.exists():
        raise HTTPException(status_code=404, detail="No best.html yet — run may still be in progress")

    return FileResponse(
        path=str(best_path),
        filename="pixelforge_best.html",
        media_type="text/html",
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
