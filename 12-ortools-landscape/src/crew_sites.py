# Adapted from the OR-Tools example assignment_linear_sum_assignment.py,
# https://github.com/google/or-tools/blob/v9.15/ortools/graph/samples/assignment_linear_sum_assignment.py (Apache-2.0)
"""Four GridCap crews to four substations, with the assignment solver and with CP-SAT (lesson 4.1.1).

GridCap is fictional; so are these travel hours.
"""

from __future__ import annotations

from ortools.graph.python import linear_sum_assignment
from ortools.sat.python import cp_model

crews = ["Ridge crew", "Valley crew", "Coast crew", "Plains crew"]
sites = ["S1 Hilltop", "S2 Riverside", "S3 Harbor", "S4 Prairie"]
hours = [            # hours[k][s]: travel hours for crew k to reach site s
    [4, 3, 9, 6],
    [2, 5, 6, 7],
    [7, 3, 4, 8],
    [5, 6, 8, 6],
]


def with_assignment_solver() -> tuple[int, list[int]]:
    solver = linear_sum_assignment.SimpleLinearSumAssignment()
    for k in range(len(crews)):
        for s in range(len(sites)):
            solver.add_arc_with_cost(k, s, hours[k][s])
    status = solver.solve()
    assert status == solver.OPTIMAL, status
    return solver.optimal_cost(), [solver.right_mate(k) for k in range(len(crews))]


def with_cp_sat() -> tuple[int, list[int]]:
    model = cp_model.CpModel()
    y = {(k, s): model.new_bool_var(f"y_{k}_{s}") for k in range(len(crews)) for s in range(len(sites))}
    for k in range(len(crews)):
        model.add_exactly_one(y[k, s] for s in range(len(sites)))        # each crew gets one site
    for s in range(len(sites)):
        model.add_exactly_one(y[k, s] for k in range(len(crews)))        # each site gets one crew
    model.minimize(sum(hours[k][s] * y[k, s] for (k, s) in y))
    solver = cp_model.CpSolver()
    solver.solve(model)
    return int(solver.objective_value), [next(s for s in range(len(sites)) if solver.value(y[k, s]))
                                         for k in range(len(crews))]


for label, (total, site_of) in (("assignment solver", with_assignment_solver()), ("CP-SAT", with_cp_sat())):
    pairs = ", ".join(f"{crews[k].split()[0]}->{sites[s].split()[0]}" for k, s in enumerate(site_of))
    print(f"{label:<17} {total} hours  {pairs}")

# The assignment solver's verdict: a status from solve(), never an exception.
print("statuses:", ", ".join(linear_sum_assignment.SimpleLinearSumAssignment.Status.__members__))
stuck = linear_sum_assignment.SimpleLinearSumAssignment()
stuck.add_arc_with_cost(0, 0, 4)                 # two crews, and both cleared only for site 0
stuck.add_arc_with_cost(1, 0, 2)
status = stuck.solve()
print("two crews, one usable site:", status.name, "| status == stuck.OPTIMAL:", status == stuck.OPTIMAL)
