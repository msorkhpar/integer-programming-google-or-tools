"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from epsilon import max_epsilon

print("main {4, 8, 12}, bonus {1, 0, 0}:", round(max_epsilon({"A": 4, "B": 8, "C": 12}, {"A": 1.0, "B": 0.0, "C": 0.0}), 4))
print("main {9, 6}, bonus {2, 2}:", round(max_epsilon({"A": 9, "B": 6}, {"A": 2.0, "B": 2.0}), 4))
print("main {7, 5}, bonus {0.5, 0.5}:", round(max_epsilon({"A": 7, "B": 5}, {"A": 0.5, "B": 0.5}), 4))
