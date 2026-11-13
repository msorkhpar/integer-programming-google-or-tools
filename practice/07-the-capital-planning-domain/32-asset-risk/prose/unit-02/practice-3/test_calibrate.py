import pytest
from scipy.stats import weibull_min

from calibrate import scale_from_report


def test_a_median_report_for_a_new_unit_becomes_its_median_life():
    eta = scale_from_report(0, 10.0, 0.5, 2.0)
    assert weibull_min(c=2.0, scale=eta).median() == pytest.approx(10.0)


def test_a_p10_report_is_a_ten_percent_chance():
    eta = scale_from_report(0, 3.0, 0.1, 2.0)
    assert weibull_min(c=2.0, scale=eta).cdf(3.0) == pytest.approx(0.1)


def test_the_chance_is_counted_from_todays_age():
    eta = scale_from_report(25, 6.0, 0.1, 3.5)
    curve = weibull_min(c=3.5, scale=eta)
    assert curve.sf(31.0) / curve.sf(25.0) == pytest.approx(0.9)
