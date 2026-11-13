"""Lessons 4.7.3: the spare-transformer network of lesson 2.1.3, with node numbers for the graph solvers.

The data is lesson 2.1.3's flow.py. Depots, hub, costs and capacities are invented for this course,
like the rest of GridCap.
"""

SUPPLY = {"Northgate": 45, "Southport": 35}                         # spares on the shelf
DEMAND = {"Ridge": 15, "Valley": 25, "Coast": 18, "Plains": 12}      # spares each region needs
HUB = "Central"
#: (from, to) -> ($k per transformer moved, most transformers the route carries)
ARCS = {
    ("Northgate", "Ridge"): (4, 20), ("Northgate", "Valley"): (6, 10), ("Northgate", HUB): (2, 40),
    ("Southport", "Coast"): (3, 25), ("Southport", "Plains"): (7, 10), ("Southport", HUB): (2, 30),
    (HUB, "Ridge"): (3, 30), (HUB, "Valley"): (3, 30), (HUB, "Coast"): (4, 30), (HUB, "Plains"): (3, 30),
}

#: The graph solvers number their nodes 0, 1, 2, ...; these are the names, in that order.
NAMES = list(SUPPLY) + [HUB] + list(DEMAND)
NODE = {name: i for i, name in enumerate(NAMES)}
