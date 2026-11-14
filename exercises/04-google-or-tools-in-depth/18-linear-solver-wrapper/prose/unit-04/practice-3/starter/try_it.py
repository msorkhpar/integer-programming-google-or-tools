"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from packing import fewest_crews

# Job lengths in months, packed into seasons of a given length.
print("jobs [4, 4, 3, 3, 2], season 8:", fewest_crews([4, 4, 3, 3, 2], 8))
print("jobs [5, 5, 5], season 9:", fewest_crews([5, 5, 5], 9))
print("jobs [2, 3, 4], season 10:", fewest_crews([2, 3, 4], 10))
print("jobs [3, 11], season 10:", fewest_crews([3, 11], 10))
