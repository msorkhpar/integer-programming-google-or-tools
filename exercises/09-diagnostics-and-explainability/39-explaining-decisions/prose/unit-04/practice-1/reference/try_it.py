"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fleet_finance import finance_text

run = {"budget": {2031: 8000, 2030: 9500}, "spend": {2030: 9100.4, 2031: 8350},
       "npv": 21780.6, "bound": 21780.6, "status": "OPTIMAL"}

print("optimal run:", finance_text(run))
print("feasible run, bound 22010.3:", finance_text({**run, "npv": 21400.0, "bound": 22010.3, "status": "FEASIBLE"}))
