"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from coefficients import Main, coefficients

main = Main(40, 3.0, 50.0, 1_000.0)
starts = [2030, 2031, 2032]

flat = coefficients(main, starts, 2030, 1, 0.0, 5, 0.0)
print("replace, 5 service years, 0%:", {s: round(v, 2) for s, v in flat.items()})
disc = coefficients(main, starts, 2030, 1, 0.0, 5, 0.05)
print("replace, 5 service years, 5%:", {s: round(v, 2) for s, v in disc.items()})
half = coefficients(main, starts, 2030, 1, 0.5, 5, 0.05)
print("keep half the age, 5 service years, 5%:", {s: round(v, 2) for s, v in half.items()})
