from __future__ import annotations

EPS = 1e-9


def reduce_row(coefs: dict[str, float], rhs: float, lo: dict[str, int],
               hi: dict[str, int]) -> tuple[str, dict[str, int]]:
    """What presolve concludes from one <= row: a verdict and the variables the row fixes."""
    # TODO: compute the least and the most activity from the bounds; decide "infeasible",
    # "redundant" or "keep"; for "keep", fix every free variable the row forces.
    return "keep", {}


if __name__ == "__main__":
    print(reduce_row({"p": 7, "q": 7, "r": 1}, 6, {"p": 0, "q": 0, "r": 0}, {"p": 1, "q": 1, "r": 1}))
