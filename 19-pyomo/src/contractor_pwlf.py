"""Lesson 5.1.4: the same contractor tiers with Pyomo's newer piecewise API, pyomo.contrib.piecewise.

GridCap is a fictional utility's portfolio. A `PiecewiseLinearFunction` is a function object:
it is called on a variable inside an ordinary constraint, and a transformation chosen afterwards
writes its formulation, the way the GDP transformations of lesson 5.1.3 do.
"""

import pyomo.environ as pyo
from pyomo.contrib.piecewise import PiecewiseLinearFunction

from contractor_model import COST, MONTHS, build
from gridcap import generate
from pyomo_timing import highs

small = generate("small")


def with_function(transformations):
    m = build(small, 40)
    m.tiers.deactivate()                                    # drop the Piecewise component's rows
    m.price = PiecewiseLinearFunction(tabular_data=dict(zip(MONTHS, COST)))
    m.pay = pyo.Constraint(expr=m.contract >= m.price(m.bought))
    for name in transformations:
        pyo.TransformationFactory(name).apply_to(m)
    return m


m = with_function([])
print("price(15) =", m.price(15), " price(30) =", m.price(30))

for chain in (["contrib.piecewise.incremental"], ["contrib.piecewise.disaggregated_logarithmic"],
              ["contrib.piecewise.inner_repn_gdp", "gdp.hull"]):
    m = with_function(chain)
    binaries = sum(1 for v in m.component_data_objects(pyo.Var) if v.is_binary()) - len(m.x)
    highs().solve(m)
    print(f"{' + '.join(chain):48} {binaries} binaries  net {pyo.value(m.net):,.1f}"
          f"  bought {m.bought.value:.1f}  contract {m.contract.value:.1f}")
