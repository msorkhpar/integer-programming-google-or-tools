from itertools import product

from lots import value_function


def by_hand(days, worth, limits, capacity):
    best = [0] * (capacity + 1)
    for counts in product(*(range(u + 1) for u in limits)):
        used = sum(a * x for a, x in zip(days, counts))
        value = sum(c * x for c, x in zip(worth, counts))
        for d in range(used, capacity + 1):
            best[d] = max(best[d], value)
    return best


def test_the_value_function_matches_every_plan_checked_by_hand():
    days, worth, limits = [1, 4, 5], [0, 6, 7], [7, 1, 1]
    assert value_function(days, worth, limits, 7) == by_hand(days, worth, limits, 7)


def test_a_lot_type_can_be_bought_more_than_once():
    days, worth, limits = [2, 7], [3, 9], [3, 1]
    assert value_function(days, worth, limits, 10) == by_hand(days, worth, limits, 10)


def test_no_type_is_bought_past_its_limit():
    days, worth, limits = [2, 5], [5, 6], [2, 2]
    assert value_function(days, worth, limits, 12) == by_hand(days, worth, limits, 12)


def test_capacity_may_be_left_unused():
    days, worth, limits = [4, 6], [6, 10], [1, 1]
    assert value_function(days, worth, limits, 11) == by_hand(days, worth, limits, 11)
