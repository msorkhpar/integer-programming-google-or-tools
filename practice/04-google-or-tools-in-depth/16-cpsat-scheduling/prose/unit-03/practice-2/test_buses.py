from buses import buy_routes


def check(routes, offers, city_limit, total, plan):
    """Assert the plan keeps every rule and costs `total`."""
    assert set(plan) == set(routes)
    for r, offer in plan.items():
        assert tuple(offer) in offers, f"{r} takes {offer}, which nobody offers"
        assert offer[0] >= routes[r], f"{r} has {routes[r]} riders and a {offer[0]}-seat bus"
    assert sum(offer[1] for offer in plan.values()) <= city_limit
    assert total == sum(offer[2] for offer in plan.values())


def test_each_route_gets_the_cheapest_bus_that_fits():
    offers = [(30, 0, 100), (30, 1, 100), (50, 0, 140), (50, 1, 140), (70, 0, 200)]
    routes = {"hill": 25, "river": 45, "mill": 60}
    total, plan = buy_routes(routes, offers, 3)
    assert total == 440
    assert {r: o[0] for r, o in plan.items()} == {"hill": 30, "river": 50, "mill": 70}


def test_every_route_gets_an_offer():
    offers = [(30, 0, 100), (50, 1, 120)]
    total, plan = buy_routes({"hill": 40}, offers, 1)
    assert tuple(plan["hill"]) in offers and plan["hill"][0] >= 40


def test_a_price_belongs_to_its_offer():
    offers = [(30, 0, 100), (30, 1, 60)]
    routes = {"hill": 20, "river": 25}
    # The city runs one route at 60; the other route pays the private price, 100.
    total, plan = buy_routes(routes, offers, 1)
    check(routes, offers, 1, total, plan)
    assert total == 160


def test_the_city_takes_no_more_routes_than_its_limit():
    offers = [(30, 0, 100), (30, 1, 70), (50, 0, 150), (50, 1, 110)]
    routes = {"hill": 25, "river": 40, "mill": 28}
    total, plan = buy_routes(routes, offers, 1)
    check(routes, offers, 1, total, plan)
    # The city's one route is best spent on river (saves 40): 100 + 110 + 100.
    assert total == 310
