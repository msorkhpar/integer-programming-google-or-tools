"""Lesson 12.5.2: submit a solve to AWS Batch on Fargate, against moto, and follow the run to its result.

moto records the job and marks it SUCCEEDED without starting any container, so the program then
runs the worker itself, with the environment Batch recorded for the job, as the container would.
No AWS is reached. GridCap is a fictional utility.
"""

import json
import tempfile
import time
from contextlib import closing
from pathlib import Path

import boto3

import run_index
from batch_stack import create_stack
from fake_aws import fake_aws
from gridcap import generate
from s3_store import S3Store
from settings import Settings
from snapshot import export, load
from solve_worker import run_worker
from submitter import start_run

with fake_aws(), tempfile.TemporaryDirectory() as folder:
    s3, batch = boto3.client("s3"), boto3.client("batch")
    s3.create_bucket(Bucket="gridcap-runs-example")
    store = S3Store(s3, "gridcap-runs-example")
    stack = create_stack(boto3.client("ec2"), boto3.client("iam"), batch)
    with closing(run_index.connect(str(Path(folder) / "runs.db"))) as conn:
        run_index.create_schema(conn)
        snap = load(json.dumps(export(generate("small"))))
        start_run(conn, store, batch, stack, "run-0007", snap, time_limit_s=60)

        job_id = conn.execute("SELECT batch_job_id FROM run WHERE run_id = 'run-0007'").fetchone()[0]
        job = batch.describe_jobs(jobs=[job_id])["jobs"][0]
        print("job name:", job["jobName"], "| queue:", job["jobQueue"].split(":")[-1])
        print("job definition:", job["jobDefinition"].split(":", 5)[-1])
        print("environment overrides:", [e["name"] for e in job["container"]["environment"]
                                         if e["name"] in ("RUN_ID", "SNAPSHOT_DIGEST", "TIME_LIMIT_S")])
        print("job timeout:", job["timeout"]["attemptDurationSeconds"], "s for a 60 s solver limit")
        while job["status"] not in ("SUCCEEDED", "FAILED"):
            time.sleep(0.1)
            job = batch.describe_jobs(jobs=[job_id])["jobs"][0]
        print("Batch says:", job["status"], "| index says:", run_index.refresh(conn, store, "run-0007"))

        definition = batch.describe_job_definitions(jobDefinitionName="gridcap-solve")["jobDefinitions"][0]
        env = {e["name"]: e["value"] for e in definition["containerProperties"]["environment"]}
        env |= {e["name"]: e["value"] for e in job["container"]["environment"]}
        key = run_worker(Settings.from_env(env), store)          # what the container would have done
        print("after the worker ran, index says:", run_index.refresh(conn, store, "run-0007"))
        row = conn.execute("SELECT status, npv, result_key FROM run WHERE run_id = 'run-0007'").fetchone()
        print(f"status {row['status']}, NPV ${row['npv']:,}k, result at {row['result_key'][:20]}...")
