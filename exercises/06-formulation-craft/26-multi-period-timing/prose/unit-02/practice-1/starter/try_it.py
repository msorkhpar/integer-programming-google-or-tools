"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from regional import Project, spend_by_region_year, start_variables

# Sewer works in two districts: id, district, spend per year of work, allowed start years.
years = [2031, 2032, 2033]
works = [
    Project("S1", "East", (70, 30), (2031, 2032)),
    Project("S2", "East", (40,), (2031, 2032, 2033)),
    Project("S3", "West", (25, 100, 10), (2031,)),
]
schedule = {"S1": 2032, "S2": 2032, "S3": 2031}

model = mathopt.Model()
x = start_variables(model, works)
spend = spend_by_region_year(works, x, years)
values = {var: 1.0 if schedule.get(pid) == t else 0.0 for (pid, t), var in x.items()}
for (region, year), expr in sorted(spend.items()):
    print(f"{region} {year}:", round(mathopt.evaluate_expression(expr, values), 2))
