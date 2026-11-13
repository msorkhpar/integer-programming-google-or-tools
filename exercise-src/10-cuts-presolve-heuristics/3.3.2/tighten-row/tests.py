import pytest

from tighten import tighten


def test_one_dominant_coefficient_is_lowered():
    coefs, rhs = tighten({"a": 5, "b": 2, "c": 2}, 6)
    assert coefs == pytest.approx({"a": 3, "b": 2, "c": 2}) and rhs == pytest.approx(4)


def test_a_row_where_one_change_is_enough():
    coefs, rhs = tighten({"a": 9, "b": 2, "c": 3}, 10)
    assert coefs == pytest.approx({"a": 4, "b": 2, "c": 3}) and rhs == pytest.approx(5)


def test_each_change_lowers_the_most_activity_for_the_next():
    coefs, rhs = tighten({"a": 4, "b": 3, "c": 3}, 8)
    assert coefs == pytest.approx({"a": 2, "b": 2, "c": 2}) and rhs == pytest.approx(4)


def test_the_callers_row_is_left_unchanged():
    row = {"q": 6, "r": 1, "s": 1}
    coefs, rhs = tighten(row, 7)
    assert coefs == pytest.approx({"q": 1, "r": 1, "s": 1}) and rhs == pytest.approx(2)
    assert row == {"q": 6, "r": 1, "s": 1}
