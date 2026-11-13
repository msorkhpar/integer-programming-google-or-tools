"""The mock interviews' trap programs: each verdict and number the pages quote."""

import pytest
from ortools.sat.python import cp_model

import diagnostic_traps
import formulation_traps
import production_traps
import solver_traps
import value_traps
from mock_support import allowed, quiet_solve


@pytest.mark.parametrize("form, plan, expected", [
    ("time sum and big-M", {("B", 2028): 1}, True),
    ("cumulative rows", {("B", 2028): 1}, False),
    ("time sum and big-M", {("A", 2027): 1, ("B", 2030): 1}, True),
    ("cumulative rows", {("A", 2027): 1, ("B", 2030): 1}, True),
    ("time sum and big-M", {("A", 2027): 1, ("B", 2029): 1}, False),
    ("cumulative rows", {("A", 2027): 1, ("B", 2029): 1}, False),
])
def test_only_the_time_sum_row_lets_the_child_start_without_its_parent(form, plan, expected):
    model, x = formulation_traps.precedence_model(form)
    assert allowed(model, x, plan) is expected


@pytest.mark.parametrize("rows, best", [("no order rows", 100), ("same-year order", 50), ("started-by order", 100)])
def test_a_same_year_order_row_removes_every_copy_of_the_best_plan(rows, best):
    model, _ = formulation_traps.symmetry_model(rows)
    assert quiet_solve(model).objective_value() == pytest.approx(best)


def test_cp_sat_names_a_sufficient_set_and_the_filter_keeps_the_clash():
    assert not hasattr(cp_model.CpSolver, "SolveWithAssumptions")
    status, named = solver_traps.solve(["must_J1", "must_J2", "crew_cap", "must_J4", "pair_J3_J4"])
    assert status == cp_model.INFEASIBLE
    assert {"must_J1", "must_J2", "crew_cap"} <= set(named)
    assert solver_traps.deletion_filter(named) == sorted({"must_J1", "must_J2", "crew_cap"} & set(named), key=named.index)


def test_the_three_readings_of_a_weibull_curve():
    views = list(value_traps.pof_views(40, 3.5, 45).values())
    assert [round(v, 3) for v in views] == [0.484, 0.030, 0.058]
    r40, r41 = value_traps.reliability(40, 3.5, 45), value_traps.reliability(41, 3.5, 45)
    assert views[2] == pytest.approx(1 - r41 / r40)


def test_escalation_from_the_start_year_makes_a_late_start_look_cheaper():
    base = value_traps.escalated_pv(1000, 2026, 2030, 0.04, 0.07, "base year", 2026)
    start = value_traps.escalated_pv(1000, 2026, 2030, 0.04, 0.07, "start year", 2026)
    assert round(base, 1) == 892.5 and round(start, 1) == 762.9
    assert value_traps.escalated_pv(1000, 2026, 2030, 0.07, 0.07, "base year", 2026) == pytest.approx(1000)


def test_cutting_benefits_at_the_plan_end_turns_a_good_project_into_a_loss():
    full = value_traps.project_npv(2027, 900, 120, 25, 0.07, 2027, None)
    cut = value_traps.project_npv(2027, 900, 120, 25, 0.07, 2027, 2031)
    assert round(full, 1) == 498.4 and round(cut, 1) == -493.5


def test_the_degenerate_lp_binds_every_row_and_prices_only_two(capsys):
    diagnostic_traps.degenerate_lp()
    out = capsys.readouterr().out
    assert out.count("slack 0") == 3
    assert "total  slack 0  price 0" in out


def test_the_milp_has_no_duals_and_the_fixed_lp_prices_no_budget(capsys):
    plan = diagnostic_traps.milp_has_no_duals()
    assert plan == {"P1": 1, "P2": 1, "P3": 0}
    diagnostic_traps.fixed_integer_resolve(plan)
    out = capsys.readouterr().out
    assert "has_dual_feasible_solution(): False" in out
    assert "budget price 0;" in out


def test_hash_ranks_change_between_processes_and_digest_ranks_do_not():
    salted_1, stable_1 = production_traps.weights_in_a_fresh_process("1")
    salted_2, stable_2 = production_traps.weights_in_a_fresh_process("2")
    assert salted_1 != salted_2
    assert stable_1 == stable_2
    assert all(0 <= int(v) < 100 for v in stable_1.split())
