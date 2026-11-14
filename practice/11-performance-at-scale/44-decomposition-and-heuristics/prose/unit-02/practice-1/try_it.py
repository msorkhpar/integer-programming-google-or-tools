"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from pump_cut import pumping_cut

stations = {
    "ridge": {"capacity": 50, "energy": 2.2, "refill": 4},
    "pond": {"capacity": 90, "energy": 1.2, "refill": 6},
}
master = mathopt.Model(name="stations")
x = {j: master.add_binary_variable(name=j) for j in stations}

for plan in ({"ridge": 0, "pond": 0}, {"ridge": 1, "pond": 0}, {"ridge": 1, "pond": 1}):
    cost, cut = pumping_cut(stations, 120, 400, 5.0, plan, x)
    print(f"plan {plan}: pumping cost {round(cost, 2)}, cut {cut}")
