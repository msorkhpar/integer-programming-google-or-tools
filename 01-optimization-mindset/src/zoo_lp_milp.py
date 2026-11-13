"""The tiny selection problem as an LP and as a MILP, in OR-Tools MathOpt."""

from ortools.math_opt.python import mathopt

from gridcap import generate

tiny = generate("tiny")


def build(integer: bool) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="tiny-selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in tiny.projects}
    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in tiny.projects) <= tiny.capital_budget,
                                name="budget")
    for p in tiny.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
    model.add_linear_constraint(x["P006"] + x["P007"] <= 1, name="alt_G006")
    model.maximize(sum(p.value * x[p.project_id] for p in tiny.projects))
    return model, x


if __name__ == "__main__":
    for integer, solver in ((False, mathopt.SolverType.GLOP), (True, mathopt.SolverType.HIGHS)):
        model, x = build(integer)
        result = mathopt.solve(model, solver)
        chosen = {pid: round(result.variable_values(v), 3) for pid, v in x.items() if result.variable_values(v) > 1e-9}
        kind = "MILP" if integer else "LP  "
        print(f"{kind} {solver.name:5} {result.termination.reason.name} value {result.objective_value():,.1f}")
        print("      ", chosen)
