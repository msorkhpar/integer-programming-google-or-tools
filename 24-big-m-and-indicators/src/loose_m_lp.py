"""The LP relaxation and the MILP of GridCap small's crew model, with M from 1e6 down to the tightest."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from crew_model import (build, hired, m_by_solving, m_from_once_rows, m_from_variable_bounds,
                        quiet_solve)

small = generate("small")
choices = {"1e6": 1e6, "bounds": m_from_variable_bounds(small), "once rows": m_from_once_rows(small),
           "LP max": m_by_solving(small, integer=False), "MILP max": m_by_solving(small, integer=True)}
exact = mathopt.SolveParameters(relative_gap_tolerance=0.0)
no_presolve = mathopt.SolveParameters(relative_gap_tolerance=0.0, presolve=mathopt.Emphasis.OFF)

row = ("transmission", 2029)
print(f"LP relaxation, row {row}: crew use, in-house crews, M and the LP's hire value")
for name in ("1e6", "MILP max"):
    lp = build(small, choices[name], integer=False)
    result = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    use = mathopt.evaluate_expression(lp.use[row], result.variable_values())
    hire = result.variable_values(lp.hire[row])
    print(f"  M = {name:9} use {use:5.1f}  crews {small.crews[row]}  M {lp.big_m[row]:>9,.0f}  hire {hire:.6f}"
          f"  fee paid {300 * hire:6.2f}k")

print("M choice     LP bound  MILP optimum  HiGHS nodes  (presolve off)  contractors hired")
for name, big_m in choices.items():
    lp = mathopt.solve(build(small, big_m, integer=False).model, mathopt.SolverType.GLOP)
    cm = build(small, big_m)
    result = quiet_solve(cm.model, params=exact)
    bare = quiet_solve(build(small, big_m).model, params=no_presolve)
    print(f"{name:10} {lp.objective_value():10,.1f}  {result.objective_value():12,.1f}  {result.solve_stats.node_count:11}"
          f"  {bare.solve_stats.node_count:14}  {hired(cm, result)}")
free = mathopt.solve(build(small, 0, integer=False, form="none", fee=0).model, mathopt.SolverType.GLOP)
print(f"LP with no crew rule and no fee: {free.objective_value():,.1f}")
