"""GridCap's plan with two prioritized objectives: NPV first, then the least money spent."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from in_order import solve_in_order
from plan_model import build

small = generate("small")


def scenario(npv_priority: int, spend_priority: int, npv_tolerance: float | None):
    pm = build(small)
    pm.model.objective.priority = npv_priority                      # max NPV is the primary objective
    total_spend = mathopt.fast_sum(pm.spend.values())
    pm.model.add_minimization_objective(total_spend, priority=spend_priority, name="spend")
    params = mathopt.ModelSolveParameters()
    if npv_tolerance is not None:
        params.objective_parameters[pm.model.objective] = mathopt.ObjectiveParameters(
            objective_degradation_relative_tolerance=npv_tolerance)
    reached, values = solve_in_order(pm.model, mathopt.SolverType.HIGHS, params)
    chosen = [(pid, t) for (pid, t), v in pm.x.items() if values[v.name] > 0.5]
    npv = sum(small.project(pid).npv[t] for pid, t in chosen)
    return npv, reached["spend"], len(chosen)


for label, args in [("NPV, then spend, exact      ", (0, 1, None)),
                    ("NPV within 1%, then spend   ", (0, 1, 0.01)),
                    ("spend first, then NPV       ", (2, 1, None))]:
    npv, spent, started = scenario(*args)
    print(f"{label} NPV {npv:9,.0f}  spend {spent:9,.0f}  projects {started}")
