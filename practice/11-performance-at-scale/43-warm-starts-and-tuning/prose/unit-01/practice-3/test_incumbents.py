import math

from incumbents import in_hand, work_to_first, work_to_within

LOG = [(12.0, 5400.0), (12.0, 5100.0), (90.0, 5160.0), (150.0, 4890.0), (900.0, 4800.0)]


def test_the_first_plan_and_a_good_plan_are_dated_by_work():
    assert work_to_first(LOG) == 12.0
    assert work_to_within(LOG, 4800.0, 0.02) == 150.0


def test_the_plan_in_hand_after_some_work_is_the_cheapest_so_far():
    assert in_hand(LOG, 50.0) == 5100.0
    assert in_hand(LOG, 1000.0) == 4800.0


def test_no_plan_means_infinite_work_not_zero():
    assert work_to_first([]) == math.inf
    assert work_to_within(LOG[:2], 4800.0, 0.01) == math.inf


def test_a_worse_plan_found_later_does_not_count():
    assert in_hand(LOG, 120.0) == 5100.0


def test_the_target_is_a_share_of_the_size_of_best():
    log = [(5.0, -900.0), (30.0, -1000.0)]
    assert work_to_within(log, -1000.0, 0.05) == 30.0


def test_a_plan_exactly_at_the_target_counts():
    log = [(7.0, 1100.0), (20.0, 1000.0)]
    assert work_to_within(log, 1000.0, 0.10) == 7.0


def test_nothing_is_in_hand_before_the_first_plan():
    assert in_hand(LOG, 5.0) is None
