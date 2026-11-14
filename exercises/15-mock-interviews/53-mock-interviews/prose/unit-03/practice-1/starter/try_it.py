"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from values import start_year_npv, yearly_pof

print("pof at age 0, beta 2, eta 20:", round(yearly_pof(0, 2.0, 20.0), 5))
print("pof at age 25, beta 2, eta 20:", round(yearly_pof(25, 2.0, 20.0), 5))
print("pof at age 25, beta 1, eta 20:", round(yearly_pof(25, 1.0, 20.0), 5))

flows = [-200, 80, 80, 80]
print("flows -200/80/80/80 started 2031, no escalation, rate 0.06, valued 2031:",
      round(start_year_npv(flows, 2031, 2031, 0.0, 0.06, 2031), 3))
print("same, started 2033, valued 2031:", round(start_year_npv(flows, 2033, 2031, 0.0, 0.06, 2031), 3))
print("same, started 2033, prices from 2030 escalating 0.03:",
      round(start_year_npv(flows, 2033, 2030, 0.03, 0.06, 2031), 3))
