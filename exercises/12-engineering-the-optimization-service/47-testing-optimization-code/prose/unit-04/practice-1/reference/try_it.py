"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from run_bytes import canonical, repeats

first = {"started_at": "2031-05-04T07:15:00", "stats": {"wall_seconds": 0.8, "nodes": 22}, "cost": 377.25,
         "routes": {"van1": ["hub", "p", "q", "hub"], "van2": ["hub", "r", "hub"]}, "unserved": {"s", "t"}}
again = {**first, "started_at": "2031-05-05T18:40:00", "stats": {"wall_seconds": 2.1, "nodes": 22},
         "cost": 377.2500000003, "unserved": {"t", "s"}}
swapped = {**first, "routes": {**first["routes"], "van1": ["hub", "q", "p", "hub"]}}

print("canonical bytes:", canonical(first))
print("next day, other clock:", repeats([first, again]))
print("van1 visits q before p:", repeats([first, swapped]))
