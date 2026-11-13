import pytest
from ortools.linear_solver import pywraplp

from report import crews_model, outcome


def test_an_optimal_solve_reports_its_value_and_plan():
    solver, x = crews_model(need=7, most=5)        # 3 line crews and 1 field crew cost 18
    result = outcome(solver, solver.Solve(), x)
    assert result["status"] == "OPTIMAL"
    assert result["value"] == pytest.approx(18)
    assert result["plan"] == pytest.approx({"line": 3, "field": 1})


def test_an_infeasible_solve_reports_no_plan():
    solver, x = crews_model(need=40, most=5)       # 5 + 5 crews cover at most 15
    result = outcome(solver, solver.Solve(), x)
    assert result == {"status": "INFEASIBLE", "value": None, "plan": None}


def test_a_feasible_solve_stopped_by_a_limit_still_has_a_plan():
    solver, x = crews_model(need=7, most=5)
    solver.Solve()
    result = outcome(solver, pywraplp.Solver.FEASIBLE, x)   # as if a time limit had stopped the search
    assert result["status"] == "FEASIBLE"
    assert result["plan"] == pytest.approx({"line": 3, "field": 1})


def test_an_unbounded_solve_reports_no_plan():
    solver = pywraplp.Solver.CreateSolver("SCIP")
    x = {"line": solver.IntVar(0, solver.infinity(), "line")}
    solver.Maximize(x["line"])
    result = outcome(solver, solver.Solve(), x)
    assert result == {"status": "UNBOUNDED", "value": None, "plan": None}
