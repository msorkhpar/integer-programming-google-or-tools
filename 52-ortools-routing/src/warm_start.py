"""Start the search from yesterday's routes, and fall back to a fresh solve when they no longer fit.

Adapted onto GridCap from the OR-Tools example vrp_initial_routes.py,
https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_initial_routes.py
The drive times are fictional (valley.py invents the map from a seed).
"""

from dataclasses import replace

from valley import sites
from valley_model import build, parameters, routes

YESTERDAY = [["A064", "A106", "A302", "A281", "A308"], ["A087", "A230"],
             ["A344", "A133", "A378", "A157", "A149", "A183"], ["A348", "A136", "A096", "A091", "A305"]]


def plan_today(places):
    node = {s.name: n for n, s in enumerate(places)}
    manager, routing = build(places, crews=4, kits_per_truck=9)
    search = parameters("PATH_CHEAPEST_ARC", "GUIDED_LOCAL_SEARCH", 100)
    # Close the model with these parameters first; reading routes would otherwise close it with defaults.
    routing.CloseModelWithParameters(search)
    initial = routing.ReadAssignmentFromRoutes([[node[name] for name in crew] for crew in YESTERDAY], True)
    if initial is None:
        print("  yesterday's routes break a rule today: solving from scratch")
        solution = routing.SolveWithParameters(search)
    else:
        print(f"  yesterday's routes still fit: cost {initial.ObjectiveValue()}")
        solution = routing.SolveFromAssignmentWithParameters(initial, search)
    print(f"  after 100 solutions of guided local search: cost {solution.ObjectiveValue()}")
    for crew, nodes in enumerate(routes(manager, routing, solution)):
        print(f"    crew {crew}: {' > '.join(places[n].name for n in nodes)}")


places = sites()
print("today, same sites and windows as yesterday:")
plan_today(places)
print("today, A305's window now closes at 13:00 (yesterday it was reached at 15:00):")
plan_today([replace(s, window=(0, 300)) if s.name == "A305" else s for s in places])
