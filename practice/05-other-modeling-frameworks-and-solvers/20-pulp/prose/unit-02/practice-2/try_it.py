"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from meters import Site, port_solve

# Site(id, district, benefit $k, cost $k, crew-weeks); an extra crew costs 40 and adds 10 weeks.
village = [
    Site("R1", "river", 60, 35, 7),
    Site("R2", "river", 25, 15, 3),
    Site("H1", "hill", 40, 30, 5),
    Site("H2", "hill", 30, 20, 6),
]
print("budget 90, 20 crew-weeks:", port_solve(village, budget=90, crew_weeks=20))
print("budget 90, 8 crew-weeks:", port_solve(village, budget=90, crew_weeks=8))
print("budget 30, 20 crew-weeks:", port_solve(village, budget=30, crew_weeks=20))
