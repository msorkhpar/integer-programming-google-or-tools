"""Module 21: every gurobipy port gives the optimum its MathOpt original gives, and the lessons' numbers hold.

Needs a Gurobi license (the course runner mounts one when the machine has it); without one the whole
module is skipped, with the reason.
"""

import os

import pytest
from ortools.math_opt.python import mathopt

gp = pytest.importorskip("gurobipy")
from gurobipy import GRB  # noqa: E402

from gridcap import generate  # noqa: E402
from grb import build_plan, build_selection, chosen, mask  # noqa: E402
from licensed_env import env_params, redacted  # noqa: E402


@pytest.fixture(scope="module")
def env():
    try:
        e = gp.Env(params={"OutputFlag": 0})
    except gp.GurobiError as error:
        pytest.skip(f"no Gurobi license: error {error.errno}")
    yield e
    e.dispose()


@pytest.fixture(scope="module")
def small():
    return generate("small")


def exact(model):
    model.Params.MIPGap = 0.0
    model.optimize()
    assert model.Status == GRB.OPTIMAL
    return model.ObjVal


# --- 5.3.1: the selection and timing models -------------------------------------------------------

def test_selection_milp_matches_mathopt_highs(env, small):
    import selection as mo_selection
    sel = mo_selection.build(small)
    expected = mo_selection.solve(sel.model, mathopt.SolverType.HIGHS,
                                  mathopt.SolveParameters(relative_gap_tolerance=0.0)).objective_value()
    g = build_selection(env, small)
    assert exact(g.model) == pytest.approx(expected) == pytest.approx(22532)
    assert sorted(i for i, v in g.x.items() if v.X > 0.5) == mo_selection.plan(
        sel, mo_selection.solve(sel.model, mathopt.SolverType.HIGHS,
                                mathopt.SolveParameters(relative_gap_tolerance=0.0)))


def test_matrix_form_has_the_same_optimum(env, small):
    g = build_selection(env, small)
    A = (g.model.update(), g.model.getA())[1]
    assert A.shape == (13, 40) and A.nnz == 69
    import numpy as np
    m = gp.Model(env=env)
    xv = m.addMVar(A.shape[1], lb=0, ub=1, vtype=GRB.BINARY)
    rows = g.model.getConstrs()
    senses = np.array([c.Sense for c in rows])
    rhs = np.array([c.RHS for c in rows])
    for sense in "<=":
        pick = np.where(senses == sense)[0]
        m.addMConstr(A[pick, :], xv, sense, rhs[pick])
    m.setObjective(np.array(g.model.getAttr("Obj", g.model.getVars())) @ xv, GRB.MAXIMIZE)
    assert exact(m) == pytest.approx(22532)


def test_timing_model_matches_mathopt(env, small):
    import plan_model
    pm = plan_model.build(small)
    expected = plan_model.solve(pm.model).objective_value()
    pl = build_plan(env, small)
    assert exact(pl.model) == pytest.approx(expected) == pytest.approx(24260)
    pl.model.update()
    assert pl.model.NumVars == pm.model.get_num_variables() == 80
    assert pl.model.NumConstrs == pm.model.get_num_linear_constraints() == 49
    assert len(chosen(pl)) == 27


def test_attribute_edits_take_effect_on_the_next_solve(env, small):
    g = build_selection(env, small)
    exact(g.model)
    g.x["P001"].UB = 0
    g.budget[2030].RHS += 1000
    assert exact(g.model) == pytest.approx(22613)
    assert g.x["P001"].X == 0


# --- 5.3.2: duals and ranging ---------------------------------------------------------------------

def test_lp_duals_match_glop(env, small):
    import selection as mo_selection
    sel = mo_selection.build(small, integer=False)
    relaxed = mo_selection.solve(sel.model, mathopt.SolverType.GLOP)
    g = build_selection(env, small, integer=False)
    g.model.optimize()
    assert g.model.ObjVal == pytest.approx(relaxed.objective_value()) == pytest.approx(23669.4936, abs=1e-3)
    for y, row in sel.budget.items():
        assert g.budget[y].Pi == pytest.approx(relaxed.dual_values(row), abs=1e-6)


def test_a_price_holds_inside_its_range_and_not_beyond(env, small):
    g = build_selection(env, small, integer=False)
    g.model.optimize()
    base, row = g.model.ObjVal, g.budget[2030]
    pi, rhs, up = row.Pi, row.RHS, row.SARHSUp
    assert up == pytest.approx(9300)
    row.RHS = up
    g.model.optimize()
    assert g.model.ObjVal - base == pytest.approx(pi * (up - rhs))
    row.RHS = up + 300
    g.model.optimize()
    assert g.model.ObjVal - base < pi * (up + 300 - rhs) - 1


def test_a_mip_has_no_pi_and_fixed_gives_an_lp(env, small):
    g = build_selection(env, small)
    exact(g.model)
    with pytest.raises((AttributeError, gp.GurobiError)):
        g.budget[2027].Pi
    f = g.model.fixed()
    f.optimize()
    assert f.IsMIP == 0 and f.ObjVal == pytest.approx(22532)


# --- 5.3.3: IIS, feasRelax, setObjectiveN, PWL ---------------------------------------------------

def scenario(env, small):
    pl = build_plan(env, small)
    pl.x["P032", 2027].LB = 1
    pl.budget[2030].RHS = 5000
    pl.budget[2031].RHS = 5000
    pl.model.update()
    return pl


def test_compute_iis_finds_the_rows_the_deletion_filter_finds(env, small):
    import plan_model
    from find_iis import deletion_filter
    pm = plan_model.build(small)
    promised = pm.x["P032", 2027]
    promised.lower_bound = 1.0
    pm.budget[2030].upper_bound = 5000
    pm.budget[2031].upper_bound = 5000
    by_hand = deletion_filter(pm.model, variables=[promised])
    pl = scenario(env, small)
    pl.model.optimize()
    assert pl.model.Status == GRB.INFEASIBLE
    pl.model.computeIIS()
    assert pl.model.IISMinimal == 1
    gurobi_rows = {c.ConstrName for c in pl.model.getConstrs() if c.IISConstr}
    assert gurobi_rows == {r.name for r in by_hand.infeasible_subsystem.linear_constraints} == {
        "must_P017", "budget_2030", "budget_2031"}
    assert not any(v.IISLB or v.IISUB for v in pl.model.getVars())


def test_feasrelax_on_budget_rows_needs_p017s_overrun(env, small):
    pl = scenario(env, small)
    relaxed = pl.model.copy()
    rows = [relaxed.getConstrByName(f"budget_{y}") for y in small.years]
    relaxed.feasRelax(0, False, None, None, None, rows, [1.0] * len(rows))
    relaxed.optimize()
    assert relaxed.ObjVal == pytest.approx(small.project("P017").cost_profile[0] - 5000) == pytest.approx(310)
    assert pl.model.NumVars == 80                      # the original is untouched: feasRelax ran on the copy


def test_feasrelaxs_with_unit_penalties_drops_the_must_do(env, small):
    relaxed = scenario(env, small).model.copy()
    relaxed.feasRelaxS(0, False, False, True)
    relaxed.optimize()
    assert relaxed.ObjVal == pytest.approx(1)
    assert relaxed.getVarByName("ArtP_must_P017").X == pytest.approx(1)


def test_set_objective_n_matches_solving_in_order(env, small):
    import plan_model
    from in_order import solve_in_order
    pm = plan_model.build(small)
    pm.model.add_minimization_objective(mathopt.fast_sum(pm.spend.values()), priority=1, name="spend")
    params = mathopt.ModelSolveParameters()
    params.objective_parameters[pm.model.objective] = mathopt.ObjectiveParameters(
        objective_degradation_relative_tolerance=0.01)
    reached, _ = solve_in_order(pm.model, mathopt.SolverType.HIGHS, params)
    pl = build_plan(env, small)
    m = pl.model
    m.ModelSense = GRB.MAXIMIZE
    m.setObjectiveN(pl.npv, index=0, priority=2, reltol=0.01)
    m.setObjectiveN(gp.quicksum(pl.spend.values()), index=1, priority=1, weight=-1.0)
    exact(m)
    m.Params.ObjNumber = 1
    assert m.ObjNVal == pytest.approx(reached["spend"]) == pytest.approx(40440)


def test_pwl_credit_line_matches_the_lambda_form(env, small):
    xs, ys = [0, 1500, 3000, 5000], [0, 675, 1050, 1250]
    model = mathopt.Model()
    x = {p.project_id: model.add_binary_variable() for p in small.projects}
    lam = [model.add_variable(lb=0, ub=1) for _ in xs]
    z = [model.add_binary_variable() for _ in range(len(xs) - 1)]
    model.add_linear_constraint(sum(lam) == 1)
    model.add_linear_constraint(sum(z) == 1)
    for j in range(len(xs)):
        model.add_linear_constraint(lam[j] <= sum(z[k] for k in (j - 1, j) if 0 <= k < len(z)))
    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in small.projects)
                                <= small.capital_budget + sum(X * l for X, l in zip(xs, lam)))
    groups = {}
    for p in small.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1)
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent])
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for members in groups.values():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1)
    model.maximize(sum(p.value * x[p.project_id] for p in small.projects) - sum(F * l for F, l in zip(ys, lam)))
    expected = mathopt.solve(model, mathopt.SolverType.GSCIP).objective_value()
    import runpy
    import io
    import contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        runpy.run_path(os.path.join(os.path.dirname(__file__), "..", "src", "pwl.py"), run_name="__main__")
    assert expected == pytest.approx(26753)
    assert "objective $26,753k, drawn $4,900k" in out.getvalue()


# --- 5.3.4: licenses and masks --------------------------------------------------------------------

def test_mask_hides_user_host_and_ids():
    raw = "No Gurobi license found (user jdoe, host box-7, hostid 9a8b7c, cores 4) for jane@example.com, LicenseID 123456"
    masked = mask(raw)
    for secret in ("jdoe", "box-7", "9a8b7c", "cores 4", "jane@example.com", "123456"):
        assert secret not in masked


def test_env_params_take_a_whole_wls_key_or_none():
    key = {"WLSACCESSID": "a", "WLSSECRET": "b", "LICENSEID": "42"}
    assert env_params(key) == {"OutputFlag": 0, "WLSACCESSID": "a", "WLSSECRET": "b", "LICENSEID": 42}
    assert env_params({}) == {"OutputFlag": 0}
    with pytest.raises(ValueError):
        env_params({"WLSACCESSID": "a"})
    assert "b" not in str(redacted(env_params(key)).values())


def test_course_models_fit_the_size_limited_license(env):
    for size in ("small", "medium"):
        pl = build_plan(env, generate(size))
        pl.model.update()
        assert pl.model.NumVars <= 2000 and pl.model.NumConstrs <= 2000
