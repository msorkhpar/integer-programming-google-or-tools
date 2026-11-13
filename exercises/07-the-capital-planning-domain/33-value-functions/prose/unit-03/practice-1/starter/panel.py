from __future__ import annotations

from statistics import median


def panel_weights(ratings: dict[str, list[float]]) -> dict[str, float]:
    """Swing weights from each member's private rating of each measure's swing."""
    # TODO: settle each measure's rating, then turn the ratings into weights.
    return {measure: 0.0 for measure in ratings}


def price(weights: dict[str, float], reference: dict[str, float], measure: str, base: str) -> float:
    """How many units of `base` one unit of `measure` is worth."""
    # TODO
    return 0.0


if __name__ == "__main__":
    votes = {"breaks": [100, 100, 100], "leakage": [60, 80, 100], "savings": [50, 40, 60]}
    w = panel_weights(votes)
    print(w, price(w, {"breaks": 20, "leakage": 500, "savings": 1_000}, "breaks", "savings"))
