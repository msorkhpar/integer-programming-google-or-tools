"""Lesson 12.5.3: a local SQLite file that indexes the runs whose snapshots and results live in S3.

S3 holds the content: the snapshot every run read and the result every run wrote. The index holds
one small row per run that points at those objects, so "every run of this snapshot", "the runs still
waiting" or "the best NPV this cycle" are SQL queries instead of a walk over the bucket. The
connection rules are lesson 12.1.4's. GridCap is a fictional utility.
"""

from __future__ import annotations

import sqlite3

from s3_store import S3Store, result_key, snapshot_key

SCHEMA = """
CREATE TABLE run (
    run_id          TEXT PRIMARY KEY,
    snapshot_digest TEXT NOT NULL CHECK (length(snapshot_digest) = 64),
    snapshot_key    TEXT NOT NULL,
    batch_job_id    TEXT,
    status          TEXT NOT NULL
                    CHECK (status IN ('submitted', 'optimal', 'time_limit', 'infeasible', 'failed')),
    result_key      TEXT,
    npv             INTEGER,
    CHECK ((status = 'submitted') = (result_key IS NULL))
) STRICT;

CREATE INDEX run_by_snapshot ON run (snapshot_digest);
"""


def connect(path: str) -> sqlite3.Connection:
    """Open the index. Foreign-key and transaction rules as in lesson 12.1.4."""
    conn = sqlite3.connect(path, autocommit=True)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.autocommit = False
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    with conn:
        conn.executescript(SCHEMA)


def record_submitted(conn: sqlite3.Connection, run_id: str, digest: str, batch_job_id: str | None) -> None:
    """One row for a run that was handed to AWS: it points at the snapshot it reads."""
    with conn:
        conn.execute("INSERT INTO run (run_id, snapshot_digest, snapshot_key, batch_job_id, status) "
                     "VALUES (?, ?, ?, ?, 'submitted')", (run_id, digest, snapshot_key(digest), batch_job_id))


def finish(conn: sqlite3.Connection, run_id: str, key: str, result: dict) -> bool:
    """Point a submitted run at its result. False if the run was not waiting (already finished)."""
    with conn:
        changed = conn.execute("UPDATE run SET status = ?, result_key = ?, npv = ? "
                               "WHERE run_id = ? AND status = 'submitted'",
                               (result["status"], key, result.get("npv"), run_id)).rowcount
    return changed == 1


def refresh(conn: sqlite3.Connection, store: S3Store, run_id: str) -> str:
    """A poll: if the run still waits, look for its result object in S3, and record it when it is there."""
    row = conn.execute("SELECT snapshot_digest, status FROM run WHERE run_id = ?", (run_id,)).fetchone()
    if row["status"] == "submitted":
        key = result_key(row["snapshot_digest"], run_id)
        result = store.get_result(key)
        if result is not None:
            finish(conn, run_id, key, result)
    return conn.execute("SELECT status FROM run WHERE run_id = ?", (run_id,)).fetchone()["status"]


def rebuild(conn: sqlite3.Connection, store: S3Store) -> int:
    """Refill an empty index from the result objects in S3. Returns the number of rows written."""
    pages = store.s3.get_paginator("list_objects_v2").paginate(Bucket=store.bucket, Prefix="results/")
    written = 0
    with conn:
        for page in pages:
            for obj in page.get("Contents", []):
                result = store.get_result(obj["Key"])
                digest = result["snapshot_digest"]
                conn.execute("INSERT INTO run (run_id, snapshot_digest, snapshot_key, status, result_key, npv) "
                             "VALUES (?, ?, ?, ?, ?, ?)",
                             (result["run_id"], digest, snapshot_key(digest), result["status"], obj["Key"],
                              result.get("npv")))
                written += 1
    return written
