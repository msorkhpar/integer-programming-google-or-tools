"""Crews and months: a month's work fits the crews who do it (lesson 14.1.2)."""

from vegcrew.data import WEEKS_PER_MONTH, season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import make_plan
from test_planner import season


def test_no_month_has_more_work_than_its_crews_can_do():
    raw = scenario("small")
    plan = make_plan(season_from_dict(raw))
    assert plan.status == "OPTIMAL" and plan.trims
    assert all(1 <= t.month <= raw["months"] for t in plan.trims.values())
    weeks = {c["id"]: c["weeks"] for c in raw["circuits"]}
    for m in range(1, raw["months"] + 1):
        work = sum(weeks[cid] for cid, t in plan.trims.items() if t.month == m)
        assert work <= raw["crews"] * WEEKS_PER_MONTH


def test_crews_can_stop_a_plan_the_budget_allows():
    # Money for both, but one crew for one month does 4 crew-weeks: only one 3-week trim fits.
    s = season(1000, ("A", 10, 50, 3), ("B", 10, 40, 3), crews=1, months=1)
    plan = make_plan(s)
    assert (plan.status, sorted(plan.trims)) == ("OPTIMAL", ["A"])


def test_a_second_month_takes_the_trim_the_first_cannot():
    s = season(1000, ("A", 10, 50, 3), ("B", 10, 40, 3), crews=1, months=2)
    plan = make_plan(s)
    assert sorted(plan.trims) == ["A", "B"]
    assert {t.month for t in plan.trims.values()} == {1, 2}
