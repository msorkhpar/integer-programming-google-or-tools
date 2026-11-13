from renewal.check import violations
from renewal.fleet import generate_fleet
from renewal.plan import plan
from renewal.request import Request
from renewal.rolling import rolling

REQUEST = Request(budget=1500, years=3, window=8, min_age=35, outage_cost=300, outages=2,
                  crew_weeks=8, lead_times=True, spares={"medium": 1, "large": 1})


def test_a_rolling_plan_keeps_every_rule_and_most_of_the_value():
    fleet = generate_fleet(30, seed=3)
    got = rolling(fleet, REQUEST, window=2, keep=1)
    assert got.replace and violations(fleet, REQUEST, got.replace) == []
    assert got.value >= 0.9 * plan(fleet, REQUEST).value


def test_one_window_over_the_whole_plan_is_the_full_model():
    fleet = generate_fleet(30, seed=3)
    assert abs(rolling(fleet, REQUEST, window=3, keep=3).value - plan(fleet, REQUEST).value) < 1e-6
