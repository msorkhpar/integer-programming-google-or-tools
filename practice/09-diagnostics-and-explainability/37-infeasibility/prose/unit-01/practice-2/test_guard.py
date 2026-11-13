from ortools.math_opt.python import mathopt

from guard import next_step

R = mathopt.TerminationReason


def ended(reason, limit=None, primal=0.0, dual=0.0):
    bounds = mathopt.ObjectiveBounds(primal_bound=primal, dual_bound=dual)
    return mathopt.SolveResult(termination=mathopt.Termination(reason=reason, limit=limit, objective_bounds=bounds))


def test_a_proven_plan_is_published_and_a_proven_conflict_is_explained():
    assert next_step(ended(R.OPTIMAL, primal=120.0, dual=120.0), 0.01) == "publish"
    assert next_step(ended(R.INFEASIBLE), 0.01) == "conflict"
    assert next_step(ended(R.UNBOUNDED), 0.01) == "model-bug"


def test_infeasible_or_unbounded_is_settled_before_anyone_hunts_a_conflict():
    assert next_step(ended(R.INFEASIBLE_OR_UNBOUNDED), 0.01) == "separate"


def test_a_limit_without_a_plan_is_a_rerun_not_a_conflict():
    assert next_step(ended(R.NO_SOLUTION_FOUND, limit=mathopt.Limit.TIME), 0.01) == "rerun"


def test_a_plan_stopped_by_a_limit_is_published_only_within_the_gap():
    assert next_step(ended(R.FEASIBLE, limit=mathopt.Limit.TIME, primal=1000.0, dual=1004.0), 0.01) == "publish"
    assert next_step(ended(R.FEASIBLE, limit=mathopt.Limit.TIME, primal=1000.0, dual=1050.0), 0.01) == "rerun"


def test_the_gap_of_a_minimization_is_its_size_not_its_sign():
    # Minimizing cost: the bound lies below the plan's cost.
    assert next_step(ended(R.FEASIBLE, limit=mathopt.Limit.TIME, primal=200.0, dual=190.0), 0.01) == "rerun"
    assert next_step(ended(R.FEASIBLE, limit=mathopt.Limit.TIME, primal=200.0, dual=199.5), 0.01) == "publish"


def test_a_plan_worth_zero_is_published_only_when_the_bound_meets_it():
    assert next_step(ended(R.FEASIBLE, limit=mathopt.Limit.TIME, primal=0.0, dual=0.0), 0.01) == "publish"
    assert next_step(ended(R.FEASIBLE, limit=mathopt.Limit.TIME, primal=0.0, dual=3.0), 0.01) == "rerun"


def test_an_answer_with_no_rule_is_escalated():
    assert next_step(ended(R.IMPRECISE), 0.01) == "escalate"
    assert next_step(ended(R.NUMERICAL_ERROR), 0.01) == "escalate"
