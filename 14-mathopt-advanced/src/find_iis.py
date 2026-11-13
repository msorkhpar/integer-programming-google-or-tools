"""An infeasible subsystem found by hand, returned in the same type `compute_infeasible_subsystem` returns.

In OR-Tools 9.15 only Gurobi computes an infeasible subsystem through MathOpt. This is the deletion
filter (Chinneck's method): drop one bound at a time from a copy of the model; if the copy stays
infeasible, the bound was not needed and stays dropped; if it becomes feasible, the bound is put
back. What is left is irreducible: every bound in it is needed for the infeasibility.
"""

from __future__ import annotations

import math

from ortools.math_opt.python import mathopt

from plan_model import quiet

INFEASIBLE = (mathopt.TerminationReason.INFEASIBLE, mathopt.TerminationReason.INFEASIBLE_OR_UNBOUNDED)


def is_infeasible(model: mathopt.Model, solver: mathopt.SolverType) -> bool:
    with quiet():
        return mathopt.solve(model, solver).termination.reason in INFEASIBLE


def deletion_filter(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS,
                    variables: list[mathopt.Variable] = ()) -> mathopt.ComputeInfeasibleSubsystemResult:
    """Rows' bounds, and the bounds of `variables` (the ones a scenario set), that stay infeasible."""
    work = mathopt.Model.from_model_proto(model.export_model())        # never edit the caller's model
    work.set_linear_objective(0.0, is_maximize=False)                  # only feasibility matters
    if not is_infeasible(work, solver):
        return mathopt.ComputeInfeasibleSubsystemResult(feasibility=mathopt.FeasibilityStatus.FEASIBLE)
    candidates = [(work.get_linear_constraint(c.id), side) for c in model.linear_constraints()
                  for side in ("lower_bound", "upper_bound")]
    candidates += [(work.get_variable(v.id), side) for v in variables for side in ("lower_bound", "upper_bound")]
    kept = []
    for item, side in candidates:
        old = getattr(item, side)
        if math.isinf(old):
            continue                                                   # no bound on this side
        setattr(item, side, -math.inf if side == "lower_bound" else math.inf)
        if not is_infeasible(work, solver):
            setattr(item, side, old)                                   # needed: put it back
            kept.append((item, side))
    rows, bounds = {}, {}
    for item, side in kept:
        target = rows if isinstance(item, mathopt.LinearConstraint) else bounds
        original = (model.get_linear_constraint(item.id) if target is rows else model.get_variable(item.id))
        old = target.get(original, mathopt.ModelSubsetBounds())
        target[original] = mathopt.ModelSubsetBounds(lower=old.lower or side == "lower_bound",
                                                     upper=old.upper or side == "upper_bound")
    return mathopt.ComputeInfeasibleSubsystemResult(
        feasibility=mathopt.FeasibilityStatus.INFEASIBLE,
        infeasible_subsystem=mathopt.ModelSubset(variable_bounds=bounds, linear_constraints=rows),
        is_minimal=True)


def report(result: mathopt.ComputeInfeasibleSubsystemResult) -> list[str]:
    """One line per bound in the subsystem, as a planner would read it."""
    if result.feasibility != mathopt.FeasibilityStatus.INFEASIBLE:
        return [f"no conflict: {result.feasibility.name}"]
    lines = []
    subset = result.infeasible_subsystem
    for row, which in sorted(subset.linear_constraints.items(), key=lambda kv: kv[0].name):
        sides = [s for s, on in (("lower", which.lower), ("upper", which.upper)) if on]
        bound = {"lower": row.lower_bound, "upper": row.upper_bound}
        lines.append(f"row {row.name}: " + ", ".join(f"{s} bound {bound[s]:,.0f}" for s in sides))
    for var, which in sorted(subset.variable_bounds.items(), key=lambda kv: kv[0].name):
        sides = [s for s, on in (("lower", which.lower), ("upper", which.upper)) if on]
        bound = {"lower": var.lower_bound, "upper": var.upper_bound}
        lines.append(f"variable {var.name}: " + ", ".join(f"{s} bound {bound[s]:g}" for s in sides))
    return lines
