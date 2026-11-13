from shipping import ship

ROUTES = {("North yard", "Elm"): (4, 10), ("North yard", "Depot"): (1, 10), ("South yard", "Depot"): (2, 10),
          ("South yard", "Oak"): (6, 10), ("Depot", "Elm"): (1, 10), ("Depot", "Oak"): (2, 10)}


def test_a_balanced_shipment_takes_the_cheapest_routes():
    plan = ship({"North yard": 5, "South yard": 5}, {"Elm": 5, "Oak": 5}, ROUTES)
    assert plan is not None
    cost, flows = plan
    assert cost == 30                     # every unit through the depot
    assert flows[("North yard", "Depot")] == 5 and flows[("South yard", "Depot")] == 5
    assert flows[("Depot", "Elm")] == 5 and flows[("Depot", "Oak")] == 5


def test_stock_left_in_the_yards_is_allowed():
    plan = ship({"North yard": 9, "South yard": 9}, {"Elm": 5, "Oak": 5}, ROUTES)
    assert plan is not None
    cost, flows = plan
    assert cost == 26                     # North sends all 9 through the depot, South 1
    assert flows[("North yard", "Depot")] == 9 and flows[("South yard", "Depot")] == 1


def test_needs_that_cannot_all_be_met_give_no_plan():
    narrow = {**ROUTES, ("Depot", "Oak"): (2, 1), ("South yard", "Oak"): (6, 2)}   # at most 3 reach Oak
    assert ship({"North yard": 5, "South yard": 5}, {"Elm": 5, "Oak": 5}, narrow) is None


def test_routes_left_empty_are_not_listed():
    plan = ship({"North yard": 5, "South yard": 5}, {"Elm": 5, "Oak": 5}, ROUTES)
    assert plan is not None
    assert ("North yard", "Elm") not in plan[1] and ("South yard", "Oak") not in plan[1]
