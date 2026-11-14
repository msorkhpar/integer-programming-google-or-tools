"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from next_node import next_node

# Waiting nodes as (id, depth, bound).
waiting = [(2, 1, 515.0), (7, 3, 498.5), (5, 2, 515.0), (8, 3, 470.0)]
for rule in ("depth", "best", "breadth"):
    print(f"rule {rule}:", next_node(waiting, rule))
