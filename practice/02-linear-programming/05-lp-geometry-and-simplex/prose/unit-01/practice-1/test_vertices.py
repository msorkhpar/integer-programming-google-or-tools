from vertices import vertices

X_NONNEG, Y_NONNEG = (-1, 0, 0), (0, -1, 0)


def test_a_triangle_has_three_corners():
    assert vertices([X_NONNEG, Y_NONNEG, (1, 1, 4)]) == [(0.0, 0.0), (0.0, 4.0), (4.0, 0.0)]


def test_parallel_sides_are_skipped_and_an_open_strip_has_two_corners():
    assert vertices([X_NONNEG, Y_NONNEG, (0, 1, 2)]) == [(0.0, 0.0), (0.0, 2.0)]


def test_a_crossing_outside_the_region_is_not_a_corner():
    rows = [X_NONNEG, Y_NONNEG, (1, 0, 3), (0, 1, 2), (1, 1, 4)]
    assert vertices(rows) == [(0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (3.0, 0.0), (3.0, 1.0)]


def test_a_corner_where_three_lines_meet_is_listed_once():
    rows = [X_NONNEG, Y_NONNEG, (1, 1, 4), (1, -1, 4)]
    assert vertices(rows) == [(0.0, 0.0), (0.0, 4.0), (4.0, 0.0)]


def test_a_corner_with_decimal_data_survives_float_rounding():
    rows = [X_NONNEG, Y_NONNEG, (0.1, 0.3, 0.3), (0.3, 0.1, 0.3)]
    assert vertices(rows) == [(0.0, 0.0), (0.0, 1.0), (0.75, 0.75), (1.0, 0.0)]
