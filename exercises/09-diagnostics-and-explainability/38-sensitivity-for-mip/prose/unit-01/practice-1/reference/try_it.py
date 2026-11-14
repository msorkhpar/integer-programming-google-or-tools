"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from lots import value_function

print("z, days [2, 3] worth [3, 5] limits [2, 1], up to 9:", value_function([2, 3], [3, 5], [2, 1], 9))
print("z, days [4] worth [7] limit [3], up to 13:", value_function([4], [7], [3], 13))
