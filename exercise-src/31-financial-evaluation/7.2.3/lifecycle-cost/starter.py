from __future__ import annotations


def lifecycle_cost(price: float, running: float, life: int, rate: float,
                   one_offs: dict[int, float], resale: float) -> float:
    """Present cost today of buying, running and finally selling one bus."""
    # TODO: the price, plus each year's running cost and each one-off, less the resale, all discounted.
    return 0.0


if __name__ == "__main__":
    print(lifecycle_cost(900, 60, 12, 0.05, {6: 150}, 50))
