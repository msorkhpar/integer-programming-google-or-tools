"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from refusal import refusal

S = mathopt.SolverType

# Two cold stores, one yes/no each.
model = mathopt.Model(name="stores")
a, b = model.add_binary_variable(name="store_a"), model.add_binary_variable(name="store_b")
model.add_linear_constraint(a + b >= 1, name="cover")
model.minimize(5 * a + 2 * b)


def caught(call):
    try:
        call()
    except Exception as error:
        return error
    return RuntimeError("the solve was accepted")


print("HiGHS with threads=2:", refusal(caught(lambda: mathopt.solve(model, S.HIGHS, params=mathopt.SolveParameters(threads=2)))))
print("PDLP on binaries:", refusal(caught(lambda: mathopt.solve(model, S.PDLP))))
print("a text with a suffix:", refusal(ValueError("seed out of range (was C++ FAILED_PRECONDITION)")))
print("a plain text:", refusal(ValueError("license expired")))
