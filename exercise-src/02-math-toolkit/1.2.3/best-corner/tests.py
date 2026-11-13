import numpy as np
import pytest

from corner import best_corner

# A bakery splits oven hours between bread (x0) and pastry (x1).
# The oven region: x0 + x1 <= 8, x0 + 3 x1 <= 12, x0 >= 0, x1 >= 0
OVEN_A = np.array([[1, 1], [1, 3], [-1, 0], [0, -1]])
OVEN_B = np.array([8, 12, 0, 0])


def test_the_best_vertex_and_its_value():
    A = np.array([[1, 2], [-1, 0], [0, -1]])               # x0 + 2 x1 <= 10, x0 >= 0, x1 >= 0
    b = np.array([10, 0, 0])
    value, point = best_corner(A, b, np.array([3, 5]))
    assert value == pytest.approx(30.0)
    assert point == pytest.approx((10.0, 0.0))


def test_a_crossing_outside_the_region_is_never_chosen():
    value, point = best_corner(OVEN_A, OVEN_B, np.array([1, 4]))
    # x0 + x1 = 8 meets x1 = 0 at (8, 0) and x0 = 0 at (0, 8); (0, 8) needs 24 hours > 12
    assert value == pytest.approx(16.0)
    assert point == pytest.approx((0.0, 4.0))


def test_parallel_rows_are_skipped():
    A = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])      # a box: x0 in [0, 5], x1 in [0, 2]
    b = np.array([5, 0, 2, 0])
    value, point = best_corner(A, b, np.array([1, 1]))
    assert value == pytest.approx(7.0)
    assert point == pytest.approx((5.0, 2.0))


def test_a_corner_that_rounding_puts_a_hair_outside_is_kept():
    A = np.array([[0.1, 0.2], [0.4, 0.1], [-1, 0], [0, -1]])
    b = np.array([0.3, 0.7, 0, 0])
    value, point = best_corner(A, b, np.array([1, 1]))     # the corner (11/7, 5/7)
    assert value == pytest.approx(16 / 7)
    assert point == pytest.approx((11 / 7, 5 / 7))
