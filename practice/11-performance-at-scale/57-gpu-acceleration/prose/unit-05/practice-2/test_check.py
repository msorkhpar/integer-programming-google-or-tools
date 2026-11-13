from check import accept

VALUES = [8.0, 5.0, 9.0, 3.0, 4.0, 11.0]
HOURS = [[0, 2], [4, 0], [4, 1], [0, 0], [3, 3], [0, 1]]
CAPACITY = [8.0, 8.0]
REQUIRES = [(2, 3)]
BEST = [1.0, 1.0, 1.0, 1.0, 0.0, 1.0]                       # worth 36


def check(x, reported, bounds, gap=1e-3):
    return accept(x, reported, bounds, VALUES, HOURS, CAPACITY, REQUIRES, gap)


def test_a_good_plan_is_accepted_and_one_over_capacity_is_refused():
    assert check(BEST, 36.0, [36.0]) == (True, "accepted")
    assert check([0.0, 1.0, 1.0, 0.0, 1.0, 0.0], 18.0, [36.0]) == (False, "over capacity in quarter 1")


def test_a_plan_short_of_the_gap_is_refused():
    assert check([1.0, 1.0, 1.0, 1.0, 0.0, 0.0], 25.0, [36.0]) == (False, "outside the gap")
    assert check([1.0, 1.0, 1.0, 1.0, 0.0, 0.0], 25.0, [36.0], gap=0.5) == (True, "accepted")


def test_values_a_hair_from_whole_numbers_count_and_a_half_does_not():
    nearly = [1.0 - 2e-6, 1.0, 1.0 + 1e-7, 1.0, 3e-6, 1.0]
    assert check(nearly, 36.0, [36.0]) == (True, "accepted")
    assert check([1.0, 1.0, 1.0, 1.0, 0.5, 1.0], 38.0, [40.0]) == (False, "not integral")


def test_a_dependency_is_checked():
    assert check([0.0, 1.0, 1.0, 1.0, 0.0, 1.0], 28.0, [28.0], gap=0.5) == (True, "accepted")
    assert check([1.0, 1.0, 0.0, 1.0, 0.0, 1.0], 27.0, [27.0], gap=0.5) == (False, "job 3 without job 2")


def test_the_plan_is_worth_what_it_selects_not_what_was_reported():
    short = [1.0, 1.0, 1.0, 0.0, 0.0, 1.0]                    # worth 33, more than 0.1% below 36
    assert check(short, 36.0, [36.0]) == (False, "outside the gap")
    assert check(short, 33.0, [33.0]) == (True, "accepted")


def test_the_tightest_bound_from_any_solver_is_the_yardstick():
    plan = [1.0, 1.0, 1.0, 1.0, 0.0, 1.0]
    assert check(plan, 36.0, [36.03, 39.0]) == (True, "accepted")
    assert check(plan, 36.0, [39.0, 36.0]) == (True, "accepted")
    assert check(plan, 36.0, [39.0, 38.0]) == (False, "outside the gap")
