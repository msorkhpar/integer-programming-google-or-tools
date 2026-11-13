import numpy as np

from check import broken_rows, is_feasible

# Three crews share four work orders; rows are crew-hours, columns are work orders.
HOURS = np.array([[4, 0, 2, 1],
                  [0, 3, 3, 0],
                  [1, 1, 0, 5]])
LIMIT = np.array([8, 7, 9])


def test_a_plan_within_every_row_is_feasible():
    x = np.array([1, 1, 0, 1])
    assert broken_rows(HOURS, LIMIT, x) == []
    assert is_feasible(HOURS, LIMIT, x) is True


def test_a_row_met_exactly_holds():
    x = np.array([1, 0, 2, 0])          # row 0: 4 + 4 = 8, exactly the limit
    assert broken_rows(HOURS, LIMIT, x) == []
    assert is_feasible(HOURS, LIMIT, x) is True


def test_a_rounding_miss_within_the_tolerance_holds():
    A = np.array([[0.1, 0.2]])
    b = np.array([0.3])
    x = np.array([1.0, 1.0])            # 0.1 + 0.2 lands a hair above 0.3
    assert broken_rows(A, b, x) == []
    assert is_feasible(A, b, x) is True


def test_one_broken_row_makes_the_plan_infeasible():
    x = np.array([0, 0, 0, 2])          # rows 0 and 1 hold, row 2 needs 10 > 9
    assert broken_rows(HOURS, LIMIT, x) == [2]
    assert is_feasible(HOURS, LIMIT, x) is False


def test_every_broken_row_is_reported():
    x = np.array([2, 1, 2, 2])          # rows 0, 1 and 2 are all over
    assert broken_rows(HOURS, LIMIT, x) == [0, 1, 2]
    assert is_feasible(HOURS, LIMIT, x) is False
