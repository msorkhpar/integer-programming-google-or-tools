import numpy_financial as npf
import pytest

from crossover import crossover_rate

RAISE = [-600] + [100] * 10
BARRIER = [-600] + [220] * 4


def test_the_rate_where_the_two_values_are_equal_is_found():
    barrier = BARRIER + [0] * 6
    rate = crossover_rate(RAISE, barrier)
    assert npf.npv(rate, RAISE) == pytest.approx(npf.npv(rate, barrier), abs=1e-3)
    assert rate == pytest.approx(npf.irr([x - y for x, y in zip(RAISE, barrier)]), abs=1e-6)


def test_options_of_different_lengths_are_compared_in_full():
    rate = crossover_rate(RAISE, BARRIER)
    assert rate == pytest.approx(npf.irr([x - y for x, y in zip(RAISE, BARRIER + [0] * 6)]), abs=1e-6)


def test_the_first_option_may_be_the_worse_one_at_low_rates():
    barrier = BARRIER + [0] * 6
    rate = crossover_rate(barrier, RAISE)
    assert rate == pytest.approx(npf.irr([x - y for x, y in zip(barrier, RAISE)]), abs=1e-6)
    assert 0.0 < rate < 1.0
