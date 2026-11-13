from __future__ import annotations

import math


def fit(sizes: list[int], seconds: list[float]) -> tuple[float, float]:
    """(a, c) with seconds ≈ c * size ** a, fitted by least squares on log(seconds) against log(size)."""
    xs = [math.log(n) for n in sizes]
    ys = [math.log(t) for t in seconds]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    c = math.exp(my - a * mx)
    return a, c


def predict(sizes: list[int], seconds: list[float], n: int) -> float:
    """The time the fitted curve gives for a portfolio of n projects."""
    a, c = fit(sizes, seconds)
    return c * n ** a


if __name__ == "__main__":
    sizes, seconds = [1_000, 2_000, 4_000, 8_000], [0.31, 1.05, 4.2, 16.9]
    a, c = fit(sizes, seconds)
    print(f"exponent {a:.2f}; 40,000 projects would take about {predict(sizes, seconds, 40_000):,.0f} s")
