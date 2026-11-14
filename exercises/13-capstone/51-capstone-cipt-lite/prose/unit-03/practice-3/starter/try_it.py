"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from value import ranking, value_table, weights

measures = {
    "npv": {("K1", 2031): 200, ("K2", 2031): 450, ("K2", 2032): 400, ("K3", 2032): 50},
    "risk": {("K1", 2031): 150.0, ("K2", 2031): 20.0, ("K2", 2032): 18.0, ("K3", 2032): 60.0},
    "minutes": {("K1", 2031): 10_000, ("K2", 2031): 0, ("K2", 2032): 0, ("K3", 2032): 70_000},
}

print("weights for ratings 100/50/50:", weights({"risk": 100, "minutes": 50, "npv": 50}))
table = value_table(measures)
print("values:", table)
print("ranking:", ranking(table))
