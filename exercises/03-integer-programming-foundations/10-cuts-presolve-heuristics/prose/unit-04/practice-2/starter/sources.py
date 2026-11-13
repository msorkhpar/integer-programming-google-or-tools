from __future__ import annotations

import math

LEGEND = {"B": "Branching", "C": "Central rounding", "F": "Feasibility pump", "H": "Heuristic",
          "I": "Shifting", "J": "Feasibility jump", "L": "Sub-MIP", "P": "Empty MIP",
          "R": "Randomized rounding", "S": "Solve LP", "T": "Evaluate node", "U": "Unbounded",
          "X": "User solution", "Y": "HiGHS solution", "Z": "ZI Round", "l": "Trivial lower",
          "p": "Trivial point", "u": "Trivial upper", "z": "Trivial zero"}


def history(rows: list[dict]) -> list[tuple[str, float, float | None]]:
    """(source name, incumbent, gap) for every row that reports a new incumbent, in log order."""
    # TODO: skip rows with no letter; look the letter up in LEGEND as it is; the gap is
    # |bound - incumbent| / |incumbent|, or None while the bound is infinite.
    return []


if __name__ == "__main__":
    print(history([{"src": "R", "bound": 1520.5, "incumbent": 1490.0}, {"src": "", "bound": 1500.0, "incumbent": 1490.0}]))
