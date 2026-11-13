"""The module 35 examples: the lexicographic passes, their tolerances, and three implementations that agree."""

import importlib.util

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from in_order import add_auxiliary, solve_in_order
from lex_model import build, score
from lexicographic import Level, allowed_loss, solve_levels

HAS_GUROBI = importlib.util.find_spec("gurobipy") is not None


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.fixture(scope="module")
def sm(small):
    return build(small)


def test_lesson_7_3_4_numbers_come_back(sm):
    npv_plan = solve_levels(sm, [Level("npv")]).plan
    risk_plan = solve_levels(sm, [Level("risk")]).plan
    assert score(sm, npv_plan, "npv") == 24260
    assert round(score(sm, npv_plan, "risk")) == 10577
    assert round(score(sm, risk_plan, "risk")) == 16086


def test_the_one_percent_plan_stays_above_its_floor_and_removes_more_risk(sm):
    out = solve_levels(sm, [Level("npv", rel_tol=0.01), Level("risk")])
    npv, risk = score(sm, out.plan, "npv"), score(sm, out.plan, "risk")
    assert out.floor["npv"] == pytest.approx(24260 * 0.99)
    assert out.floor["npv"] - 1e-6 <= npv < 24260
    assert risk == pytest.approx(12750.5, abs=0.05)


def test_the_kept_rows_are_deleted_after_the_solve(sm):
    before = len(list(sm.model.linear_constraints()))
    solve_levels(sm, [Level("npv", rel_tol=0.05), Level("risk")])
    assert len(list(sm.model.linear_constraints())) == before
    assert score(sm, solve_levels(sm, [Level("npv")]).plan, "npv") == 24260


def test_the_loss_taken_never_exceeds_the_loss_allowed(sm):
    for first in (Level("npv", rel_tol=0.005), Level("npv", abs_tol=100), Level("npv", rel_tol=0.02)):
        out = solve_levels(sm, [first, Level("risk")])
        assert out.best["npv"] - score(sm, out.plan, "npv") <= allowed_loss(out.best["npv"], first) + 1e-6


def test_an_absolute_tolerance_equal_to_one_percent_gives_the_same_plan(sm):
    relative = solve_levels(sm, [Level("npv", rel_tol=0.01), Level("risk")]).plan
    absolute = solve_levels(sm, [Level("npv", abs_tol=242.6), Level("risk")]).plan
    assert relative == absolute


def test_mathopt_in_order_matches_the_manual_passes(small):
    sm = build(small)
    sm.model.maximize(sm.objective("npv"))
    add_auxiliary(sm.model, sm.objective("risk"), priority=1, is_maximize=True, name="risk")
    params = mathopt.ModelSolveParameters(objective_parameters={
        sm.model.objective: mathopt.ObjectiveParameters(objective_degradation_relative_tolerance=0.01)})
    reached, _ = solve_in_order(sm.model, params)
    assert reached["risk"] == pytest.approx(12750.5, abs=0.05)
    assert sm.model.num_auxiliary_objectives() == 1          # the model itself is left as it was


@pytest.mark.skipif(not HAS_GUROBI, reason="gurobipy is not installed")
def test_gurobi_set_objective_n_matches_the_manual_passes(small, sm):
    from gurobipy import GRB, GurobiError
    from gurobi_model import build as build_grb, chosen, quiet_env
    try:
        env = quiet_env()
    except GurobiError:
        pytest.skip("no Gurobi license mounted")
    gm = build_grb(env, small)
    gm.model.ModelSense = GRB.MAXIMIZE
    gm.model.setObjectiveN(gm.objective["npv"], index=0, priority=2, reltol=0.01, name="npv")
    gm.model.setObjectiveN(gm.objective["risk"], index=1, priority=1, name="risk")
    gm.model.Params.MIPGap = 0.0
    gm.model.optimize()
    assert chosen(gm) == solve_levels(sm, [Level("npv", rel_tol=0.01), Level("risk")]).plan
