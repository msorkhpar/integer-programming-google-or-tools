"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from togap import work_to_gap

# (work units, incumbent, bound) rows from a solver's progress log.
maximize_log = [(12, 4000.0, 4600.0), (30, 4400.0, 4600.0), (75, 4550.0, 4580.0), (140, 4570.0, 4575.0)]
minimize_log = [(5, 820.0, 600.0), (20, 660.0, 610.0), (55, 630.0, 618.0)]
print("maximize log, target 0.05:", work_to_gap(maximize_log, 0.05))
print("maximize log, target 0.005:", work_to_gap(maximize_log, 0.005))
print("maximize log, target 0.0001:", work_to_gap(maximize_log, 0.0001))
print("minimize log, target 0.02:", work_to_gap(minimize_log, 0.02))
