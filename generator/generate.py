"""
Generates the 20 input files: cp01-cp10 (closest pair) and im01-im10 (multiplication).
Each file has its own fixed seed, so the same data can be regenerated.
Files over 1 MB go to data/large/ (not submitted). Seeds are saved in data/seeds.txt.
"""
import os
import random
import shutil

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LARGE_DIR = os.path.join(DATA_DIR, "large")
SEED_BASE = 2026000
ONE_MB = 1_000_000
MILLION = 10**6

os.makedirs(LARGE_DIR, exist_ok=True)
seeds_used = {}


# ---------- helpers ----------

# create a random generator with a fixed seed and record the seed
def make_rng(name, number):
    seed = SEED_BASE + number
    seeds_used[name] = seed
    return random.Random(seed)


# save text to data/<name>.txt, moving it to data/large/ if over 1 MB
def write_file(name, text):
    path = os.path.join(DATA_DIR, name + ".txt")
    with open(path, "w") as f:
        f.write(text)
    if os.path.getsize(path) > ONE_MB:
        shutil.move(path, os.path.join(LARGE_DIR, name + ".txt"))


# closest pair format: first line n, then one 'x y' per line
def write_points(name, points):
    lines = [str(len(points))] + [f"{x} {y}" for x, y in points]
    write_file(name, "\n".join(lines) + "\n")


# multiplication format: two lines, one number each
def write_numbers(name, a, b):
    write_file(name, a + "\n" + b + "\n")


# ---------- point generators (each returns a list of (x, y)) ----------

# n points with random real coordinates in [0, 10^6]
def uniform_points(rng, n):
    return [(round(rng.uniform(0, 1e6), 6), round(rng.uniform(0, 1e6), 6))
            for _ in range(n)]


# n points scattered around a few random centers (normal distribution)
def clustered_points(rng, n, num_centers=10, spread=5000):
    centers = [(rng.uniform(1e5, 9e5), rng.uniform(1e5, 9e5)) for _ in range(num_centers)]
    points = []
    for _ in range(n):
        cx, cy = rng.choice(centers)
        points.append((round(rng.gauss(cx, spread), 6), round(rng.gauss(cy, spread), 6)))
    return points


# integer coordinates in a small range, so many points repeat (distance 0)
def duplicate_heavy_points(rng, n, max_coord=300):
    return [(rng.randint(0, max_coord), rng.randint(0, max_coord)) for _ in range(n)]


# all points share the same x, only y varies
def vertical_line_points(rng, n, x=500000):
    return [(x, round(rng.uniform(0, 1e6), 6)) for _ in range(n)]


# equally spaced grid: many pairs tie for closest (distance 1)
def grid_points(rows=250, cols=400):
    return [(x, y) for x in range(rows) for y in range(cols)]


# random points plus a very close pair on opposite sides of x = 500000
def middle_line_pair_points(rng, n):
    points = uniform_points(rng, n - 2)
    points.append((499999.99995, 123456.0))   # left of the middle line
    points.append((500000.00005, 123456.0))   # right of it, distance 0.0001
    rng.shuffle(points)
    return points


# ---------- number generators (each returns a string of digits) ----------

# random digits with no leading zero
def random_number(rng, digits):
    if digits == 1:
        return str(rng.randint(0, 9))
    return str(rng.randint(1, 9)) + "".join(rng.choices("0123456789", k=digits - 1))


def all_nines(digits):
    return "9" * digits


# mostly zeros with a few random nonzero digits
def sparse_number(rng, digits, zero_chance=0.9):
    rest = ("0" if rng.random() < zero_chance else str(rng.randint(1, 9))
            for _ in range(digits - 1))
    return str(rng.randint(1, 9)) + "".join(rest)


# '1' followed by (digits - 1) zeros
def power_of_ten(digits):
    return "1" + "0" * (digits - 1)


# ---------- file list ----------

# closest pair files cp01-cp04: uniform, sizes 10^3 to 10^6
def main():
    for i, n in enumerate([10**3, 10**4, 10**5, 10**6], start=1):
        name = f"cp{i:02d}"
        write_points(name, uniform_points(make_rng(name, i), n))

    write_points("cp05", clustered_points(make_rng("cp05", 5), MILLION))
    write_points("cp06", duplicate_heavy_points(make_rng("cp06", 6), MILLION))
    write_points("cp07", vertical_line_points(make_rng("cp07", 7), 100_000))
    make_rng("cp08", 8)  # grid is fixed, seed recorded only for completeness
    write_points("cp08", grid_points())
    write_points("cp09", middle_line_pair_points(make_rng("cp09", 9), MILLION))
    write_points("cp10", uniform_points(make_rng("cp10", 10), 101))

    # Multiplication files im01-im04: random numbers, both with d digits
    for i, d in enumerate([10**3, 10**4, 10**5, 10**6], start=1):
        name = f"im{i:02d}"
        rng = make_rng(name, 100 + i)
        write_numbers(name, random_number(rng, d), random_number(rng, d))

    rng = make_rng("im05", 105)   # very different lengths
    write_numbers("im05", random_number(rng, MILLION), random_number(rng, 10))

    rng = make_rng("im06", 106)   # one number is all 9s
    write_numbers("im06", all_nines(100_000), random_number(rng, 100_000))

    rng = make_rng("im07", 107)   # odd length, many zeros
    write_numbers("im07", sparse_number(rng, 99_999), sparse_number(rng, 99_999))

    make_rng("im08", 108)         # powers of 10, no randomness
    write_numbers("im08", power_of_ten(MILLION), power_of_ten(MILLION))

    rng = make_rng("im09", 109)   # one number is 0
    write_numbers("im09", "0", random_number(rng, MILLION))

    rng = make_rng("im10", 110)   # small demo file
    write_numbers("im10", random_number(rng, 101), random_number(rng, 101))

    with open(os.path.join(DATA_DIR, "seeds.txt"), "w") as f:
        for name, seed in sorted(seeds_used.items()):
            f.write(f"{name}: {seed}\n")
    print("done")


if __name__ == "__main__":
    main()