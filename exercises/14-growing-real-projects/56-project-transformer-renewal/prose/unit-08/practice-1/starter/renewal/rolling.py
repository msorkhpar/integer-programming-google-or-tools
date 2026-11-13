"""A rolling horizon (lesson 11.3.5): plan a few years at a time and keep only the first of them."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from .fleet import Transformer
from .model import build
from .request import Plan, Request
from .solve import is_feasible, read_plan, solve_quietly


def rolling(fleet: list[Transformer], request: Request, window: int = 3, keep: int = 1) -> Plan:
    """Solve years [a, a + window) with earlier years fixed and later ones held at zero; keep `keep` years.

    Budget, crew and spare rows stay in the model for every year, so what a window decides is
    counted against all of them. The plan's value is exact; its bound is only the last window's.
    """
    built = build(fleet, request)
    years = list(request.plan_years())
    variables = {**built.x, **built.out}            # keyed (unit or substation, year)
    decided: dict[tuple[str, int], int] = {}
    params = mathopt.SolveParameters(relative_gap_tolerance=request.gap)
    result = None
    for i in range(0, len(years), keep):
        last = years[min(i + window, len(years)) - 1]
        for key, var in variables.items():
            if key in decided:
                var.lower_bound = var.upper_bound = decided[key]
            elif key[1] > last:
                var.lower_bound = var.upper_bound = 0
            else:
                var.lower_bound, var.upper_bound = 0, 1
        result = solve_quietly(built.model, params)
        if not is_feasible(result):
            return read_plan(built, result)
        kept = years[i:i + keep] if last != years[-1] else years[i:]
        for key, var in variables.items():
            if key[1] in kept:
                decided[key] = round(result.variable_values(var))
        if last == years[-1]:
            break
    return read_plan(built, result)
