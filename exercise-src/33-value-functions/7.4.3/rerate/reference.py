from __future__ import annotations


def weights(ratings: dict[str, float]) -> dict[str, float]:
    total = sum(ratings.values())
    return {m: r / total for m, r in ratings.items()}


def price(ratings: dict[str, float], reference: dict[str, float], measure: str, base: str) -> float:
    """Units of `base` that one unit of `measure` is worth under these ratings and references."""
    w = weights(ratings)
    return (w[measure] / reference[measure]) / (w[base] / reference[base])


def rerate(ratings: dict[str, float], old_reference: dict[str, float],
           new_reference: dict[str, float]) -> dict[str, float]:
    """Ratings for the new references that keep every price, with the biggest swing at 100."""
    scaled = {m: r * new_reference[m] / old_reference[m] for m, r in ratings.items()}
    top = max(scaled.values())
    return {m: 100 * s / top for m, s in scaled.items()}


if __name__ == "__main__":
    old = {"riders": 2_000, "accidents": 2, "savings": 500}
    print(rerate({"riders": 100, "accidents": 50, "savings": 20}, old, {**old, "accidents": 4}))
