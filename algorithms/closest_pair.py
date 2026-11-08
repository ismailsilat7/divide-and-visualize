# Closest pair of points in 2D, divide and conquer, O(n log n).

import math
from bisect import bisect_left

def closest_pair(points, record_steps=False):
    """
    points: list of (x, y) tuples.
    Returns (distance, point_a, point_b, steps).
    steps is a list of event dicts when record_steps is True, otherwise empty.
    """
    steps = []
    n = len(points)
    if n < 2:
        return float("inf"), None, None, steps

    by_x = sorted(points)                       # sorted by x (then y), once
    by_y = sorted(points, key=lambda p: p[1])   # sorted by y, once

    def dist_sq(p, q):
        return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

    def brute(pts):
        """Brute force for 2 or 3 points. Returns (squared distance, p, q)."""
        best = (float("inf"), None, None)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = dist_sq(pts[i], pts[j])
                if d < best[0]:
                    best = (d, pts[i], pts[j])
        return best

    def solve(lo, hi, ys):
        """
        Solve for by_x[lo:hi]. ys is the same points sorted by y.
        Returns (best squared distance, p, q, ys sorted by y).
        """
        if hi - lo <= 3:                                  # base case
            d, p, q = brute(by_x[lo:hi])
            if record_steps:
                steps.append({"type": "base", "lo": lo, "hi": hi,
                              "dist": math.sqrt(d), "pair": (p, q)})
            return d, p, q, ys

        mid = (lo + hi) // 2
        pivot = by_x[mid]
        mid_x = pivot[0]
        if record_steps:
            steps.append({"type": "divide", "lo": lo, "hi": hi, "mid_x": mid_x})

        # Split ys into left and right halves, keeping y order.
        # Points smaller than the pivot go left. Copies of the pivot fill
        # whatever quota the left half still needs (copies are identical).
        pivot_copies_left = mid - bisect_left(by_x, pivot, lo, hi)
        ys_left, ys_right = [], []
        for p in ys:
            if p < pivot:
                ys_left.append(p)
            elif p == pivot and pivot_copies_left > 0:
                ys_left.append(p)
                pivot_copies_left -= 1
            else:
                ys_right.append(p)

        # Conquer
        dl, pl, ql, ys_left = solve(lo, mid, ys_left)
        dr, pr, qr, ys_right = solve(mid, hi, ys_right)
        if dl <= dr:
            best, bp, bq = dl, pl, ql
        else:
            best, bp, bq = dr, pr, qr

        # Merge the two y-sorted halves (like merge sort)
        merged = []
        i = j = 0
        while i < len(ys_left) and j < len(ys_right):
            if ys_left[i][1] <= ys_right[j][1]:
                merged.append(ys_left[i])
                i += 1
            else:
                merged.append(ys_right[j])
                j += 1
        merged.extend(ys_left[i:])
        merged.extend(ys_right[j:])

        # Combine: strip of points within d of the middle line, in y order
        d = math.sqrt(best)
        strip = [p for p in merged if abs(p[0] - mid_x) < d]
        for a in range(len(strip)):
            b = a + 1
            while b < len(strip) and (strip[b][1] - strip[a][1]) ** 2 < best:
                dd = dist_sq(strip[a], strip[b])
                if record_steps:
                    steps.append({"type": "check", "lo": lo, "hi": hi,
                                  "mid_x": mid_x, "pair": (strip[a], strip[b]),
                                  "dist": math.sqrt(dd)})
                if dd < best:
                    best, bp, bq = dd, strip[a], strip[b]
                b += 1

        if record_steps:
            steps.append({"type": "combine", "lo": lo, "hi": hi, "mid_x": mid_x,
                          "strip": list(strip), "dist": math.sqrt(best),
                          "pair": (bp, bq)})
        return best, bp, bq, merged

    best, p, q, _ = solve(0, n, by_y)
    return math.sqrt(best), p, q, steps
