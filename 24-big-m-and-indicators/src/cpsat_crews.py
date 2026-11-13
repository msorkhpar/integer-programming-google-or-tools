"""The crew model in CP-SAT, where "use more crews only if hired" is a row with OnlyEnforceIf."""

from ortools.sat.python import cp_model

from gridcap import PROGRAMS, generate
from crew_model import CONTRACTOR_FEE, active

small = generate("small")
model = cp_model.CpModel()
x = {(p.project_id, t): model.new_bool_var(f"x_{p.project_id}_{t}") for p in small.projects for t in p.starts()}
hire = {(g, y): model.new_bool_var(f"hire_{g}_{y}") for g in PROGRAMS for y in small.years}
by_id = {p.project_id: p for p in small.projects}


def started(pid: str):
    return sum(x[pid, t] for t in by_id[pid].starts())


for p in small.projects:
    if p.must_do:
        model.add(started(p.project_id) == 1)
    else:
        model.add(started(p.project_id) <= 1)
for group in {p.alt_group for p in small.projects if p.alt_group}:
    model.add(sum(started(p.project_id) for p in small.projects if p.alt_group == group) <= 1)
for c in small.projects:
    if c.parent:
        for t in c.starts():
            model.add(sum(x[c.project_id, u] for u in c.starts() if u <= t)
                      <= sum(x[c.parent, s] for s in by_id[c.parent].starts() if s <= t - c.parent_lag))
for y in small.years:
    model.add(sum(p.spend(t)[y] * x[p.project_id, t] for p in small.projects for t in p.starts()
                  if y in p.spend(t)) <= small.budget[y])

for (g, y), h in hire.items():
    use = sum(p.crew_months * x[p.project_id, t] for p in small.projects if p.program == g
              for t in p.starts() if active(p, t, y))
    model.add(use <= small.crews[g, y]).only_enforce_if(~h)

model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in small.projects for t in p.starts())
               - CONTRACTOR_FEE * sum(hire.values()))
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
status = solver.solve(model)
print(f"CP-SAT {solver.status_name(status)}  objective {solver.objective_value:,.1f}"
      f"  hired {[key for key, h in hire.items() if solver.value(h)]}")
