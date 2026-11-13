"""Planner overrides, and why a plan failed (lesson 14.1.6)."""

from vegcrew.data import Override
from vegcrew.planner import Trim, check_overrides, make_plan
from test_planner import season


def test_a_pin_puts_the_trim_on_its_crew_and_week():
    s = season(1000, ("A", 10, 50, 3), crews=2, months=2)
    plan = make_plan(s, (Override("pin", "A", crew="K2", start=2, reason="landowner asked"),))
    assert plan.trims["A"] == Trim("A", "K2", 2, 5)


def test_a_skip_leaves_the_circuit_for_next_season():
    s = season(1000, ("A", 10, 520, 4), ("B", 10, 104, 4), crews=1, months=1)
    plan = make_plan(s, (Override("skip", "A", reason="road closed"),))
    assert sorted(plan.trims) == ["B"]


def test_force_trims_a_circuit_the_model_would_leave():
    s = season(1000, ("A", 10, 520, 4), ("B", 10, 104, 4), crews=1, months=1)
    plan = make_plan(s, (Override("force", "B", reason="customer complaints"),))
    assert sorted(plan.trims) == ["B"]


def test_two_pins_that_overlap_on_one_crew_are_named_together():
    s = season(1000, ("A", 10, 50, 3), ("B", 10, 40, 3), ("C", 10, 30, 1), crews=1, months=2)
    plan = make_plan(s, (Override("force", "C", reason="storm damage"),
                         Override("pin", "A", crew="K1", start=0, reason="crew is nearby"),
                         Override("pin", "B", crew="K1", start=2, reason="landowner asked")))
    assert plan.status == "INFEASIBLE"
    assert plan.explanation == ("override 2: trim A on K1 from week 0 (crew is nearby)",
                                "override 3: trim B on K1 from week 2 (landowner asked)")


def test_a_must_beyond_the_budget_names_the_must_and_the_budget():
    s = season(50, ("A", 60, 50, 1), ("B", 10, 40, 1), crews=1, months=1, must={"A": True, "B": True})
    plan = make_plan(s)
    assert plan.status == "INFEASIBLE"
    assert sorted(plan.explanation) == ["A is overdue and must be trimmed this season",
                                        "the season's budget is $50k"]


def test_overrides_that_name_nothing_are_refused_before_the_solve():
    s = season(1000, ("A", 10, 50, 3), crews=1, months=1)
    assert check_overrides(s, (Override("pin", "Z9", crew="K7", start=40), Override("trim", "A"))) == [
        "override 1: no circuit Z9", "override 1: no crew K7", "override 1: week 40 is outside the season",
        "override 2: unknown kind 'trim'"]
