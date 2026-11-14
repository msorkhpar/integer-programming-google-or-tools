"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from sweep import steps

sweep = [(6, 594, 31), (0, 600, 25), (3, 597, 25), (12, 590, 40), (20, 590, 40)]

for allowed, taken, gain in steps(600, sweep):
    print(f"allowed {allowed}: taken {taken}, gain {gain}")
