from __future__ import annotations


def share_range(scores: list[tuple[float, float]], k: int) -> tuple[float, float] | None:
    """The shares s in [0, 1] at which candidate k is a best choice for s*first + (1-s)*second.

    `scores` holds each candidate's (first, second) value, both to maximize. Returns (low, high),
    the closed interval of shares at which candidate k scores at least as much as every other
    candidate, or None when there is no such share.
    """
    low, high = 0.0, 1.0
    a, b = scores[k]
    for j, (aj, bj) in enumerate(scores):
        if j == k:
            continue
        # s*(a - aj) + (1 - s)*(b - bj) >= 0, that is  s*slope >= bj - b
        slope = (a - aj) - (b - bj)
        if slope > 0:
            low = max(low, (bj - b) / slope)
        elif slope < 0:
            high = min(high, (bj - b) / slope)
        elif bj > b:
            return None
    if low > high:
        return None
    return low, high


if __name__ == "__main__":
    print(share_range([(0, 10), (6, 8), (10, 0)], 1))
