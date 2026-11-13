from __future__ import annotations


def lifecycle_cost(price: float, running: float, life: int, rate: float,
                   one_offs: dict[int, float], resale: float) -> float:
    """Present cost today of buying, running and finally selling one bus."""
    total = price
    for year in range(1, life + 1):
        total += running / (1 + rate) ** year
    for year, cost in one_offs.items():
        total += cost / (1 + rate) ** year
    total -= resale / (1 + rate) ** life
    return total


if __name__ == "__main__":
    print(lifecycle_cost(900, 60, 12, 0.05, {6: 150}, 50))
