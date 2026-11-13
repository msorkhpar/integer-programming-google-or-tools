import math

import pytest

from sgm import shifted_geometric_mean


def test_with_no_shift_it_is_the_geometric_mean():
    assert shifted_geometric_mean([2.0, 8.0], 0.0) == pytest.approx(4.0)
    assert shifted_geometric_mean([1.0, 10.0, 100.0], 0.0) == pytest.approx(10.0)


def test_the_shift_is_added_then_subtracted():
    want = (10.5 * 14.0 * 130.0) ** (1 / 3) - 10.0
    assert shifted_geometric_mean([0.5, 4.0, 120.0], 10.0) == pytest.approx(want)
    assert shifted_geometric_mean([7.0, 7.0, 7.0], 10.0) == pytest.approx(7.0)


def test_tiny_values_are_floored_at_one_inside_the_log():
    # 0.01 and 0.1 both count as 1 when the shift is 0, so the mean is 1 - 0 = 1.
    assert shifted_geometric_mean([0.01, 0.1], 0.0) == pytest.approx(1.0)
    assert shifted_geometric_mean([0.01, 99.0], 1.0) == pytest.approx(math.sqrt(1.01 * 100.0) - 1.0)


def test_a_bigger_shift_shrinks_the_ratio_of_two_solvers():
    fast = [0.01, 0.01, 50.0, 50.0]
    slow = [0.1, 0.1, 50.0, 50.0]
    small = shifted_geometric_mean(slow, 1.0) / shifted_geometric_mean(fast, 1.0)
    large = shifted_geometric_mean(slow, 10.0) / shifted_geometric_mean(fast, 10.0)
    assert small == pytest.approx(1.0507, abs=1e-3)
    assert large == pytest.approx(1.0076, abs=1e-3)
