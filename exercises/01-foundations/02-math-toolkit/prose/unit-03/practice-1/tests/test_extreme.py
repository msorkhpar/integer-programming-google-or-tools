import numpy as np

from extreme import is_extreme_point

# A storage yard: x0 tonnes of gravel and x1 tonnes of sand.
#   x0 <= 4, x1 <= 3, x0 + x1 <= 6, x0 >= 0, x1 >= 0
YARD_A = np.array([[1, 0], [0, 1], [1, 1], [-1, 0], [0, -1]])
YARD_B = np.array([4, 3, 6, 0, 0])


def test_a_corner_is_extreme_and_an_inside_point_is_not():
    assert is_extreme_point(YARD_A, YARD_B, np.array([4, 2])) is True     # x0 <= 4 and x0 + x1 <= 6 tight
    assert is_extreme_point(YARD_A, YARD_B, np.array([2, 1])) is False    # nothing tight


def test_a_point_on_one_edge_is_not_extreme():
    assert is_extreme_point(YARD_A, YARD_B, np.array([4, 1])) is False    # only x0 <= 4 is tight


def test_a_crossing_outside_the_region_is_not_extreme():
    assert is_extreme_point(YARD_A, YARD_B, np.array([4, 3])) is False    # x0 + x1 = 7 > 6


def test_a_corner_where_three_rows_meet_is_extreme():
    A = np.array([[1, 0], [0, 1], [1, 1], [-1, 0], [0, -1]])
    b = np.array([3, 3, 6, 0, 0])
    assert is_extreme_point(A, b, np.array([3, 3])) is True               # three rows tight at once


def test_two_tight_rows_that_say_the_same_thing_are_not_a_corner():
    A = np.array([[0, 1], [0, 2], [1, 0], [-1, 0], [0, -1]])
    b = np.array([3, 6, 4, 0, 0])
    assert is_extreme_point(A, b, np.array([2, 3])) is False              # x1 <= 3 and 2 x1 <= 6


def test_a_corner_with_fractional_coordinates_is_found():
    A = np.array([[3, 1], [1, 3], [-1, 0], [0, -1]])
    b = np.array([1, 1, 0, 0])
    assert is_extreme_point(A, b, np.array([0.25, 0.25])) is True
    A = np.array([[0.1, 0.2], [0.4, 0.1], [-1, 0], [0, -1]])
    b = np.array([0.3, 0.7, 0, 0])
    corner = np.linalg.solve(A[:2], b[:2])                                # (11/7, 5/7), a hair off in floating point
    assert is_extreme_point(A, b, corner) is True


def test_in_three_dimensions_two_tight_rows_are_not_enough():
    cube_A = np.vstack([np.eye(3), -np.eye(3)])
    cube_b = np.array([1, 1, 1, 0, 0, 0])
    assert is_extreme_point(cube_A, cube_b, np.array([1, 1, 0.5])) is False   # on an edge of the cube
    assert is_extreme_point(cube_A, cube_b, np.array([1, 1, 0])) is True      # a corner
