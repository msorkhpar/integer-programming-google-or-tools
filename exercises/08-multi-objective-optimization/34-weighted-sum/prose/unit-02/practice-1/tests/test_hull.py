from hull import supported_points


def oracle(points):
    """A weighted-sum solver over a fixed list of options; ties go to the larger first, then second value."""
    calls = []

    def best_for(s):
        calls.append(s)
        return max(points, key=lambda p: (round(s * p[0] + (1 - s) * p[1], 9), p[0], p[1]))
    return best_for, calls


def test_the_supported_points_of_a_short_front_are_found():
    best_for, _ = oracle([(0, 10), (3, 7.5), (6, 7), (10, 0)])
    assert supported_points(best_for) == [(0, 10), (6, 7), (10, 0)]


def test_a_point_with_a_narrow_range_of_shares_is_found():
    # (4, 8) is best only for shares between 1/3 and 0.375
    best_for, _ = oracle([(0, 10), (2, 8.5), (4, 8), (9, 5), (10, 0)])
    assert supported_points(best_for) == [(0, 10), (4, 8), (9, 5), (10, 0)]


def test_the_search_continues_on_both_sides_of_each_new_point():
    best_for, _ = oracle([(0, 10), (4, 9), (5, 6.5), (7, 6), (9, 2.5), (10, 0)])
    assert supported_points(best_for) == [(0, 10), (4, 9), (7, 6), (9, 2.5), (10, 0)]


def test_a_single_best_option_is_returned_once():
    best_for, _ = oracle([(5, 5), (1, 1), (4, 2)])
    assert supported_points(best_for) == [(5, 5)]
