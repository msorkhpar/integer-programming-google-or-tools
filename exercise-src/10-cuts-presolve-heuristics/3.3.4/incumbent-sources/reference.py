from __future__ import annotations

import math

LEGEND = {"B": "Branching", "C": "Central rounding", "F": "Feasibility pump", "H": "Heuristic",
          "I": "Shifting", "J": "Feasibility jump", "L": "Sub-MIP", "P": "Empty MIP",
          "R": "Randomized rounding", "S": "Solve LP", "T": "Evaluate node", "U": "Unbounded",
          "X": "User solution", "Y": "HiGHS solution", "Z": "ZI Round", "l": "Trivial lower",
          "p": "Trivial point", "u": "Trivial upper", "z": "Trivial zero"}


def history(rows: list[dict]) -> list[tuple[str, float, float | None]]:
    """(source name, incumbent, gap) for every row that reports a new incumbent, in log order."""
    out = []
    for row in rows:
        if not row["src"]:
            continue
        name = LEGEND[row["src"]]
        if math.isinf(row["bound"]):
            gap = None
        else:
            gap = abs(row["bound"] - row["incumbent"]) / abs(row["incumbent"])
        out.append((name, row["incumbent"], gap))
    return out


if __name__ == "__main__":
    print(history([{"src": "R", "bound": 1520.5, "incumbent": 1490.0}, {"src": "", "bound": 1500.0, "incumbent": 1490.0}]))
