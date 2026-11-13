from storage import Site, cheapest_cover

# A transmission operator's candidate battery sites, not the lesson's portfolio.


def check(answer, sites, need):
    """The answer's set really reaches the need and really costs what the answer says."""
    cost, names = answer
    chosen = [s for s in sites if s.name in names]
    assert len(chosen) == len(names) == len(set(names))
    assert sum(s.mwh for s in chosen) >= need
    assert sum(s.cost for s in chosen) == cost


def test_the_cheapest_set_reaching_the_need_is_found():
    sites = [Site("A", 4, 20), Site("B", 5, 24), Site("C", 3, 17), Site("D", 6, 33)]
    answer = cheapest_cover(sites, 9)
    assert answer is not None and answer[0] == 44       # A + B: 9 MWh, cheaper than C + D (50)
    check(answer, sites, 9)


def test_the_answer_names_the_sites_it_pays_for():
    sites = [Site("Ridge", 4, 25), Site("Mill", 3, 19), Site("Ferry", 5, 30), Site("Gate", 2, 15)]
    answer = cheapest_cover(sites, 7)
    assert answer is not None and answer[0] == 44       # Ridge + Mill: 7 MWh
    check(answer, sites, 7)
    assert answer[1] == ["Ridge", "Mill"]


def test_a_need_no_set_can_reach_has_no_answer():
    assert cheapest_cover([], 5) is None
    sites = [Site("A", 3, 10), Site("B", 4, 12)]
    assert cheapest_cover(sites, 7) == (22, ["A", "B"])


def test_each_site_is_bought_at_most_once():
    sites = [Site("Small", 4, 10), Site("Big", 8, 30)]
    answer = cheapest_cover(sites, 8)
    assert answer == (30, ["Big"])                      # Small twice would be 20, but there is one Small


def test_overshooting_the_need_is_allowed():
    sites = [Site("A", 6, 10), Site("B", 6, 10), Site("C", 12, 25)]
    answer = cheapest_cover(sites, 10)
    assert answer is not None and answer[0] == 20       # A + B give 12 MWh, more than 10, for 20
    check(answer, sites, 10)


def test_a_need_of_zero_is_met_by_building_nothing():
    sites = [Site("A", 3, 10), Site("B", 4, 12)]
    assert cheapest_cover(sites, 0) == (0, [])          # nothing to add costs nothing; it is not "no answer"
    assert cheapest_cover(sites, 4) == (12, ["B"])
