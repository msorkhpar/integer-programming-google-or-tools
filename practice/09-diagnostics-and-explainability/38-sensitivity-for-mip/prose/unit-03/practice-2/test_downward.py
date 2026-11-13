from itertools import product

from downward import step_points

COSTS, VALUES = [3, 4, 6, 7], [5, 7, 10, 13]


def by_hand(lo, hi):
    def v(b):
        return max(sum(x * p for x, p in zip(VALUES, pick)) for pick in product((0, 1), repeat=len(COSTS))
                   if sum(c * p for c, p in zip(COSTS, pick)) <= b)
    points = [(lo, v(lo))]
    for b in range(lo + 1, hi + 1):
        if v(b) > points[-1][1]:
            points.append((b, v(b)))
    return points


def test_the_step_points_match_a_curve_checked_by_hand():
    assert step_points(COSTS, VALUES, 0, 20) == by_hand(0, 20)


def test_the_list_starts_at_lo_even_inside_a_flat_stretch():
    assert by_hand(18, 20) == [(18, 30), (20, 35)]     # V steps to 30 at 17 and stays there until 20
    assert step_points(COSTS, VALUES, 18, 20) == by_hand(18, 20)


def test_a_stretch_starting_exactly_at_lo_is_reported():
    assert by_hand(6, 12)[:2] == [(6, 10), (7, 13)]    # a stretch begins at 6, and the next at 7
    assert step_points(COSTS, VALUES, 6, 12) == by_hand(6, 12)
