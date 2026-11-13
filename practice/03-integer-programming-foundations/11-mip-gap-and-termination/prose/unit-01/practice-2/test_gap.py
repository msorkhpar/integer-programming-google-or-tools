import math

import pytest
from ortools.math_opt.python import mathopt

from gap import read_gap

INF = math.inf


def result(primal: float, dual: float, reason=mathopt.TerminationReason.FEASIBLE, limit=mathopt.Limit.TIME):
    """A SolveResult as a solver would return it, holding only how the run ended."""
    return mathopt.SolveResult(termination=mathopt.Termination(
        reason=reason, limit=limit, objective_bounds=mathopt.ObjectiveBounds(primal_bound=primal, dual_bound=dual)))


def test_a_maximization_stopped_early_gives_its_bracket_and_gaps():
    got = read_gap(result(1_000.0, 1_050.0))
    assert got == {"incumbent": 1_000.0, "bound": 1_050.0, "absolute": pytest.approx(50.0),
                   "relative": pytest.approx(0.05)}


def test_a_closed_bracket_gives_zero_gaps():
    got = read_gap(result(500.0, 500.0, mathopt.TerminationReason.OPTIMAL, None))
    assert got == {"incumbent": 500.0, "bound": 500.0, "absolute": 0.0, "relative": 0.0}


def test_a_minimization_gives_a_positive_absolute_gap():
    got = read_gap(result(800.0, 760.0))
    assert got == {"incumbent": 800.0, "bound": 760.0, "absolute": pytest.approx(40.0),
                   "relative": pytest.approx(0.05)}


def test_a_run_without_a_plan_has_no_incumbent_and_infinite_gaps():
    got = read_gap(result(-INF, 900.0, mathopt.TerminationReason.NO_SOLUTION_FOUND))
    assert got == {"incumbent": None, "bound": 900.0, "absolute": INF, "relative": INF}


def test_an_infeasible_run_has_neither_number():
    got = read_gap(result(-INF, -INF, mathopt.TerminationReason.INFEASIBLE, None))
    assert got == {"incumbent": None, "bound": None, "absolute": INF, "relative": INF}


def test_a_zero_incumbent_with_a_gap_has_an_infinite_relative_gap():
    got = read_gap(result(0.0, 30.0))
    assert got == {"incumbent": 0.0, "bound": 30.0, "absolute": pytest.approx(30.0), "relative": INF}
