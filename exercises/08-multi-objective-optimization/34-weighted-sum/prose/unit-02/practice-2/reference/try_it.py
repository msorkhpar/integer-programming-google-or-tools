"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from parks import Project, plans, unreachable

garden = [Project("hedges", 4, 1, 7), Project("fountain", 4, 5, 5), Project("arbor", 5, 7, 1),
          Project("benches", 3, 2, 2)]

print("plans within 9:", {"+".join(sorted(p)) or "none": v for p, v in plans(garden, 9).items()})
print("unreachable within 9:", unreachable(garden, 9))
print("unreachable within 5:", unreachable(garden, 5))
