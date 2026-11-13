"""The module 13 examples: the selection model, what results hold, solver switching and parameters."""

import dataclasses

import pytest
from ortools.math_opt import rpc_pb2
from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, plan, solve

S = mathopt.SolverType


@pytest.fixture(scope="module")
def small():
    return generate("small")


def reason_of(call) -> tuple[int, str]:
    """Run a call that MathOpt refuses and return the hidden status code and message (OR-Tools 9.15)."""
    with pytest.raises(Exception) as caught:
        call()
    hidden = caught.value.__context__
    return hidden.code, hidden.message


def test_the_model_has_one_binary_per_project_and_one_row_per_label(small):
    sel = build(small)
    names = [row.name for row in sel.model.linear_constraints()]
    assert sel.model.get_num_variables() == len(small.projects) == 40
    assert all(v.integer and v.lower_bound == 0 and v.upper_bound == 1 for v in sel.x.values())
    assert sum(n.startswith("budget_") for n in names) == len(small.years)
    assert sum(n.startswith("must_") for n in names) == sum(p.must_do for p in small.projects)
    assert len(names) == len(set(names))


def test_the_milp_solvers_agree_and_the_plan_keeps_every_rule(small):
    sel = build(small)
    plans = {s: plan(sel, solve(sel.model, s)) for s in (S.HIGHS, S.GSCIP, S.CP_SAT)}
    assert len({tuple(p) for p in plans.values()}) == 1
    funded = set(plans[S.HIGHS])
    assert all(p.project_id in funded for p in small.projects if p.must_do)
    for y in small.years:
        spend = sum(small.project(i).spend(small.project(i).earliest_start).get(y, 0) for i in funded)
        assert spend <= small.budget[y]
    assert solve(sel.model, S.HIGHS).objective_value() == pytest.approx(22_532)


def test_the_lp_relaxation_bounds_the_milp_and_only_simplex_lp_solvers_give_a_basis(small):
    lp = build(small, integer=False)
    glop = solve(lp.model, S.GLOP)
    assert glop.objective_value() == pytest.approx(23_669.4936, abs=1e-3)
    assert glop.has_dual_feasible_solution() and glop.has_basis()
    assert not solve(lp.model, S.GSCIP).has_dual_feasible_solution()
    assert solve(lp.model, S.PDLP).has_dual_feasible_solution()
    assert glop.dual_values(lp.budget[2029]) == pytest.approx(0, abs=1e-9)


def test_a_milp_has_no_dual_solution(small):
    sel = build(small)
    result = solve(sel.model, S.HIGHS)
    assert not result.has_dual_feasible_solution()
    with pytest.raises(ValueError):
        result.dual_values(sel.budget[2027])


def test_an_infeasible_model_has_bounds_but_no_value(small):
    poor = dataclasses.replace(small, budget={y: 100 for y in small.years})
    result = solve(build(poor).model, S.HIGHS)
    assert result.termination.reason == mathopt.TerminationReason.INFEASIBLE
    assert not result.has_primal_feasible_solution()
    with pytest.raises(ValueError):
        result.objective_value()
    assert result.primal_bound() == -float("inf")


def test_a_solution_limit_ends_feasible_with_its_limit(small):
    result = solve(build(small).model, S.HIGHS, mathopt.SolveParameters(solution_limit=1))
    assert result.termination.reason == mathopt.TerminationReason.FEASIBLE
    assert result.termination.limit == mathopt.Limit.SOLUTION
    assert result.objective_value() <= result.dual_bound()


def test_cpsat_rounds_a_continuous_model_and_still_says_optimal(small):
    lp = build(small, integer=False)
    result = solve(lp.model, S.CP_SAT)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert result.objective_value() == pytest.approx(22_532)
    assert all(result.variable_values(v) in (0.0, 1.0) for v in lp.x.values())


def test_lp_only_solvers_refuse_an_integer_model(small):
    milp = build(small).model
    for solver in (S.GLOP, S.PDLP):
        code, message = reason_of(lambda: mathopt.solve(milp, solver))
        assert code == 3 and "does not support integer variables" in message


def test_highs_refuses_threads_and_the_reason_converts_to_value_error(small):
    milp = build(small).model
    code, message = reason_of(lambda: mathopt.solve(milp, S.HIGHS, params=mathopt.SolveParameters(threads=2)))
    meant = mathopt.status_proto_to_exception(rpc_pb2.StatusProto(code=code, message=message))
    assert isinstance(meant, ValueError) and "threads not supported for HiGHS" in str(meant)


def test_only_time_and_gap_parameters_are_accepted_by_every_solver(small):
    lp, milp = build(small, integer=False).model, build(small).model
    pairs = [(S.GLOP, lp), (S.PDLP, lp), (S.HIGHS, lp), (S.GSCIP, lp), (S.HIGHS, milp), (S.GSCIP, milp),
             (S.CP_SAT, milp)]
    for params in (mathopt.SolveParameters(relative_gap_tolerance=0.001),
                   mathopt.SolveParameters(absolute_gap_tolerance=1.0)):
        for solver, model in pairs:
            solve(model, solver, params)
    with pytest.raises(Exception):
        solve(milp, S.CP_SAT, mathopt.SolveParameters(node_limit=10))


def test_a_cutoff_above_the_optimum_cannot_be_parsed(small):
    milp = build(small).model
    with pytest.raises(ValueError, match="not a valid Limit"):
        solve(milp, S.GSCIP, mathopt.SolveParameters(cutoff_limit=30_000.0))
    assert solve(milp, S.GSCIP, mathopt.SolveParameters(cutoff_limit=20_000.0)).objective_value() == pytest.approx(22_532)


def test_a_duplicate_variable_name_is_refused_at_solve_time():
    model = mathopt.Model()
    a, b = model.add_binary_variable(name="x"), model.add_binary_variable(name="x")
    model.maximize(a + b)
    code, message = reason_of(lambda: mathopt.solve(model, S.HIGHS))
    assert code == 3 and "duplicate name" in message
