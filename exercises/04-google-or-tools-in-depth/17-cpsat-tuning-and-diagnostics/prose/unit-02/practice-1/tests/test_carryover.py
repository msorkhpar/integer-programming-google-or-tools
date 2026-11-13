from ortools.sat.python import cp_model

from carryover import add_plan_hint, build, fits

# A cooperative's pole-replacement batches, not the lesson's portfolio.
COSTS = {"A": 40, "B": 30, "C": 50, "D": 20}
VALUES = {"A": 70, "B": 60, "C": 50, "D": 45}
MUST = {"C"}
BUDGET = 90


def test_a_plan_within_budget_fits_and_one_over_budget_does_not():
    assert fits(COSTS, VALUES, MUST, BUDGET, {"C", "D"}) is True
    assert fits(COSTS, VALUES, MUST, BUDGET, {"A", "B", "C"}) is False


def test_fixing_to_the_hint_reproduces_the_plan():
    model, pick = build(COSTS, VALUES, MUST, BUDGET)
    add_plan_hint(model, pick, {"B", "C"})
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.fix_variables_to_their_hinted_value = True
    assert solver.solve(model) == cp_model.OPTIMAL
    assert {p for p, var in pick.items() if solver.value(var)} == {"B", "C"}


def test_a_plan_missing_a_must_do_does_not_fit():
    assert fits(COSTS, VALUES, MUST, BUDGET, {"C"}) is True
    assert fits(COSTS, VALUES, MUST, BUDGET, {"A"}) is False
