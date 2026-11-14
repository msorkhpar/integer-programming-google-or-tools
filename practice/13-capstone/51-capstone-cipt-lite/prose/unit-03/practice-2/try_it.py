"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from risk import risk_table, scale_from_rul

snapshot = {"years": [2031, 2032], "rate": 0.04,
            "projects": {"C1": {"cost": [70], "earliest": 2031, "latest": 2032},
                         "C2": {"cost": [40, 40], "earliest": 2031, "latest": 2031}}}
assets = {"C1": {"age": 28, "beta": 2.5, "rul": 10, "eta": 50.0, "cof": 600, "keep": 0.0},
          "C2": {"age": 15, "beta": 1.8, "rul": 18, "eta": 35.0, "cof": 250, "keep": 0.4}}

print("scale for age 28, rul 10, beta 2.5:", round(scale_from_rul(28, 10, 2.5), 3))
table = risk_table(snapshot, assets, window=5)
print("starts in the table:", len(table))
for key, value in table.items():
    print("risk removed, window 5,", key, ":", value)
