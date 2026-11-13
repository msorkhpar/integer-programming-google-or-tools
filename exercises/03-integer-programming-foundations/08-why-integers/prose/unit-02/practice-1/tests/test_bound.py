import pytest

from bound import Project, fractional_bound

SHOPS = [Project("A", 30, 60), Project("B", 40, 56), Project("C", 50, 55), Project("D", 20, 18)]


def test_projects_are_funded_best_value_per_dollar_first_until_the_budget_is_spent():
    assert fractional_bound(SHOPS, 120) == pytest.approx(171)


def test_the_first_project_that_does_not_fit_is_funded_in_part():
    assert fractional_bound(SHOPS, 100) == pytest.approx(60 + 56 + 0.6 * 55)


def test_the_order_is_value_per_dollar_not_value():
    depots = [Project("E", 60, 66), Project("F", 20, 30), Project("G", 30, 39)]
    assert fractional_bound(depots, 70) == pytest.approx(30 + 39 + 66 / 3)


def test_must_do_projects_are_paid_for_first_and_in_full():
    shops = [Project("A", 30, 60), Project("B", 40, 56), Project("C", 50, 55, must_do=True), Project("D", 20, 18)]
    assert fractional_bound(shops, 100) == pytest.approx(55 + 60 + 0.5 * 56)
