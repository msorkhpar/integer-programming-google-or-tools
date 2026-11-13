"""Risk grows while a circuit waits (lesson 14.1.4)."""

from vegcrew.data import season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import horizon, make_plan
from rules import DEFER_WEEKS, carried
from test_planner import season


def test_the_fast_growing_circuit_goes_first():
    # One crew, two 4-week trims. A carries $10k a week, flat; B starts at $2k and grows by $3k a week.
    # A first: 40 + (16 + 84) = 140. B first: (8 + 18) + 80 = 106.
    plan = make_plan(season(1000, ("A", 10, 520, 4, 0), ("B", 10, 104, 4, 3), crews=1, months=2))
    assert plan.risk_carried == 106
    assert (plan.trims["B"].start, plan.trims["A"].start) == (0, 4)


def test_waiting_risk_can_change_which_circuit_is_trimmed():
    # Room for one 4-week trim. A removes more risk in a year; B's risk grows so fast that leaving it
    # for next season costs more than leaving A.
    plan = make_plan(season(1000, ("A", 10, 520, 4, 0), ("B", 10, 260, 4, 3), crews=1, months=1))
    assert sorted(plan.trims) == ["B"]


def test_the_risk_carried_is_each_circuits_risk_until_its_trim_ends():
    raw = scenario("tiny")
    raw["crews"] = 2
    s = season_from_dict(raw)
    plan = make_plan(s)
    assert plan.status == "OPTIMAL" and plan.trims
    expected = sum(carried(c, plan.trims[c["id"]].end) if c["id"] in plan.trims
                   else carried(c, horizon(s) + DEFER_WEEKS) for c in raw["circuits"])
    assert plan.risk_carried > 0 and plan.risk_carried == expected
