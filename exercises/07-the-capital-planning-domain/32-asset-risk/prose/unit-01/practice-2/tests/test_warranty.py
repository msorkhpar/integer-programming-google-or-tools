import pytest
from scipy.stats import weibull_min

from warranty import required_scale


def test_a_stricter_promise_needs_a_longer_life():
    scales = [required_scale(6, share, 2.0) for share in (0.2, 0.1, 0.02)]
    assert scales[0] < scales[1] < scales[2]


def test_with_shape_one_the_promise_is_met_exactly():
    eta = required_scale(5, 0.2, 1.0)
    assert weibull_min(c=1.0, scale=eta).cdf(5) == pytest.approx(0.2)


def test_a_wear_out_design_meets_the_promise_exactly():
    eta = required_scale(8, 0.05, 3.2)
    assert weibull_min(c=3.2, scale=eta).cdf(8) == pytest.approx(0.05)
