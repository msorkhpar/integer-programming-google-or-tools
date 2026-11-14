"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pairing import pair

# Rows are crews, columns are depots; None means the crew is not cleared there.
print("three crews, all cleared:", pair([[5, 1, 8], [2, 6, 3], [4, 9, 7]]))
print("three crews, two refusals:", pair([[5, None, 8], [2, 6, None], [4, 9, 7]]))
print("two crews cleared for one depot only:", pair([[3, None], [4, None]]))
