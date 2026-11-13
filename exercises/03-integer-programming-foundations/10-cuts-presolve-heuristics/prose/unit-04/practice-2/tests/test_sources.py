import pytest

from sources import history


def test_lettered_rows_become_named_incumbents_with_their_gaps():
    rows = [{"src": "R", "bound": 1520.5, "incumbent": 1490.0},
            {"src": "", "bound": 1510.0, "incumbent": 1490.0},
            {"src": "L", "bound": 1498.0, "incumbent": 1495.0}]
    assert history(rows) == [("Randomized rounding", 1490.0, pytest.approx(30.5 / 1490)),
                             ("Sub-MIP", 1495.0, pytest.approx(3 / 1495))]


def test_no_gap_before_the_first_bound():
    rows = [{"src": "J", "bound": float("inf"), "incumbent": 900.0}]
    assert history(rows) == [("Feasibility jump", 900.0, None)]


def test_lower_case_letters_are_their_own_sources():
    rows = [{"src": "p", "bound": 1000.0, "incumbent": 950.0}]
    assert history(rows) == [("Trivial point", 950.0, pytest.approx(50 / 950))]


def test_a_minimization_gap_is_positive():
    rows = [{"src": "T", "bound": 80.0, "incumbent": 100.0}]
    assert history(rows) == [("Evaluate node", 100.0, pytest.approx(0.2))]
