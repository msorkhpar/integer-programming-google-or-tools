"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from district import least_overspend

schools = {
    "lab-E": {2030: 350},
    "hall-F": {2030: 150, 2031: 300},
    "pool-G": {2031: 600},
}

print("overspend, lab+hall, budget 2030=600:", least_overspend(schools, {2030: 600}, {"lab-E", "hall-F"}))
print("overspend, lab+hall, budget 2030=400:", least_overspend(schools, {2030: 400}, {"lab-E", "hall-F"}))
print("overspend, all three, budgets 700/700:",
      least_overspend(schools, {2030: 700, 2031: 700}, {"lab-E", "hall-F", "pool-G"}))
