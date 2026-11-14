"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from feeders import generate_feeders

for feeder in generate_feeders(3, seed=99):
    print("seed 99:", feeder)
print("seed 99 again, same three:", generate_feeders(3, seed=99) == generate_feeders(3, seed=99))
print("first three of 50 match:", generate_feeders(50, seed=99)[:3] == generate_feeders(3, seed=99))
print("seed 100, one feeder:", generate_feeders(1, seed=100))
