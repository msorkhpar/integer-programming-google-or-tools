import pytest

from simplex import run_simplex


def test_a_bounded_lp_ends_optimal_with_its_value():
    T = [[1, 1, 1, 0, 0, 4],
         [1, 3, 0, 1, 0, 6],
         [1, 0, 0, 0, 1, 3],
         [-3, -2, 0, 0, 0, 0]]
    assert run_simplex(T) == ("OPTIMAL", pytest.approx(11))


def test_an_entering_column_with_no_positive_entry_is_unbounded():
    T = [[1, -1, 1, 2],
         [-1, -1, 0, 0]]
    assert run_simplex(T) == ("UNBOUNDED", None)


def test_a_zero_ratio_is_a_real_pivot_of_length_zero():
    T = [[1, -1, 1, 0, 0],
         [1, 1, 0, 1, 4],
         [-2, -1, 0, 0, 0]]
    assert run_simplex(T) == ("OPTIMAL", pytest.approx(6))
