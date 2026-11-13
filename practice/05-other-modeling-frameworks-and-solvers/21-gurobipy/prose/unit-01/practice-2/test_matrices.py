import numpy as np

from matrices import needs_matrix, spend_matrix

YEARS = [2040, 2041, 2042]


def test_one_year_projects_fill_their_start_year():
    projects = [("well", 2040, [300.0]), ("tank", 2040, [120.0])]
    A = spend_matrix(projects, YEARS)
    assert A.shape == (3, 2)
    assert np.array_equal(A, np.array([[300.0, 120.0], [0.0, 0.0], [0.0, 0.0]]))


def test_a_needs_row_has_plus_one_for_the_child_and_minus_one_for_the_parent():
    projects = [("well", 2040, [300.0]), ("tank", 2040, [120.0]), ("pipe", 2040, [80.0])]
    N = needs_matrix(projects, {"tank": "well", "pipe": "tank"})
    assert np.array_equal(N, np.array([[-1.0, 1.0, 0.0], [0.0, -1.0, 1.0]]))


def test_a_later_start_spends_in_its_own_calendar_years():
    projects = [("well", 2040, [300.0]), ("main", 2041, [200.0, 50.0])]
    A = spend_matrix(projects, YEARS)
    assert np.array_equal(A[:, 1], np.array([0.0, 200.0, 50.0]))


def test_spend_past_the_horizon_is_left_out():
    projects = [("well", 2040, [300.0]), ("plant", 2042, [500.0, 400.0])]
    A = spend_matrix(projects, YEARS)
    assert np.array_equal(A[:, 1], np.array([0.0, 0.0, 500.0]))
    assert A.sum() == 800.0
