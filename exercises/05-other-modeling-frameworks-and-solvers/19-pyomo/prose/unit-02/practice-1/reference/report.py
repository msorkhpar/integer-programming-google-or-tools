from __future__ import annotations

import pyomo.environ as pyo
from pyomo.contrib.solver.common.factory import SolverFactory
from pyomo.contrib.solver.common.results import SolutionStatus, TerminationCondition

WORDS = {
    TerminationCondition.convergenceCriteriaSatisfied: "optimal",
    TerminationCondition.provenInfeasible: "infeasible",
    TerminationCondition.unbounded: "unbounded",
    TerminationCondition.infeasibleOrUnbounded: "infeasible or unbounded",
}


def outcome(model: pyo.ConcreteModel, **options) -> dict:
    """Solve `model` with HiGHS and say what happened, without raising.

    Returns {"status": a word for the termination condition (or "stopped" for a limit or anything
    else), "objective": the incumbent's objective or None, "plan": {variable name: value} for every
    variable when a solution exists, else {}}.
    """
    results = SolverFactory("highs").solve(model, raise_exception_on_nonoptimal_result=False,
                                           load_solutions=False, **options)
    status = WORDS.get(results.termination_condition, "stopped")
    has_plan = results.solution_status in (SolutionStatus.optimal, SolutionStatus.feasible)
    plan = {}
    if has_plan:
        results.solution_loader.load_vars()
        plan = {v.name: v.value for v in model.component_data_objects(pyo.Var)}
    return {"status": status, "objective": results.incumbent_objective if has_plan else None, "plan": plan}


if __name__ == "__main__":
    m = pyo.ConcreteModel()
    m.x = pyo.Var(domain=pyo.Binary)
    m.y = pyo.Var(domain=pyo.Binary)
    m.c = pyo.Constraint(expr=m.x + m.y <= 1)
    m.o = pyo.Objective(expr=3 * m.x + 2 * m.y, sense=pyo.maximize)
    print(outcome(m))
