"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from dual import solve_dual

# A garage's week: hours of servicing, tyre work and valeting, value per hour.
value = {"service": 5, "tyres": 3, "valet": 1}
rows = {
    "hours": ({"service": 1, "tyres": 1, "valet": 1}, "<=", 12),
    "lifts": ({"service": 1}, "<=", 4),
}
print("dual of hours + lifts:", solve_dual(value, rows))
rows["min_valet"] = ({"valet": 1}, ">=", 2)
print("dual with valet at least 2:", solve_dual(value, rows))
