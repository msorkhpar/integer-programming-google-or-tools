import pytest
from scipy.stats import weibull_min

from likelihood import log_likelihood


def expected(beta, eta, failed, working):
    curve = weibull_min(c=beta, scale=eta)
    return sum(curve.logpdf(t) for t in failed) + sum(curve.logsf(c) for c in working)


def test_with_every_unit_failed_it_is_the_sum_of_log_densities():
    failed = [12.0, 25.0, 31.0, 40.0]
    assert log_likelihood(2.5, 30.0, failed, []) == pytest.approx(expected(2.5, 30.0, failed, []))


def test_a_unit_still_working_adds_the_log_of_its_survival():
    failed, working = [20.0], [30.0, 35.0]
    assert log_likelihood(3.0, 40.0, failed, working) == pytest.approx(expected(3.0, 40.0, failed, working))


def test_the_true_curve_scores_higher_than_a_young_dying_one():
    failed = [18.0, 22.0, 26.0, 29.0, 31.0, 33.0, 34.0]
    working = [35.0] * 20
    assert log_likelihood(3.0, 45.0, failed, working) > log_likelihood(4.4, 27.6, failed, working)
