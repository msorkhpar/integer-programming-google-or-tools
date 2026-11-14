"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from split import Terminal, split

def r(v):
    return v if v is None else round(v, 2)


yard = [Terminal("west", 1.5, 3, 300), Terminal("pier", 1.1, 1, 250), Terminal("quay", 0.6, 2, 500)]

for budget in (400, 150):
    status, value, amounts, full = split(yard, budget)
    print(f"budget {budget}:", status, r(value), amounts and {k: r(v) for k, v in amounts.items()})
    print(f"full rows at budget {budget}:", full and sorted(full))
floors = [Terminal("west", 1.5, 3, 300, 90), Terminal("pier", 1.1, 1, 250, 90)]
print("floors 90 + 90 at budget 150:", split(floors, 150))
