"""
Karatsuba multiplication, divide and conquer, about O(n^1.585).
Below THRESHOLD digits it switches to ordinary multiplication.
Optional step recording so the GUI can replay the algorithm on small inputs.
"""
import sys
from functools import lru_cache

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)       # allow million-digit numbers

THRESHOLD = 64                          # digits; at or below this, multiply directly


@lru_cache(maxsize=None)
def pow10(k):
    return 10 ** k


def karatsuba(x, y, n, steps, depth):
    """x and y have at most n digits each. steps is a list or None."""
    if x == 0 or y == 0:
        return 0
    if n <= THRESHOLD:                  # base case: ordinary multiplication
        result = x * y
        if steps is not None:
            steps.append({"type": "base", "depth": depth, "x": x, "y": y,
                          "result": result})
        return result

    m = n // 2                          # split point (low part has m digits)
    p = pow10(m)
    a, b = divmod(x, p)                 # x = a * 10^m + b
    c, d = divmod(y, p)                 # y = c * 10^m + d
    hi = n - m                          # max digits of the high parts
    if steps is not None:
        steps.append({"type": "split", "depth": depth, "x": x, "y": y, "m": m,
                      "a": a, "b": b, "c": c, "d": d})

    ac = karatsuba(a, c, hi, steps, depth + 1)
    bd = karatsuba(b, d, m, steps, depth + 1)
    z = karatsuba(a + b, c + d, hi + 1, steps, depth + 1)   # (a+b)(c+d)
    mid = z - ac - bd                   # equals ad + bc
    result = ac * pow10(2 * m) + mid * p + bd               # shifts by powers of 10

    if steps is not None:
        steps.append({"type": "combine", "depth": depth, "ac": ac, "bd": bd,
                      "z": z, "mid": mid, "result": result})
    return result


def multiply(x, y, record_steps=False):
    """x, y: non-negative ints. Returns (product, steps)."""
    steps = [] if record_steps else None
    n = max(len(str(x)), len(str(y)))
    product = karatsuba(x, y, n, steps, 0)
    return product, (steps or [])