"""Lesson 9.1.1: does any solver hand back a ray for the carry bug, and what does a hedged answer claim?

GridCap is a fictional utility's portfolio. The carry bug is the one of separate_lock.py: money
carried out of a year is added to the next year's cash but never leaves its own year. Its LP
relaxation (every x continuous in [0, 1]) is solved by three LP-capable solvers through MathOpt,
and the MIP's hedged answer from HiGHS is read field by field.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from lock_model import build, solve

small = generate("small")


def carry_bug(integer: bool):
    bug = build(small, integer=integer)
    carry = {y: bug.model.add_variable(lb=0, name=f"carry_{y}") for y in small.years}
    for i, y in enumerate(small.years):
        bug.model.delete_linear_constraint(bug.rules[f"budget_{y}"])
        incoming = carry[small.years[i - 1]] if i else 0
        bug.model.add_linear_constraint(bug.spend[y] <= small.budget[y] + incoming, name=f"cash_{y}")
    bug.model.maximize(bug.npv + 0.03 * mathopt.fast_sum(carry.values()))
    return bug.model


S = mathopt.SolverType
for solver, presolve in ((S.HIGHS, True), (S.GLOP, True), (S.GLOP, False), (S.GSCIP, True)):
    params = mathopt.SolveParameters() if presolve else mathopt.SolveParameters(presolve=mathopt.Emphasis.OFF)
    result = solve(carry_bug(integer=False), solver, params=params)
    print(f"LP relaxation, {solver.name:<5} presolve {'on ' if presolve else 'off'}: "
          f"{result.termination.reason.name:<24} ray returned: {result.has_ray()}")

status = solve(carry_bug(integer=True)).termination.problem_status
print(f"MIP, HiGHS: primal {status.primal_status.name}, dual {status.dual_status.name}, "
      f"primal_or_dual_infeasible {status.primal_or_dual_infeasible}")
