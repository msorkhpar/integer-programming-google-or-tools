from overrides import bounds_for

WINDOW = range(2027, 2032)   # 2027 to 2031


def test_start_in_fixes_one_year_and_closes_the_rest():
    assert bounds_for("start_in", (2029,), WINDOW) == {
        2027: (0, 0), 2028: (0, 0), 2029: (1, 1), 2030: (0, 0), 2031: (0, 0)}


def test_only_between_keeps_both_end_years_open():
    assert bounds_for("only_between", (2028, 2030), WINDOW) == {
        2027: (0, 0), 2028: (0, 1), 2029: (0, 1), 2030: (0, 1), 2031: (0, 0)}


def test_skip_years_closes_only_the_named_years():
    assert bounds_for("skip_years", (2028, 2030), WINDOW) == {
        2027: (0, 1), 2028: (0, 0), 2029: (0, 1), 2030: (0, 0), 2031: (0, 1)}


def test_an_override_that_leaves_no_year_is_refused():
    assert bounds_for("only_between", (2033, 2035), WINDOW) is None
    assert bounds_for("skip_years", (2027, 2028, 2029, 2030, 2031), WINDOW) is None
    assert bounds_for("skip_years", (2027,), WINDOW) == {
        2027: (0, 0), 2028: (0, 1), 2029: (0, 1), 2030: (0, 1), 2031: (0, 1)}
