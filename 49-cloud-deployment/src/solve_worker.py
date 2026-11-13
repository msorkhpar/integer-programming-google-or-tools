"""Lessons 12.5.1 and 12.5.2: what the solve container runs. One snapshot in, one result out.

AWS Batch starts the container with RUN_ID, SNAPSHOT_DIGEST and RESULT_BUCKET in its environment.
The worker reads the snapshot from S3, solves the planning model with a time limit, and writes one
result object. It never raises: anything that goes wrong becomes a `failed` result, so whoever
waits for the run always finds an answer. GridCap is a fictional utility.
"""

from __future__ import annotations

import os
from typing import Mapping

from ortools.math_opt.python import mathopt

from plan_model import build, plan, solve
from s3_store import S3Store
from settings import BadSettings, Settings


def outcome(pm, result: mathopt.SolveResult, limit_s: float) -> dict:
    """The service's status for each way a solve ends (lesson 12.4.2), with the plan if there is one."""
    reason, limit = result.termination.reason, result.termination.limit
    R = mathopt.TerminationReason
    if reason in (R.OPTIMAL, R.FEASIBLE) and result.has_primal_feasible_solution():
        status = "optimal" if reason == R.OPTIMAL else "time_limit"
        return {"status": status, "npv": round(result.objective_value()), "starts": plan(pm, result)}
    if reason == R.NO_SOLUTION_FOUND and limit == mathopt.Limit.TIME:
        return {"status": "time_limit", "message": f"no plan found within {limit_s:g} s"}
    if reason == R.INFEASIBLE:
        return {"status": "infeasible", "message": "no plan meets every rule and budget"}
    return {"status": "failed", "message": f"the solver stopped: {reason.name}"}


def run_worker(settings: Settings, store: S3Store) -> str:
    """Solve one run and write its result. Returns the result's key."""
    try:
        snap = store.get_snapshot(settings.snapshot_digest)
        pm = build(snap)
        answer = outcome(pm, solve(pm, settings.time_limit_s), settings.time_limit_s)
    except Exception as error:                   # a missing or corrupted snapshot, a solver error
        answer = {"status": "failed", "message": f"{type(error).__name__}: {error}"}
    record = {"run_id": settings.run_id, "snapshot_digest": settings.snapshot_digest, **answer}
    return store.put_result(settings.snapshot_digest, settings.run_id, record)


def main(environ: Mapping[str, str] = os.environ, s3=None) -> int:
    """The container's entry point. Exit code 0 when a result was written, 2 on bad settings."""
    try:
        settings = Settings.from_env(environ)
    except BadSettings as error:
        print(f"solve worker refused to start: {error}")
        return 2
    if s3 is None:
        import boto3                             # in AWS, the job role's credentials reach boto3 here
        s3 = boto3.client("s3")
    key = run_worker(settings, S3Store(s3, settings.bucket))
    print(f"run {settings.run_id}: result written to s3://{settings.bucket}/{key}")
    return 0
