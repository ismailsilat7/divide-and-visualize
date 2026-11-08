# Divide & Visualize

A CS2009 Design and Analysis of Algorithms project demonstrating the 2D closest-pair divide-and-conquer algorithm and Karatsuba integer multiplication. It includes seeded dataset generation, a benchmark runner, and a local interactive visualizer.

## Run the visualizer

Python 3.10+ is recommended. From the repository root:

```sh
python3 -m pip install -r requirements.txt
python3 gui/app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Select any available input in the sidebar. Small inputs show recorded algorithm frames with Replay, Prev, Next, Reset, progress scrubbing, and speed controls. The Karatsuba threshold slider reruns the selected input. Large inputs show the exact closest-pair result or the product digit count and leading/trailing digits, together with elapsed time. Large integer products are computed exactly; the UI abbreviates their display to keep the page responsive.

The Flask server reads datasets from `data/` and `data/large/`. Files above 1 MB are kept under `data/large/` and excluded from version control. Regenerate the full dataset locally before running all benchmarks if needed:

```sh
python3 generator/generate.py
python3 runner/run_all.py
```

## Algorithms

- `algorithms/closest_pair.py` sorts points once by x and y, recursively solves both halves, merges y-order, and checks the middle strip. It keeps squared distances internally and supports optional frame recording.
- `algorithms/karatsuba.py` recursively splits decimal operands and combines three subproducts. The ordinary multiplication base-case threshold is configurable (default: 64 digits).
- `generator/generate.py` creates the 20 prescribed datasets with per-file fixed seeds recorded in `data/seeds.txt`.
- `runner/run_all.py` applies both algorithms to all datasets, checks results, and writes `runner/results.csv`.

## Language and dataset note

The implementation is in Python. Large inputs are processed at runtime; the million-digit multiplication datasets are not capped. Large generated files are intentionally omitted from source control and are regenerated from the committed generator and seeds. The GUI uses plain JavaScript and SVG with no frontend framework.
