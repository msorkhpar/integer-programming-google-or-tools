from generators import most_delivered


def test_the_routes_limit_what_arrives():
    stock = {"North yard": 10, "South yard": 10}
    needs = {"Elm": 8, "Oak": 8}
    routes = {("North yard", "Elm"): 5, ("North yard", "Oak"): 2, ("South yard", "Oak"): 4}
    assert most_delivered(stock, needs, routes) == 11      # 5 + 2 + 4: every route full


def test_a_yard_sends_no_more_than_it_holds():
    stock = {"North yard": 3, "South yard": 10}
    needs = {"Elm": 8, "Oak": 8}
    routes = {("North yard", "Elm"): 5, ("North yard", "Oak"): 5, ("South yard", "Oak"): 4}
    assert most_delivered(stock, needs, routes) == 7       # 3 from North, 4 from South


def test_a_town_takes_no_more_than_it_needs():
    stock = {"North yard": 10, "South yard": 10}
    needs = {"Elm": 2, "Oak": 8}
    routes = {("North yard", "Elm"): 5, ("North yard", "Oak"): 2, ("South yard", "Oak"): 4}
    assert most_delivered(stock, needs, routes) == 8       # Elm takes 2, Oak 2 + 4


def test_units_may_pass_through_a_depot_that_holds_none():
    stock = {"North yard": 10}
    needs = {"Elm": 6, "Oak": 6}
    routes = {("North yard", "Depot"): 7, ("Depot", "Elm"): 4, ("Depot", "Oak"): 4, ("North yard", "Elm"): 1}
    assert most_delivered(stock, needs, routes) == 8       # 7 through the depot, 1 direct
