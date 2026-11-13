"""The module 14 examples: indicators, prioritized objectives, hints, scenarios, callbacks and the IIS."""

import pytest
from ortools.math_opt.python import mathopt

from find_iis import deletion_filter
from gridcap import generate
from in_order import add_auxiliary, allowed_loss, solve_in_order
from plan_model import build, plan, refusal, solve

SCIP, HIGHS = mathopt.SolverType.GSCIP, mathopt.SolverType.HIGHS


@pytest.fixture(scope="module")
def small():
    return generate("small")


def spend_in(portfolio, chosen, year):
    return sum(portfolio.project(pid).spend(t).get(year, 0) for pid, t in chosen.items())


def add_reserve(pm, portfolio, form):
    for p in portfolio.projects:
        if p.capex >= 5000:
            for t in p.starts():
                if form == "indicator":
                    pm.model.add_indicator_constraint(indicator=pm.x[p.project_id, t],
                                                      implied_constraint=pm.spend[t] <= 0.9 * portfolio.budget[t])
                else:
                    pm.model.add_linear_constraint(
                        pm.spend[t] <= portfolio.budget[t] - 0.1 * portfolio.budget[t] * pm.x[p.project_id, t])


def test_the_reserve_holds_in_every_year_a_large_project_starts(small):
    pm = build(small)
    add_reserve(pm, small, "indicator")
    result = solve(pm.model, SCIP)
    chosen = plan(pm, result.variable_values())
    assert result.objective_value() == pytest.approx(23039)
    for pid, t in chosen.items():
        if small.project(pid).capex >= 5000:
            assert spend_in(small, chosen, t) <= 0.9 * small.budget[t] + 1e-6


def test_the_linear_reserve_on_highs_matches_the_indicator_on_scip(small):
    pm = build(small)
    add_reserve(pm, small, "linear")
    assert solve(pm.model, HIGHS).objective_value() == pytest.approx(23039)


def test_highs_refuses_indicators_and_the_reason_is_on_the_context(small):
    pm = build(small)
    add_reserve(pm, small, "indicator")
    with pytest.raises(Exception) as caught:
        solve(pm.model, HIGHS)
    assert "does not support indicator constraints" in refusal(caught.value)


def test_solving_in_order_breaks_the_samples_tie_both_ways():
    model = mathopt.Model()
    x, y = model.add_variable(lb=0, ub=1, name="x"), model.add_variable(lb=0, ub=1, name="y")
    z = model.add_binary_variable(name="z")
    model.add_linear_constraint(x + y + z <= 1.5)
    model.maximize(x + y + 2 * z)
    aux = model.add_maximization_objective(y, priority=1, name="more_y")
    reached, values = solve_in_order(model, HIGHS)
    assert reached["primary"] == pytest.approx(2.5) and values["y"] == pytest.approx(0.5)
    model.delete_auxiliary_objective(aux)
    model.add_minimization_objective(y, priority=1, name="less_y")
    reached, values = solve_in_order(model, HIGHS)
    assert reached["primary"] == pytest.approx(2.5) and values["y"] == pytest.approx(0.0)


def test_the_allowed_loss_is_the_larger_tolerance():
    params = mathopt.ObjectiveParameters(objective_degradation_absolute_tolerance=100,
                                         objective_degradation_relative_tolerance=0.01)
    assert allowed_loss(24260, params) == pytest.approx(242.6)
    assert allowed_loss(-5000, params) == pytest.approx(100)
    assert allowed_loss(24260, None) == 0


def test_a_one_percent_tolerance_keeps_npv_within_one_percent(small):
    pm = build(small)
    pm.model.add_minimization_objective(mathopt.fast_sum(pm.spend.values()), priority=1, name="spend")
    params = mathopt.ModelSolveParameters()
    params.objective_parameters[pm.model.objective] = mathopt.ObjectiveParameters(
        objective_degradation_relative_tolerance=0.01)
    reached, values = solve_in_order(pm.model, HIGHS, params)
    npv = sum(small.project(pid).npv[t] for (pid, t), v in pm.x.items() if values[v.name] > 0.5)
    assert 0.99 * 24260 - 1e-6 <= npv <= 24260
    assert reached["spend"] == pytest.approx(40440)


def test_a_hint_never_changes_the_optimum(small):
    pm = build(small)
    best = solve(pm.model, HIGHS)
    pm.budget[2031].upper_bound += 200
    hint = mathopt.SolutionHint(variable_values={v: round(best.variable_values(v)) for v in pm.x.values()})
    params = mathopt.ModelSolveParameters(solution_hints=[hint])
    for solver in (HIGHS, SCIP, mathopt.SolverType.CP_SAT):
        assert solve(pm.model, solver, model_params=params).objective_value() == pytest.approx(24298)


def test_budget_cuts_are_answered_on_one_model_and_put_back(small):
    pm = build(small)
    with mathopt.IncrementalSolver(pm.model, SCIP) as solver:
        found = {}
        for share in (0.05, 0.10, 0.20):
            pm.budget[2029].upper_bound = (1 - share) * small.budget[2029]
            found[share] = solver.solve().objective_value()
            pm.budget[2029].upper_bound = small.budget[2029]
        assert found == pytest.approx({0.05: 24070, 0.10: 24053, 0.20: 23645})
        assert solver.solve().objective_value() == pytest.approx(24260)


def test_lazy_crew_rows_on_scip_match_the_rows_written_up_front(small):
    transmission = [p.project_id for p in small.projects if p.program == "transmission"]

    def row(pm, y):
        return mathopt.fast_sum(pm.x[pid, y] for pid in transmission if (pid, y) in pm.x) <= 2

    pm = build(small)
    for y in small.years:
        pm.model.add_linear_constraint(row(pm, y))
    upfront = solve(pm.model, HIGHS).objective_value()
    pm = build(small)

    def check(data):
        result = mathopt.CallbackResult()
        chosen = plan(pm, data.solution)
        for y in small.years:
            if sum(1 for pid, t in chosen.items() if t == y and pid in transmission) > 2:
                result.add_lazy_constraint(row(pm, y))
        return result

    reg = mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION}, add_lazy_constraints=True)
    lazy = solve(pm.model, SCIP, callback_reg=reg, cb=check)
    assert lazy.objective_value() == pytest.approx(upfront) == pytest.approx(24050)


def test_the_deletion_filter_finds_p017_against_both_caps(small):
    pm = build(small)
    pm.x["P032", 2027].lower_bound = 1
    pm.budget[2030].upper_bound = pm.budget[2031].upper_bound = 5000
    iis = deletion_filter(pm.model, variables=[pm.x["P032", 2027]])
    assert iis.feasibility == mathopt.FeasibilityStatus.INFEASIBLE
    rows = {row.name: (b.lower, b.upper) for row, b in iis.infeasible_subsystem.linear_constraints.items()}
    assert rows == {"budget_2030": (False, True), "budget_2031": (False, True), "must_P017": (True, False)}
    assert not iis.infeasible_subsystem.variable_bounds


def test_the_deletion_filter_reports_a_feasible_model_as_feasible(small):
    assert deletion_filter(build(small).model).feasibility == mathopt.FeasibilityStatus.FEASIBLE


def test_add_auxiliary_keeps_every_objective_s_terms():
    model = mathopt.Model()
    a, b = model.add_variable(name="a"), model.add_variable(name="b")
    first = add_auxiliary(model, 1.5 * a + 2, priority=1, is_maximize=False, name="first")
    second = add_auxiliary(model, 2 * b, priority=2, is_maximize=True, name="second")
    assert first.get_linear_coefficient(a) == 1.5 and first.offset == 2
    assert second.get_linear_coefficient(b) == 2 and second.is_maximize


def test_scip_refuses_a_two_sided_indicator_row():
    model = mathopt.Model()
    on, work = model.add_binary_variable(name="on"), model.add_variable(lb=0, ub=10, name="work")
    model.add_indicator_constraint(indicator=on, activate_on_zero=True, implied_constraint=work == 0)
    model.maximize(work - on)
    with pytest.raises(Exception) as caught:
        solve(model, SCIP)
    assert "ranged implied constraints" in refusal(caught.value)
