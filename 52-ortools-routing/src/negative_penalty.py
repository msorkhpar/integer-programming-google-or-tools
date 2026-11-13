"""Lesson 4.8.4: a disjunction with a negative penalty forces its visit.

The two-crew Valley day of valley_drops.py, with a penalty of 10000 per routine site, solved twice:
as there, and with A183's penalty set to -1. The drive times are fictional.
"""

from valley import sites
from valley_model import build, dropped, parameters, show

places = sites()
for label, a183 in (("A183 penalty 10000", 10_000), ("A183 penalty -1", -1)):
    penalty = lambda site: a183 if site.name == "A183" else 10_000
    manager, routing = build(places, crews=2, kits_per_truck=12, penalty=penalty)
    solution = routing.SolveWithParameters(parameters())
    skipped = dropped(manager, routing, solution)
    print(f"{label}: objective {solution.ObjectiveValue()}, dropped {len(skipped)}: "
          f"{', '.join(places[n].name for n in skipped)}")
    show(places, manager, routing, solution)
