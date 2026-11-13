import pytest

from violation import total_violation


def test_rows_that_agree_need_no_stretch():
    assert total_violation([([1, 1], "<=", 10), ([1, 0], ">=", 2), ([0, 1], ">=", 3)]) == pytest.approx(0, abs=1e-6)


def test_a_cap_below_a_floor_needs_the_gap():
    assert total_violation([([1, 1], "<=", 30), ([1, 1], ">=", 34)]) == pytest.approx(4)


def test_a_floor_row_can_be_the_one_that_stretches():
    rows = [([1], ">=", 5), ([1], "<=", 2), ([2], "<=", 4)]
    assert total_violation(rows) == pytest.approx(3)


def test_the_variables_stay_nonnegative():
    assert total_violation([([1, 1], "<=", -2)]) == pytest.approx(2)
