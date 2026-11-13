from togap import work_to_gap

MAX_LOG = [(10, 900.0, 1000.0), (25, 950.0, 1000.0), (60, 985.0, 1000.0), (90, 995.0, 1000.0), (140, 1000.0, 1000.0)]
MIN_LOG = [(8, 1300.0, 1000.0), (30, 1100.0, 1000.0), (70, 1040.0, 1000.0), (120, 1009.0, 1000.0)]


def test_the_first_row_within_the_target_gives_the_work():
    assert work_to_gap(MAX_LOG, 0.01) == 90          # 15/985 is 1.5%, 5/995 is 0.5%
    assert work_to_gap(MAX_LOG, 0.06) == 25


def test_a_minimization_log_uses_the_size_of_the_gap():
    assert work_to_gap(MIN_LOG, 0.05) == 70          # 100/1100 is 9.1%, 40/1040 is 3.8%


def test_a_gap_equal_to_the_target_counts_as_reached():
    log = [(5, 900.0, 1000.0), (15, 1000.0, 1020.0), (40, 1010.0, 1020.0)]
    assert work_to_gap(log, 0.02) == 15              # 20/1000 is exactly 2%


def test_a_target_never_reached_gives_none():
    assert work_to_gap(MAX_LOG, 0.01) == 90
    assert work_to_gap(MAX_LOG[:3], 0.01) is None


def test_the_gap_divides_by_the_incumbent():
    log = [(10, 900.0, 950.0), (40, 940.0, 950.0)]
    assert work_to_gap(log, 0.054) == 40             # 50/900 is 5.56%; 50/950 would be 5.26%
