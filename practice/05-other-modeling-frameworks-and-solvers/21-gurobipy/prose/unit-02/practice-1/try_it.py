"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pricing import reduced_costs, wrong_signs

# A bakery: loaves, cakes, pies; rows: oven hours, mixer hours.
c = [2.0, 6.0, 3.0]
A = [[1.0, 2.0, 1.0],
     [0.5, 2.0, 2.0]]
pi = [1.0, 1.0]
rc = reduced_costs(c, A, pi)
print("reduced costs at prices [1, 1]:", [round(r, 3) for r in rc])
print("wrong signs, all basic, maximize:", wrong_signs(rc, ["basic", "basic", "basic"], maximize=True))
print("wrong signs, lower/upper/basic, maximize:", wrong_signs(rc, ["lower", "upper", "basic"], maximize=True))
print("wrong signs, lower/upper/basic, minimize:", wrong_signs(rc, ["lower", "upper", "basic"], maximize=False))
