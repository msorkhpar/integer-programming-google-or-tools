"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rows import Project, rows_for

years = [2030, 2031, 2032, 2033]
projects = [Project("T1", "transformers", 2030, 2031, 2),
            Project("T2", "transformers", 2032, 2033, 1, parent="T1", lag=1),
            Project("B1", "breakers", 2031, 2031, 1, must_do=True),
            Project("C1", "cables", 2033, 2033, 1, alt_group="K"),
            Project("C2", "cables", 2033, 2033, 1, alt_group="K")]

for pid in ("T1", "T2", "B1", "C2"):
    print(f"rows of {pid}:", sorted(rows_for(pid, projects, years)))
