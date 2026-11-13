"""Lesson 5.1.4: Pyomo's infeasibility tools on a GridCap budget cut, with HiGHS as the only solver.

GridCap is a fictional utility's portfolio. The planners test cutting the 2030 and 2031 budgets of
the small portfolio's timing model (pyomo_timing.py). Two tools: `compute_infeasibility_explanation`
(an elastic filter and a deletion filter, run with any solver Pyomo can call) and
`find_infeasible_constraints` (checks a given plan, with no solver at all). `write_iis`, which needs
a commercial solver, is in write_iis_demo.py.
"""

import io
import logging

import pyomo.environ as pyo
from pyomo.contrib.iis import compute_infeasibility_explanation
from pyomo.contrib.solver.common.util import NoFeasibleSolutionError
from pyomo.util.infeasible import find_infeasible_constraints

from gridcap import generate
from pyomo_timing import build, highs, schedule

small = generate("small")


def cut(cap):
    m = build(small)
    m.budget[2030] = cap
    m.budget[2031] = cap
    return m


class HighsThatReturns:
    """HiGHS for the MIS tool: it must report an infeasible solve in its results, not raise."""

    def __init__(self):
        self.highs = pyo.SolverFactory("highs")

    def available(self):
        return self.highs.available()

    def solve(self, model, tee=False):
        try:
            return self.highs.solve(model, tee=tee)
        except NoFeasibleSolutionError:
            return self.highs.solve(model, tee=tee, load_solutions=False,
                                    raise_exception_on_nonoptimal_result=False)


def explain(model):
    """Run the MIS tool and return the text it logs."""
    text = io.StringIO()
    log = logging.getLogger("gridcap.mis")
    log.handlers = [logging.StreamHandler(text)]
    log.propagate = False
    log.setLevel(logging.INFO)
    compute_infeasibility_explanation(model, HighsThatReturns(), logger=log)
    return text.getvalue()


def mis_lines(report: str) -> list[str]:
    """The constraints and bounds listed under the MIS heading of the tool's report."""
    mis = report.split("Constraints / bounds in MIS:")[1].split("Constraints / bounds in guards")[0]
    return [line.strip() for line in mis.strip().splitlines()]


if __name__ == "__main__":
    # 1. Cut both years to $4,000k: the MILP is infeasible, but the MIS tool relaxes integrality.
    m = cut(4000)
    print("cap 4,000:", highs().solve(m, load_solutions=False).solver.termination_condition)
    try:
        explain(m)
    except Exception as error:
        print("  MIS tool:", error)

    # 2. Cut both years to $2,600k: now even the LP is infeasible, and the tool finds a minimal set.
    report = explain(cut(2600))
    lines = mis_lines(report)
    print("cap 2,600: MIS rows:", [line for line in lines if line.startswith("constraint")])
    print(f"  plus {sum(1 for line in lines if line.startswith('lb of var'))} lower bounds x >= 0,"
          f" e.g. {[line for line in lines if line.startswith('lb')][:2]}")
    print("  repair options it logged:", report.count("feasible solution was found"))

    # 3. Check a given plan against the cut model: the plan the full budgets gave, with no solve.
    plan = build(small)
    highs().solve(plan)
    starts = schedule(plan)
    m = cut(4000)
    for (i, t), v in m.x.items():
        v.fix(1 if starts.get(i) == t else 0)
    for row, body, which in find_infeasible_constraints(m):
        print(f"{row.name}: plan spends {body:,.0f} > {pyo.value(row.upper):,.0f}")
