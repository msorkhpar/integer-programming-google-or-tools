"""A soft finish time: crews should be back by 14:30, and each minute later costs 5 drive-minutes.

The drive times are fictional (valley.py invents the map from a seed).
"""

from valley import clock, sites
from valley_model import build, parameters, show

places = sites()
FINISH_BY, LATE_COST = 390, 5          # 14:30 is 390 minutes after 08:00

for label, extra in (("no finish time", {}), ("soft finish 14:30", {"finish_by": FINISH_BY, "late_cost": LATE_COST})):
    manager, routing = build(places, crews=4, kits_per_truck=9, **extra)
    solution = routing.SolveWithParameters(parameters())
    time_dim = routing.GetDimensionOrDie("Time")
    late = sum(max(0, solution.Min(time_dim.CumulVar(routing.End(c))) - FINISH_BY) for c in range(4))
    print(f"{label}: objective {solution.ObjectiveValue()}, minutes after {clock(FINISH_BY)}: {late}")
    show(places, manager, routing, solution)
