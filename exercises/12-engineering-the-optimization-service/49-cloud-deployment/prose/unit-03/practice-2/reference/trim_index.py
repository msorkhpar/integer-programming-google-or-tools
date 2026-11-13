from __future__ import annotations

import json
import sqlite3

from botocore.exceptions import ClientError

SCHEMA = """
CREATE TABLE run (
    run_id     TEXT PRIMARY KEY,
    digest     TEXT NOT NULL,
    status     TEXT NOT NULL CHECK (status IN ('submitted', 'optimal', 'time_limit', 'infeasible', 'failed')),
    result_key TEXT,
    cost       INTEGER,
    CHECK ((status = 'submitted') = (result_key IS NULL))
) STRICT;
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, autocommit=False)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.executescript(SCHEMA)
    return conn


def record(conn: sqlite3.Connection, run_id: str, digest: str) -> None:
    with conn:
        conn.execute("INSERT INTO run (run_id, digest, status) VALUES (?, ?, 'submitted')", (run_id, digest))


def result_key(digest: str, run_id: str) -> str:
    return f"trim-results/{digest}/{run_id}.json"


def poll(conn: sqlite3.Connection, s3, bucket: str, run_id: str) -> str:
    """The run's status; a waiting run is finished in the index when its result object exists."""
    row = conn.execute("SELECT digest, status FROM run WHERE run_id = ?", (run_id,)).fetchone()
    if row is None:
        return "unknown"
    if row["status"] != "submitted":
        return row["status"]
    key = result_key(row["digest"], run_id)
    try:
        result = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            return "submitted"
        raise
    with conn:
        conn.execute("UPDATE run SET status = ?, result_key = ?, cost = ? WHERE run_id = ? AND status = 'submitted'",
                     (result["status"], key, result.get("cost"), run_id))
    return result["status"]


def best_runs(conn: sqlite3.Connection) -> dict[str, str]:
    """For each survey digest, the finished run with a plan and the lowest cost (ties: lowest run id)."""
    rows = conn.execute("SELECT digest, run_id FROM run WHERE status IN ('optimal', 'time_limit') "
                        "ORDER BY digest, cost, run_id").fetchall()
    best: dict[str, str] = {}
    for row in rows:
        best.setdefault(row["digest"], row["run_id"])
    return best
