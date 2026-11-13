from rins import rins


def test_the_best_plan_of_the_neighbourhood_is_returned():
    values, costs = {"A": 7, "B": 6, "C": 5, "D": 2}, {"A": 5, "B": 4, "C": 3, "D": 1}
    incumbent = {"A": 1, "B": 0, "C": 0, "D": 1}
    x = {"A": 0.2, "B": 1, "C": 1, "D": 1}
    assert rins(values, costs, 9, incumbent, x) == ["A", "C", "D"]


def test_with_no_agreement_the_whole_problem_is_searched():
    values, costs = {"A": 5, "B": 4, "C": 3}, {"A": 4, "B": 3, "C": 2}
    incumbent = {"A": 1, "B": 0, "C": 0}
    x = {"A": 0.4, "B": 0.7, "C": 0.8}
    assert rins(values, costs, 5, incumbent, x) == ["B", "C"]


def test_an_lp_value_just_under_one_agrees_with_a_one():
    values, costs = {"A": 3, "B": 5, "C": 5}, {"A": 4, "B": 3, "C": 3}
    incumbent = {"A": 1, "B": 0, "C": 0}
    x = {"A": 0.9999999, "B": 0.6667, "C": 0}
    assert rins(values, costs, 6, incumbent, x) == ["A"]


def test_a_fractional_value_never_agrees():
    values, costs = {"A": 4, "B": 6}, {"A": 3, "B": 5}
    incumbent = {"A": 1, "B": 0}
    x = {"A": 0.4, "B": 0.3}
    assert rins(values, costs, 5, incumbent, x) == ["B"]


def test_a_neighbourhood_with_no_plan_in_budget_gives_none():
    values, costs = {"A": 4, "B": 3, "C": 2}, {"A": 4, "B": 4, "C": 1}
    incumbent = {"A": 1, "B": 1, "C": 0}
    x = {"A": 1, "B": 1, "C": 0.5}
    assert rins(values, costs, 6, incumbent, x) is None
