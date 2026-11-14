"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from true_gap import true_gap


def show(label, got):
    print(label, {key: round(value, 6) for key, value in got.items()})


show("incumbent 3_150_000, bound 3_150_600, constant 3_000_000:", true_gap(3_150_000, 3_150_600, 3_000_000))
show("incumbent 8_000, bound 8_120, constant 0:", true_gap(8_000, 8_120, 0))
show("min, incumbent 61_000, bound 60_400, constant 60_000:", true_gap(61_000, 60_400, 60_000))
show("incumbent 900, bound 950, constant -100:", true_gap(900, 950, -100))
