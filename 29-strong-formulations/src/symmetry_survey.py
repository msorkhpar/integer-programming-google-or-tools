"""The same comparison on 12 crew splits: four regions, three, four or five crews."""

from gridcap import REGIONS, generate
from crew_split import build, region_jobs, solve

medium = generate("medium")
setups = [(order, detect) for order in (None, "load", "index") for detect in (False, True)]
nodes = {s: [] for s in setups}
spans = set()
for region in REGIONS:
    jobs = region_jobs(medium, region)
    for crews in (3, 4, 5):
        found = []
        for order, detect in setups:
            result = solve(build(jobs, crews, order), detect)
            nodes[order, detect].append(result.solve_stats.node_count)
            found.append(round(result.objective_value()))
        spans.add(len(set(found)))
print(f"12 instances; every setup found the same makespan on each: {spans == {1}}")
base = nodes[None, False]
print("order rows   detection  total nodes  fewer than plain  more than plain")
for order, detect in setups:
    counts = nodes[order, detect]
    fewer = sum(c < b for c, b in zip(counts, base))
    more = sum(c > b for c, b in zip(counts, base))
    print(f"{str(order):11}  {'on' if detect else 'off':9}  {sum(counts):11,}  {fewer:16}  {more:15}")
