import math

import pytest
from scipy.stats import weibull_min


from breakers import chance_of_none, failures_by_year


def hazard_over(a: float, b: float, beta: float, eta: float) -> float:
    curve = weibull_min(c=beta, scale=eta)
    return curve.logsf(a) - curve.logsf(b)


def test_one_new_breaker_in_its_first_year():
    assert failures_by_year([0], 2.5, 30.0, 1) == pytest.approx([hazard_over(0, 1, 2.5, 30.0)], rel=1e-3)


def test_the_fleet_ages_each_year():
    ages = [10, 25, 40]
    expected = [sum(hazard_over(a + k, a + k + 1, 2.5, 35.0) for a in ages) for k in range(3)]
    assert failures_by_year(ages, 2.5, 35.0, 3) == pytest.approx(expected)


def test_a_worn_fleet_can_expect_more_than_one_failure_per_breaker():
    ages = [40, 45]
    got = failures_by_year(ages, 4.0, 20.0, 1)
    assert got == pytest.approx([sum(hazard_over(a, a + 1, 4.0, 20.0) for a in ages)])
    assert got[0] > len(ages)


def test_a_working_breaker_has_a_conditional_chance_of_no_failure():
    assert chance_of_none(25, 2.5, 35.0, 5) == pytest.approx(math.exp(-hazard_over(25, 30, 2.5, 35.0)))
