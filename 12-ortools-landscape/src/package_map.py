"""Where each OR-Tools family lives in the pip package, checked by importing it (lesson 4.1.1)."""

from __future__ import annotations

import importlib
import pkgutil

import ortools

FAMILIES = [
    # (family, module to import, names the lessons of section 4 start from)
    ("MathOpt", "ortools.math_opt.python.mathopt", ["Model", "solve", "SolverType"]),
    ("CP-SAT", "ortools.sat.python.cp_model", ["CpModel", "CpSolver"]),
    ("linear solver wrapper", "ortools.linear_solver.pywraplp", ["Solver"]),
    ("routing", "ortools.constraint_solver.pywrapcp", ["RoutingIndexManager", "RoutingModel"]),
    ("graph: max flow", "ortools.graph.python.max_flow", ["SimpleMaxFlow"]),
    ("graph: min-cost flow", "ortools.graph.python.min_cost_flow", ["SimpleMinCostFlow"]),
    ("graph: assignment", "ortools.graph.python.linear_sum_assignment", ["SimpleLinearSumAssignment"]),
    ("knapsack", "ortools.algorithms.python.knapsack_solver", ["KnapsackSolver"]),
]

print("OR-Tools", ortools.__version__)
print(f"{'family':<22} {'import from':<43} names")
for family, module_name, names in FAMILIES:
    module = importlib.import_module(module_name)
    missing = [n for n in names if not hasattr(module, n)]
    shown = ", ".join(names) + (f"  MISSING {missing}" if missing else "")
    print(f"{family:<22} {module_name:<43} {shown}")

used = {name.split(".")[1] for _, name, _ in FAMILIES}
others = sorted(m.name for m in pkgutil.iter_modules(ortools.__path__) if m.name not in used)
print("other top-level packages:", ", ".join(others))
