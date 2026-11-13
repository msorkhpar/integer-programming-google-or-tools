from ortools.sat.python import cp_model

from crew_hours import add_hours_rules, crew_variables


def allowed(worked: int, approved: bool) -> bool:
    model = cp_model.CpModel()
    hours, overtime = crew_variables(model)
    add_hours_rules(model, hours, overtime)
    model.add(hours == worked)
    model.add(overtime == int(approved))
    status = cp_model.CpSolver().solve(model)
    return status in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def test_without_overtime_a_week_stays_within_forty_hours():
    assert allowed(38, approved=False) is True
    assert allowed(44, approved=False) is False


def test_overtime_lifts_the_forty_hour_cap():
    assert allowed(50, approved=True) is True
    assert allowed(50, approved=False) is False


def test_overtime_still_caps_the_week_at_fifty_five():
    assert allowed(55, approved=True) is True
    assert allowed(56, approved=True) is False


def test_approved_overtime_means_at_least_forty_five_hours():
    assert allowed(45, approved=True) is True
    assert allowed(42, approved=True) is False
