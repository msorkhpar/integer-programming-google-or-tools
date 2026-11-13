from __future__ import annotations


def worth_buying(offers: list[dict]) -> list[tuple[str, float]]:
    """The offers whose total net gain is positive, as (name, gain), largest gain first."""
    # TODO: the value each offer adds at its row's price, less what it costs, for all its units.
    return []


if __name__ == "__main__":
    print(worth_buying([
        {"name": "budget", "price": 0.4, "change": 1, "cost": 0.1, "units": 100},
        {"name": "berth", "price": 0.2, "change": 1, "cost": 0.25, "units": 50},
    ]))
