from __future__ import annotations


def worth_buying(offers: list[dict]) -> list[tuple[str, float]]:
    """The offers whose total net gain is positive, as (name, gain), largest gain first."""
    gains = []
    for offer in offers:
        per_unit = offer["price"] * offer["change"] - offer["cost"]
        total = per_unit * offer["units"]
        if total > 0:
            gains.append((offer["name"], total))
    return sorted(gains, key=lambda pair: pair[1], reverse=True)


if __name__ == "__main__":
    print(worth_buying([
        {"name": "budget", "price": 0.4, "change": 1, "cost": 0.1, "units": 100},
        {"name": "berth", "price": 0.2, "change": 1, "cost": 0.25, "units": 50},
    ]))
