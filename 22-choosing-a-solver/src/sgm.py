"""The shifted geometric mean, in the form Hans Mittelmann's benchmark pages define it (lesson 5.4.2)."""

from __future__ import annotations

import math


def shifted_geometric_mean(values: list[float], shift: float) -> float:
    """exp(mean of ln(max(1, v + shift))) - shift, for nonnegative values and a nonnegative shift."""
    if not values:
        raise ValueError("no values")
    logs = [math.log(max(1.0, v + shift)) for v in values]
    return math.exp(sum(logs) / len(logs)) - shift


def arithmetic_mean(values: list[float]) -> float:
    return sum(values) / len(values)


def geometric_mean(values: list[float]) -> float:
    return math.exp(sum(math.log(v) for v in values) / len(values))


if __name__ == "__main__":
    # Two made-up solvers on the same five instances, in seconds: A is twice as fast on the four easy
    # ones; B is twice as fast on the one hard one.
    a = [0.1, 0.2, 0.4, 0.8, 3600.0]
    b = [0.2, 0.4, 0.8, 1.6, 1800.0]
    print("times (s)         A:", a)
    print("                  B:", b)
    print(f"arithmetic mean   A {arithmetic_mean(a):9.2f}   B {arithmetic_mean(b):9.2f}   B/A {arithmetic_mean(b) / arithmetic_mean(a):.3f}")
    print(f"geometric mean    A {geometric_mean(a):9.2f}   B {geometric_mean(b):9.2f}   B/A {geometric_mean(b) / geometric_mean(a):.3f}")
    for shift in (1, 10, 100):
        sa, sb = shifted_geometric_mean(a, shift), shifted_geometric_mean(b, shift)
        print(f"shifted, sh={shift:<4}  A {sa:9.2f}   B {sb:9.2f}   B/A {sb / sa:.3f}")

    print("\nFour easy instances and four hard ones: C and D tie on the hard ones")
    c = [0.01] * 4 + [100.0] * 4
    d = [0.1] * 4 + [100.0] * 4
    print(f"geometric mean    C {geometric_mean(c):9.2f}   D {geometric_mean(d):9.2f}   D/C {geometric_mean(d) / geometric_mean(c):.3f}")
    for shift in (1, 10):
        sc, sd = shifted_geometric_mean(c, shift), shifted_geometric_mean(d, shift)
        print(f"shifted, sh={shift:<4}  C {sc:9.2f}   D {sd:9.2f}   D/C {sd / sc:.3f}")
