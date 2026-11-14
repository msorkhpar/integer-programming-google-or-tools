"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from inspection import separate_floor

km = {"North": 14, "East": 4, "West": 3, "South": 2}

print("floor 10, North at 0.3:", separate_floor(km, 10, {"North": 0.3, "East": 0.8, "West": 0.9, "South": 1.0}))
print("floor 10, whole plan North+South:", separate_floor(km, 10, {"North": 1.0, "East": 0.0, "West": 0.0, "South": 1.0}))
print("floor 9, North at 0.5:", separate_floor(km, 9, {"North": 0.5, "East": 1.0, "West": 1.0, "South": 1.0}))
