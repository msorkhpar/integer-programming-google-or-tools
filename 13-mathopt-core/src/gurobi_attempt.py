"""SolverType.GUROBI in the course runner: what MathOpt does when it cannot reach a Gurobi library."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="tiny")
x = model.add_binary_variable(name="x")
model.maximize(x)
try:
    result = mathopt.solve(model, mathopt.SolverType.GUROBI)
    print("GUROBI:", result.termination.reason.name)
except Exception as error:
    print("GUROBI raised", type(error).__name__ + ":", error)
    print("hidden reason:", error.__context__)

# Point OR-Tools at the Gurobi library inside the gurobipy wheel. If the library lacks a function
# OR-Tools needs, the process aborts, so try it in a child process and keep its last error line.
import pathlib
import subprocess
import sys

import gurobipy

library = sorted((pathlib.Path(gurobipy.__file__).parent / ".libs").glob("libgurobi*.so"))[0]
probe = ("from ortools.init.python import init; "
         f"print('loaded', init.CppBridge.load_gurobi_shared_library({str(library)!r}))")
child = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True)
print("gurobipy", ".".join(map(str, gurobipy.gurobi.version())), "ships", library.name)
print("loading it: exit code", child.returncode)
for line in child.stderr.splitlines():
    if "could not find function" in line:
        print("  ", line.split("] ", 1)[1].replace(str(library), library.name))
