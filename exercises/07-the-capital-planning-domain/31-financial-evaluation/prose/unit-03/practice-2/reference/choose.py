from __future__ import annotations


def present_cost(price: float, running: float, life: int, rate: float) -> float:
    """The option's price plus its running costs, paid at the end of each year, valued today."""
    return price + sum(running / (1 + rate) ** year for year in range(1, life + 1))


def yearly_cost(price: float, running: float, life: int, rate: float) -> float:
    """The level end-of-year payment over `life` years with the option's present cost."""
    cost = present_cost(price, running, life, rate)
    if rate == 0:
        return cost / life
    return cost * rate / (1 - (1 + rate) ** -life)


def cheapest(options: dict[str, tuple[float, float, int]], rate: float) -> str:
    """The name of the option with the lowest yearly cost."""
    best_name, best_cost = "", float("inf")
    for name, (price, running, life) in options.items():
        cost = yearly_cost(price, running, life, rate)
        if cost < best_cost:
            best_name, best_cost = name, cost
    return best_name


if __name__ == "__main__":
    print(cheapest({"rebuild": (1500, 20, 35), "patch": (200, 130, 8)}, 0.06))
