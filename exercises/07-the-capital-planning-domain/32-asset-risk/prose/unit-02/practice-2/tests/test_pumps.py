import pytest
from scipy.stats import weibull_min

from pumps import mean_remaining_life


def scipy_mean_remaining(age, beta, eta):
    return weibull_min(c=beta, scale=eta).expect(lambda t: t, lb=age, conditional=True) - age


def test_a_new_pump_has_the_mean_life_of_its_kind():
    assert mean_remaining_life(0, 2.5, 40.0) == pytest.approx(weibull_min(c=2.5, scale=40.0).mean(), rel=1e-6)


def test_the_average_is_over_pumps_still_working():
    assert mean_remaining_life(30, 2.5, 40.0) == pytest.approx(scipy_mean_remaining(30, 2.5, 40.0), rel=1e-6)


def test_the_life_ahead_starts_at_todays_age():
    assert mean_remaining_life(20, 3.0, 25.0) == pytest.approx(scipy_mean_remaining(20, 3.0, 25.0), rel=1e-6)


def test_a_flat_failure_rate_has_no_memory():
    assert mean_remaining_life(35, 1.0, 18.0) == pytest.approx(18.0, rel=1e-6)


def test_an_old_pump_does_not_underflow():
    # At age 200 the hazard is 3/20 * (200/20)**2 = 15 a year and barely changes over a few weeks,
    # so the mean remaining life is just under 1/15 of a year. R(200) itself underflows to 0.
    assert mean_remaining_life(200, 3.0, 20.0) == pytest.approx(1 / 15, rel=2e-3)
