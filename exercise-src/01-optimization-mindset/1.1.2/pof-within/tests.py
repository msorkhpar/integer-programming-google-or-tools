import math

import pytest

from risk import cumulative, pof_within

LINE = dict(beta=2.2, eta=38.0)


def test_the_risk_is_a_probability_that_grows_with_the_window():
    risks = [pof_within(age=20, years=n, **LINE) for n in (1, 2, 3, 5, 10)]
    assert all(0 <= r <= 1 for r in risks)
    assert risks == sorted(risks) and risks[-1] > risks[0]


def test_a_zero_year_window_has_no_risk():
    assert pof_within(age=33, years=0, **LINE) == pytest.approx(0.0, abs=1e-12)


def test_an_old_survivor_is_riskier_than_its_curve_suggests():
    # At 70 most lines of this kind have long failed; this one has not.
    survived = 1 - cumulative(70, **LINE)
    expected = (cumulative(73, **LINE) - cumulative(70, **LINE)) / survived
    assert pof_within(age=70, years=3, **LINE) == pytest.approx(expected, rel=1e-9)


def test_a_multi_year_window_follows_the_curve_not_a_constant_rate():
    expected = 1 - math.exp(-((25 / 38.0) ** 2.2 - (20 / 38.0) ** 2.2))
    assert pof_within(age=20, years=5, **LINE) == pytest.approx(expected, rel=1e-9)
