"""A two-variable feasible region: GridCap's 2028 maintenance split between two programs.

d is what distribution maintenance gets and v what vegetation management gets, both in $k. The
round numbers are a teaching example on the fictional GridCap utility, not data of any real one.
"""

import numpy as np

names = ["budget", "crews", "veg_cap", "dist_floor", "veg_nonneg"]
A = np.array([[1, 1],      # d +  v <= 3000   (budget)
              [1, 2],      # d + 2v <= 4000   (crew-days)
              [0, 1],      #       v <= 1500  (vegetation cap)
              [-1, 0],     # -d     <= -500   (distribution floor: d >= 500)
              [0, -1]])    #      -v <= 0     (v >= 0)
b = np.array([3000, 4000, 1500, -500, 0])
c = np.array([2, 3])       # risk points removed per $k


def is_feasible(point: np.ndarray, tol: float = 1e-9) -> bool:
    return bool(np.all(A @ point <= b + tol))


if __name__ == "__main__":
    for point in ([2000, 1000], [2500, 1000], [400, 200]):
        p = np.array(point)
        broken = [n for n, ok in zip(names, A @ p <= b) if not ok]
        print(f"(d, v) = {tuple(point)}: feasible {is_feasible(p)}, breaks {broken}")
    p, q = np.array([500, 0]), np.array([1000, 1500])
    print("segment from", tuple(p.tolist()), "to", tuple(q.tolist()))
    for lam in (0, 0.25, 0.5, 0.75, 1):
        point = (1 - lam) * p + lam * q
        print(f"  lambda {lam:<4}: {tuple(point.tolist())} feasible {is_feasible(point)}")
