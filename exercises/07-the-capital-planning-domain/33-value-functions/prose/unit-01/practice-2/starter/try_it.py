"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from mains import Main, benefit


def rounded(result):
    return {k: round(v, 3) for k, v in result.items()}


birch = Main("Birch Rd", 30, 2.0, 20.0, 80, 4.0)

print("replace, start 2031, done at once:", rounded(benefit(birch, 1.0, 2031, 0, 2031, 8)))
print("reline half, start 2031, done at once:", rounded(benefit(birch, 0.5, 2031, 0, 2031, 8)))
print("replace, start 2033, two years of work:", rounded(benefit(birch, 1.0, 2033, 2, 2031, 8)))
print("replace, start 2037, two years of work:", rounded(benefit(birch, 1.0, 2037, 2, 2031, 8)))
