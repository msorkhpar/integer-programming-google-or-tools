"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from first_limit import where_it_stops

# Progress of one bus-routing run, oldest first.
trace = [
    {"seconds": 0.3, "nodes": 0, "solutions": 0, "incumbent": None, "bound": 520.0},
    {"seconds": 1.5, "nodes": 10, "solutions": 1, "incumbent": 400.0, "bound": 500.0},
    {"seconds": 6.0, "nodes": 300, "solutions": 2, "incumbent": 470.0, "bound": 490.0},
    {"seconds": 20.0, "nodes": 1500, "solutions": 5, "incumbent": 480.0, "bound": 484.0},
]

print("relative_gap 0.02, seconds 10:", where_it_stops(trace, {"relative_gap": 0.02, "seconds": 10}))
print("absolute_gap 30:", where_it_stops(trace, {"absolute_gap": 30}))
print("solutions 2, nodes 200:", where_it_stops(trace, {"solutions": 2, "nodes": 200}))
print("nodes 9000:", where_it_stops(trace, {"nodes": 9000}))
