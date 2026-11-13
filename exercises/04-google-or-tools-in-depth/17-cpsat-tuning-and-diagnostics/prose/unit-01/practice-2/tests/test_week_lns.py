from week_lns import Job, lns, value

# A utility's substation inspections, not the lesson's portfolio.
WEEK = [Job("N1", "north", 50, 20), Job("N2", "north", 40, 10), Job("N3", "north", 30, 15),
        Job("S3", "south", 20, 5), Job("S4", "south", 35, 5), Job("E2", "east", 25, 10)]
NORTH, SOUTH, EAST = {"N1", "N2", "N3"}, {"S3", "S4"}, {"E2"}
START = {"N3", "S3", "E2"}


def test_the_history_starts_at_the_start_and_never_falls():
    plan, history = lns(WEEK, 50, START, [EAST, NORTH, EAST])
    assert history[0] == value(WEEK, START) == 75
    assert len(history) == 4
    assert all(a <= b for a, b in zip(history, history[1:]))
    assert history[-1] == value(WEEK, plan)


def test_no_rounds_returns_the_start_plan():
    plan, history = lns(WEEK, 50, START, [])
    assert plan == START and history == [75]


def test_each_round_starts_from_the_plan_the_last_round_left():
    plan, history = lns(WEEK, 50, START, [NORTH, SOUTH])
    assert history == [75, 135, 170]
    assert plan == {"N1", "N2", "S3", "S4", "E2"}
