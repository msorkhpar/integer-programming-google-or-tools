"""The PuLP port with CBC against the MathOpt model, both at a relative gap of 0.

The MathOpt side runs SCIP, not HiGHS: in a process that has imported pulp, MathOpt's HiGHS crashes
on a MIP (highs_after_pulp.py shows it). The module's tests check HiGHS in a separate process.
"""

import pulp
from ortools.math_opt.python import mathopt

import mathopt_timing
import pulp_timing
from gridcap import generate
from plan_rules import broken_rules

for size in ("tiny", "small"):
    portfolio = generate(size)
    pt = pulp_timing.build(portfolio)
    status = pt.prob.solve(pulp_timing.cbc(gapRel=0))
    cbc_value, cbc_plan = pulp.value(pt.prob.objective), pulp_timing.schedule(pt)

    model, x = mathopt_timing.build(portfolio)
    result = mathopt.solve(model, mathopt.SolverType.GSCIP, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    highs_value = result.objective_value()
    highs_plan = {pid: t for (pid, t), v in x.items() if result.variable_values(v) > 0.5}

    print(f"{size:<6} CBC {pulp.LpStatus[status]} ${cbc_value:,.0f}k | SCIP {result.termination.reason.name} "
          f"${highs_value:,.0f}k | same value: {abs(cbc_value - highs_value) < 1e-6}, "
          f"same plan: {cbc_plan == highs_plan}, rules broken: {broken_rules(portfolio, cbc_plan)} / "
          f"{broken_rules(portfolio, highs_plan)}")
    rows_pulp = sorted(row.name for row in pt.prob.constraints())
    rows_mathopt = sorted(c.name for c in model.linear_constraints())
    print(f"       rows {len(rows_pulp)} / {len(rows_mathopt)}, same names: {rows_pulp == rows_mathopt}; "
          f"variables {pt.prob.numVariables()} / {len(x)}")
