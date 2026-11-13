from reduce import reduce_row


def free(*names):
    return dict.fromkeys(names, 0), dict.fromkeys(names, 1)


def test_a_row_that_always_holds_is_redundant():
    lo, hi = free("a", "b")
    assert reduce_row({"a": 2, "b": 3}, 5, lo, hi) == ("redundant", {})


def test_items_too_heavy_for_the_row_are_fixed_at_zero():
    lo, hi = free("p", "q", "r")
    assert reduce_row({"p": 7, "q": 7, "r": 1}, 6, lo, hi) == ("keep", {"p": 0, "q": 0})


def test_a_fixed_variable_raises_the_least_activity():
    lo, hi = free("a", "b", "c")
    lo["a"] = 1
    assert reduce_row({"a": 6, "b": 4, "c": 3}, 8, lo, hi) == ("keep", {"b": 0, "c": 0})


def test_a_row_that_can_never_hold_is_infeasible():
    assert reduce_row({"a": 4, "b": 3}, 6, {"a": 1, "b": 1}, {"a": 1, "b": 1}) == ("infeasible", {})


def test_a_negative_coefficient_can_force_a_one():
    lo, hi = free("a", "s")
    assert reduce_row({"a": 3, "s": -5}, -2, lo, hi) == ("keep", {"s": 1})


def test_a_row_is_deleted_only_when_it_provably_cannot_bind():
    lo, hi = free("a", "b")
    assert reduce_row({"a": 0.5, "b": 0.25}, 0.75, lo, hi) == ("redundant", {})
    assert reduce_row({"a": 0.1, "b": 0.2}, 0.3, lo, hi) == ("keep", {})
