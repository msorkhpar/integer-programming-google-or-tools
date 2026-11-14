"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from gap import Project, integrality_gap

# Three depot refits, then a pair where R2 needs R1.
depots = [Project("D1", 70, 84), Project("D2", 45, 50), Project("D3", 35, 35)]
linked = [Project("R1", 40, 30), Project("R2", 30, 54, parent="R1"), Project("R3", 50, 45)]

for name, projects in (("depots", depots), ("linked", linked)):
    bound, best, gap = integrality_gap(projects, 100)
    print(f"{name} at budget 100: LP bound", round(bound, 3), "best plan", round(best, 3), "gap", round(gap, 4))
