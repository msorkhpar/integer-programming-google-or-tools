"""Lesson 9.2.1: a one-row integer program, its value function, and what a dual of it must be.

GridCap buys pole-replacement work in three standard packages (this lesson's own example; GridCap
is fictional): a 3-crew-week package worth $40k, a 5-week one worth $70k and a 7-week one worth
$100k. Any number of each may be bought, within d crew-weeks. Values are in $10k.
"""

import math

weeks = (3, 5, 7)            # a_j: crew-weeks one package uses
worth = (4, 7, 10)           # c_j: its value, $10k
D = 28


def value_function(D: int) -> list[int]:
    """z(d) = max sum c_j x_j  s.t.  sum a_j x_j <= d,  x_j in {0, 1, 2, ...}, for d = 0..D."""
    z = [0] * (D + 1)
    for d in range(1, D + 1):
        z[d] = max([z[d - 1]] + [z[d - a] + c for a, c in zip(weeks, worth) if a <= d])
    return z


z = value_function(D)
best_ratio = max(c / a for a, c in zip(weeks, worth))          # 10/7: the LP's price per crew-week
print(f"{'d':>2} {'z(d)':>4} {'LP':>6}  price that supports z at d")
for d in range(0, 22):
    up = max((z[e] - z[d]) / (e - d) for e in range(d + 1, D + 1))        # a price must be at least this
    down = min([(z[d] - z[e]) / (d - e) for e in range(d)] or [math.inf])  # ... and at most this
    support = f"any p in [{up:.3f}, {down:.3f}]" if up <= down else "none"
    print(f"{d:>2} {z[d]:>4} {best_ratio * d:>6.2f}  {support}")


def is_dual_function(F) -> list[str]:
    """What a function F on 0..D must satisfy to bound every plan: the subadditive dual's rows."""
    broken = []
    if F(0) != 0:
        broken.append("F(0) = 0")
    if F(1) < 0:
        broken.append("F(1) >= 0 (the slack column)")
    if any(F(d) + F(e) > F(d + e) + 1e-9 for d in range(D + 1) for e in range(D + 1 - d)):
        broken.append("superadditive")
    broken += [f"F({a}) >= {c}" for a, c in zip(weeks, worth) if F(a) < c - 1e-9]
    return broken


candidates = {
    "value function z": lambda d: z[d],
    "LP price 10d/7": lambda d: best_ratio * d,
    "rounded LP floor(10d/7)": lambda d: math.floor(10 * d / 7),
    "price 1.3d": lambda d: 1.3 * d,
}
for name, F in candidates.items():
    broken = is_dual_function(F)
    bounds = ", ".join(f"F({b}) = {F(b):.2f} vs z = {z[b]}" for b in (4, 20))
    print(f"{name:24} {'dual feasible' if not broken else 'breaks ' + '; '.join(broken):28} {bounds}")
