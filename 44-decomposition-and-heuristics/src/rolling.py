"""Rolling horizon on GridCap medium with crews: plan a window of years, keep its first years, roll on."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

from capital import EXACT, Capital, build, schedule, solve_highs


def fix(var: mathopt.Variable, value: float) -> None:
    var.lower_bound = value
    var.upper_bound = value


def solve_window(portfolio: Portfolio, cap: Capital, decided: dict[tuple[str, int], int],
                 first: int, last: int) -> mathopt.SolveResult:
    """Solve with every start before `first` decided and every start after `last` held at 0."""
    for (pid, t), var in cap.x.items():
        if (pid, t) in decided:
            fix(var, decided[pid, t])
        elif t > last:
            fix(var, 0)
        else:
            var.lower_bound, var.upper_bound = 0, 1
    return solve_highs(cap.model, EXACT)


def rolling_horizon(portfolio: Portfolio, window: int, step: int, *, crews: bool = True, verbose: bool = False):
    cap = build(portfolio, crews=crews)
    must = {p.project_id: p for p in portfolio.projects if p.must_do}
    rows = {r.name: r for r in cap.model.linear_constraints()}
    decided: dict[tuple[str, int], int] = {}
    years = portfolio.years
    solves = nodes = 0
    for i in range(0, len(years), step):
        first, last = years[i], years[min(i + window, len(years)) - 1]
        for pid, p in must.items():
            # A must-do may wait for a later window while its latest start lies beyond this one.
            rows[f"must_{pid}"].lower_bound = 1 if p.latest_start <= last else 0
        result = solve_window(portfolio, cap, decided, first, last)
        solves += 1
        nodes += result.solve_stats.node_count
        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            raise RuntimeError(f"window {first}-{last}: {result.termination.reason.name}")
        keep = years[i:i + step] if last != years[-1] else years[i:]
        for (pid, t), var in cap.x.items():
            if t in keep:
                decided[pid, t] = round(result.variable_values(var))
        if verbose:
            print(f"  window {first}-{last}: keep {keep[0]}-{keep[-1]}, window plan {result.objective_value():,.0f}")
        if last == years[-1]:
            break
    plan = {pid: t for (pid, t), v in decided.items() if v}
    return plan, solves, nodes
