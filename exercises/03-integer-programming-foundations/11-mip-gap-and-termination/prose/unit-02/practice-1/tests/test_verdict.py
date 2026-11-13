import math

from ortools.math_opt.python import mathopt

from verdict import verdict

R = mathopt.TerminationReason
L = mathopt.Limit


def ended(reason, limit=None, primal=0.0, dual=0.0):
    return mathopt.Termination(reason=reason, limit=limit,
                               objective_bounds=mathopt.ObjectiveBounds(primal_bound=primal, dual_bound=dual))


def test_an_optimal_run_has_a_settled_plan():
    assert verdict(ended(R.OPTIMAL, primal=420.0, dual=420.0)) == {"has_plan": True, "settled": True, "limit": None}


def test_a_feasible_run_has_an_unsettled_plan_and_names_its_limit():
    got = verdict(ended(R.FEASIBLE, L.NODE, primal=400.0, dual=430.0))
    assert got == {"has_plan": True, "settled": False, "limit": "NODE"}


def test_a_limit_stop_without_a_plan_has_none():
    got = verdict(ended(R.NO_SOLUTION_FOUND, L.TIME, primal=-math.inf, dual=430.0))
    assert got == {"has_plan": False, "settled": False, "limit": "TIME"}


def test_an_infeasible_run_is_settled_without_a_plan():
    got = verdict(ended(R.INFEASIBLE, primal=-math.inf, dual=-math.inf))
    assert got == {"has_plan": False, "settled": True, "limit": None}


def test_optimal_within_a_tolerance_is_still_settled():
    got = verdict(ended(R.OPTIMAL, primal=419.0, dual=420.0))
    assert got == {"has_plan": True, "settled": True, "limit": None}


def test_an_undetermined_limit_is_named_as_such():
    got = verdict(ended(R.FEASIBLE, L.UNDETERMINED, primal=400.0, dual=430.0))
    assert got == {"has_plan": True, "settled": False, "limit": "UNDETERMINED"}
