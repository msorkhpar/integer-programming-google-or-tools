import pytest
from scipy.stats import weibull_min

from relays import trigger_age


def failure_rate(t: float, beta: float, eta: float) -> float:
    curve = weibull_min(c=beta, scale=eta)
    return curve.pdf(t) / curve.sf(t)


def test_a_higher_rate_is_reached_later():
    ages = [trigger_age(rate, 3.0, 30.0) for rate in (0.01, 0.05, 0.2)]
    assert 0 < ages[0] < ages[1] < ages[2]


def test_at_the_trigger_age_the_failure_rate_equals_the_limit():
    for beta, eta, rate in ((2.0, 25.0, 0.04), (3.5, 40.0, 0.1), (1.5, 60.0, 0.02)):
        t = trigger_age(rate, beta, eta)
        assert failure_rate(t, beta, eta) == pytest.approx(rate, rel=1e-6)


def test_a_falling_or_flat_failure_rate_never_triggers():
    assert trigger_age(0.05, 0.8, 30.0) is None
    assert trigger_age(0.05, 1.0, 30.0) is None
