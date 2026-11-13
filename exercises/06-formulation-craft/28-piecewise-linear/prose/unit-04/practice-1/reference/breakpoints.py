from __future__ import annotations

from typing import Callable


def fewest_breakpoints(f: Callable[[float], float], lo: float, hi: float, tol: float,
                       max_n: int = 65) -> int | None:
    """The fewest equally spaced breakpoints whose curve stays within `tol` of f on [lo, hi]."""
    checks = [lo + (hi - lo) * i / 1000 for i in range(1001)]
    for n in range(2, max_n + 1):
        knots = [lo + (hi - lo) * k / (n - 1) for k in range(n)]
        values = [f(t) for t in knots]

        def curve(x: float) -> float:
            k = min(int((x - lo) / (hi - lo) * (n - 1)), n - 2)
            share = (x - knots[k]) / (knots[k + 1] - knots[k])
            return values[k] + share * (values[k + 1] - values[k])

        if max(abs(f(x) - curve(x)) for x in checks) <= tol:
            return n
    return None


if __name__ == "__main__":
    print(fewest_breakpoints(lambda x: x * x, 0.0, 1.0, 0.011))
