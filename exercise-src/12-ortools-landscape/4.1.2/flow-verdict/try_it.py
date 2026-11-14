"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from shipping import ship

# Node 0 is a warehouse, node 3 a store; nodes 1 and 2 are cross-docks.
lanes = [(0, 1, 6, 2), (0, 2, 4, 1), (1, 3, 6, 1), (2, 3, 4, 3)]

print("send 5 pallets 0 -> 3:", ship(lanes, {0: 5, 3: -5}))
print("send 10 pallets 0 -> 3:", ship(lanes, {0: 10, 3: -10}))
print("send 12 pallets 0 -> 3:", ship(lanes, {0: 12, 3: -12}))
print("send 5, receive 4:", ship(lanes, {0: 5, 3: -4}))
