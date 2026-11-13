from __future__ import annotations


def separating_weights(ids: list[str]) -> dict[str, int]:
    """Positive integer weights: different selections have different totals, in every process."""
    return {i: 2 ** rank for rank, i in enumerate(sorted(ids))}


if __name__ == "__main__":
    print(separating_weights(["S-14", "S-02", "S-09"]))
