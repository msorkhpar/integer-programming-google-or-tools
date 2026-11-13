"""Read a HiGHS MIP log: its progress rows, and which heuristic found each new incumbent."""

from __future__ import annotations

import re
from dataclasses import dataclass

#: The legend HiGHS prints above its progress table, one letter per source of a new solution.
SOURCES = {"B": "Branching", "C": "Central rounding", "F": "Feasibility pump", "H": "Heuristic",
           "I": "Shifting", "J": "Feasibility jump", "L": "Sub-MIP", "P": "Empty MIP",
           "R": "Randomized rounding", "S": "Solve LP", "T": "Evaluate node", "U": "Unbounded",
           "X": "User solution", "Y": "HiGHS solution", "Z": "ZI Round", "l": "Trivial lower",
           "p": "Trivial point", "u": "Trivial upper", "z": "Trivial zero"}

ROW = re.compile(r"^ (?P<src>[A-Za-z ]) +(?P<proc>\d+) +(?P<queue>\d+) +(?P<leaves>\d+) +(?P<expl>[\d.]+)% +"
                 r"(?P<bound>\S+) +(?P<sol>\S+) +(?P<gap>\S+) +(?P<cuts>\d+) +(?P<inlp>\d+) +(?P<confl>\d+) +"
                 r"(?P<lpiters>\d+) +\S+$")


@dataclass
class Progress:
    src: str              # "" when the row is a periodic report, not a new solution
    nodes: int            # Proc.: nodes processed so far
    bound: float          # BestBound (inf before the first LP)
    sol: float | None     # BestSol: the incumbent's value (None before there is one)
    gap: str              # as printed: "Large" or "1.25%"
    cuts: int             # cuts found so far
    lp_iters: int


def progress(log: list[str]) -> list[Progress]:
    rows = []
    for line in log:
        m = ROW.match(line)
        if m:
            sol = m["sol"]
            rows.append(Progress(m["src"].strip(), int(m["proc"]), float(m["bound"]),
                                 None if sol in ("inf", "-inf") else float(sol), m["gap"], int(m["cuts"]),
                                 int(m["lpiters"])))
    return rows


def relative_gap(bound: float, sol: float) -> float:
    """HiGHS's gap: |bound - incumbent| / |incumbent|."""
    return abs(bound - sol) / abs(sol)
