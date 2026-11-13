from __future__ import annotations

from ortools.math_opt.python import mathopt


def explain(result: mathopt.ComputeInfeasibleSubsystemResult) -> list[str]:
    """Sorted lines, one per side of each row or variable bound, and per integrality, in the subsystem."""
    # TODO: check feasibility, then read linear_constraints, variable_bounds and variable_integrality.
    return []


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_variable(lb=0, ub=10, name="x")
    row = model.add_linear_constraint(x >= 12, name="need")
    subset = mathopt.ModelSubset(linear_constraints={row: mathopt.ModelSubsetBounds(lower=True)},
                                 variable_bounds={x: mathopt.ModelSubsetBounds(upper=True)})
    print(explain(mathopt.ComputeInfeasibleSubsystemResult(
        feasibility=mathopt.FeasibilityStatus.INFEASIBLE, infeasible_subsystem=subset, is_minimal=True)))
