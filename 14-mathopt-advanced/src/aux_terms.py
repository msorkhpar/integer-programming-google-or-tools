"""OR-Tools 9.15: adding a second auxiliary objective erases the first one's terms, and a way around it."""

from ortools.math_opt.python import mathopt

from in_order import add_auxiliary


def terms(obj) -> dict[str, float]:
    return {t.variable.name: t.coefficient for t in obj.linear_terms()}


model = mathopt.Model(name="crews")
overtime = model.add_variable(lb=0, ub=40, name="overtime")
idle = model.add_variable(lb=0, ub=40, name="idle")
model.maximize(overtime + idle)

first = model.add_minimization_objective(1.5 * overtime, priority=1, name="overtime_cost")
print("after adding the first: ", {first.name: terms(first)})
second = model.add_minimization_objective(2 * idle, priority=2, name="idle_cost")
print("after adding the second:", {first.name: terms(first), second.name: terms(second)})
print("in the exported model:  ", {o.name: dict(zip(o.linear_coefficients.ids, o.linear_coefficients.values))
                                   for o in model.export_model().auxiliary_objectives.values()})

model = mathopt.Model(name="crews")
overtime = model.add_variable(lb=0, ub=40, name="overtime")
idle = model.add_variable(lb=0, ub=40, name="idle")
model.maximize(overtime + idle)
first = add_auxiliary(model, 1.5 * overtime, priority=1, is_maximize=False, name="overtime_cost")
second = add_auxiliary(model, 2 * idle, priority=2, is_maximize=False, name="idle_cost")
print("term by term:           ", {first.name: terms(first), second.name: terms(second)})
