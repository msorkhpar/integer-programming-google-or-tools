"""The module 01 examples compute what their lessons say they print."""

import math

import pytest


def test_a_plan_is_a_zero_one_vector_and_its_objective_is_a_sum():
    from as_vector import objective, spend, to_vector
    x = to_vector({"P001", "P002", "P006"})
    assert x == [1, 1, 0, 0, 0, 1, 0, 0]
    assert objective(x) == 3504 and spend(x) == 6850


def test_cost_and_value_of_plans():
    from plan_value import cost, value
    assert cost({"P002", "P003", "P004"}) == 8200
    assert value({"P002", "P003", "P004"}) == 3567


def test_greedy_breaks_a_rule_and_brute_force_finds_the_best_allowed_plan():
    from greedy_vs_best import allowed, brute_force, greedy, value
    assert not allowed(greedy())
    best, checked = brute_force()
    assert checked == 256 and best == {"P001", "P002", "P005", "P006"} and value(best) == 3627


def test_counting_projects_trades_value_for_count():
    from wrong_objective import most_projects
    assert len(most_projects()) == 5


def test_brute_force_time_doubles_per_project():
    from growth import brute_force_years
    assert brute_force_years(41) == pytest.approx(2 * brute_force_years(40))


def test_conditional_pof_grows_with_age_while_the_unconditional_falls():
    from asset_risk import cumulative_pof, next_year_pof
    beta, eta = 3.66, 57.8
    assert next_year_pof(90, beta, eta) > next_year_pof(70, beta, eta)
    assert cumulative_pof(91, beta, eta) - cumulative_pof(90, beta, eta) < cumulative_pof(51, beta, eta) - cumulative_pof(50, beta, eta)


def test_the_risk_ranking_breaks_a_rule_and_the_optimized_plan_does_not():
    from greedy_vs_best import allowed
    from rank_vs_optimize import most_risk_avoided, riskiest_first
    assert not allowed(riskiest_first())
    assert allowed(most_risk_avoided())


def test_the_plan_survives_moderate_pof_error():
    from prediction_error import best_plan
    assert best_plan(0.5) == best_plan(2.0) == {"P001", "P002", "P005", "P006"}
    assert best_plan(0.3) != best_plan(1.0)


def test_the_lp_bounds_the_milp_and_cp_sat_agrees():
    from ortools.math_opt.python import mathopt
    from zoo_lp_milp import build
    lp = mathopt.solve(build(False)[0], mathopt.SolverType.GLOP).objective_value()
    milp = mathopt.solve(build(True)[0], mathopt.SolverType.HIGHS).objective_value()
    assert lp == pytest.approx(3770.1, abs=0.05) and milp == pytest.approx(3627)
    assert lp >= milp


def test_the_concave_split_matches_the_closed_form():
    import zoo_nlp
    share = {k: a * a for k, a in zoo_nlp.A.items()}
    total = sum(share.values())
    for k, s in zip(zoo_nlp.programs, zoo_nlp.result.x):
        assert s == pytest.approx(zoo_nlp.BUDGET * share[k] / total, rel=1e-3)


def test_a_solve_reports_its_status_and_a_budget_below_a_must_do_is_infeasible():
    from mathopt_status import solve_too_small, solve_tiny
    status, value, p006 = solve_tiny()
    assert status == "OPTIMAL" and value == pytest.approx(3627) and p006 == pytest.approx(1)
    assert solve_too_small(2000) == "INFEASIBLE"


def test_the_or_tools_mip_example_rounds_badly_and_scip_agrees_with_highs():
    from ortools.math_opt.python import mathopt
    from mip_example import allowed, build
    model, x, y = build(False)
    lp = mathopt.solve(model, mathopt.SolverType.GLOP)
    assert lp.objective_value() == pytest.approx(25) and lp.variable_values(y) == pytest.approx(2.5)
    for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP):
        model, x, y = build(True)
        milp = mathopt.solve(model, solver)
        assert milp.termination.reason == mathopt.TerminationReason.OPTIMAL
        assert milp.objective_value() == pytest.approx(23)
        assert (milp.variable_values(x), milp.variable_values(y)) == (pytest.approx(3), pytest.approx(2))
    assert allowed(0, 2) and not allowed(0, 3)
