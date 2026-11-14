"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Pyomo logs every set it builds and the whole solver log; keep its own logger to warnings.
logging.getLogger("pyomo").setLevel(logging.WARNING)

import pyomo.environ as pyo

from iis import deletion_filter


def shifts(wage_cap, late_cap):
    """Drivers on early and late shifts."""
    m = pyo.ConcreteModel()
    m.early = pyo.Var(bounds=(0, 6))
    m.late = pyo.Var(bounds=(0, 6))
    m.need = pyo.Constraint(expr=m.early + m.late >= 11)
    m.late_cap = pyo.Constraint(expr=m.late <= late_cap)
    m.wages = pyo.Constraint(expr=2 * m.early + 3 * m.late <= wage_cap)
    m.balance = pyo.Constraint(expr=m.late - m.early <= 2)
    m.cost = pyo.Objective(expr=2 * m.early + 3 * m.late)
    return m


print("rows kept, wages <= 40, late <= 3:", deletion_filter(shifts(40, 3)))
print("rows kept, wages <= 20, late <= 6:", deletion_filter(shifts(20, 6)))
