from __future__ import annotations


def best_reel(prices: dict[str, float], pieces: dict[str, tuple[int, int]], reel: int) -> tuple[float, dict[str, int]]:
    """The pattern worth the most at `prices` that fits in one reel, with at most `demand` of each piece."""
    # TODO: write the pricing problem first, then solve it.
    return 0.0, {}


if __name__ == "__main__":
    print(best_reel({"feeder": 0.5, "service": 0.2}, {"feeder": (40, 3), "service": (15, 6)}, 100))
