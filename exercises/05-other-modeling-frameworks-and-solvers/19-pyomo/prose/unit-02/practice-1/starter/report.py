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
    # TODO: solve without raising and without loading; map the termination condition through WORDS;
    #       load and read the plan only when the solution status says there is one.
    return {"status": "optimal", "objective": None, "plan": {}}


if __name__ == "__main__":
    m = pyo.ConcreteModel()
    m.x = pyo.Var(domain=pyo.Binary)
    m.y = pyo.Var(domain=pyo.Binary)
    m.c = pyo.Constraint(expr=m.x + m.y <= 1)
    m.o = pyo.Objective(expr=3 * m.x + 2 * m.y, sense=pyo.maximize)
    print(outcome(m))
