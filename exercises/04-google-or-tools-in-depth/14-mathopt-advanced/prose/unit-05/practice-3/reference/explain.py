from __future__ import annotations

from ortools.math_opt.python import mathopt


def explain(result: mathopt.ComputeInfeasibleSubsystemResult) -> list[str]:
    """Sorted lines, one per side of each row or variable bound, and per integrality, in the subsystem."""
    if result.feasibility != mathopt.FeasibilityStatus.INFEASIBLE:
        return []
    subset = result.infeasible_subsystem
    lines = []
    for item, sides in [*subset.linear_constraints.items(), *subset.variable_bounds.items()]:
        if sides.lower:
            lines.append(f"{item.name} >= {item.lower_bound:g}")
        if sides.upper:
            lines.append(f"{item.name} <= {item.upper_bound:g}")
    lines += [f"{v.name} is integer" for v in subset.variable_integrality]
    return sorted(lines)


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_variable(lb=0, ub=10, name="x")
    row = model.add_linear_constraint(x >= 12, name="need")
    subset = mathopt.ModelSubset(linear_constraints={row: mathopt.ModelSubsetBounds(lower=True)},
                                 variable_bounds={x: mathopt.ModelSubsetBounds(upper=True)})
    print(explain(mathopt.ComputeInfeasibleSubsystemResult(
        feasibility=mathopt.FeasibilityStatus.INFEASIBLE, infeasible_subsystem=subset, is_minimal=True)))
