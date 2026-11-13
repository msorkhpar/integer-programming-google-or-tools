import pytest

from bound import bound

# ratios: T1 3.0, T2 2.0, T3 1.0, T4 0.5
SPARES = [("T1", 120, 40), ("T2", 100, 50), ("T3", 45, 45), ("T4", 30, 60)]


def test_the_fill_takes_whole_items_then_a_fraction_of_the_split():
    # T1 fits (30 left); T2 fits 30/50 of the way.
    value, split = bound(SPARES, 70, {})
    assert value == pytest.approx(120 + 100 * 30 / 50) and split == "T2"


def test_when_every_item_fits_there_is_no_split():
    value, split = bound(SPARES, 200, {})
    assert value == pytest.approx(295) and split is None


def test_items_are_filled_by_ratio_not_by_value():
    items = [("big", 100, 100), ("small", 30, 10)]
    value, split = bound(items, 50, {})
    assert value == pytest.approx(30 + 100 * 40 / 100) and split == "big"


def test_the_fill_stops_at_the_split_item():
    items = [("a", 60, 20), ("b", 50, 25), ("c", 4, 4)]
    value, split = bound(items, 30, {})
    assert value == pytest.approx(60 + 50 * 10 / 25) and split == "b"


def test_items_fixed_at_one_are_paid_first_and_items_fixed_at_zero_are_skipped():
    # T4 paid first (10 left); T1 skipped; T2 fits 10/50 of the way.
    value, split = bound(SPARES, 70, {"T4": 1, "T1": 0})
    assert value == pytest.approx(30 + 100 * 10 / 50) and split == "T2"


def test_fixings_over_budget_make_the_node_infeasible():
    assert bound(SPARES, 70, {"T2": 1, "T3": 1, "T4": 1}) is None
    value, split = bound(SPARES, 70, {"T2": 1, "T1": 0})
    assert value == pytest.approx(100 + 45 * 20 / 45) and split == "T3"


def test_a_budget_used_up_exactly_has_no_split():
    # T1 and T2 cost exactly 90: nothing is left for T3.
    value, split = bound(SPARES, 90, {})
    assert value == pytest.approx(220) and split is None
    value, split = bound(SPARES, 90, {"T1": 1, "T2": 1})
    assert value == pytest.approx(220) and split is None
