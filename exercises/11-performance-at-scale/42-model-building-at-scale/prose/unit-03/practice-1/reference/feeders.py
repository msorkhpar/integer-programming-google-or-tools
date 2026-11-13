from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Feeder:
    feeder_id: str        # "F00001", "F00002", ...
    length_km: int        # 1 to 40
    customers: int        # 50 to 5,000
    crew_days: int        # 2 to 20


def between(draw: random.Random, low: int, high: int) -> int:
    """A whole number from low to high, inclusive, built on random() alone."""
    return low + min(int(draw.random() * (high - low + 1)), high - low)


def generate_feeders(n: int, seed: int) -> list[Feeder]:
    """n fictional feeders, the same for the same seed, in any process."""
    feeders = []
    for i in range(n):
        draw = random.Random(seed * 1_000_000 + i)
        feeders.append(Feeder(f"F{i + 1:05d}", between(draw, 1, 40), between(draw, 50, 5_000),
                              between(draw, 2, 20)))
    return feeders


if __name__ == "__main__":
    for feeder in generate_feeders(5, seed=42):
        print(feeder)
