from optional import build, skipped, solve

# A grocery's two vans and five orders, not the lesson's substations.
DISTANCE = [
    [0, 9, 7, 8, 12, 10],
    [9, 0, 4, 11, 6, 13],
    [7, 4, 0, 6, 8, 9],
    [8, 11, 6, 0, 10, 3],
    [12, 6, 8, 10, 0, 7],
    [10, 13, 9, 3, 7, 0],
]
CRATES = [0, 4, 3, 5, 2, 3]       # 17 crates ordered, and the two vans carry 8 each
VANS = [8, 8]
PENALTIES = {2: 50, 4: 30, 5: 40}  # orders 1 and 3 are prepaid and must go out today


def drive(routes):
    return sum(DISTANCE[a][b] for route in routes for a, b in zip([0, *route], [*route, 0]))


def cost(routes):
    manager, routing = build(DISTANCE, CRATES, VANS, PENALTIES)
    plan = routing.ReadAssignmentFromRoutes(routes, True)
    return None if plan is None else plan.ObjectiveValue()


def test_an_optional_order_may_be_skipped_at_its_penalty():
    assert cost([[1, 4], [3, 5]]) == drive([[1, 4], [3, 5]]) + 50


def test_a_required_order_is_never_skipped():
    assert cost([[1, 4], [3, 5]]) is not None
    assert cost([[1, 2], [4, 5]]) is None


def test_each_order_is_skipped_at_its_own_penalty():
    assert cost([[1, 2], [3, 5]]) == drive([[1, 2], [3, 5]]) + 30


def test_skipped_lists_every_order_on_no_route():
    manager, routing = build(DISTANCE, CRATES, VANS, PENALTIES)
    solution = solve(routing)
    assert solution is not None
    on_routes = set()
    for van in range(len(VANS)):
        index = solution.Value(routing.NextVar(routing.Start(van)))
        while not routing.IsEnd(index):
            on_routes.add(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
    missing = sorted(set(range(1, len(DISTANCE))) - on_routes)
    assert missing and skipped(routing, manager, solution) == missing
