import random
from algorithms.karatsuba import multiply

rng = random.Random(1)
def rnd(d):
    return int("".join(rng.choice("0123456789") for _ in range(d))) if d else 0

cases = [(0, 5), (7, 0), (10**200, 10**300), (10**150 - 1, rnd(150)), (rnd(500), rnd(3))]
cases += [(rnd(rng.randint(1, 400)), rnd(rng.randint(1, 400))) for _ in range(500)]
for x, y in cases:
    assert multiply(x, y)[0] == x * y, (x, y)
print("all ok")