"""Lesson 4.7.3: how many spares can the network deliver at most, and which routes limit it?

A super source feeds each depot up to its shelf, and each region drains into a super sink up to
its demand, so one source-to-sink max flow answers the whole question. GridCap is fictional.
"""

from ortools.graph.python import max_flow

from spares_network import ARCS, DEMAND, NAMES, NODE, SUPPLY

SOURCE, SINK = len(NAMES), len(NAMES) + 1          # two extra nodes after the named ones
LABEL = NAMES + ["source", "sink"]


def deliverable(closed=()):
    smf = max_flow.SimpleMaxFlow()
    for depot, shelf in SUPPLY.items():
        smf.add_arc_with_capacity(SOURCE, NODE[depot], shelf)
    for (i, j), (_, cap) in ARCS.items():
        smf.add_arc_with_capacity(NODE[i], NODE[j], 0 if (i, j) in closed else cap)
    for region, need in DEMAND.items():
        smf.add_arc_with_capacity(NODE[region], SINK, need)
    if smf.solve(SOURCE, SINK) != smf.OPTIMAL:
        raise SystemExit("max flow failed")
    cut = set(smf.get_source_side_min_cut())
    crossing = [f"{LABEL[smf.tail(a)]}->{LABEL[smf.head(a)]} ({smf.capacity(a)})"
                for a in range(smf.num_arcs())
                if smf.tail(a) in cut and smf.head(a) not in cut and smf.capacity(a) > 0]
    return smf.optimal_flow(), crossing


print(f"demand {sum(DEMAND.values())}, on the shelves {sum(SUPPLY.values())}")
for closed in ((), (("Northgate", "Central"),)):
    flow, crossing = deliverable(closed)
    print(f"closed: {', '.join(f'{i}->{j}' for i, j in closed) or 'none'}: at most {flow} spares delivered")
    print(f"  a minimum cut: {' + '.join(crossing)}")
