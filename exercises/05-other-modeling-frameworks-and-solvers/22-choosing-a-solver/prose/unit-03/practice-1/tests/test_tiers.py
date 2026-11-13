from tiers import fits

ROWS_AND_COLS = {"linear": (2000, 2000, 10000), "quadratic": (200, 2000, 10000)}
SUM_ONLY = {"linear": (None, None, 5000), "quadratic": (None, None, 200)}


def test_a_model_under_the_caps_fits_and_one_over_does_not():
    assert fits(500, 300, False, ROWS_AND_COLS) is True
    assert fits(2500, 300, False, ROWS_AND_COLS) is False


def test_a_count_equal_to_its_cap_fits():
    assert fits(2000, 2000, False, ROWS_AND_COLS) is True


def test_a_sum_cap_counts_variables_and_rows_together():
    assert fits(1000, 1000, False, SUM_ONLY) is True
    assert fits(3000, 2500, False, SUM_ONLY) is False


def test_a_quadratic_model_meets_the_quadratic_caps():
    assert fits(100, 300, True, ROWS_AND_COLS) is True
    assert fits(500, 300, True, ROWS_AND_COLS) is False


def test_a_missing_cap_is_no_cap():
    assert fits(3000, 1000, False, SUM_ONLY) is True
