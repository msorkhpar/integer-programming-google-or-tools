from warm import build, parameters, replan

# A bakery's two vans and six cafes, not the lesson's substations.
DISTANCE = [
    [0, 6, 9, 7, 11, 8, 10],
    [6, 0, 4, 9, 7, 12, 11],
    [9, 4, 0, 6, 5, 10, 8],
    [7, 9, 6, 0, 8, 4, 5],
    [11, 7, 5, 8, 0, 9, 6],
    [8, 12, 10, 4, 9, 0, 3],
    [10, 11, 8, 5, 6, 3, 0],
]
TRAYS = [0, 3, 2, 4, 3, 2, 3]
VANS = [9, 9]
# Yesterday's plan zigzags across town: it fits both vans, but it is long.
YESTERDAY = [[1, 5, 4], [3, 2, 6]]


def drive(routes):
    return sum(DISTANCE[a][b] for route in routes for a, b in zip([0, *route], [*route, 0]))


def test_yesterdays_routes_are_priced_and_searched_from():
    manager, routing = build(DISTANCE, TRAYS, VANS)
    start, solution = replan(routing, YESTERDAY, parameters())
    assert start == drive(YESTERDAY)
    assert solution is not None and solution.ObjectiveValue() <= start


def test_the_search_improves_on_yesterday():
    manager, routing = build(DISTANCE, TRAYS, VANS)
    start, solution = replan(routing, YESTERDAY, parameters())
    assert start == drive(YESTERDAY)
    assert solution.ObjectiveValue() < start


def test_routes_that_no_longer_fit_fall_back_to_a_fresh_solve():
    smaller = [10, 8]      # van 1 is in the workshop; the spare holds 8 trays, and van 0 now takes 10
    manager, routing = build(DISTANCE, TRAYS, smaller)
    start, solution = replan(routing, YESTERDAY, parameters())
    assert start is None
    assert solution is not None and solution.ObjectiveValue() > 0
