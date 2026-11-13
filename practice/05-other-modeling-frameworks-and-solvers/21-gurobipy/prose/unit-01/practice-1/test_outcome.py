from gurobipy import GRB

from outcome import outcome


def test_an_optimal_solve_is_used():
    assert outcome(GRB.OPTIMAL, 4) == "use"


def test_an_infeasible_solve_reports_a_conflict():
    assert outcome(GRB.INFEASIBLE, 0) == "no plan: infeasible"


def test_a_limit_with_a_plan_is_used_with_its_gap():
    assert outcome(GRB.TIME_LIMIT, 2) == "use, report gap"
    assert outcome(GRB.NODE_LIMIT, 1) == "use, report gap"
    assert outcome(GRB.WORK_LIMIT, 0) == "no plan: limit"
    assert outcome(GRB.INTERRUPTED, 0) == "no plan: limit"


def test_infeasible_or_unbounded_is_not_called_infeasible():
    assert outcome(GRB.INF_OR_UNBD, 0) == "no plan: re-solve with DualReductions=0"
    assert outcome(GRB.UNBOUNDED, 0) == "no plan: unbounded"


def test_any_other_status_is_a_failure():
    assert outcome(GRB.NUMERIC, 0) == "no plan: solver failure"
    assert outcome(GRB.LOADED, 0) == "no plan: solver failure"
