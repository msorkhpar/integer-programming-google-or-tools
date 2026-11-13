from fractions import Fraction as F

from gomory import gomory_in_x

A2 = [[2, 1], [1, 3]]
B2 = [7, 9]


def test_a_row_with_two_slack_entries():
    g, h = gomory_in_x([F(1), F(0), F(1, 4), F(1, 2), F(9, 4)], A2, B2)
    assert (list(g), h) == ([F(1), F(7, 4)], F(6))


def test_a_model_with_three_rows():
    A = [[1, 2], [3, 1], [1, 0]]
    b = [8, 9, 2]
    g, h = gomory_in_x([F(0), F(1), F(1, 3), F(2, 3), F(0), F(8, 3)], A, b)
    assert (list(g), h) == ([F(7, 3), F(4, 3)], F(8))


def test_a_negative_entry_uses_the_floor():
    g, h = gomory_in_x([F(1), F(0), F(3, 5), F(-1, 5), F(12, 5)], A2, B2)
    assert (list(g), h) == ([F(2), F(3)], F(11))


def test_a_nonbasic_original_variable_enters_the_cut():
    g, h = gomory_in_x([F(1), F(1, 2), F(1, 4), F(0), F(7, 4)], A2, B2)
    assert (list(g), h) == ([F(1, 2), F(-1, 4)], F(1))
