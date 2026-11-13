"""Gurobi through OR-Tools in the course runner: asked for, then pointed at gurobipy's library (lesson 4.1.2).

No Gurobi license is used or needed: every attempt here fails before a license is looked for.
Loading a library that OR-Tools rejects aborts the whole process, so those attempts run in child
processes, and only the lines that name the cause are printed.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile

import gurobipy
from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt

model = mathopt.Model(name="tiny")
model.maximize(model.add_binary_variable(name="x"))
try:
    mathopt.solve(model, mathopt.SolverType.GUROBI)
except Exception as error:
    print("MathOpt, SolverType.GUROBI:", type(error).__name__, error)
print("pywraplp, CreateSolver('GUROBI'):", pywraplp.Solver.CreateSolver("GUROBI"))

library = sorted((pathlib.Path(gurobipy.__file__).parent / ".libs").glob("libgurobi*.so"))[0]
print(f"\ngurobipy {'.'.join(map(str, gurobipy.gurobi.version()))} ships {library.name}; pointing OR-Tools at it:")
home = tempfile.mkdtemp()                         # GUROBI_HOME/lib is where pywraplp looks
os.makedirs(f"{home}/lib")
os.symlink(library, f"{home}/lib/{library.name}")
attempts = {
    "MathOpt ": ("from ortools.init.python import init; "
                 f"init.CppBridge.load_gurobi_shared_library({str(library)!r})"),
    "pywraplp": "from ortools.linear_solver import pywraplp; pywraplp.Solver.CreateSolver('GUROBI')",
}
for api, code in attempts.items():
    child = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           env={**os.environ, "GUROBI_HOME": home})
    cause = next(line for line in child.stderr.splitlines() if "could not find function" in line)
    print(f"  {api} exit code {child.returncode}: {cause.split('Error: ')[1].split(' in ')[0]}")
