"""Lesson 4.1.1's crew assignment, then two new rules: one the assignment solver can take, one it cannot
(lesson 4.1.3). GridCap is fictional; so are these travel hours.
"""

from __future__ import annotations

from ortools.graph.python import linear_sum_assignment
from ortools.sat.python import cp_model

crews = ["Ridge", "Valley", "Coast", "Plains"]
sites = ["S1", "S2", "S3", "S4"]
hours = [[4, 3, 9, 6], [2, 5, 6, 7], [7, 3, 4, 8], [5, 6, 8, 6]]
K, S = range(len(crews)), range(len(sites))


def assignment_solver(forbidden: set[tuple[int, int]]) -> str:
    solver = linear_sum_assignment.SimpleLinearSumAssignment()
    for k in K:
        for s in S:
            if (k, s) not in forbidden:                 # a pair it may not use is an arc never added
                solver.add_arc_with_cost(k, s, hours[k][s])
    if solver.solve() != solver.OPTIMAL:
        return "no assignment"
    return show(solver.optimal_cost(), [solver.right_mate(k) for k in K])


def cp_sat(forbidden: set[tuple[int, int]], truck_limit: int | None) -> str:
    model = cp_model.CpModel()
    y = {(k, s): model.new_bool_var(f"y_{crews[k]}_{sites[s]}") for k in K for s in S if (k, s) not in forbidden}
    for k in K:
        model.add_exactly_one(y[k, s] for s in S if (k, s) in y)            # one_site_k
    for s in S:
        model.add_exactly_one(y[k, s] for k in K if (k, s) in y)            # one_crew_s
    if truck_limit is not None:                                             # truck: Coast + Plains hours
        model.add(sum(hours[k][s] * y[k, s] for (k, s) in y if crews[k] in ("Coast", "Plains")) <= truck_limit)
    model.minimize(sum(hours[k][s] * y[k, s] for (k, s) in y))
    solver = cp_model.CpSolver()
    if solver.solve(model) != cp_model.OPTIMAL:
        return "no assignment"
    return show(int(solver.objective_value), [next(s for s in S if (k, s) in y and solver.value(y[k, s])) for k in K])


def show(total: int, site_of: list[int]) -> str:
    return f"{total} hours  " + ", ".join(f"{crews[k]}->{sites[s]}" for k, s in enumerate(site_of))


no_ridge_s2 = {(0, 1)}                                  # the Ridge crew is not cleared for S2
print("as in lesson 4.1.1")
print("  assignment solver:", assignment_solver(set()))
print("  CP-SAT:           ", cp_sat(set(), None))
print("Ridge not cleared for S2")
print("  assignment solver:", assignment_solver(no_ridge_s2))
print("  CP-SAT:           ", cp_sat(no_ridge_s2, None))
print("and Coast + Plains share a truck: at most 9 hours between them")
print("  CP-SAT:           ", cp_sat(no_ridge_s2, 9))
builders = [m for m in dir(linear_sum_assignment.SimpleLinearSumAssignment) if m.startswith("add_")]
print("  assignment solver: its only ways to add data are", " and ".join(builders))
