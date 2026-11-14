"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from optimum_range import optimum_range

print("no incumbent, waiting [240.5, 233]:", optimum_range(None, [240.5, 233.0]))
print("incumbent 228, waiting [240.5, 233]:", optimum_range(228.0, [240.5, 233.0]))
print("incumbent 236, waiting [233]:", optimum_range(236.0, [233.0]))
print("incumbent 236, nothing waiting:", optimum_range(236.0, []))
