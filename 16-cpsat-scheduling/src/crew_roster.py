"""Lesson 4.5.3: an eight-week roster for three crews, adapted from the nurses example.

Each crew is in exactly one place each week (a region or the yard), each region gets the crews its
work needs, and each crew spends at least one week in the yard for equipment service. A crew's
place is an integer at[c, w]; moving between two places costs travel, read by Element from a
5 x 5 table, and Coast to Ridge (or back) in one week is a forbidden pair.
Adapted from the OR-Tools "Employee Scheduling" example,
https://developers.google.com/optimization/scheduling/employee_scheduling, and the forbidden
transitions of examples/python/shift_scheduling_sat.py. GridCap is fictional.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve

PLACES = ["Ridge", "Valley", "Coast", "Plains", "yard"]
RIDGE, VALLEY, COAST, PLAINS, YARD = range(5)
CREWS, WEEKS = ["A", "B", "C"], range(8)
NEED = [{COAST: 2, PLAINS: 1}, {COAST: 2, PLAINS: 1}, {RIDGE: 1, COAST: 1, PLAINS: 1},
        {RIDGE: 2, VALLEY: 1}, {RIDGE: 1, VALLEY: 1}, {VALLEY: 2}, {VALLEY: 1, RIDGE: 1}, {COAST: 1, RIDGE: 1}]
TRAVEL = [[0, 3, 6, 4, 2],      # $k to move one crew from the row's place to the column's place
          [3, 0, 3, 3, 2],
          [6, 3, 0, 4, 2],
          [4, 3, 4, 0, 2],
          [2, 2, 2, 2, 0]]
FLAT = [TRAVEL[p][q] for p in range(5) for q in range(5)]


def roster(forbid_coast_ridge: bool) -> None:
    model = cp_model.CpModel()
    there = {(c, w, p): model.new_bool_var(f"{c}_w{w}_{PLACES[p]}") for c in CREWS for w in WEEKS for p in range(5)}
    at = {}
    for c in CREWS:
        for w in WEEKS:
            model.add_exactly_one(there[c, w, p] for p in range(5))
            at[c, w] = model.new_int_var(0, 4, f"at_{c}_w{w}")
            model.add(at[c, w] == sum(p * there[c, w, p] for p in range(5)))
        model.add(sum(there[c, w, YARD] for w in WEEKS) >= 1)
    for w in WEEKS:
        for p in range(4):
            model.add(sum(there[c, w, p] for c in CREWS) == NEED[w].get(p, 0))

    moves = []
    for c in CREWS:
        for w in WEEKS[:-1]:
            if forbid_coast_ridge:
                model.add_forbidden_assignments([at[c, w], at[c, w + 1]], [(COAST, RIDGE), (RIDGE, COAST)])
            move = model.new_int_var(0, max(FLAT), f"travel_{c}_w{w}")
            model.add_element(5 * at[c, w] + at[c, w + 1], FLAT, move)
            moves.append(move)
    model.minimize(sum(moves))

    solver, status = solve(model)
    print(f"{'Coast-Ridge forbidden' if forbid_coast_ridge else 'every move allowed'}: {status}, "
          f"travel ${solver.objective_value:.0f}k")
    for c in CREWS:
        print(f"  crew {c}: " + " ".join(f"{PLACES[solver.value(at[c, w])]:<6}" for w in WEEKS))


roster(forbid_coast_ridge=False)
roster(forbid_coast_ridge=True)
