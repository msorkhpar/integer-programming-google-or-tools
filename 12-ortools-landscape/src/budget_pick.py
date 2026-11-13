# Adapted from the OR-Tools example knapsack.py, https://github.com/google/or-tools/blob/v9.15/ortools/algorithms/samples/knapsack.py (Apache-2.0)
"""GridCap tiny's budget-only selection, one knapsack, in four OR-Tools APIs (lesson 4.1.1).

`with_knapsack_solver` follows the OR-Tools knapsack sample; the other three write the same model in
MathOpt, CP-SAT and the linear solver wrapper.
"""

from __future__ import annotations

from ortools.algorithms.python import knapsack_solver
from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import generate
from quiet import muted

tiny = generate("tiny")
ids = [p.project_id for p in tiny.projects]
value = {p.project_id: p.value for p in tiny.projects}      # v_i, NPV in $k
cost = {p.project_id: p.capex for p in tiny.projects}       # c_i, capex in $k
budget = tiny.capital_budget                                # B, in $k


def with_mathopt() -> list[str]:
    model = mathopt.Model(name="budget_pick")
    x = {i: model.add_binary_variable(name=f"x_{i}") for i in ids}
    model.add_linear_constraint(sum(cost[i] * x[i] for i in ids) <= budget, name="budget")
    model.maximize(sum(value[i] * x[i] for i in ids))
    with muted():
        result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return [i for i in ids if result.variable_values(x[i]) > 0.5]


def with_cp_sat() -> list[str]:
    model = cp_model.CpModel()
    x = {i: model.new_bool_var(f"x_{i}") for i in ids}
    model.add(sum(cost[i] * x[i] for i in ids) <= budget)
    model.maximize(sum(value[i] * x[i] for i in ids))
    solver = cp_model.CpSolver()
    solver.solve(model)
    return [i for i in ids if solver.value(x[i])]


def with_pywraplp() -> list[str]:
    solver = pywraplp.Solver.CreateSolver("SCIP")
    x = {i: solver.BoolVar(f"x_{i}") for i in ids}
    solver.Add(sum(cost[i] * x[i] for i in ids) <= budget, "budget")
    solver.Maximize(sum(value[i] * x[i] for i in ids))
    solver.Solve()
    return [i for i in ids if x[i].solution_value() > 0.5]


def with_knapsack_solver() -> list[str]:
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "budget_pick")
    solver.init([value[i] for i in ids], [[cost[i] for i in ids]], [budget])
    solver.solve()
    return [i for n, i in enumerate(ids) if solver.best_solution_contains(n)]


answers = {"MathOpt (HiGHS)": with_mathopt(), "CP-SAT": with_cp_sat(),
           "pywraplp (SCIP)": with_pywraplp(), "KnapsackSolver": with_knapsack_solver()}
print(f"GridCap tiny: {len(ids)} projects, budget {budget:,} $k")
for api, chosen in answers.items():
    total = sum(value[i] for i in chosen)
    spent = sum(cost[i] for i in chosen)
    print(f"{api:<16} NPV {total:>5,}  spend {spent:,}  {' '.join(chosen)}")
print("all four choose the same projects:", len({tuple(c) for c in answers.values()}) == 1)

# CP-SAT's verdict, read before the plan, and an objective with decimals.
model = cp_model.CpModel()
x = {i: model.new_bool_var(f"x_{i}") for i in ids}
model.add(sum(cost[i] * x[i] for i in ids) <= budget)
model.maximize(sum(round(value[i] / 1000, 2) * x[i] for i in ids))      # NPV in $M, two decimals
solver = cp_model.CpSolver()
status = solver.solve(model)
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):             # a plan to read; OPTIMAL also proves it best
    print(f"CP-SAT status {solver.status_name(status)}, objective {solver.objective_value:.2f} $M,",
          " ".join(i for i in ids if solver.value(x[i])))
print("CP-SAT statuses:", ", ".join(cp_model.CpSolverStatus.__members__))
