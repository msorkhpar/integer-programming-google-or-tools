"""The outage model in one CP-SAT solve, to check logic-based Benders: the plan rules and every
year's outages together, each outage an optional interval present only if its project starts."""

from ortools.sat.python import cp_model

from gridcap import generate

from capital import alt_groups
from lbbd import lbbd
from outages import jobs

small = generate("small")
outage = jobs(small)
model = cp_model.CpModel()
x = {(p.project_id, t): model.new_bool_var(f"x_{p.project_id}_{t}") for p in small.projects for t in p.starts()}
by_id = {p.project_id: p for p in small.projects}


def started(pid):
    return sum(x[pid, t] for t in by_id[pid].starts())


for p in small.projects:
    model.add(started(p.project_id) == 1) if p.must_do else model.add(started(p.project_id) <= 1)
for members in alt_groups(small).values():
    model.add(sum(started(m) for m in members) <= 1)
for c in small.projects:
    if c.parent:
        for t in c.starts():
            model.add(sum(x[c.project_id, u] for u in c.starts() if u <= t)
                      <= sum(x[c.parent, s] for s in by_id[c.parent].starts() if s <= t - c.parent_lag))
for y in small.years:
    model.add(sum(c * x[p.project_id, t] for p in small.projects for t in p.starts()
                  for yy, c in p.spend(t).items() if yy == y) <= small.budget[y])
    year_outages = []
    for pid, j in outage.items():
        if (pid, y) in x:
            start = model.new_int_var(j.release, j.deadline - j.weeks, f"s_{pid}_{y}")
            year_outages.append(model.new_optional_fixed_size_interval_var(start, j.weeks, x[pid, y], f"o_{pid}_{y}"))
    model.add_no_overlap(year_outages)
model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in small.projects for t in p.starts()))
solver = cp_model.CpSolver()
solver.parameters.num_workers = 8
status = solver.solve(model)
best, plan, iterations, cuts = lbbd(small, relaxation="season")
print(f"one CP-SAT model:        {solver.status_name(status)} {solver.objective_value:,.0f}")
print(f"logic-based Benders:     {best:,.0f}  ({iterations} master solve, {cuts} cuts)")
