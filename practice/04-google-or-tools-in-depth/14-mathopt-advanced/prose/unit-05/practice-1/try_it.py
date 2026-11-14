"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from tracker import make_tracker

# Three parcels, maximize their value.
model = mathopt.Model(name="parcels")
p = [model.add_binary_variable(name=f"parcel{i}") for i in range(3)]
callback, history = make_tracker({p[0]: 6.0, p[1]: 4.0, p[2]: 9.0}, maximize=True)

for solution in ({p[0]: 1.0}, {p[0]: 1.0, p[1]: 1.0}, {p[1]: 1.0}, {p[2]: 1.0, p[1]: 1.0}):
    result = callback(mathopt.CallbackData(event=mathopt.Event.MIP_SOLUTION, solution=solution))
    print("history after", sorted(v.name for v in solution), "->", history, "terminate", result and result.terminate)

low_callback, low_history = make_tracker({p[0]: 6.0, p[1]: 4.0}, maximize=False)
for solution in ({p[0]: 1.0, p[1]: 1.0}, {p[1]: 1.0}, {p[0]: 1.0}):
    low_callback(mathopt.CallbackData(event=mathopt.Event.MIP_SOLUTION, solution=solution))
print("history when minimizing:", low_history)
