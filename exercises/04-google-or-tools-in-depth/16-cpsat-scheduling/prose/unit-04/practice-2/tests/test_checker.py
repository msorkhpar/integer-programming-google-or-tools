from checker import broken_rules

JOBS = {"drill": (2, 2, [(0, 3), (6, 9)]), "paint": (3, 1, None), "hang": (1, 3, None)}


def test_a_plan_that_keeps_every_rule_breaks_none():
    assert broken_rules(JOBS, {"drill": 0, "paint": 0, "hang": 4}, 3, 10) == set()


def test_work_past_the_horizon_is_reported():
    assert broken_rules(JOBS, {"drill": 0, "paint": 8, "hang": 4}, 3, 10) == {("outside", "paint")}
    assert broken_rules(JOBS, {"drill": 0, "paint": 0, "hang": -1}, 3, 10) == {("outside", "hang")}


def test_a_job_ending_as_its_window_closes_is_inside():
    # drill on days 1-2 ends at 3, as the first closure does: inside.
    assert broken_rules(JOBS, {"drill": 1, "paint": 3, "hang": 9}, 3, 10) == set()
    # drill on days 2-3 runs past the first closure and starts before the second.
    assert broken_rules(JOBS, {"drill": 2, "paint": 4, "hang": 9}, 3, 10) == {("window", "drill")}


def test_a_crowded_day_counts_installers_not_jobs():
    # Day 4: paint (1) and hang (3) need 4 installers; the team has 3.
    assert broken_rules(JOBS, {"drill": 0, "paint": 3, "hang": 4}, 3, 10) == {("crowded", 4)}
