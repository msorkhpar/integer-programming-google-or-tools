from __future__ import annotations


def price_bound(value: dict[str, float], rows: dict[str, tuple[dict[str, float], float]],
                prices: dict[str, float]) -> float | None:
    """The upper bound that `prices` prove for the LP, or None if they prove nothing."""
    if any(price < 0 for price in prices.values()):
        return None
    for activity, worth in value.items():
        covered = sum(coeffs.get(activity, 0) * prices[name] for name, (coeffs, _) in rows.items())
        if covered < worth - 1e-9:
            return None
    return sum(rhs * prices[name] for name, (_, rhs) in rows.items())


if __name__ == "__main__":
    value = {"bus": 0.5, "rail": 0.8}
    rows = {"budget": ({"bus": 1, "rail": 1}, 800), "track": ({"rail": 1}, 300)}
    print(price_bound(value, rows, {"budget": 0.5, "track": 0.3}))
    print(price_bound(value, rows, {"budget": 0.5, "track": 0.0}))
