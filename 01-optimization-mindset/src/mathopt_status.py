"""What a solve answers: a status first, then a value and the variables' values only if it found a plan."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from zoo_lp_milp import build

tiny = generate("tiny")


def solve_tiny() -> tuple[str, float, float]:
    model, x = build(integer=True)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason.name, result.objective_value(), result.variable_values(x["P006"])


def solve_too_small(budget: int) -> str:
    model = mathopt.Model(name="too-small")
    x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in tiny.projects}
    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in tiny.projects) <= budget, name="budget")
    model.add_linear_constraint(x["P002"] == 1, name="must_P002")
    model.maximize(sum(p.value * x[p.project_id] for p in tiny.projects))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason.name


if __name__ == "__main__":
    status, value, p006 = solve_tiny()
    print(f"budget 7,390: {status}, value {value:,.1f}, x_P006 = {p006:.1f}")
    print(f"budget 2,000: {solve_too_small(2000)}")
    print("every status:", ", ".join(reason.name for reason in mathopt.TerminationReason))
