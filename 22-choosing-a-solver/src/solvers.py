"""One run of one solver on one instance with one seed, and the work measures each solver reports.

Every solver runs on one thread, with a fixed random seed and a relative gap target of 0 unless a
target is given, so that a run can repeat. Each run keeps:
- what the solver proved (status, objective, best bound);
- its deterministic work measures: counts the solver reports that depend only on the path the
  search took, so they repeat when the path repeats;
- the wall-clock seconds, which change on every run. Programs may compute with them; no lesson
  prints them.

HiGHS and SCIP are solved through MathOpt; CP-SAT through `cp_model`, whose response carries its
deterministic time; CBC through `pywraplp`, the only API in the runner that has it.
"""

from __future__ import annotations

import datetime
import time
from dataclasses import dataclass, field

from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2
from ortools.sat.python import cp_model

from instances import Instance, build_cpsat, build_mathopt, build_wrapper
from quiet import muted

LIMIT_SECONDS = 120.0

#: The deterministic measures each solver reports, the first being the one the harness ranks by.
MEASURES = {
    "HiGHS": ("lp_iterations", "nodes"),
    "SCIP": ("lp_iterations", "nodes"),
    "CP-SAT": ("det_time", "branches"),
    "CBC": ("lp_iterations", "nodes"),
}
#: Whether the solver's API in this runner accepts a random seed.
TAKES_SEED = {"HiGHS": True, "SCIP": True, "CP-SAT": True, "CBC": False}


@dataclass(frozen=True)
class Run:
    solver: str
    instance: str
    seed: int
    status: str                                    # "optimal", "gap reached", or why it stopped
    objective: float
    bound: float
    work: dict[str, float] = field(default_factory=dict)
    wall: float = 0.0                              # seconds; never printed on a page

    @property
    def solved(self) -> bool:
        return self.status in ("optimal", "gap reached")

    def gap(self) -> float:
        """|bound - objective| / |objective|: one definition for every solver, the course's relative gap."""
        return abs(self.bound - self.objective) / max(abs(self.objective), 1e-9)


def _mathopt(solver: str, inst: Instance, seed: int, gap: float, settings: dict) -> Run:
    model, _ = build_mathopt(inst)
    if solver == "HiGHS":
        params = mathopt.SolveParameters(
            random_seed=seed, relative_gap_tolerance=gap, **settings,
            time_limit=datetime.timedelta(seconds=LIMIT_SECONDS),
            highs=highs_pb2.HighsOptionsProto(int_options={"threads": 1}))   # HiGHS refuses the common `threads`
        kind = mathopt.SolverType.HIGHS
    else:
        params = mathopt.SolveParameters(
            random_seed=seed, relative_gap_tolerance=gap, threads=1, **settings,
            time_limit=datetime.timedelta(seconds=LIMIT_SECONDS))
        kind = mathopt.SolverType.GSCIP
    start = time.perf_counter()
    with muted():
        result = mathopt.solve(model, kind, params=params)
    wall = time.perf_counter() - start
    reason = result.termination.reason
    status = ("optimal" if reason == mathopt.TerminationReason.OPTIMAL and gap == 0
              else "gap reached" if reason == mathopt.TerminationReason.OPTIMAL
              else reason.name.lower())
    stats = result.solve_stats
    return Run(solver, inst.name, seed, status, result.objective_value(),
               result.termination.objective_bounds.dual_bound,
               {"lp_iterations": stats.simplex_iterations, "nodes": stats.node_count}, wall)


def _cpsat(inst: Instance, seed: int, gap: float) -> Run:
    model, _ = build_cpsat(inst)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = seed
    solver.parameters.relative_gap_limit = gap
    solver.parameters.max_time_in_seconds = LIMIT_SECONDS
    start = time.perf_counter()
    code = solver.solve(model)
    wall = time.perf_counter() - start
    status = ("optimal" if code == cp_model.OPTIMAL and gap == 0
              else "gap reached" if code == cp_model.OPTIMAL
              else solver.status_name(code).lower())
    return Run("CP-SAT", inst.name, seed, status, solver.objective_value, solver.best_objective_bound,
               {"det_time": round(solver.deterministic_time, 4), "branches": solver.num_branches}, wall)


def _cbc(inst: Instance, gap: float) -> Run:
    solver, _ = build_wrapper(inst, "CBC")
    solver.SetNumThreads(1)
    solver.SetTimeLimit(int(LIMIT_SECONDS * 1000))
    params = pywraplp.MPSolverParameters()
    params.SetDoubleParam(params.RELATIVE_MIP_GAP, gap)
    start = time.perf_counter()
    code = solver.Solve(params)
    wall = time.perf_counter() - start
    status = ("optimal" if code == pywraplp.Solver.OPTIMAL and gap == 0
              else "gap reached" if code == pywraplp.Solver.OPTIMAL else f"status {code}")
    return Run("CBC", inst.name, 0, status, solver.Objective().Value(), solver.Objective().BestBound(),
               {"lp_iterations": solver.iterations(), "nodes": solver.nodes()}, wall)


def run(solver: str, inst: Instance, seed: int, gap: float = 0.0, **settings) -> Run:
    """Solve `inst` with `solver` ("HiGHS", "SCIP", "CP-SAT" or "CBC") on one thread.

    `settings` are extra MathOpt `SolveParameters` fields, for HiGHS and SCIP only.
    """
    if solver in ("HiGHS", "SCIP"):
        return _mathopt(solver, inst, seed, gap, settings)
    if settings:
        raise ValueError(f"settings are for the MathOpt solvers, not {solver}")
    if solver == "CP-SAT":
        return _cpsat(inst, seed, gap)
    if solver == "CBC":
        return _cbc(inst, gap)
    raise ValueError(f"no solver {solver!r} in the runner")
