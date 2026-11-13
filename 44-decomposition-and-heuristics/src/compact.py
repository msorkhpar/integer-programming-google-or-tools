"""The same crew-day question as one compact MILP, as on OR-Tools' bin packing page: a variable per
task type and day, and a yes/no per day. It checks column generation's answer."""

import math

from ortools.math_opt.python import mathopt

from colgen import DAY, TASKS, column_generation


def compact(days: int, integer: bool = True) -> mathopt.SolveResult:
    m = mathopt.Model(name="crew days, compact")
    use = [m.add_variable(lb=0, ub=1, is_integer=integer, name=f"use_{k}") for k in range(days)]
    n = {(t, k): m.add_variable(lb=0, ub=need, is_integer=integer, name=f"n_{t}_{k}")
         for t, (_, need) in TASKS.items() for k in range(days)}
    for t, (_, need) in TASKS.items():
        m.add_linear_constraint(sum(n[t, k] for k in range(days)) >= need, name=f"cover_{t}")
    for k in range(days):
        m.add_linear_constraint(sum(minutes * n[t, k] for t, (minutes, _) in TASKS.items()) <= DAY * use[k],
                                name=f"day_{k}")
        if k:
            m.add_linear_constraint(use[k] <= use[k - 1], name=f"order_{k}")   # days used first to last
    m.minimize(sum(use))
    return mathopt.solve(m, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))


z_lp, z_ip, _, history, _ = column_generation(verbose=False)
days = z_ip + 2                                       # any upper bound on the days will do
lp, milp = compact(days, integer=False), compact(days)
print(f"compact LP bound      {lp.objective_value():7.3f}  -> proves at least {math.ceil(lp.objective_value() - 1e-6)} days")
print(f"column generation LP  {z_lp:7.3f}  -> proves at least {math.ceil(z_lp - 1e-6)} days")
print(f"compact MILP optimum  {milp.objective_value():3.0f} days ({milp.termination.reason.name});"
      f" column generation found {z_ip}")
