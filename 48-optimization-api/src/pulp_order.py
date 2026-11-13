"""Does the order of `import pulp` and OR-Tools matter for lesson 5.2.1's crash? Each case in its own process."""

import signal
import subprocess
import sys

MIP = """
from ortools.math_opt.python import mathopt
m = mathopt.Model()
x = m.add_integer_variable(lb=0, ub=3, name="x")
m.add_linear_constraint(2 * x <= 5)
m.maximize(x)
print(mathopt.solve(m, mathopt.SolverType.HIGHS).objective_value())
"""

cases = {
    "import pulp, then OR-Tools, then solve": "import pulp\n" + MIP,
    "OR-Tools, then import pulp, then solve": "from ortools.math_opt.python import mathopt\nimport pulp\n" + MIP,
    "solve, import pulp, solve again": MIP + "import pulp\n" + MIP,
}
for label, code in cases.items():
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    ending = (f"killed by {signal.Signals(-done.returncode).name}" if done.returncode < 0
              else f"exit {done.returncode}, objective {' and '.join(done.stdout.split())}")
    print(f"{label:<40} {ending}")
