from itertools import permutations

from sites import assign


def brute_force(crews, sites, cost):
    """The cheapest assignment by trying every ordering of the crews."""
    best = None
    for order in permutations(crews, len(sites)):
        pairs = list(zip(order, sites))
        if all(p in cost for p in pairs):
            total = sum(cost[p] for p in pairs)
            if best is None or total < best:
                best = total
    return best


def check(crews, sites, cost):
    result = assign(crews, sites, cost)
    want = brute_force(crews, sites, cost)
    if want is None:
        assert result is None
        return
    assert result is not None
    total, plan = result
    assert total == want
    assert sorted(plan.values()) == sorted(sites)
    assert all((crew, site) in cost for crew, site in plan.items())
    assert sum(cost[crew, site] for crew, site in plan.items()) == total


CREWS = ["Ash", "Birch", "Cedar"]
SITES = ["dam", "mill", "weir"]
FULL = {("Ash", "dam"): 8, ("Ash", "mill"): 4, ("Ash", "weir"): 7,
        ("Birch", "dam"): 5, ("Birch", "mill"): 2, ("Birch", "weir"): 3,
        ("Cedar", "dam"): 9, ("Cedar", "mill"): 4, ("Cedar", "weir"): 8}


def test_every_crew_gets_a_site_at_least_cost():
    check(CREWS, SITES, FULL)
    assert assign(CREWS, SITES, FULL)[0] == 15


def test_a_forbidden_pair_is_never_used():
    allowed = {pair: c for pair, c in FULL.items() if pair not in {("Birch", "mill"), ("Ash", "mill")}}
    check(CREWS, SITES, allowed)


def test_spare_crews_stay_idle():
    crews = CREWS + ["Dogwood", "Elm"]
    cost = {**FULL, ("Dogwood", "dam"): 1, ("Elm", "weir"): 2}
    check(crews, SITES, cost)
    assert len(assign(crews, SITES, cost)[1]) == 3


def test_a_site_no_crew_may_take_gives_no_plan():
    allowed = {pair: c for pair, c in FULL.items() if pair[1] != "weir"}
    assert assign(CREWS, SITES, allowed) is None
