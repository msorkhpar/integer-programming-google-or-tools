from refusals import Limit, full_but_not_tight, refusals

LIMITS = [
    Limit("capital_fund", {"roof_east": 180, "roof_west": 150, "boiler": 220, "windows": 90, "paving": 60,
                           "resurface": 50}, 500),
    Limit("crew_weeks", {"roof_east": 6, "roof_west": 5, "boiler": 4, "windows": 3, "paving": 1, "resurface": 2}, 12),
    Limit("one_roof_crew", {"roof_east": 1, "roof_west": 1}, 1),
    Limit("asphalt_fund", {"paving": 60, "resurface": 50}, 100),
]
PLAN = {"roof_east", "boiler"}      # capital 400 of 500, crew 10 of 12, one roof of 1, asphalt 0 of 100


def test_each_candidate_is_tried_alone_on_top_of_the_plan():
    plan = {"boiler", "paving"}     # capital 280 of 500, crew 5 of 12, no roof, asphalt 60 of 100
    assert refusals(LIMITS, plan, ["windows", "resurface"]) == {"windows": [], "resurface": ["asphalt_fund"]}


def test_a_limit_filled_exactly_is_not_broken():
    limits = [Limit("crew_weeks", {"roof_east": 6, "boiler": 4, "gutters": 2}, 12)]
    assert refusals(limits, PLAN, ["gutters"]) == {"gutters": []}


def test_every_limit_a_candidate_breaks_is_listed():
    assert refusals(LIMITS, PLAN, ["roof_west", "paving"]) == {
        "roof_west": ["capital_fund", "crew_weeks", "one_roof_crew"], "paving": []}


def test_a_limit_with_no_room_left_is_not_counted_as_full_but_not_tight():
    assert full_but_not_tight(LIMITS, PLAN, ["roof_west"]) == ["capital_fund", "crew_weeks"]


def test_a_limit_with_room_that_refuses_nothing_is_left_out():
    assert full_but_not_tight(LIMITS, PLAN, ["windows", "paving"]) == ["crew_weeks"]
