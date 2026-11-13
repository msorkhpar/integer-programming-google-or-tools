from packages import accepted

ROADS = {
    "elm":   {"safety": 50.0, "cost": 4.0, "noise": -1.0, "jobs": 10.0},
    "oak":   {"safety": 50.0, "cost": 3.5, "noise": -5.0, "jobs": 12.0},
    "ash":   {"safety": 48.0, "cost": 1.0, "noise": -4.0, "jobs": 20.0},
    "birch": {"safety": 40.0, "cost": 2.0, "noise": -2.0, "jobs": 30.0},
}


def test_with_no_tolerance_each_level_keeps_only_its_best():
    assert accepted(ROADS, [("safety", True, 0.0, 0.0), ("noise", True, 0.0, 0.0)]) == ["elm"]


def test_a_relative_tolerance_lets_the_next_level_choose():
    # 5% of 50 lets safety fall to 47.5, so ash is still accepted and wins on cost.
    assert accepted(ROADS, [("safety", True, 0.0, 0.05), ("cost", False, 0.0, 0.0)]) == ["ash"]


def test_each_best_is_taken_among_the_packages_still_accepted():
    # birch creates the most jobs, but safety removed it; the best survivor is ash.
    assert accepted(ROADS, [("safety", True, 2.0, 0.0), ("jobs", True, 0.0, 0.0)]) == ["ash"]


def test_a_minimized_level_may_rise_by_its_tolerance():
    levels = [("safety", True, 2.0, 0.0), ("cost", False, 2.6, 0.0)]
    assert accepted(ROADS, levels) == ["ash", "oak"]


def test_a_relative_tolerance_uses_the_size_of_a_negative_best():
    # The best noise score is -1.0 (elm); 300% of its size allows down to -4.0.
    assert accepted(ROADS, [("noise", True, 0.0, 3.0)]) == ["ash", "birch", "elm"]
