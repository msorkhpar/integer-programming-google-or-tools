"""Weather and access windows, crews' weeks off, and must-trim circuits (lesson 14.1.5)."""

from vegcrew.planner import make_plan
from test_planner import season


def test_a_trim_stays_inside_its_access_window():
    plan = make_plan(season(1000, ("A", 10, 50, 3), crews=1, months=2, windows={"A": [[4, 7]]}))
    assert (plan.trims["A"].start, plan.trims["A"].end) == (4, 7)


def test_a_trim_fits_inside_one_window_never_across_two():
    # Weeks 0-1 and 5-7 are open; a 3-week trim cannot use weeks 0-1, nor run through the closed 2-4.
    plan = make_plan(season(1000, ("A", 10, 50, 3), crews=1, months=2, windows={"A": [[0, 1], [5, 7]]}))
    assert plan.trims["A"].start == 5


def test_a_window_shorter_than_the_trim_leaves_it_for_next_season():
    plan = make_plan(season(1000, ("A", 10, 50, 3), crews=1, months=2, windows={"A": [[0, 1]]}))
    assert (plan.status, plan.trims) == ("OPTIMAL", {})


def test_no_crew_works_in_its_weeks_off():
    plan = make_plan(season(1000, ("A", 10, 50, 3), crews=1, months=2, crew_off={"K1": [[0, 3]]}))
    assert (plan.trims["A"].crew, plan.trims["A"].start) == ("K1", 4)


def test_the_crew_with_no_time_off_takes_the_early_trim():
    plan = make_plan(season(1000, ("A", 10, 50, 3), crews=2, months=2, crew_off={"K1": [[0, 3]]}))
    assert (plan.trims["A"].crew, plan.trims["A"].start) == ("K2", 0)


def test_a_must_circuit_is_trimmed_even_when_it_removes_less_risk():
    plan = make_plan(season(1000, ("A", 10, 520, 4), ("B", 10, 104, 4), crews=1, months=1,
                            must={"B": True}))
    assert sorted(plan.trims) == ["B"]


def test_must_circuits_that_cannot_all_fit_make_the_season_infeasible():
    plan = make_plan(season(1000, ("A", 10, 50, 3), ("B", 10, 40, 3), crews=1, months=1,
                            must={"A": True, "B": True}))
    assert (plan.status, plan.trims) == ("INFEASIBLE", {})
