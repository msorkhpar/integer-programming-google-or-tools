from __future__ import annotations


def next_prices(prices: dict[int, float], floors: dict[int, float], veg_spend: dict[int, float],
                bound: float, best_value: float, theta: float) -> dict[int, float]:
    """One projected subgradient step on the floor prices, with Polyak's step length."""
    # TODO: write L(mu), its subgradient and the projected step first, then code them.
    return {y: -1.0 for y in prices}


if __name__ == "__main__":
    print(next_prices({2027: 0.5, 2028: 0.5}, {2027: 100, 2028: 100}, {2027: 80, 2028: 130}, 1200, 1000, 1.0))
