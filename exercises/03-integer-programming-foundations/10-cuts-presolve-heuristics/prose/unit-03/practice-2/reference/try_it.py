"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from dive import dive

# A pretend LP: it knows the points for a few sets of fixings.
answers = {
    (): {"s1": 0.7, "s2": 0.2, "s3": 1},
    (("s2", 0),): {"s1": 0.95, "s2": 0, "s3": 1},
    (("s1", 1), ("s2", 0)): {"s1": 1, "s2": 0, "s3": 1},
}


def lp(fixed):
    return answers.get(tuple(sorted(fixed.items())))


print("dive over s1, s2, s3:", dive(lp))
print("dive when the first LP is 0-1:", dive(lambda fixed: {"t1": 1, "t2": 0}))
