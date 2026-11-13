from sweep import steps


def test_each_allowance_that_reaches_a_better_plan_is_a_step():
    sweep = [(0, 800, 10), (4, 796, 13), (9, 791, 20), (15, 785, 21)]
    assert steps(800, sweep) == [(0, 0, 0), (4, 4, 3), (9, 9, 10), (15, 15, 11)]


def test_a_sweep_of_one_row_is_one_step_with_no_gain():
    assert steps(120, [(0, 120, 7)]) == [(0, 0, 0)]


def test_rows_may_arrive_in_any_order():
    sweep = [(9, 791, 20), (0, 800, 10), (15, 785, 21), (4, 796, 13)]
    assert steps(800, sweep) == [(0, 0, 0), (4, 4, 3), (9, 9, 10), (15, 15, 11)]


def test_a_larger_allowance_that_reaches_the_same_plan_is_not_a_new_step():
    sweep = [(0, 300, 50), (6, 294, 58), (12, 294, 58), (20, 280, 70)]
    assert steps(300, sweep) == [(0, 0, 0), (6, 6, 8), (20, 20, 20)]


def test_taken_is_what_the_plan_gave_up_not_what_was_allowed():
    sweep = [(0, 1000, 5), (25, 990, 9), (60, 958, 14)]
    assert steps(1000, sweep) == [(0, 0, 0), (25, 10, 4), (60, 42, 9)]
