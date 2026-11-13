import pytest
from scipy.stats import weibull_min

from coefficients import Main, coefficients

MAIN = Main(48, 2.8, 45.0, 1_200.0)
CURVE = weibull_min(c=2.8, scale=45.0)


def expected_failures(age):
    return CURVE.logsf(age) - CURVE.logsf(age + 1)


def reduction(start, year, duration=2, first=2027):
    """The risk removed in `year` by a replacement (keep 0) started in `start`."""
    done = start + duration
    old = MAIN.age + (year - first)
    return 0.0 if year < done else 1_200 * (expected_failures(old) - expected_failures(year - done))


def test_a_first_year_start_undiscounted_sums_its_service_years():
    got = coefficients(MAIN, [2027], 2027, 2, 0.0, 6, 0.0)
    assert got[2027] == pytest.approx(sum(reduction(2027, y) for y in range(2029, 2035)))


def test_a_later_start_counts_as_many_service_years():
    got = coefficients(MAIN, [2027, 2029], 2027, 2, 0.0, 6, 0.0)
    assert got[2029] == pytest.approx(sum(reduction(2029, y) for y in range(2031, 2037)))


def test_every_start_is_discounted_to_the_plans_first_year():
    got = coefficients(MAIN, [2028], 2027, 2, 0.0, 4, 0.08)
    assert got[2028] == pytest.approx(sum(reduction(2028, y) / 1.08 ** (y - 2027) for y in range(2030, 2034)))


def test_discounting_compounds_each_year():
    got = coefficients(MAIN, [2027], 2027, 2, 0.0, 8, 0.10)
    assert got[2027] == pytest.approx(sum(reduction(2027, y) / 1.10 ** (y - 2027) for y in range(2029, 2037)))
