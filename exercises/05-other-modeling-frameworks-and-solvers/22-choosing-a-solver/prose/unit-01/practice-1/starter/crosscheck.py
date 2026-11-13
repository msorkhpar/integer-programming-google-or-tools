from __future__ import annotations

import statistics


def suspects(results: dict[str, tuple[str, float]], rel_tol: float) -> list[str]:
    """Names of the OPTIMAL solvers whose objective is off the OPTIMAL median by more than rel_tol * max(1, |median|)."""
    # TODO: keep the OPTIMAL results, take the median of their objectives, and flag the far ones.
    return []


if __name__ == "__main__":
    print(suspects({"A": ("OPTIMAL", 20.3078), "B": ("OPTIMAL", 20.3078), "C": ("OPTIMAL", 19.68)}, 1e-6))
