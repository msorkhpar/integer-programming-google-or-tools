"""One solve of one regional plan, with every new incumbent recorded against the solver's deterministic work.

Every run uses one thread and a fixed seed, so that it can repeat, and keeps:
- what the solver proved (status, objective, best bound) and its total deterministic work;
- `events`: one (work, objective) pair per new best plan, in the order found. A start the solver
  accepts appears as the first event, at work 0;
- `wall`: seconds on the clock, which change on every run. Programs may compute with them; no
  lesson prints them.

How each solver's incumbents are seen, in its own deterministic unit:
- SCIP (through MathOpt): a callback on `Event.MIP_SOLUTION`, reading `mip_stats.simplex_iterations`;
- HiGHS (through MathOpt): HiGHS ignores MathOpt callbacks (lesson 4.3.5), so the rows of its log's
  progress table are read: each row that shows a better `BestSol` is a new plan, at `LpIters`;
- CP-SAT (`cp_model`): a solution callback, reading `num_branches`. With one worker the callback's
  `deterministic_time` stays at its value after presolve for the whole search (`cpsat_clock.py`
  shows it), so it cannot date an incumbent.
"""

from __future__ import annotations

import datetime
import math
import re
import time
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2
from ortools.sat.python import cp_model

from gridcap import Portfolio
from plan_model import build, build_cpsat, plan_of
from quiet import muted

LIMIT_SECONDS = 120.0
UNIT = {"SCIP": "lp_iterations", "HiGHS": "lp_iterations", "CP-SAT": "branches"}


@dataclass(frozen=True)
class Run:
    solver: str
    instance: str
    seed: int
    status: str
    objective: float
    bound: float
    work: float                                         # total, in UNIT[solver]
    events: tuple[tuple[float, float], ...] = ()        # (work, objective) for each new best plan
    plan: dict = field(default_factory=dict, compare=False)
    log: tuple[str, ...] = field(default=(), compare=False)
    wall: float = field(default=0.0, compare=False)     # seconds; never printed on a page

    def first(self) -> float:
        """Work to the first plan found: the time to first incumbent, in the solver's unit."""
        return self.events[0][0] if self.events else math.inf

    def within(self, best: float, share: float) -> float:
        """Work until a plan within `share` of `best` (a maximization) was found."""
        for work, objective in self.events:
            if objective >= best - share * abs(best):
                return work
        return math.inf


def hint_values(keys, plan: dict[str, int]) -> dict:
    """1 for each (project, year) the plan starts, 0 for every other key: a complete start."""
    return {(i, t): 1.0 if plan.get(i) == t else 0.0 for i, t in keys}


def _status(reason, gap: float) -> str:
    if reason in (mathopt.TerminationReason.OPTIMAL, cp_model.OPTIMAL):
        return "optimal" if gap == 0 else "gap reached"
    return str(getattr(reason, "name", reason)).lower()


def scip(pf: Portfolio, seed: int, start: dict | None = None, gap: float = 0.0,
         gscip=None, **common) -> Run:
    """SCIP through MathOpt. `start` maps (project, year) to a hinted value; `gscip` is a GScipParameters."""
    pm = build(pf)
    events: list[tuple[float, float]] = []

    npv = {pm.x[p.project_id, t]: p.npv[t] for p in pf.projects for t in p.starts()}

    def on_solution(data: mathopt.CallbackData) -> mathopt.CallbackResult:
        found = sum(npv[v] * value for v, value in data.solution.items())    # the new plan's NPV
        if not events or found > events[-1][1] + 1e-6:
            events.append((float(data.mip_stats.simplex_iterations), found))
        return mathopt.CallbackResult()

    params = mathopt.SolveParameters(threads=1, random_seed=seed, relative_gap_tolerance=gap,
                                     time_limit=datetime.timedelta(seconds=LIMIT_SECONDS), **common)
    if gscip is not None:
        params.gscip.CopyFrom(gscip)
    model_params = None
    if start is not None:
        hint = mathopt.SolutionHint(variable_values={pm.x[k]: v for k, v in start.items() if k in pm.x})
        model_params = mathopt.ModelSolveParameters(solution_hints=[hint])
    clock = time.perf_counter()
    result = mathopt.solve(pm.model, mathopt.SolverType.GSCIP, params=params, model_params=model_params,
                           callback_reg=mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION}),
                           cb=on_solution)
    wall = time.perf_counter() - clock
    return Run("SCIP", pf.name, seed, _status(result.termination.reason, gap), result.objective_value(),
               result.termination.objective_bounds.dual_bound, float(result.solve_stats.simplex_iterations),
               tuple(events), plan_of(pm, result.variable_values()), (), wall)


def progress_rows(log: list[str]) -> list[tuple[str, float, float]]:
    """(source, best plan's value, LP iterations) for each row of a HiGHS MIP log's progress table."""
    rows, table = [], False
    for line in log:
        if "LpIters" in line:
            table = True
            continue
        if table and line.startswith("Solving report"):
            break
        tokens = line.split()
        if not table or len(tokens) < 11 or not re.fullmatch(r"\d+(\.\d+)?s", tokens[-1]):
            continue
        source = line[:4].strip()
        try:
            best, iterations = float(tokens[-7]), float(tokens[-2])
        except ValueError:
            continue
        rows.append((source, best, iterations))
    return rows


def highs(pf: Portfolio, seed: int, start: dict | None = None, gap: float = 0.0,
          options: dict | None = None, **common) -> Run:
    """HiGHS through MathOpt, one thread. `options` are HiGHS options by name (bool, int, double or string)."""
    pm = build(pf)
    proto = highs_pb2.HighsOptionsProto(int_options={"threads": 1})       # lesson 4.2.4: not the common `threads`
    for name, v in (options or {}).items():
        target = (proto.bool_options if isinstance(v, bool) else proto.int_options if isinstance(v, int)
                  else proto.double_options if isinstance(v, float) else proto.string_options)
        target[name] = v
    params = mathopt.SolveParameters(random_seed=seed, relative_gap_tolerance=gap, highs=proto,
                                     time_limit=datetime.timedelta(seconds=LIMIT_SECONDS), **common)
    model_params = None
    if start is not None:
        hint = mathopt.SolutionHint(variable_values={pm.x[k]: v for k, v in start.items() if k in pm.x})
        model_params = mathopt.ModelSolveParameters(solution_hints=[hint])
    log: list[str] = []
    clock = time.perf_counter()
    with muted():
        result = mathopt.solve(pm.model, mathopt.SolverType.HIGHS, params=params, model_params=model_params,
                               msg_cb=mathopt.list_message_callback(log))
    wall = time.perf_counter() - clock
    events: list[tuple[float, float]] = []
    for _, best, iterations in progress_rows(log):
        if math.isfinite(best) and (not events or best > events[-1][1] + 1e-6):
            events.append((iterations, best))
    return Run("HiGHS", pf.name, seed, _status(result.termination.reason, gap), result.objective_value(),
               result.termination.objective_bounds.dual_bound, float(result.solve_stats.simplex_iterations),
               tuple(events), plan_of(pm, result.variable_values()), tuple(log), wall)


class _Incumbents(cp_model.CpSolverSolutionCallback):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[float, float]] = []

    def on_solution_callback(self) -> None:
        self.events.append((float(self.num_branches), self.objective_value))


def cpsat(pf: Portfolio, seed: int, start: dict | None = None, gap: float = 0.0, **parameters) -> Run:
    """CP-SAT with one worker. `parameters` are extra `SatParameters` fields."""
    model, x = build_cpsat(pf)
    for k, v in (start or {}).items():
        if k in x:
            model.add_hint(x[k], int(round(v)))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = seed
    solver.parameters.relative_gap_limit = gap
    solver.parameters.max_time_in_seconds = LIMIT_SECONDS
    for name, v in parameters.items():
        setattr(solver.parameters, name, v)
    seen = _Incumbents()
    clock = time.perf_counter()
    code = solver.solve(model, seen)
    wall = time.perf_counter() - clock
    plan = {i: t for (i, t), var in x.items() if solver.value(var)} if code in (cp_model.OPTIMAL, cp_model.FEASIBLE) else {}
    return Run("CP-SAT", pf.name, seed, _status(code, gap) if code == cp_model.OPTIMAL else solver.status_name(code).lower(),
               solver.objective_value, solver.best_objective_bound, float(solver.num_branches),
               tuple(seen.events), plan, (), wall)


SOLVERS = {"SCIP": scip, "HiGHS": highs, "CP-SAT": cpsat}
