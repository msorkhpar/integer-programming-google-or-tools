"""Lesson 2.3.4: a yes/no model has no dual values. Its value moves in steps as the budget grows."""

from ortools.math_opt.python import mathopt

from gridcap import generate

tiny = generate("tiny")


def selection(budget: int, integer: bool) -> tuple[mathopt.Model, mathopt.LinearConstraint]:
    """The tiny one-period selection model of lesson 1.1.3, with a budget to vary."""
    model = mathopt.Model(name="tiny-selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in tiny.projects}
    row = model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in tiny.projects) <= budget, name="budget")
    for p in tiny.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
    model.add_linear_constraint(x["P006"] + x["P007"] <= 1, name="alt_G006")
    model.maximize(sum(p.value * x[p.project_id] for p in tiny.projects))
    return model, row


model, row = selection(tiny.capital_budget, integer=True)
result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print(f"MILP {result.termination.reason.name}, value {result.objective_value():,.0f}")
try:
    result.dual_values(row)
except ValueError as error:
    print("dual_values:", error)

print(f"{'budget':>6} {'MILP value':>10} {'LP value':>9} {'LP price':>8}")
for budget in range(7000, 7801, 100):
    milp = mathopt.solve(selection(budget, integer=True)[0], mathopt.SolverType.HIGHS)
    lp_model, lp_row = selection(budget, integer=False)
    lp = mathopt.solve(lp_model, mathopt.SolverType.GLOP)
    print(f"{budget:>6,} {milp.objective_value():>10,.0f} {lp.objective_value():>9,.1f} {lp.dual_values(lp_row):>8.4f}")
