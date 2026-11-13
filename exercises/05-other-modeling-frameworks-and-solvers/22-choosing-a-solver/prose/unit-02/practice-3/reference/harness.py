from __future__ import annotations

import math
from collections.abc import Callable


def shifted_geometric_mean(values: list[float], shift: float) -> float:
    """exp(mean of ln(max(1, v + shift))) - shift (given)."""
    logs = [math.log(max(1.0, v + shift)) for v in values]
    return math.exp(sum(logs) / len(logs)) - shift


def benchmark(solve: Callable[[str, str, int], tuple[bool, float]], solvers: list[str], instances: list[str],
              seeds: list[int], shift: float, cap: float) -> dict[str, dict]:
    """Per solver: runs, solved, repeat and sgm over every (instance, seed) cell, each cell solved twice."""
    summary = {}
    for solver in solvers:
        firsts, repeat = [], True
        for instance in instances:
            for seed in seeds:
                first, second = solve(solver, instance, seed), solve(solver, instance, seed)
                repeat = repeat and first == second
                firsts.append(first)
        counted = [work if solved else cap for solved, work in firsts]
        summary[solver] = {"runs": len(firsts), "solved": sum(solved for solved, _ in firsts),
                           "repeat": repeat, "sgm": shifted_geometric_mean(counted, shift)}
    return summary

if __name__ == "__main__":
    table = {("A", "i1", 1): (True, 120.0), ("A", "i2", 1): (True, 3000.0)}
    print(benchmark(lambda s, i, k: table[s, i, k], ["A"], ["i1", "i2"], [1], 100.0, 1e6))
