"""A trim takes weeks on one crew (lesson 14.1.3)."""

from vegcrew.data import season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import crew_ids, horizon, make_plan
from test_planner import season


def two_crews():
    """The tiny season with a second crew: small enough to solve in a moment, with a crew to choose."""
    raw = scenario("tiny")
    raw["crews"] = 2
    return season_from_dict(raw)


def test_each_trim_runs_on_one_crew_for_its_weeks():
    s = two_crews()
    plan = make_plan(s)
    assert plan.status == "OPTIMAL" and plan.trims
    for t in plan.trims.values():
        assert t.crew in crew_ids(s)
        assert 0 <= t.start and t.end == t.start + s.circuit(t.cid).weeks <= horizon(s)


def test_no_crew_works_two_circuits_at_once():
    s = two_crews()
    plan = make_plan(s)
    for k in crew_ids(s):
        weeks = [w for t in plan.trims.values() if t.crew == k for w in range(t.start, t.end)]
        assert len(weeks) == len(set(weeks))
    assert sum(t.end - t.start for t in plan.trims.values()) == sum(s.circuit(c).weeks for c in plan.trims)
    assert all(t.end > t.start for t in plan.trims.values())


def test_a_trim_longer_than_a_month_runs_across_two():
    plan = make_plan(season(1000, ("A", 10, 50, 6), crews=1, months=2))
    assert sorted(plan.trims) == ["A"]
    assert plan.trims["A"].end - plan.trims["A"].start == 6


def test_two_crews_cannot_share_one_trim():
    # 8 crew-weeks in the month, but a 6-week trim on one crew does not fit in 4 weeks.
    plan = make_plan(season(1000, ("A", 10, 50, 6), crews=2, months=1))
    assert (plan.status, plan.trims) == ("OPTIMAL", {})


def test_crews_can_stop_a_plan_the_budget_allows():
    plan = make_plan(season(1000, ("A", 10, 50, 3), ("B", 10, 40, 3), crews=1, months=1))
    assert (plan.status, sorted(plan.trims)) == ("OPTIMAL", ["A"])


def test_one_crew_does_two_trims_one_after_the_other():
    plan = make_plan(season(1000, ("A", 10, 50, 3), ("B", 10, 40, 3), crews=1, months=2))
    a, b = sorted(plan.trims.values(), key=lambda t: t.start)
    assert a.end <= b.start and {a.crew, b.crew} == {"K1"}
