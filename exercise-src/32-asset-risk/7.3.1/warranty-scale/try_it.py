"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from warranty import required_scale

for share in (0.15, 0.05, 0.01):
    print(f"4-year warranty, at most {share} failing, beta 3:", round(required_scale(4, share, 3.0), 3))
print("4-year warranty, at most 0.05 failing, beta 1:", round(required_scale(4, 0.05, 1.0), 3))
