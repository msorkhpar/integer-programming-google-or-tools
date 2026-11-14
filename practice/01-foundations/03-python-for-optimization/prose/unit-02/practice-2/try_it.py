"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from links import Project, link_problems

works = [
    Project("H1", group="pump"),
    Project("H2", parent="H1", group="pump"),
    Project("H3", parent="H3"),
    Project("H4", parent="H9"),
    Project("H5", group="pump"),
    Project("H5"),
]
print("problems:", link_problems(works))
print("problems for H1 and child H6:", link_problems(works[:1] + [Project("H6", parent="H1")]))
