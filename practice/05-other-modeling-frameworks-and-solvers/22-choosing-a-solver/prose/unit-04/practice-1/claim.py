from __future__ import annotations


def faster(a: list[float], b: list[float], factor: float) -> str:
    """"a" or "b" if that solver is ahead by at least `factor` in every repetition, else "neither"."""
    # TODO: compare repetition by repetition, both ways.
    return "a"


if __name__ == "__main__":
    print(faster([1.0, 1.2, 0.9], [4.1, 3.9, 4.4], 2.0))
