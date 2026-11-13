from lags import start_to_start, usable_child_years

# A water utility's renewals, not the lessons' portfolio.


def test_finish_to_start_adds_the_parent_duration():
    assert start_to_start("FS", 1, 3, 2) == 4
    assert start_to_start("SS", 2, 3, 2) == 2


def test_usable_years_drop_child_years_no_parent_start_can_serve():
    # the child's 2029 is blocked by an outage, so its window has a hole
    assert usable_child_years((2027,), (2027, 2028, 2030, 2031), 2) == [2030, 2031]


def test_finish_to_finish_subtracts_the_child_duration():
    assert start_to_start("FF", 0, 2, 3) == -1
    assert start_to_start("FF", 2, 4, 1) == 5


def test_start_to_finish_subtracts_the_child_duration():
    assert start_to_start("SF", 1, 3, 2) == -1
    assert start_to_start("SF", 4, 1, 1) == 3


def test_a_lag_of_zero_allows_the_same_year():
    assert usable_child_years((2028,), (2027, 2028, 2029), 0) == [2028, 2029]


def test_any_parent_start_can_serve_a_child_year():
    assert usable_child_years((2027, 2029), (2028, 2029, 2030, 2031), 2) == [2029, 2030, 2031]
