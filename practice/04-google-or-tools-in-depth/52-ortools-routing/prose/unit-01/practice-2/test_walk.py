from itertools import permutations

from walk import solve_tour

# A pest-control van's six customers and its base, not the lesson's substations.
VAN = [
    [0, 12, 10, 19, 8, 14, 11],
    [12, 0, 3, 7, 2, 9, 13],
    [10, 3, 0, 6, 20, 4, 8],
    [19, 7, 6, 0, 4, 5, 15],
    [8, 2, 20, 4, 0, 11, 6],
    [14, 9, 4, 5, 11, 0, 7],
    [11, 13, 8, 15, 6, 7, 0],
]


def best_cost(cost, depot):
    others = [n for n in range(len(cost)) if n != depot]
    return min(sum(cost[a][b] for a, b in zip((depot, *order), (*order, depot))) for order in permutations(others))


def test_the_tour_visits_every_stop_once_from_the_depot():
    tour, _ = solve_tour(VAN, 0)
    assert tour[0] == tour[-1] == 0
    assert sorted(tour[1:-1]) == [1, 2, 3, 4, 5, 6]


def test_the_total_counts_every_arc_including_the_drive_back():
    tour, total = solve_tour(VAN, 0)
    assert total == sum(VAN[a][b] for a, b in zip(tour, tour[1:]))
    assert total == best_cost(VAN, 0)


def test_a_depot_that_is_not_node_0():
    tour, total = solve_tour(VAN, 3)
    assert tour[0] == tour[-1] == 3
    assert sorted(tour[1:-1]) == [0, 1, 2, 4, 5, 6]
    assert total == best_cost(VAN, 3)
