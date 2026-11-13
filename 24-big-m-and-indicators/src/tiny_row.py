"""One crew row of GridCap tiny, its big-M derived three ways, and what a too-small M refuses."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from crew_model import active, build, m_by_solving, m_from_once_rows, m_from_variable_bounds, quiet_solve

tiny = generate("tiny")
row = ("distribution", 2029)
terms = {f"x_{p.project_id}_{t}": p.crew_months for p in tiny.projects if p.program == row[0]
         for t in p.starts() if active(p, t, row[1])}
print(f"crew use of {row[0]} in {row[1]}: {terms}, in-house {tiny.crews[row]}")
print("M from variable bounds:", m_from_variable_bounds(tiny)[row])
print("M from once rows:      ", m_from_once_rows(tiny)[row])
print("M by solving the MILP: ", m_by_solving(tiny, integer=True)[row])


def allows(plan: dict[str, int], big_m: int) -> bool:
    """Fix the plan and a hired contractor; does the model with this row's M accept it?"""
    m = {key: 100 for key in tiny.crews} | {row: big_m}
    cm = build(tiny, m)
    for (pid, t), var in cm.x.items():
        var.lower_bound = var.upper_bound = 1.0 if plan.get(pid) == t else 0.0
    cm.hire[row].lower_bound = 1.0
    return quiet_solve(cm.model).termination.reason == mathopt.TerminationReason.OPTIMAL


plan = {"P002": 2028, "P001": 2029}
for big_m in (1, 2):
    print(f"plan {plan} with a contractor and M = {big_m}: {'allowed' if allows(plan, big_m) else 'refused'}")
