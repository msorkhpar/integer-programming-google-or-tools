from overtime import build

# Two window-cleaning crews and four office blocks, not the lesson's substations. Minutes.
TRAVEL = [
    [0, 10, 20, 15, 25],
    [10, 0, 12, 18, 20],
    [20, 12, 0, 10, 14],
    [15, 18, 10, 0, 9],
    [25, 20, 14, 9, 0],
]
SERVICE = [0, 30, 30, 30, 30]
# Route 1-2 returns at 10 + 30 + 12 + 30 + 20 = 102 after 42 minutes of travel;
# route 3-4 returns at 15 + 30 + 9 + 30 + 25 = 109 after 49 minutes of travel. Travel in all: 91.


def cost(routes, finish_by, cost_per_minute=5):
    manager, routing = build(TRAVEL, SERVICE, finish_by, cost_per_minute)
    plan = routing.ReadAssignmentFromRoutes(routes, True)
    return None if plan is None else plan.ObjectiveValue()


def test_a_crew_back_late_pays_for_each_minute_and_one_on_time_pays_nothing():
    assert cost([[3, 4], [1, 2]], [120, 120]) == 91
    assert cost([[3, 4], [1, 2]], [105, 105]) == 91 + 5 * 4


def test_every_late_crew_pays():
    assert cost([[1, 2], [3, 4]], [100, 100]) == 91 + 5 * (2 + 9)


def test_each_crew_is_measured_against_its_own_finish_time():
    assert cost([[1, 2], [3, 4]], [100, 120]) == 91 + 5 * 2
