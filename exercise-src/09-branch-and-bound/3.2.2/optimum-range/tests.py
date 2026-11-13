import pytest

from optimum_range import optimum_range


def test_the_range_runs_from_the_incumbent_to_the_largest_waiting_bound():
    assert optimum_range(50.0, [70.0, 64.0]) == (50.0, 70.0, False)


def test_with_nothing_waiting_the_incumbent_is_proven():
    assert optimum_range(50.0, []) == (50.0, 50.0, True)


def test_the_search_is_proven_once_the_ends_meet():
    low, high, proven = optimum_range(50.0, [50.0000001, 50.0])
    assert low == 50.0 and high == pytest.approx(50.0) and proven
    assert optimum_range(50.0, [50.5])[2] is False


def test_before_the_first_plan_there_is_no_lower_end():
    assert optimum_range(None, [70.0, 64.0]) == (None, 70.0, False)
    assert optimum_range(None, []) == (None, None, False)


def test_waiting_bounds_below_the_incumbent_do_not_lower_the_upper_end():
    assert optimum_range(80.0, [70.0, 64.0]) == (80.0, 80.0, True)
