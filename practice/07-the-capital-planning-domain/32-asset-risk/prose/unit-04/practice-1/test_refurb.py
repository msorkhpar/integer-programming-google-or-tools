import pytest
from scipy.stats import weibull_min

from refurb import Pump, yearly_cut

YEARS = list(range(2027, 2035))
PUMP = Pump(35, 3.0, 40.0, 2.0, 60.0, 900.0)


def expected_failures(age, beta, eta):
    curve = weibull_min(c=beta, scale=eta)
    return curve.logsf(age) - curve.logsf(age + 1)


def test_nothing_is_removed_before_the_work_ends_and_something_after():
    cut = yearly_cut(PUMP, YEARS, 2028, 2)
    assert all(cut[y] == pytest.approx(0) for y in (2027, 2028, 2029))
    assert all(cut[y] > 0 for y in range(2030, 2035))


def test_the_new_unit_fails_on_its_own_curve():
    cut = yearly_cut(PUMP, YEARS, 2028, 1)
    before = 900 * expected_failures(35 + 2, 3.0, 40.0)
    assert cut[2029] == pytest.approx(before - 900 * expected_failures(0, 2.0, 60.0))


def test_the_new_unit_ages_after_installation():
    cut = yearly_cut(PUMP, YEARS, 2028, 1)
    before = 900 * expected_failures(35 + 5, 3.0, 40.0)
    assert cut[2032] == pytest.approx(before - 900 * expected_failures(3, 2.0, 60.0))


def test_without_the_work_the_old_pump_keeps_aging():
    cut = yearly_cut(PUMP, YEARS, 2027, 1)
    assert cut[2030] == pytest.approx(900 * expected_failures(38, 3.0, 40.0) - 900 * expected_failures(2, 2.0, 60.0))
