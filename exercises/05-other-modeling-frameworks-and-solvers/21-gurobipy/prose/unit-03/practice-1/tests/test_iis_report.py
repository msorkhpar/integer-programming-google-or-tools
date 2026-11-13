from gurobipy import GRB

from iis_report import iis_report


def row(name, sense, rhs, iis):
    return {"name": name, "sense": sense, "rhs": rhs, "iis": iis}


def var(name, lb, ub, iis_lb=0, iis_ub=0):
    return {"name": name, "lb": lb, "ub": ub, "iis_lb": iis_lb, "iis_ub": iis_ub}


def test_rows_marked_by_iisconstr_are_listed():
    rows = [row("ward_b_cap", "<", 12.0, 1), row("ward_a_cap", "<", 30.0, 1)]
    assert iis_report(GRB.INFEASIBLE, rows, []) == ["ward_a_cap <= 30", "ward_b_cap <= 12"]


def test_rows_outside_the_iis_are_left_out():
    rows = [row("ward_a_cap", "<", 30.0, 1), row("budget", "<", 9000.0, 0), row("ward_c_cap", "<", 8.0, 0)]
    assert iis_report(GRB.INFEASIBLE, rows, []) == ["ward_a_cap <= 30"]


def test_each_sense_is_written_as_its_operator():
    rows = [row("night_cover", ">", 6.0, 1), row("one_shift_ann", "=", 1.0, 1), row("hours", "<", 40.0, 1)]
    assert iis_report(GRB.INFEASIBLE, rows, []) == ["hours <= 40", "night_cover >= 6", "one_shift_ann == 1"]


def test_variable_bounds_in_the_iis_are_listed():
    rows = [row("hours", "<", 40.0, 1)]
    bounds = [var("overtime", 0.0, 8.0, iis_ub=1), var("agency", 2.0, 10.0, iis_lb=1), var("float", 0.0, 5.0)]
    assert iis_report(GRB.INFEASIBLE, rows, bounds) == ["agency >= 2", "hours <= 40", "overtime <= 8"]


def test_a_model_that_is_not_infeasible_has_no_report():
    rows = [row("hours", "<", 40.0, 1)]
    assert iis_report(GRB.OPTIMAL, rows, []) == []
    assert iis_report(GRB.INF_OR_UNBD, rows, []) == []
    assert iis_report(GRB.INFEASIBLE, rows, []) == ["hours <= 40"]
