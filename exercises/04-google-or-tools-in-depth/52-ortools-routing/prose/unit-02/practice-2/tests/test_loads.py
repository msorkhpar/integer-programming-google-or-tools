from loads import build

# A brewery's two delivery trucks and five pubs, not the lesson's substations.
DISTANCE = [
    [0, 6, 8, 5, 9, 7],
    [6, 0, 3, 7, 8, 9],
    [8, 3, 0, 6, 4, 8],
    [5, 7, 6, 0, 5, 3],
    [9, 8, 4, 5, 0, 6],
    [7, 9, 8, 3, 6, 0],
]
KEGS = [0, 3, 2, 4, 1, 2]           # kegs each pub takes
KG = [0, 150, 300, 120, 400, 100]   # kilograms of bottled stock each pub takes


def allowed(routes, demands, capacities):
    manager, routing = build(DISTANCE, 2, demands, capacities)
    return routing.ReadAssignmentFromRoutes(routes, True) is not None


def test_a_truck_may_carry_up_to_its_capacity_and_no_more():
    kegs_only = {"kegs": KEGS}
    assert allowed([[1, 2, 4], [3, 5]], kegs_only, {"kegs": [6, 6]}) is True
    assert allowed([[1, 2, 3], [4, 5]], kegs_only, {"kegs": [6, 6]}) is False


def test_every_kind_of_load_has_its_own_limit():
    both = {"kegs": KEGS, "kg": KG}
    assert allowed([[1, 3], [2, 4, 5]], both, {"kegs": [8, 8], "kg": [800, 800]}) is True
    assert allowed([[1, 3], [2, 4, 5]], both, {"kegs": [8, 8], "kg": [800, 700]}) is False


def test_each_kind_is_counted_with_its_own_demands():
    both = {"kegs": KEGS, "kg": KG}
    assert allowed([[1, 2, 3], [4, 5]], both, {"kegs": [9, 9], "kg": [600, 600]}) is True
    assert allowed([[1, 2, 3], [4, 5]], both, {"kegs": [8, 9], "kg": [600, 600]}) is False


def test_a_smaller_truck_has_a_smaller_limit():
    kegs_only = {"kegs": KEGS}
    assert allowed([[1, 3], [2, 4, 5]], kegs_only, {"kegs": [7, 5]}) is True
    assert allowed([[2, 4, 5], [1, 3]], kegs_only, {"kegs": [7, 5]}) is False
