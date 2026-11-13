"""The module 16 examples: intervals, NoOverlap, cumulative pools, element and tables, the season."""

import runpy

import pytest

from cpsat_run import solve
from schedule_check import risk, violations
from season import CREWS, HORIZON, OUTAGE_WINDOWS, jobs
from season_model import STANDBY, build, crews_per_week, minimize_lateness, minimize_makespan, starts

RULES = dict(standby=STANDBY, outages=True, one_outage_per_region=True)


def printed(program, capsys):
    """Run a program of src/ as __main__ and return what it printed."""
    runpy.run_module(program, run_name="__main__")
    return capsys.readouterr().out


@pytest.fixture(scope="module")
def season():
    return jobs()


def test_the_season_has_twelve_jobs_and_68_crew_weeks(season):
    assert len(season) == 12
    assert sum(j.weeks * j.crews for j in season) == 68
    assert sorted(j.jid for j in season if j.due == 6) == ["P004", "P006", "P008", "P011", "P012"]
    assert {j.jid for j in season if j.needs_outage} == {"P003", "P008", "P010", "P015", "P018"}


def test_an_interval_ties_the_end_to_the_start(capsys):
    out = printed("interval_basics", capsys)
    assert "with the interval:    OPTIMAL  start 3  end 5" in out
    assert "without the interval: OPTIMAL  start 3  end 0" in out


def test_one_crew_needs_14_weeks_free_and_18_with_blocks(capsys):
    out = printed("one_crew", capsys)
    assert "OPTIMAL: makespan 14 weeks" in out and "OPTIMAL: makespan 18 weeks" in out
    assert "makespan 18 weeks with 20 order Booleans" in printed("pairwise_order", capsys)


def test_the_documentation_job_shop_ends_at_11(capsys):
    assert "OPTIMAL: makespan 11 (horizon 21)" in printed("jobshop", capsys)
    assert "OPTIMAL: makespan 18 (horizon 35)" in printed("jobshop_crews", capsys)


def test_two_crews_end_at_10_and_a_shared_interval_at_19(capsys):
    out = printed("two_crews", capsys)
    assert "OPTIMAL: makespan 10 weeks" in out
    assert "one interval in both crews' lists: OPTIMAL, makespan 19 weeks" in out


@pytest.mark.parametrize("options", [{}, {"standby": STANDBY}, {"standby": STANDBY, "outages": True},
                                     RULES])
def test_every_rule_set_keeps_a_24_week_season(season, options):
    s = build(season, **options)
    minimize_makespan(s)
    solver, status = solve(s.model)
    assert status == "OPTIMAL" and solver.value(s.makespan) == 24
    start = starts(s, solver)
    profile = crews_per_week(season, start)
    for w, used in enumerate(profile):
        away = 1 if "standby" in options and 12 <= w < 16 else 0
        assert used <= CREWS - away
    if options.get("outages"):
        for j in season:
            if j.needs_outage:
                assert any(a <= start[j.jid] and start[j.jid] + j.weeks <= b for a, b in OUTAGE_WINDOWS[j.region])


def test_nooverlap_and_capacity_one_cumulative_agree(capsys):
    out = printed("nooverlap_is_cumulative", capsys)
    assert out.count("makespan 18") == 2


def test_the_nurse_roster_has_5184_schedules(capsys):
    assert "OPTIMAL: 5184 schedules" in printed("nurses", capsys)


def test_element_and_booleans_give_the_same_costs(capsys):
    element = printed("methods_element", capsys)
    booleans = printed("methods_booleans", capsys)
    for line in ("deadline week 14: OPTIMAL, cost $215k", "deadline week 8: OPTIMAL, cost $255k",
                 "deadline week 5: OPTIMAL, cost $355k"):
        assert line in element and line in booleans
    assert "size must be affine or constant" in booleans


def test_the_offer_table_prices_and_refuses(capsys):
    out = printed("methods_table", capsys)
    for line in ("deadline week 8: OPTIMAL, cost $245k", "deadline week 4: OPTIMAL, cost $280k",
                 "deadline week 3: OPTIMAL, cost $330k", "deadline week 2: INFEASIBLE"):
        assert line in out
    assert "manual     contractor" not in out and "aerial     own crew" not in out


def test_forbidding_coast_ridge_costs_2k(capsys):
    out = printed("crew_roster", capsys)
    assert "every move allowed: OPTIMAL, travel $26k" in out
    assert "Coast-Ridge forbidden: OPTIMAL, travel $28k" in out


def test_hard_due_weeks_are_infeasible(season):
    s = build(season, **RULES)
    for j in season:
        s.model.add(s.end(j.jid) <= j.due)
    assert solve(s.model)[1] == "INFEASIBLE"


def test_the_least_risk_is_360_and_the_shortest_season_carries_1038(season):
    s = build(season, **RULES)
    minimize_lateness(s)
    solver, status = solve(s.model)
    best = starts(s, solver)
    assert status == "OPTIMAL" and solver.objective_value == 360
    assert risk(season, best) == 360 and violations(season, best) == []
    assert max(best[j.jid] + j.weeks for j in season) <= HORIZON

    fast = build(season, **RULES)
    minimize_makespan(fast)
    solver, _ = solve(fast.model)
    assert risk(season, starts(fast, solver)) == 1038


def test_the_checker_catches_hand_edits(capsys):
    out = printed("check_demo", capsys)
    assert "rules broken: none" in out
    assert "P015 is not inside one Coast outage window (weeks 9-10)" in out
    assert "P003 and P010 de-energize Valley circuits at the same time" in out


def test_named_crews_never_overlap(capsys):
    out = printed("crew_assignment", capsys)
    rows = [line for line in out.splitlines() if line.startswith("crew ")]
    assert len(rows) == CREWS
    for row in rows:
        spans = []
        for item in row.split(": ", 1)[1].split(", "):
            _, weeks = item.rsplit(" ", 1)
            first, last = map(int, weeks.split("-"))
            spans.append((first, last))
        spans.sort()
        assert all(a[1] < b[0] for a, b in zip(spans, spans[1:]))
