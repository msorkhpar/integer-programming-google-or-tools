from shifts import build

# A home-care agency's nurses and five patients, not the lesson's substations. Minutes.
DRIVE = [
    [0, 10, 15, 20, 12, 18],
    [10, 0, 8, 25, 14, 22],
    [15, 8, 0, 9, 20, 16],
    [20, 25, 9, 0, 11, 7],
    [12, 14, 20, 11, 0, 9],
    [18, 22, 16, 7, 9, 0],
]


def allowed(shifts, routes):
    manager, routing = build(DRIVE, shifts)
    return routing.ReadAssignmentFromRoutes(routes, True) is not None


def test_routes_within_every_shift_are_allowed_and_one_over_is_refused():
    # 0-1-2-0 drives 10 + 8 + 15 = 33; 0-3-5-4-0 drives 20 + 7 + 9 + 12 = 48.
    assert allowed([50, 50], [[1, 2], [3, 5, 4]]) is True
    # 0-1-2-3-5-4-0 drives 10 + 8 + 9 + 7 + 9 + 12 = 55.
    assert allowed([50, 50], [[1, 2, 3, 5, 4], []]) is False


def test_a_part_time_crew_has_its_own_shorter_limit():
    assert allowed([50, 40], [[3, 5, 4], [1, 2]]) is True
    assert allowed([50, 40], [[1, 2], [3, 5, 4]]) is False


def test_a_route_exactly_at_the_limit_is_allowed():
    assert allowed([48, 33], [[3, 5, 4], [1, 2]]) is True
    assert allowed([47, 33], [[3, 5, 4], [1, 2]]) is False
