from fill import round_and_fill


def test_rounding_keeps_the_whole_items_and_drops_the_fraction():
    values, costs = {"A": 8, "B": 5, "C": 3}, {"A": 4, "B": 4, "C": 3}
    assert round_and_fill(values, costs, 9, {"A": 1, "B": 1, "C": 1 / 3}) == ["A", "B"]


def test_the_fill_adds_an_item_that_fits():
    values, costs = {"A": 9, "B": 5, "C": 1}, {"A": 6, "B": 3, "C": 2}
    assert round_and_fill(values, costs, 10, {"A": 1, "B": 0.5, "C": 0}) == ["A", "B"]


def test_an_lp_value_just_under_one_counts_as_one():
    values, costs = {"A": 4, "B": 9}, {"A": 5, "B": 6}
    assert round_and_fill(values, costs, 6, {"A": 0.9999999, "B": 1 / 6}) == ["A"]


def test_a_fractional_item_is_never_rounded_up():
    values, costs = {"A": 6, "B": 5, "C": 2}, {"A": 5, "B": 5, "C": 3}
    assert round_and_fill(values, costs, 8, {"A": 1, "B": 0.6, "C": 0}) == ["A", "C"]


def test_an_item_that_does_not_fit_is_skipped_and_the_next_is_tried():
    values, costs = {"A": 9, "B": 5, "C": 1}, {"A": 6, "B": 5, "C": 2}
    assert round_and_fill(values, costs, 10, {"A": 1, "B": 0.8, "C": 0}) == ["A", "C"]
