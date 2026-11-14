"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fill import Project, round_down_and_fill

# Five sewer works; S1 is ordered by the regulator, S5 needs S4, S2 and S3 are alternatives.
sewers = [
    Project("S1", 40, 48, must_do=True),
    Project("S2", 30, 45, group="outfall"),
    Project("S3", 25, 35, group="outfall"),
    Project("S4", 20, 18),
    Project("S5", 10, 16, parent="S4"),
]
shares = {"S1": 1.0, "S2": 1.0, "S3": 0.0, "S4": 0.5, "S5": 0.5}
print("LP shares at budget 90:", shares)
print("plan at budget 90:", sorted(round_down_and_fill(shares, sewers, 90)))
print("plan at budget 120:", sorted(round_down_and_fill(shares, sewers, 120)))
