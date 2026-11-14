"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from outages import Outage, violations

sound = [Outage("U1", "Birch", 20, 2, 1), Outage("U2", "Birch", 22, 3, 2), Outage("U3", "Cedar", 21, 2, 2)]
print("three outages, 3 crews a week:", violations(sound, crews_per_week=3))

broken = [Outage("U1", "Birch", 20, 4, 2), Outage("U2", "Birch", 22, 1, 1),
          Outage("U2", "Cedar", 50, 4, 1)]
for line in violations(broken, crews_per_week=2):
    print("broken plan, 2 crews a week:", line)
