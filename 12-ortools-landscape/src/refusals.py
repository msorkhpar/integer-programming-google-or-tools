"""Where each OR-Tools API reports a request it will not carry out, in OR-Tools 9.15 (lesson 4.1.2).

The model is lesson 4.2.3's one-continuous model: max 1.01 a + 2.9 b subject to
0.37 a + 1.13 b <= 7.71, a continuous in [0, 10], b integer in [0, 10].
"""

from __future__ import annotations

from ortools.algorithms.python import knapsack_solver
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from ortools.graph.python import linear_sum_assignment, min_cost_flow
from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from quiet import captured, muted

print("MathOpt: an exception from mathopt.solve")
model = mathopt.Model(name="one-continuous")
a = model.add_variable(lb=0, ub=10, name="a")
b = model.add_integer_variable(lb=0, ub=10, name="b")
model.add_linear_constraint(0.37 * a + 1.13 * b <= 7.71, name="cap")
model.maximize(1.01 * a + 2.9 * b)
try:
    mathopt.solve(model, mathopt.SolverType.GLOP)
except Exception as error:
    print(f"  GLOP, integer b: {type(error).__name__}; __context__.message = {error.__context__.message!r}")

print("pywraplp: None from CreateSolver, or a status from Solve")
print("  CreateSolver('CPLEX') returns", pywraplp.Solver.CreateSolver("CPLEX"))
for solver_id in ("GLOP", "HIGHS", "BOP"):
    solver = pywraplp.Solver.CreateSolver(solver_id)
    pa, pb = solver.NumVar(0, 10, "a"), solver.IntVar(0, 10, "b")
    solver.Add(0.37 * pa + 1.13 * pb <= 7.71, "cap")
    solver.Maximize(1.01 * pa + 2.9 * pb)
    log: list[str] = []
    with muted(), captured(log, fd=2):                      # the reason, if any, goes to the log
        status = solver.Solve()
    names = {solver.OPTIMAL: "OPTIMAL", solver.ABNORMAL: "ABNORMAL", solver.INFEASIBLE: "INFEASIBLE"}
    print(f"  {solver_id:<5} integer b: Solve() = {names.get(status, status)}, b = {pb.solution_value():.4f}")
    for line in log:
        if "not supported" in line:
            print("        log:", line.split("] ", 1)[1])

print("CP-SAT: a TypeError while building, or MODEL_INVALID from solve")
cp = cp_model.CpModel()
n = cp.new_int_var(0, 10, "n")
try:
    cp.add(0.37 * n <= 7)
except TypeError as error:
    print("  a 0.37 coefficient:", str(error).split(":")[0])
bad = cp_model.CpModel()
bad.new_int_var(5, 3, "m")                                  # lower bound above upper bound
solver = cp_model.CpSolver()
status = solver.solve(bad)
print(f"  domain [5, 3]: solve() = {solver.status_name(status)}; validate() = {bad.validate()!r}")
try:
    solver.status_name()
except TypeError as error:
    print("  status_name() with no argument:", type(error).__name__)

print("special-purpose solvers: a TypeError for a fractional number")
assign = linear_sum_assignment.SimpleLinearSumAssignment()
try:
    assign.add_arc_with_cost(0, 0, 2.5)
except TypeError as error:
    print("  assignment, cost 2.5:", str(error).split(". ")[0])
pack = knapsack_solver.KnapsackSolver(knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "k")
try:
    pack.init([1.5, 2], [[1, 2]], [3])
except TypeError as error:
    print("  knapsack, value 1.5:", str(error).split(". ")[0])

print("graph: a status from solve()")
flow = min_cost_flow.SimpleMinCostFlow()
flow.add_arc_with_capacity_and_unit_cost(0, 1, 3, 2)        # 3 units at most from 0 to 1
flow.set_node_supply(0, 5)
flow.set_node_supply(1, -5)
print("  ship 5 over an arc of capacity 3:", flow.solve().name)
flow.set_node_supply(1, -4)
print("  supply 5, demand 4:", flow.solve().name)
flow.add_arc_with_capacity_and_unit_cost(0, 1, 2, 3)        # a second arc beside it, 2 more units
flow.set_node_supply(1, -5)
status = flow.solve()
print("  with a second arc:", status.name, "| status == flow.OPTIMAL:", status == flow.OPTIMAL,
      "| cost", flow.optimal_cost())
print("  statuses:", ", ".join(min_cost_flow.SimpleMinCostFlow.Status.__members__))

print("routing: None from SolveWithParameters, and the reason in status()")
manager = pywrapcp.RoutingIndexManager(3, 1, 0)
routing = pywrapcp.RoutingModel(manager)
routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(lambda i, j: 1))
load = routing.RegisterUnaryTransitCallback(lambda i: [0, 2, 2][manager.IndexToNode(i)])
routing.AddDimensionWithVehicleCapacity(load, 0, [3], True, "load")    # carries 3, stops need 4
solution = routing.SolveWithParameters(pywrapcp.DefaultRoutingSearchParameters())
print("  stops needing 4 units, a van carrying 3:", solution, routing_enums_pb2.RoutingSearchStatus.Value.Name(routing.status()))
