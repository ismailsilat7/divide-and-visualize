import sys, time
from algorithms.closest_pair import closest_pair

def load_points(path):
    with open(path) as f:
        n = int(f.readline())
        return [tuple(map(float, line.split())) for line in f][:n]

for path in sys.argv[1:]:
    pts = load_points(path)
    t = time.perf_counter()
    d, p, q, _ = closest_pair(pts)
    print(f"{path}: n={len(pts)} dist={d} pair={p},{q} time={time.perf_counter() - t:.2f}s")