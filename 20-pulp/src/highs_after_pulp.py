"""Run MathOpt on a two-line MIP in a fresh Python process, with and without `import pulp` first.

Each case runs in a child process, because the crash it looks for ends the process that has it.
"""

import signal
import subprocess
import sys

MIP = """
from ortools.math_opt.python import mathopt
m = mathopt.Model()
x = m.add_integer_variable(lb=0, ub=3, name="x")
m.add_linear_constraint(2 * x <= 5)
m.maximize(x)
print(mathopt.solve(m, mathopt.SolverType.{solver}).objective_value())
"""

for first, solver in (("", "HIGHS"), ("import pulp", "HIGHS"), ("import pulp", "GSCIP"), ("import pulp", "CP_SAT")):
    code = first + "\n" + MIP.format(solver=solver)
    done = subprocess.run([sys.executable, "-X", "faulthandler", "-c", code], capture_output=True, text=True)
    if done.returncode < 0:
        trace = done.stderr                         # faulthandler's dump of the native stack
        outcome = (f"killed by {signal.Signals(-done.returncode).name}; the native stack passes through "
                   f"OR-Tools' HighsSolver: {'HighsSolver' in trace}, and highspy: {'highspy' in trace}")
    else:
        outcome = f"exit {done.returncode}, objective {done.stdout.strip()}"
    print(f"{first or '(no pulp)':<12} then MathOpt {solver:<6}: {outcome}")
