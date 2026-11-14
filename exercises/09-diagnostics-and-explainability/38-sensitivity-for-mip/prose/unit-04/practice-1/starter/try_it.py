"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from forecast import forecast_and_gain


def show(label, answer):
    print(label, {k: round(v, 3) for k, v in answer.items()})


show("costs [3, 5] values [9, 5], budget 2, extra 3:", forecast_and_gain([3, 5], [9, 5], 2, 3))
show("costs [4, 4] values [4, 4], budget 5, extra 2:", forecast_and_gain([4, 4], [4, 4], 5, 2))
show("costs [1, 1] values [2, 2], budget 1, extra 1:", forecast_and_gain([1, 1], [2, 2], 1, 1))
