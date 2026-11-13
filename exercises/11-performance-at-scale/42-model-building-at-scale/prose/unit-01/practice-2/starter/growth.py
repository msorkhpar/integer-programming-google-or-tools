from __future__ import annotations

import math


def fit(sizes: list[int], seconds: list[float]) -> tuple[float, float]:
    """(a, c) with seconds ≈ c * size ** a, fitted by least squares on log(seconds) against log(size)."""
    # TODO: the slope and intercept of the best straight line through (log size, log seconds).
    return 0.0, 0.0


def predict(sizes: list[int], seconds: list[float], n: int) -> float:
    """The time the fitted curve gives for a portfolio of n projects."""
    # TODO
    return 0.0


if __name__ == "__main__":
    sizes, seconds = [1_000, 2_000, 4_000, 8_000], [0.31, 1.05, 4.2, 16.9]
    a, c = fit(sizes, seconds)
    print(f"exponent {a:.2f}; 40,000 projects would take about {predict(sizes, seconds, 40_000):,.0f} s")
