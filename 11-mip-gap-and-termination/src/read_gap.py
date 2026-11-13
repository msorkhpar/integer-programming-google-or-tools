"""Read the incumbent, the best bound and the gap from a MathOpt SolveResult."""

import dataclasses

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs


def gap(result: mathopt.SolveResult) -> tuple[float, float]:
    """Absolute and relative gap of a maximization that holds a plan worth more than 0."""
    bounds = result.termination.objective_bounds
    absolute = bounds.dual_bound - bounds.primal_bound
    relative = absolute / abs(bounds.primal_bound)
    return absolute, relative


medium = generate("medium")
sel = build(medium)
result = solve_highs(sel.model, mathopt.SolveParameters(node_limit=100, relative_gap_tolerance=0.0))

print(f"termination: {result.termination.reason.name}, limit {result.termination.limit.name}")
print(f"result.objective_value():   {result.objective_value():,.1f}")
print(f"result.best_objective_bound(): {result.best_objective_bound():,.1f}")
print(f"result.termination.objective_bounds: {result.termination.objective_bounds}")
absolute, relative = gap(result)
print(f"absolute gap {absolute:,.1f} ($k), relative gap {relative:.4%}")

print()
short = dataclasses.replace(medium, budget={**medium.budget, 2027: 1_000})
broken = solve_highs(build(short).model)
print(f"2027 budget cut to 1,000: {broken.termination.reason.name}, "
      f"has a plan: {broken.has_primal_feasible_solution()}")
print(f"objective_bounds: {broken.termination.objective_bounds}")
try:
    broken.objective_value()
except ValueError as error:
    print(f"objective_value(): ValueError: {error}")
