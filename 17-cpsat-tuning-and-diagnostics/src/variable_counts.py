"""Lesson 4.6.4: why the response summary can count more integers than Booleans.

Three tiny models over five Booleans, solved with one worker and presolve off so the counts are the
model's own: a clause only, a weighted linear row, and the same row with a weighted objective.
"""

from ortools.sat.python import cp_model


def counts(label: str, row: bool, objective: bool) -> None:
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x{i}") for i in range(5)]
    model.add_bool_or(x)
    if row:
        model.add(sum((i + 2) * v for i, v in enumerate(x)) <= 9)
    if objective:
        model.maximize(sum((i + 3) * v for i, v in enumerate(x)))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.cp_model_presolve = False
    solver.solve(model)
    response = solver.response_proto
    print(f"{label:<34} booleans {response.num_booleans}  integers {response.num_integers}")


counts("5 Booleans, one clause", row=False, objective=False)
counts("+ a weighted linear row", row=True, objective=False)
counts("+ a weighted objective", row=True, objective=True)
