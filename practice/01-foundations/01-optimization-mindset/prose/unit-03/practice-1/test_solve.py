import pytest

from solve import Project, solve_plan

QUAYS = [
    Project("Q1", 25, 30, must_do=True),
    Project("Q2", 30, 54),
    Project("Q3", 20, 34),
    Project("Q4", 15, 24),
    Project("Q5", 10, 15),
]
OPEN = [Project(p.pid, p.cost, p.value) for p in QUAYS]


def test_the_best_plan_and_its_value_come_back_with_status_optimal():
    assert solve_plan(OPEN, 30) == ("OPTIMAL", pytest.approx(54), frozenset({"Q2"}))


def test_a_budget_below_the_must_do_cost_is_infeasible_with_no_value_and_no_plan():
    assert solve_plan(QUAYS, 25)[0] == "OPTIMAL"
    assert solve_plan(QUAYS, 20) == ("INFEASIBLE", None, None)


def test_the_must_do_project_is_funded_even_when_others_are_worth_more():
    assert solve_plan(OPEN, 60)[1] == pytest.approx(103)
    assert solve_plan(QUAYS, 60) == ("OPTIMAL", pytest.approx(88), frozenset({"Q1", "Q3", "Q4"}))


def test_each_project_is_funded_whole_or_not_at_all():
    status, value, plan = solve_plan(QUAYS, 60)
    assert status == "OPTIMAL"
    assert value == pytest.approx(sum(p.value for p in QUAYS if p.pid in plan))
