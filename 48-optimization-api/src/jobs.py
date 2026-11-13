"""Lesson 12.4.2's job service: a request becomes a job, a worker solves it, and the job keeps its outcome.

GridCap is fictional. The worker runs in the API's own process (a thread pool by default), so two
process-wide facts shape it: HiGHS fixes its thread count at the first HiGHS solve of a process
(lesson 4.2.4), and a process that has imported PuLP crashes on a HiGHS MIP
solve (lesson 5.2.1). This module never imports pulp.
"""

from __future__ import annotations

import itertools
import threading
from concurrent.futures import Executor, Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import timedelta
from functools import lru_cache
from typing import Annotated, Literal

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2
from pydantic import BaseModel, ConfigDict, Field

from gridcap import Portfolio, generate
from plan_model import build, starts_of

Status = Literal["queued", "running", "optimal", "time_limit", "infeasible", "failed"]
FINISHED = ("optimal", "time_limit", "infeasible", "failed")


class JobRequest(BaseModel):
    """What a planner tool sends to start a job."""

    model_config = ConfigDict(extra="forbid")

    portfolio: Literal["tiny", "small", "medium", "large"]
    budget: dict[int, Annotated[int, Field(ge=0)]] = Field(default_factory=dict)
    time_limit_s: float = Field(default=60.0, gt=0, le=3600)
    highs_threads: int | None = Field(default=None, ge=1)   # a mistake, kept to show why: HiGHS threads are per process


@dataclass
class Outcome:
    """What one finished job produced. A worker returns one for every job, whatever happened."""

    status: Status
    message: str
    starts: dict[str, int] = field(default_factory=dict)
    npv: float | None = None
    bound: float | None = None
    gap: float | None = None


@lru_cache(maxsize=None)
def portfolio(name: str) -> Portfolio:
    return generate(name)


def relative_gap(npv: float, bound: float) -> float:
    """How far the best plan may be from the best possible, as a share of the plan's NPV (a max model)."""
    return max(0.0, bound - npv) / max(abs(npv), 1.0)


def outcome_of(result: mathopt.SolveResult, starts: dict[str, int], limit_s: float) -> Outcome:
    """Map MathOpt's termination reason to the service's statuses."""
    reason, limit = result.termination.reason, result.termination.limit
    R = mathopt.TerminationReason
    if reason == R.OPTIMAL:
        npv = result.objective_value()
        return Outcome("optimal", f"Best plan found and proven: NPV ${npv:,.0f}k.", starts, npv,
                       result.best_objective_bound(), relative_gap(npv, result.best_objective_bound()))
    if reason == R.FEASIBLE and limit == mathopt.Limit.TIME:
        npv, bound = result.objective_value(), result.best_objective_bound()
        gap = relative_gap(npv, bound)
        return Outcome("time_limit", f"Stopped at the {limit_s:g} s limit with a plan worth ${npv:,.0f}k; "
                       f"no plan is worth more than ${bound:,.0f}k (gap {gap:.2%}).", starts, npv, bound, gap)
    if reason == R.NO_SOLUTION_FOUND and limit == mathopt.Limit.TIME:
        return Outcome("time_limit", f"No plan found within the {limit_s:g} s limit. This does not mean "
                       "that no plan exists: run again with more time.")
    if reason == R.INFEASIBLE:
        return Outcome("infeasible", "No plan meets every rule and budget. The must-do projects and the "
                       "budgets cannot all be met; check the budgets you changed first.")
    return Outcome("failed", f"The solver stopped without an answer ({reason.name}"
                   f"{', limit ' + limit.name if limit else ''}). The inputs were not judged.")


def run_job(request: JobRequest) -> Outcome:
    """The worker: build, solve, map. It never raises; an exception becomes a `failed` outcome."""
    try:
        pf = portfolio(request.portfolio)
        pm = build(pf, {**pf.budget, **request.budget})
        params = mathopt.SolveParameters(relative_gap_tolerance=0.0,
                                         time_limit=timedelta(seconds=request.time_limit_s))
        if request.highs_threads is not None:
            params.highs = highs_pb2.HighsOptionsProto(int_options={"threads": request.highs_threads})
        result = mathopt.solve(pm.model, mathopt.SolverType.HIGHS, params=params)
        starts = starts_of(pm, result) if result.has_primal_feasible_solution() else {}
        return outcome_of(result, starts, request.time_limit_s)
    except Exception as error:   # the solver's own reason hides on __context__ in OR-Tools 9.15
        reason = error.__context__ if error.__context__ is not None else error
        return Outcome("failed", f"The solve failed: {reason}. The inputs were not judged.")


@dataclass
class Job:
    job_id: str
    request: JobRequest
    future: Future


class JobStore:
    """Every job the service has accepted, by id. The executor decides where the solves run."""

    def __init__(self, executor: Executor | None = None, worker=run_job):
        self.executor = executor or ThreadPoolExecutor(max_workers=1)
        self.worker = worker
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._ids = itertools.count(1)

    def submit(self, request: JobRequest) -> str:
        with self._lock:
            job_id = f"job-{next(self._ids)}"
            self._jobs[job_id] = Job(job_id, request, self.executor.submit(self.worker, request))
        return job_id

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def status(self, job: Job) -> Status:
        if job.future.done():
            return self.outcome(job).status
        return "running" if job.future.running() else "queued"

    def outcome(self, job: Job) -> Outcome:
        """The finished job's outcome. A worker process that died has no outcome, so the store writes one."""
        error = job.future.exception()
        if error is not None:
            return Outcome("failed", f"The worker stopped before answering ({type(error).__name__}). "
                           "The inputs were not judged.")
        return job.future.result()
