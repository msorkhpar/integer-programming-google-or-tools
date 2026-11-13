"""The module 12 examples: one problem in several APIs, the runner's backends, and where refusals appear."""

import importlib

import pytest
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from ortools.graph.python import linear_sum_assignment, min_cost_flow
from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

S = mathopt.SolverType


def quietly(name: str):
    """Import a lesson program (it prints its output at import; pytest captures it)."""
    return importlib.import_module(name)


def test_the_four_apis_fund_the_same_tiny_projects():
    pick = quietly("budget_pick")
    answers = [pick.with_mathopt(), pick.with_cp_sat(), pick.with_pywraplp(), pick.with_knapsack_solver()]
    assert all(a == ["P001", "P004", "P005", "P006"] for a in answers)
    assert sum(pick.value[i] for i in answers[0]) == 4876
    assert sum(pick.cost[i] for i in answers[0]) == 7370 <= pick.budget == 7390


def test_the_assignment_solver_and_cp_sat_agree_on_the_crews():
    crews = quietly("crew_sites")
    assert crews.with_assignment_solver() == crews.with_cp_sat() == (15, [1, 0, 2, 3])


def test_the_side_rules_change_the_plan_as_the_lesson_says():
    side = quietly("side_rule")
    assert side.assignment_solver(set()).startswith("15 hours")
    assert side.assignment_solver({(0, 1)}) == side.cp_sat({(0, 1)}, None)
    assert side.cp_sat({(0, 1)}, None).startswith("18 hours")
    assert side.cp_sat({(0, 1)}, 9) == "19 hours  Ridge->S1, Valley->S3, Coast->S2, Plains->S4"


def test_the_route_is_found_but_not_proven():
    route = quietly("inspection_route")
    assert route.solution.ObjectiveValue() == 40
    assert route.routing.status() == routing_enums_pb2.RoutingSearchStatus.ROUTING_SUCCESS


def test_mathopt_solves_with_exactly_five_solvers_here():
    solves = set()
    for solver in S:
        try:
            mathopt.solve(mathopt.Model(), solver)
            solves.add(solver)
        except Exception:
            pass
    assert solves == {S.GSCIP, S.GLOP, S.CP_SAT, S.PDLP, S.HIGHS}


def test_the_wrapper_has_eight_backends_and_no_commercial_one():
    present = {i for i in ("GLOP", "PDLP", "CLP", "HIGHS", "CBC", "SCIP", "CP_SAT", "BOP",
                           "GUROBI", "XPRESS", "CPLEX", "GLPK") if pywraplp.Solver.CreateSolver(i)}
    assert present == {"GLOP", "PDLP", "CLP", "HIGHS", "CBC", "SCIP", "CP_SAT", "BOP"}
    assert not pywraplp.Solver.CreateSolver("GLOP").IsMip()
    assert pywraplp.Solver.CreateSolver("HIGHS").SolverVersion() == "PDLP Solver"


def test_gurobi_fails_through_mathopt_without_a_named_cause():
    model = mathopt.Model()
    model.maximize(model.add_binary_variable())
    with pytest.raises(RuntimeError, match="bad_function_call"):
        mathopt.solve(model, S.GUROBI)


def test_the_wrappers_glop_relaxes_an_integer_variable_and_mathopts_refuses():
    solver = pywraplp.Solver.CreateSolver("GLOP")
    a, b = solver.NumVar(0, 10, "a"), solver.IntVar(0, 10, "b")
    solver.Add(0.37 * a + 1.13 * b <= 7.71)
    solver.Maximize(1.01 * a + 2.9 * b)
    assert solver.Solve() == solver.OPTIMAL
    assert b.solution_value() == pytest.approx(3.5487, abs=1e-4)
    model = mathopt.Model()
    model.add_integer_variable(lb=0, ub=10)
    with pytest.raises(Exception) as caught:
        mathopt.solve(model, S.GLOP)
    assert caught.value.__context__.message == "Glop does not support integer variables"


def test_cp_sat_refuses_while_building_and_after_solving():
    model = cp_model.CpModel()
    n = model.new_int_var(0, 10, "n")
    with pytest.raises(TypeError):
        model.add(0.37 * n <= 7)
    bad = cp_model.CpModel()
    bad.new_int_var(5, 3, "m")
    solver = cp_model.CpSolver()
    assert solver.solve(bad) == cp_model.MODEL_INVALID
    assert "no domain" in bad.validate()


def test_special_solvers_refuse_fractions_and_flows_report_status():
    with pytest.raises(TypeError):
        linear_sum_assignment.SimpleLinearSumAssignment().add_arc_with_cost(0, 0, 2.5)
    flow = min_cost_flow.SimpleMinCostFlow()
    flow.add_arc_with_capacity_and_unit_cost(0, 1, 3, 2)
    flow.set_node_supply(0, 5)
    flow.set_node_supply(1, -5)
    assert flow.solve() == flow.INFEASIBLE
    flow.set_node_supply(1, -4)
    assert flow.solve() == flow.UNBALANCED


def test_routing_returns_none_when_it_finds_no_route():
    manager = pywrapcp.RoutingIndexManager(3, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(lambda i, j: 1))
    load = routing.RegisterUnaryTransitCallback(lambda i: [0, 2, 2][manager.IndexToNode(i)])
    routing.AddDimensionWithVehicleCapacity(load, 0, [3], True, "load")
    assert routing.SolveWithParameters(pywrapcp.DefaultRoutingSearchParameters()) is None
    assert routing.status() == routing_enums_pb2.RoutingSearchStatus.ROUTING_FAIL
