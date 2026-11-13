"""Lesson 12.5.3: a local SQLite index of runs, pointing at their snapshots and results in S3.

S3 is moto's fake (no AWS is reached); the index file lives in a temporary directory. The worker
is called directly, as the Batch container would run it (lesson 12.5.2). GridCap is fictional.
"""

import copy
import json
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

import boto3

import run_index
from fake_aws import fake_aws
from gridcap import generate
from s3_store import S3Store
from settings import Settings
from snapshot import export, load
from solve_worker import run_worker

BUCKET = "gridcap-runs-example"
doc = export(generate("small"))
cut = copy.deepcopy(doc)
cut["budget"][2]["amount"] = 7000                                       # finance cuts 2029

with fake_aws(), tempfile.TemporaryDirectory() as folder:
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket=BUCKET)
    store = S3Store(s3, BUCKET)
    path = str(Path(folder) / "runs.db")
    with closing(run_index.connect(path)) as conn:
        run_index.create_schema(conn)
        base, lower = store.put_snapshot(load(json.dumps(doc))), store.put_snapshot(load(json.dumps(cut)))
        for run_id, digest in [("run-0007", base), ("run-0008", base), ("run-0009", lower)]:
            run_index.record_submitted(conn, run_id, digest, batch_job_id=None)
        for run_id, digest in [("run-0007", base), ("run-0009", lower)]:      # run-0008 is still queued
            run_worker(Settings(BUCKET, run_id, digest, 60), store)
        print("polls:", {r: run_index.refresh(conn, store, r) for r in ("run-0007", "run-0008", "run-0009")})

        query = ("SELECT run_id, substr(snapshot_digest, 1, 12) AS snapshot, status, npv "
                 "FROM run ORDER BY run_id")
        for row in conn.execute(query):
            print(dict(row))
        try:
            with conn:
                conn.execute("UPDATE run SET status = 'optimal' WHERE run_id = 'run-0008'")
        except sqlite3.IntegrityError as error:
            print("finish run-0008 without a result key:", error)

    os.remove(path)                                                     # the index file is lost
    with closing(run_index.connect(path)) as conn:
        run_index.create_schema(conn)
        print("rebuilt from S3:", run_index.rebuild(conn, store), "rows")
        print([tuple(r) for r in conn.execute("SELECT run_id, status, npv FROM run ORDER BY run_id")])
