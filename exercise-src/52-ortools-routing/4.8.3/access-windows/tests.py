from windows import build

# A lift-maintenance engineer's four buildings, not the lesson's substations. Minutes.
TRAVEL = [
    [0, 10, 20, 15, 25],
    [10, 0, 12, 18, 20],
    [20, 12, 0, 10, 14],
    [15, 18, 10, 0, 9],
    [25, 20, 14, 9, 0],
]
SERVICE = [0, 30, 30, 30, 30]      # minutes of work in each building
WIDE = (0, 300)


def allowed(windows, plan, shift_end=300, max_wait=60):
    manager, routing = build(TRAVEL, SERVICE, windows, shift_end, max_wait)
    return routing.ReadAssignmentFromRoutes([plan], True) is not None


def test_a_plan_inside_every_window_is_allowed_and_a_late_one_refused():
    windows = {1: (0, 60), 2: (40, 120), 3: (60, 200), 4: (100, 240)}
    # 1 at 10, 2 at 52, 3 at 92, 4 at 131: all inside.
    assert allowed(windows, [1, 2, 3, 4]) is True
    # 4 no earlier than 100, then 3 at 139 and 2 at 179, after building 2 closes at 120.
    assert allowed(windows, [4, 3, 2, 1]) is False


def test_the_work_in_a_building_delays_the_next_arrival():
    windows = {1: (0, 100), 2: (0, 50), 3: WIDE, 4: WIDE}
    # 2 at 20; 30 minutes of work and 12 of travel put 1 at 62.
    assert allowed(windows, [2, 1, 3, 4]) is True
    # 1 at 10; 30 minutes of work and 12 of travel put 2 at 52, after it closes at 50.
    assert allowed(windows, [1, 2, 3, 4]) is False


def test_the_engineer_may_wait_between_buildings():
    windows = {1: (0, 15), 2: (100, 150), 3: WIDE, 4: WIDE}
    # 1 by 15, done by 45, at 2 by 57: 43 minutes of waiting before building 2 opens at 100.
    assert allowed(windows, [1, 2, 3, 4]) is True
    # 2 no earlier than 100, so 1 no earlier than 142, long after it closes at 15.
    assert allowed(windows, [2, 1, 3, 4]) is False


def test_the_engineer_is_back_by_the_end_of_the_shift():
    windows = {node: (0, 180) for node in (1, 2, 3, 4)}
    # 3-4-2-1 travels 15 + 9 + 14 + 12 + 10 = 60 and works 120: back at 180.
    assert allowed(windows, [3, 4, 2, 1], shift_end=180) is True
    # 1-2-3-4 travels 10 + 12 + 10 + 9 + 25 = 66 and works 120: back at 186.
    assert allowed(windows, [1, 2, 3, 4], shift_end=180) is False
