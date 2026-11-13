"""Lesson 4.7.3: what SimpleMinCostFlow does with a shortfall, with surplus stock, and with fractional data.

The network is lesson 2.1.3's spare-transformer network. GridCap and its network are fictional.
"""

from ortools.graph.python import min_cost_flow

from spares_network import ARCS, DEMAND, NODE, SUPPLY


def network(closed=(), extra_demand=0):
    """The network with no shelf node: supplies 80, demands 70 (+ extra_demand at Valley)."""
    smcf = min_cost_flow.SimpleMinCostFlow()
    for (i, j), (cost, cap) in ARCS.items():
        smcf.add_arc_with_capacity_and_unit_cost(NODE[i], NODE[j], 0 if (i, j) in closed else cap, cost)
    for depot, shelf in SUPPLY.items():
        smcf.set_node_supply(NODE[depot], shelf)
    for region, need in DEMAND.items():
        smcf.set_node_supply(NODE[region], -(need + (extra_demand if region == "Valley" else 0)))
    return smcf


# Surplus stock: solve() refuses unequal totals; solve_max_flow_with_min_cost() ships what it can.
smcf = network()
print(f"80 on hand, 70 wanted: solve() -> {smcf.solve().name}; "
      f"solve_max_flow_with_min_cost() -> {smcf.solve_max_flow_with_min_cost().name}, "
      f"{smcf.maximum_flow()} shipped, cost ${smcf.optimal_cost()}k")

# Balanced totals, but a route closed: the demand cannot all be met.
smcf = network(closed=[("Northgate", "Central")], extra_demand=10)
print(f"80 wanted, Northgate->Central closed: solve() -> {smcf.solve().name}")
smcf = network(closed=[("Northgate", "Central")], extra_demand=10)
status = smcf.solve_max_flow_with_min_cost()
print(f"  solve_max_flow_with_min_cost() -> {status.name}, {smcf.maximum_flow()} shipped, cost ${smcf.optimal_cost()}k")

# Fractional data: the solver's arguments are integers.
smcf = min_cost_flow.SimpleMinCostFlow()
try:
    smcf.add_arc_with_capacity_and_unit_cost(0, 1, 20, 2.5)
except TypeError as error:
    print(f"unit cost 2.5 -> TypeError: {str(error).splitlines()[0]}")
arc = smcf.add_arc_with_capacity_and_unit_cost(0, 1, 20, round(2.5 * 10))     # in $100s instead of $k
print(f"unit cost 25 in $100s accepted: arc {arc}, unit cost {smcf.unit_cost(arc)}")
