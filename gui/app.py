"""Local Flask API for the divide-and-visualize project."""
from __future__ import annotations

import math
import sys
import time
from itertools import combinations
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))
from algorithms.closest_pair import closest_pair  # noqa: E402
from algorithms.karatsuba import multiply  # noqa: E402

app = Flask(__name__, static_folder="static")


def dataset_path(name: str) -> Path | None:
    if not name or not (name.startswith("cp") or name.startswith("im")):
        return None
    if len(name) != 4 or not name[2:].isdigit():
        return None
    candidate = DATA / f"{name}.txt"
    if not candidate.exists():
        candidate = DATA / "large" / f"{name}.txt"
    return candidate if candidate.is_file() else None


def inspect_file(name: str, path: Path) -> dict:
    size = path.stat().st_size
    if name.startswith("cp"):
        with path.open() as f:
            count = int(f.readline())
        return {"id": name, "kind": "closest", "size": count,
                "size_label": f"{count:,} points", "animatable": count <= 1000,
                "bytes": size}
    with path.open() as f:
        digits = [len(line.strip()) for line in f if line.strip()]
    max_digits = max(digits, default=0)
    return {"id": name, "kind": "multiply", "size": max_digits,
            "size_label": f"{max_digits:,} digits", "animatable": max_digits <= 200,
            "bytes": size}


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/files")
def files():
    found = []
    for folder in (DATA, DATA / "large"):
        if folder.exists():
            for p in folder.glob("*.txt"):
                if p.stem.startswith(("cp", "im")) and len(p.stem) == 4:
                    found.append(inspect_file(p.stem, p))
    found.sort(key=lambda item: (item["kind"] != "closest", item["id"]))
    return jsonify({"files": found})


@app.get("/api/run")
def run_file():
    name = request.args.get("file", "")
    path = dataset_path(name)
    if path is None:
        return jsonify({"error": "Input file not found."}), 404
    try:
        # 64 is the real setting used for benchmarks; the page sends a smaller
        # value (32) only for the animated demos.
        threshold = max(4, min(128, int(request.args.get("threshold", "64"))))
    except ValueError:
        return jsonify({"error": "Threshold must be an integer."}), 400

    info = inspect_file(name, path)
    animated = info["animatable"]
    start = time.perf_counter()
    if info["kind"] == "closest":
        with path.open() as f:
            f.readline()  # count is already available in the file list metadata
            points = [tuple(map(float, line.split())) for line in f if line.strip()]
        distance, p, q, steps = closest_pair(points, record_steps=animated)
        elapsed = time.perf_counter() - start
        if animated:
            checked = min((math.dist(a, b) for a, b in combinations(points, 2)),
                          default=float("inf"))
            correct = math.isclose(distance, checked, rel_tol=1e-12, abs_tol=1e-12)
            verification = "Cross-check passed" if correct else "Cross-check failed"
        else:
            verification = "Completed (independent check skipped for this input size)"
        return jsonify({"file": name, "kind": "closest", "animated": animated,
                        "elapsed": elapsed, "result": {"distance": distance, "pair": [p, q]},
                        "verification": verification, "points": points if animated else [],
                        "overview_points": (points[::max(1, len(points) // 600)] + [p, q]) if not animated else [],
                        "steps": steps if animated else []})

    with path.open() as f:
        x_text = f.readline().strip()
        y_text = f.readline().strip()
    x, y = int(x_text), int(y_text)
    product, steps = multiply(x, y, record_steps=animated, threshold=threshold)
    elapsed = time.perf_counter() - start        # timer stops before the check below
    exact = str(product)
    result = {"digits": len(exact), "input_digits": max(len(x_text), len(y_text)),
              "prefix": exact if animated else exact[:32],
              "suffix": exact if animated else exact[-32:]}
    if animated:
        result["product"] = exact
    # Built-in multiply is used only to verify, and is not included in the timing.
    verification = ("Cross-check passed (built-in multiply)" if product == x * y
                    else "Cross-check failed")
    return jsonify({"file": name, "kind": "multiply", "animated": animated,
                    "elapsed": elapsed, "result": result, "verification": verification,
                    "steps": steps if animated else [], "threshold": threshold})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)