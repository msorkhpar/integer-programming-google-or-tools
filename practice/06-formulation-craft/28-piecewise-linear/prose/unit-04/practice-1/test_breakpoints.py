import math

from breakpoints import fewest_breakpoints


def test_a_parabola_needs_six_breakpoints_for_its_tolerance():
    # gap of x^2 with segments of width w is w^2 / 4: 0.0100 at w = 0.2, 0.0156 at w = 0.25
    assert fewest_breakpoints(lambda x: x * x, 0.0, 1.0, 0.011) == 6


def test_a_straight_line_needs_only_its_ends():
    assert fewest_breakpoints(lambda x: 3 * x - 2, -5.0, 5.0, 1e-9) == 2
    assert fewest_breakpoints(lambda x: 3 * x - 2, -5.0, 5.0, 10.0) == 2


def test_the_gap_is_measured_between_breakpoints_not_only_at_midpoints():
    # on its first segment, sqrt's gap peaks a quarter of the way along, not at the middle
    assert fewest_breakpoints(math.sqrt, 0.0, 1.0, 0.05) == 26


def test_no_count_within_the_limit_returns_none():
    assert fewest_breakpoints(lambda x: x * x, 0.0, 1.0, 0.011, max_n=5) is None
    assert fewest_breakpoints(lambda x: x * x, 0.0, 1.0, 0.011, max_n=6) == 6
