# Runs closest pair on cp01-cp10 and Karatsuba on im01-im10.
# Checks each result, prints a table and saves it to runner/results.csv.

import csv
import math
import os
import sys
import time

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
from algorithms.closest_pair import closest_pair
from algorithms.karatsuba import multiply

DATA = os.path.join(ROOT, "data")
BRUTE_LIMIT = 5000                                      # brute force check only up to this n
KNOWN_DIST = {"cp06": 0.0, "cp08": 1.0, "cp09": 1e-4}   # answers known from how files are built


def find(name):
    for folder in (DATA, os.path.join(DATA, "large")):
        path = os.path.join(folder, name + ".txt")
        if os.path.exists(path):
            return path
    raise FileNotFoundError(name)


def load_points(path):
    with open(path) as f:
        n = int(f.readline())
        return [tuple(map(float, line.split())) for line in f][:n]


def brute_force(points):
    return min(math.dist(points[i], points[j])
               for i in range(len(points)) for j in range(i + 1, len(points)))


# True if no two points are closer than d. Independent grid check, about O(n)
def no_closer_pair(points, d):
    grid = {}
    for p in points:
        grid.setdefault((int(p[0] // d), int(p[1] // d)), []).append(p)
    for (cx, cy), cell in grid.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for q in grid.get((cx + dx, cy + dy), ()):
                    for p in cell:
                        if p is not q and math.dist(p, q) < d - 1e-9:
                            return False
    return True

def run_closest_pair(name):
    points = load_points(find(name))
    start = time.perf_counter()
    d, p, q, _ = closest_pair(points)
    elapsed = time.perf_counter() - start

    if len(points) <= BRUTE_LIMIT:
        ok, how = abs(d - brute_force(points)) < 1e-8, "brute force"
    elif name in KNOWN_DIST:
        ok, how = abs(d - KNOWN_DIST[name]) < 1e-8, "known answer"
    else:
        ok, how = d > 0 and no_closer_pair(points, d), "grid check"
    return [name, "closest pair", len(points), f"d={d:.6f} pair={p},{q}",
            f"{elapsed:.2f}", ok, how]


def run_karatsuba(name):
    with open(find(name)) as f:
        x, y = int(f.readline()), int(f.readline())
    start = time.perf_counter()
    product, _ = multiply(x, y)
    elapsed = time.perf_counter() - start

    ok = product == x * y                            # built-in used for checking only
    digits = str(product)
    summary = f"{len(digits)} digits, starts {digits[:10]}, ends {digits[-10:]}"
    size = f"{len(str(x))} x {len(str(y))} digits"
    return [name, "karatsuba", size, summary, f"{elapsed:.2f}", ok, "verified vs built-in"]


def main():
    rows = [run_closest_pair(f"cp{i:02d}") for i in range(1, 11)]
    rows += [run_karatsuba(f"im{i:02d}") for i in range(1, 11)]

    header = ["file", "algorithm", "size", "result", "time_s", "correct", "checked_with"]
    with open(os.path.join(os.path.dirname(__file__), "results.csv"), "w", newline="") as f:
        csv.writer(f).writerows([header] + rows)

    for r in rows:
        print(f"{r[0]}  {r[2]!s:<22} {r[4]:>7}s  correct={r[5]}  ({r[6]})")


if __name__ == "__main__":
    main()