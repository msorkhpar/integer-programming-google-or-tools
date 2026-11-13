from __future__ import annotations

import re


def incumbents(log: list[str], minimize: bool = True) -> list[tuple[float, float]]:
    """(LP iterations, objective) each time a HiGHS MIP log's progress table shows a better plan."""
    events: list[tuple[float, float]] = []
    in_table = False
    for line in log:
        if "LpIters" in line:
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("Solving report"):
            break
        tokens = line.split()
        if len(tokens) < 11 or not re.fullmatch(r"\d+(\.\d+)?s", tokens[-1]):
            continue
        try:
            best = float(tokens[-7])
            iterations = float(tokens[-2][:-1]) * 1000 if tokens[-2].endswith("k") else float(tokens[-2])
        except ValueError:
            continue
        if best in (float("inf"), float("-inf")):
            continue
        better = not events or (best < events[-1][1] if minimize else best > events[-1][1])
        if better:
            events.append((iterations, best))
    return events


if __name__ == "__main__":
    demo = [
        "Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time",
        " J       0       0         0   0.00%   0               9120              Large        0      0      0         0     0.0s",
        " L       0       0         0   0.00%   7710.5          7800               1.15%      12      9      0       210     0.1s",
    ]
    print(incumbents(demo))
