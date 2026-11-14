"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from guards import plan_nights

# Places 0 and 1 are gates, place 2 is the rest room; cost[p][q] is a move from p to q.
cost = [[0, 4, 2], [4, 0, 2], [2, 2, 0]]
need = [{0: 1, 1: 1}, {0: 2}, {1: 1}]
total, at = plan_nights(["cleo", "dev", "eli"], need, cost, [])
print("moving cost, no forbidden moves:", total)
print("places:", at)
total, at = plan_nights(["cleo", "dev", "eli"], need, cost, [(2, 0)])
print("moving cost, 2 -> 0 forbidden:", total)
