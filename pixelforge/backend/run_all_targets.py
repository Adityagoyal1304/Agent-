"""
run_all_targets.py — Run PixelForge on all target images and collect results.

Usage:
    python run_all_targets.py

Runs all PNGs in the targets/ directory through the full graph pipeline
and writes results to runs/<timestamp>_batch/summary.json.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import time
from pathlib import Path

from run_cli import run


def main():
    targets_dir = Path(__file__).parent.parent / "targets"
    target_files = sorted(targets_dir.glob("*.png"))

    if not target_files:
        print("ERROR: No PNG files found in targets/")
        sys.exit(1)

    print(f"Found {len(target_files)} targets:")
    for t in target_files:
        print(f"  - {t.name}")
    print()

    results = []
    for target in target_files:
        print(f"\n{'#'*60}")
        print(f"# Target: {target.name}")
        print(f"{'#'*60}")
        start = time.time()
        try:
            result = run(str(target))
            result["target_name"] = target.name
            result["status"] = "ok"
        except Exception as e:
            print(f"ERROR running {target.name}: {e}")
            result = {
                "target_name": target.name,
                "status": "error",
                "error": str(e),
                "best_score": 0,
                "total_seconds": time.time() - start,
            }
        results.append(result)

    # Print summary table
    print(f"\n{'='*70}")
    print("  BATCH SUMMARY")
    print(f"{'='*70}")
    print(f"  {'Target':<30} {'Score':>6} {'Iterations':>10} {'Seconds':>8}")
    print(f"  {'-'*65}")
    for r in results:
        name = r.get("target_name", "?")[:28]
        score = r.get("best_score", 0)
        iters = r.get("total_iterations", "?")
        secs = r.get("total_seconds", 0)
        status = r.get("status", "?")
        print(f"  {name:<30} {score:>6} {str(iters):>10} {secs:>7.1f}s  [{status}]")
    print(f"{'='*70}\n")

    # Save batch summary
    runs_dir = Path(__file__).parent.parent / "runs"
    summary_path = runs_dir / "batch_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Batch summary: {summary_path}")


if __name__ == "__main__":
    main()
