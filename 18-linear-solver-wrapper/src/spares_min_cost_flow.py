"""Lesson 4.7.3: the spare-transformer shipment of lesson 2.1.3, solved by SimpleMinCostFlow.

First as data straight from lesson 2.1.3 (80 spares on the shelves, 70 wanted), which the solver
refuses; then with a "shelf" node that takes the spares left behind. The cost is checked against
the LP of lesson 2.1.3, rebuilt here in MathOpt. GridCap and its network are fictional.
"""

from ortools.graph.python import min_cost_flow
from ortools.math_opt.python import mathopt

from spares_network import ARCS, DEMAND, NAMES, NODE, SUPPLY


def network(with_shelf: bool):
    smcf = min_cost_flow.SimpleMinCostFlow()
    arcs, kept = {}, {}
    for (i, j), (cost, cap) in ARCS.items():
        arcs[i, j] = smcf.add_arc_with_capacity_and_unit_cost(NODE[i], NODE[j], cap, cost)
    for depot, shelf in SUPPLY.items():
        smcf.set_node_supply(NODE[depot], shelf)
    for region, need in DEMAND.items():
        smcf.set_node_supply(NODE[region], -need)
    if with_shelf:
        shelf = len(NAMES)                                   # one extra node: spares that stay put
        for depot, on_hand in SUPPLY.items():
            kept[depot] = smcf.add_arc_with_capacity_and_unit_cost(NODE[depot], shelf, on_hand, 0)
        smcf.set_node_supply(shelf, -(sum(SUPPLY.values()) - sum(DEMAND.values())))
    return smcf, arcs, kept


smcf, _, _ = network(with_shelf=False)
print(f"supplies sum to {sum(smcf.supply(n) for n in range(smcf.num_nodes()))}: status {smcf.solve().name}")

smcf, arcs, kept = network(with_shelf=True)
status = smcf.solve()
print(f"with a shelf node taking {sum(SUPPLY.values()) - sum(DEMAND.values())}: status {status.name}, "
      f"cost ${smcf.optimal_cost()}k")
for (i, j), arc in arcs.items():
    if smcf.flow(arc) > 0:
        print(f"  {i:10} -> {j:8} {smcf.flow(arc):3}")
print("  left on the shelf: " + ", ".join(f"{smcf.flow(arc)} at {depot}" for depot, arc in kept.items()))

# The same network as lesson 2.1.3's LP, solved by GLOP, for a check.
model = mathopt.Model(name="spares LP")
f = {a: model.add_variable(lb=0, ub=cap, name=f"f_{a[0]}_{a[1]}") for a, (_, cap) in ARCS.items()}
for n in NAMES:
    net = sum(f[a] for a in ARCS if a[0] == n) - sum(f[a] for a in ARCS if a[1] == n)   # out - in
    if n in SUPPLY:
        model.add_linear_constraint(net <= SUPPLY[n], name=f"supply_{n}")
    elif n in DEMAND:
        model.add_linear_constraint(net == -DEMAND[n], name=f"demand_{n}")
    else:
        model.add_linear_constraint(net == 0, name=f"balance_{n}")
model.minimize(sum(cost * f[a] for a, (cost, _) in ARCS.items()))
lp = mathopt.solve(model, mathopt.SolverType.GLOP)
print(f"lesson 2.1.3's LP: cost ${lp.objective_value():,.0f}k; same cost: {lp.objective_value() == smcf.optimal_cost()}")
