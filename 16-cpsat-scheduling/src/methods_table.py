"""Lesson 4.5.3: a table of allowed (method, who, weeks, cost) rows, one table per job.

GridCap's own crew has no aerial saw; the contractor has no climbers and charges $15k more for a
mechanical job. The table both forbids the combinations nobody offers and fixes weeks and cost
for the ones that exist. Each job is then an optional interval on the crew that does it.
GridCap is fictional, and so are the method data.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve
from methods_element import DATA, METHODS

MANUAL, MECHANICAL, AERIAL = range(3)
OWN, CONTRACTOR = 0, 1


def rows(w: list[int], c: list[int]) -> list[tuple[int, int, int, int]]:
    """Allowed (method, who, weeks, cost) for a job with weeks w and in-house costs c by method."""
    return [(MANUAL, OWN, w[MANUAL], c[MANUAL]),
            (MECHANICAL, OWN, w[MECHANICAL], c[MECHANICAL]),
            (MECHANICAL, CONTRACTOR, w[MECHANICAL], c[MECHANICAL] + 15),
            (AERIAL, CONTRACTOR, w[AERIAL], c[AERIAL])]


def plan(deadline: int) -> None:
    model = cp_model.CpModel()
    method, hired, weeks, cost = {}, {}, {}, {}
    on = {OWN: [], CONTRACTOR: []}
    for j, (w, c) in DATA.items():
        method[j] = model.new_int_var(0, len(METHODS) - 1, f"method_{j}")
        hired[j] = model.new_bool_var(f"contractor_does_{j}")
        weeks[j] = model.new_int_var(min(w), max(w), f"weeks_{j}")
        cost[j] = model.new_int_var(0, 1_000, f"cost_{j}")
        model.add_allowed_assignments([method[j], hired[j], weeks[j], cost[j]], rows(w, c))
        start = model.new_int_var(0, deadline, f"start_{j}")
        end = model.new_int_var(0, deadline, f"end_{j}")
        on[OWN].append(model.new_optional_interval_var(start, weeks[j], end, ~hired[j], f"{j}_own"))
        on[CONTRACTOR].append(model.new_optional_interval_var(start, weeks[j], end, hired[j], f"{j}_hired"))
    model.add_no_overlap(on[OWN])
    model.add_no_overlap(on[CONTRACTOR])
    model.minimize(sum(cost.values()))
    solver, status = solve(model)
    if status != "OPTIMAL":
        print(f"deadline week {deadline}: {status}")
        return
    print(f"deadline week {deadline}: {status}, cost ${solver.objective_value:.0f}k")
    for j in DATA:
        who = "contractor" if solver.boolean_value(hired[j]) else "own crew"
        print(f"  {j} {METHODS[solver.value(method[j])]:<10} {who:<10} weeks {solver.value(weeks[j])}  ${solver.value(cost[j])}k")


for deadline in (8, 4, 3, 2):
    plan(deadline)
