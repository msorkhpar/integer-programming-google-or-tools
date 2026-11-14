"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from check import accept

values = [6.0, 10.0, 7.0, 4.0, 9.0]
hours = [[3, 0], [2, 4], [0, 3], [1, 1], [4, 2]]
capacity = [6.0, 6.0]
requires = [(0, 3)]


def check(x, reported, bounds, gap=1e-3):
    return accept(x, reported, bounds, values, hours, capacity, requires, gap)


print("x 1,1,0,1,0 reported 20, bound 20:", check([1, 1, 0, 1, 0], 20.0, [20.0]))
print("x 1,1,0,1,0 reported 25, bounds 20 and 22:", check([1, 1, 0, 1, 0], 25.0, [22.0, 20.0]))
print("x 0,1,0,1,0 reported 14, bound 20:", check([0, 1, 0, 1, 0], 14.0, [20.0]))
print("x 0,1,1,0,1 reported 26, bound 26:", check([0, 1, 1, 0, 1], 26.0, [26.0]))
print("x 1,0.5,0,0,0 reported 11, bound 20:", check([1, 0.5, 0, 0, 0], 11.0, [20.0]))
print("x 0,1,0,0,0 reported 10, bound 20, gap 0.6:", check([0, 1, 0, 0, 0], 10.0, [20.0], gap=0.6))
