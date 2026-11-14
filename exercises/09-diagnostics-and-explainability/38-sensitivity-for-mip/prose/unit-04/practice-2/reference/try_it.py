"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from extra import what_extra_buys

curve = [(50, 20), (80, 35), (95, 41), (140, 60)]

print("from 60 with 30 more:", what_extra_buys(curve, 60, 30))
print("from 80 with 10 more:", what_extra_buys(curve, 80, 10))
print("from 150 with 20 more:", what_extra_buys(curve, 150, 20))
print("from 40 with 20 more:", what_extra_buys(curve, 40, 20))
