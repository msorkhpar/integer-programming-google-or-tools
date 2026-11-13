from __future__ import annotations

import pyomo.environ as pyo
from pyomo.contrib.solver.common.factory import SolverFactory
from pyomo.contrib.solver.common.results import TerminationCondition


def feasible(model: pyo.ConcreteModel) -> bool:
    """Whether the model's active rows and the variables' bounds have a common point."""
    results = SolverFactory("highs").solve(model, raise_exception_on_nonoptimal_result=False,
                                           load_solutions=False)
    return results.termination_condition != TerminationCondition.provenInfeasible


def deletion_filter(model: pyo.ConcreteModel) -> list[str]:
    """Names of the rows of one irreducible infeasible subsystem of an infeasible model (bounds kept)."""
    # TODO: deactivate the objective; take each active row in turn: drop it, and put it back only
    #       if the model without it is feasible. The rows left active are the subsystem.
    return []


if __name__ == "__main__":
    m = pyo.ConcreteModel()
    m.x = pyo.Var(bounds=(0, 10))
    m.y = pyo.Var(bounds=(0, 10))
    m.a = pyo.Constraint(expr=m.x + m.y >= 12)
    m.b = pyo.Constraint(expr=m.x <= 3)
    m.c = pyo.Constraint(expr=m.y <= 4)
    m.d = pyo.Constraint(expr=m.x - m.y <= 5)
    print(deletion_filter(m))
