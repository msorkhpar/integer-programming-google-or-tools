"""Lesson 9.1.3: Pyomo's two infeasibility tools on the Budget Lock scenario and on its crew conflict alone.

GridCap is a fictional utility's portfolio. The Pyomo model is lock_model's, copied row for row
(convert.to_pyomo); every row is `rows[<name>]`. `write_iis` asks Gurobi's persistent interface for an
IIS of the MILP and writes it to a file; `compute_infeasibility_explanation` runs an elastic filter
and a deletion filter with any solver, here HiGHS. The solvers' own output goes to /dev/null.
"""

import io
import logging
import os
import tempfile
from dataclasses import replace

import pyomo.environ as pyo
from pyomo.contrib.iis import compute_infeasibility_explanation, write_iis
from pyomo.contrib.solver.common.util import NoFeasibleSolutionError

from convert import to_pyomo
from gridcap import generate
from lock_model import LOCK, build, quiet

small = generate("small")


class Highs:
    """HiGHS as the MIS tool needs it: an infeasible solve comes back as results, not as an exception."""

    def __init__(self):
        self.highs = pyo.SolverFactory("highs")
        self.solves = 0

    def available(self):
        return self.highs.available()

    def solve(self, model, tee=False):
        self.solves += 1
        try:
            return self.highs.solve(model, tee=tee)
        except NoFeasibleSolutionError:
            return self.highs.solve(model, tee=tee, load_solutions=False,
                                    raise_exception_on_nonoptimal_result=False)


def iis_rows(model) -> list[str]:
    with tempfile.TemporaryDirectory() as folder, quiet():
        path = write_iis(model, os.path.join(folder, "lock.ilp"), solver="gurobi")
        with open(path) as file:
            text = file.read()
    rows = text.split("Subject To")[1].split("Bounds")[0]
    return [line.split(":")[0].strip() for line in rows.splitlines() if ":" in line]


def mis(model) -> tuple[list[str], int]:
    """The MIS tool's report, cut to the lines under its MIS heading, and the solves it made."""
    text = io.StringIO()
    log = logging.getLogger("gridcap.mis")
    log.handlers = [logging.StreamHandler(text)]
    log.propagate = False
    log.setLevel(logging.INFO)
    highs = Highs()
    try:
        with quiet():
            compute_infeasibility_explanation(model, highs, logger=log)
    except Exception as error:                       # the tool raises when it finds a plan
        return [f"raised: {error}"], highs.solves
    block = text.getvalue().split("Constraints / bounds in MIS:")[1].split("Constraints / bounds in guards")[0]
    return [line.strip() for line in block.strip().splitlines()], highs.solves


crews_only = replace(LOCK, name="crew-cut", budget={}, force_in={})
for scenario in (LOCK, crews_only):
    model = to_pyomo(build(small, scenario).model)
    print(f"{scenario.name}: write_iis (Gurobi) rows {iis_rows(model)}")
    lines, solves = mis(model)
    rows = [line for line in lines if not line.startswith("lb of var")]
    bounds = len(lines) - len(rows)
    print(f"{scenario.name}: MIS tool (HiGHS), {solves} solves: {rows}" + (f" + {bounds} lower bounds" if bounds else ""))
