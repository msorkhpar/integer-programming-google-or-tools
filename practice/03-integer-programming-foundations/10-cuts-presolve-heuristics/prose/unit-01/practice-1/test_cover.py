from cover import find_cover


def check_violated_cover(cover, hours, window, y):
    assert cover is not None, "a violated cover exists here"
    assert set(cover) <= set(hours) and len(set(cover)) == len(cover)
    assert sum(hours[j] for j in cover) > window, "the jobs must take more hours than the window"
    assert sum(1 - y[j] for j in cover) < 1, "the point must break the cover inequality"


def test_finds_a_violated_cover_with_one_fractional_job():
    hours = {"J1": 5, "J2": 4, "J3": 3, "J4": 2}
    y = {"J1": 1, "J2": 1, "J3": 1 / 3, "J4": 0}
    check_violated_cover(find_cover(hours, 10, y), hours, 10, y)


def test_finds_a_violated_cover_with_two_fractional_jobs():
    hours = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2}
    y = {"A": 1, "B": 0.8, "C": 0.5, "D": 0, "E": 0}
    check_violated_cover(find_cover(hours, 12, y), hours, 12, y)


def test_the_cover_is_minimal():
    hours = {"A": 2, "B": 3, "C": 9}
    y = {"A": 1, "B": 1, "C": 5 / 9}
    cover = find_cover(hours, 10, y)
    check_violated_cover(cover, hours, 10, y)
    for k in cover:
        assert sum(hours[j] for j in cover) - hours[k] <= 10, f"still a cover without {k}: not minimal"


def test_jobs_that_exactly_fill_the_window_are_not_a_cover():
    hours = {"A": 4, "B": 3, "C": 3}
    assert find_cover(hours, 10, {"A": 1, "B": 1, "C": 1}) is None


def test_none_when_the_point_breaks_no_cover():
    hours = {"A": 5, "B": 4, "C": 3}
    assert find_cover(hours, 10, {"A": 1, "B": 1, "C": 0}) is None
