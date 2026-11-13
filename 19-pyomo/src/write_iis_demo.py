"""Lesson 5.1.4: `write_iis` on the GridCap budget cut. It runs only where CPLEX, Gurobi or Xpress is licensed.

GridCap is a fictional utility's portfolio. `write_iis` asks a commercial solver's persistent
interface for an IIS of the MILP and writes it as an LP-format file. In the course runner without
a Gurobi license it raises; with a license mounted (lesson 5.3.4) it writes the file, and this
program prints the rows in it. The solver's own log is sent to /dev/null, so only the rows print.
"""

import ctypes
import os
import sys
import tempfile

import pyomo.environ as pyo
from pyomo.contrib.iis import write_iis

from gridcap import generate
from pyomo_timing import build

small = generate("small")
m = build(small)
m.budget[2030] = 2600
m.budget[2031] = 2600

usable = [s for s in ("cplex", "gurobi", "xpress") if pyo.SolverFactory(f"{s}_persistent").available(exception_flag=False)]
print("commercial solvers write_iis can use here:", usable)


def quiet(call):
    """Run `call` with the process's standard output pointed at /dev/null (the solver's log is C output)."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return call()
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


with tempfile.TemporaryDirectory() as folder:
    try:
        path = quiet(lambda: write_iis(m, os.path.join(folder, "budget_cut.ilp")))
    except RuntimeError as error:
        print("write_iis:", error)
    else:
        with open(path) as file:
            text = file.read()
        rows = text.split("Subject To")[1].split("Bounds")[0]
        print("IIS rows:", [line.split(":")[0].strip() for line in rows.splitlines() if ":" in line])
