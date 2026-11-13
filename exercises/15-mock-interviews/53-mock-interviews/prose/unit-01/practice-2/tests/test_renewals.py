from ortools.math_opt.python import mathopt

from renewals import Renewal, build

# A water utility's pipe renewals, not the lessons' portfolio.
RENEWALS = [
    Renewal("R1", (2027, 2028), (40, 40)),
    Renewal("R2", (2027, 2028, 2029), (50,)),
    Renewal("R3", (2027, 2028), (30, 30, 30)),
    Renewal("R4", (2028, 2029, 2030), (20,), parent="R1", lag=2),
    Renewal("R5", (2028, 2029), (40,), group="M4"),
    Renewal("R6", (2028, 2029), (50,), group="M4"),
]
BUDGETS = {2027: 100, 2028: 100, 2029: 100, 2030: 100}


def allowed(plan: dict[str, int]) -> bool:
    """Fix every start variable to the plan (renewal -> start year) and ask whether the model accepts it."""
    model, x = build(RENEWALS, BUDGETS)
    for (rid, t), var in x.items():
        value = 1.0 if plan.get(rid) == t else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_spending_within_every_budget_is_allowed_and_an_overspent_year_refused():
    assert allowed({"R1": 2027, "R2": 2029}) is True
    assert allowed({"R1": 2027, "R2": 2027, "R3": 2027}) is False


def test_at_most_one_alternative_of_a_main():
    assert allowed({"R5": 2028}) is True
    assert allowed({"R5": 2028, "R6": 2028}) is False


def test_a_child_starts_its_lag_after_its_parent():
    assert allowed({"R1": 2027, "R4": 2030}) is True
    assert allowed({"R1": 2028, "R4": 2029}) is False


def test_cost_is_charged_in_each_year_of_work():
    assert allowed({"R1": 2027, "R3": 2027}) is True
    assert allowed({"R1": 2027, "R3": 2027, "R2": 2028}) is False


def test_alternatives_in_different_years_are_still_refused():
    assert allowed({"R6": 2029}) is True
    assert allowed({"R5": 2028, "R6": 2029}) is False


def test_a_child_may_start_exactly_its_lag_after_its_parent():
    assert allowed({"R1": 2027, "R4": 2029}) is True
    assert allowed({"R1": 2028, "R4": 2029}) is False


def test_a_child_without_its_parent_is_refused():
    assert allowed({"R1": 2027, "R4": 2030}) is True
    assert allowed({"R4": 2029}) is False
