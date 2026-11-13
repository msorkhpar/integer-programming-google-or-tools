from __future__ import annotations

import math


def strong_choice(parent: float, trials: dict[str, tuple[float | None, float | None]], eps: float = 1e-6) -> str:
    """The candidate whose two children lower the bound most, scored by the product of the drops."""
    # TODO: drop = parent - child value, or math.inf for an infeasible child (None);
    # score = max(drop_down, eps) * max(drop_up, eps); keep the first highest score.
    return ""


if __name__ == "__main__":
    print(strong_choice(500.0, {"crews_east": (470.0, 499.9), "crews_west": (494.0, 495.0), "open_depot": (None, 488.0)}))
