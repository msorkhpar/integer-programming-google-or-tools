"""Ridge's crew split with and without symmetry-breaking rows, with HiGHS's symmetry detection on and off."""

from gridcap import generate
from crew_split import build, region_jobs, solve

jobs = region_jobs(generate("medium"), "Ridge")
print("order rows   detection  makespan  nodes")
for order in (None, "load", "index"):
    for detect in (False, True):
        cs = build(jobs, crews=4, order=order)
        result = solve(cs, detect)
        print(f"{str(order):11}  {'on' if detect else 'off':9}  {result.objective_value():8.0f}  "
              f"{result.solve_stats.node_count:5}")

# The same plain model, built and solved twice more: does HiGHS repeat its node count?
again = [solve(build(jobs, crews=4, order=None), False).solve_stats.node_count for _ in range(2)]
print("plain model, detection off, two more identical runs: nodes", ", ".join(str(n) for n in again))
