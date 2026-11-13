from __future__ import annotations


def share_range(scores: list[tuple[float, float]], k: int) -> tuple[float, float] | None:
    """The shares s in [0, 1] at which candidate k is a best choice for s*first + (1-s)*second.

    `scores` holds each candidate's (first, second) value, both to maximize. Returns (low, high),
    the closed interval of shares at which candidate k scores at least as much as every other
    candidate, or None when there is no such share.
    """
    # TODO: compare candidate k with every other candidate.
    return (0.5, 0.5)


if __name__ == "__main__":
    print(share_range([(0, 10), (6, 8), (10, 0)], 1))
