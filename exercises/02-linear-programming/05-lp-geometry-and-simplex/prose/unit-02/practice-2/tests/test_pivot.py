import copy

import pytest

from pivot import pivot

START = [[1, 1, 1, 0, 0, 4],
         [1, 3, 0, 1, 0, 6],
         [1, 0, 0, 0, 1, 3],
         [-3, -2, 0, 0, 0, 0]]
SECOND = [[0, 1, 1, 0, -1, 1],
          [0, 3, 0, 1, -1, 3],
          [1, 0, 0, 0, 1, 3],
          [0, -2, 0, 0, 3, 9]]


def rows(T):
    return [pytest.approx(row) for row in T]


def test_a_unit_pivot_clears_the_column_in_every_constraint_row():
    assert pivot(START, 2, 0)[:-1] == rows(SECOND[:-1])


def test_the_pivot_row_is_divided_by_the_pivot_element():
    after = pivot(SECOND, 1, 1)[:-1]
    assert after == rows([[0, 0, 1, -1 / 3, -2 / 3, 0],
                          [0, 1, 0, 1 / 3, -1 / 3, 1],
                          [1, 0, 0, 0, 1, 3]])


def test_the_objective_row_is_updated_too():
    assert pivot(START, 2, 0)[-1] == pytest.approx([0, -2, 0, 0, 3, 9])
    assert pivot(SECOND, 1, 1)[-1] == pytest.approx([0, 0, 0, 2 / 3, 7 / 3, 11])


def test_the_input_tableau_is_left_unchanged():
    before = copy.deepcopy(START)
    after = pivot(START, 2, 0)
    assert after[0] == pytest.approx(SECOND[0])
    assert START == before
