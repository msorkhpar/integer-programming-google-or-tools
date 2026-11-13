"""Lesson 4.7.1: run the legacy pywraplp selection script on GridCap tiny and small.

GridCap is a fictional utility's portfolio.
"""

from ortools.linear_solver import pywraplp

from gridcap import generate
from legacy_selection import solve_legacy

for size in ("tiny", "small"):
    portfolio = generate(size)
    status, value, funded, solver = solve_legacy(portfolio)
    ok = "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else status
    print(f"{size}: {ok}, {solver.NumVariables()} variables, {solver.NumConstraints()} rows, "
          f"value ${value:,.0f}k, {len(funded)} funded")
    if size == "tiny":
        print("  funded:", " ".join(funded))
        print("  rows:", " ".join(c.name() for c in solver.constraints()))
