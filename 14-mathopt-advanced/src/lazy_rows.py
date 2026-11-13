"""A rule added only when a solution breaks it: lazy constraints from a MIP_SOLUTION callback.

The pattern follows the OR-Tools example `tsp.py`, which checks each integer solution in a callback
and adds the cutset rows it violates, with `add_lazy_constraints=True`,
https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/tsp.py
That example solves with Gurobi; here the same pattern runs on the solvers the runner has.
"""

from collections import Counter

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, plan, refusal, solve

small = generate("small")
CREWS = 2                       # at most 2 transmission projects may start in the same year
TRANSMISSION = [p.project_id for p in small.projects if p.program == "transmission"]


def starts_per_year(chosen: dict[str, int]) -> dict[int, int]:
    return dict(sorted(Counter(t for pid, t in chosen.items() if pid in TRANSMISSION).items()))


def crew_row(pm, year: int):
    return mathopt.fast_sum(pm.x[pid, year] for pid in TRANSMISSION if (pid, year) in pm.x) <= CREWS


# Every row up front: one per year.
pm = build(small)
print("without the rule:", starts_per_year(plan(pm, solve(pm.model).variable_values())))
for y in small.years:
    pm.model.add_linear_constraint(crew_row(pm, y), name=f"crews_{y}")
upfront = solve(pm.model)
print(f"rows up front  HIGHS   NPV {upfront.objective_value():,.0f}"
      f"  starts {starts_per_year(plan(pm, upfront.variable_values()))}")

# The same rule, added only for the years a solution breaks.
for solver in (mathopt.SolverType.GSCIP, mathopt.SolverType.HIGHS, mathopt.SolverType.CP_SAT):
    pm = build(small)
    added = []

    def check(data: mathopt.CallbackData) -> mathopt.CallbackResult:
        result = mathopt.CallbackResult()
        for year, count in starts_per_year(plan(pm, data.solution)).items():
            if count > CREWS:
                result.add_lazy_constraint(crew_row(pm, year))
                added.append(year)
        return result

    registration = mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION}, add_lazy_constraints=True)
    try:
        result = solve(pm.model, solver, callback_reg=registration, cb=check)
        chosen = plan(pm, result.variable_values())
        print(f"lazy rows      {solver.name:6}  NPV {result.objective_value():,.0f}"
              f"  starts {starts_per_year(chosen)}  rows sent {len(added)}")
    except Exception as error:
        print(f"lazy rows      {solver.name:6}  refused: {refusal(error)}")
