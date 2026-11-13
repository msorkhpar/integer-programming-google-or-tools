import pytest

from best import best_corners

PENTAGON = [(0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (3.0, 1.0), (3.0, 0.0)]


def test_the_best_corner_and_its_value():
    assert best_corners(PENTAGON, (2, 1)) == (pytest.approx(7), [(3.0, 1.0)])


def test_a_tie_returns_both_ends_of_the_optimal_edge():
    assert best_corners(PENTAGON, (1, 1)) == (pytest.approx(4), [(2.0, 2.0), (3.0, 1.0)])


def test_minimizing_takes_the_smallest_value():
    assert best_corners(PENTAGON, (1, -1), "min") == (pytest.approx(-2), [(0.0, 2.0)])


def test_an_empty_region_has_no_value_rather_than_zero():
    assert best_corners(PENTAGON, (0, 1))[0] == pytest.approx(2)
    assert best_corners([], (1, 1)) == (None, [])
