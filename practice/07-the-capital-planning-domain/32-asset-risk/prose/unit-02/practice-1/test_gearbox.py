import pytest
from scipy.stats import weibull_min

from gearbox import years_until


def test_a_new_gearbox_reaches_one_half_at_the_median_life():
    assert years_until(0, 0.5, 2.8, 25.0) == pytest.approx(weibull_min(c=2.8, scale=25.0).median())


def test_the_years_are_counted_from_today():
    curve = weibull_min(c=2.8, scale=25.0)
    r = years_until(12, 0.5, 2.8, 25.0)
    assert curve.sf(12 + r) / curve.sf(12) == pytest.approx(0.5)


def test_the_chance_is_given_that_it_works_today():
    curve = weibull_min(c=3.5, scale=30.0)
    r = years_until(15, 0.2, 3.5, 30.0)
    assert curve.sf(15 + r) / curve.sf(15) == pytest.approx(0.8)


def test_the_level_is_a_chance_of_failing():
    assert years_until(0, 0.1, 2.8, 25.0) == pytest.approx(weibull_min(c=2.8, scale=25.0).ppf(0.1))
