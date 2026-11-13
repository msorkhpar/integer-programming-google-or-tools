from __future__ import annotations

import re


def incumbents(log: list[str], minimize: bool = True) -> list[tuple[float, float]]:
    """(LP iterations, objective) each time a HiGHS MIP log's progress table shows a better plan."""
    # TODO: find the table, read BestSol and LpIters from each row, keep only better plans.
    return []


if __name__ == "__main__":
    demo = [
        "Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time",
        " J       0       0         0   0.00%   0               9120              Large        0      0      0         0     0.0s",
        " L       0       0         0   0.00%   7710.5          7800               1.15%      12      9      0       210     0.1s",
    ]
    print(incumbents(demo))
