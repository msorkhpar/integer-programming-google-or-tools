"""The module 07 examples compute what their lessons say they print."""

import pytest
from ortools.math_opt.python import mathopt

from funding_lp import build, in_between, spend_in
from gridcap import generate
from solver_log import mask_times, solve_with_log


@pytest.fixture(scope="module")
def medium():
    return generate("medium")


def test_the_funding_lp_has_one_cash_row_per_year_and_one_must_row_per_must_do(medium):
    lp = build(medium)
    assert len(lp.cash) == len(medium.years) == 10
    assert len(lp.must) == sum(p.must_do for p in medium.projects) == 39
    assert len(list(lp.model.variables())) == 410 and len(list(lp.model.linear_constraints())) == 49


def test_every_lp_method_reaches_the_same_optimum_and_pdlp_only_within_tolerance(medium):
    lp = build(medium)
    values = {}
    for solver, algorithm in ((mathopt.SolverType.GLOP, mathopt.LPAlgorithm.PRIMAL_SIMPLEX),
                              (mathopt.SolverType.HIGHS, mathopt.LPAlgorithm.BARRIER),
                              (mathopt.SolverType.PDLP, mathopt.LPAlgorithm.FIRST_ORDER)):
        result = mathopt.solve(lp.model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))
        assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
        values[solver.name] = result.objective_value()
    assert values["GLOP"] == pytest.approx(234898.1206, abs=1e-3)
    assert values["HIGHS"] == pytest.approx(values["GLOP"], rel=1e-9)
    assert values["PDLP"] == pytest.approx(values["GLOP"], rel=1e-6)


def test_a_simplex_vertex_has_at_most_one_in_between_variable_per_cash_row(medium):
    lp = build(medium)
    result = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    assert in_between(lp, result) <= len(lp.cash)


def test_glop_refuses_barrier():
    lp = build(generate("small"))
    with pytest.raises(Exception):
        mathopt.solve(lp.model, mathopt.SolverType.GLOP,
                      params=mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.BARRIER))


def test_masking_removes_times_and_keeps_the_rest():
    assert mask_times("10 rows, 368 cols, 601 nonzeros  0s") == "10 rows, 368 cols, 601 nonzeros  <t>s"
    assert mask_times("HiGHS run time      :          0.12") == "HiGHS run time      :          <t>"
    assert mask_times("Simplex   iterations: 14") == "Simplex   iterations: 14"


def test_the_highs_log_footer_agrees_with_the_result(medium):
    lp = build(medium)
    result, log = solve_with_log(lp.model, mathopt.SolverType.HIGHS)
    assert "Model status        : Optimal" in log
    assert f"Simplex   iterations: {result.solve_stats.simplex_iterations}" in log
    assert any(line.startswith("Presolve reductions: rows 10(-39); columns 368(-42)") for line in log)


def test_cutting_the_first_year_below_must_do_spend_is_infeasible(medium):
    assert sum(spend_in(p, 2027) for p in medium.projects if p.must_do) == 3040
    lp = build(medium)
    lp.cash[2027].upper_bound = 1000
    result = mathopt.solve(lp.model, mathopt.SolverType.HIGHS)
    assert result.termination.reason == mathopt.TerminationReason.INFEASIBLE


def test_a_warm_glop_resolve_takes_far_fewer_iterations_and_gives_the_cold_answer(medium):
    lp = build(medium)
    solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)
    base = solver.solve()
    lp.cash[2030].upper_bound *= 0.9
    warm = solver.solve()
    cold = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    solver.close()
    assert warm.objective_value() == pytest.approx(cold.objective_value(), rel=1e-9)
    assert warm.solve_stats.simplex_iterations * 10 < cold.solve_stats.simplex_iterations
    assert base.objective_value() > warm.objective_value()


def test_a_warm_glop_resolve_with_dual_simplex_needs_fewer_pivots_than_the_default(medium):
    pivots = {}
    for label, params in (("primal", mathopt.SolveParameters()),
                          ("dual", mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.DUAL_SIMPLEX))):
        lp = build(medium)
        solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)
        solver.solve(params=params)
        lp.cash[2030].upper_bound *= 0.9
        log: list[str] = []
        cut = solver.solve(params=params, msg_cb=log.extend)
        solver.close()
        assert cut.objective_value() == pytest.approx(233003.9574, abs=1e-3)
        assert any(line.startswith(label.capitalize() + " optimization phase") for line in log)
        pivots[label] = cut.solve_stats.simplex_iterations
    assert pivots["dual"] < pivots["primal"]


def test_the_dual_value_predicts_a_small_cut_exactly_and_overstates_a_large_one(medium):
    lp = build(medium)
    base = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    price = base.dual_values(lp.cash[2030])
    budget = lp.cash[2030].upper_bound
    for cut, exact in ((100, True), (11529, False)):
        lp.cash[2030].upper_bound = budget - cut
        actual = mathopt.solve(lp.model, mathopt.SolverType.GLOP).objective_value()
        predicted = base.objective_value() - price * cut
        assert (predicted == pytest.approx(actual, abs=1e-6)) is exact
        assert predicted >= actual - 1e-6


def test_each_solver_default_is_the_simplex_form_its_documentation_names(medium):
    lp = build(medium)
    pivots = {}
    for solver, algorithm in ((mathopt.SolverType.GLOP, mathopt.LPAlgorithm.PRIMAL_SIMPLEX),
                              (mathopt.SolverType.HIGHS, mathopt.LPAlgorithm.DUAL_SIMPLEX)):
        chosen = mathopt.solve(lp.model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))
        default = mathopt.solve(lp.model, solver)
        pivots[solver.name] = (chosen.solve_stats.simplex_iterations, default.solve_stats.simplex_iterations)
    assert pivots == {"GLOP": (191, 191), "HIGHS": (14, 14)}


def test_barrier_without_crossover_stops_inside_and_crossover_lands_on_a_vertex():
    from barrier_crossover import inside_counts
    off, counts_off = inside_counts("off")
    on, counts_on = inside_counts("on")
    assert counts_off[0] == 410 and counts_off[3] > 10
    assert counts_on == [10, 10, 10, 10]
    assert off.getInfo().objective_function_value < on.getInfo().objective_function_value
    assert on.getInfo().objective_function_value == pytest.approx(234898.1206, abs=1e-3)


def test_the_bare_pdhg_step_reaches_the_plan_and_the_prices():
    from pdhg_sketch import pdhg
    x, y, k = pdhg(report=lambda line: None)
    assert x == pytest.approx([3, 1], abs=1e-5) and y == pytest.approx([2, 0, 1], abs=1e-5)
    assert k == 957
