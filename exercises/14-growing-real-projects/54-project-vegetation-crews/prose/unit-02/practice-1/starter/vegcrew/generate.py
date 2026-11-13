"""A seeded generator of fictional trimming seasons, in the shape the circuit inventory exports.

Each column is drawn from its own random stream, named after the seed, the size and the column, so
adding a column later never changes the values of the columns already there.
"""

from __future__ import annotations

import random

SIZES = {"tiny": 6, "small": 20, "medium": 60}
REGIONS = ("North", "River", "Hills")


def stream(seed: int, size: str, column: str) -> random.Random:
    return random.Random(f"{seed}-{size}-{column}")


def scenario(size: str = "small", seed: int = 54) -> dict:
    """One season: a budget and the circuits, as plain JSON-ready values."""
    n = SIZES[size]
    draw = stream(seed, size, "circuits")
    circuits = []
    for i in range(1, n + 1):
        miles = draw.randint(8, 40)
        circuits.append({
            "id": f"C{i:02d}",
            "region": draw.choice(REGIONS),
            "miles": miles,
            "cost": round(miles * draw.uniform(3.0, 6.0)),       # $k to trim the whole circuit
            "risk": round(miles * draw.uniform(2.0, 12.0)),      # $k a year of tree-caused outage risk
        })
    budget = round(0.45 * sum(c["cost"] for c in circuits))
    return {"name": f"{size}-{seed}", "budget": budget, "circuits": circuits}
