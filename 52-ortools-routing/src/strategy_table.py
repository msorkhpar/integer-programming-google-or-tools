"""First-solution strategies, then local search: the four-crew Valley day (lesson 4.8.3's model).

Every run is stopped by a solution limit or by reaching a local minimum, never by a clock, so
every number below is the same on every machine and every run. The drive times are fictional.
"""

from ortools.constraint_solver import routing_enums_pb2

from valley import sites
from valley_model import build, parameters, routes

places = sites()
STRATEGIES = ["PATH_CHEAPEST_ARC", "PATH_MOST_CONSTRAINED_ARC", "SAVINGS", "CHRISTOFIDES",
              "PARALLEL_CHEAPEST_INSERTION", "LOCAL_CHEAPEST_INSERTION", "GLOBAL_CHEAPEST_ARC",
              "LOCAL_CHEAPEST_ARC", "FIRST_UNBOUND_MIN_VALUE", "BEST_INSERTION", "ALL_UNPERFORMED"]
STAGES = [("first solution", None, 1),                  # stop at the first solution found
          ("greedy descent", "GREEDY_DESCENT", None),   # improve until no move helps
          ("guided local search", "GUIDED_LOCAL_SEARCH", 300)]   # keep going for 300 solutions


def run(strategy: str, metaheuristic: str | None, limit: int | None):
    manager, routing = build(places, crews=4, kits_per_truck=9)
    solution = routing.SolveWithParameters(parameters(strategy, metaheuristic, limit))
    status = routing_enums_pb2.RoutingSearchStatus.Value.Name(routing.status())
    return (solution.ObjectiveValue() if solution else None), status, solution and routes(manager, routing, solution)


print(f"{'first-solution strategy':28}" + "".join(f"{label:>22}" for label, _, _ in STAGES))
statuses = set()
for strategy in STRATEGIES:
    cells = []
    for _, metaheuristic, limit in STAGES:
        cost, status, _ = run(strategy, metaheuristic, limit)
        statuses.add((metaheuristic, limit, status))
        cells.append(f"{cost if cost is not None else status:>22}")
    print(f"{strategy:28}" + "".join(cells))

print("statuses seen, by stage:")
for label, metaheuristic, limit in STAGES:
    print(f"  {label}: {sorted({s for m, l, s in statuses if (m, l) == (metaheuristic, limit)})}")

first = run("PATH_CHEAPEST_ARC", "GUIDED_LOCAL_SEARCH", 300)
again = run("PATH_CHEAPEST_ARC", "GUIDED_LOCAL_SEARCH", 300)
print(f"two runs of PATH_CHEAPEST_ARC + guided local search, 300 solutions: costs {first[0]} and {again[0]}, "
      f"same routes: {first[2] == again[2]}")
