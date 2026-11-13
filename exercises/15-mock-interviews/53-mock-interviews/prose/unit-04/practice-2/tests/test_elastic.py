import pytest
from ortools.math_opt.python import mathopt

from elastic import Project, build

# A transit agency's capital projects, not the lessons' portfolio.
PROJECTS = [
    Project("M1", 2027, 80, must_do=True),
    Project("M2", 2028, 90, must_do=True),
    Project("F1", 2027, 40),
    Project("F2", 2028, 30),
    Project("F3", 2027, 30),
]
EVEN = {2027: 1.0, 2028: 1.0}


def least_repair(budgets, penalty, plan=None):
    """Solve the elastic model, with the plan fixed if one is given; return the status and the penalty."""
    model, x = build(PROJECTS, budgets, penalty)
    if plan is not None:
        for pid, var in x.items():
            var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return result.termination.reason.name, None
    return "OPTIMAL", result.objective_value()


def test_a_plan_within_budgets_needs_no_repair_and_an_overspend_is_priced():
    budgets = {2027: 80, 2028: 90}
    assert least_repair(budgets, EVEN, {"M1", "M2"}) == ("OPTIMAL", pytest.approx(0.0))
    assert least_repair(budgets, EVEN, {"M1", "M2", "F1"}) == ("OPTIMAL", pytest.approx(40.0))


def test_an_over_committed_scenario_still_has_a_cheapest_repair():
    assert least_repair({2027: 50, 2028: 50}, EVEN) == ("OPTIMAL", pytest.approx(70.0))


def test_an_underspent_year_earns_no_credit():
    assert least_repair({2027: 100, 2028: 200}, EVEN, {"M1", "M2", "F1"}) == ("OPTIMAL", pytest.approx(20.0))


def test_an_overspend_larger_than_the_budget_is_still_priced():
    assert least_repair({2027: 10, 2028: 90}, EVEN, {"M1", "M2"}) == ("OPTIMAL", pytest.approx(70.0))
    assert least_repair({2027: 10, 2028: 90}, EVEN, {"M1", "M2", "F1"}) == ("OPTIMAL", pytest.approx(110.0))


def test_each_year_has_its_own_price():
    assert least_repair({2027: 100, 2028: 100}, {2027: 1.0, 2028: 3.0}, {"M1", "M2", "F2"}) == (
        "OPTIMAL", pytest.approx(60.0))
