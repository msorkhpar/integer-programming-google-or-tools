"""A flow model: ship spare transformers from two depots, through a hub or direct, to four regions.

Depots, hub, costs and capacities are invented for this course, like the rest of GridCap.
"""

from ortools.math_opt.python import mathopt

SUPPLY = {"Northgate": 45, "Southport": 35}                         # spares on the shelf
DEMAND = {"Ridge": 15, "Valley": 25, "Coast": 18, "Plains": 12}      # spares each region needs
HUB = "Central"
#: (from, to) -> ($k per transformer moved, most transformers the route carries)
ARCS = {
    ("Northgate", "Ridge"): (4, 20), ("Northgate", "Valley"): (6, 10), ("Northgate", HUB): (2, 40),
    ("Southport", "Coast"): (3, 25), ("Southport", "Plains"): (7, 10), ("Southport", HUB): (2, 30),
    (HUB, "Ridge"): (3, 30), (HUB, "Valley"): (3, 30), (HUB, "Coast"): (4, 30), (HUB, "Plains"): (3, 30),
}

model = mathopt.Model(name="spare transformers")
f = {(i, j): model.add_variable(lb=0, ub=cap, name=f"f_{i}_{j}") for (i, j), (_, cap) in ARCS.items()}


def inflow(n):
    return sum(f[i, j] for (i, j) in ARCS if j == n)


def outflow(n):
    return sum(f[i, j] for (i, j) in ARCS if i == n)


for n, amount in SUPPLY.items():
    model.add_linear_constraint(outflow(n) - inflow(n) <= amount, name=f"supply_{n}")   # spares may stay put
model.add_linear_constraint(inflow(HUB) - outflow(HUB) == 0, name=f"balance_{HUB}")   # the hub stores nothing
for n, amount in DEMAND.items():
    model.add_linear_constraint(inflow(n) - outflow(n) == amount, name=f"demand_{n}")
model.minimize(sum(cost * f[a] for a, (cost, _) in ARCS.items()))

result = mathopt.solve(model, mathopt.SolverType.GLOP)
print(f"{result.termination.reason.name}, cost ${result.objective_value():,.0f}k")
for (i, j), var in f.items():
    if result.variable_values(var) > 1e-9:
        print(f"  {i:10} -> {j:8} {result.variable_values(var):5.1f}")
