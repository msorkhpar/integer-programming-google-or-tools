from standard_form import standard_form

V = ["pipe", "valve", "meter"]


def test_a_max_lp_with_only_at_most_rows_is_copied_into_matrices():
    rows = [({"pipe": 2, "valve": 1}, "<=", 40), ({"valve": 1, "meter": 3}, "<=", 30)]
    c, A, b = standard_form(V, {"pipe": 5, "valve": 4, "meter": 2}, "max", rows)
    assert c == [5, 4, 2]
    assert A == [[2, 1, 0], [0, 1, 3]]
    assert b == [40, 30]


def test_an_at_least_row_is_multiplied_by_minus_one_on_both_sides():
    c, A, b = standard_form(V, {"pipe": 1}, "max", [({"pipe": 1, "meter": 2}, ">=", 12)])
    assert A == [[-1, 0, -2]]
    assert b == [-12]


def test_an_equation_becomes_an_at_most_row_and_a_negated_one():
    c, A, b = standard_form(V, {"pipe": 1}, "max", [({"pipe": 1, "valve": -1}, "==", 4)])
    assert A == [[1, -1, 0], [-1, 1, 0]]
    assert b == [4, -4]


def test_a_minimization_becomes_a_maximization_of_the_negated_costs():
    c, A, b = standard_form(V, {"pipe": 3, "valve": 1, "meter": 7}, "min", [({"pipe": 1}, "<=", 9)])
    assert c == [-3, -1, -7]
    assert A == [[1, 0, 0]] and b == [9]
