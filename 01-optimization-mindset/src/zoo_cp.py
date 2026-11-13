"""The same selection in CP-SAT, where a business rule can be written as logic."""

from ortools.sat.python import cp_model

from gridcap import generate

tiny = generate("tiny")

model = cp_model.CpModel()
x = {p.project_id: model.new_bool_var(f"x_{p.project_id}") for p in tiny.projects}
model.add(sum(p.capex * x[p.project_id] for p in tiny.projects) <= tiny.capital_budget)
for p in tiny.projects:
    if p.must_do:
        model.add(x[p.project_id] == 1)
    if p.parent:
        model.add_implication(x[p.project_id], x[p.parent])      # child => parent
model.add_at_most_one(x["P006"], x["P007"])
model.maximize(sum(p.value * x[p.project_id] for p in tiny.projects))

solver = cp_model.CpSolver()
status = solver.solve(model)
print("CP-SAT", solver.status_name(status), "value", int(solver.objective_value))
print("       ", sorted(pid for pid, v in x.items() if solver.value(v)))
