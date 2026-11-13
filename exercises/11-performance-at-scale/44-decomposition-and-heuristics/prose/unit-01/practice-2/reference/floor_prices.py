from __future__ import annotations


def next_prices(prices: dict[int, float], floors: dict[int, float], veg_spend: dict[int, float],
                bound: float, best_value: float, theta: float) -> dict[int, float]:
    """One projected subgradient step on the floor prices, with Polyak's step length."""
    g = {y: veg_spend[y] - floors[y] for y in floors}          # L(mu) adds mu * (veg - F)
    norm = sum(v * v for v in g.values())
    if norm == 0:
        return dict(prices)
    step = theta * (bound - best_value) / norm
    return {y: max(0.0, prices[y] - step * g[y]) for y in floors}


if __name__ == "__main__":
    print(next_prices({2027: 0.5, 2028: 0.5}, {2027: 100, 2028: 100}, {2027: 80, 2028: 130}, 1200, 1000, 1.0))
