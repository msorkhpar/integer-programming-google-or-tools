"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Pyomo logs every set it builds and the whole solver log; keep its own logger to warnings.
logging.getLogger("pyomo").setLevel(logging.WARNING)

import pyomo.environ as pyo

from report import outcome


def depot(vans_needed):
    """Small vans (cost 2) and lorries (cost 5, carry 3) covering a load."""
    m = pyo.ConcreteModel()
    m.van = pyo.Var(domain=pyo.NonNegativeIntegers, bounds=(0, 4))
    m.lorry = pyo.Var(domain=pyo.NonNegativeIntegers, bounds=(0, 2))
    m.cover = pyo.Constraint(expr=m.van + 3 * m.lorry >= vans_needed)
    m.cost = pyo.Objective(expr=2 * m.van + 5 * m.lorry)
    return m


print("load 7:", outcome(depot(7)))
print("load 20:", outcome(depot(20)))
