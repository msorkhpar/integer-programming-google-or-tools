"""Optional low-priority inspections: which sites the routing model drops, and how the penalty decides.

Adapted onto GridCap from the OR-Tools example vrp_drop_nodes.py,
https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_drop_nodes.py
The drive times are fictional (valley.py invents the map from a seed).
"""

from valley import drive_minutes, sites
from valley_model import build, dropped, parameters, show

places = sites()
print(f"all arcs of the drive matrix add up to {sum(map(sum, drive_minutes(places)))} minutes")
print("low-priority sites (cof $k):", ", ".join(f"{s.name} {s.cof}" for s in places[1:] if not s.urgent))

policies = [
    ("two crews, penalty 10000 each", 2, lambda site: 10_000),
    ("two crews, penalty cof // 10", 2, lambda site: site.cof // 10),
    ("three crews, penalty 10000 each", 3, lambda site: 10_000),
    ("three crews, penalty cof // 100", 3, lambda site: site.cof // 100),
]
for label, crews, penalty in policies:
    manager, routing = build(places, crews=crews, kits_per_truck=12, penalty=penalty)
    solution = routing.SolveWithParameters(parameters())
    skipped = dropped(manager, routing, solution)
    paid = sum(penalty(places[n]) for n in skipped)
    print(f"{label}: objective {solution.ObjectiveValue()} = drive {solution.ObjectiveValue() - paid}"
          f" + penalties {paid}")
    print(f"  dropped {len(skipped)}: {', '.join(places[n].name for n in skipped) or 'none'}")
    show(places, manager, routing, solution)
