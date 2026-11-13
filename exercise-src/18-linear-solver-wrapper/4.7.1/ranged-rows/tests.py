from rows import best


def test_rows_with_an_upper_bound_cut_the_plan():
    # x0 + 2 x1 <= 8: the best of x0 + 3 x1 is x1 = 4
    assert best([("cap", None, {"x0": 1, "x1": 2}, 8)], {"x0": 1, "x1": 3}) == 12


def test_a_missing_lower_bound_is_no_bound_at_all():
    # x0 - x1 <= 3 has no lower bound, so x1 may exceed x0
    rows = [("net", None, {"x0": 1, "x1": -1}, 3), ("cap", None, {"x1": 1}, 7)]
    assert best(rows, {"x0": -2, "x1": 1}) == 7


def test_a_lower_bound_is_kept():
    # x1 - x0 >= 2: x1 stays at least 2 above x0
    assert best([("gap", 2, {"x0": -1, "x1": 1}, None)], {"x0": 2, "x1": -1}) == 6


def test_a_missing_upper_bound_is_no_bound_at_all():
    # x0 >= 3 with no upper bound: the smallest x0 is 3
    assert best([("floor", 3, {"x0": 1}, None)], {"x0": -1}) == -3
