"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from blend import Pit, mix

def r(v):
    return v if v is None else round(v, 2)


quarries = [Pit("North", 14, 3, 400), Pit("Mill", 10, 8, 500), Pit("River", 6, 15, 300)]

status, cost, tons = mix(quarries, 600, 5, 9)
print("600 tons, fines 5..9:", status, r(cost), tons and {k: r(v) for k, v in tons.items()})
status, cost, tons = mix(quarries, 800, 7, 12)
print("800 tons, fines 7..12:", status, r(cost), tons and {k: r(v) for k, v in tons.items()})
print("600 tons, fines 1..2:", mix(quarries, 600, 1, 2))
