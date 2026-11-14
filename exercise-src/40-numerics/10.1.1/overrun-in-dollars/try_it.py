"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from allowance import allowed_overrun

row = 5_400_000       # a capital row of $5.4M

print("absolute 1e-6, row in $k:", round(allowed_overrun(row, 1_000, 1e-6, relative=False), 6))
print("absolute 1e-6, row in $M:", round(allowed_overrun(row, 1_000_000, 1e-6, relative=False), 6))
print("relative 1e-6, row in $k:", round(allowed_overrun(row, 1_000, 1e-6, relative=True), 6))
print("relative 1e-6, row of $250 in $k:", round(allowed_overrun(250, 1_000, 1e-6, relative=True), 6))
