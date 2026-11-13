"""Lesson 4.7.2: the legacy pywraplp script and its MathOpt port, solved on three GridCap sizes.

Both use SCIP. The port is right when it reaches the same optimal value, and when each one's plan
is allowed by the other's rows. GridCap is a fictional utility's portfolio.
"""

from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt

from gridcap import generate
from legacy_selection import solve_legacy
from ported_selection import solve_ported


def allowed(portfolio, funded) -> bool:
    """Does a plan keep every rule of the selection model? Checked by hand, not by a solver."""
    chosen = set(funded)
    if sum(portfolio.project(pid).capex for pid in chosen) > portfolio.capital_budget:
        return False
    groups = {}
    for p in portfolio.projects:
        if p.must_do and p.project_id not in chosen:
            return False
        if p.parent and p.project_id in chosen and p.parent not in chosen:
            return False
        if p.alt_group and p.project_id in chosen:
            groups[p.alt_group] = groups.get(p.alt_group, 0) + 1
    return all(n <= 1 for n in groups.values())


default_gap = pywraplp.MPSolverParameters().GetDoubleParam(pywraplp.MPSolverParameters.RELATIVE_MIP_GAP)
print(f"pywraplp's default relative MIP gap: {default_gap}")
for size, gap in (("tiny", None), ("small", None), ("medium", None), ("medium", 0.0)):
    portfolio = generate(size)
    status, old_value, old_plan, _ = solve_legacy(portfolio, relative_gap=gap)
    reason, new_value, new_plan, _ = solve_ported(portfolio, relative_gap=gap)
    same_value = abs(old_value - new_value) <= 1e-6 * max(1.0, abs(old_value))
    print(f"{size:6} gap {'default' if gap is None else gap}: pywraplp {'OPTIMAL' if status == pywraplp.Solver.OPTIMAL else status} ${old_value:,.0f}k | "
          f"MathOpt {reason.name} ${new_value:,.0f}k | same value: {same_value}, "
          f"same plan: {sorted(old_plan) == sorted(new_plan)}, "
          f"each plan allowed: {allowed(portfolio, old_plan) and allowed(portfolio, new_plan)}")
