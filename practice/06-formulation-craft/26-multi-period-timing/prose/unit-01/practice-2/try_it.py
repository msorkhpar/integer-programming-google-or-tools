"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from starts import Project, ScheduleError, deferrals, read_starts

mains = [Project("R1", (2030, 2031)), Project("R2", (2030, 2031, 2032)), Project("R3", (2031,))]

values = {("R1", 2030): 0.0, ("R1", 2031): 0.9999998,
          ("R2", 2030): 0.0, ("R2", 2031): 0.0, ("R2", 2032): 1.0,
          ("R3", 2031): 2e-8}
starts = read_starts(values, mains)
print("start years:", starts)
print("deferrals:", deferrals(starts, mains))

half = dict(values)
half["R3", 2031] = 0.5
try:
    print("with R3 at 0.5:", read_starts(half, mains))
except ScheduleError as err:
    print("with R3 at 0.5: ScheduleError", err)
