from __future__ import annotations


def best_reel(prices: dict[str, float], pieces: dict[str, tuple[int, int]], reel: int) -> tuple[float, dict[str, int]]:
    """The pattern worth the most at `prices` that fits in one reel, with at most `demand` of each piece."""
    best = [(0.0, {})] * (reel + 1)                 # best[c]: the most worth within c metres
    for name, (length, demand) in pieces.items():
        new = list(best)
        for c in range(reel + 1):
            for n in range(1, demand + 1):
                if n * length > c:
                    break
                worth, pattern = best[c - n * length]
                worth += n * prices[name]
                if worth > new[c][0] + 1e-12:
                    new[c] = (worth, {**pattern, name: n})
        best = new
    return best[reel]


if __name__ == "__main__":
    print(best_reel({"feeder": 0.5, "service": 0.2}, {"feeder": (40, 3), "service": (15, 6)}, 100))
