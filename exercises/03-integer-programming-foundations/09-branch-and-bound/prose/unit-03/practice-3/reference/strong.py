from __future__ import annotations

import math


def strong_choice(parent: float, trials: dict[str, tuple[float | None, float | None]], eps: float = 1e-6) -> str:
    """The candidate whose two children lower the bound most, scored by the product of the drops."""

    def drop(child: float | None) -> float:
        return math.inf if child is None else parent - child

    best, best_score = None, -1.0
    for name, (down, up) in trials.items():
        score = max(drop(down), eps) * max(drop(up), eps)
        if score > best_score:
            best, best_score = name, score
    return best


if __name__ == "__main__":
    print(strong_choice(500.0, {"crews_east": (470.0, 499.9), "crews_west": (494.0, 495.0), "open_depot": (None, 488.0)}))
