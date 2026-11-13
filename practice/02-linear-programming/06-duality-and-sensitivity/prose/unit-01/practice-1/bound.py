from __future__ import annotations


def price_bound(value: dict[str, float], rows: dict[str, tuple[dict[str, float], float]],
                prices: dict[str, float]) -> float | None:
    """The upper bound that `prices` prove for the LP, or None if they prove nothing."""
    # TODO: check that the prices may be used, then return the bound they prove.
    return 0.0


if __name__ == "__main__":
    value = {"bus": 0.5, "rail": 0.8}
    rows = {"budget": ({"bus": 1, "rail": 1}, 800), "track": ({"rail": 1}, 300)}
    print(price_bound(value, rows, {"budget": 0.5, "track": 0.3}))
    print(price_bound(value, rows, {"budget": 0.5, "track": 0.0}))
