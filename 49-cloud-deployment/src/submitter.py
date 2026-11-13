"""Lesson 12.5.2: start a run. Store the snapshot, submit the solve to Batch, and index the run.

The API of lesson 12.4.2 calls `start_run` where lesson 12.4.2 handed the solve to a thread pool.
GridCap is a fictional utility.
"""

from __future__ import annotations

import sqlite3

import run_index
from batch_stack import Stack
from s3_store import S3Store
from snapshot import Snapshot


def submit_solve(batch, stack: Stack, run_id: str, digest: str, time_limit_s: int) -> str:
    """Submit one solve job; return Batch's job id. The run id doubles as the job's name."""
    job = batch.submit_job(
        jobName=run_id,
        jobQueue=stack.queue,
        jobDefinition=stack.definition,
        containerOverrides={"environment": [
            {"name": "RUN_ID", "value": run_id},
            {"name": "SNAPSHOT_DIGEST", "value": digest},
            {"name": "TIME_LIMIT_S", "value": str(time_limit_s)},
        ]},
        timeout={"attemptDurationSeconds": max(60, time_limit_s + 600)},
    )
    return job["jobId"]


def start_run(conn: sqlite3.Connection, store: S3Store, batch, stack: Stack,
              run_id: str, snap: Snapshot, time_limit_s: int) -> str:
    """Snapshot first, then the job, then the index row: each step only refers to what exists."""
    digest = store.put_snapshot(snap)
    job_id = submit_solve(batch, stack, run_id, digest, time_limit_s)
    run_index.record_submitted(conn, run_id, digest, job_id)
    return digest
