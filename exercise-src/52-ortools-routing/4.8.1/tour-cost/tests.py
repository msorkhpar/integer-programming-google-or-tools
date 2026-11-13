from tour import build, scaled

# A meter reader's loop through five streets, not the lesson's substations.
STREETS = [
    [0, 7, 9, 8, 6],
    [7, 0, 4, 9, 8],
    [9, 4, 0, 5, 9],
    [8, 9, 5, 0, 3],
    [6, 8, 9, 3, 0],
]
# One-way streets: driving 1 -> 2 is short, 2 -> 1 is a long way round.
ONE_WAY = [
    [0, 5, 9, 6],
    [8, 0, 2, 9],
    [3, 11, 0, 4],
    [5, 7, 10, 0],
]


def tour_cost(cost, depot, stops):
    """What the model charges for the tour depot -> stops -> depot, or None if it refuses the tour."""
    manager, routing = build(cost, depot)
    plan = routing.ReadAssignmentFromRoutes([stops], True)
    return None if plan is None else plan.ObjectiveValue()


def test_a_tour_costs_the_sum_of_its_arcs():
    assert tour_cost(STREETS, 0, [1, 2, 3, 4]) == 7 + 4 + 5 + 3 + 6
    assert tour_cost(STREETS, 0, [2, 1, 4, 3]) == 9 + 4 + 8 + 3 + 8


def test_one_way_streets_are_priced_in_the_driving_direction():
    assert tour_cost(ONE_WAY, 0, [1, 2, 3]) == 5 + 2 + 4 + 5
    assert tour_cost(ONE_WAY, 0, [3, 2, 1]) == 6 + 10 + 11 + 8


def test_a_depot_that_is_not_node_0():
    assert tour_cost(STREETS, 3, [4, 0, 1, 2]) == 3 + 6 + 7 + 4 + 5


def test_scaled_costs_are_integers():
    grid = scaled([[0, 1.5], [2.25, 0]], 100)
    assert grid == [[0, 150], [225, 0]]
    assert all(type(c) is int for row in grid for c in row)


def test_scaling_rounds_to_the_nearest_integer():
    assert scaled([[0, 1.97], [0.29, 0]], 10) == [[0, 20], [3, 0]]
    assert scaled([[0, 0.29]], 100) == [[0, 29]]
